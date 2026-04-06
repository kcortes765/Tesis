# STATUS — Thesis OS

**Última actualización:** 2026-04-06 (sesión 9)

## Estado general
Activo — Convergencia dp v2 lista para lanzar en WS.

## Fase actual
Fase 3 — Convergencia dp nueva → Round 3 verificación → Producción 5D.

## Qué está listo
- Pipeline 5D verificado con canal paramétrico (sin pared frontal)
- Screening R1 completo (24/25 dp=0.005) + análisis
- Screening R2 completo (15/15 dp=0.004) + análisis profundo
- R2 hallazgos: fricción domina (rho=-0.92), masa segunda, frontera multidimensional
- Gauges se adaptan correctamente al slope (confirmado en código)
- Round 3 diseñado (10 casos, `config/screening_round3.csv`)
- Convergencia v2 script listo (`scripts/run_convergence_v2.py`), validado por revisores
- Importador generalizado (`scripts/import_screening.py`)

## Qué falta
- **Convergencia dp v2** — lanzar en WS (7 core + 2 exploratorios)
- **Decidir dp producción** basado en GCI
- **Round 3** (10 casos al dp convergido) — verificación final
- **Diseñar LHS 5D** (o 4D si rot_z no importa tras R3)
- **Campaña producción + AL loop**
- **Cap 6** con resultados paramétricos

## Riesgos activos
- dp=0.002 podría ser el límite VRAM del RTX 5090 con canal 15m
- dp=0.0015 y 0.001 probablemente no caben (~133M+ partículas de fluido)
- Convergencia anterior (DEC-029) descartada — dp producción TBD
- Criterio ESTABLE/FALLO inconsistente entre scripts legacy y nuevo

## Próximo hito
Convergencia dp completada → dp producción elegido → Round 3 lanzado.
