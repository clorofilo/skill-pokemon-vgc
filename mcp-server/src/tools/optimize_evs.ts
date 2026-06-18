import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { z } from "zod";
import { spawnPython } from "../utils/subprocess.js";

const PokemonDefSchema = z.object({
  species: z.string(),
  item: z.string().optional(),
  nature: z.string().optional(),
  evs: z.record(z.number()).optional(),
  teraType: z.string().optional(),
});

const ThresholdSchema = z.object({
  type: z.enum(["survive", "outspeed"]),
  attacker: PokemonDefSchema.optional(),
  move: z.string().optional(),
  target_speed: z.number().optional(),
});

export function registerOptimizeEvsTool(server: McpServer) {
  server.tool(
    "optimize_evs",
    "Find the minimum EV spread for a Pokémon to meet survival or speed thresholds.",
    {
      pokemon: PokemonDefSchema,
      targets: z.array(ThresholdSchema),
    },
    async (params) => {
      const result = await spawnPython("ev_optimizer.py", params);
      return { content: [{ type: "text" as const, text: JSON.stringify(result, null, 2) }] };
    }
  );
}
