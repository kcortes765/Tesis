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

## 2026-05-14 20:20 - Export liviano AL batch1 hybrid

### Objetivo
Preparar y subir por Git el resultado liviano del lote `al_batch1_hybrid` para sincronizarlo con la laptop sin copiar binarios ni salidas crudas pesadas.

### Acciones
- Se verifico que no quedaran procesos `DualSPHysics`, `GenCase` o `python` productivos activos.
- Se leyo `data/production_status.json` y se confirmo `completed=8`, `failed=0`, `progress=8/8`.
- Se contrastaron los resultados oficiales en `data/results.sqlite` para los casos `al1_*`.
- Se creo el export liviano `exports/al_batch1_hybrid_20260514/`.
- Se copiaron solo archivos trazables y livianos: resumen CSV/MD, status JSON, tail del log, matriz, extract SQLite e inventario.
- Se actualizaron `STATUS.md`, `HANDOFF.md`, `PLAN.md` e `INDEX.md` para reflejar que AL batch1 termino.

### Archivos revisados
- `data/production_status.json`
- `data/production_20260513_0941.log`
- `data/results.sqlite`
- `config/al_batch1_hybrid_20260513.csv`
- `data/processed/al1_*`

### Archivos modificados
- `.apos/STATUS.md`
- `.apos/HANDOFF.md`
- `.apos/PLAN.md`
- `.apos/INDEX.md`
- `.apos/JOURNAL.md`
- `data/results.sqlite`
- `exports/al_batch1_hybrid_20260514/`

### Comandos importantes
```text
Get-Process | Where-Object { $_.ProcessName -match "DualSPHysics|GenCase|python" }
Get-Content data\production_status.json
python - <<sqlite/extract>>
git status -sb
```

### Resultados
- AL batch1 termino oficialmente 8/8 OK.
- No hubo fallos numericos.
- Tiempo total reportado: 34.37 h.
- Resultado fisico por criterio `displacement_only`: 7 ESTABLE y 1 FALLO.
- Caso fallido: `al1_base_m085_mu0780`.
- El export liviano contiene 25 archivos y pesa aproximadamente 58 KB.
- No se incluyeron `cases/`, `data/processed/` completos, `*_out/`, `Part*`, `.bi4`, `.ibi4`, VTK ni binarios pesados.

### Errores / bloqueos
- Sin bloqueos para sincronizacion por Git.

### Proximos pasos
- Hacer `git pull` en la laptop.
- Revisar `exports/al_batch1_hybrid_20260514/al_batch1_summary.md`.
- Analizar piloto + batch2 + batch3 + batch4 + AL1 antes de lanzar otro lote.

### Advertencias metodologicas
- AL batch1 es un lote dirigido, no una grilla completa del dominio.
- No lanzar nuevas simulaciones hasta revisar el efecto conjunto de H, mu y masa.
- La frontera sigue condicionada a `dp=0.003` como resolucion operativa.

## 2026-05-14 20:35 - Lanzamiento AL batch2 bracket-closing

### Objetivo
Lanzar un lote dirigido de 10 casos para cerrar brackets posteriores a AL batch1, manteniendo la metodologia productiva fija: `dp=0.003`, `classification_mode=displacement_only`, `reference_time_s=0.5`, rotacion diagnostica.

### Acciones
- Se verifico que no hubiera procesos `DualSPHysics`, `GenCase` o `python` productivos activos antes de lanzar.
- Se reviso `git status -sb` de forma informativa; el repo estaba alineado con `origin/master`.
- Se confirmo que `scripts/run_production.py` existe y acepta `--prod`, `--matrix`, `--max-cases` y `--dry-run`.
- Se creo `config/al_batch2_bracket_closing_20260514.csv` con exactamente 10 casos.
- Se ejecuto dry-run con `--prod` y matriz explicita.
- El dry-run confirmo 10 casos, `dp=0.003`, `classification_mode=displacement_only`, `reference_time_s=0.5` y rutas previstas.
- Se lanzo AL batch2 real en segundo plano para no bloquear la sesion.
- Se confirmo que `GenCase` paso y que `DualSPHysics5.4_win64` inicio el caso 1/10.
- Se actualizaron `STATUS.md`, `HANDOFF.md`, `PLAN.md` y `RISKS.md`.

