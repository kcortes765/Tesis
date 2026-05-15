# LAPTOP_SYNC

Ultima actualizacion WS: 2026-05-15T00:11:48
Proyecto: SPH-Tesis
Ruta WS: `C:\Users\Admin\Desktop\SPH-Tesis`

Este archivo es el resumen inteligente que `/guardar` debe versionar para que la laptop reciba contexto por `git pull`.

## Git
- Rama: `master`
- HEAD: `f43aab8 Add absolute scales to convergence figures`

```text
## master...origin/master
 M .agents/skills/guardar/SKILL.md
 M data/results.sqlite
?? scripts/apos_prepare_laptop_sync.py
```

## Estado productivo / simulaciones
- **phase:** `production`
- **mode:** `prod`
- **dp:** `0.003`
- **total_cases:** `10`
- **completed:** `1`
- **failed:** `0`
- **current_case:** `al2_base_m085_mu0820`
- **progress:** `2/10`
- **updated:** `2026-05-15T00:03:03.066972`
- **eta_human:** `28.4h (1.2d)`
- **eta:** `2026-05-16T04:26:03.738019`

## Estado APOS resumido

### STATUS
_bracket_closing_20260514.csv` con 10 casos dirigidos.
- Dry-run AL batch2 fue correcto: 10 casos, matriz explicita, `dp=0.003`, `classification_mode=displacement_only`, `reference_time_s=0.5`.
- AL batch2 real fue lanzado en WS el 2026-05-14 20:30 con `python scripts\run_production.py --prod --matrix config\al_batch2_bracket_closing_20260514.csv --max-cases 10`.
- Estado inicial AL batch2: `phase=production`, `current_case=al2_lowH_m085_mu0585`, `progress=1/10`.
- Procesos activos al lanzamiento: `python` PID 8356 y `DualSPHysics5.4_win64` PID 20088.
- ntfy nativo quedo activo para AL batch2: el log registra `PRODUCCION INICIADA` e `INICIO CASO 1/10`.
- Se generaron figuras finales de convergencia con doble lectura porcentual/absoluta en `data/figures/derived_convergence_graphics/`.
- Se genero una nueva carpeta de figuras productivas/active learning en `data/figures/production_story_graphics/`.
- `data/figures/production_story_graphics/master_production_story.csv` consolida piloto, batch2, batch3, batch4 y AL1: 43 filas totales, con el caso parcial de batch4 marcado como no oficial.
- AL2 no fue incorporado a las figuras porque sigue activo y aun no tiene export oficial.
- La guia visual SOTA para figuras cientificas quedo en `docs/VISUAL_STORYTELLING_Q1_TESIS_20260514.md`.
- Los STL recibidos localmente estan en `models/bloques/b02_variantes_20260510/`.
- El analisis de STL escalado esta en `data/geometry/bloques_b02_20260510/`.

## Decisiones activas
- Usar solo `C:\Seba\Tesis` como repo local canonico.
- APOS canonico vive solo en `C:\Seba\Tesis\.apos`.
- Runtime APOS del proyecto queda reducido a tres skills repo-locales: `/apos`, `/guardar`, `/apos-status`.
- `apos-system/` se conserva como herramienta/historial parcial, no como segundo APOS vivo.
- No mantener worktrees temporales como fuente de trabajo.
- No recuperar automaticamente `stash@{0}`; revisarlo solo si falta algo especifico.
- No borrar `cases/`, `data/`, `imports/`, `archive/` ni backups sin revision explicita.
- Adoptar `dp=0.003` como resolucion operativa de produccion, sin vender convergencia asintotica fuerte.
- Usar `classification_mode=displacement_only` como criterio primario.
- Usar `reference_time_s=0.5`.
- Tratar la rotacion como diagnostico, no como criterio primario.
- Mantener tandas futuras con matriz explicita, `--max-cases`, dry-run previo y export liviano.

## Inferencias vigentes
- El estado cientifico versionable debe leerse desde GitHub/WS + exports livianos.
- La data local de laptop puede ser valiosa, pero debe portarse selectivamente y con origen declarado.
- Piloto + batch2 + batch3 ya dan base suficiente para entrenar un surrogate exploratorio o disenar el siguiente mini-batch.
- La variacion geometrica requiere pipeline especifico: STL, escala, masa, centroide, inercia, insertion point y sanity de contacto.

## Pendientes criticos
- Revisar cientificamente piloto + batch2 + batch3 + batch4 + AL batch1 juntos.
- Revisar las nuevas figuras de `data/figures/production_story_graphics/` y elegir cuales pasan a tesis/PPT.
- Hacer `git pull` en laptop principal para traer `exports/al_batch1_hybrid_20260514/`.
- Monitorear AL batch2 hasta terminar o fallar.
- Crear export liviano AL batch2 cuando termine.
- Regenerar `production_story_graphics` cuando AL2 tenga export oficial.
- Decidir si el siguiente paso es surrogate exploratorio, mini-batch adicional o incorporacion controlada de geometria.
- Decidir si repetir o reprocesar oficialmente `batch4_mass_m125_H0225_mu0860` antes de entrenar surrogate final.
- Revisar `stash@{0}` solo para recuperar cambios locales explicitamente valiosos.
- Revisar cientificamente los resultados ya versionados para decidir surrogate/mini-batch/geometria.

## Riesgos activos
- Riesgo de mezclar origen WS/GitHub con origen laptop/local si no se cita el export o path.
- Riesgo de perder datos si se limpia data local sin revisar backups y stash.
- Riesgo interpretativo: leer batch2/batch3 como campana parametrica completa; son lotes dirigidos.
- Riesgo interpretativo: mezclar rotacion diagnostica con criterio primario `displacement_only`.
- Riesgo de trazabilidad: batch4 caso 12 tiene recuperacion parcial, no resultado oficial completo; no mezclarlo sin flag.
- Riesgo interpretativo: no tratar AL batch1 como mapa completo; es lote dirigido hibrido post batch4.
- Riesgo operativo: AL batch2 esta en ejecucion; no lanzar otra tanda encima.
- Riesgo interpretativo: AL batch2 cierra brackets dirigidos, no reemplaza validacion global.

## Evidencia reciente
- `docs/DATA_ORIGIN_POLICY.md`
- `C:\Seba\workspace_backups\tesis-reconcile-20260510_125339\backup_summary.json`
- `.apos/cache/git-untracked-conflicts-20260510_125339/moved_manifest.csv`
- `stash@{0}: pre-reconcile tracked changes 20260510_125339`
- `exports/pilot_productivo_20260501/`
- `exports/batch2_productivo_20260505/`
- `exports/batch3_productivo_20260509/`
- `models/bloques/b02_variantes_20260510/`
- `data/geometry/bloques_b02_20260510/ANALISIS_BLOQUES_STL_20260510.md`
- `0e98b65 Reconcile local APOS and verification assets`
- `exports/batch4_mass_probe_20260513/README.md`
- `exports/batch4_mass_probe_20260513/batch4_summary.csv`
- `exports/batch4_mass_probe_20260513/batch4_case12_partial_recovery.csv`
- `data/production_20260510_2054.log`
- `config/al_batch1_hybrid_20260513.csv`
- `docs/PROMPT_WS_AL_BATCH1_HYBRID_20260513.md`
- `data/production_20260513_0941.log`
- `data/production_status.json`
- `exports/al_batch1_hybrid_20260514/README.md`
- `exports/al_batch1_hybrid_20260514/al_batch1_summary.csv`
- `exports/al_batch1_hybrid_20260514/al_batch1_summary.md`
- `config/al_batch2_bracket_closing_20260514.csv`
- `data/production_20260514_2030.log`
- `data/production_status.json`
- `data/figures/derived_convergence_graphics/FIGURE_INDEX.md`
- `data/figures/production_story_graphics/FIGURE_INDEX.md`
- `data/figures/production_story_graphics/master_production_story.csv`
- `docs/VISUAL_STORYTELLING_Q1_TESIS_20260514.md`

### HANDOFF
sv`.
- Comando real: `python scripts\run_production.py --prod --matrix config\al_batch1_hybrid_20260513.csv --max-cases 8`.
- AL batch1 no usa `--no-notify`; ntfy nativo esta activo.
- Estado inicial: `current_case=al1_lowH_m085_mu0620`, `progress=1/8`.
- AL batch1 termino 8/8 OK, 0 fallos numericos, 34.37 h.
- Export AL batch1: `exports/al_batch1_hybrid_20260514/`.
- Resultado AL batch1: 1 FALLO (`al1_base_m085_mu0780`) y 7 ESTABLE por `displacement_only`.
- AL batch2 bracket-closing fue creado en `config/al_batch2_bracket_closing_20260514.csv`.
- Dry-run AL batch2 fue correcto: 10 casos, `dp=0.003`, matriz explicita, `displacement_only`, `reference_time_s=0.5`.
- AL batch2 fue lanzado el 2026-05-14 20:30 con `python scripts\run_production.py --prod --matrix config\al_batch2_bracket_closing_20260514.csv --max-cases 10`.
- Estado inicial AL batch2: `current_case=al2_lowH_m085_mu0585`, `progress=1/10`.
- Log AL batch2: `data/production_20260514_2030.log`.
- ntfy nativo esta activo para AL batch2.
- Figuras de convergencia retocadas: `data/figures/derived_convergence_graphics/`; todo porcentaje de desplazamiento tiene equivalente absoluto en mm.
- Figuras nuevas de produccion/AL: `data/figures/production_story_graphics/`; consolidan piloto, batch2, batch3, batch4 y AL1, pero no AL2 activo.
- Guia visual Q1: `docs/VISUAL_STORYTELLING_Q1_TESIS_20260514.md`.
- Los STL nuevos estan en `models/bloques/b02_variantes_20260510/`.
- El analisis de formas esta en `data/geometry/bloques_b02_20260510/`.

