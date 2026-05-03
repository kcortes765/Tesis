---
name: apos-status
description: Retoma o diagnostica el estado APOS del proyecto. Usar cuando el usuario diga /apos-status, /retomar, retomemos, que sigue, estado APOS, continuar o revisar continuidad.
---

# /apos-status

## Objetivo
Reconstruir el estado operativo del proyecto desde `.apos/` y archivos reales, sin escribir por defecto.

## Lectura minima
1. `.apos/CONTEXT_POLICY.md`
2. `.apos/INDEX.md`
3. `.apos/STATUS.md`
4. `.apos/HANDOFF.md`
5. `.apos/PLAN.md`
6. `.apos/RISKS.md`
7. `.apos/OPEN_QUESTIONS.md`
8. Tail de `.apos/DECISIONS.md` y `.apos/JOURNAL.md` si hace falta.

Si falta `.apos/`, recomendar `/apos`.

## Respuesta
Entregar:
- estado actual
- hechos verificados
- decisiones activas
- inferencias
- pendientes
- riesgos
- proximo paso concreto
- que no tocar todavia

## Reglas
- No escribir archivos salvo que el usuario lo pida.
- No cargar todo `JOURNAL.md`.
- Si hay contradiccion, priorizar archivos reales y comandos recientes.
