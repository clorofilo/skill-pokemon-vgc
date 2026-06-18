import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";

export const server = new McpServer({
  name: "vgc-assistant",
  version: "1.0.0",
});

// Tools are registered in Task 10 and Task 13.
// This stub allows TypeScript compilation to be verified early.

async function main() {
  const transport = new StdioServerTransport();
  await server.connect(transport);
}

main().catch(console.error);
