# vgc-app — Pokémon Champions VGC Assistant

Monorepo con tres subsistemas para análisis competitivo en el formato **Pokémon Champions Reglamento MB** (dobles, 6 registrar / 4 traer, Teracristalización activa).

---

## Estructura

```
vgc-app/
├── skill/
│   └── pokemon-vgc.md        # Skill de Claude Code (routing automático)
├── mcp-server/               # Servidor MCP en TypeScript (8 herramientas)
│   └── src/
│       ├── index.ts
│       ├── tools/            # damage, usage, sets, teamcheck, optimize_evs,
│       │                     # turn_sim, lead_analysis, matchup_matrix
│       └── cache/manager.ts  # Cache 24 h + fallback offline
├── calc-tools/               # Scripts Python standalone
│   ├── damage_calc.py
│   ├── ev_optimizer.py
│   ├── team_analyzer.py
│   ├── turn_simulator.py
│   ├── lead_analyzer.py
│   ├── matchup_matrix.py
│   └── tests/                # 31 tests (pytest)
├── data/
│   ├── cache/                # Cache local de Showdown/Smogon
│   └── formats/
│       └── champions-mb.json # Reglamento MB: reglas, banned list, benchmarks
└── memory/                   # Estado del proyecto entre sesiones
```

---

## Skill (`skill/pokemon-vgc.md`)

Skill de Claude Code con routing automático: detecta el tipo de consulta sin intervención del usuario y enruta al flujo correcto.

| Entrada | Flujo |
|---|---|
| "arma un equipo", idea de equipo | Teambuilding desde cero |
| Paste Showdown de un equipo | Análisis de equipo existente |
| "¿cuántos EVs para sobrevivir X?" | Cálculo de KOs y spreads |

### Uso en Claude Code

Añade en tu `settings.json`:

```json
{
  "mcpServers": {
    "vgc-assistant": {
      "command": "node",
      "args": ["mcp-server/dist/index.js"],
      "cwd": "."
    }
  }
}
```

Luego invoca la skill con `/pokemon-vgc` o simplemente pregunta sobre VGC — Claude la activa automáticamente.

---

## MCP Server (TypeScript)

### Requisitos

- Node.js 18+
- npm

### Instalación y build

```bash
cd mcp-server
npm install
npm run build        # genera dist/
npm run dev          # desarrollo con tsx (sin build)
npm run typecheck    # verificación de tipos
```

### Herramientas expuestas (8)

| Tool | Descripción |
|---|---|
| `calculate_damage` | Rango de daño exacto con rolls (usa `@smogon/calc`) |
| `get_usage_stats` | % de uso mensual desde Smogon Stats |
| `get_viable_sets` | Sets más comunes (items, moves, spreads) |
| `analyze_team` | Debilidades, speed control, speed tiers |
| `optimize_evs` | Spread mínimo por thresholds survive/outspeed |
| `simulate_turn` | Simulación de turno con prioridades, weather y terrain |
| `analyze_lead` | Mejores leads y bring recomendado |
| `matchup_matrix` | Matriz de matchups vs amenazas del meta |

### Prueba de humo

```bash
echo '{"jsonrpc":"2.0","id":1,"method":"tools/list","params":{}}' | node dist/index.js
```

Debe devolver los 8 tools registrados.

---

## calc-tools (Python)

Scripts independientes: cada uno acepta JSON por `stdin` y devuelve JSON por `stdout`. También usables por CLI directamente.

### Requisitos

- Python 3.9+
- Node.js (para `damage_calc.py` — llama a `@smogon/calc` via subprocess)

### Instalación

```bash
cd calc-tools
pip install -r requirements.txt
# También instalar dependencias Node en mcp-server/ para el bridge de daño:
cd ../mcp-server && npm install
```

### Scripts

```bash
# Cálculo de daño
echo '{"attacker":{"species":"Calyrex-Shadow","item":"Choice Specs","nature":"Timid","evs":{"spa":252},"teraType":"Psychic"},"defender":{"species":"Incineroar","item":"Assault Vest","nature":"Careful","evs":{"hp":252,"spd":252}},"move":"Astral Barrage"}' | python damage_calc.py

# Optimización de EVs
echo '{"pokemon":{"species":"Incineroar","item":"Assault Vest","nature":"Careful"},"targets":[{"type":"survive","attacker":{"species":"Calyrex-Shadow","item":"Choice Specs","nature":"Timid","evs":{"spa":252}},"move":"Astral Barrage"}]}' | python ev_optimizer.py

# Análisis de equipo (paste Showdown)
echo '{"team_paste":"Incineroar @ Assault Vest\nAbility: Intimidate\nEVs: 252 HP / 4 Atk / 252 SpD\nCareful Nature\n- Fake Out\n- Knock Off\n- U-turn\n- Flare Blitz"}' | python team_analyzer.py

# Simulación de turno
echo '{"state":{"side_a":["Incineroar","Flutter Mane"],"side_b":["Calyrex-Shadow","Rillaboom"],"weather":null,"terrain":null},"moves":[{"user":"Incineroar","move":"Fake Out","target":"Calyrex-Shadow"},{"user":"Flutter Mane","move":"Moonblast","target":"Calyrex-Shadow"}]}' | python turn_simulator.py

# Análisis de leads
echo '{"team":["Incineroar","Flutter Mane","Rillaboom","Urshifu-Rapid-Strike","Landorus-Therian","Amoonguss"],"meta":["Calyrex-Shadow"]}' | python lead_analyzer.py

# Matriz de matchups
echo '{"team_paste":"<paste>","threats":["Calyrex-Shadow","Flutter Mane"]}' | python matchup_matrix.py
```

### Tests

```bash
cd vgc-app   # raíz del repo
pytest calc-tools/tests/ -v
# 31 tests — cubre: priority ordering, weather/terrain, synergy bonus,
# matchup matrix, outspeed EVs, EV remaining, tera type, speed control...
```

---

## Formato: Pokémon Champions Reglamento MB

- **Modalidad:** Dobles
- **Equipo:** 6 Pokémon registrados, 4 traídos a batalla
- **Mecánicas activas:** Teracristalización
- **Mecánicas inactivas:** Z-moves, Mega Evolución, Dynamax/Gigamax
- **Generación:** 9 (Escarlata y Violeta)
- **Datos del formato:** `data/formats/champions-mb.json`

---

## Desarrollo

Este proyecto usa un harness SDD (Subagent-Driven Development) para implementación:

- `memory/project_state.md` — estado de cada subsistema
- `docs/superpowers/` — spec, plan, progreso SDD y diffs de review
- `CLAUDE.md` — instrucciones para Claude Code

Al iniciar una sesión nueva, Claude lee `memory/MEMORY.md` y `memory/project_state.md` para retomar el trabajo sin necesidad de contexto adicional.
