# PLAN

## Objetivo activo
Cerrar la transicion desde convergencia a produccion controlada y preparar APOS-X local para continuidad confiable entre chats.

## Fase actual
Piloto productivo en ejecucion + migracion APOS-X local.

## Proximos hitos
- [x] Cerrar convergencia y adoptar `dp=0.003` como malla operativa.
- [x] Documentar configuracion productiva oficial.
- [x] Crear matriz piloto explicita de 5 casos.
- [x] Agregar guardas a `scripts/run_production.py`.
- [x] Ejecutar dry-run del piloto.
- [x] Lanzar piloto real de 5 casos.
- [x] Esperar fin del piloto y auditar resultados.
- [x] Crear export liviano del piloto productivo.
- [ ] Revisar cientificamente el export del piloto.
- [ ] Implementar `apos-system/` local con skills y safe-harness.
- [ ] Instalar skills repo-locales en `.agents/skills` solo despues de validar.
- [ ] Disenar primera tanda productiva real con limite explicito y dry-run previo.

## Bloqueos
- No iniciar otra tanda sin revisar el export y hacer dry-run.
- No tocar global/system sin confirmacion explicita.

## Fuera de alcance por ahora
- Campana parametrica grande.
- Watchers en background.
- MCP server local.
- Vector DB.
- Dashboard complejo.
