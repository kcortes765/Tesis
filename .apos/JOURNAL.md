# JOURNAL

## 2026-05-01 00:15 - Preparacion APOS-X local

### Objetivo
Actualizar este proyecto para continuidad APOS-X sin interrumpir el piloto productivo activo ni tocar configuracion global.

### Acciones
- Se leyo `.apos/BOOTSTRAP.md`.
- Se verifico estado del piloto productivo.
- Se auditaron rutas locales de skills y memoria APOS.
- Se creo snapshot antes de migrar.
- Se agrego estructura local APOS-X.
- Se reemplazaron archivos vivos `STATUS.md`, `HANDOFF.md` y `PLAN.md`.
- Se agregaron archivos faltantes de politica, calidad, riesgos, preguntas abiertas, fuentes e investigacion.

### Archivos revisados
- `.apos/BOOTSTRAP.md`
- `.apos/DECISIONS.md`
- `.apos/STATUS.md`
- `.apos/HANDOFF.md`
- `data/production_status.json`

### Archivos modificados
- `.apos/STATUS.md`
- `.apos/HANDOFF.md`
- `.apos/PLAN.md`
- `.apos/INDEX.md`
- `.apos/README.md`
- `.apos/CONTEXT_POLICY.md`
- `.apos/NARRATIVE.md`
- `.apos/SOURCES.md`
- `.apos/RESEARCH_LOG.md`
- `.apos/QUALITY.md`
- `.apos/MODULES.md`
- `.apos/RISKS.md`
- `.apos/OPEN_QUESTIONS.md`
- `.apos/.gitignore`
- `.apos/evidence/README.md`
- `.apos/research/INDEX.md`
- `.apos/transfers/INDEX.md`
- `.apos/evidence/migration/apox-readiness-20260501.md`

### Comandos importantes
```text
Get-Process | Where-Object { $_.ProcessName -match 'DualSPHysics|GenCase|python' }
Get-Content data\production_status.json
Copy-Item .apos -> .apos\snapshots\apox-migration-20260501_001524
```

### Resultados
- Piloto productivo sigue activo y no fue interrumpido.
- Snapshot creado antes de la migracion.
- `.apos/` queda preparado para lectura APOS-X selectiva.

### Errores / bloqueos
- Archivos APOS historicos tienen mojibake.
- Rutas historicas `C:\Seba` y `C:\Users\kevin` no existen en esta WS.

### Proximos pasos
- Esperar fin del piloto.
- Implementar `apos-system/` y `apos-run` local.
- Instalar skills repo-locales solo despues de validar.

### Advertencias metodologicas
- No usar memoria historica como fuente unica.
- No lanzar otra tanda mientras GPU siga ocupada.

## 2026-05-01 00:19 - Semilla apos-system y validacion de harness

### Objetivo
Dejar una fuente local versionada de APOS-X y probar la primera guarda de ejecucion segura sin correr simulaciones.

### Acciones
- Se creo `apos-system/` con estructura base.
- Se agregaron skills esqueleto: `init-apos`, `retomar`, `guardar`, `apos-skill-governance`.
- Se agregaron modulos esqueleto: `safe-harness`, `chat-transfer`, `research-autonomo`, `quality-evals`.
- Se agrego adaptador Codex con snippet para `AGENTS.md`.
- Se implemento `apos-system/harness/apos-run.py`.
- Se compilo `apos-run.py`.
- Se ejecuto preflight sobre un comando ambiguo para confirmar bloqueo.
- Se ejecuto dry-run APOS sobre la matriz piloto explicita.

### Archivos modificados
- `apos-system/README.md`
- `apos-system/VERSION.md`
- `apos-system/PROMPT_IMPLEMENTACION_APOS_X.md`
- `apos-system/harness/apos-run.py`
- `apos-system/harness/apos-run.ps1`
- `apos-system/harness/risk_rules.yaml`
- `apos-system/skills/*/SKILL.md`
- `apos-system/modules/*/SKILL.md`
- `apos-system/adapters/codex/*`
- `apos-system/docs/*`
- `apos-system/migration/*`

