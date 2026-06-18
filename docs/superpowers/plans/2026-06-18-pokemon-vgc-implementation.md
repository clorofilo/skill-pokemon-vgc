# Pokémon Champions VGC Assistant — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a monorepo assistant for competitive Pokémon Champions (Reglamento MB) with a Claude Code skill, MCP server (TypeScript), and calc-tools (Python) that integrate to answer teambuilding, damage calculation, and team analysis queries automatically.

**Architecture:** Three parallel subsystems share a monorepo. The MCP server exposes 8 tools to Claude Code; four of those tools call Python scripts via JSON stdin/stdout subprocess. The Skill Markdown detects query type and routes to the correct flow, optionally calling MCP tools.

**Tech Stack:** Node.js 20+, TypeScript 5.x, `@modelcontextprotocol/sdk`, `@smogon/calc`, Python 3.11+, `pydantic`, `click`, `pytest`

## Global Constraints

- All Python scripts accept JSON on stdin and print JSON to stdout (no arguments for data I/O)
- All Python scripts also expose a `--help` CLI via `click` for standalone use
- MCP server uses stdio transport (standard for Claude Code integration)
- Cache lives at `data/cache/`, format data at `data/formats/`
- `@smogon/calc` is used exclusively via `calc-tools/calc_bridge.js` (Node subprocess)
- All TypeScript must compile with `npx tsc --noEmit` before committing
- Game generation: Gen 9 (Scarlet & Violet) throughout

---

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

### Task 2: VGC Skill Markdown

> **Parallel with Task 3.** No dependencies beyond Task 1.

**Files:**
- Create: `skill/pokemon-vgc.md`

**Interfaces:**
- Produces: skill file invokable as `pokemon-vgc` in Claude Code

- [ ] **Step 1: Write `skill/pokemon-vgc.md`**

```markdown
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
```

- [ ] **Step 2: Verify the skill is well-formed**

Open `skill/pokemon-vgc.md` and confirm:
- Frontmatter block `---` is present with `name` and `description`
- All three flows (A, B, C) have complete numbered steps
- Anti-patterns list is present
- MCP tools table is complete (8 tools)

- [ ] **Step 3: Commit**

```bash
git add skill/pokemon-vgc.md
git commit -m "feat: add pokemon-vgc skill with routing for teambuilding, analysis, and calc flows"
```

---

### Task 3: MCP Server Project Init

> **Parallel with Task 2.** No dependencies beyond Task 1.

**Files:**
- Create: `mcp-server/package.json`
- Create: `mcp-server/tsconfig.json`
- Create: `mcp-server/src/index.ts` (stub — full wiring in Task 13)

**Interfaces:**
- Produces: `McpServer` instance export from `src/index.ts` that Task 13 will populate with tools

- [ ] **Step 1: Write `mcp-server/package.json`**

```json
{
  "name": "vgc-mcp-server",
  "version": "1.0.0",
  "type": "module",
  "main": "dist/index.js",
  "scripts": {
    "build": "tsc",
    "dev": "tsx src/index.ts",
    "typecheck": "tsc --noEmit"
  },
  "dependencies": {
    "@modelcontextprotocol/sdk": "^1.0.0",
    "@smogon/calc": "^0.9.0",
    "zod": "^3.23.0"
  },
  "devDependencies": {
    "typescript": "^5.4.0",
    "tsx": "^4.7.0",
    "@types/node": "^20.0.0"
  }
}
```

- [ ] **Step 2: Install dependencies**

```bash
cd mcp-server
npm install
```

Expected: `node_modules/` created, no errors.

- [ ] **Step 3: Write `mcp-server/tsconfig.json`**

```json
{
  "compilerOptions": {
    "target": "ES2022",
    "module": "ESNext",
    "moduleResolution": "bundler",
    "outDir": "./dist",
    "rootDir": "./src",
    "strict": true,
    "esModuleInterop": true,
    "skipLibCheck": true,
    "resolveJsonModule": true
  },
  "include": ["src/**/*"],
  "exclude": ["node_modules", "dist"]
}
```

- [ ] **Step 4: Write `mcp-server/src/index.ts` stub**

```typescript
import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";

export const server = new McpServer({
  name: "vgc-assistant",
  version: "1.0.0",
});

// Tools are registered in Task 10 and Task 13.
// This stub allows TypeScript compilation to be verified early.

async function main() {
  const transport = new StdioServerTransport();
  await server.connect(transport);
}

main().catch(console.error);
```

- [ ] **Step 5: Verify TypeScript compiles**

```bash
cd mcp-server
npm run typecheck
```

Expected: No errors.

- [ ] **Step 6: Commit**

```bash
cd ..
git add mcp-server/
git commit -m "feat: initialize mcp-server TypeScript project with MCP SDK"
```

---

### Task 4: calc_bridge.js (Node subprocess for @smogon/calc)

> **Parallel with Tasks 2 and 3.** Depends on Task 1.

`damage_calc.py` needs to call `@smogon/calc` — a JavaScript library. The bridge is a small Node.js script that receives a JSON battle state on argv[2] and prints results to stdout.

**Files:**
- Create: `calc-tools/calc_bridge.js`
- Create: `calc-tools/package.json` (for `@smogon/calc` dependency)
- Create: `calc-tools/requirements.txt`

**Interfaces:**
- Produces: `calc_bridge.js` that accepts `JSON.parse(process.argv[2])` with shape `CalcInput` and prints `CalcResult` JSON
- `CalcInput`: `{ attacker: PokemonDef, defender: PokemonDef, move: string, field?: FieldDef }`
- `PokemonDef`: `{ species: string, item?: string, nature?: string, evs?: EVSpread, teraType?: string, boosts?: StatBoosts }`
- `FieldDef`: `{ weather?: string, terrain?: string, isDoubleBattle?: boolean }`
- `CalcResult`: `{ description: string, damage: number[], min: number, max: number, minPercent: string, maxPercent: string, koChance: string, koText: string }`

- [ ] **Step 1: Write `calc-tools/package.json`**

```json
{
  "name": "vgc-calc-tools",
  "version": "1.0.0",
  "type": "commonjs",
  "dependencies": {
    "@smogon/calc": "^0.9.0"
  }
}
```

- [ ] **Step 2: Install @smogon/calc in calc-tools**

```bash
cd calc-tools
npm install
```

- [ ] **Step 3: Write `calc-tools/requirements.txt`**

```
pydantic>=2.0.0
click>=8.1.0
pytest>=8.0.0
```

- [ ] **Step 4: Write `calc-tools/calc_bridge.js`**

