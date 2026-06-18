import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { z } from "zod";
import { cacheManager } from "../cache/manager.js";

export function registerSetsTool(server: McpServer) {
  server.tool(
    "get_viable_sets",
    "Get common competitive sets for a Pokémon in the given format.",
    {
      pokemon: z.string().describe("Pokémon species name"),
      format: z.string().describe("Showdown format ID"),
    },
    async ({ pokemon, format }) => {
      const sets = await cacheManager.getViableSets(pokemon, format);
      const offline = cacheManager.isOffline ? "\n⚠️ Offline mode." : "";
      if (sets.length === 0) {
        return { content: [{ type: "text" as const, text: `No sets found for ${pokemon} in ${format}.${offline}` }] };
      }
      return { content: [{ type: "text" as const, text: JSON.stringify(sets, null, 2) }] };
    }
  );
}
