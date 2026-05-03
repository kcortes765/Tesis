---
name: guardar
description: Guarda el avance APOS de la sesion. Usar cuando el usuario diga /guardar, guardar avance, cerrar sesion, dejar handoff, actualizar APOS o preparar el proximo chat.
---

# /guardar

## Objetivo
Persistir el estado real de la sesion para que el proximo chat pueda continuar sin depender de memoria conversacional.

## Leer antes
1. `.apos/CONTEXT_POLICY.md`
2. `.apos/STATUS.md`
3. `.apos/HANDOFF.md`
4. `.apos/PLAN.md`
5. `.apos/RISKS.md`
6. `.apos/OPEN_QUESTIONS.md`

Si faltan, reportar que el proyecto necesita `/apos`.

## Actualizar archivos vivos
- `.apos/STATUS.md`
- `.apos/HANDOFF.md`
- `.apos/PLAN.md`
- `.apos/INDEX.md`
- `.apos/QUALITY.md` si hubo validacion.
- `.apos/RISKS.md` si cambio un riesgo.
- `.apos/OPEN_QUESTIONS.md` si cambio una incertidumbre.

## Append-only
Agregar entradas nuevas, nunca reescribir historia:
- `.apos/JOURNAL.md` siempre.
- `.apos/DECISIONS.md` si hubo decision real.
- `.apos/SOURCES.md` si hubo fuente nueva.
- `.apos/RESEARCH_LOG.md` si hubo investigacion cerrada.

## Clasificacion obligatoria
Separar:
- hecho verificado
- decision
- inferencia
- pendiente
- riesgo
- desconocido

## Cierre
Responder con:
- archivos actualizados
- evidencia/comandos relevantes
- proxima accion recomendada
- que no tocar todavia
