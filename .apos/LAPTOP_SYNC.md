# LAPTOP_SYNC

Ultima actualizacion WS: 2026-05-20T18:04:54
Proyecto: SPH-Tesis
Ruta WS: `C:\Users\Admin\Desktop\SPH-Tesis`

Este archivo es el resumen inteligente que `/guardar` debe versionar para que la laptop reciba contexto por `git pull`.

## Git
- Rama: `master`
- HEAD: `fd74ede Add after-AL3 GP analysis and AL4 plan`

```text
## master...origin/master
 M .apos/HANDOFF.md
 M .apos/INDEX.md
 M .apos/JOURNAL.md
 M .apos/PLAN.md
 M .apos/STATUS.md
 M data/results.sqlite
?? exports/al_batch4_after_al3_20260520/
```

## Estado productivo / simulaciones
- **phase:** `completed`
- **mode:** `prod`
- **dp:** `0.003`
- **total_cases:** `8`
- **completed:** `8`
- **failed:** `0`
- **current_case:** `al4_base_m100_mu06808`
- **progress:** `8/8`
- **updated:** `2026-05-20T03:12:58.590969`
- **eta_human:** `0.0h (0.0d)`
- **eta:** `2026-05-19T23:02:30.913454`

## Estado APOS resumido

### STATUS
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

### HANDOFF
# HANDOFF

## Proxima accion recomendada
1. Hacer commit/push desde la WS con el export AL4 liviano y `data/results.sqlite` actualizado.
2. En laptop: `git pull`.
3. En laptop: reentrenar GP after-AL4 usando datos oficiales hasta AL4.
4. Decidir si corresponde AL5, holdout o checks finos `dp=0.002`.

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
- La laptop debe reentrenar el GP; la WS no debe usar `--retrain-gp`.

## Archivos a leer primero
- `.apos/STATUS.md`
- `.apos/PLAN.md`
- `exports/al_batch4_after_al3_20260520/al_batch4_summary.md`
- `exports/al_batch4_after_al3_20260520/al_batch4_summary.csv`
- `config/al_batch4_after_al3_20260518.csv`
- `data/results.sqlite`

## Comandos sugeridos para laptop
```powershell
git pull
Get-Content exports\al_batch4_after_al3_20260520\al_batch4_summary.md
Import-Csv exports\al_batch4_after_al3_20260520\al_batch4_summary.csv |
  Select case_name,dam_height,boulder_mass,friction_coefficient,criterion_class,disp_pct_deq,margin_pct_deq
```

## Senales de exito
- Laptop ve `exports/al_batch4_after_al3_20260520/`.
- Laptop ve `data/results.sqlite` con filas `al4_*`.
- GP after-AL4 se entrena solo en laptop.
- Siguiente lote se decide con brackets actualizados, no por intuicion.

## No hacer todavia
- No lanzar AL5 antes de reentrenar y revisar AL4.
- No abrir pendiente/orientacion/forma antes de cerrar el analisis AL4.
- No tratar el GP como resultado SPH directo.
- No versionar crudos pesados.
- No usar `--retrain-gp` en WS.

## Riesgos inmediatos
- AL4 incluye puntos muy cercanos al umbral; pequenas diferencias de resolucion/contacto pueden cambiar clase.
- Rotacion supera 5 grados en varios casos, pero no decide la clase bajo `displacement_only`.
- Si el GP after-AL4 propone puntos fuera de brackets observados, revisar que sea realmente necesario.

### PLAN
# PLAN

## Objetivo activo
Cerrar de forma robusta la frontera base `[H, mu, m*]` con active learning trazable, antes de abrir pendiente, orientacion y forma como extensiones jerarquicas.

## Fase actual
Post-AL4 en WS: export liviano creado y pendiente de sincronizar por Git para reentrenamiento GP after-AL4 en laptop.

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
- [ ] Subir AL4 por Git a laptop.
- [ ] Reentrenar GP after-AL4 en laptop.
- [ ] Decidir si sigue AL5, holdout o checks finos `dp=0.002`.
- [ ] Actualizar web post-convergencia con AL4 y GP after-AL4.
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
- `exports\al_batch4_after_al3_20260520` (2026-05-20T18:03)
- `exports\al_batch3_gp_after_al2_20260518` (2026-05-18T15:00)
- `exports\al_batch2_bracket_closing_20260516` (2026-05-16T17:24)
- `exports\stitch_visual_package_20260515` (2026-05-15T03:29)
- `exports\al_batch1_hybrid_20260514` (2026-05-14T20:12)
- `exports\batch4_mass_probe_20260513` (2026-05-13T08:34)
- `exports\batch3_productivo_20260509` (2026-05-09T23:24)
- `exports\batch2_productivo_20260505` (2026-05-06T11:30)

## Cambios locales al momento de guardar
**Cambios livianos o de codigo:**
- `M .apos/HANDOFF.md`
- ` M .apos/INDEX.md`
- ` M .apos/JOURNAL.md`
- ` M .apos/PLAN.md`
- ` M .apos/STATUS.md`
- `?? exports/al_batch4_after_al3_20260520/`

**Cambios runtime/pesados/no sincronizar a ciegas:**
- ` M data/results.sqlite`

## Instrucciones para laptop
1. Ejecutar `git pull`.
2. Leer primero `.apos/LAPTOP_SYNC.md`.
3. Luego leer `.apos/HANDOFF.md` y `.apos/STATUS.md`.
4. No asumir que outputs runtime ignorados por Git estan disponibles localmente.
5. Si hay simulacion activa en WS, tratar `data/results.sqlite` como vivo hasta que exista export liviano cerrado.
