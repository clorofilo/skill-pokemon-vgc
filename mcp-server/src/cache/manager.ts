import fs from "fs/promises";
import path from "path";
import { fileURLToPath } from "url";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const DATA_DIR = path.resolve(__dirname, "../../../data/cache");
const CACHE_TTL_MS = 24 * 60 * 60 * 1000;

export interface UsageEntry {
  pokemon: string;
  usagePercent: number;
  rank: number;
}

export interface ViableSet {
  pokemon: string;
  item: string;
  nature: string;
  evs: Record<string, number>;
  moves: string[];
  teraType?: string;
}

export class CacheManager {
  isOffline = false;

  private cacheFile(name: string) {
    return path.join(DATA_DIR, `${name}.json`);
  }

  private async readCache<T>(name: string): Promise<T | null> {
    try {
      const stat = await fs.stat(this.cacheFile(name));
      if (Date.now() - stat.mtimeMs > CACHE_TTL_MS) return null;
      const raw = await fs.readFile(this.cacheFile(name), "utf-8");
      return JSON.parse(raw) as T;
    } catch {
      return null;
    }
  }

  private async writeCache(name: string, data: unknown): Promise<void> {
    await fs.mkdir(DATA_DIR, { recursive: true });
    await fs.writeFile(this.cacheFile(name), JSON.stringify(data));
  }

  private async fetchUsageStats(format: string): Promise<UsageEntry[]> {
    // Showdown usage stats are at smogon.com/stats/YYYY-MM/<format>-0.txt
    // For Champions format, verify the format ID on the Showdown ladder
    const now = new Date();
    const month = `${now.getFullYear()}-${String(now.getMonth() + 1).padStart(2, "0")}`;
    const url = `https://www.smogon.com/stats/${month}/${format}-0.txt`;

    const resp = await fetch(url);
    if (!resp.ok) throw new Error(`HTTP ${resp.status} from ${url}`);
    const text = await resp.text();

    const entries: UsageEntry[] = [];
    const lines = text.split("\n");
    for (const line of lines.slice(5)) {
      const m = line.match(/^\s*\d+\s*\|\s*(\S+)\s*\|\s*([\d.]+)%/);
      if (m) entries.push({ pokemon: m[1], usagePercent: parseFloat(m[2]), rank: entries.length + 1 });
    }
    return entries;
  }

  async getUsageStats(pokemon: string, format: string): Promise<UsageEntry | null> {
    const cacheKey = `usage-${format}`;
    let entries = await this.readCache<UsageEntry[]>(cacheKey);

    if (!entries) {
      try {
        entries = await this.fetchUsageStats(format);
        await this.writeCache(cacheKey, entries);
        this.isOffline = false;
      } catch {
        this.isOffline = true;
        entries = [];
      }
    }

    return entries.find((e) => e.pokemon.toLowerCase() === pokemon.toLowerCase()) ?? null;
  }

  async getViableSets(pokemon: string, _format: string): Promise<ViableSet[]> {
    const cacheKey = `sets-${pokemon.toLowerCase()}`;
    const cached = await this.readCache<ViableSet[]>(cacheKey);
    if (cached) return cached;

    // Showdown sets endpoint — returns empty array if unavailable (offline fallback)
    try {
      const resp = await fetch(`https://play.pokemonshowdown.com/data/sets/gen9.json`);
      if (!resp.ok) throw new Error(`HTTP ${resp.status}`);
      const all = await resp.json() as Record<string, unknown>;
      const sets = (all[pokemon] as ViableSet[] | undefined) ?? [];
      await this.writeCache(cacheKey, sets);
      return sets;
    } catch {
      this.isOffline = true;
      return [];
    }
  }
}

export const cacheManager = new CacheManager();
