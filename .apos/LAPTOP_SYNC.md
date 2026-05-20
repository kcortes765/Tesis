# LAPTOP_SYNC

Ultima actualizacion WS: 2026-05-20T18:51:27
Proyecto: SPH-Tesis
Ruta WS: `C:\Users\kevin\projects\Tesis`

Este archivo es el resumen inteligente que `/guardar` debe versionar para que la laptop reciba contexto por `git pull`.

## Git
- Rama: ``
- HEAD: `6be2ea8 Enable external ntfy watcher for production runs`

```text
## HEAD (no branch)
UU .apos/HANDOFF.md
M  .apos/INDEX.md
UU .apos/JOURNAL.md
UU .apos/LAPTOP_SYNC.md
M  .apos/OPEN_QUESTIONS.md
UU .apos/PLAN.md
M  .apos/RISKS.md
UU .apos/STATUS.md
```

## Estado productivo / simulaciones
_No hay `data/production_status.json` disponible._

## Estado APOS resumido

### STATUS
a para uso productivo: `dp=0.003`, `classification_mode=displacement_only`, `reference_time_s=0.5`.
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
- Decision estrategica nueva: adoptar plan ambicioso, no minimo. Se mantiene cierre jerarquico: primero frontera base `[H, mu, m*]`, luego holdout/checks `dp=0.002`, y despues extensiones de pendiente, orientacion y forma.
- El usuario quiere idealmente usar las 10 formas STL disponibles; esto queda aceptado como objetivo aspiracional, condicionado a analisis geometrico avanzado, sanity de contacto por forma y diseno experimental interpretable.

## Decisiones activas
- La WS solo ejecuta simulaciones y exporta resultados livianos; el reentrenamiento GP se hace deliberadamente en laptop.
- AL5 debe correrse en WS con matriz explicita y sin `--retrain-gp`.
- La tesis apunta a campana amplia si el tiempo/WS lo permite: orden de magnitud `90-130` simulaciones adicionales planificadas por etapas, no lanzadas de una sola vez.
- Las 10 formas pueden entrar solo si se tratan como extension de forma, no como mezcla desordenada dentro del GP base.
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
- Con 4 meses o mas de computo disponible, el limite principal ya no es solo tiempo GPU; el limite real es diseno metodologico, trazabilidad y capacidad de interpretar variables sin mezclar efectos.

## Pendientes criticos
- Commit/push de analisis after-AL4, matriz AL5, prompt WS AL5 y APOS.
- En WS: hacer `git pull`, dry-run AL5 y ejecutar solo si lista exactamente 8 casos.
- Al terminar AL5, crear export liviano, subir a Git y avisar explicitamente a laptop: "SI ACTIVE SIEMPRE NTFY".
- Cuando vuelva AL5: reentrenar GP after-AL5 y decidir holdout/checks finos `dp=0.002`.
- Actualizar web post-convergencia con AL4 despues del reentrenamiento local.
- Planificar etapa posterior ambiciosa: holdout base, checks finos `dp=0.002`, campana pendiente, campana orientacion, analisis STL de las 10 formas, sanity de contacto por forma y campana de forma idealmente con las 10 formas si pasan filtros.

## Riesgos activos
- Riesgo de reentrenar GP automaticamente en WS; mantenerlo desactivado.
- Riesgo de confundir interpolacion GP con resultado SPH directo.
- Riesgo de abrir pendiente/orientacion/forma antes de cerrar bien la frontera base.
- Riesgo de sobreinterpretar rotacion diagnostica como falla primaria.
- Riesgo de intentar usar las 10 formas sin normalizar volumen/masa/inercia/apoyo, lo que confundiria efecto de forma con errores de setup.

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

### HANDOFF
# HANDOFF

## Proxima accion recomendada
1. Hacer commit/push desde laptop con GP after-AL4, matriz AL5, prompt WS AL5 y APOS.
2. En WS: `git pull origin master`.
3. En WS: dry-run AL5 con `config/al_batch5_after_al4_20260520.csv`.
4. Si dry-run lista exactamente 8 casos, ejecutar AL5.
5. Despues de AL5 y reentrenamiento, preparar hoja de ruta ambiciosa para pendiente, orientacion y forma.

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
- AL5 ya fue lanzado en WS el 2026-05-20 18:29.
- Como AL5 fue lanzado con `--no-notify`, se activo watcher externo ntfy a las 18:43.
- Watcher AL5: `scripts/watch_production_ntfy.py`, log `data/logs/production_ntfy_watch_al5_20260520.log`.
- Regla para siguientes lotes: si se usa `--no-notify`, arrancar siempre `scripts/start_production_ntfy_watch.ps1`.
- Decision estrategica de sesion: el plan objetivo ya no es cerrar con el minimo. Se adopta plan ambicioso, compatible con ~90-130 simulaciones adicionales por etapas si aportan evidencia interpretable.
- El usuario quiere idealmente usar las 10 formas STL. Eso queda como objetivo, pero solo despues de cerrar frontera base y pasar analisis geometrico + sanity de contacto por forma.

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
- `data/geometry/bloques_b02_20260510/ANALISIS_BLOQUES_STL_20260510.md`

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
- ntfy queda activo por notificacion nativa o watcher externo.