### Comandos importantes
```text
python -m py_compile apos-system\harness\apos-run.py
python apos-system\harness\apos-run.py preflight --cmd "python scripts\run_production.py --pilot --prod"
python apos-system\harness\apos-run.py dry-run --matrix config\pilot_productivo_20260430.csv --max-cases 5
```

### Resultados
- `apos-run.py` compila.
- El preflight bloqueo `run_production.py --pilot --prod`.
- Se guardo evidencia en `.apos/evidence/harness-runs/20260501_001919/preflight.md`.
- El dry-run de matriz piloto registro 5 casos y guardo evidencia en `.apos/evidence/harness-runs/20260501_001923/dry-run.md`.

### Proximos pasos
- Convertir skeletons en skills repo-locales reales bajo `.agents/skills` despues de evals.
- Agregar tests de append-only y harness.
- Mantener el piloto productivo sin interrupciones.

## 2026-05-01 00:25 - Simplificacion de skills visibles APOS

### Objetivo
Reducir la superficie visible de skills APOS a solo tres comandos claros para el usuario.

### Acciones
- Se eliminaron las skills repo-locales extra creadas inicialmente.
- Se dejaron unicamente:
  - `/apos`
  - `/apos-status`
  - `/guardar`
- Se ajusto `/apos` para inicializar o reparar APOS en proyectos greenfield o brownfield.
- Se ajusto `/apos-status` para retomar/diagnosticar estado sin escribir por defecto.
- Se mantuvo `/guardar` como persistencia de sesion.

### Archivos modificados
- `.agents/skills/apos/SKILL.md`
- `.agents/skills/apos-status/SKILL.md`
- `.agents/skills/guardar/SKILL.md`

### Resultados
- `.agents/skills` contiene exactamente 3 skills.
- Los tres `SKILL.md` tienen frontmatter valido.

### Advertencias metodologicas
- La sesion actual puede no recargar skills dinamicamente; en un chat nuevo del proyecto deberian aparecer como repo-local skills.

## 2026-05-02 00:00 - Export liviano del piloto productivo

### Objetivo
Preparar un paquete liviano, trazable y sincronizable por Git del piloto productivo terminado 5/5 OK.

### Acciones
- Se audito `data/production_status.json`.
- Se reviso el log `data/production_20260430_1758.log`.
- Se consulto `data/results.sqlite`, tabla `results`, filas `prod_pilot_%`.
- Se revisaron carpetas `data/processed/prod_pilot_*`.
- Se creo `exports/pilot_productivo_20260501/`.
- Se genero `pilot_summary.csv` con una fila por caso.
- Se genero `pilot_summary.md` con interpretacion corta.
- Se copio matriz, status final y tail de log.
- Se incluyeron solo `Run.csv` y `RunPARTs.csv` por caso como metricas procesadas livianas.
- Se ajusto `.gitignore` para ignorar `data/processed/`, status/logs vivos y permitir `exports/**`.

### Archivos revisados
- `data/production_status.json`
- `data/production_20260430_1758.log`
- `data/results.sqlite`
- `config/pilot_productivo_20260430.csv`
- `scripts/run_production.py`
- `src/main_orchestrator.py`
- `.gitignore`

### Archivos modificados
- `.gitignore`
- `.apos/STATUS.md`
- `.apos/HANDOFF.md`
- `.apos/PLAN.md`
- `.apos/JOURNAL.md`

### Archivos creados
- `exports/pilot_productivo_20260501/README.md`
- `exports/pilot_productivo_20260501/pilot_summary.csv`
- `exports/pilot_productivo_20260501/pilot_summary.md`
- `exports/pilot_productivo_20260501/production_status.json`
- `exports/pilot_productivo_20260501/production_log_tail.txt`
- `exports/pilot_productivo_20260501/processed_inventory.csv`
- `exports/pilot_productivo_20260501/source_manifest.csv`
- `exports/pilot_productivo_20260501/processed_run_metrics/*.csv`

### Resultados
- Export de 18 archivos, ~55 KB.
- Piloto operativo: 5/5 OK, 0 fallos numericos, 22.11 h.
- Clases fisicas por `displacement_only`: 3 FALLO, 2 ESTABLE.

### Proximos pasos
- Revisar cientificamente el piloto.
- Disenar siguiente batch con matriz explicita.
- Ejecutar dry-run antes de cualquier nueva simulacion.

