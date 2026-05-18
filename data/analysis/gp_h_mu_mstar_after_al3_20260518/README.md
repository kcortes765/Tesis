# GP H-mu-mstar after AL3

Fecha: 2026-05-18

## Objetivo

Entrenar de forma deliberada el surrogate actual de la tesis, sin usar el
reentrenamiento legacy automatico.

## Modelo

- Inputs: `H`, `mu`, `m*`.
- Target fisico: `g = 5 - Dmax(% d_eq)`.
- Interpretacion: `g > 0` estable; `g < 0` movimiento/fallo.
- Target de entrenamiento: `g` con clipping en [-20.0, 4.0] `% d_eq`.
- Kernel: `ConstantKernel * Matern(nu=2.5, ARD) + WhiteKernel`.
- Casos usados: 56.
- Casos excluidos: 5.

## Validacion LOO

- MAE train target: 2.866 `% d_eq`.
- RMSE train target: 4.485 `% d_eq`.
- Accuracy clase LOO: 0.857.
- Falsos estables LOO: 2.
- Falsos fallos LOO: 6.

## Archivos

- `dataset_master.csv`: todos los casos leidos desde exports.
- `dataset_used.csv`: casos oficiales dentro del dominio usados para GP.
- `brackets_by_h_mstar.csv`: brackets observados por corte H-m*.
- `loo_predictions.csv`: validacion leave-one-out.
- `candidate_grid_ranked.csv`: grilla candidata ordenada por U-value.
- `al4_candidates.csv`: candidatos recomendados para siguiente lote.
- `validation_metrics.json`: metricas y kernel final.
- `figures/`: figuras de validacion, frontera e incertidumbre.
- Modelo: `models/surrogates/gp_h_mu_mstar_after_al3_20260518.pkl`.

## AL4 recomendado

```csv
case_id,dam_height,boulder_mass,boulder_rot_z,friction_coefficient,slope_inv
al4_lowH_m085_mu0566,0.175,0.85,0,0.566,20
al4_base_m085_mu0790,0.200,0.85,0,0.790,20
al4_midH_m085_mu0890,0.210,0.85,0,0.890,20
al4_midH_m100_mu0748,0.210,1.00,0,0.748,20
al4_highH_m100_mu0865,0.225,1.00,0,0.865,20
al4_highH_m115_mu0750,0.225,1.15,0,0.750,20
al4_highH_m125_mu0680,0.225,1.25,0,0.680,20
al4_base_m100_mu06808,0.200,1.00,0,0.681,20
```
