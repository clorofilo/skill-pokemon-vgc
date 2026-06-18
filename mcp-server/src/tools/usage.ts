import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { z } from "zod";
import { cacheManager } from "../cache/manager.js";

export function registerUsageTool(server: McpServer) {
  server.tool(
    "get_usage_stats",
    "Get usage statistics for a Pokémon in the given format. Returns usage % and rank.",
    {
      pokemon: z.string().describe("Pokémon species name (e.g. 'Incineroar')"),
      format: z.string().describe("Showdown format ID (e.g. 'gen9pokemonchampions')"),
    },
    async ({ pokemon, format }) => {
      const entry = await cacheManager.getUsageStats(pokemon, format);
      const offline = cacheManager.isOffline ? "\n⚠️ Offline mode — data may be stale." : "";
      if (!entry) {
        return { content: [{ type: "text" as const, text: `${pokemon} not found in ${format} usage stats.${offline}` }] };
      }
      return {
        content: [{
          type: "text" as const,
          text: JSON.stringify({ ...entry, offline: cacheManager.isOffline }, null, 2),
        }],
      };
    }
  );
}