### Advertencias metodologicas
- No lanzar campana grande todavia.
- No versionar `data/processed/` crudo ni `cases/`.
- La rotacion sigue siendo diagnostica, no criterio primario.

## 2026-05-03 18:38 - Lanzamiento batch2 productivo chico

### Objetivo
Ejecutar un lote chico de 8 casos para refinar frontera cerca de `mu≈0.6806`, explorar sensibilidad hidraulica moderada y verificar la rama `slope_inv=10` sin lanzar campana grande.

### Acciones
- Se verifico que no habia `DualSPHysics`, `GenCase` ni `python` corriendo.
- Se creo `config/batch2_productivo_20260503.csv`.
- Se ejecuto APOS preflight.
- Se ejecuto APOS matrix dry-run.
- Se ejecuto dry-run real de `scripts/run_production.py`.
- Se lanzo el batch real en background con `Start-Process`.

### Archivos revisados
- `.apos/STATUS.md`
- `data/production_status.json`
- `scripts/run_production.py`
- `src/main_orchestrator.py`

### Archivos modificados
- `config/batch2_productivo_20260503.csv`
- `.apos/STATUS.md`
- `.apos/HANDOFF.md`
- `.apos/PLAN.md`
- `.apos/JOURNAL.md`

### Comandos importantes
```text
python apos-system\harness\apos-run.py preflight --cmd "python scripts\run_production.py --prod --matrix config\batch2_productivo_20260503.csv --max-cases 8 --dry-run --no-notify"
python apos-system\harness\apos-run.py dry-run --matrix config\batch2_productivo_20260503.csv --max-cases 8
python scripts\run_production.py --prod --matrix config\batch2_productivo_20260503.csv --max-cases 8 --dry-run --no-notify
Start-Process python scripts\run_production.py --prod --matrix config\batch2_productivo_20260503.csv --max-cases 8 --no-notify
```

### Resultados
- Dry-run listo: 8/8 casos, `dp=0.003`, `classification_mode=displacement_only`, `reference_time_s=0.5`.
- Batch real lanzado.
- `data/production_status.json` reporta `total_cases=8`, `progress=1/8`, `current_case=batch2_base_mu0675`.
- Procesos activos observados: `python` y `DualSPHysics5.4_win64`.

### Proximos pasos
- Monitorear hasta completar o fallar.
- Al terminar, generar export liviano batch2.
- No lanzar nuevas simulaciones encima.

### Advertencias metodologicas
- Este lote no es campana grande ni active learning todavia.
- Mantener rotacion como diagnostico.
- Fallo numerico no equivale a fallo fisico.

## 2026-05-06 00:00 - Cierre y export liviano batch2

### Objetivo
Auditar el fin del lote batch2, crear un export liviano trazable y actualizar APOS para continuar sin depender del chat.

### Acciones
- Se verifico `data/production_status.json`.
- Se verifico que no habia procesos `DualSPHysics`, `GenCase` ni `python` corriendo.
- Se reviso el tail de `data/production_20260503_1838.log`.
- Se leyeron resultados batch2 desde `data/results.sqlite`.
- Se inventariaron carpetas `data/processed/batch2_*`.
- Se creo `exports/batch2_productivo_20260505/`.
- Se actualizo APOS vivo: `STATUS`, `HANDOFF`, `PLAN`, `INDEX`, `RISKS`.

### Archivos revisados
- `data/production_status.json`
- `data/production_20260503_1838.log`
- `data/results.sqlite`
- `data/processed/batch2_*`
- `config/batch2_productivo_20260503.csv`

### Archivos modificados
- `.apos/STATUS.md`
- `.apos/HANDOFF.md`
- `.apos/PLAN.md`
- `.apos/INDEX.md`
- `.apos/RISKS.md`
- `.apos/JOURNAL.md`

### Archivos creados
- `exports/batch2_productivo_20260505/README.md`
- `exports/batch2_productivo_20260505/batch2_summary.csv`
- `exports/batch2_productivo_20260505/batch2_summary.md`
- `exports/batch2_productivo_20260505/production_status.json`
- `exports/batch2_productivo_20260505/production_log_tail.txt`
- `exports/batch2_productivo_20260505/processed_inventory.csv`
- `exports/batch2_productivo_20260505/source_manifest.csv`
- `exports/batch2_productivo_20260505/processed_run_metrics/*.csv`

