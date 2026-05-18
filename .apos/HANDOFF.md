# HANDOFF

## Proxima accion recomendada
1. Subir a Git los cambios locales de AL3/GP/web/AL4.
2. Enviar a la WS el prompt `docs/PROMPT_WS_AL4_AFTER_AL3_20260518.md`.
3. En WS: hacer `git pull origin master`, dry-run AL4 y correr los 8 casos solo si el dry-run coincide.

## Contexto minimo para continuar
- AL3 ya volvio desde la WS: 8/8 OK, todos ESTABLE.
- AL3 no invalida el proceso; cierra el lado estable de varios brackets.
- GP after-AL3 fue entrenado localmente con 56 casos oficiales.
- Metricas GP after-AL3: LOO accuracy 0.857, MAE 2.866% d_eq, RMSE 4.485% d_eq.
- AL4 no expande dominio; baja `mu` dentro de brackets observados para ubicar mejor el cambio estable/fallo.
- `m*` es masa relativa respecto del caso base: 0.85, 1.00, 1.15, 1.25.
- La WS no debe usar `--retrain-gp`; solo simula y exporta resultados livianos.

## Archivos a leer primero
- `.apos/STATUS.md`
- `.apos/PLAN.md`
- `docs/PROMPT_WS_AL4_AFTER_AL3_20260518.md`
- `config/al_batch4_after_al3_20260518.csv`
- `data/analysis/gp_h_mu_mstar_after_al3_20260518/README.md`
- `docs/post_convergence_story_web/index.html`

## Comandos sugeridos para WS
```powershell
git pull origin master
python scripts\run_production.py --prod --matrix config\al_batch4_after_al3_20260518.csv --max-cases 8 --dry-run --no-notify
python scripts\run_production.py --prod --matrix config\al_batch4_after_al3_20260518.csv --max-cases 8 --no-notify
```

## Senales de exito
- Dry-run AL4 lista exactamente 8 casos.
- `dp=0.003`, `classification_mode=displacement_only`, `reference_time_s=0.5`.
- No aparece `--retrain-gp`.
- AL4 queda corriendo o termina con export liviano `exports/al_batch4_after_al3_YYYYMMDD/`.
- Al menos varios casos AL4 caen cerca de `Dmax=5% d_eq`, con mezcla de ESTABLE/FALLO.

## No hacer todavia
- No lanzar AL5 sin incorporar AL4.
- No reentrenar GP en la WS.
- No abrir forma/orientacion/pendiente antes de cerrar el analisis AL4.
- No tratar el GP como resultado SPH directo.
- No versionar crudos pesados.

## Riesgos inmediatos
- La WS podria tener cambios locales; no limpiar ni resetear sin revisar.
- AL4 incluye un chequeo muy fino `mu=0.6808` en la transicion base; si sale distinto a lo esperado, tratarlo como sensibilidad/noise local, no como crisis metodologica.
- Si AL4 sale casi todo estable o casi todo fallo, ajustar AL5 con brackets actualizados antes de pasar a holdout.
