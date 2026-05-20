# INDEX

## Lectura minima para retomar
1. `.apos/CONTEXT_POLICY.md`
2. `.apos/STATUS.md`
3. `.apos/HANDOFF.md`
4. `.apos/PLAN.md`
5. `.apos/RISKS.md`
6. `.apos/OPEN_QUESTIONS.md`

## Ultimas decisiones relevantes
- Adoptar `dp=0.003` como malla operativa de produccion.
- Usar `classification_mode=displacement_only` como criterio primario.
- Mantener rotacion como diagnostico.
- No correr mas convergencia.
- No lanzar campana grande hasta revisar piloto + batch2 + batch3 + batch4.
- Mantener ejecuciones productivas con matriz explicita, `--max-cases` y dry-run.
- Usar `C:\Seba\Tesis` como unico repo canonico local.
- Distinguir explicitamente datos WS/GitHub de datos laptop/local.
- APOS runtime de tesis = `.apos/` + `/apos`, `/guardar`, `/apos-status`; no usar `apos-system/` como segundo APOS vivo.
- AL3 completo 8/8 ESTABLE; GP after-AL3 entrenado localmente.
- AL4 queda definido por brackets observados after-AL3 y debe correr en WS sin `--retrain-gp`.
- AL4 completo 8/8 OK, 5 ESTABLE y 3 FALLO; export liviano en `exports/al_batch4_after_al3_20260520/`.
- GP after-AL4 entrenado localmente con 64 casos oficiales; AL5 definido en `config/al_batch5_after_al4_20260520.csv`.
- Plan cientifico actualizado: no cerrar con minimo; usar 6 meses/WS para estrategia jerarquica con pendiente, orientacion y forma como extensiones controladas.
- Decision nueva: adoptar plan ambicioso, con posibilidad de ~90-130 simulaciones adicionales por etapas. La forma debe tener peso; se buscara idealmente usar las 10 STL si pasan filtros geometricos/contacto.

## Ultimas sesiones
- 2026-04-30: cierre de convergencia, documento productivo, matriz piloto y guardas `run_production.py`.
- 2026-04-30/2026-05-01: lanzamiento y monitoreo del piloto productivo de 5 casos.
- 2026-05-01: export liviano del piloto productivo.
- 2026-05-03: matriz y lanzamiento batch2 productivo chico de 8 casos.
- 2026-05-05: batch2 completo 8/8 OK.
- 2026-05-06: export liviano batch2 creado y APOS actualizado.
- 2026-05-07/2026-05-09: batch3 productivo dirigido completado 10/10 OK y exportado liviano.
- 2026-05-10: reconciliacion Git/local; `C:\Seba\Tesis` vuelve a ser repo canonico unico.
- 2026-05-13: batch4 mass probe exportado liviano; 11/12 casos oficiales y 1 caso parcial recuperado.
- 2026-05-13: AL batch1 hibrido recibido por Git, dry-run validado y corrida real lanzada en WS.
- 2026-05-14: AL batch1 hibrido completo 8/8 OK y exportado liviano.
- 2026-05-14: AL batch2 bracket-closing creado, dry-run validado y corrida real lanzada en WS.
- 2026-05-16: AL2 recibido, GP after-AL2 entrenado, web post-convergencia actualizada y AL3 preparado/subido en commit `6f9eb41`.
- 2026-05-16: mock sintetico de entregable final creado para visualizar estado limite, frontera, fragilidad y validacion por capas.
- 2026-05-18: AL3 recibido, GP after-AL3 entrenado, web post-convergencia actualizada y AL4 preparado para WS.
- 2026-05-20: AL4 after-AL3 completo 8/8 OK; export liviano creado para laptop.
- 2026-05-20: AL4 recibido en laptop, GP after-AL4 entrenado y AL5 preparado para WS.
- 2026-05-20: se adopta plan ambicioso; forma pasa a ser extension fuerte, idealmente con 10 STL si el analisis lo permite.

## Research relevante
- Pendiente: registrar investigaciones futuras en `.apos/research/` y `RESEARCH_LOG.md`.

## Modulos activos
- APOS local: enabled.
- Skills repo-locales: `/apos`, `/apos-status`, `/guardar`.
- safe-harness: semilla historica en `apos-system/harness/apos-run.py`; usar como referencia, no como segundo runtime APOS.
- chat-transfer: planned.
- research-autonomo: planned.
- quality-evals: planned.

## Mapas externos utiles
- `docs/CONFIGURACION_PRODUCTIVA_TESIS.md`
- `docs/PILOTO_PRODUCTIVO_PROPUESTO.md`
- `data/figures/derived_convergence_graphics/FIGURE_INDEX.md`
- `config/pilot_productivo_20260430.csv`
- `config/batch2_productivo_20260503.csv`
- `exports/pilot_productivo_20260501/pilot_summary.csv`
- `exports/batch2_productivo_20260505/batch2_summary.csv`
- `exports/batch3_productivo_20260509/batch3_summary.csv`
- `exports/batch4_mass_probe_20260513/batch4_summary.csv`
- `exports/batch4_mass_probe_20260513/batch4_summary.md`
- `config/al_batch1_hybrid_20260513.csv`
- `docs/PROMPT_WS_AL_BATCH1_HYBRID_20260513.md`
- `exports/al_batch1_hybrid_20260514/al_batch1_summary.csv`
- `exports/al_batch1_hybrid_20260514/al_batch1_summary.md`
- `config/al_batch2_bracket_closing_20260514.csv`
- `data/production_20260514_2030.log`
- `docs/DATA_ORIGIN_POLICY.md`
- `data/geometry/bloques_b02_20260510/ANALISIS_BLOQUES_STL_20260510.md`
- `data/analysis/gp_h_mu_mstar_20260516/README.md`
- `data/analysis/gp_h_mu_mstar_20260516/validation_metrics.json`
- `config/al_batch3_gp_after_al2_20260516.csv`
- `docs/PROMPT_WS_AL3_AFTER_AL2_20260516.md`
- `exports/al_batch3_gp_after_al2_20260518/al_batch3_summary.md`
- `data/analysis/gp_h_mu_mstar_after_al3_20260518/README.md`
- `data/analysis/gp_h_mu_mstar_after_al3_20260518/validation_metrics.json`
- `config/al_batch4_after_al3_20260518.csv`
- `docs/PROMPT_WS_AL4_AFTER_AL3_20260518.md`
- `exports/al_batch4_after_al3_20260520/al_batch4_summary.md`
- `exports/al_batch4_after_al3_20260520/al_batch4_summary.csv`
- `data/analysis/gp_h_mu_mstar_after_al4_20260520/README.md`
- `data/analysis/gp_h_mu_mstar_after_al4_20260520/validation_metrics.json`
- `config/al_batch5_after_al4_20260520.csv`
- `docs/PROMPT_WS_AL5_AFTER_AL4_20260520.md`
- `docs/post_convergence_story_web/index.html`
- `docs/mock_final_deliverable_20260516/index.html`
