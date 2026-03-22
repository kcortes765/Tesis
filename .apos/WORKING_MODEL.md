# WORKING_MODEL — Thesis OS

**Última actualización:** 2026-03-21

## Comprensión vigente

### Thread 1 — Pipeline de simulación
7 módulos en src/ (geometry_builder, batch_runner, data_cleaner, main_orchestrator, ml_surrogate, gp_active_learning, sanity_checks). Verificado end-to-end en laptop (RTX 4060) con dp=0.02. dsph_config.json auto-detecta ejecutables en laptop y WS.

### Thread 2 — Campaña de simulaciones
5 sims de validación corridas localmente (dp=0.02, esquinas + centro del dominio). SQLite tiene 6 resultados. Tendencias correctas: dam_h domina (Spearman rho=0.95), mass secundario. Batch producción de 20 casos (dp=0.004) diseñado pero NO deployado aún.

### Thread 3 — Surrogate GP
GP Matérn 5/2 + ARD entrenado con 5 datos reales (canal 30m). LOO Q2=0.92, RMSE=1.92m. U-function implementada, propone siguiente punto: dam_h=0.10, mass=1.11. Converged=False (U_min=0.005, necesita ≥2.0). Con 5 puntos es impreciso — producción con 20+ puntos dará mejor modelo.

### Thread 4 — Tesis escrita
Cap 3 expandido a 647 líneas con metodología GP+AL (81 ecuaciones, 19 refs, 57 secciones). Caps 1-5 listos. Caps 6-7 dependen de resultados producción.

### Thread 5 — Papers y futuro
Sin cambios. GP=tesis, GNN=Paper 1, Diff-GNS=Paper 2.

### Thread 6 — Governance y automatización
APOS activo. agente.ps1 probado overnight (8/8 features, maneja rate limits). Research ahora se persiste a docs/RESEARCH_*.md (no a tasks efímeras). autonomous_runner.py disponible como alternativa Python.

## Tensiones actuales
- **Datos dev vs prod** — resultados actuales son dp=0.02, producción necesita dp=0.004
- **Deploy a WS** — script listo pero no ejecutado, WS no verificada recientemente

## Hipótesis operativa
1. Deploy 20 casos a WS (dp=0.004)
2. Recolectar → re-entrenar GP → AL loop
3. Sobol → Cap 6 → Cap 7 → tesis lista

## STL base: BLIR3.stl
- Volumen: 0.00053023 m³
- Densidad implícita: ~2000 kg/m³
- Diámetro equivalente: 0.100421 m
- Bounding box (scale=0.04): 0.1710 × 0.2100 × 0.0399 m

## Qué no hacer
- results.sqlite tiene 6 filas (5 validación dp=0.02 + 1 referencia) — NO son datos de producción
- No asumir que gp_surrogate.pkl es definitivo
- No tratar 15 resultados de canal 15m como base final (tiene saturación)
- No reinventar el pipeline (ya funciona)
- No escribir conclusiones sin datos reconciliados
