# CONTEXT.md — SPH-IncipientMotion (para agente headless)

## Proyecto
Tesis UCN 2026: simulacion SPH de movimiento incipiente de bloques costeros bajo flujos tipo tsunami. Pipeline: DualSPHysics v5.4 + Chrono → GP surrogate + Active Learning. El objetivo es encontrar umbrales criticos de movimiento en espacio 2D (dam_height, boulder_mass).

## Archivos de referencia

| Archivo | Para que |
|---------|----------|
| `CLAUDE.md` | Reglas tecnicas del proyecto (XML, CSV format, correcciones fisicas) |
| `config/dsph_config.json` | Rutas a ejecutables DualSPHysics (auto-detect laptop/WS) |
| `config/param_ranges.json` | Rangos de parametros: dam_h [0.10, 0.50]m, mass [0.80, 1.60]kg |
| `config/template_base.xml` | Template XML DualSPHysics (canal 30m, dp variable) |
| `config/gp_initial_batch.csv` | 20 casos del batch inicial GP (LHS maximin) |
| `docs/RESEARCH_GP_AL.md` | Research completo: GP kernels, acquisition functions, AL loop |
| `docs/RESEARCH_EMPIRICAL_SANITY.md` | Ecuaciones empiricas, sanity checks, figuras esperadas |
| `docs/PLAN_GP_AL_BATCH.md` | Diseno del batch inicial y plan del AL loop |
| `src/geometry_builder.py` | Genera XMLs de caso desde template + STL + parametros |
| `src/batch_runner.py` | Ejecuta GenCase → DualSPHysics GPU → cleanup .bi4 |
| `src/data_cleaner.py` | Parsea CSVs Chrono/Gauges → metricas → SQLite |
| `src/main_orchestrator.py` | LHS matrix → loop completo (geometry → sim → clean → SQLite) |
| `src/ml_surrogate.py` | GP regression existente (necesita reescritura con AL) |
| `models/BLIR3.stl` | STL del boulder (escala 0.04) |
| `data/results.sqlite` | Base maestra de resultados (puede estar vacia) |

## Convenciones de codigo

- **Python 3.8+** (laptop tiene 3.8, no usar walrus operator ni match/case)
- **Deps:** numpy, pandas, trimesh, lxml, scipy, scikit-learn, matplotlib, sqlalchemy
- **CSV DualSPHysics:** separador `;`, decimal `.`, sentinel `-3.40282e+38` → NaN
- **Chrono obligatorio:** RigidAlgorithm=3, massbody (no rhopbody), inercia desde trimesh
- **FtPause >= 0.5** siempre
- **dp=0.004** produccion, **dp=0.02** desarrollo/test
- **Canal 30m** (no 15m, esa geometria esta obsoleta)
- **fillbox void** obligatorio para STLs
- **dsph_config.json** tiene `"dsph_bin": "auto"` — resuelve automaticamente laptop vs WS
- **Logging:** usar `logging` module, no `print()` para info de pipeline
- **Tests:** verificar con datos sinteticos o con casos existentes en `data/processed/`

## Estructura de resultados

```
data/
  processed/{case_id}/     # CSVs limpios por caso
    ChronoExchange_mkbound_51.csv
    ChronoBody_forces.csv
    GaugesVel_V*.csv
    GaugesMaxZ_hmax*.csv
  results.sqlite           # Base maestra
  figures/                 # Figuras generadas
```

## Lo que NO hacer

- NO tocar config/template_base.xml sin justificacion
- NO usar FloatingInfo ni ComputeForces (Chrono genera CSVs directamente)
- NO usar rhopbody (usar massbody)
- NO asumir que results.sqlite tiene datos (puede estar vacia)
- NO generar archivos en la raiz del proyecto (usar data/, scripts/, etc.)
- NO borrar casos existentes en cases/ o data/processed/