## Archivos a leer primero
1. `.apos/CONTEXT_POLICY.md`
2. `.apos/INDEX.md`
3. `.apos/STATUS.md`
4. `.apos/HANDOFF.md`
5. `docs/DATA_ORIGIN_POLICY.md`
6. `exports/batch3_productivo_20260509/batch3_summary.md`
7. `exports/batch3_productivo_20260509/batch3_summary.csv`
8. `exports/batch2_productivo_20260505/batch2_summary.csv`
9. `exports/pilot_productivo_20260501/pilot_summary.csv`
10. `data/geometry/bloques_b02_20260510/ANALISIS_BLOQUES_STL_20260510.md`
11. `exports/batch4_mass_probe_20260513/batch4_summary.md`
12. `exports/batch4_mass_probe_20260513/batch4_summary.csv`
13. `config/al_batch1_hybrid_20260513.csv`
14. `docs/PROMPT_WS_AL_BATCH1_HYBRID_20260513.md`
15. `data/production_20260513_0941.log`
16. `exports/al_batch1_hybrid_20260514/al_batch1_summary.md`
17. `exports/al_batch1_hybrid_20260514/al_batch1_summary.csv`
18. `config/al_batch2_bracket_closing_20260514.csv`
19. `data/production_status.json`
20. `data/production_20260514_2030.log`
21. `data/figures/production_story_graphics/FIGURE_INDEX.md`
22. `data/figures/production_story_graphics/master_production_story.csv`
23. `docs/VISUAL_STORYTELLING_Q1_TESIS_20260514.md`