### Archivos revisados
- `scripts/run_production.py`
- `data/production_status.json`
- `data/production_20260514_2030.log`
- `.apos/STATUS.md`
- `.apos/HANDOFF.md`
- `.apos/PLAN.md`
- `.apos/RISKS.md`

### Archivos modificados
- `config/al_batch2_bracket_closing_20260514.csv`
- `.apos/STATUS.md`
- `.apos/HANDOFF.md`
- `.apos/PLAN.md`
- `.apos/RISKS.md`
- `.apos/JOURNAL.md`

### Comandos importantes
```text
python scripts\run_production.py --prod --matrix config\al_batch2_bracket_closing_20260514.csv --max-cases 10 --dry-run
python scripts\run_production.py --prod --matrix config\al_batch2_bracket_closing_20260514.csv --max-cases 10
Get-Content data\production_status.json
Get-Content data\production_20260514_2030.log -Tail 120
```

### Resultados
- Dry-run correcto.
- AL batch2 lanzado el 2026-05-14 20:30.
- Estado inicial: `phase=production`, `total_cases=10`, `current_case=al2_lowH_m085_mu0585`, `progress=1/10`.
- Procesos activos al chequeo inicial: `python` PID 8356 y `DualSPHysics5.4_win64` PID 20088.
- ntfy nativo activo: log registra `PRODUCCION INICIADA` e `INICIO CASO 1/10`.

### Errores / bloqueos
- Sin errores de preflight ni dry-run.
- Una consulta de PowerShell con `Get-ChildItem -Filter` usando lista de filtros fallo, pero no afecto la corrida ni archivos.

### Proximos pasos
- Monitorear `data/production_status.json`.
- Al terminar, crear export liviano `exports/al_batch2_bracket_closing_YYYYMMDD/`.
- Subir por Git matriz, export y APOS actualizado.

### Advertencias metodologicas
- AL batch2 es lote dirigido para cerrar brackets, no campana completa.
- No lanzar otro lote mientras AL batch2 este activo.
- Si un caso falla numericamente, no relanzar automaticamente sin diagnostico.

## 2026-05-14 23:35 - Pulido visual cientifico y storytelling

### Objetivo
Elevar las figuras de convergencia y produccion/active learning a un estandar de tesis/paper: doble lectura porcentual-absoluta, legibilidad, color accesible, narrativa por capas y uso de todos los datos oficiales utiles hasta la fecha.

### Acciones
- Se reviso el estado de AL2: sigue activo y sin export oficial, por lo que no se incorporo a figuras finales.
- Se investigaron referencias de visualizacion cientifica, uso de color y storytelling visual.
- Se creo `scripts/generate_production_story_graphics.py`.
- Se genero `data/figures/production_story_graphics/` con master CSV, indice y 8 figuras PNG/SVG.
- Se dejo documentada la guia visual en `docs/VISUAL_STORYTELLING_Q1_TESIS_20260514.md`.
- Se verifico que los scripts principales compilen con `python -m py_compile`.
- Se actualizaron `STATUS.md`, `HANDOFF.md` y `PLAN.md`.

### Archivos revisados
- `.apos/STATUS.md`
- `.apos/HANDOFF.md`
- `.apos/PLAN.md`
- `exports/pilot_productivo_20260501/pilot_summary.csv`
- `exports/batch2_productivo_20260505/batch2_summary.csv`
- `exports/batch3_productivo_20260509/batch3_summary.csv`
- `exports/batch4_mass_probe_20260513/batch4_summary.csv`
- `exports/al_batch1_hybrid_20260514/al_batch1_summary.csv`

### Archivos modificados
- `scripts/generate_production_story_graphics.py`
- `data/figures/production_story_graphics/`
- `docs/VISUAL_STORYTELLING_Q1_TESIS_20260514.md`
- `.apos/STATUS.md`
- `.apos/HANDOFF.md`
- `.apos/PLAN.md`
- `.apos/JOURNAL.md`
- `.apos/SOURCES.md`

