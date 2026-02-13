import * as cdk from 'aws-cdk-lib';
import * as ec2 from 'aws-cdk-lib/aws-ec2';
import * as rds from 'aws-cdk-lib/aws-rds';
import * as secretsmanager from 'aws-cdk-lib/aws-secretsmanager';
import { Construct } from 'constructs';
import { EnvironmentConfig } from '../../config/environments';

export interface DatabaseStackProps extends cdk.StackProps {
  config: EnvironmentConfig;
  vpc: ec2.IVpc;
  databaseSecurityGroup: ec2.ISecurityGroup;
}

export class DatabaseStack extends cdk.Stack {
  public readonly database: rds.IDatabaseInstance;
  public readonly databaseSecret: secretsmanager.ISecret;

  constructor(scope: Construct, id: string, props: DatabaseStackProps) {
    super(scope, id, props);

    const { config, vpc, databaseSecurityGroup } = props;

    // Create database credentials in Secrets Manager
    this.databaseSecret = new secretsmanager.Secret(this, 'DatabaseSecret', {
      secretName: `lessonlines/${config.envName}/database`,
      description: 'LessonLines database credentials',
      generateSecretString: {
        secretStringTemplate: JSON.stringify({ username: 'lessonlines' }),
        generateStringKey: 'password',
        excludePunctuation: true,
        passwordLength: 32,
      },
    });

    // Map instance class string to CDK instance type
    const instanceType = this.getInstanceType(config.database.instanceClass);

    // Create RDS PostgreSQL instance
    this.database = new rds.DatabaseInstance(this, 'Database', {
      instanceIdentifier: `lessonlines-${config.envName}`,
      engine: rds.DatabaseInstanceEngine.postgres({
        version: rds.PostgresEngineVersion.VER_15,
      }),
      instanceType,
      vpc,
      vpcSubnets: {
        subnetType: ec2.SubnetType.PRIVATE_ISOLATED,
      },
      securityGroups: [databaseSecurityGroup],
      credentials: rds.Credentials.fromSecret(this.databaseSecret),
      databaseName: 'lessonlines',
      allocatedStorage: config.database.allocatedStorage,
      maxAllocatedStorage: config.database.allocatedStorage * 2,
      multiAz: config.database.multiAz,
      deletionProtection: config.database.deletionProtection,
      removalPolicy: config.database.deletionProtection
        ? cdk.RemovalPolicy.RETAIN
        : cdk.RemovalPolicy.DESTROY,
      backupRetention: cdk.Duration.days(config.envName === 'prod' ? 7 : 1),
      storageEncrypted: true,
      publiclyAccessible: false,
    });

    // Outputs
    new cdk.CfnOutput(this, 'DatabaseEndpoint', {
      value: this.database.dbInstanceEndpointAddress,
      description: 'Database endpoint',
      exportName: `${config.envName}-DatabaseEndpoint`,
    });

    new cdk.CfnOutput(this, 'DatabaseSecretArn', {
      value: this.databaseSecret.secretArn,
      description: 'Database secret ARN',
      exportName: `${config.envName}-DatabaseSecretArn`,
    });
  }

  private getInstanceType(instanceClass: string): ec2.InstanceType {
    const classMap: Record<string, ec2.InstanceType> = {
      't3.micro': ec2.InstanceType.of(ec2.InstanceClass.T3, ec2.InstanceSize.MICRO),
      't3.small': ec2.InstanceType.of(ec2.InstanceClass.T3, ec2.InstanceSize.SMALL),
      't3.medium': ec2.InstanceType.of(ec2.InstanceClass.T3, ec2.InstanceSize.MEDIUM),
      't3.large': ec2.InstanceType.of(ec2.InstanceClass.T3, ec2.InstanceSize.LARGE),
    };
    return classMap[instanceClass] || classMap['t3.micro'];
  }
}