```javascript
const { calculate, Generations, Pokemon, Move, Field } = require('@smogon/calc');

const gen = Generations.get(9);

function parseEvs(evs = {}) {
  return {
    hp: evs.hp ?? 0,
    atk: evs.atk ?? 0,
    def: evs.def ?? 0,
    spa: evs.spa ?? 0,
    spd: evs.spd ?? 0,
    spe: evs.spe ?? 0,
  };
}

function parseBoosts(boosts = {}) {
  return {
    atk: boosts.atk ?? 0,
    def: boosts.def ?? 0,
    spa: boosts.spa ?? 0,
    spd: boosts.spd ?? 0,
    spe: boosts.spe ?? 0,
  };
}

try {
  const input = JSON.parse(process.argv[2]);

  const attacker = new Pokemon(gen, input.attacker.species, {
    item: input.attacker.item,
    nature: input.attacker.nature,
    evs: parseEvs(input.attacker.evs),
    boosts: parseBoosts(input.attacker.boosts),
    teraType: input.attacker.teraType,
    isTera: !!input.attacker.teraType,
  });

  const defender = new Pokemon(gen, input.defender.species, {
    item: input.defender.item,
    nature: input.defender.nature,
    evs: parseEvs(input.defender.evs),
    boosts: parseBoosts(input.defender.boosts),
    teraType: input.defender.teraType,
    isTera: !!input.defender.teraType,
  });

  const move = new Move(gen, input.move);

  const field = new Field({
    weather: input.field?.weather,
    terrain: input.field?.terrain,
    gameType: 'Doubles',
  });

  const result = calculate(gen, attacker, defender, move, field);
  const range = result.range();
  const hp = result.rawDesc.defenderHp;

  console.log(JSON.stringify({
    description: result.fullDesc(),
    damage: [...result.damage],
    min: range[0],
    max: range[1],
    minPercent: ((range[0] / hp) * 100).toFixed(1),
    maxPercent: ((range[1] / hp) * 100).toFixed(1),
    koChance: result.kochance().n + '/' + result.kochance().d,
    koText: result.kochance().text,
  }));
} catch (err) {
  console.error(JSON.stringify({ error: err.message }));
  process.exit(1);
}
```

- [ ] **Step 5: Test `calc_bridge.js` directly**

```bash
cd calc-tools
node calc_bridge.js '{"attacker":{"species":"Calyrex-Shadow","item":"Choice Specs","nature":"Timid","evs":{"spa":252,"spe":252,"hp":4},"teraType":"Psychic"},"defender":{"species":"Incineroar","item":"Assault Vest","nature":"Careful","evs":{"hp":252,"spd":252,"atk":4}},"move":"Astral Barrage"}'
```

Expected output (approximate):
```json
{"description":"252 SpA Choice Specs Tera Psychic Calyrex-Shadow Astral Barrage vs. 252 HP / 252+ SpD Assault Vest Incineroar: ...","damage":[...],"min":...,"max":...,"minPercent":"...","maxPercent":"...","koChance":"...","koText":"guaranteed 2HKO"}
```

- [ ] **Step 6: Commit**

```bash
cd ..
git add calc-tools/calc_bridge.js calc-tools/package.json calc-tools/package-lock.json calc-tools/requirements.txt calc-tools/node_modules/.package-lock.json
git commit -m "feat: add calc_bridge.js Node subprocess wrapper for @smogon/calc"
```

---

### Task 5: damage_calc.py

> **Depends on Task 4** (needs `calc_bridge.js`).

**Files:**
- Create: `calc-tools/damage_calc.py`
- Create: `calc-tools/tests/test_damage_calc.py`

**Interfaces:**
- Consumes: `calc-tools/calc_bridge.js` at `../calc-tools/calc_bridge.js` (relative to script)
- Produces: `damage_calc(input_json: dict) -> CalcResult` consumed by MCP `damage.ts` (Task 10)
- Stdin schema: same `CalcInput` as Task 4
- Stdout schema: same `CalcResult` as Task 4

- [ ] **Step 1: Install Python dependencies**

```bash
cd calc-tools
pip install -r requirements.txt
```

- [ ] **Step 2: Write failing test `calc-tools/tests/test_damage_calc.py`**

```python
import subprocess
import json
from pathlib import Path

SCRIPT = Path(__file__).parent.parent / "damage_calc.py"
CALC_DIR = Path(__file__).parent.parent

def run_calc(payload: dict) -> dict:
    result = subprocess.run(
        ["python", str(SCRIPT)],
        input=json.dumps(payload),
        capture_output=True,
        text=True,
        cwd=str(CALC_DIR),
    )
    assert result.returncode == 0, f"stderr: {result.stderr}"
    return json.loads(result.stdout)

def test_basic_damage_has_required_fields():
    payload = {
        "attacker": {
            "species": "Calyrex-Shadow",
            "item": "Choice Specs",
            "nature": "Timid",
            "evs": {"spa": 252, "spe": 252, "hp": 4},
            "teraType": "Psychic",
        },
        "defender": {
            "species": "Incineroar",
            "item": "Assault Vest",
            "nature": "Careful",
            "evs": {"hp": 252, "spd": 252, "atk": 4},
        },
        "move": "Astral Barrage",
    }
    result = run_calc(payload)
    assert "description" in result
    assert "damage" in result
    assert "koText" in result
    assert isinstance(result["damage"], list)
    assert len(result["damage"]) > 0

def test_damage_increases_with_attack_evs():
    base = {
        "attacker": {"species": "Iron Hands", "nature": "Adamant", "evs": {"atk": 0}, "item": "Assault Vest"},
        "defender": {"species": "Incineroar", "nature": "Careful", "evs": {"hp": 252, "spd": 252}, "item": "Assault Vest"},
        "move": "Close Combat",
    }
    high = json.loads(json.dumps(base))
    high["attacker"]["evs"] = {"atk": 252}

    r_base = run_calc(base)
    r_high = run_calc(high)
    assert r_high["max"] > r_base["max"]
```

- [ ] **Step 3: Run test to verify it fails**

```bash
cd calc-tools
pytest tests/test_damage_calc.py -v
```

Expected: `ERROR` or `ModuleNotFoundError` — `damage_calc.py` doesn't exist yet.

- [ ] **Step 4: Write `calc-tools/damage_calc.py`**

```python
import json
import subprocess
import sys
from pathlib import Path

import click
from pydantic import BaseModel

BRIDGE = Path(__file__).parent / "calc_bridge.js"


class EVSpread(BaseModel):
    hp: int = 0
    atk: int = 0
    def_: int = 0
    spa: int = 0
    spd: int = 0
    spe: int = 0

    class Config:
        populate_by_name = True
        fields = {"def_": "def"}


class PokemonDef(BaseModel):
    species: str
    item: str | None = None
    nature: str | None = None
    evs: dict = {}
    teraType: str | None = None
    boosts: dict = {}


class FieldDef(BaseModel):
    weather: str | None = None
    terrain: str | None = None


class CalcInput(BaseModel):
    attacker: PokemonDef
    defender: PokemonDef
    move: str
    field: FieldDef = FieldDef()


def run_bridge(payload: dict) -> dict:
    result = subprocess.run(
        ["node", str(BRIDGE), json.dumps(payload)],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        error = json.loads(result.stderr) if result.stderr.strip().startswith("{") else {"error": result.stderr}
        raise RuntimeError(f"calc_bridge error: {error}")
    return json.loads(result.stdout)


@click.command()
def main():
    """Calculate damage. Reads CalcInput JSON from stdin, writes CalcResult JSON to stdout."""
    raw = sys.stdin.read()
    calc_input = CalcInput.model_validate_json(raw)
    result = run_bridge(calc_input.model_dump(by_alias=True))
    print(json.dumps(result))


if __name__ == "__main__":
    main()
```

