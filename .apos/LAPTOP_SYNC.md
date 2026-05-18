# LAPTOP_SYNC

Ultima actualizacion WS: 2026-05-18T15:17:51
Proyecto: SPH-Tesis
Ruta WS: `C:\Users\kevin\projects\Tesis`

Este archivo es el resumen inteligente que `/guardar` debe versionar para que la laptop reciba contexto por `git pull`.

## Git
- Rama: `master`
- HEAD: `0d40eec Add AL3 after-AL2 lightweight export`

```text
## master...origin/master
 M .apos/HANDOFF.md
 M .apos/INDEX.md
 M .apos/JOURNAL.md
 M .apos/PLAN.md
 M .apos/STATUS.md
 M data/figures/production_story_graphics/01_response_map_h_mu_by_mass.png
 M data/figures/production_story_graphics/01_response_map_h_mu_by_mass.svg
 M data/figures/production_story_graphics/02_margin_vs_mu_by_mass_and_h.png
 M data/figures/production_story_graphics/02_margin_vs_mu_by_mass_and_h.svg
 M data/figures/production_story_graphics/03_batch_story_margin_strip.png
 M data/figures/production_story_graphics/03_batch_story_margin_strip.svg
 M data/figures/production_story_graphics/04_local_hydraulics_vs_displacement.png
 M data/figures/production_story_graphics/04_local_hydraulics_vs_displacement.svg
 M data/figures/production_story_graphics/05_forces_vs_displacement.png
 M data/figures/production_story_graphics/05_forces_vs_displacement.svg
 M data/figures/production_story_graphics/06_rotation_diagnostic_vs_displacement.png
 M data/figures/production_story_graphics/06_rotation_diagnostic_vs_displacement.svg
 M data/figures/production_story_graphics/07_computational_cost_by_batch.png
 M data/figures/production_story_graphics/07_computational_cost_by_batch.svg
 M data/figures/production_story_graphics/08_mass_effect_displacement_summary.png
 M data/figures/production_story_graphics/08_mass_effect_displacement_summary.svg
 M data/figures/production_story_graphics/FIGURE_INDEX.md
 M data/figures/production_story_graphics/figure_index.csv
 M data/figures/production_story_graphics/master_production_story.csv
 M docs/post_convergence_story_web/data/FIGURE_INDEX.md
 D docs/post_convergence_story_web/data/al3_candidates.csv
 D docs/post_convergence_story_web/data/al3_matrix_recommended.csv
 M docs/post_convergence_story_web/data/brackets_by_h_mstar.csv
 M docs/post_convergence_story_web/data/dataset_used.csv
 M docs/post_convergence_story_web/data/figure_index.csv
 M docs/post_convergence_story_web/data/master_production_story.csv
 M docs/post_convergence_story_web/data/validation_metrics.json
 M docs/post_convergence_story_web/figures/01_loo_validation.png
 M docs/post_convergence_story_web/figures/01_loo_validation.svg
 M docs/post_convergence_story_web/figures/01_response_map_h_mu_by_mass.png
 M docs/post_convergence_story_web/figures/01_response_map_h_mu_by_mass.svg
 M docs/post_convergence_story_web/figures/02_gp_frontier_by_mass.png
 M docs/post_convergence_story_web/figures/02_gp_frontier_by_mass.svg
 M docs/post_convergence_story_web/figures/02_margin_vs_mu_by_mass_and_h.png
 M docs/post_convergence_story_web/figures/02_margin_vs_mu_by_mass_and_h.svg
 M docs/post_convergence_story_web/figures/03_batch_story_margin_strip.png
 M docs/post_convergence_story_web/figures/03_batch_story_margin_strip.svg
 M docs/post_convergence_story_web/figures/03_gp_uncertainty_by_mass.png
 M docs/post_convergence_story_web/figures/03_gp_uncertainty_by_mass.svg
 M docs/post_convergence_story_web/figures/04_local_hydraulics_vs_displacement.png
 M docs/post_convergence_story_web/figures/04_local_hydraulics_vs_displacement.svg
 M docs/post_convergence_story_web/figures/08_mass_effect_displacement_summary.png
 M docs/post_convergence_story_web/figures/08_mass_effect_displacement_summary.svg
 M docs/post_convergence_story_web/index.html
 M scripts/build_post_convergence_story_web.py
 M scripts/generate_production_story_graphics.py
?? config/al_batch4_after_al3_20260518.csv
?? data/analysis/gp_h_mu_mstar_after_al3_20260518/
?? docs/PROMPT_WS_AL4_AFTER_AL3_20260518.md
?? docs/post_convergence_story_web/data/al4_candidates.csv
?? docs/post_convergence_story_web/data/al4_matrix_recommended.csv
?? models/surrogates/gp_h_mu_mstar_after_al3_20260518.pkl
?? scripts/train_gp_h_mu_mstar_after_al3_20260518.py
```