### Resultados
- Batch2 termino `completed`, 8/8 OK, 0 fallos numericos, 34.55 h.
- Export de 24 archivos, ~69 KB.
- Clases por `displacement_only`: 3 FALLO y 5 ESTABLE.
- Frontera base reforzada: `H=0.20`, `slope=1:20`, FALLO en `mu=0.675`, ESTABLE en `mu=0.685` y `mu=0.700`.
- Hidraulica fuerte `H=0.225` fallo en `mu=0.680` y `mu=0.720`.
- `slope=1:10` fue estable por desplazamiento en `mu=0.600` y `mu=0.650`, con rotacion diagnostica.

### Proximos pasos
- Auditar cientificamente piloto + batch2.
- Decidir mini-batch dirigido o primer surrogate exploratorio.
- No lanzar campana grande sin matriz revisada, dry-run y limite explicito.

### Advertencias metodologicas
- Batch2 no es campana parametrica completa.
- La rotacion sigue siendo diagnostica, no criterio primario.
- No versionar outputs crudos pesados.

## 2026-05-06 00:00 - Sincronizacion WS a Git

### Objetivo
Transferir al PC local por Git el estado versionable de la WS, incluyendo codigo, APOS, docs, configs, resultados livianos, exports y tablas de convergencia/batch2.

### Acciones
- Se audito `git status`, remoto y rama actual.
- Se detecto que un `git add -A` inicial intentaria versionar ~11 GB, incluyendo blobs crudos de DualSPHysics de hasta ~2.1 GB.
- Se actualizo `.gitignore` para permitir exports livianos pero excluir binarios crudos dentro de `exports/`.
- Se excluyeron artefactos temporales contaminados: `CODEX_START_HERE.md` y `codex_context_sph.zip`.
- Se verifico que el paquete versionable quedaba en ~492 MB y sin archivos >50 MB.
- Se hizo commit y push a `origin/master`.

### Archivos modificados
- `.gitignore`
- `.apos/STATUS.md`
- `.apos/HANDOFF.md`
- `.apos/JOURNAL.md`
- multiples archivos versionables de codigo, docs, configs, resultados, exports y figuras.

### Comandos importantes
```text
git add -A
git commit -m "Sync WS thesis results and batch2 export"
git push origin master
```

### Resultados
- Commit creado: `646c567 Sync WS thesis results and batch2 export`.
- Push exitoso: `master -> origin/master`.
- Estado posterior: `master...origin/master` sin diferencias.

### Proximos pasos
- En el PC local: `git pull origin master`.
- Luego auditar `exports/batch2_productivo_20260505/batch2_summary.csv`.

### Advertencias metodologicas
- No se subieron binarios crudos pesados (`*.bi4`, `*.ibi4`, VTK, `Part*`, `*_out/`).
- Para traer absolutamente los crudos, usar disco externo, storage separado o Git LFS configurado deliberadamente.

## 2026-05-07 19:33 - Lanzamiento batch3 productivo dirigido

### Objetivo
Lanzar un lote productivo dirigido de 10 casos con `dp=0.003` para mejorar el mapa local de estabilidad sin abrir una campana grande ni volver a convergencia.

### Acciones
- Se verifico que no habia procesos `DualSPHysics`, `GenCase` ni runners `python` activos.
- Se reviso `git status` sin limpiar ni revertir nada.
- Se confirmo que `scripts/run_production.py` acepta `--matrix`, `--max-cases`, `--dry-run` y `--no-notify`.
- Se confirmo que `src/main_orchestrator.py` usa `PRODUCTION_CLASSIFICATION_MODE="displacement_only"` y `PRODUCTION_REFERENCE_TIME_S=0.5`.
- Se confirmo `config/dsph_config.json`: `dp_prod=0.003`.
- Se creo `config/batch3_productivo.csv` con 10 casos.
- Se ejecuto dry-run obligatorio.
- Se lanzo batch3 real en background.
- Se actualizo APOS vivo para reflejar batch3 corriendo.