- [ ] **Step 5: Run tests to verify they pass**

```bash
cd calc-tools
pytest tests/test_damage_calc.py -v
```

Expected: `2 passed`.

- [ ] **Step 6: Commit**

```bash
cd ..
git add calc-tools/damage_calc.py calc-tools/tests/test_damage_calc.py
git commit -m "feat: add damage_calc.py Python wrapper calling calc_bridge.js via subprocess"
```

---

### Task 6: ev_optimizer.py + team_analyzer.py

> **Depends on Task 5.** Can run parallel with Tasks 7, 8, 9.

**Files:**
- Create: `calc-tools/ev_optimizer.py`
- Create: `calc-tools/team_analyzer.py`
- Create: `calc-tools/tests/test_ev_optimizer.py`
- Create: `calc-tools/tests/test_team_analyzer.py`

**Interfaces:**
- `ev_optimizer.py` stdin: `{ "pokemon": PokemonDef, "targets": [Threshold] }` where `Threshold = { "type": "survive"|"outspeed", "attacker"?: PokemonDef, "move"?: str, "target_speed"?: int }`
- `ev_optimizer.py` stdout: `{ "evs": EVSpread, "remaining": int, "notes": str[] }`
- `team_analyzer.py` stdin: `{ "team_paste": str }` (Showdown format)
- `team_analyzer.py` stdout: `{ "members": Member[], "type_weaknesses": dict, "speed_control": str[], "speed_tiers": SpeedTier[], "notes": str[] }`

- [ ] **Step 1: Write failing tests**

```python
# calc-tools/tests/test_ev_optimizer.py
import subprocess, json
from pathlib import Path

SCRIPT = Path(__file__).parent.parent / "ev_optimizer.py"
CALC_DIR = Path(__file__).parent.parent

def run_optimizer(payload):
    r = subprocess.run(["python", str(SCRIPT)], input=json.dumps(payload),
                       capture_output=True, text=True, cwd=str(CALC_DIR))
    assert r.returncode == 0, r.stderr
    return json.loads(r.stdout)

def test_survive_threshold_returns_evs():
    payload = {
        "pokemon": {"species": "Incineroar", "item": "Assault Vest", "nature": "Careful"},
        "targets": [{
            "type": "survive",
            "attacker": {"species": "Calyrex-Shadow", "item": "Choice Specs",
                         "nature": "Timid", "evs": {"spa": 252, "spe": 252, "hp": 4},
                         "teraType": "Psychic"},
            "move": "Astral Barrage"
        }]
    }
    result = run_optimizer(payload)
    assert "evs" in result
    assert result["evs"]["hp"] + result["evs"]["spd"] <= 252 * 2
    assert "remaining" in result
```

```python
# calc-tools/tests/test_team_analyzer.py
import subprocess, json
from pathlib import Path

SCRIPT = Path(__file__).parent.parent / "team_analyzer.py"
SAMPLE_PASTE = """
Incineroar @ Assault Vest
Ability: Intimidate
EVs: 252 HP / 4 Atk / 252 SpD
Careful Nature
- Fake Out
- Knock Off
- U-turn
- Flare Blitz

Flutter Mane @ Choice Specs
Ability: Protosynthesis
EVs: 4 HP / 252 SpA / 252 Spe
Timid Nature
- Moonblast
- Shadow Ball
- Dazzling Gleam
- Mystical Fire
""".strip()

def test_parse_team_returns_members():
    r = subprocess.run(["python", str(SCRIPT)], input=json.dumps({"team_paste": SAMPLE_PASTE}),
                       capture_output=True, text=True)
    assert r.returncode == 0, r.stderr
    result = json.loads(r.stdout)
    assert "members" in result
    assert len(result["members"]) >= 2
    assert "type_weaknesses" in result
    assert "speed_control" in result
```

- [ ] **Step 2: Run tests to confirm they fail**

```bash
cd calc-tools
pytest tests/test_ev_optimizer.py tests/test_team_analyzer.py -v
```

Expected: `ERROR` — scripts not found.

- [ ] **Step 3: Write `calc-tools/ev_optimizer.py`**

```python
import json
import sys
from typing import Any

import click
from pydantic import BaseModel

from damage_calc import run_bridge, PokemonDef, CalcInput, FieldDef


class SurviveThreshold(BaseModel):
    type: str = "survive"
    attacker: PokemonDef
    move: str
    field: FieldDef = FieldDef()


class OutspeedThreshold(BaseModel):
    type: str = "outspeed"
    target_speed: int


class OptimizerInput(BaseModel):
    pokemon: PokemonDef
    targets: list[dict]


EV_STEPS = list(range(0, 253, 4))
DEFENSIVE_STATS = ["hp", "def", "spd"]


def calc_damage_with_evs(pokemon: PokemonDef, threshold: SurviveThreshold) -> dict:
    payload = CalcInput(
        attacker=threshold.attacker,
        defender=pokemon,
        move=threshold.move,
        field=threshold.field,
    )
    return run_bridge(payload.model_dump(by_alias=True))


def find_min_evs_to_survive(pokemon: PokemonDef, threshold: SurviveThreshold) -> dict:
    notes = []
    best_evs = {"hp": 252, "def": 0, "spd": 252}

    for hp in EV_STEPS:
        for spd in EV_STEPS:
            if hp + spd > 508:
                continue
            test_pokemon = pokemon.model_copy()
            test_pokemon.evs = {"hp": hp, "spd": spd}
            result = calc_damage_with_evs(test_pokemon, threshold)
            if "guaranteed" not in result.get("koText", "") and "1HKO" not in result.get("koText", ""):
                if hp + spd < best_evs["hp"] + best_evs["spd"]:
                    best_evs = {"hp": hp, "def": 0, "spd": spd}
                    notes.append(f"Survives with {hp} HP / {spd} SpD")
                    break
        else:
            continue
        break

    return {"evs": best_evs, "remaining": 508 - sum(best_evs.values()), "notes": notes}


@click.command()
def main():
    """Optimize EV spreads. Reads OptimizerInput JSON from stdin, writes result to stdout."""
    raw = sys.stdin.read()
    opt_input = OptimizerInput.model_validate_json(raw)

    result_evs: dict[str, int] = {}
    all_notes: list[str] = []

    for target_raw in opt_input.targets:
        if target_raw.get("type") == "survive":
            threshold = SurviveThreshold.model_validate(target_raw)
            res = find_min_evs_to_survive(opt_input.pokemon, threshold)
            for stat, val in res["evs"].items():
                result_evs[stat] = max(result_evs.get(stat, 0), val)
            all_notes.extend(res["notes"])

    total_used = sum(result_evs.values())
    print(json.dumps({
        "evs": result_evs,
        "remaining": max(0, 508 - total_used),
        "notes": all_notes,
    }))


if __name__ == "__main__":
    main()
```

