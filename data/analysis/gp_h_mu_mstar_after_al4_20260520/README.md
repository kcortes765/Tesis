# GP H-mu-mstar after AL4

Fecha: 2026-05-20

## Objetivo

Entrenar de forma deliberada el surrogate actual de la tesis, sin usar el
reentrenamiento legacy automatico.

## Modelo

- Inputs: `H`, `mu`, `m*`.
- Target fisico: `g = 5 - Dmax(% d_eq)`.
- Interpretacion: `g > 0` estable; `g < 0` movimiento/fallo.
- Target de entrenamiento: `g` con clipping en [-20.0, 4.0] `% d_eq`.
- Kernel: `ConstantKernel * Matern(nu=2.5, ARD) + WhiteKernel`.
- Casos usados: 64.
- Casos excluidos: 5.

## Validacion LOO

- MAE train target: 2.557 `% d_eq`.
- RMSE train target: 4.226 `% d_eq`.
- Accuracy clase LOO: 0.875.
- Falsos estables LOO: 3.
- Falsos fallos LOO: 5.

## Archivos

- `dataset_master.csv`: todos los casos leidos desde exports.
- `dataset_used.csv`: casos oficiales dentro del dominio usados para GP.
- `brackets_by_h_mstar.csv`: brackets observados por corte H-m*.
- `loo_predictions.csv`: validacion leave-one-out.
- `candidate_grid_ranked.csv`: grilla candidata ordenada por U-value.
- `al5_candidates.csv`: candidatos recomendados para siguiente lote.
- `validation_metrics.json`: metricas y kernel final.
- `figures/`: figuras de validacion, frontera e incertidumbre.
- Modelo: `models/surrogates/gp_h_mu_mstar_after_al4_20260520.pkl`.

## AL5 recomendado

```csv
case_id,dam_height,boulder_mass,boulder_rot_z,friction_coefficient,slope_inv
al5_highH_m085_mu0900,0.225,0.85,0,0.900,20
al5_base_m085_mu0795,0.200,0.85,0,0.795,20
al5_midH_m100_mu0744,0.210,1.00,0,0.744,20
al5_highH_m100_mu08625,0.225,1.00,0,0.863,20
al5_midH_m115_mu0700,0.210,1.15,0,0.700,20
al5_highH_m115_mu0755,0.225,1.15,0,0.755,20
al5_midH_m125_mu0660,0.210,1.25,0,0.660,20
al5_highH_m125_mu0690,0.225,1.25,0,0.690,20
```
