# RISKS

## RISK-20260501-001 - Piloto productivo en ejecucion

Estado: activo
Severidad: alta
Probabilidad: media
Evidencia: `data/production_status.json` reporta progreso 2/5 y proceso `DualSPHysics5.4_win64` activo.
Mitigacion: no lanzar otra tanda, no borrar outputs, monitorear solo lectura.
Relacionado: `scripts/run_production.py`, `config/pilot_productivo_20260430.csv`

## RISK-20260501-002 - Memoria APOS historica desfasada

Estado: activo
Severidad: media
Probabilidad: alta
Evidencia: `BOOTSTRAP.md`, `STATUS.md` y `HANDOFF.md` antiguos indicaban que `dp` no estaba cerrado.
Mitigacion: usar archivos reales y estado actualizado; mantener historicos como contexto, no fuente unica.
Relacionado: `STATUS.md`, `HANDOFF.md`, `CONTEXT_POLICY.md`

## RISK-20260501-003 - Ejecucion productiva accidental grande

Estado: activo
Severidad: alta
Probabilidad: media
Evidencia: el pipeline historico tenia matriz por defecto amplia y modos ambiguos.
Mitigacion: `--matrix`, `--max-cases`, `--dry-run`; siguiente paso: `apos-run`.
Relacionado: `scripts/run_production.py`, safe-harness APOS-X