## Comandos sugeridos para WS mientras AL5 corre
```powershell
Get-Content data\production_status.json
Get-Content data\production_20260520_1829.log -Tail 100 -Wait
Get-Content data\logs\production_ntfy_watch_al5_20260520.log -Tail 40
```

## No hacer todavia
- No cambiar la matriz AL5 en WS sin volver a justificarla en laptop.
- No abrir pendiente/orientacion/forma antes de cerrar el analisis AL4.
- No lanzar campana de 10 formas antes de elegir metricas geometricas, confirmar masa/inercia/centroide/apoyo por STL, correr sanity de contacto por forma y decidir si todas aportan variacion real.
- No tratar el GP como resultado SPH directo.
- No versionar crudos pesados.
- No usar `--retrain-gp` en WS.
- No dejar corridas largas sin ntfy: usar nativo o watcher externo.

## Riesgos inmediatos
- AL4 incluye puntos muy cercanos al umbral; pequenas diferencias de resolucion/contacto pueden cambiar clase.
- Rotacion supera 5 grados en varios casos, pero no decide la clase bajo `displacement_only`.
- `al5_highH_m085_mu0900` puede fallar aun con `mu=0.90`; si ocurre, se reporta que para `H=0.225,m*=0.85` la frontera queda fuera del dominio de `mu<=0.90`.

### PLAN
o
Construir una tesis fuerte con plan ambicioso y jerarquico: cerrar primero la frontera base `[H, mu, m*]`, validarla, y luego expandir a pendiente, orientacion y forma sin perder interpretabilidad.

## Fase actual
Post-AL4 en laptop: GP after-AL4 reentrenado y AL5 preparado para ejecutar en WS.

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
- [x] En WS: dry-run AL4.
- [x] En WS: ejecutar AL4.
- [x] Exportar AL4 liviano.
- [x] Subir AL4 por Git a laptop.
- [x] Reentrenar GP after-AL4 en laptop.
- [x] Decidir si sigue AL5, holdout o checks finos `dp=0.002`.
- [x] Generar matriz AL5.
- [x] Preparar prompt WS AL5.
- [ ] Commit/push de GP after-AL4 y AL5.
- [ ] En WS: dry-run AL5.
- [ ] En WS: ejecutar AL5.
- [x] Activar watcher externo ntfy para AL5 lanzado con `--no-notify`.
- [ ] Traer AL5 a laptop.
- [ ] Reentrenar GP after-AL5.
- [ ] Decidir holdout/checks finos `dp=0.002`.
- [ ] Actualizar web post-convergencia con AL4 y GP after-AL4.
- [ ] Seleccionar variables secundarias: pendiente, orientacion y formas/STL representativas.
- [ ] Al cerrar AL5, exportar liviano, subir por Git y registrar que ntfy estuvo activo.
- [ ] Preparar plan ambicioso post-base con presupuesto de ~90-130 simulaciones adicionales por etapas.
- [ ] Analizar si las 10 formas STL disponibles aportan variacion geometrica suficiente o si algunas son redundantes.
- [ ] Disenar sanity de contacto por forma.
- [ ] Decidir campana de forma: idealmente 10 formas, pero solo si pasan filtros geometricos/contacto.

## Linea metodologica prevista
1. Cerrar frontera base con `[H, mu, m*]`.
2. Validar la frontera base con holdout/repeticiones marginales.
3. Agregar checks finos `dp=0.002` en pocos puntos criticos.
4. Agregar pendiente como extension controlada.
5. Agregar orientacion como sensibilidad controlada.
6. Agregar forma como extension fuerte. Objetivo ideal: usar las 10 formas STL, siempre que el analisis geometrico demuestre que no son redundantes y que cada una pasa sanity de contacto.
7. Entregar estado limite, fragilidad condicional, incertidumbre y validacion por capas.

## Plan ambicioso de simulaciones
- Base final `[H, mu, m*]`: AL5 + posible AL6 + holdout + checks `dp=0.002`.
- Pendiente: mini-campana dirigida en varios `slope_inv`.
- Orientacion: sensibilidad por angulos discretos del bloque.
- Forma: idealmente 10 STL, con sanity por forma y casos hidraulicos cerca de frontera.
- Rango objetivo: `90-130` simulaciones adicionales maximas planificadas por etapas, no lanzadas simultaneamente.

