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
