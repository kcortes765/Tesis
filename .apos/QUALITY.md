# QUALITY

Ultima actualizacion: 2026-05-01

## Estado de validacion
- init-apos: planned
- retomar: planned
- guardar: planned
- apos-skill-governance: planned
- safe-harness: planned
- chat-transfer: planned
- research-autonomo: planned
- quality-evals: planned

## Ultimas validaciones
- Backup local `.apos/snapshots/apox-migration-20260501_001524` creado antes de migrar.
- Inventario local confirmo piloto productivo activo y memoria APOS parcial.
- `python -m py_compile apos-system\harness\apos-run.py` paso sin errores.
- `apos-run preflight` bloqueo correctamente `run_production.py --pilot --prod`.
- `apos-run dry-run` registro la matriz piloto de 5 casos sin ejecutar simulaciones.
- `.agents/skills` contiene exactamente `apos`, `apos-status` y `guardar`, con frontmatter valido.

## Tests pendientes
- Validar append-only.
- Validar `retomar` corto/tecnico.
- Validar `guardar` sin perder decisiones.
- Validar bloqueo de `run_production.py --pilot --prod`.

## Regresiones conocidas
- Archivos APOS historicos tienen mojibake de encoding.
- Estado historico de convergencia estaba desfasado.
