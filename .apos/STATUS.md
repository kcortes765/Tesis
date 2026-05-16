# STATUS

Ultima actualizacion: 2026-05-16 18:23
Proyecto: SPH-IncipientMotion / Tesis UCN 2026
Ruta canonica WS: C:\Users\Admin\Desktop\SPH-Tesis
Estado actual: AL3 quedo preparado y subido; se definio orientar la tesis hacia un plan jerarquico mas ambicioso, no solo cerrar con el minimo de simulaciones.

## Hechos verificados
- Convergencia cerrada para uso productivo: `dp=0.003`, `classification_mode=displacement_only`, `reference_time_s=0.5`.
- Piloto, batch2, batch3, batch4, AL1 y AL2 tienen exports livianos versionables.
- AL2 termino 10/10 OK, con 5 ESTABLE y 5 FALLO.
- Se entreno localmente un GP after-AL2 con 48 casos oficiales del dominio principal `[H, mu, m*]`.
- Modelo deliberado GP: `models/surrogates/gp_h_mu_mstar_after_al2_20260516.pkl`.
- Validacion LOO del GP after-AL2: accuracy 0.875, MAE 3.140% d_eq, RMSE 4.736% d_eq.
- Matriz AL3 preparada: `config/al_batch3_gp_after_al2_20260516.csv`, 8 casos.
- Prompt WS AL3 preparado: `docs/PROMPT_WS_AL3_AFTER_AL2_20260516.md`.
- Web post-convergencia actualizada con AL2 y GP after-AL2: `docs/post_convergence_story_web/index.html`.
- Commit `6f9eb41` subido a `origin/master` con GP after-AL2, web y plan AL3.
- Mock de entregable final sintetico creado en `docs/mock_final_deliverable_20260516/index.html`.

## Decisiones activas
- Adoptar `dp=0.003` como resolucion operativa de produccion, sin vender convergencia asintotica fuerte.
- Usar `classification_mode=displacement_only` como criterio primario.
- Usar `reference_time_s=0.5`.
- Tratar rotacion, fuerza SPH/contacto y gauges como diagnosticos, no como criterio primario.
- La WS solo ejecuta simulaciones; el reentrenamiento GP se hace deliberadamente en laptop.
- AL3 se corre con matriz explicita, `--max-cases 8`, `--prod`, dry-run previo y sin `--retrain-gp`.
- Plan cientifico actualizado: frontera base `[H, mu, m*]` primero; luego expansion jerarquica a pendiente, orientacion y forma como sensibilidades/modelos secundarios, no como factorial caotico.

## Inferencias vigentes
- Con 6 meses disponibles y RTX 5090, el plan puede ser mas ambicioso que 30 simulaciones restantes.
- Un rango razonable para tesis fuerte/paper candidate es del orden de 130-220 simulaciones adicionales si se incorporan pendiente, orientacion, forma, holdout y checks finos.
- La forma final del entregable probablemente combinara: ecuacion de estado limite `g(H,mu,m*)`, frontera/contornos, fragilidad condicional, validacion por capas y limites explicitos.
- El mock sintetico ayuda a visualizar el resultado final, pero no es evidencia cientifica.

## Pendientes criticos
- En WS: `git pull origin master`, dry-run AL3 y ejecutar solo si lista 8 casos correctos.
- Al volver AL3, reentrenar GP nuevamente en laptop y decidir AL4/holdout.
- Disenar plan jerarquico expandido con presupuesto real de simulaciones para pendiente, orientacion y forma.
- Analizar geometricamente formas/STL disponibles antes de decidir cuantas entran.
- Mantener el caso parcial `batch4_mass_m125_H0225_mu0860` fuera de evidencia oficial salvo reproceso/repeticion.

## Riesgos activos
- Riesgo de usar accidentalmente un GP legacy; usar solo el modelo versionado after-AL2.
- Riesgo de confundir interpolacion GP con resultado SPH directo.
- Riesgo de abrir demasiadas variables sin jerarquia y perder interpretabilidad.
- Riesgo de quedarse corto por exceso de conservadurismo computacional, dada la disponibilidad real de WS.
- Riesgo de tratar el mock sintetico como resultado real.

## Evidencia reciente
- `config/al_batch3_gp_after_al2_20260516.csv`
- `docs/PROMPT_WS_AL3_AFTER_AL2_20260516.md`
- `docs/post_convergence_story_web/index.html`
- `data/analysis/gp_h_mu_mstar_20260516/validation_metrics.json`
- `models/surrogates/gp_h_mu_mstar_after_al2_20260516.pkl`
- `docs/mock_final_deliverable_20260516/index.html`
- `scripts/generate_mock_final_deliverable_20260516.py`
- Commit `6f9eb41 Add after-AL2 GP analysis and AL3 plan`
