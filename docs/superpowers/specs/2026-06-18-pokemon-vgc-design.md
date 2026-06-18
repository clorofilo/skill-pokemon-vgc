# Design Spec: Pokémon Champions VGC Assistant

**Date:** 2026-06-18  
**Format:** Pokémon Champions — Reglamento MB (vigente)  
**Stack:** TypeScript (MCP server) + Python (calc-tools)  
**Architecture:** Monorepo integrado con harness SDD

---

## 1. Objetivo

Construir un sistema asistente para análisis competitivo de Pokémon en el formato Pokémon Champions (Reglamento MB) que integre tres subsistemas desde el día uno:

1. **VGC Skill** — archivo Markdown de skill para Claude Code con routing automático y conocimiento experto embebido
2. **MCP Server** — servidor TypeScript que expone herramientas de datos (Showdown/Smogon) con cache local y fallback offline
3. **calc-tools** — scripts Python para cálculo exacto de daño, optimización de EVs, análisis de equipo, simulación de turnos, análisis de leads y matriz de matchups

El sistema detecta automáticamente el tipo de consulta del usuario y enruta al flujo correcto sin que el usuario tenga que especificarlo.

---

## 2. Estructura del Monorepo

```
vgc-app/
├── .claude/
│   └── settings.json          # permisos y hooks del harness SDD
├── skill/
│   └── pokemon-vgc.md         # skill de Claude Code
├── mcp-server/
│   ├── src/
│   │   ├── index.ts
│   │   ├── tools/
│   │   │   ├── damage.ts
│   │   │   ├── usage.ts
│   │   │   ├── sets.ts
│   │   │   ├── teamcheck.ts
│   │   │   ├── turn_sim.ts
│   │   │   ├── lead_analysis.ts
│   │   │   └── matchup_matrix.ts
│   │   └── cache/
│   │       └── manager.ts
│   ├── package.json
│   └── tsconfig.json
├── calc-tools/
│   ├── damage_calc.py
│   ├── ev_optimizer.py
│   ├── team_analyzer.py
│   ├── turn_simulator.py
│   ├── lead_analyzer.py
│   ├── matchup_matrix.py
│   └── requirements.txt
├── data/
│   ├── cache/
│   └── formats/
│       └── champions-mb.json
├── docs/
│   └── superpowers/
│       └── specs/
│           └── 2026-06-18-pokemon-vgc-design.md
└── memory/
    ├── MEMORY.md
    └── *.md
```

---

## 3. La Skill Markdown (`skill/pokemon-vgc.md`)

### Routing automático

La skill detecta el tipo de consulta y enruta sin intervención del usuario:

| Patrón de entrada | Flujo activado |
|---|---|
| "arma un equipo", "quiero usar X", descripción de idea de equipo | Teambuilding desde cero |
| Paste de equipo en formato Showdown | Análisis de equipo existente |
| "¿cuántos EVs para sobrevivir X?", "¿OHKOea Y?" | Cálculo de KOs y spreads |

### Conocimiento embebido (funciona sin MCP)

- Reglas del formato Pokémon Champions Reglamento MB: dobles, registro 4 de 6, Teracristalización activa, banned list vigente
- **Anti-patrón prohibido:** sugerir distribuciones 252/252/4 sin justificación matemática
- **Orden de prioridades en decisiones:** speed creeps del meta → control de velocidad (Tailwind/Trick Room/Icy Wind) → cobertura ofensiva y defensiva → spreads defensivos
- Evaluación obligatoria de Tera Type antes de cerrar cualquier set

### Herramientas MCP disponibles

| Tool | Descripción |
|---|---|
| `get_usage_stats(pokemon, format)` | % de uso y viabilidad del mes |
| `get_viable_sets(pokemon, format)` | Sets más comunes con items/moves/spreads |
| `calculate_damage(attacker, defender, move, conditions)` | KO exacto con rolls |
| `analyze_team(team_paste)` | Debilidades, resistencias, speed control |
| `optimize_evs(pokemon, targets)` | Spread mínimo por thresholds |
| `simulate_turn(state)` | Simulación de secuencia de turnos |
| `analyze_lead(team, meta)` | Leads óptimos y bring recomendado |
| `matchup_matrix(team, threats)` | Matriz de matchups vs amenazas del formato |

---

## 4. MCP Server (TypeScript)

### Ciclo de vida del cache

```
Al iniciar:
  cache < 24h  → servir desde local
  cache > 24h  → intentar descarga Showdown/Smogon
    éxito      → actualizar cache + servir
    error      → servir cache viejo + flag "offline mode"
```

### Fuentes de datos por herramienta

| Tool | Fuente primaria | Fallback |
|---|---|---|
| `get_usage_stats` | smogon-usage API mensual | `data/cache/usage-*.json` |
| `get_viable_sets` | Showdown export sets | `data/cache/sets-*.json` |
| `calculate_damage` | `@smogon/calc` (local npm) | — (siempre disponible) |
| `analyze_team` | parsing + calc local | — (siempre disponible) |
| `optimize_evs` | Python subprocess | — |
| `simulate_turn` | Python subprocess | — |
| `analyze_lead` | Python subprocess | — |
| `matchup_matrix` | Python subprocess | — |

