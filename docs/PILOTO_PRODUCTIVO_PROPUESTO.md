# Piloto productivo propuesto

## Estado

Propuesta preliminar. No correr sin confirmacion explicita.

## Matriz y comando seguro

Matriz piloto explicita:

- `config/pilot_productivo_20260430.csv`

Dry-run verificado:

```powershell
python scripts\run_production.py --prod --matrix config\pilot_productivo_20260430.csv --max-cases 5 --dry-run --no-notify
```

Comando real recomendado, solo con confirmacion explicita:

```powershell
python scripts\run_production.py --prod --matrix config\pilot_productivo_20260430.csv --max-cases 5 --no-notify
```

No usar `python scripts\run_production.py --pilot --prod` por ahora: puede leer/generar una matriz mas grande que el piloto previsto.

## Objetivo

Validar el flujo productivo con `dp=0.003`, `classification_mode=displacement_only` y `reference_time_s=0.5` antes de lanzar una campana parametrica grande.

El piloto debe confirmar:

- GenCase termina;
- DualSPHysics termina;
- Chrono escribe CSV completo;
- `data_cleaner.py` clasifica con `displacement_only`;
- SQLite/CSV guardan `criterion_mode`, `criterion_class`, `criterion_reference_time_s`, `moved`, `rotated`;
- la nomenclatura de casos es trazable;
- no se mezclan fallos numericos con fallos fisicos.

## Scripts candidatos

1. `scripts/run_production.py`
   - CLI con `--prod`, `--pilot`, `--generate`, `--desde`, `--dry-run`.
   - Usa `src/main_orchestrator.py`.
   - Candidato principal para campana, pero antes requiere definir matriz piloto/productiva controlada.

2. `src/main_orchestrator.py`
   - Genera LHS y ejecuta un caso mediante `run_pipeline_case`.
   - Ya queda ajustado para postprocesar con `classification_mode="displacement_only"` y `reference_time_s=0.5`.
   - Candidato base para flujo productivo.

3. `scripts/run_convergence_threshold.py`
   - Candidato auxiliar para casos unitarios controlados.
   - No es el runner natural de campana grande, pero es util para pruebas puntuales por CLI.

## Casos propuestos

| case_id | dam_height_m | mass_kg | rot_z_deg | friction_mu | slope_inv | motivo |
|---|---:|---:|---:|---:|---:|---|
| prod_pilot_stable_high_mu | 0.20 | 1.0 | 0 | 0.75 | 20 | Estable esperado por friccion alta |
| prod_pilot_fail_low_mu | 0.20 | 1.0 | 0 | 0.60 | 20 | Fallo esperado por friccion baja |
| prod_pilot_frontier | 0.20 | 1.0 | 0 | 0.6806 | 20 | Caso cerca del bracket dp=0.003 |
| prod_pilot_low_friction_stronger_h | 0.25 | 1.0 | 0 | 0.30 | 20 | Hidraulica/friccion mas exigente |
| prod_pilot_slope_check | 0.20 | 1.0 | 0 | 0.68 | 10 | Chequeo de variable pendiente |

## Advertencias

- No usar esta tabla como diseno final de tesis; es piloto operacional.
- No lanzar los 5 casos hasta tener definida la convencion de nombres y matriz CSV oficial.
- Si un caso cae por I/O o solver, registrarlo como fallo numerico, no como falla fisica.
- La frontera de `dp=0.003` no debe recalcularse desde este piloto salvo que se decida una campana especifica para eso.
