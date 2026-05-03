---
name: apos
description: Inicializa, instala o repara APOS en un proyecto greenfield o brownfield. Usar cuando el usuario diga /apos, instalar APOS, preparar APOS, crear memoria del proyecto, migrar APOS o dejar el repo listo para continuidad.
---

# /apos

## Objetivo
Dejar un proyecto listo para continuidad APOS sin inventar contexto ni tocar configuracion global.

Funciona para:
- greenfield: repo sin `.apos/`.
- brownfield: repo con `.apos/` parcial, viejo o roto.

## Reglas duras
- Backup antes de migrar.
- No modificar skills globales, `.system`, hooks o config global sin confirmacion explicita.
- No copiar chats completos.
- No tocar codigo productivo salvo pedido explicito.
- No sobrescribir append-only; agregar entradas nuevas.

## Flujo
1. Detectar raiz real del proyecto.
2. Leer instrucciones del repo: `AGENTS.md`, README, docs clave.
3. Auditar `.apos/` si existe.
4. Crear snapshot en `.apos/snapshots/` antes de cambios.
5. Crear o reparar estructura:
   - `README.md`
   - `BOOTSTRAP.md`
   - `STATUS.md`
   - `HANDOFF.md`
   - `PLAN.md`
   - `ACTIVE_SPEC.md`
   - `WORKING_MODEL.md`
   - `DECISIONS.md`
   - `JOURNAL.md`
   - `NARRATIVE.md`
   - `SOURCES.md`
   - `QUALITY.md`
   - `INDEX.md`
   - `MODULES.md`
   - `RISKS.md`
   - `OPEN_QUESTIONS.md`
   - `CONTEXT_POLICY.md`
   - `RESEARCH_LOG.md`
   - `evidence/`, `research/`, `transfers/`, `snapshots/`, `cache/`
6. Crear `.agents/skills` repo-local con solo:
   - `apos`
   - `apos-status`
   - `guardar`
7. Registrar en `JOURNAL.md` y `DECISIONS.md` si hubo decision de migracion.

## Salida
Reportar:
- si era greenfield o brownfield
- backup creado
- archivos creados/reparados
- riesgos detectados
- proximo paso recomendado