### Archivos revisados
- `.apos/BOOTSTRAP.md`
- `.agents/skills/guardar/SKILL.md`
- `scripts/run_production.py`
- `src/main_orchestrator.py`
- `config/dsph_config.json`
- `data/production_status.json`

### Archivos modificados
- `config/batch3_productivo.csv`
- `.apos/STATUS.md`
- `.apos/HANDOFF.md`
- `.apos/PLAN.md`
- `.apos/RISKS.md`
- `.apos/JOURNAL.md`

### Comandos importantes
```text
python scripts\run_production.py --prod --matrix config\batch3_productivo.csv --max-cases 10 --dry-run --no-notify
python scripts\run_production.py --prod --matrix config\batch3_productivo.csv --max-cases 10 --no-notify
```

### Resultados
- Dry-run correcto: 10 casos, `dp=0.003`, `classification_mode=displacement_only`, `reference_time_s=0.5`.
- Batch3 real lanzado el 2026-05-07 19:33 aprox.
- `data/production_status.json`: `phase=production`, `total_cases=10`, `completed=0`, `failed=0`, `current_case=batch3_base_mu0678`, `progress=1/10`.
- Procesos activos: `python.exe` runner y `DualSPHysics5.4_win64.exe`.
- Log productivo: `data/production_20260507_1933.log`.

### Proximos pasos
- Monitorear batch3 hasta completar o fallar.
- Al terminar, generar export liviano `exports/batch3_productivo_YYYYMMDD/`.
- No lanzar otra tanda encima.

### Advertencias metodologicas
- Batch3 es produccion dirigida, no convergencia.
- No cambiar `dp`, criterio ni referencia temporal durante el lote.
- La rotacion sigue siendo diagnostica.

## 2026-05-09 13:55 - Cierre y export liviano batch3

### Objetivo
Registrar el cierre de batch3 productivo dirigido y preparar datos livianos para sincronizar con la IA/local via Git.

### Acciones
- Se verifico `data/production_status.json`: `phase=completed`, `completed=10`, `failed=0`, tiempo total 42.03 h.
- Se reviso `data/production_20260507_1933.log` y los directorios `data/processed/batch3_*`.
- Se extrajeron metricas desde `data/results.sqlite` y `Run.csv`.
- Se creo `exports/batch3_productivo_20260509/` siguiendo el patron de piloto y batch2.
- Se actualizaron `STATUS.md`, `HANDOFF.md` y `PLAN.md` para reflejar que batch3 ya termino.

### Archivos revisados
- `data/production_status.json`
- `data/production_20260507_1933.log`
- `data/results.sqlite`
- `data/processed/batch3_*`
- `config/batch3_productivo.csv`

### Archivos modificados
- `.apos/STATUS.md`
- `.apos/HANDOFF.md`
- `.apos/PLAN.md`
- `.apos/JOURNAL.md`

### Archivos creados
- `exports/batch3_productivo_20260509/README.md`
- `exports/batch3_productivo_20260509/batch3_summary.csv`
- `exports/batch3_productivo_20260509/batch3_summary.md`
- `exports/batch3_productivo_20260509/production_status.json`
- `exports/batch3_productivo_20260509/production_log_tail.txt`
- `exports/batch3_productivo_20260509/processed_inventory.csv`
- `exports/batch3_productivo_20260509/source_manifest.csv`
- `exports/batch3_productivo_20260509/processed_run_metrics/*`

### Resultados
- Batch3: 10/10 OK, 0 fallos numericos.
- Clasificacion por desplazamiento: 6 FALLO, 4 ESTABLE.
- Base `H=0.20`, `slope=1:20`: FALLO en `mu=0.678` y `0.680`; ESTABLE en `mu=0.682`.
- `H=0.175`: estable en todos los puntos corridos (`mu=0.600`, `0.640`, `0.660`).
- `H=0.210` y `H=0.225`: fallan en los puntos corridos, incluso con fricciones altas.

### Proximos pasos
- Hacer commit/push de export liviano y APOS actualizado.
- En la IA/local, auditar piloto + batch2 + batch3 juntos antes de disenar otro lote.

