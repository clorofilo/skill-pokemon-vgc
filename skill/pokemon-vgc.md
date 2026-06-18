---
name: pokemon-vgc
description: Competitive Pokémon Champions analysis — teambuilding from scratch, existing team analysis, damage/EV calculation. Invoke for any VGC or Champions format question.
---

# Pokémon Champions VGC Assistant

## Format: Reglamento MB (Pokémon Champions)
- **Battles:** Doubles (2v2 per turn)
- **Team:** 6 Pokémon, bring 4
- **Teracristallization:** Active — 1 Tera per battle per side
- **Banned:** Z-Moves, Mega Evolution, Dynamax/Gigantamax
- **Species Clause + Item Clause active**

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
2. Call `get_usage_stats(core_pokemon, "gen9pokemonchampions")` — check viability
3. Identify speed control strategy: Trick Room / Tailwind / Icy Wind / none
4. Find 2 partners with complementary offensive and defensive roles
5. Fill remaining 3 slots: redirector (Rage Powder/Follow Me), hazard removal, coverage
6. Call `get_viable_sets(pokemon, "gen9pokemonchampions")` for each of the 6 members
7. Call `optimize_evs(pokemon, targets)` for each member's spread
8. Evaluate Tera Types: prefer non-conflicting types across the team
9. Output: complete team in Showdown paste format + per-member rationale

## Flow B: Existing team analysis

1. Parse the Showdown paste (detect: species, item, ability, EVs, nature, moves, Tera type)
2. Call `analyze_team(team_paste)` — get type matrix + speed tiers + speed control count
3. Call `matchup_matrix(team, top_threats)` where top_threats = current meta list from `memory/format_data.md`
4. Call `analyze_lead(team, meta)` — optimal lead pairs and bring recommendations
5. Output structured report:
   - **Type weaknesses:** which types hit 2+ members super-effectively
   - **Speed control:** count and types present
   - **Tera conflicts:** overlapping Tera types that create coverage holes
   - **Top 3 improvements:** specific changes (EV adjustment, Pokémon swap, Tera change)

## Flow C: Damage / EV calculation

1. Parse: attacker (species, item, nature, EVs, Tera), defender (same), move, field conditions
2. Call `calculate_damage(attacker, defender, move, conditions)`
3. If the user asks for survival: call `optimize_evs(defender, [{survive: attacker_move}])`
4. Output:
   - Damage range: `min-max (X.X% - Y.Y%)`
   - KO probability: `guaranteed 2HKO` / `X% chance to OHKO` / etc.
   - If EV optimization: minimum spread + remaining EVs for offense/speed

---

## Decision Priorities (apply in this order, always)

1. **Speed creeps first** — check if key speed tiers are covered before assigning any EVs
   - Key benchmarks: base 60 (Incineroar), base 110 (Flutter Mane), +1 Urshifu, max Calyrex-S
2. **Speed control** — team must have ≥1 source: Tailwind, Trick Room, Icy Wind, or Thunder Wave
3. **Offensive coverage** — can the team hit Steel, Water, Fire, Dragon, Ground?
4. **Defensive coverage** — are super-effective weaknesses covered by at least one partner resist?
5. **EV spreads last** — only after 1-4 are satisfied; justify every deviation from 4/252/252

## Anti-patterns (NEVER do these)

- **Never** suggest 252 Atk / 252 Spe / 4 HP without a specific speed tier target and damage threshold justification
- **Never** finalize a set without assigning and justifying the Tera Type
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
