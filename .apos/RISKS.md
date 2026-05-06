# RISKS

## RISK-20260501-001 - Piloto/batch productivo en ejecucion

Estado: mitigado
Severidad: alta
Probabilidad: media
Evidencia: piloto 5/5 OK y batch2 8/8 OK; `data/production_status.json` reporta `phase=completed`.
Mitigacion: no lanzar otra tanda hasta auditar export; conservar outputs crudos fuera de Git y usar exports livianos.
Relacionado: `scripts/run_production.py`, `config/pilot_productivo_20260430.csv`, `config/batch2_productivo_20260503.csv`

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

## RISK-20260506-001 - Sobreinterpretar batch2 como campana completa

Estado: activo
Severidad: media
Probabilidad: media
Evidencia: batch2 tiene 8 casos dirigidos, no un muestreo amplio del espacio parametrico.
Mitigacion: presentarlo como lote exploratorio/informativo; antes de afirmar fragilidad global, disenar otro batch o surrogate con validacion.
Relacionado: `exports/batch2_productivo_20260505/batch2_summary.csv`

## RISK-20260506-002 - Mezclar rotacion diagnostica con criterio primario

Estado: activo
Severidad: media
Probabilidad: media
Evidencia: 5/8 casos batch2 tienen `rotated=True`, pero solo `moved=True` define FALLO bajo `displacement_only`.
Mitigacion: reportar rotacion en columna separada; no cambiar `criterion_class` por rotacion.
Relacionado: `src/data_cleaner.py`, `exports/batch2_productivo_20260505/batch2_summary.csv`