### Comandos importantes
```text
python scripts\generate_production_story_graphics.py
python -m py_compile scripts\generate_production_story_graphics.py scripts\generate_convergence_graphics.py scripts\summarize_preproduction_verification_20260508.py
```

### Resultados
- `master_production_story.csv` contiene 43 filas: piloto, batch2, batch3, batch4 y AL1.
- El caso parcial de batch4 queda incluido en el maestro como no oficial, no como evidencia principal.
- Se generaron 8 figuras productivas en PNG/SVG.
- Toda figura con desplazamiento normalizado incluye equivalente absoluto en mm o marca de escala.
- Los outliers extremos se marcan como fuera de escala para preservar legibilidad sin ocultar su existencia.

### Errores / bloqueos
- No se incorporo AL2 porque aun esta corriendo y no tiene export oficial.

### Proximos pasos
- Revisar visualmente set de figuras productivas y seleccionar las esenciales para tesis/PPT.
- Regenerar `production_story_graphics` cuando AL2 termine y exista export liviano.
- Despues de AL2, entrenar surrogate exploratorio o disenar siguiente lote con base en margen continuo.

### Advertencias metodologicas
- Las figuras productivas representan frontera operacional a `dp=0.003`, no convergencia universal.
- Las lineas entre puntos son guias visuales, no interpolacion formal.
- La rotacion sigue siendo diagnostico, no criterio primario.

## 2026-05-16 17:30 - AL2 completado y exportado

### Objetivo
Sincronizar a laptop los resultados livianos de AL batch2 y bloquear el reentrenamiento GP automatico.

### Acciones
- Verificado data/production_status.json: AL2 completed=10, ailed=0, phase=completed.
- Creado export liviano exports/al_batch2_bracket_closing_20260516/.
- Extraida tabla oficial desde data/results.sqlite a l_batch2_summary.csv.
- Actualizado APOS: STATUS, HANDOFF y PLAN.
- Bloqueado reentrenamiento automatico en scripts/run_production.py; ahora requiere --retrain-gp.
- Modelo GP automatico retirado de data/gp_surrogate.pkl y dejado en cuarentena local ignorada.

### Archivos modificados
- .apos/STATUS.md
- .apos/HANDOFF.md
- .apos/PLAN.md
- .apos/JOURNAL.md
- exports/al_batch2_bracket_closing_20260516/
- data/results.sqlite

### Resultados
- AL2: 10/10 OK, 5 ESTABLE, 5 FALLO, 0 fallos numericos.
- Export liviano listo para Git/laptop.

### Advertencias metodologicas
- AL2 es cierre dirigido de brackets, no mapa global completo.
- Cualquier GP nuevo debe entrenarse deliberadamente con target y features revisados.

## 2026-05-16 17:56 - GP after-AL2, web post-convergencia y AL3 preparado

### Objetivo
Incorporar AL2 en la laptop, entrenar un GP deliberado para `[H, mu, m*]`, actualizar la web post-convergencia y dejar lista la matriz AL3 para la WS.

### Acciones
- Se entreno `scripts/train_gp_h_mu_mstar_20260516.py` con exports oficiales hasta AL2.
- Se genero `data/analysis/gp_h_mu_mstar_20260516/` con dataset, validacion LOO, candidatos y matriz AL3.
- Se guardo el modelo deliberado en `models/surrogates/gp_h_mu_mstar_after_al2_20260516.pkl`.
- Se actualizo `scripts/generate_production_story_graphics.py` para incluir AL2 y normalizar aliases de columnas.
- Se actualizo `docs/post_convergence_story_web/index.html` con AL2, GP after-AL2, incertidumbre y explicacion de `m*`.
- Se creo `config/al_batch3_gp_after_al2_20260516.csv`.
- Se creo `docs/PROMPT_WS_AL3_AFTER_AL2_20260516.md`.
- Se actualizaron `STATUS.md`, `HANDOFF.md` y `PLAN.md`.

