# HANDOFF — Thesis OS

**Última sesión:** 2026-03-21 (sesión 4)

## Qué se hizo
- Research re-hecho con 3 agentes paralelos, persistido a docs/ (no a tasks efímeras):
  - docs/RESEARCH_GP_AL.md — GP kernels, 6 acquisition functions, implementación, Sobol, 16 refs
  - docs/RESEARCH_EMPIRICAL_SANITY.md — Ritter, Nandasena, Cox 2020, 7 sanity checks, 24 figuras
  - docs/PLAN_GP_AL_BATCH.md — diseño batch 20 pts LHS maximin, plan AL loop
  - config/gp_initial_batch.csv — 20 casos listos
- Construido sistema autónomo:
  - seba_os/scripts/autonomous_runner.py — orquestador Python (alternativa a agente.ps1)
  - feature_list.json + CONTEXT.md + prompts/coding_prompt.md para agente.ps1
- Ejecutado agente.ps1 -All overnight — **8/8 features completadas**:
  - S1.1: Pipeline verificado end-to-end (GenCase + DualSPHysics GPU local, RTX 4060)
  - S1.2: 5 sims de validación corridas (esquinas + centro del dominio 2D)
  - S1.3: src/gp_active_learning.py implementado (Matérn 5/2, U-function, LOO Q2=0.92)
  - S1.4: src/sanity_checks.py implementado (5 checks, todos PASS)
  - S1.5: Sanity checks validados con datos reales
  - S2.1: GP entrenado con datos reales, 6 figuras generadas (PNG+PDF)
  - S2.2: scripts/deploy_ws.py creado
  - S2.3: tesis/cap3_metodologia.md expandido (647 líneas, 81 ecuaciones, 19 refs)
- dsph_config.json actualizado con auto-detect de ejecutables (laptop + WS)
- Regla de persistencia de research agregada a BOOTSTRAP.md warning #8
- PLAN.md actualizado con Fase 3 en progreso

## Qué cambió
- 6 commits nuevos del agente (feat S1.3 a S2.3)
- 3 módulos nuevos: src/gp_active_learning.py, src/sanity_checks.py, scripts/deploy_ws.py
- 3 docs de research en docs/
- SQLite: 6 filas con datos reales (5 gp_* + test_diego_reference)
- 12 figuras nuevas en data/figures/gp/ y data/figures/sanity/
- Cap 3 expandido con metodología GP+AL completa
- config/dsph_config.json: dsph_bin="auto" con paths laptop + WS

## Qué debe hacer el siguiente agente
1. **Deployar a WS**: ejecutar `python scripts/deploy_ws.py` → copiar ZIP a WS UCN
2. **Lanzar batch producción**: 20 casos dp=0.004 en RTX 5090 (~15h)
3. **Recolectar resultados** → meter en SQLite local
4. **Re-entrenar GP** con 20 puntos → LOO, figuras, Sobol
5. **AL loop**: proponer siguiente punto → simular → repetir hasta U_min >= 2.0
6. **Cap 6**: escribir con figuras finales

## Qué no debe asumir
- Que los 5 resultados actuales (dp=0.02) son definitivos — son de desarrollo, producción es dp=0.004
- Que el GP con 5 puntos es preciso — es verificación, no resultado final
- Que deploy_ws.py ya fue ejecutado — solo fue creado, no usado
- Que la WS está lista — verificar espacio en disco y estado

## Contexto mínimo para retomar
Leer: BOOTSTRAP.md → este HANDOFF → PLAN.md
Si toca código: src/gp_active_learning.py, src/sanity_checks.py
Si toca deploy: scripts/deploy_ws.py, config/dsph_config.json
