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
- No lanzar campana grande hasta revisar piloto + batch2.
- Mantener ejecuciones productivas con matriz explicita, `--max-cases` y dry-run.

## Ultimas sesiones
- 2026-04-30: cierre de convergencia, documento productivo, matriz piloto y guardas `run_production.py`.
- 2026-04-30/2026-05-01: lanzamiento y monitoreo del piloto productivo de 5 casos.
- 2026-05-01: export liviano del piloto productivo.
- 2026-05-03: matriz y lanzamiento batch2 productivo chico de 8 casos.
- 2026-05-05: batch2 completo 8/8 OK.
- 2026-05-06: export liviano batch2 creado y APOS actualizado.

## Research relevante
- Pendiente: registrar investigaciones futuras en `.apos/research/` y `RESEARCH_LOG.md`.

## Modulos activos
- APOS local: enabled.
- Skills repo-locales: `/apos`, `/apos-status`, `/guardar`.
- safe-harness: semilla local en `apos-system/harness/apos-run.py`.
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