### Advertencias metodologicas
- Batch3 no es convergencia ni mapa completo de fragilidad.
- No afirmar convergencia asintotica fuerte.
- La rotacion se mantiene como diagnostico, no como criterio primario.

## 2026-05-13 - Export liviano batch4 mass probe

### Objetivo
Preparar resultados batch4 de la WS para sincronizacion por Git hacia la laptop principal, sin incluir binarios ni outputs pesados.

### Acciones
- Se verifico `data/production_status.json`: batch4 quedo con `completed=11`, `failed=0`, `progress=12/12`.
- Se confirmo que no habia procesos `DualSPHysics`, `GenCase` ni `python` productivos activos.
- Se audito `data/production_20260510_2054.log`.
- Se extrajeron 11 casos oficiales desde `data/results.sqlite`.
- Se detecto que `batch4_mass_m125_H0225_mu0860` no fue guardado en `data/processed` ni SQLite.
- Se revisaron CSVs crudos del caso 12 en `cases/batch4_mass_m125_H0225_mu0860/..._out`.
- Se genero recuperacion parcial del caso 12 desde CSVs crudos, marcandola como diagnostica/no oficial.
- Se creo `exports/batch4_mass_probe_20260513/`.

### Archivos revisados
- `data/production_status.json`
- `data/production_20260510_2054.log`
- `data/results.sqlite`
- `config/batch4_mass_probe_20260510.csv`
- `config/batch4_precheck_mass_sanity_20260510.csv`
- `cases/batch4_mass_m125_H0225_mu0860/batch4_mass_m125_H0225_mu0860_out/ChronoExchange_mkbound_51.csv`

### Archivos creados
- `exports/batch4_mass_probe_20260513/README.md`
- `exports/batch4_mass_probe_20260513/batch4_summary.csv`
- `exports/batch4_mass_probe_20260513/batch4_summary.md`
- `exports/batch4_mass_probe_20260513/batch4_precheck_summary.csv`
- `exports/batch4_mass_probe_20260513/batch4_case12_partial_recovery.csv`
- `exports/batch4_mass_probe_20260513/results_sqlite_batch4_extract_plus_partial.csv`
- `exports/batch4_mass_probe_20260513/production_status.json`
- `exports/batch4_mass_probe_20260513/production_log_tail.txt`
- `exports/batch4_mass_probe_20260513/processed_inventory.csv`
- `exports/batch4_mass_probe_20260513/source_manifest.csv`
- `exports/batch4_mass_probe_20260513/processed_run_metrics/*`

### Resultados
- Batch4 oficial: 11/12 casos postprocesados.
- Conteo oficial: 5 FALLO y 6 ESTABLE por `displacement_only`.
- Caso parcial recuperado: `batch4_mass_m125_H0225_mu0860`, `sim_time_reached` ~9.506 s, marcado `PARTIAL_RECOVERED_NOT_SQLITE`.
- Precheck masa/contacto: 2/2 OK.
- Export liviano: 39 archivos, ~85 KB.

### Proximos pasos
- Commit y push de export batch4 + configs + APOS actualizado.
- En laptop principal, `git pull` y auditar batch4 antes de entrenar surrogate o lanzar nuevos lotes.
- Decidir si repetir/reprocesar oficialmente el caso 12 parcial.

### Advertencias metodologicas
- No mezclar el caso 12 parcial con resultados oficiales sin conservar `quality_flags`.
- Batch4 es lote dirigido de masa, no campana completa.
- Mantener `dp=0.003` como resolucion operativa y rotacion como diagnostico.

## 2026-05-13 09:45 - Lanzamiento AL batch1 hibrido en WS

### Objetivo
Sincronizar la WS con Git y lanzar el siguiente lote productivo corto `AL batch1 hibrido`, no convergencia ni sensibilidad de forma.

### Acciones
- Se hizo `git fetch` y `git pull --ff-only origin master`.
- Se incorporo el commit remoto `0e97767 Prepare hybrid AL batch1 handoff`.
- Se leyo `docs/PROMPT_WS_AL_BATCH1_HYBRID_20260513.md`.
- Se verifico que no hubiera procesos `DualSPHysics`, `GenCase` ni `python` productivos activos.
- Se verifico `exports/batch4_mass_probe_20260513/batch4_summary.csv`.
- Se ejecuto dry-run con `--prod`, matriz explicita y `--max-cases 8`.
- Se lanzo el lote real sin `--no-notify` para usar ntfy nativo.

