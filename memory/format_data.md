# Pokémon Champions — Reglamento M-B

**Last verified: 2026-08-07** via Bulbapedia, Victory Road, Pikalytics, and the
`smogon/pokemon-showdown` `config/formats.ts` source. Regulation M-B is time-boxed
(2026-06-17 → 2026-09-02/09) — re-verify this file when a new regulation letter ships,
since mechanics flip between regulations (see below).

## Battle Rules
- Format: VGC Doubles (2v2 per turn)
- Team: 6 Pokémon registered, bring 4 to battle
- **Mega Evolution: ACTIVE** — 1 Mega per battle, only select species can Mega Evolve
  (16 new Megas added in M-B on top of the previous regulation's list)
- **Terastallization: NOT active in M-B** — Champions launched Mega-only; Tera is
  confirmed for a *future* regulation but has no announced date. Do not assume Tera
  is available without re-checking the current regulation.
- Z-Moves, Dynamax/Gigantamax: inactive (unchanged across regulations so far)

## Clauses
- Species Clause: no duplicate species
- Item Clause: no duplicate held items (confirmed)

## Roster notes
Champions uses a curated, growing roster (300+ eligible Pokémon across gens 1-9 as of
M-B) rather than a full-dex ban list. Some Legendary/Mythical mons prominent in classic
VGC (Calyrex-Shadow, Miraidon, Koraidon, Landorus-Therian, Tornadus) do **not** appear
in current M-B usage data — this may mean they're not yet on the roster, or simply not
meta this regulation. Don't assert they're "banned" without checking; call
`get_usage_stats`/`get_viable_sets` before building around any of them.

## Showdown Format ID
- `gen9championsvgc2026regmb` (mod: `champions`) — Bo3 variant: `gen9championsvgc2026regmbbo3`
- Source: `[Gen 9 Champions] VGC 2026 Reg M-B` entry in `config/formats.ts`
- Previous regulation (M-A) uses mod `championsregma` — do not reuse M-B's mod for it

## Key Meta Threats (Pikalytics Reg M-B Season 3 ranked data, verified 2026-08-07)
Garchomp, Sinistcha, Basculegion, Whimsicott, Kingambit, Staraptor, Incineroar,
Charizard, Raichu, Pelipper, Sneasler, Archaludon, Grimmsnarl, Sylveon, Swampert,
Metagross, Farigiraf, Floette-Eternal, Gholdengo, Aerodactyl.
Most common core: Garchomp + Whimsicott (~18.7% of sampled teams).
Notable Mega users in the meta: Charizard (Mega Y), Metagross, Aerodactyl.