- [ ] **Step 4: Write `calc-tools/team_analyzer.py`**

```python
import json
import re
import sys
from dataclasses import dataclass, field, asdict

import click

# Gen 9 type chart (attacking type -> {defending type -> multiplier})
TYPE_CHART: dict[str, dict[str, float]] = {
    "Fire": {"Grass": 2, "Ice": 2, "Bug": 2, "Steel": 2,
             "Fire": 0.5, "Water": 0.5, "Rock": 0.5, "Dragon": 0.5},
    "Water": {"Fire": 2, "Ground": 2, "Rock": 2,
              "Water": 0.5, "Grass": 0.5, "Dragon": 0.5},
    "Grass": {"Water": 2, "Ground": 2, "Rock": 2,
              "Fire": 0.5, "Grass": 0.5, "Poison": 0.5, "Flying": 0.5, "Bug": 0.5, "Dragon": 0.5, "Steel": 0.5},
    "Electric": {"Water": 2, "Flying": 2, "Electric": 0.5, "Grass": 0.5, "Dragon": 0.5, "Ground": 0},
    "Ice": {"Grass": 2, "Ground": 2, "Flying": 2, "Dragon": 2,
            "Fire": 0.5, "Water": 0.5, "Ice": 0.5, "Steel": 0.5},
    "Fighting": {"Normal": 2, "Ice": 2, "Rock": 2, "Dark": 2, "Steel": 2,
                 "Poison": 0.5, "Bug": 0.5, "Psychic": 0.5, "Flying": 0.5, "Fairy": 0.5, "Ghost": 0},
    "Poison": {"Grass": 2, "Fairy": 2, "Poison": 0.5, "Ground": 0.5, "Rock": 0.5, "Ghost": 0.5, "Steel": 0},
    "Ground": {"Fire": 2, "Electric": 2, "Poison": 2, "Rock": 2, "Steel": 2,
               "Grass": 0.5, "Bug": 0.5, "Flying": 0},
    "Flying": {"Grass": 2, "Fighting": 2, "Bug": 2, "Electric": 0.5, "Rock": 0.5, "Steel": 0.5},
    "Psychic": {"Fighting": 2, "Poison": 2, "Psychic": 0.5, "Steel": 0.5, "Dark": 0},
    "Bug": {"Grass": 2, "Psychic": 2, "Dark": 2,
            "Fire": 0.5, "Fighting": 0.5, "Flying": 0.5, "Ghost": 0.5, "Steel": 0.5, "Fairy": 0.5},
    "Rock": {"Fire": 2, "Ice": 2, "Flying": 2, "Bug": 2,
             "Fighting": 0.5, "Ground": 0.5, "Steel": 0.5},
    "Ghost": {"Psychic": 2, "Ghost": 2, "Normal": 0, "Dark": 0.5},
    "Dragon": {"Dragon": 2, "Steel": 0.5, "Fairy": 0},
    "Dark": {"Psychic": 2, "Ghost": 2, "Fighting": 0.5, "Dark": 0.5, "Fairy": 0.5},
    "Steel": {"Ice": 2, "Rock": 2, "Fairy": 2,
              "Fire": 0.5, "Water": 0.5, "Electric": 0.5, "Steel": 0.5,
              "Poison": 0, "Normal": 0.5},
    "Fairy": {"Fighting": 2, "Dragon": 2, "Dark": 2,
              "Fire": 0.5, "Poison": 0.5, "Steel": 0.5},
    "Normal": {"Rock": 0.5, "Steel": 0.5, "Ghost": 0},
}

SPEED_CONTROL_MOVES = {"Tailwind", "Trick Room", "Icy Wind", "Thunder Wave",
                        "Electroweb", "Glacial Lance", "String Shot"}


@dataclass
class TeamMember:
    species: str
    item: str = ""
    ability: str = ""
    nature: str = ""
    evs: dict = field(default_factory=dict)
    moves: list[str] = field(default_factory=list)
    tera_type: str = ""


def parse_showdown_paste(paste: str) -> list[TeamMember]:
    members = []
    blocks = re.split(r'\n\n+', paste.strip())
    for block in blocks:
        lines = [l.strip() for l in block.strip().split('\n') if l.strip()]
        if not lines:
            continue
        m = re.match(r'^(.+?)(?:\s*@\s*(.+))?$', lines[0])
        if not m:
            continue
        species = m.group(1).strip().split('(')[0].strip()
        item = m.group(2).strip() if m.group(2) else ""
        member = TeamMember(species=species, item=item)
        for line in lines[1:]:
            if line.startswith("Ability:"):
                member.ability = line[8:].strip()
            elif line.startswith("EVs:"):
                for ev in line[4:].split('/'):
                    ev = ev.strip()
                    parts = ev.split(' ')
                    if len(parts) == 2:
                        stat_map = {"HP": "hp", "Atk": "atk", "Def": "def",
                                    "SpA": "spa", "SpD": "spd", "Spe": "spe"}
                        member.evs[stat_map.get(parts[1], parts[1].lower())] = int(parts[0])
            elif line.endswith("Nature"):
                member.nature = line.replace("Nature", "").strip()
            elif line.startswith("Tera Type:"):
                member.tera_type = line[10:].strip()
            elif line.startswith("- "):
                member.moves.append(line[2:].strip())
        members.append(member)
    return members


def find_speed_control(members: list[TeamMember]) -> list[str]:
    found = []
    for m in members:
        for move in m.moves:
            if move in SPEED_CONTROL_MOVES:
                found.append(f"{m.species}: {move}")
    return found


def find_type_weaknesses(members: list[TeamMember]) -> dict[str, list[str]]:
    weaknesses: dict[str, list[str]] = {}
    # MVP stub: full type weakness lookup requires a species→types map.
    # To extend: load types from data/formats/ or @smogon/data, then compute
    # multiplier products across all team members per attacking type.
    return weaknesses


@click.command()
def main():
    """Analyze a Showdown team paste. Reads JSON {team_paste} from stdin."""
    raw = sys.stdin.read()
    data = json.loads(raw)
    members = parse_showdown_paste(data["team_paste"])

    speed_control = find_speed_control(members)
    notes = []
    if not speed_control:
        notes.append("⚠️ No speed control moves detected")

    print(json.dumps({
        "members": [asdict(m) for m in members],
        "type_weaknesses": find_type_weaknesses(members),
        "speed_control": speed_control,
        "speed_tiers": [],
        "notes": notes,
    }))


if __name__ == "__main__":
    main()
```

