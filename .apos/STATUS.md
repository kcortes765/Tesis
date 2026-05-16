# STATUS

Ultima actualizacion: 2026-05-16 17:56
Proyecto: SPH-IncipientMotion / Tesis UCN 2026
Ruta canonica WS: C:\Users\Admin\Desktop\SPH-Tesis
Estado actual: AL2 fue incorporado en laptop; se entreno deliberadamente un GP after-AL2 y quedo preparado AL3 para la WS.

## Hechos verificados
- Convergencia cerrada para uso productivo: `dp=0.003`, `classification_mode=displacement_only`, `reference_time_s=0.5`.
- Piloto, batch2, batch3, batch4, AL1 y AL2 tienen exports livianos versionables.
- AL2 termino 10/10 OK, con 5 ESTABLE y 5 FALLO.
- Se entreno localmente un GP after-AL2 con 48 casos oficiales del dominio principal `[H, mu, m*]`.
- Modelo deliberate GP: `models/surrogates/gp_h_mu_mstar_after_al2_20260516.pkl`.
- Analisis GP: `data/analysis/gp_h_mu_mstar_20260516/`.
- Validacion LOO del GP after-AL2: accuracy 0.875, MAE 3.140% d_eq, RMSE 4.736% d_eq.
- Matriz AL3 preparada: `config/al_batch3_gp_after_al2_20260516.csv`, 8 casos.
- Prompt WS AL3 preparado: `docs/PROMPT_WS_AL3_AFTER_AL2_20260516.md`.
- Web post-convergencia actualizada con AL2 y GP after-AL2: `docs/post_convergence_story_web/index.html`.
- `run_production.py` no debe reentrenar GP salvo con `--retrain-gp` explicito.

## Decisiones activas
- Adoptar `dp=0.003` como resolucion operativa de produccion, sin vender convergencia asintotica fuerte.
- Usar `classification_mode=displacement_only` como criterio primario.
- Usar `reference_time_s=0.5`.
- Tratar rotacion, fuerza SPH/contacto y gauges como diagnosticos, no como criterio primario.
- La WS solo ejecuta simulaciones; el reentrenamiento GP se hace deliberadamente en laptop.
- AL3 se corre con matriz explicita, `--max-cases 8`, `--prod`, dry-run previo y sin `--retrain-gp`.

## Inferencias vigentes
- La base piloto + batch2 + batch3 + batch4 + AL1 + AL2 ya permite proponer AL3 con criterio de frontera/incertidumbre, no por grilla ciega.
- `m*=0.85` sigue siendo la zona mas critica; `m*=1.15` y `m*=1.25` necesitan cierre de brackets en H alto.
- AL3 debe priorizar cerrar transiciones, no expandir campana.

## Pendientes criticos
- Subir a Git el GP after-AL2, la web actualizada y el prompt AL3.
- En WS: `git pull origin master`, dry-run AL3 y ejecutar solo si lista 8 casos correctos.
- Al volver AL3, reentrenar GP nuevamente en laptop y decidir si hace falta AL4 o holdout.
- Mantener el caso parcial `batch4_mass_m125_H0225_mu0860` fuera de evidencia oficial salvo reproceso/repeticion.

## Riesgos activos
- Riesgo de usar accidentalmente un GP legacy; usar solo el modelo versionado after-AL2.
- Riesgo de que `mu=0.900` en AL3 extienda levemente el rango previo; se justifica como cierre de bracket para `H=0.210, m*=0.85`.
- Riesgo de confundir interpolacion GP con resultado SPH directo.
- Riesgo de tratar el caso parcial de batch4 como oficial.

## Evidencia reciente
- `exports/al_batch2_bracket_closing_20260516/al_batch2_summary.csv`
- `scripts/train_gp_h_mu_mstar_20260516.py`
- `data/analysis/gp_h_mu_mstar_20260516/validation_metrics.json`
- `data/analysis/gp_h_mu_mstar_20260516/al3_matrix_recommended.csv`
- `models/surrogates/gp_h_mu_mstar_after_al2_20260516.pkl`
- `config/al_batch3_gp_after_al2_20260516.csv`
- `docs/PROMPT_WS_AL3_AFTER_AL2_20260516.md`
- `docs/post_convergence_story_web/index.html`
