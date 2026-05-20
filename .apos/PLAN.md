# PLAN

## Objetivo activo
Cerrar de forma robusta la frontera base `[H, mu, m*]` con active learning trazable, antes de abrir pendiente, orientacion y forma como extensiones jerarquicas.

## Fase actual
Post-AL4 en laptop: GP after-AL4 reentrenado y AL5 preparado para ejecutar en WS.

## Proximos hitos
- [x] Cerrar convergencia y adoptar `dp=0.003` como resolucion operativa.
- [x] Ejecutar piloto, batch2, batch3, batch4, AL1 y AL2.
- [x] Bloquear reentrenamiento GP automatico al terminar produccion.
- [x] Entrenar GP after-AL2 de forma deliberada.
- [x] Generar y correr AL3 en WS.
- [x] Traer AL3 a laptop.
- [x] Entrenar GP after-AL3 de forma deliberada.
- [x] Actualizar web post-convergencia con AL3 y GP after-AL3.
- [x] Generar matriz AL4.
- [x] Preparar prompt WS AL4.
- [x] En WS: dry-run AL4.
- [x] En WS: ejecutar AL4.
- [x] Exportar AL4 liviano.
- [x] Subir AL4 por Git a laptop.
- [x] Reentrenar GP after-AL4 en laptop.
- [x] Decidir si sigue AL5, holdout o checks finos `dp=0.002`.
- [x] Generar matriz AL5.
- [x] Preparar prompt WS AL5.
- [ ] Commit/push de GP after-AL4 y AL5.
- [ ] En WS: dry-run AL5.
- [ ] En WS: ejecutar AL5.
- [ ] Traer AL5 a laptop.
- [ ] Reentrenar GP after-AL5.
- [ ] Decidir holdout/checks finos `dp=0.002`.
- [ ] Actualizar web post-convergencia con AL4 y GP after-AL4.
- [ ] Seleccionar variables secundarias: pendiente, orientacion y formas/STL representativas.

## Linea metodologica prevista
1. Cerrar frontera base con `[H, mu, m*]`.
2. Validar la frontera base con holdout/repeticiones marginales.
3. Agregar checks finos `dp=0.002` en pocos puntos criticos.
4. Agregar pendiente como extension controlada.
5. Agregar orientacion como sensibilidad controlada.
6. Agregar forma con pocas geometrias representativas elegidas por analisis STL.
7. Entregar estado limite, fragilidad condicional, incertidumbre y validacion por capas.

## Bloqueos
- No lanzar nuevos casos si la WS no esta sincronizada por Git.
- No usar GP legacy ni reentreno automatico.
- No versionar crudos pesados.
- No usar el caso parcial de batch4 como oficial.

## Fuera de alcance por ahora
- Factorial completo 6D sin active learning.
- Dominio amplio de forma sin seleccion geometrica previa.
- Claims universales de bloques costeros.
