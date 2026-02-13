import * as cdk from 'aws-cdk-lib';
import * as ec2 from 'aws-cdk-lib/aws-ec2';
import * as lambda from 'aws-cdk-lib/aws-lambda';
import * as apigatewayv2 from 'aws-cdk-lib/aws-apigatewayv2';
import * as apigatewayv2Integrations from 'aws-cdk-lib/aws-apigatewayv2-integrations';
import * as rds from 'aws-cdk-lib/aws-rds';
import * as secretsmanager from 'aws-cdk-lib/aws-secretsmanager';
import * as logs from 'aws-cdk-lib/aws-logs';
import * as path from 'path';
import { Construct } from 'constructs';
import { EnvironmentConfig } from '../../config/environments';

export interface BackendStackProps extends cdk.StackProps {
  config: EnvironmentConfig;
  vpc: ec2.IVpc;
  database: rds.IDatabaseInstance;
  databaseSecret: secretsmanager.ISecret;
  lambdaSecurityGroup: ec2.ISecurityGroup;
}

export class BackendStack extends cdk.Stack {
  public readonly apiUrl: string;
  public readonly lambdaFunction: lambda.IFunction;

  constructor(scope: Construct, id: string, props: BackendStackProps) {
    super(scope, id, props);

    const { config, vpc, database, databaseSecret, lambdaSecurityGroup } = props;

    // Backend code path
    const backendPath = path.join(__dirname, '../../../backend');

    // Lambda function
    // Bundling uses Docker for pip install. For local dev without Docker,
    // the local fallback copies files directly (dependencies must be pre-installed or
    // deployment must use Docker/CI).
    this.lambdaFunction = new lambda.Function(this, 'ApiFunction', {
      functionName: `lessonlines-${config.envName}-api`,
      runtime: lambda.Runtime.PYTHON_3_11,
      handler: 'handler.handler',
      code: lambda.Code.fromAsset(backendPath, {
        bundling: {
          image: lambda.Runtime.PYTHON_3_11.bundlingImage,
          command: [
            'bash', '-c',
            [
              'pip install -r requirements-lambda.txt -t /asset-output',
              'cp -r app alembic handler.py /asset-output/',
              // Strip unnecessary files to reduce package size
              'find /asset-output -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null',
              'find /asset-output -type d -name "*.dist-info" -exec rm -rf {} + 2>/dev/null',
              'find /asset-output -type d -name tests -exec rm -rf {} + 2>/dev/null',
              'find /asset-output -type d -name test -exec rm -rf {} + 2>/dev/null',
              'true',
            ].join(' && '),
          ],
          local: {
            tryBundle(outputDir: string) {
              // Fallback for local synthesis without Docker
              const { execSync, spawnSync } = require('child_process');

              // Try pip3, pip, or python3 -m pip for local bundling
              let pipCmd: string | null = null;
              if (spawnSync('pip3', ['--version'], { stdio: 'ignore' }).status === 0) {
                pipCmd = 'pip3';
              } else if (spawnSync('pip', ['--version'], { stdio: 'ignore' }).status === 0) {
                pipCmd = 'pip';
              } else if (spawnSync('python3', ['-m', 'pip', '--version'], { stdio: 'ignore' }).status === 0) {
                pipCmd = 'python3 -m pip';
              }

              if (!pipCmd) {
                console.error('ERROR: No pip found. Cannot bundle Lambda dependencies.');
                return false; // Fall back to Docker bundling
              }

              execSync(`${pipCmd} install -r ${backendPath}/requirements-lambda.txt -t ${outputDir} --quiet`, {
                stdio: 'inherit',
              });
              // Copy only runtime source files
              execSync(`cp -r ${backendPath}/app ${backendPath}/alembic ${backendPath}/handler.py ${outputDir}/`, { stdio: 'inherit' });
              // Strip unnecessary files
              execSync(`find ${outputDir} -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null; true`, { stdio: 'inherit' });
              execSync(`find ${outputDir} -type d -name "*.dist-info" -exec rm -rf {} + 2>/dev/null; true`, { stdio: 'inherit' });
              return true;
            },
          },
        },
      }),
      vpc,
      vpcSubnets: {
        subnetType: ec2.SubnetType.PRIVATE_ISOLATED,
      },
      securityGroups: [lambdaSecurityGroup],
      memorySize: config.lambda.memorySize,
      timeout: cdk.Duration.seconds(config.lambda.timeout),
      environment: {
        DATABASE_SECRET_ARN: databaseSecret.secretArn,
        DATABASE_HOST: database.dbInstanceEndpointAddress,
        DATABASE_PORT: '5432',
        DATABASE_NAME: 'lessonlines',
        ENVIRONMENT: config.envName,
        JWT_SECRET_KEY: 'REPLACE_WITH_SECURE_SECRET', // Should be in Secrets Manager for prod
        JWT_ALGORITHM: 'HS256',
        ACCESS_TOKEN_EXPIRE_MINUTES: '60',
      },
      logRetention: logs.RetentionDays.ONE_WEEK,
    });

    // Grant Lambda permission to read database secret
    databaseSecret.grantRead(this.lambdaFunction);

    // HTTP API Gateway
    const httpApi = new apigatewayv2.HttpApi(this, 'HttpApi', {
      apiName: `lessonlines-${config.envName}-api`,
      description: 'LessonLines API Gateway',
      corsPreflight: {
        allowOrigins: ['*'], // Will be restricted by Lambda CORS middleware
        allowMethods: [
          apigatewayv2.CorsHttpMethod.GET,
          apigatewayv2.CorsHttpMethod.POST,
          apigatewayv2.CorsHttpMethod.PUT,
          apigatewayv2.CorsHttpMethod.DELETE,
          apigatewayv2.CorsHttpMethod.PATCH,
          apigatewayv2.CorsHttpMethod.OPTIONS,
        ],
        allowHeaders: ['*'],
        allowCredentials: false,
      },
    });

    // Lambda integration
    const lambdaIntegration = new apigatewayv2Integrations.HttpLambdaIntegration(
      'LambdaIntegration',
      this.lambdaFunction
    );

    // Add routes - catch all for FastAPI routing
    httpApi.addRoutes({
      path: '/{proxy+}',
      methods: [apigatewayv2.HttpMethod.ANY],
      integration: lambdaIntegration,
    });

    // Also add root path
    httpApi.addRoutes({
      path: '/',
      methods: [apigatewayv2.HttpMethod.ANY],
      integration: lambdaIntegration,
    });

    this.apiUrl = httpApi.apiEndpoint;

    // Outputs
    new cdk.CfnOutput(this, 'ApiUrl', {
      value: this.apiUrl,
      description: 'API Gateway URL',
      exportName: `${config.envName}-ApiUrl`,
    });

    new cdk.CfnOutput(this, 'LambdaFunctionName', {
      value: this.lambdaFunction.functionName,
      description: 'Lambda function name',
      exportName: `${config.envName}-LambdaFunctionName`,
    });
  }
}
