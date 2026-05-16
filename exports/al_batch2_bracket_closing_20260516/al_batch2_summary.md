# AL batch2 bracket closing - export liviano

Fecha export: 2026-05-16 17:24

## Estado operacional

- Lote: AL batch2 bracket closing.
- Casos objetivo: 10.
- Casos oficiales en SQLite: 10/10.
- Fallos numericos: 0 segun `production_status.json`.
- Estables: 5.
- Fallos por desplazamiento: 5.
- Resolucion: dp=0.003 m.
- Criterio: displacement_only.
- reference_time_s: 0.5.
- Rotacion: diagnostica, no criterio primario.

## Archivos incluidos

- `al_batch2_summary.csv`: tabla oficial extraida desde SQLite.
- `processed_inventory.csv`: inventario liviano de `data/processed/al2_*`.
- `al_batch2_bracket_closing_20260514.csv`: matriz corrida.
- `production_status.json`: estado final del lote.
- `production_log_tail.txt`: cola relevante del log productivo.

## Casos mas cercanos al umbral

- al2_midH_m085_mu0880: FALLO, Dmax=5.19% d_eq, margin=-0.19% d_eq
- al2_midH_m100_mu0770: ESTABLE, Dmax=4.31% d_eq, margin=0.69% d_eq
- al2_highH_m100_mu0880: ESTABLE, Dmax=3.31% d_eq, margin=1.69% d_eq
- al2_highH_m115_mu0740: FALLO, Dmax=6.72% d_eq, margin=-1.72% d_eq
- al2_base_m085_mu0820: ESTABLE, Dmax=2.28% d_eq, margin=2.72% d_eq

## Lectura preliminar

Este export solo consolida resultados. La interpretacion cientifica final debe hacerse despues de revisar la tabla completa, compararla con piloto, batch2, batch3, batch4 y AL1, y decidir el siguiente paso del surrogate/active learning. No se reentreno GP automaticamente: el reentrenamiento automatico quedo bloqueado y cualquier GP nuevo debe ser deliberado.

## No incluido

No se incluyen `cases/`, carpetas `_out`, `.bi4`, `.ibi4`, VTK, Part* ni outputs crudos pesados.
