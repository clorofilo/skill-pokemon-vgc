import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { z } from "zod";
import { spawnPython } from "../utils/subprocess.js";

const PokemonDefSchema = z.object({
  species: z.string(),
  item: z.string().optional(),
  nature: z.string().optional(),
  evs: z.record(z.number()).optional(),
  teraType: z.string().optional(),
  boosts: z.record(z.number()).optional(),
});

const FieldSchema = z.object({
  weather: z.string().optional(),
  terrain: z.string().optional(),
});

export function registerDamageTool(server: McpServer) {
  server.tool(
    "calculate_damage",
    "Calculate exact damage rolls using @smogon/calc. Returns damage range, KO chance, and description.",
    {
      attacker: PokemonDefSchema,
      defender: PokemonDefSchema,
      move: z.string(),
      field: FieldSchema.optional(),
    },
    async (params) => {
      const result = await spawnPython("damage_calc.py", params);
      return { content: [{ type: "text" as const, text: JSON.stringify(result, null, 2) }] };
    }
  );
}
