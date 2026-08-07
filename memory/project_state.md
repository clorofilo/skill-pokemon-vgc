# Project State

## Subsystems

| Subsystem | Status | Notes |
|---|---|---|
| Monorepo scaffolding | ✅ Complete | Task 1 |
| skill/pokemon-vgc.md | ✅ Complete | Task 2; corrected for Reg M-B 2026-08-07 |
| mcp-server init | ✅ Complete | Task 3; vitest added 2026-08-07 |
| calc_bridge.js | ✅ Complete | Task 4 |
| damage_calc.py | ✅ Complete | Task 5 |
| ev_optimizer.py | ✅ Complete | Task 6; 2 correctness bugs fixed 2026-08-07 |
| team_analyzer.py | ✅ Complete | Task 6; nickname-parsing bug fixed 2026-08-07 |
| champions-mb.json | ✅ Complete | Task 7; corrected for Reg M-B 2026-08-07 |
| subprocess.ts | ✅ Complete | Task 8; crash-on-ENOENT + timeout fixed 2026-08-07 |
| cache/manager.ts | ✅ Complete | Task 9; format-key cache bug fixed 2026-08-07 |
| MCP core tools (4) | ✅ Complete | Task 10 |
| calc-tools advanced (3) | ✅ Complete | Task 11 |
| MCP advanced tools (4) | ✅ Complete | Task 12 |
| MCP server wiring | ✅ Complete | Task 13 |

## 2026-08-07 audit + fix pass

Full review across mcp-server (TS), calc-tools (Python), and format currency (web
research). See [[decisions]] D5 for the format-data finding. Fixed with TDD (test
first, watched red, minimal fix, watched green):

- `team_analyzer.py`: nicknamed Showdown pastes (`Nickname (Species) @ Item`) parsed
  the nickname as species, breaking `matchup_matrix` lookups for any nicknamed mon.
- `ev_optimizer.py`: survive-threshold search locked onto the first HP value with any
  working SpD, never checking whether more HP investment gave a lower total (same bug
  class as the `e71ce68` outspeed fix). Rewrote as per-HP binary search + global min.
- `ev_optimizer.py`: `SPEED_BASES` table only covered the old (June 2026) meta —
  current Reg M-B threats like Garchomp silently fell back to base 80. Added current
  meta's base speeds and an explicit "assumed 80, verify" note for unknown species.
- `mcp-server/src/utils/subprocess.ts`: `spawn()` had no `error` listener — if Python
  isn't on PATH, Node's uncaught `error` event kills the *entire* MCP server, not just
  one tool call. Added the handler plus a 15s timeout so a hung script can't wedge a
  tool call forever. Added vitest (previously zero TS test coverage).
- `mcp-server/src/cache/manager.ts`: `getViableSets` ignored the `format` parameter in
  both the cache key and the fetch URL — different formats returned identical cached
  data. Cache key and URL now derive from `format`.
- `.claude/settings.json` (tracked in git): pointed at a stale path
  (`C:\Codigos\vgc-app\...`) from before the repo moved to
  `C:\Codigos\private\skill-pokemon-vgc`. Fixed to the current path — this file is
  machine-specific but version-controlled, worth revisiting (see recommendations).
- `docs/superpowers/sdd/progress.md` marked every task "pending" despite all being
  shipped; corrected against git log.

**Not fixed (lower severity, logged for later):** `cache/manager.ts` `isOffline` is a
shared mutable flag with a race under concurrent tool calls; zod schemas in
`optimize_evs.ts` under-validate vs. the Python pydantic models (a malformed
`survive` target throws a raw pydantic traceback instead of a clean MCP error); the 6
Python scripts' `main()` functions don't wrap stdin parsing in try/except, so bad
input surfaces as a raw traceback in stderr rather than structured JSON (subprocess.ts
still catches and rejects on it, so this is a UX/polish gap, not a crash).