## Estado productivo / simulaciones
_No hay `data/production_status.json` disponible._

## Estado APOS resumido

### STATUS
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

### HANDOFF
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

### PLAN
# PLAN

## Objetivo activo
Cerrar de forma robusta la frontera base `[H, mu, m*]` con active learning trazable, antes de abrir pendiente, orientacion y forma como extensiones jerarquicas.

## Fase actual
Post-AL3 con surrogate deliberate after-AL3 entrenado en laptop y AL4 listo para WS.

## Proximos hitos
- [x] Cerrar convergencia y adoptar `dp=0.003` como resolucion operativa.
- [x] Ejecutar piloto, batch2, batch3, batch4, AL1 y AL2.
- [x] Bloquear reentrenamiento GP automatico al terminar produccion.
- [x] Entrenar GP after-AL2 de forma deliberada.
- [x] Generar y correr AL3 en WS.
- [x] Traer AL3 a laptop.
- [x] Entrenar GP after-AL3 de forma deliberada.
- [x] Actualizar web post-convergencia con AL3 y GP after-AL3.
- [x] Generar matriz AL4.
- [x] Preparar prompt WS AL4.
- [ ] Subir cambios AL4 a Git.
- [ ] En WS: dry-run AL4.
- [ ] En WS: ejecutar AL4 si el dry-run coincide.
- [ ] Exportar AL4 liviano y traerlo a laptop.
- [ ] Reentrenar GP after-AL4 en laptop.
- [ ] Decidir si sigue AL5, holdout o checks finos `dp=0.002`.
- [ ] Seleccionar variables secundarias: pendiente, orientacion y formas/STL representativas.

## Linea metodologica prevista
1. Cerrar frontera base con `[H, mu, m*]`.
2. Validar la frontera base con holdout/repeticiones marginales.
3. Agregar checks finos `dp=0.002` en pocos puntos criticos.
4. Agregar pendiente como extension controlada.
5. Agregar orientacion como sensibilidad controlada.
6. Agregar forma con pocas geometrias representativas elegidas por analisis STL.
7. Entregar estado limite, fragilidad condicional, incertidumbre y validacion por capas.

## Bloqueos
- No lanzar nuevos casos si la WS no esta sincronizada por Git.
- No usar GP legacy ni reentreno automatico.
- No versionar crudos pesados.
- No usar el caso parcial de batch4 como oficial.

## Fuera de alcance por ahora
- Factorial completo 6D sin active learning.
- Dominio amplio de forma sin seleccion geometrica previa.
- Claims universales de bloques costeros.

### Riesgos activos
Probabilidad: media
Evidencia: la WS produce exports via GitHub y la laptop contiene STL/documentos/figuras/scripts locales no necesariamente sincronizados.
Mitigacion: usar `docs/DATA_ORIGIN_POLICY.md`; citar export/commit para WS y path local para laptop; versionar solo lo liviano y trazable.
Relacionado: `docs/DATA_ORIGIN_POLICY.md`, `exports/`, `models/bloques/`

## RISK-20260510-002 - Recuperar cambios antiguos del stash y reintroducir estado obsoleto

Estado: activo
Severidad: media
Probabilidad: media
Evidencia: los cambios trackeados previos quedaron en `stash@{0}` antes del fast-forward.
Mitigacion: no aplicar el stash completo; inspeccionar y recuperar solo archivos puntuales si falta algo.
Relacionado: `C:\Seba\workspace_backups\tesis-reconcile-20260510_125339`

## RISK-20260510-003 - Perdida de crudos locales por limpieza

Estado: activo
Severidad: alta
Probabilidad: media
Evidencia: existen datos locales grandes en `cases/`, `data/`, `imports/` y `archive/`.
Mitigacion: no borrar ni limpiar esos directorios; mover crudos a disco externo/storage solo con plan explicito.
Relacionado: `.gitignore`, `docs/DATA_ORIGIN_POLICY.md`

## RISK-20260514-001 - AL batch2 productivo en ejecucion

Estado: mitigado
Severidad: alta
Probabilidad: media
Evidencia: AL2 termino 10/10 OK y export liviano en `exports/al_batch2_bracket_closing_20260516/`.
Mitigacion: AL3 se diseno despues de incorporar AL2 y reentrenar GP localmente.
Relacionado: `config/al_batch2_bracket_closing_20260514.csv`, `scripts/run_production.py`, `data/production_20260514_2030.log`

## RISK-20260516-001 - Plan demasiado conservador frente a capacidad computacional real

