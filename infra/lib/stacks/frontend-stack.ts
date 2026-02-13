import * as cdk from 'aws-cdk-lib';
import * as amplify from 'aws-cdk-lib/aws-amplify';
import * as secretsmanager from 'aws-cdk-lib/aws-secretsmanager';
import { Construct } from 'constructs';
import { EnvironmentConfig } from '../../config/environments';

export interface FrontendStackProps extends cdk.StackProps {
  config: EnvironmentConfig;
  apiUrl: string;
}

export class FrontendStack extends cdk.Stack {
  public readonly amplifyApp: amplify.CfnApp;

  constructor(scope: Construct, id: string, props: FrontendStackProps) {
    super(scope, id, props);

    const { config, apiUrl } = props;

    // Note: GitHub access token must be stored in Secrets Manager before deployment
    // aws secretsmanager create-secret --name lessonlines/github-token --secret-string "ghp_..."
    const githubTokenSecret = secretsmanager.Secret.fromSecretNameV2(
      this,
      'GitHubToken',
      'lessonlines/github-token'
    );

    // Amplify App using CfnApp for more control
    this.amplifyApp = new amplify.CfnApp(this, 'AmplifyApp', {
      name: `lessonlines-${config.envName}`,
      repository: `https://github.com/${config.githubOwner}/${config.githubRepo}`,
      accessToken: githubTokenSecret.secretValue.unsafeUnwrap(),
      platform: 'WEB_COMPUTE',
      environmentVariables: [
        {
          name: 'VITE_API_URL',
          value: apiUrl,
        },
        {
          name: '_LIVE_UPDATES',
          value: JSON.stringify([
            {
              pkg: '@aws-amplify/backend',
              type: 'npm',
              version: 'latest',
            },
            {
              pkg: '@aws-amplify/backend-cli',
              type: 'npm',
              version: 'latest',
            },
          ]),
        },
      ],
      customRules: [
        {
          source: '/api/<*>',
          target: `${apiUrl}/api/<*>`,
          status: '200',
        },
        {
          source: '</^[^.]+$|\\.(?!(css|gif|ico|jpg|js|png|txt|svg|woff|woff2|ttf|map|json|webp)$)([^.]+$)/>',
          target: '/index.html',
          status: '200',
        },
      ],
      buildSpec: cdk.Fn.sub(`version: 1
frontend:
  phases:
    preBuild:
      commands:
        - cd frontend
        - npm ci
    build:
      commands:
        - npm run build
  artifacts:
    baseDirectory: frontend/dist
    files:
      - '**/*'
  cache:
    paths:
      - frontend/node_modules/**/*
`),
    });

    // Branch configuration
    const branch = new amplify.CfnBranch(this, 'MainBranch', {
      appId: this.amplifyApp.attrAppId,
      branchName: config.githubBranch,
      enableAutoBuild: true,
      enablePullRequestPreview: false,
      stage: config.envName === 'prod' ? 'PRODUCTION' : 'DEVELOPMENT',
      environmentVariables: [
        {
          name: 'VITE_API_URL',
          value: apiUrl,
        },
      ],
    });

    // Outputs
    new cdk.CfnOutput(this, 'AmplifyAppId', {
      value: this.amplifyApp.attrAppId,
      description: 'Amplify App ID',
      exportName: `${config.envName}-AmplifyAppId`,
    });

    new cdk.CfnOutput(this, 'AmplifyDefaultDomain', {
      value: `https://${config.githubBranch}.${this.amplifyApp.attrDefaultDomain}`,
      description: 'Amplify default domain URL',
      exportName: `${config.envName}-AmplifyUrl`,
    });
  }
}
