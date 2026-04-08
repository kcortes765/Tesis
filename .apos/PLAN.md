# PLAN — Thesis OS

**Última actualización:** 2026-04-08

## Fase 1 — Infraestructura (COMPLETADA, feb 2026)
- [x] Pipeline: geometry_builder → batch_runner → data_cleaner → ml_surrogate
- [x] Template XML paramétrico con Chrono
- [x] Inyección automática de masa, inercia, fillbox, gauges
- [x] Limpieza .bi4 en try/finally, notificaciones ntfy.sh
- [x] Correcciones físicas: massbody, inercia trimesh, FtPause=0.5

## Fase 2 — Convergencia original (COMPLETADA, mar 2026)
- [x] 7 niveles de dp testeados hasta `dp=0.003`
- [x] Convergencia válida para la configuración antigua
- [x] Contact force descartado como criterio
- [x] Resultado histórico documentado en tesis/reportes
- [ ] Reconciliar scripts versionados con la versión final histórica (deuda de trazabilidad)

## Fase 3 — Setup 5D actual (EN PROGRESO, mar-jun 2026)
- [x] Pipeline actualizado a 5D: dam_h, mass, rot_z, friction, slope_inv
- [x] Canal paramétrico con slope variable
- [x] Screening R1 completo (24/25 dp=0.005)
- [x] Screening R2 completo (15/15 dp=0.004)
- [x] Análisis profundo R2
- [x] Round 3 diseñado (`config/screening_round3.csv`)
- [x] Convergencia v2 preparada
- [x] Convergencia v2 corrida en WS e importada
- [ ] **Cerrar criterio de convergencia** (onset vs trayectoria completa)
- [ ] **Elegir dp producción** en la configuración nueva
- [ ] Extraer métricas de onset de la v2 existente
- [ ] **Decidir con Moris** si hace falta una v3 corta cerca de la frontera
- [ ] Si hace falta: correr v3 (`dp=0.004`, `0.003`, `0.002`) en 1–2 casos de umbral
- [ ] Lanzar Round 3 con el dp ya defendido
- [ ] Decidir 4D o 5D para producción
- [ ] Diseñar LHS 5D (o 4D) con active learning
- [ ] Campaña producción + AL loop
- [ ] Sobol indices analíticos desde GP
- [ ] Superficie de fragilidad (Monte Carlo sobre GP)
- [ ] Comparar umbral SPH vs Nandasena/Nott

## Fase 4 — Tesis escrita (EN CURSO)
- [x] Cap 1: Introducción
- [x] Cap 2: Marco Teórico
- [x] Cap 3: Metodología Numérica
- [x] Cap 4: Resultados Convergencia original
- [x] Cap 5: Pipeline Computacional
- [ ] Cap 6: Resultados Paramétricos
- [ ] Cap 7: Conclusiones
- [ ] Actualizar relato metodológico de convergencia para distinguir Fase 2 vs Fase 3

## Prioridad actual
Reunión con Moris → criterio metodológico claro → decidir si basta onset de v2 o si hace falta v3 cerca de la frontera → elegir dp → Round 3.
