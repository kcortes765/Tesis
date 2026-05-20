# AL4 after-AL3 lightweight export

Fuente local: `data/results.sqlite`, `data/processed/al4_*`, `data/production_20260518_1542.log`.

## Resumen operacional
- Estado: completed
- Casos oficiales: 8/8
- Fallos numericos: 0
- Clases por `displacement_only`: 5 ESTABLE, 3 FALLO
- Tiempo total: 35.5 h
- dp: 0.003 m

## Lectura corta
AL4 cerro varios brackets bajando mu dentro de rangos ya observados. A diferencia de AL3, no salio todo estable: aparecieron fallos fisicos por desplazamiento en puntos clave, por lo que el lote aporta informacion directa para reentrenar el GP en la laptop.

La rotacion se mantiene como diagnostico: algunos casos rotan mas de 5 grados, pero la clase se decide por `moved` bajo `classification_mode=displacement_only`.

## Casos mas cercanos al umbral
- al4_highH_m100_mu0865: ESTABLE, Dmax=4.86% d_eq, margen=+0.14% d_eq
- al4_highH_m115_mu0750: FALLO, Dmax=5.45% d_eq, margen=-0.45% d_eq
- al4_base_m085_mu0790: FALLO, Dmax=6.18% d_eq, margen=-1.18% d_eq

## Archivos
- `al_batch4_summary.csv`: tabla oficial AL4 desde SQLite.
- `processed_inventory.csv`: inventario liviano de `data/processed/al4_*`.
- `al_batch4_after_al3_20260518.csv`: matriz corrida.
- `production_status.json`: snapshot final.
- `production_log_tail.txt`: cola relevante del log productivo.
- `run_files/`: `Run.csv` y `RunPARTs.csv` por caso.

No incluye Chrono/Gauges completos, `.bi4`, `.ibi4`, VTK, `Part*`, `cases/` ni carpetas `_out`.
