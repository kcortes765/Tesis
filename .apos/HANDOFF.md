# HANDOFF

## Proxima accion recomendada
1. Continuar exclusivamente desde `C:\Seba\Tesis`.
2. Revisar piloto + batch2 + batch3 juntos desde los exports livianos.
3. Decidir si se entrena surrogate exploratorio o se disena un mini-batch adicional.
4. Si se abre geometria, partir por los STL `b02` ya analizados y un sanity de contacto por geometria.

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

## Comandos sugeridos
```powershell
cd C:\Seba\Tesis
git status -sb

Get-Content exports\batch3_productivo_20260509\batch3_summary.md

Import-Csv exports\batch3_productivo_20260509\batch3_summary.csv |
  Select case_id,dam_height,friction_coefficient,slope_inv,criterion_class,disp_pct_deq,max_rotation_deg
```

## Senales de exito
- `git status -sb` no muestra otro worktree como fuente canonica.
- Los datos de WS se citan por export/commit.
- Los datos locales se citan por path y quedan versionados si son livianos.
- No queda APOS duplicado como verdad viva.

## No hacer todavia
- No recrear ni usar worktrees temporales como fuente diaria.
- No aplicar `stash@{0}` completo sin revisar.
- No borrar backups, `cases/`, `data/`, `imports/` ni `archive/`.
- No lanzar otra tanda antes de revisar piloto + batch2 + batch3.
- No versionar crudos pesados.
- No mezclar rotacion diagnostica con falla por desplazamiento.

## Riesgos inmediatos
- Confundir origen WS/GitHub con origen laptop/local.
- Recuperar cambios viejos del stash y reintroducir APOS antiguo.
- Sobreinterpretar batch2/batch3 como mapa completo.