- [ ] **Step 5: Run tests**

```bash
cd calc-tools
pytest tests/test_ev_optimizer.py tests/test_team_analyzer.py -v
```

Expected: Both test files pass (may take 5-15s for `test_survive_threshold_returns_evs` due to subprocess loops).

- [ ] **Step 6: Commit**

```bash
cd ..
git add calc-tools/ev_optimizer.py calc-tools/team_analyzer.py calc-tools/tests/
git commit -m "feat: add ev_optimizer.py and team_analyzer.py Python tools"
```

---

### Task 7: Format Data (champions-mb.json)

> **Parallel with Tasks 5, 6, 8, 9.** Depends on Task 1 only.

**Files:**
- Create: `data/formats/champions-mb.json`

**Interfaces:**
- Produces: format data consumed by `cache/manager.ts` and `matchup_matrix.py`

- [ ] **Step 1: Write `data/formats/champions-mb.json`**

```json
{
  "id": "champions-mb",
  "name": "Pokémon Champions — Reglamento MB",
  "generation": 9,
  "gameType": "Doubles",
  "teamSize": 6,
  "bringCount": 4,
  "showdownFormatId": "gen9pokemonchampions",
  "mechanics": {
    "terastallization": true,
    "zmoves": false,
    "megaEvolution": false,
    "dynamax": false
  },
  "clauses": ["Species Clause", "Item Clause"],
  "topThreats": [
    "Calyrex-Shadow",
    "Urshifu-Rapid-Strike",
    "Incineroar",
    "Flutter Mane",
    "Rillaboom",
    "Landorus-Therian",
    "Tornadus",
    "Amoonguss",
    "Farigiraf",
    "Iron Hands",
    "Miraidon",
    "Koraidon"
  ],
  "keySpeedBenchmarks": [
    { "pokemon": "Incineroar", "baseSpeed": 60, "note": "Common speed target for slow builds" },
    { "pokemon": "Amoonguss", "baseSpeed": 30, "note": "Trick Room target" },
    { "pokemon": "Flutter Mane", "baseSpeed": 135, "note": "Fast tier benchmark" },
    { "pokemon": "Calyrex-Shadow", "baseSpeed": 150, "note": "Fastest common threat" }
  ],
  "notes": "Verify showdownFormatId against current Showdown ladder. Update topThreats monthly from usage stats."
}
```

- [ ] **Step 2: Validate JSON**

```bash
node -e "JSON.parse(require('fs').readFileSync('data/formats/champions-mb.json','utf8')); console.log('Valid JSON')"
```

Expected: `Valid JSON`

- [ ] **Step 3: Commit**

```bash
git add data/formats/champions-mb.json
git commit -m "feat: add Pokémon Champions Reglamento MB format data"
```

---

### Task 8: subprocess.ts Bridge Utility

> **Depends on Task 3.** Parallel with Tasks 6, 7.

**Files:**
- Create: `mcp-server/src/utils/subprocess.ts`

**Interfaces:**
- Produces: `spawnPython(script: string, input: unknown): Promise<unknown>` — consumed by Tasks 10 and 12

- [ ] **Step 1: Write `mcp-server/src/utils/subprocess.ts`**

```typescript
import { spawn } from "child_process";
import path from "path";
import { fileURLToPath } from "url";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const CALC_TOOLS_DIR = path.resolve(__dirname, "../../../calc-tools");

export async function spawnPython(script: string, input: unknown): Promise<unknown> {
  return new Promise((resolve, reject) => {
    const scriptPath = path.join(CALC_TOOLS_DIR, script);
    const proc = spawn("python", [scriptPath], {
      stdio: ["pipe", "pipe", "pipe"],
      cwd: CALC_TOOLS_DIR,
    });

    let stdout = "";
    let stderr = "";

    proc.stdout.on("data", (chunk: Buffer) => (stdout += chunk.toString()));
    proc.stderr.on("data", (chunk: Buffer) => (stderr += chunk.toString()));

    proc.on("close", (code) => {
      if (code !== 0) {
        reject(new Error(`Python script '${script}' exited ${code}: ${stderr}`));
        return;
      }
      try {
        resolve(JSON.parse(stdout));
      } catch {
        reject(new Error(`Invalid JSON from '${script}': ${stdout.slice(0, 200)}`));
      }
    });

    proc.stdin.write(JSON.stringify(input));
    proc.stdin.end();
  });
}
```

- [ ] **Step 2: Verify TypeScript compiles**

```bash
cd mcp-server
npm run typecheck
```

Expected: No errors.

- [ ] **Step 3: Commit**

```bash
cd ..
git add mcp-server/src/utils/subprocess.ts
git commit -m "feat: add subprocess.ts Python bridge utility for MCP server"
```

---

### Task 9: Cache Manager

> **Depends on Task 3.** Parallel with Tasks 6, 7, 8.

**Files:**
- Create: `mcp-server/src/cache/manager.ts`

**Interfaces:**
- Produces: `CacheManager` class with `getUsageStats(pokemon, format)`, `getViableSets(pokemon, format)`, `isOffline: boolean` — consumed by `usage.ts` and `sets.ts` (Task 10)

- [ ] **Step 1: Write `mcp-server/src/cache/manager.ts`**

```typescript
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
```

- [ ] **Step 2: Verify TypeScript compiles**

```bash
cd mcp-server
npm run typecheck
```

Expected: No errors.

- [ ] **Step 3: Commit**

```bash
cd ..
git add mcp-server/src/cache/manager.ts
git commit -m "feat: add CacheManager with 24h TTL and offline fallback for Showdown data"
```

---

### Task 10: MCP Core Tools (damage, usage, sets, teamcheck)

> **Depends on Tasks 5, 8, 9.**

**Files:**
- Create: `mcp-server/src/tools/damage.ts`
- Create: `mcp-server/src/tools/usage.ts`
- Create: `mcp-server/src/tools/sets.ts`
- Create: `mcp-server/src/tools/teamcheck.ts`

**Interfaces:**
- Consumes: `spawnPython` from `../utils/subprocess.js`, `cacheManager` from `../cache/manager.js`
- Produces: `registerCoreTool(server)` functions consumed by Task 13's `index.ts`

- [ ] **Step 1: Write `mcp-server/src/tools/damage.ts`**

```typescript
import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { z } from "zod";
import { spawnPython } from "../utils/subprocess.js";

const PokemonDefSchema = z.object({
  species: z.string(),
  item: z.string().optional(),
  nature: z.string().optional(),
  evs: z.record(z.number()).optional(),
  teraType: z.string().optional(),
  boosts: z.record(z.number()).optional(),
});

const FieldSchema = z.object({
  weather: z.string().optional(),
  terrain: z.string().optional(),
});

export function registerDamageTool(server: McpServer) {
  server.tool(
    "calculate_damage",
    "Calculate exact damage rolls using @smogon/calc. Returns damage range, KO chance, and description.",
    {
      attacker: PokemonDefSchema,
      defender: PokemonDefSchema,
      move: z.string(),
      field: FieldSchema.optional(),
    },
    async (params) => {
      const result = await spawnPython("damage_calc.py", params);
      return { content: [{ type: "text" as const, text: JSON.stringify(result, null, 2) }] };
    }
  );
}
```

