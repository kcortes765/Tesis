# PLAN

## Objetivo activo
Analizar resultados consolidados hasta AL batch2 y preparar el siguiente paso cientifico sin lanzar otra tanda todavia.

## Fase actual
Post-AL2: todos los lotes dirigidos principales estan exportados y listos para analisis conjunto.

## Proximos hitos
- [x] Cerrar convergencia y adoptar dp=0.003 como malla operativa.
- [x] Ejecutar piloto, batch2, batch3, batch4 y AL1.
- [x] Ejecutar AL batch2 bracket-closing.
- [x] Crear export liviano AL batch2.
- [x] Bloquear reentrenamiento GP automatico al terminar produccion.
- [ ] Traer AL2 a laptop con git pull.
- [ ] Analizar piloto + batch2 + batch3 + batch4 + AL1 + AL2 juntos.
- [ ] Regenerar figuras productivas/AL incorporando AL2.
- [ ] Definir surrogate deliberado: variables, target continuo, validacion y exclusiones.
- [ ] Decidir si repetir/reprocesar el caso parcial batch4.
- [ ] Diseñar proximo mini-batch solo si el analisis consolidado lo justifica.

## Bloqueos
- No lanzar nuevas simulaciones antes del analisis consolidado.
- No usar GP legacy automatico como resultado cientifico.
- No versionar crudos pesados.

## Fuera de alcance por ahora
- Campana grande.
- Geometria multiple.
- GP final/paper sin auditoria de datos.
