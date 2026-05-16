# HANDOFF

## Proxima accion recomendada
1. Enviar a la WS el prompt `docs/PROMPT_WS_AL3_AFTER_AL2_20260516.md`.
2. En WS: hacer `git pull origin master`, dry-run AL3 y correr los 8 casos solo si el dry-run coincide.
3. Paralelamente, preparar el plan jerarquico expandido para los proximos 6 meses: base `[H, mu, m*]`, luego pendiente, orientacion, forma, holdout y checks finos.

## Contexto minimo para continuar
- AL2 ya fue traido a laptop.
- El GP after-AL2 fue entrenado localmente, no en WS.
- AL3 tiene 8 casos propuestos por frontera/incertidumbre del GP.
- `m*` es masa relativa respecto del caso base: 0.85, 1.00, 1.15, 1.25.
- La WS no debe usar `--retrain-gp`; solo simula y exporta resultados livianos.
- El plan ya no debe pensarse como "30 simulaciones y cerrar"; con 6 meses y WS potente conviene una campana jerarquica mas ambiciosa.
- Pendiente, orientacion y forma importan; se incorporaran como etapas secundarias/controladas, no todas mezcladas desde el inicio.
- El mock en `docs/mock_final_deliverable_20260516/` es solo sintetico para visualizar el entregable final.

## Archivos a leer primero
- `.apos/STATUS.md`
- `.apos/PLAN.md`
- `docs/PROMPT_WS_AL3_AFTER_AL2_20260516.md`
- `config/al_batch3_gp_after_al2_20260516.csv`
- `data/analysis/gp_h_mu_mstar_20260516/README.md`
- `docs/mock_final_deliverable_20260516/index.html`
- `docs/post_convergence_story_web/index.html`

## Comandos sugeridos
```powershell
git pull origin master
python scripts\run_production.py --prod --matrix config\al_batch3_gp_after_al2_20260516.csv --max-cases 8 --dry-run --no-notify
python scripts\run_production.py --prod --matrix config\al_batch3_gp_after_al2_20260516.csv --max-cases 8 --no-notify
```

## Senales de exito
- Dry-run AL3 lista exactamente 8 casos.
- `dp=0.003`, `classification_mode=displacement_only`, `reference_time_s=0.5`.
- No aparece `--retrain-gp`.
- AL3 queda corriendo o termina con export liviano `exports/al_batch3_gp_after_al2_YYYYMMDD/`.
- El siguiente plan separa claramente frontera base, extension de pendiente, extension de orientacion, extension de forma y validacion.

## No hacer todavia
- No lanzar AL4 sin incorporar AL3.
- No reentrenar GP en la WS.
- No abrir forma/orientacion/pendiente como un factorial completo sin diseno jerarquico.
- No tratar el mock sintetico como resultado real.
- No usar el caso parcial de batch4 como oficial.

## Riesgos inmediatos
- La WS podria tener cambios locales; no limpiar ni resetear sin revisar.
- `mu=0.900` extiende levemente el rango previo, pero es intencional para cerrar bracket en `H=0.210, m*=0.85`.
- Si se expanden variables sin jerarquia, el resultado puede volverse dificil de defender aunque haya mucho computo.
