---
name: safe-harness
description: Usa APOS-X safe harness para auditar y bloquear comandos productivos, grandes, destructivos, GPU o ambiguos antes de ejecutarlos. Debe registrar evidencia y exigir matriz explicita, dry-run y limites de casos.
---

# safe-harness

Usar para:
- `run_production.py`
- comandos con `--prod`
- GPU batch
- comandos destructivos
- ejecuciones costosas

Reglas:
- `run_production.py --pilot --prod` se bloquea.
- Produccion requiere `--matrix`, `--max-cases` y dry-run o token explicito.
- Registrar evidencia en `.apos/evidence/harness-runs/`.
