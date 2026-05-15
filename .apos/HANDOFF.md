# HANDOFF

## Proxima accion recomendada
1. Monitorear AL batch2 en la WS hasta que termine o falle.
2. No lanzar otra tanda encima.
3. Cuando termine, crear export liviano `exports/al_batch2_bracket_closing_YYYYMMDD/` y subirlo por Git.
4. Despues revisar piloto + batch2 + batch3 + batch4 + AL batch1 + AL batch2 juntos.
5. Revisar las figuras `data/figures/production_story_graphics/` y elegir set final para tesis/PPT.
6. Decidir si se entrena surrogate exploratorio, se repite el caso 12 parcial de batch4 o se disena otro mini-batch.

## Contexto minimo para continuar
- `C:\Seba\Tesis` vuelve a ser el unico repo canonico local.
- En esta laptop, `C:\Seba\Tesis` es una junction hacia `C:\Users\kevin\projects\Tesis`; ambos paths son la misma carpeta.
- `C:\Seba\Tesis` esta actualizado y pusheado a `origin/master` en commit `0e98b65`.
- La carpeta temporal `C:\Seba\Tesis_origin_master_clean_20260510_123639` ya fue retirada; su `.apos` quedo respaldado en `C:\Seba\workspace_backups\tesis-reconcile-20260510_125339\temp_worktree_before_remove`.
- Los cambios trackeados locales previos quedaron guardados en `stash@{0}` y backup externo.
- Backup externo: `C:\Seba\workspace_backups\tesis-reconcile-20260510_125339`.
- Data WS/GitHub: exports livianos versionados.
- Data laptop/local: STL, web, figuras, scripts y documentos locales; usar solo si se versionan o se cita el path.
- Convergencia cerrada: `dp=0.003` queda como resolucion operativa.
- Criterio primario: `displacement_only`.
- Referencia temporal: `reference_time_s=0.5`.
- Rotacion: diagnostico.
- Piloto: 5/5 OK, export en `exports/pilot_productivo_20260501/`.
- Batch2: 8/8 OK, export en `exports/batch2_productivo_20260505/`.
- Batch3: 10/10 OK, 0 fallos numericos, export en `exports/batch3_productivo_20260509/`.
- Batch3 base `H=0.20`, `slope=1:20`: FALLO en `mu=0.678` y `0.680`; ESTABLE en `mu=0.682`.
- Batch4 mass probe en WS: 11/12 casos oficiales en SQLite + 1 caso parcial recuperado desde CSV crudos.
- Export batch4: `exports/batch4_mass_probe_20260513/`.
- Caso parcial batch4: `batch4_mass_m125_H0225_mu0860`; usar solo como diagnostico hasta repetir o reprocesar oficialmente.
- AL batch1 hibrido fue lanzado el 2026-05-13 09:41 desde `config/al_batch1_hybrid_20260513.csv`.
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
