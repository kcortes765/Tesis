# CONTEXT_POLICY

## Lectura minima
1. `INDEX.md`
2. `STATUS.md`
3. `HANDOFF.md`
4. `PLAN.md`

## Lectura bajo demanda
- `ACTIVE_SPEC.md` si cambia el alcance.
- `WORKING_MODEL.md` si cambia arquitectura o pipeline.
- `DECISIONS.md` si la tarea toca decisiones metodologicas.
- `JOURNAL.md` si se necesita historia reciente.
- `RISKS.md` y `OPEN_QUESTIONS.md` si hay ejecucion, produccion o incertidumbre.
- `NARRATIVE.md` solo para reconstruccion historica amplia.

## Prioridad de evidencia
1. Archivos reales actuales.
2. Resultados de comandos recientes.
3. `DECISIONS.md`.
4. `STATUS.md`.
5. `JOURNAL.md`.
6. `NARRATIVE.md`.
7. Chat actual.
8. Memoria conversacional.
9. Fuentes externas.

## Clasificacion obligatoria
- Hecho verificado.
- Decision.
- Inferencia.
- Pendiente.
- Riesgo.
- Desconocido.

## Cuando pedir confirmacion
- Antes de tocar skills globales, `.system`, hooks o configuracion global.
- Antes de lanzar campanas productivas o GPU batch.
- Antes de borrar, mover o sobrescribir outputs.
- Antes de cambiar criterios metodologicos cerrados.

## Cuando usar safe-harness
Usar safe-harness o `apos-run` para comandos productivos, grandes, destructivos, ambiguos, GPU, batch o costosos.

## Que no cargar por defecto
- Chats completos.
- Outputs binarios pesados.
- `cases/**/_out` completos.
- `Part*.bi4`, VTK o artefactos grandes salvo necesidad justificada.
- Todo `JOURNAL.md` historico.

## Politica de memoria
Guardar solo informacion que permita continuar, justificar o auditar. No reemplazar trazabilidad por confianza en el chat.
