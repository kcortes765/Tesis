# PLAN

## Objetivo activo
Cerrar la transicion desde convergencia a produccion controlada, auditar piloto + batch2, y preparar el siguiente diseno sin lanzar una campana grande.

## Fase actual
Batch2 completado y exportado; siguiente paso es analisis cientifico y decision de diseno.

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
- [ ] Revisar cientificamente el export del piloto y batch2 juntos.
- [ ] Decidir mini-batch dirigido o primer surrogate exploratorio.
- [ ] Si hay otro lote: crear matriz explicita, dry-run y limite `--max-cases`.
- [ ] Completar evals APOS-X sobre las tres skills repo-locales y endurecer `apos-run`.

## Bloqueos
- No iniciar otra tanda hasta revisar cientificamente batch2.
- No tocar global/system sin confirmacion explicita.

## Fuera de alcance por ahora
- Campana parametrica grande.
- Watchers en background.
- MCP server local.
- Vector DB.
- Dashboard complejo.
