# LAPTOP_SYNC

Ultima actualizacion WS: 2026-05-16T18:26:35
Proyecto: SPH-Tesis
Ruta WS: `C:\Users\kevin\projects\Tesis`

Este archivo es el resumen inteligente que `/guardar` debe versionar para que la laptop reciba contexto por `git pull`.

## Git
- Rama: `master`
- HEAD: `6f9eb41 Add after-AL2 GP analysis and AL3 plan`

```text
## master...origin/master
 M .apos/DECISIONS.md
 M .apos/HANDOFF.md
 M .apos/INDEX.md
 M .apos/JOURNAL.md
 M .apos/OPEN_QUESTIONS.md
 M .apos/PLAN.md
 M .apos/RISKS.md
 M .apos/STATUS.md
?? docs/mock_final_deliverable_20260516/
?? scripts/generate_mock_final_deliverable_20260516.py
```

## Estado productivo / simulaciones
_No hay `data/production_status.json` disponible._

## Estado APOS resumido

### STATUS
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

### HANDOFF
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

### PLAN
# PLAN

## Objetivo activo
Ejecutar AL3 y preparar un plan jerarquico robusto de seis meses para pasar de frontera base `[H, mu, m*]` a una tesis con sensibilidad de pendiente, orientacion y forma.

## Fase actual
Post-AL2 con surrogate deliberate after-AL2, AL3 listo para WS y mock sintetico de entregable final creado.

## Proximos hitos
- [x] Cerrar convergencia y adoptar dp=0.003 como resolucion operativa.
- [x] Ejecutar piloto, batch2, batch3, batch4, AL1 y AL2.
- [x] Bloquear reentrenamiento GP automatico al terminar produccion.
- [x] Traer AL2 a laptop.
- [x] Entrenar GP after-AL2 de forma deliberada.
- [x] Generar matriz AL3.
- [x] Actualizar web post-convergencia con AL2 y GP after-AL2.
- [x] Subir GP/web/AL3 a Git en commit `6f9eb41`.
- [x] Crear mock sintetico de entregable final.
- [ ] En WS: dry-run AL3.
- [ ] En WS: ejecutar AL3 si el dry-run coincide.
- [ ] Exportar AL3 liviano y traerlo a laptop.
- [ ] Reentrenar GP after-AL3 en laptop.
- [ ] Definir plan jerarquico expandido con presupuesto de simulaciones.
- [ ] Decidir AL4/holdout/checks finos `dp=0.002`.
- [ ] Seleccionar variables secundarias: pendiente, orientacion y formas/STL representativas.

## Linea metodologica prevista
1. Cerrar frontera base con `[H, mu, m*]`.
2. Agregar pendiente como extension controlada, no mezclada desde el inicio.
3. Agregar orientacion como sensibilidad controlada.
4. Agregar forma con pocas geometria representativas, elegidas por analisis STL.
5. Validar con holdout, repeticiones marginales y `dp=0.002` selectivo.
6. Entregar estado limite, fragilidad condicional, incertidumbre y validacion por capas.

## Bloqueos
- No lanzar nuevos casos si la WS no esta sincronizada por Git.
- No usar GP legacy ni reentreno automatico.
- No versionar crudos pesados.
- No usar el mock sintetico como evidencia.

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
- `exports\stitch_visual_package_20260515` (2026-05-16T17:36)
- `exports\batch4_mass_probe_20260513` (2026-05-16T17:36)
- `exports\al_batch2_bracket_closing_20260516` (2026-05-16T17:36)
- `exports\al_batch1_hybrid_20260514` (2026-05-16T17:36)
- `exports\ws_delta_conv_edge_f0685_20260422_090418` (2026-05-10T12:54)
- `exports\ws_delta_conv_edge_f0685_20260422_081859` (2026-05-10T12:54)
- `exports\thesis_analysis_prelim_20260421_144616` (2026-05-10T12:54)
- `exports\batch3_productivo_20260509` (2026-05-10T12:54)

## Cambios locales al momento de guardar
**Cambios livianos o de codigo:**
- `M .apos/DECISIONS.md`
- ` M .apos/HANDOFF.md`
- ` M .apos/INDEX.md`
- ` M .apos/JOURNAL.md`
- ` M .apos/OPEN_QUESTIONS.md`
- ` M .apos/PLAN.md`
- ` M .apos/RISKS.md`
- ` M .apos/STATUS.md`
- `?? docs/mock_final_deliverable_20260516/`
- `?? scripts/generate_mock_final_deliverable_20260516.py`

## Instrucciones para laptop
1. Ejecutar `git pull`.
2. Leer primero `.apos/LAPTOP_SYNC.md`.
3. Luego leer `.apos/HANDOFF.md` y `.apos/STATUS.md`.
4. No asumir que outputs runtime ignorados por Git estan disponibles localmente.
5. Si hay simulacion activa en WS, tratar `data/results.sqlite` como vivo hasta que exista export liviano cerrado.
