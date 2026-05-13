# Postproceso batch4 y preparacion AL batch1 - 2026-05-13

## Origen y seguridad
- Repo local HEAD: `a9aa449`.
- Batch4 leido desde `origin/master` commit `95d9468` sin hacer `git pull` destructivo.
- Los cambios locales APOS/no trackeados no se pisan en este postproceso.

## Dataset maestro
- Filas totales piloto+batch2+batch3+batch4: 35.
- Casos GP-compatible oficiales: 30.
- Clases GP-compatible: ESTABLE=14, FALLO=16.
- Target continuo: `g_pct = 5 - disp_pct_deq`; positivo estable, negativo falla.
- Target de entrenamiento robusto: `g_train_clip_pct = clip(g_pct, -20, 8)` para que fallas gigantes no dominen la frontera.

## Diagnostico batch4
- Batch4 oficial aporta una tercera variable fisica: `boulder_mass` o `m*`.
- Oficiales batch4: 11; ESTABLE=6, FALLO=5.
- Casos cerca de frontera oficial batch4 (`|g| <= 2`): 3.
- `m=0.85`: 4/4 fallan; confirma que masa baja desplaza la frontera hacia mayor resistencia requerida.
- `m=1.15`: 3/3 estables; ancla zona segura intermedia.
- `m=1.25`: 2/2 estables oficiales; el caso parcial `mu=0.860` queda fuera del entrenamiento.

## GP seed
- GP Mat?rn 5/2 entrenado con 30 casos compatibles.
- Kernel ajustado: `1.3**2 * Matern(length_scale=[0.197, 0.279, 0.615], nu=2.5) + WhiteKernel(noise_level=0.0141)`.
- LOO MAE sobre `g_train_clip_pct`: 3.80 puntos porcentuales de d_eq.
- LOO RMSE sobre `g_train_clip_pct`: 5.98 puntos porcentuales de d_eq.
- Este GP es suficiente para proponer candidatos, no para cerrar resultados finales todavia.

## Siguiente lote recomendado si se acepta el GP seed
Matriz propuesta `al_batch1_matrix_20260513.csv`:

| case_id | H | m | mu | motivo |
|---|---:|---:|---:|---|
| `al1_H174_m093_mu0755` | 0.174 | 0.930 | 0.755 | frontera/incertidumbre GP; media g=-0.00, sigma=9.25 |
| `al1_H170_m118_mu0740` | 0.170 | 1.180 | 0.740 | frontera/incertidumbre GP; media g=-0.00, sigma=10.54 |
| `al1_H200_m117_mu0885` | 0.200 | 1.170 | 0.885 | frontera/incertidumbre GP; media g=0.00, sigma=12.18 |
| `al1_H178_m086_mu0620` | 0.178 | 0.860 | 0.620 | frontera/incertidumbre GP; media g=0.00, sigma=6.76 |
| `al1_H200_m096_mu0810` | 0.200 | 0.960 | 0.810 | frontera/incertidumbre GP; media g=0.00, sigma=7.73 |
| `al1_H226_m124_mu0770` | 0.226 | 1.240 | 0.770 | control high-H/high-mass; media g=0.01, sigma=4.85 |

## Gate antes de WS
- Revisar visualmente `gp_seed_cuts_and_al_candidates_20260513.png` y `batch4_mass_effect_map_20260513.png`.
- Si el GP propone puntos absurdos o demasiado pegados a existentes, reemplazar por lote dirigido manual.
- No incluir el caso parcial batch4 como oficial ni repetirlo antes de necesitarlo.
- No correr `dp=0.002` todavia: primero hacer AL batch1 o mini-lote de confirmacion.