### Archivos revisados
- `exports/al_batch2_bracket_closing_20260516/al_batch2_summary.csv`
- `scripts/generate_production_story_graphics.py`
- `scripts/build_post_convergence_story_web.py`
- `data/analysis/gp_h_mu_mstar_20260516/`

### Archivos modificados
- `.apos/STATUS.md`
- `.apos/HANDOFF.md`
- `.apos/PLAN.md`
- `.apos/JOURNAL.md`
- `scripts/generate_production_story_graphics.py`
- `scripts/build_post_convergence_story_web.py`
- `scripts/train_gp_h_mu_mstar_20260516.py`
- `data/analysis/gp_h_mu_mstar_20260516/`
- `models/surrogates/gp_h_mu_mstar_after_al2_20260516.pkl`
- `config/al_batch3_gp_after_al2_20260516.csv`
- `docs/PROMPT_WS_AL3_AFTER_AL2_20260516.md`
- `docs/post_convergence_story_web/`

### Comandos importantes
```text
python scripts\train_gp_h_mu_mstar_20260516.py
python scripts\generate_production_story_graphics.py
python scripts\build_post_convergence_story_web.py
```

### Resultados
- GP after-AL2: 48 casos usados, LOO accuracy 0.875, MAE 3.140% d_eq, RMSE 4.736% d_eq.
- AL3 recomendado: 8 casos en `config/al_batch3_gp_after_al2_20260516.csv`.
- Web post-convergencia regenerada con figuras observadas, GP, incertidumbre y validacion interna.

### Errores / bloqueos
- No se detectaron errores de ejecucion en los scripts.
- La validacion GP sigue siendo exploratoria; no reemplaza simulaciones SPH-Chrono.

### Proximos pasos
- Subir cambios a Git.
- Pedir a WS dry-run y ejecucion AL3.
- Cuando AL3 vuelva por Git, reentrenar GP en laptop y decidir AL4/holdout/checks finos.

### Advertencias metodologicas
- AL3 se basa en frontera/incertidumbre del GP after-AL2, no en una grilla factorial.
- La WS no debe usar `--retrain-gp`.
- `mu=0.900` en AL3 extiende levemente el rango previo para cerrar un bracket especifico.

## 2026-05-16 18:23 - Guardado de decision estrategica y mock de entregable final

### Objetivo
Guardar el cambio de enfoque discutido: usar la capacidad computacional disponible para un plan jerarquico mas ambicioso, y documentar como podria verse el entregable final de la tesis.

### Acciones
- Se genero `docs/mock_final_deliverable_20260516/` con datos sinteticos para visualizar el entregable final.
- Se creo `scripts/generate_mock_final_deliverable_20260516.py`.
- Se aclaro que el resultado final no seria solo una ecuacion o grafico, sino un paquete con estado limite, frontera, fragilidad condicional, validacion por capas y limites.
- Se discutio que pendiente, orientacion y forma si importan, pero no deben entrar como factorial completo simultaneo.
- Se acepto una estrategia jerarquica mas ambiciosa: base `[H, mu, m*]`, luego pendiente, orientacion y forma como extensiones controladas.
- Se actualizaron `STATUS.md`, `HANDOFF.md`, `PLAN.md`, `INDEX.md`, `RISKS.md`, `OPEN_QUESTIONS.md` y `DECISIONS.md`.

### Archivos revisados
- `.apos/STATUS.md`
- `.apos/HANDOFF.md`
- `.apos/PLAN.md`
- `.apos/RISKS.md`
- `.apos/OPEN_QUESTIONS.md`
- `docs/mock_final_deliverable_20260516/index.html`

### Archivos modificados
- `.apos/STATUS.md`
- `.apos/HANDOFF.md`
- `.apos/PLAN.md`
- `.apos/INDEX.md`
- `.apos/RISKS.md`
- `.apos/OPEN_QUESTIONS.md`
- `.apos/DECISIONS.md`
- `.apos/JOURNAL.md`
- `docs/mock_final_deliverable_20260516/`
- `scripts/generate_mock_final_deliverable_20260516.py`