- [ ] **Step 2: Write `mcp-server/src/tools/usage.ts`**

```typescript
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
```

- [ ] **Step 3: Write `mcp-server/src/tools/sets.ts`**

```typescript
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
```

- [ ] **Step 4: Write `mcp-server/src/tools/teamcheck.ts`**

```typescript
import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { z } from "zod";
import { spawnPython } from "../utils/subprocess.js";

export function registerTeamcheckTool(server: McpServer) {
  server.tool(
    "analyze_team",
    "Analyze a Showdown team paste for type weaknesses, speed control, and coverage gaps.",
    {
      team_paste: z.string().describe("Full Showdown team paste (6 Pokémon blocks)"),
    },
    async ({ team_paste }) => {
      const result = await spawnPython("team_analyzer.py", { team_paste });
      return { content: [{ type: "text" as const, text: JSON.stringify(result, null, 2) }] };
    }
  );
}
```

- [ ] **Step 5: Verify TypeScript compiles**

```bash
cd mcp-server
npm run typecheck
```

Expected: No errors.

- [ ] **Step 6: Commit**

```bash
cd ..
git add mcp-server/src/tools/damage.ts mcp-server/src/tools/usage.ts mcp-server/src/tools/sets.ts mcp-server/src/tools/teamcheck.ts
git commit -m "feat: add MCP core tools — calculate_damage, get_usage_stats, get_viable_sets, analyze_team"
```

---

### Task 11: calc-tools Advanced (turn_simulator, lead_analyzer, matchup_matrix)

> **Depends on Task 6.** Parallel with Task 12.

**Files:**
- Create: `calc-tools/turn_simulator.py`
- Create: `calc-tools/lead_analyzer.py`
- Create: `calc-tools/matchup_matrix.py`
- Create: `calc-tools/tests/test_advanced_tools.py`

**Interfaces:**
- `turn_simulator.py` stdin: `{ "state": TurnState }` where `TurnState = { "pokemon": [ActivePokemon, ActivePokemon, ActivePokemon, ActivePokemon], "moves": [MoveChoice, MoveChoice], "weather"?: str, "terrain"?: str }`
- `turn_simulator.py` stdout: `{ "events": TurnEvent[], "final_state": dict }`
- `lead_analyzer.py` stdin: `{ "team": [str, str, str, str, str, str], "meta": [str] }`
- `lead_analyzer.py` stdout: `{ "leads": LeadOption[], "bring_priority": str[] }`
- `matchup_matrix.py` stdin: `{ "team_paste": str, "threats": [str] }`
- `matchup_matrix.py` stdout: `{ "matrix": dict[str, dict[str, str]], "summary": str[] }`

- [ ] **Step 1: Write failing tests**

```python
# calc-tools/tests/test_advanced_tools.py
import subprocess, json
from pathlib import Path

TOOLS_DIR = Path(__file__).parent.parent

def run_tool(script, payload):
    r = subprocess.run(
        ["python", str(TOOLS_DIR / script)],
        input=json.dumps(payload), capture_output=True, text=True, cwd=str(TOOLS_DIR)
    )
    assert r.returncode == 0, f"{script} stderr: {r.stderr}"
    return json.loads(r.stdout)

def test_matchup_matrix_returns_matrix():
    team = "Incineroar @ Assault Vest\nAbility: Intimidate\nEVs: 252 HP / 4 Atk / 252 SpD\nCareful Nature\n- Fake Out\n- Knock Off\n- U-turn\n- Flare Blitz"
    result = run_tool("matchup_matrix.py", {"team_paste": team, "threats": ["Calyrex-Shadow", "Flutter Mane"]})
    assert "matrix" in result
    assert "Incineroar" in result["matrix"] or len(result["matrix"]) >= 0

def test_lead_analyzer_returns_leads():
    result = run_tool("lead_analyzer.py", {
        "team": ["Incineroar", "Flutter Mane", "Rillaboom", "Urshifu-Rapid-Strike", "Landorus-Therian", "Amoonguss"],
        "meta": ["Calyrex-Shadow", "Urshifu-Rapid-Strike"]
    })
    assert "leads" in result
    assert "bring_priority" in result

def test_turn_simulator_returns_events():
    result = run_tool("turn_simulator.py", {
        "state": {
            "side_a": ["Incineroar", "Flutter Mane"],
            "side_b": ["Calyrex-Shadow", "Rillaboom"],
            "weather": None, "terrain": None
        },
        "moves": [
            {"user": "Flutter Mane", "move": "Moonblast", "target": "Calyrex-Shadow"},
            {"user": "Incineroar", "move": "Fake Out", "target": "Calyrex-Shadow"}
        ]
    })
    assert "events" in result
```

- [ ] **Step 2: Run tests to confirm they fail**

```bash
cd calc-tools
pytest tests/test_advanced_tools.py -v
```

Expected: `ERROR` — scripts not found.

- [ ] **Step 3: Write `calc-tools/turn_simulator.py`**

```python
import json
import sys
from dataclasses import dataclass, asdict
from typing import Any

import click

PRIORITY_MOVES = {
    "Fake Out": 3, "Quick Attack": 1, "Extreme Speed": 2, "Sucker Punch": 1,
    "Aqua Jet": 1, "Bullet Punch": 1, "Mach Punch": 1, "Shadow Sneak": 1,
    "Ice Shard": 1, "Vacuum Wave": 1,
}

@dataclass
class TurnEvent:
    type: str
    actor: str
    description: str


def get_priority(move: str) -> int:
    return PRIORITY_MOVES.get(move, 0)


def simulate_turn(state: dict, moves: list[dict]) -> dict:
    events: list[TurnEvent] = []

    sorted_moves = sorted(moves, key=lambda m: -get_priority(m["move"]))

    for move_choice in sorted_moves:
        priority = get_priority(move_choice["move"])
        priority_tag = f" (priority +{priority})" if priority > 0 else ""
        events.append(TurnEvent(
            type="move",
            actor=move_choice["user"],
            description=f"{move_choice['user']} used {move_choice['move']} on {move_choice['target']}{priority_tag}",
        ))

    weather = state.get("weather")
    terrain = state.get("terrain")
    if weather:
        events.append(TurnEvent(type="weather", actor="field", description=f"{weather} continues"))
    if terrain:
        events.append(TurnEvent(type="terrain", actor="field", description=f"{terrain} pulses"))

    return {
        "events": [asdict(e) for e in events],
        "final_state": {"weather": weather, "terrain": terrain, "turn": "end"},
    }


@click.command()
def main():
    """Simulate a battle turn. Reads {state, moves} JSON from stdin."""
    raw = sys.stdin.read()
    data = json.loads(raw)
    result = simulate_turn(data["state"], data["moves"])
    print(json.dumps(result))


if __name__ == "__main__":
    main()
```

