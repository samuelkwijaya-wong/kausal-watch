const config = {
  client: {
    includes: ["./tests/**/*.ts", "./common/**/*.ts"],
    service: {
      name: "E2ETestsClient",
      localSchemaFile: "../__generated__/schema-test-mode.graphql",
    },
  },
};
export default config;
