# HANDOFF — Thesis OS

**Última sesión:** 2026-04-06 (sesión 9)

## Qué se hizo

### Screening Round 2 importado y analizado
- 15/15 casos dp=0.004 importados desde WS via git (ZIP 44 MB)
- Scripts: `collect_ws_results.py` (WS→ZIP), `import_screening.py` (ZIP→laptop, generalizado)
- Análisis profundo: temporal, dominio, reflexión, fuerzas, Spearman, variables aisladas, replicación
- 7 figuras de análisis + 5 figuras dashboard autocontenidas en `data/figures/`

### Hallazgos Round 2
- **Fricción domina** (rho=-0.916, p<0.001) a dam_h=0.20
- **Masa significativa** (rho=-0.605, p=0.017)
- **dam_h no significativo** en R2 (artefacto de diseño dirigido con 5/15 a dam_h=0.20)
- **sc2_007 sorpresa:** dam_h=0.12 + fric=0.1 + mass=0.8 → FALLO 1097mm
- **sc2_010 water_h=0.0:** NO es bug de gauges — gauges SÍ se adaptan al slope (confirmado en código). Es resultado físico: agua insuficiente a esa posición en slope 1:5
- **Replicación sc_008 vs sc2_015:** consistente (3.1mm vs 2.1mm, ambos ESTABLE)
- **Reflexión sc2_005:** señal en V12 pero boulder ESTABLE, no problemática

### Round 3 diseñado (EN ESPERA)
- 10 casos verificación: baseline, rot_z, fricción transición, sc2_007 decomposición, slope×friction
- `config/screening_round3.csv` listo
- **NO lanzar aún** — convergencia dp va primero

### Convergencia dp v2 preparada (LISTO PARA WS)
- `scripts/run_convergence_v2.py` — revisado y validado por 3 revisores
- Caso fijo Moris: dam_h=0.30, mass=1.0, fric=0.3, slope=1:20, canal 15m, altura 1.5m
- dp core: 0.010, 0.008, 0.006, 0.005, 0.004, 0.003, 0.002
- dp exploratorios: 0.0015, 0.001 (si caben en VRAM)
- Primarias: displacement, velocity, SPH force (GCI Celik 2008)
- Rotation como diagnóstico (promueve si monotónica)
- GCI solo para métricas monotónicas, MemGpu leído correctamente de Run.csv
- CSV incremental + status JSON para monitoreo remoto

## Qué cambió
- `scripts/collect_ws_results.py` — recolector WS (nuevo)
- `scripts/import_screening.py` — importador generalizado para cualquier round (nuevo)
- `scripts/import_round2.py` — importador original R2 (legacy, reemplazado por import_screening.py)
- `scripts/analisis_round2_profundo.py` — análisis deep R2 (nuevo)
- `scripts/figuras_round2.py` — dashboard + figuras autocontenidas R2 (nuevo)
- `scripts/run_convergence_v2.py` — convergencia nueva configuración (nuevo)
- `config/screening_round3.csv` — matriz Round 3 (nuevo, en espera)
- `data/processed/sc2_001..015/` — datos completos R2 extraídos
- `data/results/results_round2.csv` — CSV consolidado R2
- `data/results.sqlite` — actualizado con 15 casos R2
- `data/figures/` — 12+ figuras nuevas de análisis R2

## Qué debe hacer el siguiente agente
1. **Lanzar convergencia en WS:** `git pull && python scripts/run_convergence_v2.py`
2. **Esperar resultados** (~días, dp gruesos rápidos, finos lentos)
3. **Importar y analizar:** `--solo-analisis` o recolectar datos
4. **Decidir dp producción** basado en GCI < 5% en las 3 primarias
5. **Lanzar Round 3** al dp que salga de convergencia (si es 0.003 o 0.002, ajustar)
6. **Después de Round 3:** diseñar LHS 5D (o 4D si rot_z no importa) → producción + AL

## Qué no debe asumir
- La convergencia anterior (Fase 2, DEC-029) está **descartada** — fue con configuración distinta (canal viejo, sin slope paramétrico, sin fricción). Se rehace desde cero.
- dp=0.003 como producción (DEC-029) es **provisional** hasta que la convergencia nueva lo confirme o cambie.
- Los datos R2 a dp=0.004 son screening exploratorio, no producción.
- water_h=0.0 en sc2_010 NO es un bug — es físico. Los gauges SÍ se adaptan al slope.
- El criterio ESTABLE/FALLO en `import_round2.py` usa solo desplazamiento. `import_screening.py` usa desplazamiento OR rotación (unificado con data_cleaner).
- Round 3 está diseñado pero NO lanzado. Convergencia va primero.

## Contexto mínimo para retomar
Leer: BOOTSTRAP.md → este HANDOFF → data/figures/screening_round2_analysis_deep.md → config/screening_round3.csv
