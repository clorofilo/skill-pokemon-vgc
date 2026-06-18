### Task 1: Monorepo Scaffolding

**Files:**
- Create: `C:\Codigos\vgc-app\.gitignore`
- Create: `C:\Codigos\vgc-app\CLAUDE.md`
- Create: `C:\Codigos\vgc-app\memory\MEMORY.md`
- Create: `C:\Codigos\vgc-app\memory\project_state.md`
- Create: `C:\Codigos\vgc-app\memory\format_data.md`
- Create: `C:\Codigos\vgc-app\memory\decisions.md`
- Create: directory tree: `skill/`, `mcp-server/src/tools/`, `mcp-server/src/cache/`, `mcp-server/src/utils/`, `calc-tools/`, `data/cache/`, `data/formats/`

**Interfaces:**
- Produces: directory structure consumed by all subsequent tasks

- [ ] **Step 1: Initialize git and create directories**

```powershell
cd C:\Codigos\vgc-app
git init
mkdir skill, calc-tools, data\cache, data\formats, memory
mkdir mcp-server\src\tools, mcp-server\src\cache, mcp-server\src\utils
```

- [ ] **Step 2: Write `.gitignore`**

```
node_modules/
dist/
__pycache__/
*.pyc
.env
data/cache/*.json
*.log
```

- [ ] **Step 3: Write `CLAUDE.md`**

```markdown
# vgc-app — Pokémon Champions VGC Assistant

## Project Overview
Monorepo with three subsystems: VGC skill, MCP server (TypeScript), calc-tools (Python).
Format: Pokémon Champions — Reglamento MB (doubles, 6 pick 4, Tera active).

## Session Start Protocol
1. Read `memory/MEMORY.md` to load project context
2. Read `memory/project_state.md` to check current implementation status
3. Invoke `superpowers:subagent-driven-development` for parallel implementation tasks

## Skill
The file `skill/pokemon-vgc.md` is the VGC analysis skill. For any competitive Pokémon
question in this project, invoke it via the Skill tool as `pokemon-vgc`.

## MCP Server
- Start: `cd mcp-server && npm run dev`
- Config entry for Claude Code: add `mcp-server` as an MCP server with command `node dist/index.js`

## calc-tools
- Install: `cd calc-tools && pip install -r requirements.txt`
- Each script runs standalone: `echo '{"input": ...}' | python damage_calc.py`

## Key Decisions
See `memory/decisions.md`.
```

- [ ] **Step 4: Write `memory/MEMORY.md`**

```markdown
# Memory Index — vgc-app

- [Project State](project_state.md) — current implementation status per subsystem
- [Format Data](format_data.md) — Pokémon Champions Reglamento MB rules
- [Architecture Decisions](decisions.md) — key technical decisions and rationale
```

- [ ] **Step 5: Write `memory/project_state.md`**

```markdown
# Project State

## Subsystems

| Subsystem | Status | Notes |
|---|---|---|
| Monorepo scaffolding | ✅ Complete | Task 1 |
| skill/pokemon-vgc.md | ⏳ Pending | Task 2 |
| mcp-server init | ⏳ Pending | Task 3 |
| calc_bridge.js | ⏳ Pending | Task 4 |
| damage_calc.py | ⏳ Pending | Task 5 |
| ev_optimizer.py | ⏳ Pending | Task 6 |
| team_analyzer.py | ⏳ Pending | Task 6 |
| champions-mb.json | ⏳ Pending | Task 7 |
| subprocess.ts | ⏳ Pending | Task 8 |
| cache/manager.ts | ⏳ Pending | Task 9 |
| MCP core tools (4) | ⏳ Pending | Task 10 |
| calc-tools advanced (3) | ⏳ Pending | Task 11 |
| MCP advanced tools (4) | ⏳ Pending | Task 12 |
| MCP server wiring | ⏳ Pending | Task 13 |
```

- [ ] **Step 6: Write `memory/format_data.md`**

```markdown
# Pokémon Champions — Reglamento MB

## Battle Rules
- Format: VGC Doubles (2v2 per turn)
- Team: 6 Pokémon, bring 4 to battle
- Teracristallization: Active (1 per battle per side)
- Banned: Z-Moves, Mega Evolution, Dynamax/Gigantamax

## Clauses
- Species Clause: no duplicate species
- Item Clause: no duplicate held items

## Showdown Format ID
- `gen9pokemonchampions` (verify on Showdown ladder; may vary by series)

## Key Meta Threats (update as meta evolves)
- Calyrex-Shadow, Urshifu-Rapid-Strike, Incineroar, Flutter Mane, Rillaboom
- Landorus-T, Tornadus, Amoonguss, Farigiraf, Iron Hands
```

- [ ] **Step 7: Write `memory/decisions.md`**

```markdown
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
```

- [ ] **Step 8: Commit**

```bash
git add .
git commit -m "feat: initialize monorepo scaffolding and memory files"
```

---

