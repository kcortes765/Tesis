# RISKS

## RISK-20260501-001 - Piloto/batch productivo en ejecucion

Estado: mitigado
Severidad: alta
Probabilidad: media
Evidencia: piloto 5/5 OK y batch2 8/8 OK; `data/production_status.json` reporta `phase=completed`.
Mitigacion: no lanzar otra tanda hasta auditar export; conservar outputs crudos fuera de Git y usar exports livianos.
Relacionado: `scripts/run_production.py`, `config/pilot_productivo_20260430.csv`, `config/batch2_productivo_20260503.csv`

## RISK-20260501-002 - Memoria APOS historica desfasada

Estado: activo
Severidad: media
Probabilidad: alta
Evidencia: `BOOTSTRAP.md`, `STATUS.md` y `HANDOFF.md` antiguos indicaban que `dp` no estaba cerrado.
Mitigacion: usar archivos reales y estado actualizado; mantener historicos como contexto, no fuente unica.
Relacionado: `STATUS.md`, `HANDOFF.md`, `CONTEXT_POLICY.md`

## RISK-20260501-003 - Ejecucion productiva accidental grande

Estado: activo
Severidad: alta
Probabilidad: media
Evidencia: el pipeline historico tenia matriz por defecto amplia y modos ambiguos.
Mitigacion: `--matrix`, `--max-cases`, `--dry-run`; siguiente paso: `apos-run`.
Relacionado: `scripts/run_production.py`, safe-harness APOS-X

## RISK-20260506-001 - Sobreinterpretar batch2 como campana completa

Estado: activo
Severidad: media
Probabilidad: media
Evidencia: batch2 tiene 8 casos dirigidos, no un muestreo amplio del espacio parametrico.
Mitigacion: presentarlo como lote exploratorio/informativo; antes de afirmar fragilidad global, disenar otro batch o surrogate con validacion.
Relacionado: `exports/batch2_productivo_20260505/batch2_summary.csv`

## RISK-20260506-002 - Mezclar rotacion diagnostica con criterio primario

Estado: activo
Severidad: media
Probabilidad: media
Evidencia: 5/8 casos batch2 tienen `rotated=True`, pero solo `moved=True` define FALLO bajo `displacement_only`.
Mitigacion: reportar rotacion en columna separada; no cambiar `criterion_class` por rotacion.
Relacionado: `src/data_cleaner.py`, `exports/batch2_productivo_20260505/batch2_summary.csv`

## RISK-20260507-001 - Batch3 productivo en ejecucion

Estado: mitigado
Severidad: alta
Probabilidad: media
Evidencia: batch3 termino 10/10 OK, 0 fallos numericos, export liviano en `exports/batch3_productivo_20260509/`.
Mitigacion: no lanzar otra tanda hasta auditar piloto + batch2 + batch3; conservar outputs crudos fuera de Git y usar export liviano.
Relacionado: `config/batch3_productivo.csv`, `scripts/run_production.py`, `exports/batch3_productivo_20260509/`

## RISK-20260510-001 - Confundir origen WS/GitHub con origen laptop/local

Estado: activo
Severidad: alta
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

## RISK-20260520-001 - Usar 10 formas sin control geometrico/contacto

Estado: activo
Severidad: alta
Probabilidad: media
Evidencia: el usuario quiere idealmente usar las 10 formas STL para dar peso cientifico al efecto de forma, pero varias pueden ser geometricamente parecidas o requerir ajustes de masa/inercia/apoyo.
Mitigacion: antes de correr campana de forma, hacer analisis geometrico avanzado, verificar masa/inercia/centroide/apoyo por STL y correr sanity de contacto por forma. Tratar forma como extension jerarquica, no como mezcla dentro del GP base.
Relacionado: `data/geometry/bloques_b02_20260510/ANALISIS_BLOQUES_STL_20260510.md`, `models/`
