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
