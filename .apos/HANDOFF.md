# HANDOFF

## Proxima accion recomendada
1. Hacer commit/push desde laptop con GP after-AL4, matriz AL5, prompt WS AL5 y APOS.
2. En WS: `git pull origin master`.
3. En WS: dry-run AL5 con `config/al_batch5_after_al4_20260520.csv`.
4. Si dry-run lista exactamente 8 casos, ejecutar AL5.

## Contexto minimo para continuar
- AL4 after-AL3 termino limpio: `8/8` OK, `0` fallos numericos, `35.5 h`.
- AL4 no fue convergencia: fue lote productivo dirigido para cerrar brackets after-AL3.
- Metodologia fija: `dp=0.003`, `classification_mode=displacement_only`, `reference_time_s=0.5`, rotacion diagnostica.
- Resultado AL4: 5 ESTABLE y 3 FALLO.
- Fallos AL4:
  - `al4_base_m085_mu0790`: `Dmax=6.18% d_eq`.
  - `al4_highH_m115_mu0750`: `Dmax=5.45% d_eq`.
  - `al4_highH_m125_mu0680`: `Dmax=6.20% d_eq`.
- Estables cercanos:
  - `al4_highH_m100_mu0865`: `Dmax=4.86% d_eq`.
  - `al4_base_m100_mu06808`: `Dmax=3.57% d_eq`.
- Export liviano WS: `exports/al_batch4_after_al3_20260520/`.
- La laptop ya reentreno GP after-AL4.
- GP after-AL4: 64 casos usados, LOO accuracy `0.875`, MAE `2.557% d_eq`, RMSE `4.226% d_eq`.
- AL5 recomendado: 8 casos para cerrar brackets y llenar cortes H-m* faltantes.
- La WS no debe usar `--retrain-gp`.

## Archivos a leer primero
- `.apos/STATUS.md`
- `.apos/PLAN.md`
- `exports/al_batch4_after_al3_20260520/al_batch4_summary.md`
- `exports/al_batch4_after_al3_20260520/al_batch4_summary.csv`
- `config/al_batch4_after_al3_20260518.csv`
- `data/results.sqlite`
- `data/analysis/gp_h_mu_mstar_after_al4_20260520/README.md`
- `data/analysis/gp_h_mu_mstar_after_al4_20260520/al5_candidates.csv`
- `config/al_batch5_after_al4_20260520.csv`
- `docs/PROMPT_WS_AL5_AFTER_AL4_20260520.md`

## Comandos sugeridos para laptop
```powershell
git status --short
git add .apos config/al_batch5_after_al4_20260520.csv docs/PROMPT_WS_AL5_AFTER_AL4_20260520.md scripts/train_gp_h_mu_mstar_after_al4_20260520.py data/analysis/gp_h_mu_mstar_after_al4_20260520 models/surrogates/gp_h_mu_mstar_after_al4_20260520.pkl
git commit -m "Add after-AL4 GP analysis and AL5 plan"
git push origin master
```

## Senales de exito
- Git remoto contiene `config/al_batch5_after_al4_20260520.csv`.
- WS puede hacer dry-run AL5 con exactamente 8 casos.
- AL5 se ejecuta sin `--retrain-gp`.

## No hacer todavia
- No cambiar la matriz AL5 en WS sin volver a justificarla en laptop.
- No abrir pendiente/orientacion/forma antes de cerrar el analisis AL4.
- No tratar el GP como resultado SPH directo.
- No versionar crudos pesados.
- No usar `--retrain-gp` en WS.

## Riesgos inmediatos
- AL4 incluye puntos muy cercanos al umbral; pequenas diferencias de resolucion/contacto pueden cambiar clase.
- Rotacion supera 5 grados en varios casos, pero no decide la clase bajo `displacement_only`.
- `al5_highH_m085_mu0900` puede fallar aun con `mu=0.90`; si ocurre, se reporta que para `H=0.225,m*=0.85` la frontera queda fuera del dominio de `mu<=0.90`.