## Comandos sugeridos
```powershell
cd C:\Seba\Tesis
git status -sb

Get-Content exports\batch3_productivo_20260509\batch3_summary.md

Import-Csv exports\batch3_productivo_20260509\batch3_summary.csv |
  Select case_id,dam_height,friction_coefficient,slope_inv,criterion_class,disp_pct_deq,max_rotation_deg

Import-Csv exports\batch4_mass_probe_20260513\batch4_summary.csv |
  Select case_id,status,dam_height,boulder_mass,friction_coefficient,criterion_class,disp_pct_deq,quality_flags

Get-Content data\production_status.json

Get-ChildItem data -Filter "production_*.log" |
  Sort LastWriteTime -Descending |
  Select -First 1 |
  Get-Content -Tail 120

Import-Csv exports\al_batch1_hybrid_20260514\al_batch1_summary.csv |
  Select case_id,status,dam_height,boulder_mass,friction_coefficient,criterion_class,disp_pct_deq

Get-Content data\production_status.json

Get-Content data\production_20260514_2030.log -Tail 120

Get-Process | Where-Object { $_.ProcessName -match "DualSPHysics|GenCase|python" } |
  Select Id,ProcessName,StartTime,CPU

Get-Content data\figures\production_story_graphics\FIGURE_INDEX.md
```