### Archivos revisados
- `config/al_batch1_hybrid_20260513.csv`
- `docs/PROMPT_WS_AL_BATCH1_HYBRID_20260513.md`
- `data/analysis/batch4_postprocess_20260513/AL_BATCH1_HYBRID_RATIONALE_20260513.md`
- `exports/batch4_mass_probe_20260513/batch4_summary.csv`
- `scripts/run_production.py`

### Comandos importantes
```text
git pull --ff-only origin master
python scripts\run_production.py --prod --matrix config\al_batch1_hybrid_20260513.csv --max-cases 8 --dry-run --no-notify
python scripts\run_production.py --prod --matrix config\al_batch1_hybrid_20260513.csv --max-cases 8
```

### Resultados
- Dry-run correcto: 8 casos, `dp=0.003`, `classification_mode=displacement_only`, `reference_time_s=0.5`.
- Lote real lanzado el 2026-05-13 09:41.
- Estado inicial: `phase=production`, `current_case=al1_lowH_m085_mu0620`, `progress=1/8`.
- Procesos activos al lanzamiento: `python.exe` runner y `DualSPHysics5.4_win64.exe`.
- El log `data/production_20260513_0941.log` registra ntfy nativo: `PRODUCCION INICIADA` e `INICIO CASO 1/8`.

### Proximos pasos
- Monitorear hasta completar o fallar.
- Al terminar, crear export liviano `exports/al_batch1_hybrid_YYYYMMDD/`.
- No lanzar otro lote encima.

### Advertencias metodologicas
- AL batch1 es lote dirigido por GP seed + brackets fisicos; no es validacion de `dp`.
- No relanzar aun el caso parcial batch4 salvo decision explicita.
- Mantener `dp=0.003`, geometria base y `displacement_only`.

## 2026-05-10 12:58 - Reconciliacion Git/local y unificacion APOS

### Objetivo
Volver a dejar `C:\Seba\Tesis` como unico repo canonico, actualizado con la data WS/GitHub, sin perder data local de laptop ni dejar APOS dividido.

### Acciones
- Se creo el goal de reconciliacion del repo.
- Se verifico que la carpeta temporal `C:\Seba\Tesis_origin_master_clean_20260510_123639` era solo un worktree de rescate.
- Se creo backup externo en `C:\Seba\workspace_backups\tesis-reconcile-20260510_125339`.
- Se respaldaron cambios trackeados, listas de no trackeados, ignorados, conflictos y APOS.
- Se detectaron 8 archivos no trackeados que chocaban con archivos nuevos de `origin/master`.
- Esos 8 archivos se movieron a `.apos/cache/git-untracked-conflicts-20260510_125339/` y tambien quedaron respaldados externamente.
- Se guardaron cambios trackeados previos en `stash@{0}`.
- Se actualizo `C:\Seba\Tesis` por fast-forward a `origin/master`, commit `3c443e9`.
- Se documento la politica de origen de datos en `docs/DATA_ORIGIN_POLICY.md`.
- Se actualizo APOS vivo en `C:\Seba\Tesis`.

### Archivos revisados
- `.apos/STATUS.md`
- `.apos/HANDOFF.md`
- `.apos/PLAN.md`
- `.apos/INDEX.md`
- `.apos/RISKS.md`
- `.apos/JOURNAL.md`
- `exports/batch3_productivo_20260509/batch3_summary.md`
- `data/geometry/bloques_b02_20260510/ANALISIS_BLOQUES_STL_20260510.md`

### Archivos modificados
- `.gitignore`
- `.apos/STATUS.md`
- `.apos/HANDOFF.md`
- `.apos/PLAN.md`
- `.apos/INDEX.md`
- `.apos/RISKS.md`
- `.apos/JOURNAL.md`
- `.apos/DECISIONS.md`
- `docs/DATA_ORIGIN_POLICY.md`

