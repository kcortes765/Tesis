# STATUS

Ultima actualizacion: 2026-05-18 15:15
Proyecto: SPH-IncipientMotion / Tesis UCN 2026
Ruta canonica WS: C:\Users\Admin\Desktop\SPH-Tesis
Estado actual: AL3 fue traido desde Git, analizado en laptop, se reentreno el GP after-AL3 y quedo preparado AL4 para la WS.

## Hechos verificados
- Convergencia cerrada para uso productivo: `dp=0.003`, `classification_mode=displacement_only`, `reference_time_s=0.5`.
- Piloto, batch2, batch3, batch4, AL1, AL2 y AL3 tienen exports livianos versionables.
- AL3 termino 8/8 OK, 0 fallos numericos, 8 ESTABLE y 0 FALLO.
- AL3 corrio entre 2026-05-16 18:10 y 2026-05-18 05:53; tiempo total 35.73 h, promedio 4.41 h/caso.
- Caso AL3 mas cercano al umbral: `al3_base_m085_mu0800`, ESTABLE con `Dmax=4.85% d_eq`.
- Otros casos cercanos: `al3_highH_m115_mu0760` con `4.29% d_eq`, `al3_midH_m100_mu0755` con `3.58% d_eq`.
- Se entreno localmente un GP after-AL3 con 56 casos oficiales del dominio principal `[H, mu, m*]`.
- Modelo deliberate GP after-AL3: `models/surrogates/gp_h_mu_mstar_after_al3_20260518.pkl`.
- Validacion LOO GP after-AL3: accuracy 0.857, MAE 2.866% d_eq, RMSE 4.485% d_eq.
- Matriz AL4 preparada: `config/al_batch4_after_al3_20260518.csv`, 8 casos.
- Prompt WS AL4 preparado: `docs/PROMPT_WS_AL4_AFTER_AL3_20260518.md`.
- Web post-convergencia actualizada con AL3 y GP after-AL3: `docs/post_convergence_story_web/index.html`.

## Decisiones activas
- La WS solo ejecuta simulaciones y exporta resultados livianos; el reentrenamiento GP se hace deliberadamente en laptop.
- AL4 debe cerrar brackets observados, no expandir dominio.
- AL4 mantiene `dp=0.003`, pendiente `1:20`, orientacion `rot_z=0`, geometria base y criterio `displacement_only`.
- No usar `--retrain-gp` en WS.
- Tratar rotacion, fuerzas y gauges como diagnosticos, no como criterio primario.
- Mantener el caso parcial `batch4_mass_m125_H0225_mu0860` fuera de evidencia oficial salvo reproceso/repeticion.

## Inferencias vigentes
- AL3 mostro que varios puntos propuestos eran del lado estable; esto es util porque cierra el lado seguro de los brackets.
- El siguiente paso mas eficiente es bajar levemente `mu` dentro de brackets ya observados para ubicar el cambio de clase.
- La frontera base `[H, mu, m*]` aun necesita AL4 y probablemente un holdout/repeticiones antes de declararse cerrada.
- La expansion a pendiente, orientacion y forma sigue prevista como etapa jerarquica posterior, no mezclada con AL4.

## Pendientes criticos
- Subir a Git el GP after-AL3, web actualizada, matriz AL4 y prompt WS AL4.
- En WS: `git pull origin master`, dry-run AL4 y ejecutar solo si lista 8 casos correctos.
- Al volver AL4, reentrenar GP en laptop y decidir si corresponde holdout, AL5 o checks finos `dp=0.002`.
- Preparar plan jerarquico cuantitativo para pendiente, orientacion y forma.
- Analizar geometricamente los STL disponibles antes de elegir formas secundarias.

## Riesgos activos
- Riesgo de usar accidentalmente un GP legacy; usar solo modelos versionados `after_al2`/`after_al3`.
- Riesgo de confundir interpolacion GP con resultado SPH directo.
- Riesgo de abrir pendiente/orientacion/forma antes de cerrar bien la frontera base.
- Riesgo de que el GP siga con incertidumbre alta en zonas poco muestreadas; por eso AL4 prioriza brackets observados.

## Evidencia reciente
- `exports/al_batch3_gp_after_al2_20260518/al_batch3_summary.md`
- `data/analysis/gp_h_mu_mstar_after_al3_20260518/README.md`
- `data/analysis/gp_h_mu_mstar_after_al3_20260518/validation_metrics.json`
- `models/surrogates/gp_h_mu_mstar_after_al3_20260518.pkl`
- `config/al_batch4_after_al3_20260518.csv`
- `docs/PROMPT_WS_AL4_AFTER_AL3_20260518.md`
- `docs/post_convergence_story_web/index.html`