## Senales de exito
- `git status -sb` no muestra otro worktree como fuente canonica.
- Los datos de WS se citan por export/commit.
- Batch4 queda versionado como export liviano; el caso 12 queda explicitamente marcado como parcial.
- AL batch1 queda versionado como export liviano y trazable.
- AL batch2 queda monitoreado hasta `completed=10` o falla diagnosticada.
- Las figuras productivas usan todos los datos oficiales hasta AL1 y declaran los outliers fuera de escala.
- Los datos locales se citan por path y quedan versionados si son livianos.
- No queda APOS duplicado como verdad viva.

## No hacer todavia
- No recrear ni usar worktrees temporales como fuente diaria.
- No aplicar `stash@{0}` completo sin revisar.
- No borrar backups, `cases/`, `data/`, `imports/` ni `archive/`.
- No lanzar otra tanda antes de revisar AL batch1 junto con los lotes anteriores.
- No lanzar otra tanda mientras AL batch2 este activo.
- No versionar crudos pesados.
- No mezclar rotacion diagnostica con falla por desplazamiento.

## Riesgos inmediatos
- Confundir origen WS/GitHub con origen laptop/local.
- Recuperar cambios viejos del stash y reintroducir APOS antiguo.
- Sobreinterpretar batch2/batch3 como mapa completo.

### PLAN
# PLAN

## Objetivo activo
Monitorear AL batch2 bracket-closing en la WS, conservar trazabilidad por matriz explicita y preparar export liviano cuando termine.

## Fase actual
AL batch2 real lanzado en WS con 10 casos dirigidos, `dp=0.003`, `classification_mode=displacement_only` y `reference_time_s=0.5`.

## Proximos hitos
- [x] Cerrar convergencia y adoptar `dp=0.003` como malla operativa.
- [x] Documentar configuracion productiva oficial.
- [x] Crear matriz piloto explicita de 5 casos.
- [x] Agregar guardas a `scripts/run_production.py`.
- [x] Ejecutar dry-run del piloto.
- [x] Lanzar piloto real de 5 casos.
- [x] Esperar fin del piloto y auditar resultados.
- [x] Crear export liviano del piloto productivo.
- [x] Crear matriz batch2 chica de 8 casos.
- [x] Ejecutar preflight y dry-run batch2.
- [x] Lanzar batch2 real en background.
- [x] Esperar fin de batch2 y auditar resultados.
- [x] Crear export liviano batch2.
- [x] Crear matriz batch3 productiva dirigida de 10 casos.
- [x] Ejecutar dry-run batch3.
- [x] Lanzar batch3 real.
- [x] Esperar fin de batch3 y auditar resultados.
- [x] Crear export liviano batch3.
- [x] Actualizar `C:\Seba\Tesis` a `origin/master` sin perder cambios locales.
- [x] Respaldar cambios locales en `C:\Seba\workspace_backups\tesis-reconcile-20260510_125339`.
- [x] Guardar cambios trackeados previos en `stash@{0}`.
- [x] Documentar politica de origen de datos en `docs/DATA_ORIGIN_POLICY.md`.
- [x] Simplificar APOS operativo a `.apos/` + tres skills repo-locales: `/apos`, `/guardar`, `/apos-status`.
- [x] Committear APOS unificado, politica de origen, verificacion local y analisis de bloques.
- [x] Retirar el worktree temporal `C:\Seba\Tesis_origin_master_clean_20260510_123639`.
- [x] Ejecutar batch4 mass probe en WS con `dp=0.003`.
- [x] Crear export liviano batch4 en `exports/batch4_mass_probe_20260513/`.
- [x] Recibir desde Git la matriz `config/al_batch1_hybrid_20260513.csv`.
- [x] Ejecutar dry-run AL batch1 hibrido.
- [x] Lanzar AL batch1 hibrido real en WS.
- [x] Monitorear AL batch1 hasta completar o fallar.
- [x] Crear export liviano AL batch1.
- [x] Crear matriz AL batch2 bracket-closing.
- [x] Ejecutar dry-run AL batch2.
- [x] Lanzar AL batch2 real.
- [x] Retocar figuras de convergencia para mostrar porcentajes y medidas absolutas.
- [x] Crear figuras productivas/AL con todos los datos oficiales hasta AL1.
- [x] Documentar guia visual Q1 para figuras cientificas y storytelling.
- [ ] Monitorear AL batch2 hasta completar o fallar.
- [ ] Crear export liviano AL batch2.
- [ ] Regenerar figuras productivas/AL incorporando AL2 cuando exista export oficial.
- [ ] Revisar cientificamente el export del piloto, batch2, batch3, batch4, AL batch1 y AL batch2 juntos.
- [ ] Decidir si repetir/reprocesar el caso 12 parcial de batch4.
- [ ] Decidir mini-batch adicional o primer surrogate exploratorio.
- [ ] Decidir si se abre modulo geometrico con 2-3 STL reales + formas sinteticas controladas.
- [ ] Completar evals APOS-X sobre las tres skills repo-locales y endurecer `apos-run`.