### Comandos importantes
```text
python scripts\generate_mock_final_deliverable_20260516.py
python -m py_compile scripts\generate_mock_final_deliverable_20260516.py
```

### Resultados
- Mock sintetico disponible en `docs/mock_final_deliverable_20260516/index.html`.
- Decision `DEC-20260516-001` agregada.
- Queda definido que el plan de seis meses debe contemplar mas que el minimo: potencialmente 130-220 simulaciones adicionales si se incorporan pendiente, orientacion, forma y validacion.

### Errores / bloqueos
- Ninguno tecnico.

### Proximos pasos
- Ejecutar AL3 en WS.
- Al volver AL3, reentrenar GP after-AL3 y decidir AL4/holdout.
- Preparar plan cuantitativo de expansion jerarquica de variables.
- Analizar STL/formas antes de seleccionar geometria secundaria.

### Advertencias metodologicas
- El mock usa datos sinteticos y no debe citarse como resultado.
- La expansion de variables debe ser jerarquica para no perder interpretabilidad.

## 2026-05-18 15:15 - AL3 incorporado, GP after-AL3 y AL4 preparado

### Objetivo
Incorporar el export AL3 enviado desde la WS, analizar sus resultados, reentrenar localmente el GP y dejar preparado el siguiente lote AL4.

### Acciones
- Se hizo `git pull origin master` y se incorporo el commit remoto `0d40eec Add AL3 after-AL2 lightweight export`.
- Se reviso `exports/al_batch3_gp_after_al2_20260518/al_batch3_summary.md`.
- Se verifico que AL3 termino 8/8 OK, 0 fallos numericos, todos ESTABLE.
- Se creo `scripts/train_gp_h_mu_mstar_after_al3_20260518.py`.
- Se entreno el GP after-AL3 con exports oficiales hasta AL3.
- Se genero `data/analysis/gp_h_mu_mstar_after_al3_20260518/`.
- Se guardo el modelo deliberado en `models/surrogates/gp_h_mu_mstar_after_al3_20260518.pkl`.
- Se actualizo `scripts/generate_production_story_graphics.py` para incluir AL3.
- Se actualizo `scripts/build_post_convergence_story_web.py` para usar GP after-AL3.
- Se regenero `docs/post_convergence_story_web/` con AL3 y candidatos AL4.
- Se creo `config/al_batch4_after_al3_20260518.csv`.
- Se creo `docs/PROMPT_WS_AL4_AFTER_AL3_20260518.md`.
- Se actualizaron `STATUS.md`, `HANDOFF.md` y `PLAN.md`.

### Archivos revisados
- `exports/al_batch3_gp_after_al2_20260518/al_batch3_summary.md`
- `exports/al_batch3_gp_after_al2_20260518/al_batch3_summary.csv`
- `data/analysis/gp_h_mu_mstar_after_al3_20260518/README.md`
- `data/analysis/gp_h_mu_mstar_after_al3_20260518/brackets_by_h_mstar.csv`
- `data/analysis/gp_h_mu_mstar_after_al3_20260518/al4_candidates.csv`

### Archivos modificados
- `.apos/STATUS.md`
- `.apos/HANDOFF.md`
- `.apos/PLAN.md`
- `.apos/JOURNAL.md`
- `scripts/train_gp_h_mu_mstar_after_al3_20260518.py`
- `scripts/generate_production_story_graphics.py`
- `scripts/build_post_convergence_story_web.py`
- `data/analysis/gp_h_mu_mstar_after_al3_20260518/`
- `models/surrogates/gp_h_mu_mstar_after_al3_20260518.pkl`
- `config/al_batch4_after_al3_20260518.csv`
- `docs/PROMPT_WS_AL4_AFTER_AL3_20260518.md`
- `docs/post_convergence_story_web/`

### Comandos importantes
```text
git pull origin master
python scripts\train_gp_h_mu_mstar_after_al3_20260518.py
python scripts\generate_production_story_graphics.py
python scripts\build_post_convergence_story_web.py
```

