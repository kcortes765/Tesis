# APOS-X readiness audit - 2026-05-01

## Alcance
Preparar este proyecto para continuidad APOS-X local sin tocar skills globales, `.system`, hooks ni ejecuciones productivas.

## Hechos verificados
- Raiz del proyecto: `C:\Users\Admin\Desktop\SPH-Tesis`.
- APOS historico existia, pero incompleto para APOS-X.
- `data/production_status.json` indica piloto productivo activo: 5 casos, progreso 2/5.
- Procesos activos observados: `python` y `DualSPHysics5.4_win64`.
- `$HOME\.codex\skills` existe y contiene solo `.system`.
- `$HOME\.agents\skills` no existe.
- `.agents\skills` repo-local no existe.
- `C:\Seba\.agente-global\skills` no existe en esta WS.
- `C:\Users\kevin\.codex\skills` no existe en esta WS.

## Backup
- Snapshot creado antes de migrar: `.apos/snapshots/apox-migration-20260501_001524`.

## Cambios aplicados
- Se agrego estructura APOS-X local.
- Se reemplazaron archivos vivos `STATUS.md`, `HANDOFF.md`, `PLAN.md`.
- Se agregaron `CONTEXT_POLICY.md`, `INDEX.md`, `QUALITY.md`, `MODULES.md`, `RISKS.md`, `OPEN_QUESTIONS.md`, `SOURCES.md`, `RESEARCH_LOG.md` y carpetas de evidencia/investigacion/transferencias.

## No aplicado
- No se crearon skills globales.
- No se tocaron skills `.system`.
- No se instalaron hooks.
- No se ejecuto ninguna simulacion nueva.
- No se interrumpio el piloto activo.

## Riesgos
- El piloto sigue corriendo; cualquier cambio productivo debe esperar.
- Falta implementar `apos-system/` y `apos-run`.
- Archivos historicos APOS tienen mojibake y no deben ser fuente unica.
