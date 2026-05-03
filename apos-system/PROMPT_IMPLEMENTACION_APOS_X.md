# PROMPT_IMPLEMENTACION_APOS_X

Actua como implementador senior de APOS-X en esta workspace Windows/Codex.

Objetivo:
Migrar el sistema APOS actual a APOS-X sin romper nada. APOS-X debe ser local-first, auditable, compatible con Codex, conservador, modular y util para proyectos largos.

Reglas criticas:
1. No borres ni reemplaces nada sin backup.
2. Audita rutas actuales antes de modificar.
3. Crea backup fechado antes de cualquier cambio.
4. No modifiques skills `.system`.
5. No modifiques skills globales/config global/hooks globales sin confirmacion explicita.
6. No pegues chats completos en APOS.
7. No inventes contexto: separa hechos verificados, decisiones, inferencias, pendientes y riesgos.
8. Respeta append-only:
   - `DECISIONS.md`
   - `JOURNAL.md`
   - `SOURCES.md`
   - `RESEARCH_LOG.md`

Implementa:
- `apos-system/`
- templates `.apos/`
- skills `init-apos`, `retomar`, `guardar`, `apos-skill-governance`
- modules `chat-transfer`, `research-autonomo`, `safe-harness`, `quality-evals`
- `apos-run`
- Codex adapter
- evals locales

Reglas de instalacion:
1. Primero proyecto sandbox.
2. Luego este proyecto en dry-run.
3. Luego repo-local `.agents/skills`.
4. User/global solo despues de validar y con confirmacion.
