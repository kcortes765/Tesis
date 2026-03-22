# .apos-auto — APOS Automático (staging)

Este directorio es actualizado AUTOMÁTICAMENTE por agente.ps1 durante ejecución headless.

**NO es el APOS oficial del proyecto.** Es un borrador que se promueve a `.apos/` después de revisión humana.

## Flujo
1. `agente.ps1 -All` corre features → actualiza `.apos-auto/HANDOFF.md` y `STATUS.md`
2. Usuario vuelve → lee `.apos-auto/` → revisa qué hizo el agente
3. Si aprueba → `/guardar` merge `.apos-auto/` → `.apos/`
4. `.apos-auto/` se limpia para la siguiente corrida

## Archivos
- `HANDOFF.md` — log acumulativo de lo que hizo cada feature
- `STATUS.md` — estado al terminar la corrida
- `ERRORS.md` — features que fallaron y por qué