## Bloqueos
- No lanzar nuevos casos si la WS no esta sincronizada por Git.
- No usar GP legacy ni reentreno automatico.
- No versionar crudos pesados.
- No usar el caso parcial de batch4 como oficial.
- No abrir forma si no esta resuelto el procesamiento consistente de volumen, centroide, masa, inercia, apoyo inicial e insertion point por STL.

## Fuera de alcance por ahora
- Factorial completo 6D sin active learning.
- Dominio amplio de forma sin seleccion geometrica/contacto previa.
- Claims universales de bloques costeros.

### Riesgos activos
y recuperar solo archivos puntuales si falta algo.
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

## RISK-20260520-001 - Usar 10 formas sin control geometrico/contacto

Estado: activo
Severidad: alta
Probabilidad: media
Evidencia: el usuario quiere idealmente usar las 10 formas STL para dar peso cientifico al efecto de forma, pero varias pueden ser geometricamente parecidas o requerir ajustes de masa/inercia/apoyo.
Mitigacion: antes de correr campana de forma, hacer analisis geometrico avanzado, verificar masa/inercia/centroide/apoyo por STL y correr sanity de contacto por forma. Tratar forma como extension jerarquica, no como mezcla dentro del GP base.
Relacionado: `data/geometry/bloques_b02_20260510/ANALISIS_BLOQUES_STL_20260510.md`, `models/`

### Preguntas abiertas
5 casos esta corriendo.
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

Estado: resuelta parcialmente
Tipo: tecnica
Contexto: se decidio que el plan no debe cerrar con el minimo de simulaciones si hay 6 meses y WS potente. Pendiente, orientacion y forma importan, pero deben entrar de forma jerarquica.
Que evidencia falta:
- resultados de AL5 y posible AL6;
- reentrenamiento GP after-AL5;
- holdout base;
- analisis geometrico/STL actualizado para determinar si conviene usar las 10 formas o un subconjunto;
- presupuesto actualizado de tiempo por simulacion.
Resolucion: se adopta plan ambicioso por etapas; no se lanzara factorial 6D. La forma entra como extension fuerte, idealmente con las 10 formas, si pasan analisis geometrico y sanity de contacto.

## Q-20260520-001 - Usar las 10 formas STL o subconjunto representativo

Estado: abierta
Tipo: tecnica
Contexto: el usuario quiere idealmente aprovechar las 10 formas disponibles para que el efecto de forma tenga peso cientifico. Antes se propuso usar pocas formas por prudencia metodologica.
Que evidencia falta:
- revisar/actualizar analisis geometrico de las 10 STL;
- medir volumen, d_eq, bbox, ratios L/B/T, solidez, huella inferior, centroide e inercia;
- verificar que el pipeline genera masa/inercia/apoyo correcto por forma;
- correr sanity de contacto por forma;
- decidir si todas las formas son suficientemente distintas o si algunas son redundantes.
Resolucion: pendiente; objetivo ideal es usar las 10, pero no sin filtros geometricos/contacto.

## Exports livianos recientes
- `exports\al_batch4_after_al3_20260520` (2026-05-20T18:07)
- `exports\al_batch3_gp_after_al2_20260518` (2026-05-18T15:02)
- `exports\stitch_visual_package_20260515` (2026-05-16T17:36)
- `exports\batch4_mass_probe_20260513` (2026-05-16T17:36)
- `exports\al_batch2_bracket_closing_20260516` (2026-05-16T17:36)
- `exports\al_batch1_hybrid_20260514` (2026-05-16T17:36)
- `exports\ws_delta_conv_edge_f0685_20260422_090418` (2026-05-10T12:54)
- `exports\ws_delta_conv_edge_f0685_20260422_081859` (2026-05-10T12:54)

## Cambios locales al momento de guardar
**Cambios livianos o de codigo:**
- `UU .apos/HANDOFF.md`
- `M  .apos/INDEX.md`
- `UU .apos/JOURNAL.md`
- `UU .apos/LAPTOP_SYNC.md`
- `M  .apos/OPEN_QUESTIONS.md`
- `UU .apos/PLAN.md`
- `M  .apos/RISKS.md`
- `UU .apos/STATUS.md`

## Instrucciones para laptop
1. Ejecutar `git pull`.
2. Leer primero `.apos/LAPTOP_SYNC.md`.
3. Luego leer `.apos/HANDOFF.md` y `.apos/STATUS.md`.
4. No asumir que outputs runtime ignorados por Git estan disponibles localmente.
5. Si hay simulacion activa en WS, tratar `data/results.sqlite` como vivo hasta que exista export liviano cerrado.
