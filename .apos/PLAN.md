# PLAN — Thesis OS

**Última actualización:** 2026-03-21

## Fase 1 — Infraestructura (COMPLETADA, feb 2026)
- [x] Pipeline: geometry_builder → batch_runner → data_cleaner → ml_surrogate
- [x] Template XML paramétrico con Chrono
- [x] Inyección automática de masa, inercia, fillbox, gauges
- [x] Limpieza .bi4 en try/finally, notificaciones ntfy.sh
- [x] Correcciones físicas: massbody, inercia trimesh, FtPause=0.5

## Fase 2 — Convergencia (COMPLETADA, mar 2026)
- [x] 7 niveles de dp testeados (dp=0.020 → dp=0.003)
- [x] Convergencia alcanzada: 3 métricas primarias < 5% entre dp=0.004 y dp=0.003
- [x] dp=0.004 = producción; dp=0.003 = referencia más fina posible (hardware limit)
- [x] dp=0.002/0.0025 inviable: >43 GB VRAM, excede RTX 5090 32GB
- [x] Contact force descartado como criterio (CV=82%) — hallazgo científico
- [x] dp render=0.01

## Fase 3 — GP + Active Learning (EN PROGRESO, mar 2026)
- [x] Matriz 50 LHS original: CANCELADA (solo 5 corridos)
- [x] Estrategia nueva: GP + active learning en 2D (dam_h, mass)
- [x] Research completado y persistido: docs/RESEARCH_GP_AL.md, docs/RESEARCH_EMPIRICAL_SANITY.md
- [x] Batch inicial diseñado: 20 puntos LHS maximin (config/gp_initial_batch.csv)
- [x] Pipeline verificado end-to-end local (canal 30m, dp=0.02, RTX 4060)
- [x] 5 sims validacion corridas (SQLite: 6 filas, tendencias correctas)
- [x] src/gp_active_learning.py (Matern 5/2, U-function, LOO Q2=0.92, 6 figuras)
- [x] src/sanity_checks.py (monotonicidad, Ritter, magnitudes, fuerzas, suavidad)
- [x] Sanity checks validados con datos reales
- [x] Entrenar GP con datos reales + generar figuras (LOO Q2=0.92, 6 figuras en data/figures/gp/)
- [x] Script deploy WS (scripts/deploy_ws.py)
- [x] Cap 3 Metodologia expandido (647 lineas, GP+AL completo)
- [ ] Deployar 20 casos a WS UCN
- [ ] Active learning loop (U-function, ~10 sims adicionales)
- [ ] Sobol indices del GP
- [ ] Comparar umbral SPH vs Nandasena/Nott

## Fase 4 — Tesis escrita (EN CURSO)
- [x] Cap 1: Introducción
- [x] Cap 2: Marco Teórico (30+ refs)
- [x] Cap 3: Metodología Numérica
- [x] Cap 4: Resultados Convergencia
- [x] Cap 5: Pipeline Computacional
- [ ] Cap 6: Resultados Paramétricos (depende de Fase 3)
- [ ] Cap 7: Conclusiones

## Fase 5 — Multi-forma (PENDIENTE)
- [ ] Email Moris → 6 STLs adicionales
- [ ] 245 sims (7 formas × 35 casos)
- [ ] Análisis multi-forma

## Fase 6 — Paper 1: GNN (PENDIENTE)
- [ ] Setup GNN en laptop (Geoelements GNS)
- [ ] Entrenar incrementalmente
- [ ] GNN refinada con 295 casos totales
- [ ] Submit → Coastal Engineering / CMAME

## Fase 7 — Paper 2: Tailings (FUTURO)
- [ ] CB-Geo MPM setup
- [ ] Diff-GNS inverso
- [ ] Transfer Learning (bonus)
- [ ] Submit → CMAME / Computers and Geotechnics

## Timeline (revisado 2026-03-20 v2)
```
MAR 2026:      Compilar plan + batch inicial → deployar a WS
ABR:           Sanity check → active learning loop → umbral → Sobol → Cap 6
MAY-JUN:       245 sims multi-forma (si STLs Moris) → Cap 7 → Conclusiones
JUL-AGO:       Setup GNN + Paper 1
SEP:           Submit Paper 1
DIC:           Defensa tesis
```

## Prioridad actual
Deploy 20 casos a WS → batch produccion dp=0.004 → recolectar → re-entrenar GP → AL loop → Sobol → Cap 6.
