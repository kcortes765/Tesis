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

## Fase 3 — Campaña 4D dp=0.003 + Active Learning (EN PROGRESO, mar-jun 2026)
- [x] Producción cambiada a dp=0.003 (DEC-029, supersede DEC-005)
- [x] Pipeline actualizado a 4D: dam_h, mass, rot_z, friction_coefficient
- [x] Fricción parametrizada via Kfric_User property override en Chrono
- [x] GP generalizado a dimensiones arbitrarias (kernel ARD, grid nD, figuras slices)
- [x] Investigación SOTA: GP+AL, multi-fidelidad, campaign design, Chrono friction
- [x] Batch inicial 25 puntos LHS 4D diseñado (config/gp_initial_batch.csv)
- [x] Campaña lanzada en WS: 5/25 completados (gp_001-gp_005)
- [ ] Completar 25 sims iniciales (~14 abril)
- [ ] Entrenar GP 4D con 25 puntos → LOO-CV → figuras
- [ ] Active learning loop secuencial (~75 iteraciones)
- [ ] Sobol indices analíticos desde GP
- [ ] Superficie de fragilidad (Monte Carlo sobre GP)
- [ ] Comparar umbral SPH vs Nandasena/Nott
- [ ] Modos de transporte desde datos de rotación Chrono

## Fase 4 — Tesis escrita (EN CURSO)
- [x] Cap 1: Introducción
- [x] Cap 2: Marco Teórico (30+ refs)
- [x] Cap 3: Metodología Numérica
- [x] Cap 4: Resultados Convergencia
- [x] Cap 5: Pipeline Computacional
- [ ] Cap 6: Resultados Paramétricos (depende de Fase 3)
- [ ] Cap 7: Conclusiones

## Fase 5 — Multi-forma (SEMESTRE 2, ago-nov 2026)
- [ ] Solicitar 9 STLs escaneados a Moris
- [ ] Calcular descriptores geométricos (CSF, aspect ratio, sphericity)
- [ ] ~25 sims dp=0.003 por forma adicional (GP transfiere desde primera geometría)
- [ ] GP unificado con forma como variable continua
- [ ] Sobol actualizado con dimensión de forma

## Fase 6 — Parametrizar pendiente de playa (PENDIENTE)
- [ ] Moris pidió 5ta variable: pendiente de playa
- [ ] Requiere nuevo STL de canal o geometría paramétrica
- [ ] Evaluar viabilidad e impacto en presupuesto de sims

## Timeline (revisado 2026-03-30 v3)
```
MAR 2026:      Pipeline 4D + lanzar 25 sims dp=0.003 ✓
ABR:           25 sims completan → entrenar GP 4D → iniciar AL
MAY-JUN:       AL loop (~75 iter) → Sobol → fragilidad → Cap 6
JUL:           Exposición 1 + cierre semestre 1
AGO-OCT:       Multi-forma (9 STLs × ~25 sims) → GP unificado
NOV:           Cap 7 + revisión tesis completa
DIC:           Defensa tesis
```

## Prioridad actual
Esperar 25 sims dp=0.003 4D (~14 abril) → recolectar → entrenar GP 4D → AL loop secuencial → Sobol → fragilidad → Cap 6.