### Resultados
- AL3: 8/8 ESTABLE; el punto mas cercano fue `al3_base_m085_mu0800` con `Dmax=4.85% d_eq`.
- GP after-AL3: 56 casos oficiales, 22 fallos, 34 estables.
- Validacion LOO: accuracy 0.857, MAE 2.866% d_eq, RMSE 4.485% d_eq.
- AL4 recomendado: 8 casos para cerrar brackets observados, sin expandir dominio.
- Web post-convergencia actualizada con 60 casos oficiales y 1 parcial documentado.

### Errores / bloqueos
- No hubo errores de ejecucion.
- La lectura de AL3 obliga a no expandir todavia a pendiente/orientacion/forma; primero conviene cerrar brackets AL4.

### Proximos pasos
- Commit y push de los cambios.
- Enviar prompt AL4 a WS.
- Cuando AL4 vuelva por Git, reentrenar GP after-AL4 y decidir holdout/AL5/checks finos.

### Advertencias metodologicas
- AL3 no fue un fracaso por ser todo estable; cerro el lado estable de los brackets.
- AL4 baja `mu` dentro de brackets conocidos para buscar mezcla ESTABLE/FALLO.
- El GP guia el diseno; la evidencia principal siguen siendo las simulaciones SPH-Chrono.

## 2026-05-20 03:30 - AL4 after-AL3 completado y exportado liviano

### Objetivo
Registrar el cierre de AL4 en la WS, crear un paquete liviano para la laptop y dejar claro que el siguiente reentrenamiento GP debe hacerse fuera de la WS.

### Acciones
- Se verifico `data/production_status.json`.
- Se reviso el log `data/production_20260518_1542.log`.
- Se confirmo que no quedaban procesos `DualSPHysics`, `GenCase` ni `python` productivos activos.
- Se consulto `data/results.sqlite` para extraer las filas oficiales `al4_*`.
- Se creo `exports/al_batch4_after_al3_20260520/`.
- Se actualizaron `STATUS.md`, `HANDOFF.md`, `PLAN.md` e `INDEX.md`.

### Archivos revisados
- `data/production_status.json`
- `data/production_20260518_1542.log`
- `data/results.sqlite`
- `config/al_batch4_after_al3_20260518.csv`
- `data/processed/al4_*`

### Archivos modificados
- `.apos/STATUS.md`
- `.apos/HANDOFF.md`
- `.apos/PLAN.md`
- `.apos/INDEX.md`
- `.apos/JOURNAL.md`
- `exports/al_batch4_after_al3_20260520/`

### Comandos importantes
```text
Get-Content data\production_status.json
Get-Process | Where-Object { $_.ProcessName -match 'DualSPHysics|GenCase|python' }
python <inline export builder>
```

### Resultados
- AL4 termino `8/8` OK, `0` fallos numericos.
- Tiempo total AL4: `35.5 h`.
- Clases por `displacement_only`: 5 ESTABLE, 3 FALLO.
- Fallos fisicos: `al4_base_m085_mu0790`, `al4_highH_m115_mu0750`, `al4_highH_m125_mu0680`.
- Export liviano creado en `exports/al_batch4_after_al3_20260520/`.

### Errores / bloqueos
- No hubo errores numericos ni fallos de postproceso.

### Proximos pasos
- Subir export AL4 y `data/results.sqlite` por Git.
- En laptop: hacer `git pull` y reentrenar GP after-AL4.
- Decidir AL5, holdout o checks finos `dp=0.002` con base en el GP after-AL4.

### Advertencias metodologicas
- AL4 no debe interpretarse como convergencia de dp; es produccion dirigida a brackets.
- Rotacion sigue siendo diagnostica, no criterio primario.
- El GP after-AL4 debe entrenarse de forma deliberada en laptop, no automaticamente en WS.

## 2026-05-20 19:10 - GP after-AL4 entrenado y AL5 preparado

