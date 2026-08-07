# Architecture Decisions

## D1: TypeScript MCP server + Python calc-tools
TypeScript has native `@smogon/calc` support; Python is better for iterative EV search.
Communication: JSON over stdin/stdout subprocess — no HTTP overhead.

## D2: Single calc_bridge.js for all damage calculations
All damage math goes through `@smogon/calc` via Node subprocess. Python scripts call it
rather than re-implementing the damage formula. Ensures parity with official calc.

## D3: 24-hour cache TTL
Smogon usage stats update monthly. 24h TTL balances freshness vs. API load.
Offline fallback serves stale cache rather than failing.

## D4: MCP stdio transport
Standard for Claude Code integration. No HTTP server needed; Claude Code spawns the process.

## D5: Format data must carry a verification date and re-check trigger
2026-08-07 audit found the format assumptions baked into the skill/memory at design
time (2026-06-18) were inverted on two mechanics: Terastallization was recorded as
active when Reg M-B actually has it disabled (Mega Evolution active instead), and the
Showdown format ID (`gen9pokemonchampions`) never matched anything real
(`gen9championsvgc2026regmb`). Regulations rotate every ~2-3 months and can flip core
mechanics, not just the threat list — `memory/format_data.md` and
`data/formats/champions-mb.json` now carry a `metaVerifiedDate`/regulation window and
an explicit instruction to re-verify mechanics (not just topThreats) on every
regulation change. Don't trust the skill's embedded rules block without cross-checking
this date against the current regulation.
