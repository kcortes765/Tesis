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
