/// <reference path="./.sst/platform/config.d.ts" />

export default $config({
  app(input) {
    return {
      name: "avm-executor",
      removal: input?.stage === "production" ? "retain" : "remove",
      protect: ["production"].includes(input?.stage),
      home: "aws",
      providers: {
        cloudflare: "6.6.0",
        aws: {
          region: "eu-north-1",
        },
      },
    };
  },
  async run() {
    const env = {
      VM_IP: new sst.Secret("VM_IP").value,
      VM_PORT: new sst.Secret("VM_PORT").value,
    };
    const vpc = new sst.aws.Vpc("avm-executor-vpc");
    const cluster = new sst.aws.Cluster("avm-executor-cluster", { vpc });
    new sst.aws.Service("avm-executor-service", {
      cluster,
      loadBalancer: {
        ports: [
          { listen: "80/http", forward: "8080/http" },
          { listen: "443/https", forward: "8080/http" },
        ],
        domain: {
          name:
            $app.stage === "main"
              ? "executor.avm.codes"
              : "executor-dev.avm.codes",
          dns: sst.cloudflare.dns(),
        },
      },
      environment: {
        ENV: $app.stage === "main" ? "production" : "development",
        ...env,
      },
    });
  },
});
