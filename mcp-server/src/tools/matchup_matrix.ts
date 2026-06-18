import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { z } from "zod";
import { spawnPython } from "../utils/subprocess.js";

export function registerMatchupMatrixTool(server: McpServer) {
  server.tool(
    "matchup_matrix",
    "Generate a full matchup matrix for a team against a list of meta threats.",
    {
      team_paste: z.string().describe("Full Showdown team paste"),
      threats: z.array(z.string()).describe("Pokémon species to evaluate matchups against"),
    },
    async (params) => {
      const result = await spawnPython("matchup_matrix.py", params);
      return { content: [{ type: "text" as const, text: JSON.stringify(result, null, 2) }] };
    }
  );
}
