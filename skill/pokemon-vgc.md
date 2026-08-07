---
name: pokemon-vgc
description: Competitive Pokémon Champions analysis — teambuilding from scratch, existing team analysis, damage/EV calculation. Invoke for any VGC or Champions format question.
---

# Pokémon Champions VGC Assistant

## Format: Reglamento M-B (Pokémon Champions)
Active 2026-06-17 → 2026-09-02. **Re-verify this block when the regulation letter
changes** — mechanics (Tera/Mega) flip between regulations, this isn't cosmetic.

- **Battles:** Doubles (2v2 per turn)
- **Team:** 6 Pokémon registered, bring 4
- **Mega Evolution:** Active — 1 Mega per battle, only select species can Mega Evolve
- **Terastallization:** NOT active in M-B (Champions launched Mega-only; Tera is
  confirmed for a future regulation, no date announced)
- **Inactive:** Z-Moves, Dynamax/Gigantamax
- **Species Clause + Item Clause active**
- **Showdown format ID:** `gen9championsvgc2026regmb` (mod `champions`; Bo3 variant
  `gen9championsvgc2026regmbbo3`)
- Roster is curated and growing (300+ eligible Pokémon as of M-B), not a full-dex ban
  list — a Pokémon missing from current usage data may just not be on the roster yet.
  Verify with `get_usage_stats`/`get_viable_sets` before assuming it's legal.

---

## Step 0: Classify the query (ALWAYS do this first)

Read the user's message and choose exactly one flow:

| If the message contains... | Use Flow |
|---|---|
| "arma un equipo", "quiero usar", "necesito un equipo con", any team idea | **A — Teambuilding** |
| A Showdown paste (lines with species @ item, Ability:, EVs:, moves) | **B — Team Analysis** |
| "¿cuántos EVs", "¿OHKOea", "¿2HKO", "¿sobrevive", damage/KO question | **C — Damage/EV Calc** |

---

## Flow A: Teambuilding from scratch

1. Identify the **core Pokémon or archetype** from the user's idea
2. Call `get_usage_stats(core_pokemon, "gen9championsvgc2026regmb")` — check viability
3. Identify speed control strategy: Trick Room / Tailwind / Icy Wind / none
4. Find 2 partners with complementary offensive and defensive roles
5. Fill remaining 3 slots: redirector (Rage Powder/Follow Me), hazard removal, coverage
6. Call `get_viable_sets(pokemon, "gen9championsvgc2026regmb")` for each of the 6 members
7. Call `optimize_evs(pokemon, targets)` for each member's spread
8. Assign the team's single Mega Evolution slot (1 per battle, only eligible species) —
   prefer the member that most needs the stat/typing boost; do not assign a Mega to a
   species that can't Mega Evolve
9. Output: complete team in Showdown paste format + per-member rationale

## Flow B: Existing team analysis

1. Parse the Showdown paste (detect: species, item, ability, EVs, nature, moves)
2. Call `analyze_team(team_paste)` — get type matrix + speed tiers + speed control count
3. Call `matchup_matrix(team, top_threats)` where top_threats = current meta list from `memory/format_data.md`
4. Call `analyze_lead(team, meta)` — optimal lead pairs and bring recommendations
5. Output structured report:
   - **Type weaknesses:** which types hit 2+ members super-effectively
   - **Speed control:** count and types present
   - **Mega Evolution slot:** which member (if any) is assigned the team's one Mega, and whether that's the best use of it
   - **Top 3 improvements:** specific changes (EV adjustment, Pokémon swap, Mega reassignment)

## Flow C: Damage / EV calculation

1. Parse: attacker (species, item, nature, EVs, Mega if applicable), defender (same), move, field conditions
2. Call `calculate_damage(attacker, defender, move, conditions)`
3. If the user asks for survival: call `optimize_evs(defender, [{survive: attacker_move}])`
4. Output:
   - Damage range: `min-max (X.X% - Y.Y%)`
   - KO probability: `guaranteed 2HKO` / `X% chance to OHKO` / etc.
   - If EV optimization: minimum spread + remaining EVs for offense/speed

---

## Decision Priorities (apply in this order, always)

1. **Speed creeps first** — check if key speed tiers are covered before assigning any EVs
   - Key benchmarks (Reg M-B): base 50 (Kingambit), base 60 (Incineroar), base 102
     (Garchomp), base 130 (Aerodactyl) — pull the full list from `memory/format_data.md`
     or `data/formats/champions-mb.json`, don't hardcode a stale meta from memory
2. **Speed control** — team must have ≥1 source: Tailwind, Trick Room, Icy Wind, or Thunder Wave
3. **Offensive coverage** — can the team hit Steel, Water, Fire, Dragon, Ground?
4. **Defensive coverage** — are super-effective weaknesses covered by at least one partner resist?
5. **EV spreads last** — only after 1-4 are satisfied; justify every deviation from 4/252/252

## Anti-patterns (NEVER do these)

- **Never** suggest 252 Atk / 252 Spe / 4 HP without a specific speed tier target and damage threshold justification
- **Never** finalize a team without deciding and justifying who (if anyone) holds the Mega Evolution slot
- **Never** assume Terastallization is available — it is inactive in Reg M-B; re-check `memory/format_data.md` before assuming otherwise for a future regulation
- **Never** suggest a team with zero speed control
- **Never** skip calling MCP tools when they are available — estimates are a last resort

## MCP Tools Reference

| Tool | When to call |
|---|---|
| `get_usage_stats(pokemon, format)` | Before committing to any Pokémon on the team |
| `get_viable_sets(pokemon, format)` | When building or reviewing sets |
| `calculate_damage(attacker, defender, move, conditions)` | Any damage/KO question |
| `analyze_team(team_paste)` | When given an existing team |
| `optimize_evs(pokemon, targets)` | When finding minimum EV spreads |
| `simulate_turn(state)` | When turn-order or priority matters |
| `analyze_lead(team, meta)` | When evaluating lead options |
| `matchup_matrix(team, threats)` | When checking coverage vs meta |

If the MCP server is unavailable, use embedded knowledge and note: "⚠️ MCP server offline — results are estimates based on embedded knowledge."
