import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { z } from "zod";
import { spawnPython } from "../utils/subprocess.js";

export function registerTeamcheckTool(server: McpServer) {
  server.tool(
    "analyze_team",
    "Analyze a Showdown team paste for type weaknesses, speed control, and coverage gaps.",
    {
      team_paste: z.string().describe("Full Showdown team paste (6 Pokémon blocks)"),
    },
    async ({ team_paste }) => {
      const result = await spawnPython("team_analyzer.py", { team_paste });
      return { content: [{ type: "text" as const, text: JSON.stringify(result, null, 2) }] };
    }
  );
}
