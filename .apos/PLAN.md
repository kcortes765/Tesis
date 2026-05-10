# PLAN

## Objetivo activo
Ejecutar batch3 productivo dirigido y usar piloto + batch2 + batch3 para decidir el siguiente paso cientifico sin lanzar una campana grande.

## Fase actual
Batch3 productivo dirigido completado y exportado liviano para sincronizacion por Git.

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
- [ ] Revisar cientificamente el export del piloto, batch2 y batch3 juntos.
- [ ] Decidir mini-batch adicional o primer surrogate exploratorio.
- [ ] Completar evals APOS-X sobre las tres skills repo-locales y endurecer `apos-run`.

## Bloqueos
- No iniciar otra tanda antes de revisar cientificamente piloto + batch2 + batch3.
- No tocar global/system sin confirmacion explicita.

## Fuera de alcance por ahora
- Campana parametrica grande.
- Watchers en background.
- MCP server local.
- Vector DB.
- Dashboard complejo.
