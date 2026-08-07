import { describe, it, expect } from "vitest";
import { viableSetsCacheKey, viableSetsUrl } from "../src/cache/manager.js";

describe("viableSetsCacheKey", () => {
  it("produces different keys for the same pokemon in different formats", () => {
    const keyA = viableSetsCacheKey("Incineroar", "gen9championsvgc2026regmb");
    const keyB = viableSetsCacheKey("Incineroar", "gen9ou");
    expect(keyA).not.toBe(keyB);
  });
});

describe("viableSetsUrl", () => {
  it("derives the generation from the given format instead of hardcoding gen9", () => {
    expect(viableSetsUrl("gen8doublesou")).toContain("gen8");
    expect(viableSetsUrl("gen9championsvgc2026regmb")).toContain("gen9");
  });
});