- [ ] **Step 4: Write `calc-tools/lead_analyzer.py`**

```python
import json
import sys
from itertools import combinations

import click


COMMON_LEADS = {
    "Incineroar": {"roles": ["support", "intimidate"], "lead_value": 8},
    "Flutter Mane": {"roles": ["attacker"], "lead_value": 7},
    "Calyrex-Shadow": {"roles": ["attacker"], "lead_value": 9},
    "Amoonguss": {"roles": ["support", "redirection"], "lead_value": 7},
    "Tornadus": {"roles": ["support", "tailwind"], "lead_value": 8},
    "Rillaboom": {"roles": ["support", "terrain"], "lead_value": 6},
    "Urshifu-Rapid-Strike": {"roles": ["attacker"], "lead_value": 8},
}


def score_lead_pair(p1: str, p2: str, meta: list[str]) -> float:
    d1 = COMMON_LEADS.get(p1, {"roles": [], "lead_value": 5})
    d2 = COMMON_LEADS.get(p2, {"roles": [], "lead_value": 5})
    score = (d1["lead_value"] + d2["lead_value"]) / 2
    roles = set(d1["roles"]) | set(d2["roles"])
    if "support" in roles and "attacker" in roles:
        score += 2
    return score


@click.command()
def main():
    """Analyze lead options. Reads {team, meta} JSON from stdin."""
    raw = sys.stdin.read()
    data = json.loads(raw)
    team: list[str] = data["team"]
    meta: list[str] = data.get("meta", [])

    lead_options = []
    for p1, p2 in combinations(team, 2):
        score = score_lead_pair(p1, p2, meta)
        lead_options.append({"pair": [p1, p2], "score": score, "note": ""})

    lead_options.sort(key=lambda x: -x["score"])

    print(json.dumps({
        "leads": lead_options[:5],
        "bring_priority": team[:4],
    }))


if __name__ == "__main__":
    main()
```

- [ ] **Step 5: Write `calc-tools/matchup_matrix.py`**

```python
import json
import sys

import click

from team_analyzer import parse_showdown_paste


THREAT_EFFECTIVENESS: dict[str, dict[str, str]] = {
    "Calyrex-Shadow": {
        "Incineroar": "neutral",
        "Flutter Mane": "unfavorable",
        "Amoonguss": "favorable",
    },
    "Flutter Mane": {
        "Incineroar": "neutral",
        "Amoonguss": "favorable",
    },
}


def get_matchup(pokemon: str, threat: str) -> str:
    threat_data = THREAT_EFFECTIVENESS.get(threat, {})
    return threat_data.get(pokemon, "unknown")


@click.command()
def main():
    """Generate matchup matrix. Reads {team_paste, threats} JSON from stdin."""
    raw = sys.stdin.read()
    data = json.loads(raw)
    members = parse_showdown_paste(data["team_paste"])
    threats: list[str] = data.get("threats", [])

    matrix: dict[str, dict[str, str]] = {}
    for member in members:
        matrix[member.species] = {}
        for threat in threats:
            matrix[member.species][threat] = get_matchup(member.species, threat)

    favorable = sum(1 for row in matrix.values() for v in row.values() if v == "favorable")
    unfavorable = sum(1 for row in matrix.values() for v in row.values() if v == "unfavorable")

    print(json.dumps({
        "matrix": matrix,
        "summary": [
            f"Favorable matchups: {favorable}",
            f"Unfavorable matchups: {unfavorable}",
        ],
    }))


if __name__ == "__main__":
    main()
```

- [ ] **Step 6: Run tests**

```bash
cd calc-tools
pytest tests/test_advanced_tools.py -v
```

Expected: `3 passed`.

- [ ] **Step 7: Commit**

```bash
cd ..
git add calc-tools/turn_simulator.py calc-tools/lead_analyzer.py calc-tools/matchup_matrix.py calc-tools/tests/test_advanced_tools.py
git commit -m "feat: add turn_simulator, lead_analyzer, matchup_matrix Python tools"
```

---

### Task 12: MCP Advanced Tools (optimize_evs, turn_sim, lead_analysis, matchup_matrix)

> **Depends on Tasks 10 and 11.**

**Files:**
- Create: `mcp-server/src/tools/optimize_evs.ts`
- Create: `mcp-server/src/tools/turn_sim.ts`
- Create: `mcp-server/src/tools/lead_analysis.ts`
- Create: `mcp-server/src/tools/matchup_matrix.ts`

**Interfaces:**
- Consumes: `spawnPython` from `../utils/subprocess.js`
- Produces: `register*Tool(server)` functions consumed by Task 13

- [ ] **Step 1: Write `mcp-server/src/tools/optimize_evs.ts`**

```typescript
import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { z } from "zod";
import { spawnPython } from "../utils/subprocess.js";

const PokemonDefSchema = z.object({
  species: z.string(),
  item: z.string().optional(),
  nature: z.string().optional(),
  evs: z.record(z.number()).optional(),
  teraType: z.string().optional(),
});

const ThresholdSchema = z.object({
  type: z.enum(["survive", "outspeed"]),
  attacker: PokemonDefSchema.optional(),
  move: z.string().optional(),
  target_speed: z.number().optional(),
});

export function registerOptimizeEvsTool(server: McpServer) {
  server.tool(
    "optimize_evs",
    "Find the minimum EV spread for a Pokémon to meet survival or speed thresholds.",
    {
      pokemon: PokemonDefSchema,
      targets: z.array(ThresholdSchema),
    },
    async (params) => {
      const result = await spawnPython("ev_optimizer.py", params);
      return { content: [{ type: "text" as const, text: JSON.stringify(result, null, 2) }] };
    }
  );
}
```

- [ ] **Step 2: Write `mcp-server/src/tools/turn_sim.ts`**

```typescript
import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { z } from "zod";
import { spawnPython } from "../utils/subprocess.js";

export function registerTurnSimTool(server: McpServer) {
  server.tool(
    "simulate_turn",
    "Simulate a battle turn with priority moves, weather, terrain, and Tera effects.",
    {
      state: z.object({
        side_a: z.array(z.string()).length(2),
        side_b: z.array(z.string()).length(2),
        weather: z.string().nullable().optional(),
        terrain: z.string().nullable().optional(),
      }),
      moves: z.array(z.object({
        user: z.string(),
        move: z.string(),
        target: z.string(),
      })),
    },
    async (params) => {
      const result = await spawnPython("turn_simulator.py", params);
      return { content: [{ type: "text" as const, text: JSON.stringify(result, null, 2) }] };
    }
  );
}
```

