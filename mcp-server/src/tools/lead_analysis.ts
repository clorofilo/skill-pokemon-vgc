import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { z } from "zod";
import { spawnPython } from "../utils/subprocess.js";

export function registerLeadAnalysisTool(server: McpServer) {
  server.tool(
    "analyze_lead",
    "Analyze optimal lead pairs and bring recommendations for a team against the current meta.",
    {
      team: z.array(z.string()).length(6).describe("6 Pokémon species names"),
      meta: z.array(z.string()).describe("Top meta threats to consider"),
    },
    async (params) => {
      const result = await spawnPython("lead_analyzer.py", params);
      return { content: [{ type: "text" as const, text: JSON.stringify(result, null, 2) }] };
    }
  );
}