### Objetivo
Incorporar el export AL4 en laptop, reentrenar el surrogate GP local y definir el siguiente lote productivo WS sin usar reentrenamiento automatico en la WS.

### Acciones
- Se hizo `git pull origin master`; el repo ya contenia el commit `873fc18 Add AL4 after-AL3 lightweight export`.
- Se verifico `exports/al_batch4_after_al3_20260520/`.
- Se confirmo que `data/results.sqlite` contiene 8 filas oficiales `al4_*`.
- Se creo `scripts/train_gp_h_mu_mstar_after_al4_20260520.py`.
- Se entreno el GP after-AL4 localmente.
- Se genero `data/analysis/gp_h_mu_mstar_after_al4_20260520/`.
- Se guardo el modelo en `models/surrogates/gp_h_mu_mstar_after_al4_20260520.pkl`.
- Se creo `config/al_batch5_after_al4_20260520.csv`.
- Se creo `docs/PROMPT_WS_AL5_AFTER_AL4_20260520.md`.
- Se actualizaron `STATUS.md`, `HANDOFF.md`, `PLAN.md` e `INDEX.md`.

### Archivos revisados
- `exports/al_batch4_after_al3_20260520/al_batch4_summary.md`
- `exports/al_batch4_after_al3_20260520/al_batch4_summary.csv`
- `data/results.sqlite`
- `data/analysis/gp_h_mu_mstar_after_al4_20260520/brackets_by_h_mstar.csv`
- `data/analysis/gp_h_mu_mstar_after_al4_20260520/al5_candidates.csv`

### Archivos modificados
- `.apos/STATUS.md`
- `.apos/HANDOFF.md`
- `.apos/PLAN.md`
- `.apos/INDEX.md`
- `.apos/JOURNAL.md`
- `scripts/train_gp_h_mu_mstar_after_al4_20260520.py`
- `data/analysis/gp_h_mu_mstar_after_al4_20260520/`
- `models/surrogates/gp_h_mu_mstar_after_al4_20260520.pkl`
- `config/al_batch5_after_al4_20260520.csv`
- `docs/PROMPT_WS_AL5_AFTER_AL4_20260520.md`

### Comandos importantes
```text
git pull origin master
python scripts\train_gp_h_mu_mstar_after_al4_20260520.py
```

### Resultados
- GP after-AL4 uso 64 casos oficiales dentro del dominio.
- Dataset: 25 FALLO y 39 ESTABLE.
- Validacion LOO: accuracy `0.875`, MAE `2.557% d_eq`, RMSE `4.226% d_eq`.
- AL5 recomendado: 8 casos.
- Brackets clave after-AL4:
  - `H=0.200,m*=0.85`: `mu=0.7900` FALLO / `0.8000` ESTABLE.
  - `H=0.210,m*=1.00`: `mu=0.7400` FALLO / `0.7480` ESTABLE.
  - `H=0.225,m*=1.00`: `mu=0.8600` FALLO / `0.8650` ESTABLE.
  - `H=0.225,m*=1.15`: `mu=0.7500` FALLO / `0.7600` ESTABLE.
  - `H=0.225,m*=1.25`: `mu=0.6800` FALLO / `0.7000` ESTABLE.

### Errores / bloqueos
- No hubo errores de entrenamiento.
- El ranking automatico de candidatos por U-value cae en zonas de alta incertidumbre sin bracket fisico claro; se prefirio una matriz AL5 hibrida basada en brackets y vacios H-m*.

### Proximos pasos
- Commit/push de cambios locales.
- En WS: `git pull`, dry-run AL5 y corrida real si el dry-run lista exactamente 8 casos.
- Al volver AL5: reentrenar GP after-AL5 y decidir holdout/checks `dp=0.002`.

### Advertencias metodologicas
- AL5 sigue siendo active learning productivo, no convergencia.
- `al5_highH_m085_mu0900` puede fallar; si falla, indica que para `H=0.225,m*=0.85` la frontera queda fuera del dominio `mu<=0.90`.
- No abrir pendiente/orientacion/forma hasta tener la frontera base y validacion interna mas cerradas.
