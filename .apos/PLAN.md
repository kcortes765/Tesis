# PLAN

## Objetivo activo
Ejecutar AL3 y preparar un plan jerarquico robusto de seis meses para pasar de frontera base `[H, mu, m*]` a una tesis con sensibilidad de pendiente, orientacion y forma.

## Fase actual
Post-AL2 con surrogate deliberate after-AL2, AL3 listo para WS y mock sintetico de entregable final creado.

## Proximos hitos
- [x] Cerrar convergencia y adoptar dp=0.003 como resolucion operativa.
- [x] Ejecutar piloto, batch2, batch3, batch4, AL1 y AL2.
- [x] Bloquear reentrenamiento GP automatico al terminar produccion.
- [x] Traer AL2 a laptop.
- [x] Entrenar GP after-AL2 de forma deliberada.
- [x] Generar matriz AL3.
- [x] Actualizar web post-convergencia con AL2 y GP after-AL2.
- [x] Subir GP/web/AL3 a Git en commit `6f9eb41`.
- [x] Crear mock sintetico de entregable final.
- [ ] En WS: dry-run AL3.
- [ ] En WS: ejecutar AL3 si el dry-run coincide.
- [ ] Exportar AL3 liviano y traerlo a laptop.
- [ ] Reentrenar GP after-AL3 en laptop.
- [ ] Definir plan jerarquico expandido con presupuesto de simulaciones.
- [ ] Decidir AL4/holdout/checks finos `dp=0.002`.
- [ ] Seleccionar variables secundarias: pendiente, orientacion y formas/STL representativas.

## Linea metodologica prevista
1. Cerrar frontera base con `[H, mu, m*]`.
2. Agregar pendiente como extension controlada, no mezclada desde el inicio.
3. Agregar orientacion como sensibilidad controlada.
4. Agregar forma con pocas geometria representativas, elegidas por analisis STL.
5. Validar con holdout, repeticiones marginales y `dp=0.002` selectivo.
6. Entregar estado limite, fragilidad condicional, incertidumbre y validacion por capas.

## Bloqueos
- No lanzar nuevos casos si la WS no esta sincronizada por Git.
- No usar GP legacy ni reentreno automatico.
- No versionar crudos pesados.
- No usar el mock sintetico como evidencia.

## Fuera de alcance por ahora
- Factorial completo 6D sin active learning.
- Dominio amplio de forma sin seleccion geometrica previa.
- Claims universales de bloques costeros.
