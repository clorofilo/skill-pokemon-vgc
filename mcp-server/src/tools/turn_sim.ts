import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { z } from "zod";
import { spawnPython } from "../utils/subprocess.js";

export function registerTurnSimTool(server: McpServer) {
  server.tool(
    "simulate_turn",
    "Simulate a battle turn with priority moves, weather, terrain, and Tera effects.",
    {
      state: z.object({
        side_a: z.array(z.string()).length(2),
        side_b: z.array(z.string()).length(2),
        weather: z.string().nullable().optional(),
        terrain: z.string().nullable().optional(),
      }),
      moves: z.array(z.object({
        user: z.string(),
        move: z.string(),
        target: z.string(),
      })),
    },
    async (params) => {
      const result = await spawnPython("turn_simulator.py", params);
      return { content: [{ type: "text" as const, text: JSON.stringify(result, null, 2) }] };
    }
  );
}
