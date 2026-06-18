import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";

import { registerDamageTool } from "./tools/damage.js";
import { registerUsageTool } from "./tools/usage.js";
import { registerSetsTool } from "./tools/sets.js";
import { registerTeamcheckTool } from "./tools/teamcheck.js";
import { registerOptimizeEvsTool } from "./tools/optimize_evs.js";
import { registerTurnSimTool } from "./tools/turn_sim.js";
import { registerLeadAnalysisTool } from "./tools/lead_analysis.js";
import { registerMatchupMatrixTool } from "./tools/matchup_matrix.js";

export const server = new McpServer({
  name: "vgc-assistant",
  version: "1.0.0",
});

registerDamageTool(server);
registerUsageTool(server);
registerSetsTool(server);
registerTeamcheckTool(server);
registerOptimizeEvsTool(server);
registerTurnSimTool(server);
registerLeadAnalysisTool(server);
registerMatchupMatrixTool(server);

async function main() {
  const transport = new StdioServerTransport();
  await server.connect(transport);
}

main().catch(console.error);
