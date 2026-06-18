# vgc-app — Pokémon Champions VGC Assistant

Asistente de análisis competitivo para el formato **Pokémon Champions Reglamento MB** (dobles, 6 registrar / 4 traer, Teracristalización activa), integrado con Claude Code.

---

## Instalación rápida

### Requisitos previos

- [Node.js 18+](https://nodejs.org/)
- [Python 3.9+](https://www.python.org/)
- [Claude Code](https://claude.ai/code)

### Windows

```powershell
git clone https://github.com/clorofilo/skill-pokemon-vgc
cd skill-pokemon-vgc
.\setup.ps1
```

### macOS / Linux

```bash
git clone https://github.com/clorofilo/skill-pokemon-vgc
cd skill-pokemon-vgc
bash setup.sh
```

El script hace todo en un paso:

1. Instala dependencias npm y Python
2. Compila el MCP server (`mcp-server/dist/`)
3. Registra la skill globalmente en `~/.claude/skills/`
4. Añade routing automático a `~/.claude/CLAUDE.md`
5. Escribe `.claude/settings.json` con el path correcto para esta máquina

---

## Usar la skill en otro directorio

Después del setup, copia **un solo archivo** al directorio donde quieras usar la skill:

```
.claude/settings.json  →  <tu-proyecto>/.claude/settings.json
```

La skill ya está registrada globalmente — no se necesita nada más.

### Instalar en un proyecto específico (sin setup global)

Copia estos dos archivos al directorio del proyecto:

```
skill/pokemon-vgc.md   →  <tu-proyecto>/.claude/skills/pokemon-vgc.md
.claude/settings.json  →  <tu-proyecto>/.claude/settings.json
```

Claude Code detecta `.claude/skills/` automáticamente al abrir ese directorio.

---

## Qué hace la skill

Detecta el tipo de consulta y enruta al flujo correcto sin que tengas que especificarlo:

| Entrada | Flujo activado |
|---|---|
| "arma un equipo", idea de equipo | Teambuilding desde cero |
| Paste de equipo en formato Showdown | Análisis de equipo existente |
| "¿cuántos EVs para sobrevivir X?", "¿OHKOea Y?" | Cálculo de KOs y spreads |

Puedes invocarla explícitamente con `/pokemon-vgc` o simplemente hacer una pregunta de VGC — Claude la activa automáticamente.

---

## MCP Server — 8 herramientas

El servidor MCP expone estas herramientas que la skill usa internamente:

| Tool | Descripción |
|---|---|
| `calculate_damage` | Rango de daño exacto con rolls (usa `@smogon/calc`) |
| `get_usage_stats` | % de uso mensual desde Smogon Stats |
| `get_viable_sets` | Sets más comunes (items, moves, spreads) |
| `analyze_team` | Debilidades de tipo, speed control, speed tiers |
| `optimize_evs` | Spread mínimo para thresholds survive y/o outspeed |
| `simulate_turn` | Simulación de turno: prioridades, weather, terrain |
| `analyze_lead` | Mejores leads y bring recomendado vs meta |
| `matchup_matrix` | Matriz de matchups del equipo vs amenazas del formato |

El cache se actualiza automáticamente cada 24 h y cae a modo offline si no hay red.

### Verificar que el servidor funciona

```bash
cd mcp-server
echo '{"jsonrpc":"2.0","id":1,"method":"tools/list","params":{}}' | node dist/index.js
```

Debe listar los 8 tools.

### Comandos de desarrollo

```bash
cd mcp-server
npm run dev          # desarrollo con tsx (hot reload)
npm run build        # compilar a dist/
npm run typecheck    # verificar tipos sin compilar
```

---

## calc-tools — Scripts Python

Seis scripts independientes. Cada uno acepta JSON por `stdin` y devuelve JSON por `stdout`. Usables directamente desde CLI sin el MCP server.

### Requisitos

- Python 3.9+
- Node.js (solo para `damage_calc.py` — llama a `@smogon/calc` via subprocess)

```bash
cd calc-tools
pip install -r requirements.txt
```

### Ejemplos de uso

```bash
# Cálculo de daño
echo '{
  "attacker": {"species":"Calyrex-Shadow","item":"Choice Specs","nature":"Timid","evs":{"spa":252},"teraType":"Psychic"},
  "defender": {"species":"Incineroar","item":"Assault Vest","nature":"Careful","evs":{"hp":252,"spd":252}},
  "move": "Astral Barrage"
}' | python damage_calc.py

# Optimización de EVs (survive)
echo '{
  "pokemon": {"species":"Incineroar","item":"Assault Vest","nature":"Careful"},
  "targets": [{"type":"survive","attacker":{"species":"Calyrex-Shadow","item":"Choice Specs","nature":"Timid","evs":{"spa":252}},"move":"Astral Barrage"}]
}' | python ev_optimizer.py

# Optimización de EVs (outspeed)
echo '{
  "pokemon": {"species":"Flutter Mane","item":"Choice Specs","nature":"Timid"},
  "targets": [{"type":"outspeed","target_speed":130}]
}' | python ev_optimizer.py

# Análisis de equipo
echo '{
  "team_paste": "Incineroar @ Assault Vest\nAbility: Intimidate\nEVs: 252 HP / 4 Atk / 252 SpD\nCareful Nature\n- Fake Out\n- Knock Off\n- U-turn\n- Flare Blitz"
}' | python team_analyzer.py

# Simulación de turno
echo '{
  "state": {"side_a":["Incineroar","Flutter Mane"],"side_b":["Calyrex-Shadow","Rillaboom"],"weather":null,"terrain":null},
  "moves": [
    {"user":"Incineroar","move":"Fake Out","target":"Calyrex-Shadow"},
    {"user":"Flutter Mane","move":"Moonblast","target":"Calyrex-Shadow"}
  ]
}' | python turn_simulator.py

# Análisis de leads
echo '{
  "team": ["Incineroar","Flutter Mane","Rillaboom","Urshifu-Rapid-Strike","Landorus-Therian","Amoonguss"],
  "meta": ["Calyrex-Shadow","Flutter Mane"]
}' | python lead_analyzer.py

# Matriz de matchups
echo '{
  "team_paste": "Incineroar @ Assault Vest\n...",
  "threats": ["Calyrex-Shadow","Flutter Mane"]
}' | python matchup_matrix.py
```

### Tests

```bash
# Desde la raíz del repo
pytest calc-tools/tests/ -v
# 31 tests — priority ordering, weather/terrain, synergy bonus,
# matchup matrix, outspeed EVs, EV remaining, tera type, speed control...
```

---

## Formato: Pokémon Champions Reglamento MB

| Campo | Valor |
|---|---|
| Modalidad | Dobles |
| Equipo | 6 registrados, 4 traídos a batalla |
| Teracristalización | Activa |
| Z-moves / Mega / Dynamax | Inactivos |
| Generación | 9 (Escarlata y Violeta) |
| Datos del formato | `data/formats/champions-mb.json` |

---

## Estructura del repositorio

```
vgc-app/
├── setup.ps1                   # Setup automático — Windows
├── setup.sh                    # Setup automático — macOS/Linux
├── skill/
│   └── pokemon-vgc.md          # Skill de Claude Code
├── mcp-server/                 # Servidor MCP (TypeScript)
│   └── src/
│       ├── index.ts            # Wiring de los 8 tools
│       ├── tools/              # damage, usage, sets, teamcheck,
│       │                       # optimize_evs, turn_sim, lead_analysis, matchup_matrix
│       └── cache/manager.ts    # Cache 24 h + fallback offline
├── calc-tools/                 # Scripts Python standalone
│   ├── calc_bridge.js          # Bridge Node → @smogon/calc
│   ├── damage_calc.py
│   ├── ev_optimizer.py
│   ├── team_analyzer.py
│   ├── turn_simulator.py
│   ├── lead_analyzer.py
│   ├── matchup_matrix.py
│   └── tests/                  # 31 tests pytest
├── data/
│   ├── cache/                  # Cache local Showdown/Smogon
│   └── formats/
│       └── champions-mb.json
└── .claude/
    └── settings.json           # Config MCP (path absoluto, generado por setup)
```

---

## Solución de problemas

**La skill no se activa**
- Verifica que `~/.claude/skills/pokemon-vgc.md` existe (se crea con el setup)
- O copia `skill/pokemon-vgc.md` a `.claude/skills/pokemon-vgc.md` en tu proyecto

**El MCP server no arranca**
- Asegúrate de haber compilado: `cd mcp-server && npm run build`
- Verifica que el path en `.claude/settings.json` apunta a `dist/index.js` existente

**`damage_calc.py` falla**
- Node.js debe estar en el PATH — `node --version` debe responder
- `cd mcp-server && npm install` debe haberse ejecutado (instala `@smogon/calc`)

**Tests de Python fallan**
- `pip install -r calc-tools/requirements.txt`
- Los tests de `ev_optimizer` y `damage_calc` necesitan Node.js disponible
