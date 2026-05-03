# Piloto productivo 2026-05-01

## Resultado operativo

- Estado: completed
- Casos completados: 5/5
- Fallidos numericos: 0
- Tiempo total: 22.11 h
- Inicio: 2026-04-30T17:58:30.854818
- Termino: 2026-05-01T16:04:49.244926
- dp: 0.003

## Clases fisicas por `displacement_only`

- ESTABLE: 2
- FALLO: 3
- Rotated=True diagnostico: 4/5

| case_id | mu | H(m) | slope | class | moved | rotated | disp % d_eq | rot deg | time min |
|---|---:|---:|---:|---|---|---|---:|---:|---:|
| prod_pilot_stable_high_mu | 0.75 | 0.2 | 1:20 | ESTABLE | False | False | 1.231657 | 4.461535 | 249.0484 |
| prod_pilot_fail_low_mu | 0.6 | 0.2 | 1:20 | FALLO | True | True | 42.3796 | 10.67676 | 249.6686 |
| prod_pilot_frontier | 0.6806 | 0.2 | 1:20 | FALLO | True | True | 5.021031 | 5.07661 | 249.3627 |
| prod_pilot_stronger_hydraulic | 0.3 | 0.25 | 1:20 | FALLO | True | True | 1341.54 | 55.77997 | 324.9678 |
| prod_pilot_slope_check | 0.68 | 0.2 | 1:10 | ESTABLE | False | True | 1.420254 | 7.427412 | 252.3756 |

## Lectura cientifica minima

Los 5 casos terminaron OK desde el punto de vista operacional: GenCase, DualSPHysics, Chrono CSV, postproceso, SQLite y status final funcionaron sin fallos numericos. El piloto no debe interpretarse como campana final, sino como validacion del pipeline productivo con una matriz pequena y trazable.

El criterio primario fue `classification_mode=displacement_only` con `reference_time_s ~ 0.5`. Por tanto, `criterion_class` depende de `moved`; la rotacion se reporta como diagnostico y no cambia la clase primaria.

El piloto produjo 3 casos FALLO y 2 casos ESTABLE. El caso `prod_pilot_frontier` quedo practicamente sobre el umbral de 5% d_eq y debe tratarse como caso marginal. `prod_pilot_stronger_hydraulic` produjo desplazamiento muy grande, util como prueba de fallo claro. `prod_pilot_slope_check` fue ESTABLE por desplazamiento aunque `rotated=True`, lo que refuerza la necesidad de mantener la rotacion separada como diagnostico.

## Warning metodologico

No lanzar campana grande todavia solo por este 5/5. Primero revisar esta tabla, confirmar que los rangos parametricos del siguiente batch son fisicamente utiles y correr dry-run con matriz explicita + `--max-cases`.