## Bloqueos
- No iniciar otra tanda mientras AL batch2 este activo.
- No interpretar AL batch2 como campana global; es cierre dirigido de brackets.
- No tocar global/system sin confirmacion explicita.
- No aplicar `stash@{0}` completo sin revision.
- No borrar backups ni crudos locales.

## Fuera de alcance por ahora
- Campana parametrica grande.
- Watchers en background.
- MCP server local.
- Vector DB.
- Dashboard complejo.

### Riesgos activos
treo amplio del espacio parametrico.
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

Estado: activo
Severidad: alta
Probabilidad: media
Evidencia: `data/production_status.json` reporta `phase=production`, `total_cases=10`, `current_case=al2_lowH_m085_mu0585`, `progress=1/10`; procesos `python` y `DualSPHysics5.4_win64` activos.
Mitigacion: no lanzar otra tanda; monitorear `data/production_status.json` y `data/production_20260514_2030.log`; si falla un caso, diagnosticar antes de relanzar.
Relacionado: `config/al_batch2_bracket_closing_20260514.csv`, `scripts/run_production.py`, `data/production_20260514_2030.log`

### Preguntas abiertas
# OPEN_QUESTIONS

## Q-20260501-001 - Resultado completo del piloto productivo

Estado: abierta
Tipo: tecnica
Contexto: el piloto de 5 casos esta corriendo.
Que evidencia falta:
- `production_status.json` final.
- logs finales.
- CSVs procesados por caso.
Resolucion: pendiente hasta que termine el proceso.

## Q-20260501-002 - Instalacion de skills APOS-X

Estado: abierta
Tipo: requisito
Contexto: se preparo memoria APOS-X local, pero no se instalaron skills repo-locales ni globales.
Que evidencia falta:
- decision del usuario sobre instalar `.agents/skills`.
- resultado de evals locales.
Resolucion: pendiente.

## Q-20260501-003 - Alcance de `apos-system/`

Estado: abierta
Tipo: tecnica
Contexto: la especificacion APOS-X define una fuente versionada `apos-system/`.
Que evidencia falta:
- decidir si vive en este repo, en repo separado, o como paquete personal.
Resolucion: pendiente; por ahora se preparo el proyecto local sin tocar global.

## Exports livianos recientes
- `exports\al_batch1_hybrid_20260514` (2026-05-14T20:12)
- `exports\batch4_mass_probe_20260513` (2026-05-13T08:34)
- `exports\batch3_productivo_20260509` (2026-05-09T23:24)
- `exports\batch2_productivo_20260505` (2026-05-06T11:30)
- `exports\pilot_productivo_20260501` (2026-05-03T12:20)
- `exports\ws_delta_conv_edge_f0685_20260422_090418` (2026-04-22T09:04)
- `exports\ws_delta_conv_edge_f0685_20260422_081859` (2026-04-22T08:18)
- `exports\thesis_analysis_prelim_20260421_144616_parts` (2026-04-21T17:56)

## Cambios locales al momento de guardar
**Cambios livianos o de codigo:**
- `M .agents/skills/guardar/SKILL.md`
- `?? scripts/apos_prepare_laptop_sync.py`

**Cambios runtime/pesados/no sincronizar a ciegas:**
- ` M data/results.sqlite`

## Instrucciones para laptop
1. Ejecutar `git pull`.
2. Leer primero `.apos/LAPTOP_SYNC.md`.
3. Luego leer `.apos/HANDOFF.md` y `.apos/STATUS.md`.
4. No asumir que outputs runtime ignorados por Git estan disponibles localmente.
5. Si hay simulacion activa en WS, tratar `data/results.sqlite` como vivo hasta que exista export liviano cerrado.
