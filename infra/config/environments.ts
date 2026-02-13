export interface EnvironmentConfig {
  readonly envName: string;
  readonly account?: string;
  readonly region: string;
  readonly domainName?: string;
  readonly githubOwner: string;
  readonly githubRepo: string;
  readonly githubBranch: string;
  readonly database: {
    readonly instanceClass: string;
    readonly allocatedStorage: number;
    readonly multiAz: boolean;
    readonly deletionProtection: boolean;
  };
  readonly lambda: {
    readonly memorySize: number;
    readonly timeout: number;
  };
}

export const devConfig: EnvironmentConfig = {
  envName: 'dev',
  region: 'us-east-1',
  githubOwner: 'johnbjensen68',
  githubRepo: 'lessonlines',
  githubBranch: 'main',
  database: {
    instanceClass: 't3.micro',
    allocatedStorage: 20,
    multiAz: false,
    deletionProtection: false,
  },
  lambda: {
    memorySize: 256,
    timeout: 30,
  },
};

export const prodConfig: EnvironmentConfig = {
  envName: 'prod',
  region: 'us-east-1',
  githubOwner: 'johnbjensen68',
  githubRepo: 'lessonlines',
  githubBranch: 'main',
  database: {
    instanceClass: 't3.small',
    allocatedStorage: 50,
    multiAz: true,
    deletionProtection: true,
  },
  lambda: {
    memorySize: 512,
    timeout: 30,
  },
};

export function getConfig(envName: string): EnvironmentConfig {
  switch (envName) {
    case 'prod':
      return prodConfig;
    case 'dev':
    default:
      return devConfig;
  }
}