Estado: activo
Severidad: media
Probabilidad: media
Evidencia: con 6 meses disponibles y WS RTX 5090/i9, cerrar con solo ~30 simulaciones adicionales podria dejar fuera pendiente, orientacion y forma.
Mitigacion: adoptar plan jerarquico: frontera base `[H, mu, m*]`, luego pendiente, orientacion y forma como extensiones controladas, con holdout y checks finos.
Relacionado: `docs/mock_final_deliverable_20260516/index.html`, `data/analysis/gp_h_mu_mstar_20260516/`

## RISK-20260516-002 - Expansion de variables sin jerarquia

Estado: activo
Severidad: alta
Probabilidad: media
Evidencia: abrir simultaneamente `H, mu, m*, pendiente, orientacion, forma` puede volver la frontera dificil de interpretar y requerir muchas mas simulaciones.
Mitigacion: disenar etapas separadas y usar active learning/holdout; no hacer factorial completo 6D sin justificacion.
Relacionado: `.apos/PLAN.md`, `config/al_batch3_gp_after_al2_20260516.csv`

## RISK-20260516-003 - Confundir mock sintetico con resultado real

Estado: activo
Severidad: media
Probabilidad: baja
Evidencia: se creo `docs/mock_final_deliverable_20260516/` con datos sinteticos para visualizar el entregable final.
Mitigacion: mantener rotulos explicitos de datos sinteticos y no citarlo como evidencia cientifica.
Relacionado: `scripts/generate_mock_final_deliverable_20260516.py`

### Preguntas abiertas
# OPEN_QUESTIONS

## Q-20260501-001 - Resultado completo del piloto productivo

Estado: resuelta
Tipo: tecnica
Contexto: el piloto de 5 casos esta corriendo.
Que evidencia falta:
- `production_status.json` final.
- logs finales.
- CSVs procesados por caso.
Resolucion: piloto completado y exportado en `exports/pilot_productivo_20260501/`.

## Q-20260501-002 - Instalacion de skills APOS-X

Estado: resuelta
Tipo: requisito
Contexto: se preparo memoria APOS-X local, pero no se instalaron skills repo-locales ni globales.
Que evidencia falta:
- decision del usuario sobre instalar `.agents/skills`.
- resultado de evals locales.
Resolucion: el runtime APOS de tesis quedo simplificado a tres skills repo-locales: `/apos`, `/guardar`, `/apos-status`.

## Q-20260501-003 - Alcance de `apos-system/`

Estado: resuelta
Tipo: tecnica
Contexto: la especificacion APOS-X define una fuente versionada `apos-system/`.
Que evidencia falta:
- decidir si vive en este repo, en repo separado, o como paquete personal.
Resolucion: para tesis, `apos-system/` no es runtime vivo; APOS canonico es `.apos/` mas tres skills repo-locales.

## Q-20260516-001 - Cuanto expandir pendiente, orientacion y forma

Estado: abierta
Tipo: tecnica
Contexto: se decidio que el plan no debe cerrar con el minimo de simulaciones si hay 6 meses y WS potente. Pendiente, orientacion y forma importan, pero deben entrar de forma jerarquica.
Que evidencia falta:
- resultados de AL3;
- reentrenamiento GP after-AL3;
- analisis geometrico/STL para seleccionar formas representativas;
- presupuesto actualizado de tiempo por simulacion.
Resolucion: pendiente.

## Exports livianos recientes
- `exports\al_batch3_gp_after_al2_20260518` (2026-05-18T15:02)
- `exports\stitch_visual_package_20260515` (2026-05-16T17:36)
- `exports\batch4_mass_probe_20260513` (2026-05-16T17:36)
- `exports\al_batch2_bracket_closing_20260516` (2026-05-16T17:36)
- `exports\al_batch1_hybrid_20260514` (2026-05-16T17:36)
- `exports\ws_delta_conv_edge_f0685_20260422_090418` (2026-05-10T12:54)
- `exports\ws_delta_conv_edge_f0685_20260422_081859` (2026-05-10T12:54)
- `exports\thesis_analysis_prelim_20260421_144616` (2026-05-10T12:54)

