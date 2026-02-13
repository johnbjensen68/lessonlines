#!/usr/bin/env node
import 'source-map-support/register';
import * as cdk from 'aws-cdk-lib';
import { NetworkStack } from '../lib/stacks/network-stack';
import { DatabaseStack } from '../lib/stacks/database-stack';
import { BackendStack } from '../lib/stacks/backend-stack';
import { FrontendStack } from '../lib/stacks/frontend-stack';
import { getConfig } from '../config/environments';

const app = new cdk.App();

const envName = app.node.tryGetContext('env') || 'dev';
const config = getConfig(envName);

const env = {
  account: config.account || process.env.CDK_DEFAULT_ACCOUNT,
  region: config.region,
};

const networkStack = new NetworkStack(app, `LessonLines-${config.envName}-Network`, {
  env,
  config,
  description: 'LessonLines VPC and networking infrastructure',
});

const databaseStack = new DatabaseStack(app, `LessonLines-${config.envName}-Database`, {
  env,
  config,
  vpc: networkStack.vpc,
  databaseSecurityGroup: networkStack.databaseSecurityGroup,
  description: 'LessonLines RDS PostgreSQL database',
});
databaseStack.addDependency(networkStack);

const backendStack = new BackendStack(app, `LessonLines-${config.envName}-Backend`, {
  env,
  config,
  vpc: networkStack.vpc,
  database: databaseStack.database,
  databaseSecret: databaseStack.databaseSecret,
  lambdaSecurityGroup: networkStack.lambdaSecurityGroup,
  description: 'LessonLines Lambda and API Gateway',
});
backendStack.addDependency(databaseStack);

const frontendStack = new FrontendStack(app, `LessonLines-${config.envName}-Frontend`, {
  env,
  config,
  apiUrl: backendStack.apiUrl,
  description: 'LessonLines Amplify frontend hosting',
});
frontendStack.addDependency(backendStack);

cdk.Tags.of(app).add('Project', 'LessonLines');
cdk.Tags.of(app).add('Environment', config.envName);
