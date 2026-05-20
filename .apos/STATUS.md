# STATUS

Ultima actualizacion: 2026-05-20 03:30
Proyecto: SPH-IncipientMotion / Tesis UCN 2026
Ruta canonica WS: C:\Users\Admin\Desktop\SPH-Tesis
Estado actual: AL4 after-AL3 termino en la WS, fue procesado oficialmente y tiene export liviano listo para laptop.

## Hechos verificados
- Convergencia cerrada para uso productivo: `dp=0.003`, `classification_mode=displacement_only`, `reference_time_s=0.5`.
- Piloto, batch2, batch3, batch4, AL1, AL2, AL3 y AL4 tienen o deben tener exports livianos versionables.
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

## Decisiones activas
- La WS solo ejecuta simulaciones y exporta resultados livianos; el reentrenamiento GP se hace deliberadamente en laptop.
- AL4 debe analizarse en laptop antes de lanzar AL5, holdout o checks finos.
- Tratar rotacion, fuerzas y gauges como diagnosticos, no como criterio primario.
- Mantener el caso parcial `batch4_mass_m125_H0225_mu0860` fuera de evidencia oficial salvo reproceso/repeticion.
- No usar `--retrain-gp` en WS.

## Inferencias vigentes
- AL4 fue informativo porque mezclo ESTABLE/FALLO dentro de brackets observados.
- El GP after-AL4 deberia mejorar la localizacion de fronteras para `m*=0.85`, `m*=1.00`, `m*=1.15` y `m*=1.25`.
- La frontera base `[H, mu, m*]` probablemente esta cerca de estar lista para una fase de holdout o AL5 muy pequeno, pero eso debe decidirse tras reentrenar en laptop.

## Pendientes criticos
- Subir por Git el export AL4, `data/results.sqlite` actualizado y APOS.
- En laptop: `git pull`, leer `exports/al_batch4_after_al3_20260520/al_batch4_summary.md` y reentrenar GP after-AL4.
- Decidir con evidencia si sigue AL5, holdout, o checks finos `dp=0.002`.
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