## Cambios locales al momento de guardar
**Cambios livianos o de codigo:**
- `M .apos/HANDOFF.md`
- ` M .apos/INDEX.md`
- ` M .apos/JOURNAL.md`
- ` M .apos/PLAN.md`
- ` M .apos/STATUS.md`
- ` M data/figures/production_story_graphics/01_response_map_h_mu_by_mass.png`
- ` M data/figures/production_story_graphics/01_response_map_h_mu_by_mass.svg`
- ` M data/figures/production_story_graphics/02_margin_vs_mu_by_mass_and_h.png`
- ` M data/figures/production_story_graphics/02_margin_vs_mu_by_mass_and_h.svg`
- ` M data/figures/production_story_graphics/03_batch_story_margin_strip.png`
- ` M data/figures/production_story_graphics/03_batch_story_margin_strip.svg`
- ` M data/figures/production_story_graphics/04_local_hydraulics_vs_displacement.png`
- ` M data/figures/production_story_graphics/04_local_hydraulics_vs_displacement.svg`
- ` M data/figures/production_story_graphics/05_forces_vs_displacement.png`
- ` M data/figures/production_story_graphics/05_forces_vs_displacement.svg`
- ` M data/figures/production_story_graphics/06_rotation_diagnostic_vs_displacement.png`
- ` M data/figures/production_story_graphics/06_rotation_diagnostic_vs_displacement.svg`
- ` M data/figures/production_story_graphics/07_computational_cost_by_batch.png`
- ` M data/figures/production_story_graphics/07_computational_cost_by_batch.svg`
- ` M data/figures/production_story_graphics/08_mass_effect_displacement_summary.png`
- ` M data/figures/production_story_graphics/08_mass_effect_displacement_summary.svg`
- ` M data/figures/production_story_graphics/FIGURE_INDEX.md`
- ` M data/figures/production_story_graphics/figure_index.csv`
- ` M data/figures/production_story_graphics/master_production_story.csv`
- ` M docs/post_convergence_story_web/data/FIGURE_INDEX.md`
- ` D docs/post_convergence_story_web/data/al3_candidates.csv`
- ` D docs/post_convergence_story_web/data/al3_matrix_recommended.csv`
- ` M docs/post_convergence_story_web/data/brackets_by_h_mstar.csv`
- ` M docs/post_convergence_story_web/data/dataset_used.csv`
- ` M docs/post_convergence_story_web/data/figure_index.csv`
- ` M docs/post_convergence_story_web/data/master_production_story.csv`
- ` M docs/post_convergence_story_web/data/validation_metrics.json`
- ` M docs/post_convergence_story_web/figures/01_loo_validation.png`
- ` M docs/post_convergence_story_web/figures/01_loo_validation.svg`
- ` M docs/post_convergence_story_web/figures/01_response_map_h_mu_by_mass.png`
- ` M docs/post_convergence_story_web/figures/01_response_map_h_mu_by_mass.svg`
- ` M docs/post_convergence_story_web/figures/02_gp_frontier_by_mass.png`
- ` M docs/post_convergence_story_web/figures/02_gp_frontier_by_mass.svg`
- ` M docs/post_convergence_story_web/figures/02_margin_vs_mu_by_mass_and_h.png`
- ` M docs/post_convergence_story_web/figures/02_margin_vs_mu_by_mass_and_h.svg`
- ` M docs/post_convergence_story_web/figures/03_batch_story_margin_strip.png`
- ` M docs/post_convergence_story_web/figures/03_batch_story_margin_strip.svg`
- ` M docs/post_convergence_story_web/figures/03_gp_uncertainty_by_mass.png`
- ` M docs/post_convergence_story_web/figures/03_gp_uncertainty_by_mass.svg`
- ` M docs/post_convergence_story_web/figures/04_local_hydraulics_vs_displacement.png`
- ` M docs/post_convergence_story_web/figures/04_local_hydraulics_vs_displacement.svg`
- ` M docs/post_convergence_story_web/figures/08_mass_effect_displacement_summary.png`
- ` M docs/post_convergence_story_web/figures/08_mass_effect_displacement_summary.svg`
- ` M docs/post_convergence_story_web/index.html`
- ` M scripts/build_post_convergence_story_web.py`
- ` M scripts/generate_production_story_graphics.py`
- `?? config/al_batch4_after_al3_20260518.csv`
- `?? data/analysis/gp_h_mu_mstar_after_al3_20260518/`
- `?? docs/PROMPT_WS_AL4_AFTER_AL3_20260518.md`
- `?? docs/post_convergence_story_web/data/al4_candidates.csv`
- `?? docs/post_convergence_story_web/data/al4_matrix_recommended.csv`
- `?? models/surrogates/gp_h_mu_mstar_after_al3_20260518.pkl`
- `?? scripts/train_gp_h_mu_mstar_after_al3_20260518.py`

## Instrucciones para laptop
1. Ejecutar `git pull`.
2. Leer primero `.apos/LAPTOP_SYNC.md`.
3. Luego leer `.apos/HANDOFF.md` y `.apos/STATUS.md`.
4. No asumir que outputs runtime ignorados por Git estan disponibles localmente.
5. Si hay simulacion activa en WS, tratar `data/results.sqlite` como vivo hasta que exista export liviano cerrado.