### Comandos importantes
```text
git stash push -m "pre-reconcile tracked changes 20260510_125339"
git merge --ff-only origin/master
```

### Resultados
- `C:\Seba\Tesis` queda como repo canonico unico.
- APOS ya no debe tomarse desde el worktree temporal.
- Los datos WS/GitHub quedan representados por exports livianos y commit.
- Los datos laptop/local quedan separados por politica de origen y versionado selectivo.

### Proximos pasos
- Committear APOS, politica de origen, verificacion local y analisis de bloques.
- Retirar el worktree temporal cuando el commit este listo.
- Revisar cientificamente piloto + batch2 + batch3.

### Advertencias metodologicas
- No aplicar `stash@{0}` completo.
- No borrar crudos locales ni backups.
- No lanzar otro batch antes de la lectura cientifica conjunta.

## 2026-05-10 13:25 - Cierre de reconciliacion local

### Objetivo
Dejar el repo local listo para continuar sin APOS duplicado y con separacion clara entre datos WS/GitHub y datos laptop/local.

### Acciones
- Se confirmo que `C:\Seba\Tesis` es una junction hacia `C:\Users\kevin\projects\Tesis`.
- Se documento esa junction en `docs/DATA_ORIGIN_POLICY.md`, `STATUS.md` y `HANDOFF.md`.
- Se decidio simplificar el runtime APOS de tesis a `.apos/` + `/apos`, `/guardar`, `/apos-status`.
- Se dejo `apos-system/` como herramienta/historial parcial, no como segundo APOS vivo.
- Se filtro el ruido local en `.gitignore` y `.git/info/exclude` sin borrar archivos.
- Se preparo para commit el set liviano: APOS, politica de origen, verificacion preproduccion, web de convergencia, benchmark, comparacion analitica, STL b02 y analisis geometrico.

### Archivos revisados
- `.gitignore`
- `.git/info/exclude`
- `docs/DATA_ORIGIN_POLICY.md`
- `.apos/STATUS.md`
- `.apos/HANDOFF.md`
- `.apos/PLAN.md`
- `.apos/INDEX.md`
- `.apos/RISKS.md`
- `.apos/SOURCES.md`
- `.apos/DECISIONS.md`

### Archivos modificados
- `.apos/DECISIONS.md`
- `.apos/HANDOFF.md`
- `.apos/INDEX.md`
- `.apos/JOURNAL.md`
- `.apos/PLAN.md`
- `.apos/RISKS.md`
- `.apos/SOURCES.md`
- `.apos/STATUS.md`
- `.gitignore`
- `.git/info/exclude`
- `docs/DATA_ORIGIN_POLICY.md`
- `.apos/evidence/repo-cleanup-20260510_123543/REPO_CLEANUP_REPORT.md`

### Comandos importantes
```text
git status -sb --untracked-files=all
git ls-files --others --exclude-standard
git add -A
git diff --cached --stat
git diff --cached --name-only | Select-String -Pattern '\.(bi4|ibi4|vtk|vtp|zip)$|_out/|Part'
```

### Resultados
- No se stagearon crudos pesados tipo `.bi4`, `.ibi4`, VTK, `Part*`, zip ni carpetas `*_out/`.
- El set versionable nuevo pesa aproximadamente 5.5 MB.
- El backup externo de seguridad sigue disponible en `C:\Seba\workspace_backups\tesis-reconcile-20260510_125339`.
- Se creo el commit local de reconciliacion, luego amendido para registrar el retiro del worktree temporal.
- Se retiro el worktree temporal `C:\Seba\Tesis_origin_master_clean_20260510_123639` luego de respaldar su `.apos`.
- El commit final de reconciliacion quedo como `0e98b65` y fue pusheado a `origin/master`.

### Errores / bloqueos
- `git diff --cached --check` reporta whitespace en SVG/artefactos generados; no afecta ejecucion ni trazabilidad.

### Proximos pasos
- En la siguiente sesion, analizar piloto + batch2 + batch3 para decidir surrogate o mini-batch.

### Advertencias metodologicas
- No interpretar `apos-system/` como APOS vivo del proyecto.
- No usar backups/worktrees temporales como fuente diaria.
- No aplicar el stash completo salvo necesidad puntual.
