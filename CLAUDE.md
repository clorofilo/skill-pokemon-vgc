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
