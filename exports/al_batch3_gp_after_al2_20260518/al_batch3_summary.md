# AL batch3 GP after-AL2 - export liviano

Fecha export: 2026-05-18 15:00

## Estado operacional

- Lote: AL3 after-AL2.
- Casos objetivo: 8.
- Casos oficiales en SQLite: 8/8.
- Fallos numericos: 0 segun `production_status.json`.
- Estables: 8.
- Fallos por desplazamiento: 0.
- Resolucion: dp=0.003 m.
- Criterio: displacement_only.
- reference_time_s: 0.5.
- Rotacion: diagnostica, no criterio primario.

## Archivos incluidos

- `al_batch3_summary.csv`: tabla oficial extraida desde SQLite.
- `processed_inventory.csv`: inventario liviano de `data/processed/al3_*`.
- `al_batch3_gp_after_al2_20260516.csv`: matriz corrida.
- `production_status.json`: estado final del lote.
- `production_log_tail.txt`: cola relevante del log productivo AL3.

## Casos mas cercanos al umbral

- al3_base_m085_mu0800: ESTABLE, Dmax=4.85% d_eq, margin=0.15% d_eq
- al3_highH_m115_mu0760: ESTABLE, Dmax=4.29% d_eq, margin=0.71% d_eq
- al3_midH_m100_mu0755: ESTABLE, Dmax=3.58% d_eq, margin=1.42% d_eq
- al3_midH_m085_mu0900: ESTABLE, Dmax=3.37% d_eq, margin=1.63% d_eq
- al3_highH_m100_mu0870: ESTABLE, Dmax=2.98% d_eq, margin=2.02% d_eq
- al3_highH_m125_mu0700: ESTABLE, Dmax=2.95% d_eq, margin=2.05% d_eq

## Lectura preliminar

Este export consolida AL3 para analisis en laptop junto con los lotes previos. No incluye crudos pesados. El entrenamiento GP debe mantenerse deliberado en laptop, no automatico en la WS.

## No incluido

No se incluyen `cases/`, carpetas `_out`, `.bi4`, `.ibi4`, VTK, Part* ni outputs crudos pesados.
