# PLAN

## Objetivo activo
Ejecutar AL3 en la WS usando la matriz propuesta por el GP after-AL2 y mantener el reentrenamiento del modelo en la laptop.

## Fase actual
Post-AL2 con surrogate deliberado after-AL2 y web post-convergencia actualizada.

## Proximos hitos
- [x] Cerrar convergencia y adoptar dp=0.003 como resolucion operativa.
- [x] Ejecutar piloto, batch2, batch3, batch4, AL1 y AL2.
- [x] Bloquear reentrenamiento GP automatico al terminar produccion.
- [x] Traer AL2 a laptop.
- [x] Entrenar GP after-AL2 de forma deliberada.
- [x] Generar matriz AL3.
- [x] Actualizar web post-convergencia con AL2 y GP after-AL2.
- [ ] Subir cambios a Git.
- [ ] En WS: dry-run AL3.
- [ ] En WS: ejecutar AL3 si el dry-run coincide.
- [ ] Exportar AL3 liviano y traerlo a laptop.
- [ ] Reentrenar GP after-AL3 en laptop.
- [ ] Decidir si sigue AL4, holdout o checks finos `dp=0.002`.

## Bloqueos
- No lanzar nuevos casos si la WS no esta sincronizada por Git.
- No usar GP legacy ni reentreno automatico.
- No versionar crudos pesados.

## Fuera de alcance por ahora
- Campana masiva.
- Dominio amplio de geometria.
- GP final/paper sin validar despues de AL3.