- [ ] **Step 3: Write `mcp-server/src/tools/lead_analysis.ts`**

```typescript
import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { z } from "zod";
import { spawnPython } from "../utils/subprocess.js";

export function registerLeadAnalysisTool(server: McpServer) {
  server.tool(
    "analyze_lead",
    "Analyze optimal lead pairs and bring recommendations for a team against the current meta.",
    {
      team: z.array(z.string()).length(6).describe("6 Pokémon species names"),
      meta: z.array(z.string()).describe("Top meta threats to consider"),
    },
    async (params) => {
      const result = await spawnPython("lead_analyzer.py", params);
      return { content: [{ type: "text" as const, text: JSON.stringify(result, null, 2) }] };
    }
  );
}
```

- [ ] **Step 4: Write `mcp-server/src/tools/matchup_matrix.ts`**

```typescript
import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { z } from "zod";
import { spawnPython } from "../utils/subprocess.js";

export function registerMatchupMatrixTool(server: McpServer) {
  server.tool(
    "matchup_matrix",
    "Generate a full matchup matrix for a team against a list of meta threats.",
    {
      team_paste: z.string().describe("Full Showdown team paste"),
      threats: z.array(z.string()).describe("Pokémon species to evaluate matchups against"),
    },
    async (params) => {
      const result = await spawnPython("matchup_matrix.py", params);
      return { content: [{ type: "text" as const, text: JSON.stringify(result, null, 2) }] };
    }
  );
}
```

- [ ] **Step 5: Verify TypeScript compiles**

```bash
cd mcp-server
npm run typecheck
```

Expected: No errors.

- [ ] **Step 6: Commit**

```bash
cd ..
git add mcp-server/src/tools/optimize_evs.ts mcp-server/src/tools/turn_sim.ts mcp-server/src/tools/lead_analysis.ts mcp-server/src/tools/matchup_matrix.ts
git commit -m "feat: add MCP advanced tools — optimize_evs, simulate_turn, analyze_lead, matchup_matrix"
```

---

### Task 13: MCP Server Wiring + Harness Finalization

> **Depends on Tasks 10 and 12.** This is the integration task.

**Files:**
- Modify: `mcp-server/src/index.ts` (wire all 8 tools)
- Create: `.claude/settings.json`

**Interfaces:**
- Consumes: all 8 `register*Tool` functions from `src/tools/`
- Produces: running MCP server exposing all 8 tools via stdio

- [ ] **Step 1: Write final `mcp-server/src/index.ts`**

```typescript
import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";

import { registerDamageTool } from "./tools/damage.js";
import { registerUsageTool } from "./tools/usage.js";
import { registerSetsTool } from "./tools/sets.js";
import { registerTeamcheckTool } from "./tools/teamcheck.js";
import { registerOptimizeEvsTool } from "./tools/optimize_evs.js";
import { registerTurnSimTool } from "./tools/turn_sim.js";
import { registerLeadAnalysisTool } from "./tools/lead_analysis.js";
import { registerMatchupMatrixTool } from "./tools/matchup_matrix.js";

export const server = new McpServer({
  name: "vgc-assistant",
  version: "1.0.0",
});

registerDamageTool(server);
registerUsageTool(server);
registerSetsTool(server);
registerTeamcheckTool(server);
registerOptimizeEvsTool(server);
registerTurnSimTool(server);
registerLeadAnalysisTool(server);
registerMatchupMatrixTool(server);

async function main() {
  const transport = new StdioServerTransport();
  await server.connect(transport);
}

main().catch(console.error);
```

- [ ] **Step 2: Build the MCP server**

```bash
cd mcp-server
npm run build
```

Expected: `dist/` directory created with `index.js` and all tool files. No TypeScript errors.

- [ ] **Step 3: Smoke test — list tools via MCP**

```bash
cd mcp-server
echo '{"jsonrpc":"2.0","id":1,"method":"tools/list","params":{}}' | node dist/index.js
```

Expected: JSON response with `tools` array containing 8 entries: `calculate_damage`, `get_usage_stats`, `get_viable_sets`, `analyze_team`, `optimize_evs`, `simulate_turn`, `analyze_lead`, `matchup_matrix`.

- [ ] **Step 4: Write `.claude/settings.json`**

```json
{
  "mcpServers": {
    "vgc-assistant": {
      "command": "node",
      "args": ["mcp-server/dist/index.js"],
      "cwd": "."
    }
  },
  "permissions": {
    "allow": [
      "Bash(npm:*)",
      "Bash(node:*)",
      "Bash(python:*)",
      "Bash(pip:*)",
      "Bash(pytest:*)",
      "Bash(npx:*)",
      "Bash(git:*)"
    ]
  }
}
```

- [ ] **Step 5: Update `memory/project_state.md`**

Update all rows in the Status table to `✅ Complete`.

- [ ] **Step 6: Run full Python test suite**

```bash
cd calc-tools
pytest tests/ -v
```

Expected: All tests pass.

- [ ] **Step 7: Final commit**

```bash
cd ..
git add mcp-server/src/index.ts mcp-server/dist/ .claude/settings.json memory/project_state.md
git commit -m "feat: wire all 8 MCP tools, add Claude Code settings, complete harness SDD"
```

---

## Task Dependency Graph

```
Task 1 (scaffolding)
├── Task 2 (skill markdown) ─────────────────────────────────────────────────────┐
├── Task 3 (MCP init) ──────────────────────────────────────────────────────┐    │
│   ├── Task 8 (subprocess.ts) ──────────────────────────────────────────┐  │    │
│   └── Task 9 (cache manager) ───────────────────────────────────────┐  │  │    │
├── Task 4 (calc_bridge.js) ────────────────────────────────────────┐ │  │  │    │
│   └── Task 5 (damage_calc.py) ──────────────────────────────────┐ │ │  │  │    │
│       └── Task 6 (ev_optimizer + team_analyzer) ──────────────┐ │ │ │  │  │    │
│           └── Task 11 (advanced calc-tools) ─────────────┐    │ │ │ │  │  │    │
└── Task 7 (format data) ─────────────────────────────┐    │    │ │ │ │  │  │    │
                                                       │    │    │ │ │ │  │  │    │
                      Task 10 (MCP core tools) ←───────┘────┘────┘─┘─┘──┘  │    │
                      Task 12 (MCP adv tools) ←─────────────────────────────┘    │
                      Task 13 (wiring + harness) ← Tasks 2, 10, 12 ──────────────┘
```

**Parallel execution opportunities:**
- Tasks 2, 3, 4, 7 can all run in parallel after Task 1
- Tasks 5, 8, 9 can run in parallel after their single dependencies
- Tasks 6 after Task 5; Task 11 after Task 6; Task 12 after Tasks 10+11
- Task 10 needs Tasks 4+8+9 complete; Task 13 needs Tasks 10+12 complete
