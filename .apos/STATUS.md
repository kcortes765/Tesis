# STATUS

Ultima actualizacion: 2026-05-13
Proyecto: SPH-IncipientMotion / Tesis UCN 2026
Ruta canonica local: C:\Seba\Tesis
Estado actual: repo canonico unico actualizado y pusheado a `origin/master` con piloto, batch2, batch3, verificacion preproduccion, web de convergencia y analisis STL b02; APOS unificado en esta carpeta; datos locales nuevos identificados y separados por origen.

## Hechos verificados
- `C:\Seba\Tesis` esta actualizado a `origin/master` en commit `3c443e9 Add batch3 production export`.
- Commit local de reconciliacion `0e98b65 Reconcile local APOS and verification assets` fue pusheado a `origin/master`.
- En esta laptop, `C:\Seba\Tesis` es una junction hacia `C:\Users\kevin\projects\Tesis`; ambos paths representan la misma carpeta, no dos repos.
- No queda una segunda carpeta canonica: `C:\Seba\Tesis_origin_master_clean_20260510_123639` fue solo un worktree temporal de rescate.
- El worktree temporal `C:\Seba\Tesis_origin_master_clean_20260510_123639` fue retirado tras respaldar su `.apos` en `C:\Seba\workspace_backups\tesis-reconcile-20260510_125339\temp_worktree_before_remove`.
- Antes de actualizar, los cambios trackeados locales quedaron en `stash@{0}` con mensaje `pre-reconcile tracked changes 20260510_125339`.
- Existe backup externo en `C:\Seba\workspace_backups\tesis-reconcile-20260510_125339`.
- Ocho archivos no trackeados que chocaban con archivos nuevos de GitHub fueron movidos a `.apos/cache/git-untracked-conflicts-20260510_125339/` y respaldados externamente.
- La politica de origen de datos quedo documentada en `docs/DATA_ORIGIN_POLICY.md`.
- La fuente GitHub/WS se identifica como `origin/master` y los exports livianos versionados.
- La fuente laptop/local se identifica como `C:\Seba\Tesis` para analisis, documentos, STL recibidos y archivos no sincronizados.
- Los crudos pesados deben quedar fuera de Git normal y moverse a disco externo/storage dedicado si se quieren conservar completos.
- Convergencia cerrada para uso productivo: `dp=0.003`, `classification_mode=displacement_only`, `reference_time_s=0.5`.
- Piloto productivo: 5/5 OK, 0 fallos numericos, export en `exports/pilot_productivo_20260501/`.
- Batch2 productivo: 8/8 OK, 0 fallos numericos, export en `exports/batch2_productivo_20260505/`.
- Batch3 productivo dirigido: 10/10 OK, 0 fallos numericos, export en `exports/batch3_productivo_20260509/`.
- Batch3 produjo 6 FALLO y 4 ESTABLE por `displacement_only`.
- Batch3 base `H=0.20`, `slope=1:20`: FALLO en `mu=0.678` y `mu=0.680`; ESTABLE en `mu=0.682`.
- Batch3 `H=0.175`: ESTABLE en `mu=0.600`, `0.640` y `0.660`.
- Batch3 `H=0.210`: FALLO en `mu=0.700` y `mu=0.740`.
- Batch3 `H=0.225`: FALLO en `mu=0.760` y `mu=0.800`.
- En WS `C:\Users\Admin\Desktop\SPH-Tesis`, batch4 mass probe fue ejecutado con matriz explicita `config/batch4_mass_probe_20260510.csv`, `dp=0.003`, `classification_mode=displacement_only` y `reference_time_s=0.5`.
- Batch4 produjo 11/12 casos oficiales postprocesados en SQLite y `data/processed`; el caso 12 (`batch4_mass_m125_H0225_mu0860`) genero CSVs crudos parciales hasta ~9.506 s, pero no quedo postprocesado oficialmente por el runner.
- Export liviano batch4 creado en `exports/batch4_mass_probe_20260513/`: 39 archivos, ~85 KB, sin binarios pesados.
- `exports/batch4_mass_probe_20260513/batch4_summary.csv` contiene 11 casos oficiales + caso 12 marcado como `PARTIAL_RECOVERED_NOT_SQLITE`.
- Batch4 oficial: 5 FALLO y 6 ESTABLE por `displacement_only`; el caso 12 parcial aparece ESTABLE, pero solo como diagnostico no oficial.
- Precheck de masa/contacto batch4: 2/2 OK en `exports/batch4_mass_probe_20260513/batch4_precheck_summary.csv`.
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
- Revisar cientificamente piloto + batch2 + batch3 + batch4 juntos.
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
