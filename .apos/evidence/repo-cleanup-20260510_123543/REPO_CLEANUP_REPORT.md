# Repo cleanup report - 2026-05-10

## Estado actualizado 2026-05-10 13:15

Este reporte documenta el diagnostico inicial. La recomendacion original de trabajar desde
`C:\Seba\Tesis_origin_master_clean_20260510_123639` quedo reemplazada despues de la
reconciliacion: el repo canonico vuelve a ser `C:\Seba\Tesis`, que es una junction hacia
`C:\Users\kevin\projects\Tesis`.

Acciones posteriores verificadas:

- `C:\Seba\Tesis` fue actualizado por fast-forward a `origin/master` en commit `3c443e9`.
- Los cambios trackeados locales previos fueron guardados en `stash@{0}` antes de actualizar.
- Los 8 archivos no trackeados que chocaban con GitHub fueron movidos a `.apos/cache/git-untracked-conflicts-20260510_125339/`.
- El origen de datos GitHub/WS versus laptop/local quedo documentado en `docs/DATA_ORIGIN_POLICY.md`.
- El worktree temporal ya no debe usarse como fuente de trabajo; queda solo como respaldo hasta retirarlo.

## Decision

No se hizo `git pull` directo sobre `C:\Seba\Tesis` porque el arbol local esta sucio y contiene datos locales/crudos. Para no perder nada, se creo una copia limpia separada desde `origin/master`.

## Carpetas

- Carpeta sucia / archivo local: `C:\Seba\Tesis`
- Carpeta limpia canonica para leer GitHub actual: `C:\Seba\Tesis_origin_master_clean_20260510_123639`
- Auditoria y parches de respaldo: `C:\Seba\Tesis\.apos\evidence\repo-cleanup-20260510_123543`

## Estado Git real

`C:\Seba\Tesis` esta en `master` y esta 3 commits detras de `origin/master`. No tiene commits locales encima de `origin/master`; el problema son cambios no committeados y archivos no trackeados.

### Commits entrantes desde GitHub

```text
3c443e9 Add batch3 production export
a46842a Record WS git transfer handoff
646c567 Sync WS thesis results and batch2 export
```

## Cambios locales trackeados en C:\Seba\Tesis

Estos cambios quedaron respaldados como parche en `08_git_diff_binary.patch`. No se borraron ni se revirtieron.

```text
﻿M	apos-system/PROMPT_IMPLEMENTACION_APOS_X.md
M	apos-system/README.md
M	apos-system/VERSION.md
M	apos-system/adapters/codex/AGENTS.snippet.md
M	apos-system/adapters/codex/discover-codex-paths.ps1
M	apos-system/docs/architecture.md
M	apos-system/docs/migration.md
M	apos-system/docs/safe-harness.md
M	apos-system/docs/skill-governance.md
M	apos-system/evals/README.md
M	apos-system/harness/apos-run.ps1
M	apos-system/harness/apos-run.py
M	apos-system/harness/risk_rules.yaml
M	apos-system/migration/audit-report.md
M	apos-system/migration/backup-report.md
M	apos-system/modules/chat-transfer/SKILL.md
M	apos-system/modules/quality-evals/SKILL.md
M	apos-system/modules/research-autonomo/SKILL.md
M	apos-system/modules/safe-harness/SKILL.md
D	apos-system/skills/apos-skill-governance/SKILL.md
M	apos-system/skills/guardar/SKILL.md
D	apos-system/skills/init-apos/SKILL.md
D	apos-system/skills/retomar/SKILL.md
M	config/template_base.xml
M	data/results.sqlite
M	scripts/analisis_convergencia_corregida.py
M	scripts/plot_03_convergence_metrics_only.py
```

## Archivos locales no trackeados / ignorados

Resumen:

- No trackeados: 3903 archivos.
- Ignorados: 23619 archivos.
- Los inventarios estan en:
  - `13_untracked_inventory.csv`
  - `14_ignored_top_inventory.csv`
  - `11_ignored_files.txt`

Top-level sizes in dirty workspace `C:\Seba\Tesis`:

```text
cases      13.896 GB
.venv-gnn   4.572 GB
imports     1.356 GB
.git        0.865 GB
data        0.803 GB
archive     0.178 GB
.claude     0.075 GB
```

## Export versionable disponible en la copia limpia

```text
﻿
Name                                     LastWriteTime             Files       KB
----                                     -------------             -----       --
batch2_productivo_20260505               10/05/2026 12:36:49 p. m.    24     67.8
batch3_productivo_20260509               10/05/2026 12:36:49 p. m.    28     75.1
pilot_productivo_20260501                10/05/2026 12:36:49 p. m.    18     53.6
thesis_analysis_prelim_20260421_144616   10/05/2026 12:36:51 p. m.   307 223046.7
ws_delta_conv_edge_f0685_20260422_081859 10/05/2026 12:36:51 p. m.    17    510.7
ws_delta_conv_edge_f0685_20260422_090418 10/05/2026 12:36:51 p. m.     4     27.5
```

## Regla de trabajo desde ahora

1. Para leer resultados GitHub/WS actualizados, usar `C:\Seba\Tesis_origin_master_clean_20260510_123639`.
2. No usar `C:\Seba\Tesis` como fuente canonica hasta decidir que hacer con sus cambios locales.
3. No borrar `cases/`, `data/`, `imports/` ni `archive/`; primero extraer o respaldar lo que tenga valor.
4. Para agregar lo nuevo de bloques STL, portar desde `C:\Seba\Tesis\models\bloques\b02_variantes_20260510` y `C:\Seba\Tesis\data\geometry\bloques_b02_20260510` hacia la carpeta limpia solo cuando se decida versionarlo.
5. No correr simulaciones desde la carpeta sucia si se busca reproducibilidad limpia.

## Archivos de respaldo creados

- `02_git_status_sb_all.txt`
- `03_git_status_porcelain.txt`
- `08_git_diff_binary.patch`
- `10_untracked_excluding_ignored.txt`
- `11_ignored_files.txt`
- `13_untracked_inventory.csv`
- `14_ignored_top_inventory.csv`
- `15_worktree_add_origin_master.txt`
- `16_clean_worktree_status.txt`
- `17_clean_worktree_exports.txt`

## Conclusion

No se perdio data. El estado limpio y actualizado de GitHub queda disponible en el worktree separado. El arbol original queda intacto como archivo local con datos pesados y cambios pendientes.