### Subprocess bridge TypeScript → Python

Comunicación por JSON en stdin/stdout, sin HTTP entre procesos:

```typescript
const result = await spawnPython('calc-tools/ev_optimizer.py', {
  pokemon: params.pokemon,
  targets: params.targets
});
```

---

## 5. calc-tools (Python)

Seis módulos independientes, cada uno con CLI propia (usables sin el MCP):

| Módulo | Función |
|---|---|
| `damage_calc.py` | Rango de daño, % KO, rolls individuales — llama a Node subprocess con `@smogon/calc` para resultados exactos |
| `ev_optimizer.py` | Spread mínimo que cumple lista de thresholds (sobrevivir/outspeed) |
| `team_analyzer.py` | Matriz de resistencias, huecos de coverage, análisis de speed control |
| `turn_simulator.py` | Simulación de secuencia de turnos: priority, weather, terrain, Tera |
| `lead_analyzer.py` | Leads óptimos vs meta, bring recomendado según matchup |
| `matchup_matrix.py` | Matriz completa de matchups equipo vs amenazas del formato actual |

Cada script acepta JSON por stdin y devuelve JSON por stdout para integración con el MCP server.

---

## 6. Harness SDD y Memoria entre Sesiones

### Archivos de memoria (`memory/`)

| Archivo | Contenido |
|---|---|
| `MEMORY.md` | Índice de todas las memorias (cargado automáticamente) |
| `project_state.md` | Estado actual de cada subsistema (pendiente/en progreso/completo) |
| `format_data.md` | Datos del reglamento Champions MB: reglas, banned list, mecánicas activas |
| `decisions.md` | Decisiones de arquitectura tomadas y su justificación |
| `feedback_*.md` | Correcciones de comportamiento del asistente entre sesiones |

### Hooks en `.claude/settings.json`

- `PostToolUse` en `Write`/`Edit` → actualiza `memory/project_state.md`
- Permisos automáticos para `npm`, `node`, `python`, `pip` dentro del proyecto

### Flujo de sesión nueva

```
1. Claude lee MEMORY.md (cargado en contexto automáticamente)
2. Lee project_state.md → sabe qué está hecho y qué falta
3. Invoca writing-plans si hay plan de implementación pendiente
4. Invoca subagent-driven-development para ejecutar tareas paralelas
5. Al finalizar → actualiza project_state.md + memorias relevantes
```

---

## 7. Orden de Implementación (SDD paralelo)

Los tres subsistemas son independientes y pueden desarrollarse en paralelo:

**Fase 1 — Scaffolding (paralelo):**
- Subagente A: inicializar monorepo, git, `.claude/settings.json`, estructura de directorios
- Subagente B: escribir `skill/pokemon-vgc.md` con routing y conocimiento embebido
- Subagente C: inicializar `mcp-server/` con TypeScript + MCP SDK

**Fase 2 — Core tools (paralelo):**
- Subagente A: implementar `damage_calc.py` + `ev_optimizer.py` + `team_analyzer.py`
- Subagente B: implementar tools MCP: `damage.ts`, `usage.ts`, `sets.ts`, `teamcheck.ts`
- Subagente C: implementar `cache/manager.ts` con descarga Showdown + fallback

**Fase 3 — Tools avanzadas (paralelo):**
- Subagente A: `turn_simulator.py`, `lead_analyzer.py`, `matchup_matrix.py`
- Subagente B: tools MCP: `optimize_evs.ts`, `turn_sim.ts`, `lead_analysis.ts`, `matchup_matrix.ts`
- Subagente C: `data/formats/champions-mb.json` con datos del reglamento MB

**Fase 4 — Integración y harness:**
- Conectar subprocess bridge TypeScript → Python
- Configurar hooks SDD en `.claude/settings.json`
- Poblar `memory/` inicial con estado del proyecto

---

## 8. Criterios de Éxito

- [ ] La skill detecta correctamente el tipo de consulta sin que el usuario especifique el flujo
- [ ] El MCP server arranca y sirve las 8 herramientas en < 2s
- [ ] El cache se actualiza automáticamente y tiene fallback offline funcional
- [ ] `damage_calc.py` produce resultados equivalentes a la calculadora web de Smogon
- [ ] `ev_optimizer.py` encuentra spreads válidos para thresholds simples en < 5s
- [ ] Una sesión nueva puede retomar el trabajo leyendo solo `MEMORY.md` + `project_state.md`
- [ ] Los 6 scripts Python son usables independientemente desde CLI

---

## 9. Dependencias Externas

**TypeScript / Node.js:**
- `@modelcontextprotocol/sdk` — protocolo MCP
- `@smogon/calc` — cálculo de daño oficial
- `typescript`, `ts-node`, `tsx`

**Python:**
- `pydantic` — validación de inputs JSON
- `click` — CLI para cada script
- `node` (runtime) — `damage_calc.py` llama a Node subprocess para usar `@smogon/calc` directamente

**Datos:**
- Smogon usage stats (descarga mensual desde `smogon.com/stats`)
- Showdown sets export (desde `play.pokemonshowdown.com/data`)
