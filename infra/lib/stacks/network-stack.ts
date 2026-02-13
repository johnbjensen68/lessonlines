import * as cdk from 'aws-cdk-lib';
import * as ec2 from 'aws-cdk-lib/aws-ec2';
import { Construct } from 'constructs';
import { EnvironmentConfig } from '../../config/environments';

export interface NetworkStackProps extends cdk.StackProps {
  config: EnvironmentConfig;
}

export class NetworkStack extends cdk.Stack {
  public readonly vpc: ec2.IVpc;
  public readonly lambdaSecurityGroup: ec2.ISecurityGroup;
  public readonly databaseSecurityGroup: ec2.ISecurityGroup;

  constructor(scope: Construct, id: string, props: NetworkStackProps) {
    super(scope, id, props);

    const { config } = props;

    // Create VPC with public and private subnets
    // No NAT gateways to minimize costs - Lambda will use VPC endpoints
    // Explicitly specify AZs to avoid context lookups during synthesis
    this.vpc = new ec2.Vpc(this, 'Vpc', {
      vpcName: `lessonlines-${config.envName}-vpc`,
      availabilityZones: [`${config.region}a`, `${config.region}b`],
      natGateways: 0,
      subnetConfiguration: [
        {
          name: 'Public',
          subnetType: ec2.SubnetType.PUBLIC,
          cidrMask: 24,
        },
        {
          name: 'Private',
          subnetType: ec2.SubnetType.PRIVATE_ISOLATED,
          cidrMask: 24,
        },
      ],
    });

    // Security group for Lambda
    this.lambdaSecurityGroup = new ec2.SecurityGroup(this, 'LambdaSecurityGroup', {
      vpc: this.vpc,
      securityGroupName: `lessonlines-${config.envName}-lambda-sg`,
      description: 'Security group for LessonLines Lambda function',
      allowAllOutbound: true,
    });

    // Security group for RDS
    this.databaseSecurityGroup = new ec2.SecurityGroup(this, 'DatabaseSecurityGroup', {
      vpc: this.vpc,
      securityGroupName: `lessonlines-${config.envName}-db-sg`,
      description: 'Security group for LessonLines RDS instance',
      allowAllOutbound: false,
    });

    // Allow Lambda to connect to RDS
    this.databaseSecurityGroup.addIngressRule(
      this.lambdaSecurityGroup,
      ec2.Port.tcp(5432),
      'Allow Lambda to connect to PostgreSQL'
    );

    // VPC Endpoint for Secrets Manager (required for Lambda to access DB credentials)
    // Use selectSubnets with explicit subnet selection to avoid AZ lookups
    new ec2.InterfaceVpcEndpoint(this, 'SecretsManagerEndpoint', {
      vpc: this.vpc,
      service: ec2.InterfaceVpcEndpointAwsService.SECRETS_MANAGER,
      subnets: this.vpc.selectSubnets({ subnetType: ec2.SubnetType.PRIVATE_ISOLATED }),
      privateDnsEnabled: true,
    });

    // Outputs
    new cdk.CfnOutput(this, 'VpcId', {
      value: this.vpc.vpcId,
      description: 'VPC ID',
      exportName: `${config.envName}-VpcId`,
    });
  }
}
