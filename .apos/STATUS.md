# STATUS

Ultima actualizacion: 2026-05-20 19:10
Proyecto: SPH-IncipientMotion / Tesis UCN 2026
Ruta canonica WS: C:\Users\Admin\Desktop\SPH-Tesis
Estado actual: AL4 after-AL3 fue incorporado en laptop, el GP after-AL4 fue reentrenado localmente y AL5 quedo preparado para ejecutar en WS.

## Hechos verificados
- Convergencia cerrada para uso productivo: `dp=0.003`, `classification_mode=displacement_only`, `reference_time_s=0.5`.
- Piloto, batch2, batch3, batch4, AL1, AL2, AL3 y AL4 tienen exports livianos versionables.
- AL4 corrio entre 2026-05-18 15:42 y 2026-05-20 03:12.
- AL4 termino `8/8` casos, `0` fallos numericos, tiempo total `35.5 h`.
- AL4 fue produccion dirigida por GP after-AL3 y brackets observados; no fue convergencia ni campana grande.
- AL4 uso `dp=0.003`, pendiente `1:20`, `rot_z=0`, `classification_mode=displacement_only`, `reference_time_s=0.5`.
- AL4 produjo 5 ESTABLE y 3 FALLO por desplazamiento:
  - FALLO: `al4_base_m085_mu0790`, `al4_highH_m115_mu0750`, `al4_highH_m125_mu0680`.
  - ESTABLE: `al4_lowH_m085_mu0566`, `al4_midH_m085_mu0890`, `al4_midH_m100_mu0748`, `al4_highH_m100_mu0865`, `al4_base_m100_mu06808`.
- Casos mas cercanos al umbral:
  - `al4_highH_m100_mu0865`: ESTABLE, `Dmax=4.86% d_eq`.
  - `al4_highH_m115_mu0750`: FALLO, `Dmax=5.45% d_eq`.
  - `al4_base_m085_mu0790`: FALLO, `Dmax=6.18% d_eq`.
- Export liviano creado: `exports/al_batch4_after_al3_20260520/`.
- El export AL4 incluye resumen CSV/MD, snapshot de status, tail de log, matriz corrida, inventario procesado y `Run.csv`/`RunPARTs.csv`.
- No se incluyeron Chrono/Gauges completos, `.bi4`, `.ibi4`, VTK, `Part*`, `cases/` ni carpetas `_out`.
- Laptop ya contiene commit `873fc18 Add AL4 after-AL3 lightweight export`.
- GP after-AL4 entrenado localmente:
  - Script: `scripts/train_gp_h_mu_mstar_after_al4_20260520.py`.
  - Analisis: `data/analysis/gp_h_mu_mstar_after_al4_20260520/`.
  - Modelo: `models/surrogates/gp_h_mu_mstar_after_al4_20260520.pkl`.
  - Casos usados: 64 oficiales dentro del dominio `[H, mu, m*]`.
  - LOO accuracy: `0.875`; MAE: `2.557% d_eq`; RMSE: `4.226% d_eq`.
- AL5 preparado:
  - Matriz: `config/al_batch5_after_al4_20260520.csv`.
  - Prompt WS: `docs/PROMPT_WS_AL5_AFTER_AL4_20260520.md`.
- AL5 fue lanzado en WS el 2026-05-20 18:29 con `--no-notify`; se activo watcher externo ntfy a las 18:43.
- Watcher externo AL5: `scripts/watch_production_ntfy.py`, log `data/logs/production_ntfy_watch_al5_20260520.log`.
- Se agrego atajo versionado: `scripts/start_production_ntfy_watch.ps1`.

## Decisiones activas
- La WS solo ejecuta simulaciones y exporta resultados livianos; el reentrenamiento GP se hace deliberadamente en laptop.
- AL5 debe correrse en WS con matriz explicita y sin `--retrain-gp`.
- Tratar rotacion, fuerzas y gauges como diagnosticos, no como criterio primario.
- Mantener el caso parcial `batch4_mass_m125_H0225_mu0860` fuera de evidencia oficial salvo reproceso/repeticion.
- No usar `--retrain-gp` en WS.
- Para lotes largos en WS, ntfy queda operacionalmente obligatorio: usar notificacion nativa o watcher externo si el comando usa `--no-notify`.

## Inferencias vigentes
- AL4 fue informativo porque mezclo ESTABLE/FALLO dentro de brackets observados.
- El GP after-AL4 mejoro respecto a after-AL3 y dejo brackets muy estrechos en varios cortes:
  - `H=0.200,m*=1.00`: `mu=0.6806` FALLO / `0.6808` ESTABLE.
  - `H=0.225,m*=1.00`: `mu=0.8600` FALLO / `0.8650` ESTABLE.
  - `H=0.225,m*=1.15`: `mu=0.7500` FALLO / `0.7600` ESTABLE.
- Aun faltan puntos para cerrar/llenar cortes:
  - `H=0.225,m*=0.85`: no hay ESTABLE dentro de los corridos.
  - `H=0.210,m*=1.15` y `H=0.210,m*=1.25`: faltan fallos o transiciones claras.

## Pendientes criticos
- Commit/push de analisis after-AL4, matriz AL5, prompt WS AL5 y APOS.
- En WS: hacer `git pull`, dry-run AL5 y ejecutar solo si lista exactamente 8 casos.
- Al terminar AL5, crear export liviano, subir a Git y avisar explicitamente a laptop: "SI ACTIVE SIEMPRE NTFY".
- Cuando vuelva AL5: reentrenar GP after-AL5 y decidir holdout/checks finos `dp=0.002`.
- Actualizar web post-convergencia con AL4 despues del reentrenamiento local.

## Riesgos activos
- Riesgo de reentrenar GP automaticamente en WS; mantenerlo desactivado.
- Riesgo de confundir interpolacion GP con resultado SPH directo.
- Riesgo de abrir pendiente/orientacion/forma antes de cerrar bien la frontera base.
- Riesgo de sobreinterpretar rotacion diagnostica como falla primaria.

## Evidencia reciente
- `data/production_status.json`
- `data/production_20260518_1542.log`
- `data/results.sqlite`
- `exports/al_batch4_after_al3_20260520/al_batch4_summary.md`
- `exports/al_batch4_after_al3_20260520/al_batch4_summary.csv`
- `config/al_batch4_after_al3_20260518.csv`
- `data/analysis/gp_h_mu_mstar_after_al4_20260520/validation_metrics.json`
- `data/analysis/gp_h_mu_mstar_after_al4_20260520/brackets_by_h_mstar.csv`
- `data/analysis/gp_h_mu_mstar_after_al4_20260520/al5_candidates.csv`
- `config/al_batch5_after_al4_20260520.csv`
