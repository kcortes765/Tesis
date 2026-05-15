# PLAN

## Objetivo activo
Monitorear AL batch2 bracket-closing en la WS, conservar trazabilidad por matriz explicita y preparar export liviano cuando termine.

## Fase actual
AL batch2 real lanzado en WS con 10 casos dirigidos, `dp=0.003`, `classification_mode=displacement_only` y `reference_time_s=0.5`.

## Proximos hitos
- [x] Cerrar convergencia y adoptar `dp=0.003` como malla operativa.
- [x] Documentar configuracion productiva oficial.
- [x] Crear matriz piloto explicita de 5 casos.
- [x] Agregar guardas a `scripts/run_production.py`.
- [x] Ejecutar dry-run del piloto.
- [x] Lanzar piloto real de 5 casos.
- [x] Esperar fin del piloto y auditar resultados.
- [x] Crear export liviano del piloto productivo.
- [x] Crear matriz batch2 chica de 8 casos.
- [x] Ejecutar preflight y dry-run batch2.
- [x] Lanzar batch2 real en background.
- [x] Esperar fin de batch2 y auditar resultados.
- [x] Crear export liviano batch2.
- [x] Crear matriz batch3 productiva dirigida de 10 casos.
- [x] Ejecutar dry-run batch3.
- [x] Lanzar batch3 real.
- [x] Esperar fin de batch3 y auditar resultados.
- [x] Crear export liviano batch3.
- [x] Actualizar `C:\Seba\Tesis` a `origin/master` sin perder cambios locales.
- [x] Respaldar cambios locales en `C:\Seba\workspace_backups\tesis-reconcile-20260510_125339`.
- [x] Guardar cambios trackeados previos en `stash@{0}`.
- [x] Documentar politica de origen de datos en `docs/DATA_ORIGIN_POLICY.md`.
- [x] Simplificar APOS operativo a `.apos/` + tres skills repo-locales: `/apos`, `/guardar`, `/apos-status`.
- [x] Committear APOS unificado, politica de origen, verificacion local y analisis de bloques.
- [x] Retirar el worktree temporal `C:\Seba\Tesis_origin_master_clean_20260510_123639`.
- [x] Ejecutar batch4 mass probe en WS con `dp=0.003`.
- [x] Crear export liviano batch4 en `exports/batch4_mass_probe_20260513/`.
- [x] Recibir desde Git la matriz `config/al_batch1_hybrid_20260513.csv`.
- [x] Ejecutar dry-run AL batch1 hibrido.
- [x] Lanzar AL batch1 hibrido real en WS.
- [x] Monitorear AL batch1 hasta completar o fallar.
- [x] Crear export liviano AL batch1.
- [x] Crear matriz AL batch2 bracket-closing.
- [x] Ejecutar dry-run AL batch2.
- [x] Lanzar AL batch2 real.
- [ ] Monitorear AL batch2 hasta completar o fallar.
- [ ] Crear export liviano AL batch2.
- [ ] Revisar cientificamente el export del piloto, batch2, batch3, batch4, AL batch1 y AL batch2 juntos.
- [ ] Decidir si repetir/reprocesar el caso 12 parcial de batch4.
- [ ] Decidir mini-batch adicional o primer surrogate exploratorio.
- [ ] Decidir si se abre modulo geometrico con 2-3 STL reales + formas sinteticas controladas.
- [ ] Completar evals APOS-X sobre las tres skills repo-locales y endurecer `apos-run`.

## Bloqueos
- No iniciar otra tanda mientras AL batch2 este activo.
- No interpretar AL batch2 como campana global; es cierre dirigido de brackets.
- No tocar global/system sin confirmacion explicita.
- No aplicar `stash@{0}` completo sin revision.
- No borrar backups ni crudos locales.

## Fuera de alcance por ahora
- Campana parametrica grande.
- Watchers en background.
- MCP server local.
- Vector DB.
- Dashboard complejo.
