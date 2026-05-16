# GP H-mu-mstar after AL2

Fecha: 2026-05-16

## Objetivo

Entrenar de forma deliberada el surrogate actual de la tesis, sin usar el
reentrenamiento legacy automatico.

## Modelo

- Inputs: `H`, `mu`, `m*`.
- Target fisico: `g = 5 - Dmax(% d_eq)`.
- Interpretacion: `g > 0` estable; `g < 0` movimiento/fallo.
- Target de entrenamiento: `g` con clipping en [-20.0, 4.0] `% d_eq`.
- Kernel: `ConstantKernel * Matern(nu=2.5, ARD) + WhiteKernel`.
- Casos usados: 48.
- Casos excluidos: 5.

## Validacion LOO

- MAE train target: 3.140 `% d_eq`.
- RMSE train target: 4.736 `% d_eq`.
- Accuracy clase LOO: 0.875.
- Falsos estables LOO: 1.
- Falsos fallos LOO: 5.

## Archivos

- `dataset_master.csv`: todos los casos leidos desde exports.
- `dataset_used.csv`: casos oficiales dentro del dominio usados para GP.
- `brackets_by_h_mstar.csv`: brackets observados por corte H-m*.
- `loo_predictions.csv`: validacion leave-one-out.
- `candidate_grid_ranked.csv`: grilla candidata ordenada por U-value.
- `al3_candidates.csv`: candidatos recomendados para siguiente lote.
- `validation_metrics.json`: metricas y kernel final.
- `figures/`: figuras de validacion, frontera e incertidumbre.
- Modelo: `models/surrogates/gp_h_mu_mstar_after_al2_20260516.pkl`.

## AL3 recomendado

```csv
case_id,dam_height,boulder_mass,boulder_rot_z,friction_coefficient,slope_inv
al3_lowH_m085_mu0572,0.175,0.85,0,0.572,20
al3_base_m085_mu0800,0.200,0.85,0,0.800,20
al3_midH_m085_mu0900,0.210,0.85,0,0.900,20
al3_midH_m100_mu0755,0.210,1.00,0,0.755,20
al3_highH_m100_mu0870,0.225,1.00,0,0.870,20
al3_highH_m115_mu0760,0.225,1.15,0,0.760,20
al3_highH_m115_mu0780,0.225,1.15,0,0.780,20
al3_highH_m125_mu0700,0.225,1.25,0,0.700,20
```
