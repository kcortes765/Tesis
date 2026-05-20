# PLAN

## Objetivo activo
Construir una tesis fuerte con plan ambicioso y jerarquico: cerrar primero la frontera base `[H, mu, m*]`, validarla, y luego expandir a pendiente, orientacion y forma sin perder interpretabilidad.

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
- [x] Activar watcher externo ntfy para AL5 lanzado con `--no-notify`.
- [ ] Traer AL5 a laptop.
- [ ] Reentrenar GP after-AL5.
- [ ] Decidir holdout/checks finos `dp=0.002`.
- [ ] Actualizar web post-convergencia con AL4 y GP after-AL4.
- [ ] Seleccionar variables secundarias: pendiente, orientacion y formas/STL representativas.
- [ ] Al cerrar AL5, exportar liviano, subir por Git y registrar que ntfy estuvo activo.
- [ ] Preparar plan ambicioso post-base con presupuesto de ~90-130 simulaciones adicionales por etapas.
- [ ] Analizar si las 10 formas STL disponibles aportan variacion geometrica suficiente o si algunas son redundantes.
- [ ] Disenar sanity de contacto por forma.
- [ ] Decidir campana de forma: idealmente 10 formas, pero solo si pasan filtros geometricos/contacto.

## Linea metodologica prevista
1. Cerrar frontera base con `[H, mu, m*]`.
2. Validar la frontera base con holdout/repeticiones marginales.
3. Agregar checks finos `dp=0.002` en pocos puntos criticos.
4. Agregar pendiente como extension controlada.
5. Agregar orientacion como sensibilidad controlada.
6. Agregar forma como extension fuerte. Objetivo ideal: usar las 10 formas STL, siempre que el analisis geometrico demuestre que no son redundantes y que cada una pasa sanity de contacto.
7. Entregar estado limite, fragilidad condicional, incertidumbre y validacion por capas.

## Plan ambicioso de simulaciones
- Base final `[H, mu, m*]`: AL5 + posible AL6 + holdout + checks `dp=0.002`.
- Pendiente: mini-campana dirigida en varios `slope_inv`.
- Orientacion: sensibilidad por angulos discretos del bloque.
- Forma: idealmente 10 STL, con sanity por forma y casos hidraulicos cerca de frontera.
- Rango objetivo: `90-130` simulaciones adicionales maximas planificadas por etapas, no lanzadas simultaneamente.

## Bloqueos
- No lanzar nuevos casos si la WS no esta sincronizada por Git.
- No usar GP legacy ni reentreno automatico.
- No versionar crudos pesados.
- No usar el caso parcial de batch4 como oficial.
- No abrir forma si no esta resuelto el procesamiento consistente de volumen, centroide, masa, inercia, apoyo inicial e insertion point por STL.

## Fuera de alcance por ahora
- Factorial completo 6D sin active learning.
- Dominio amplio de forma sin seleccion geometrica/contacto previa.
- Claims universales de bloques costeros.
