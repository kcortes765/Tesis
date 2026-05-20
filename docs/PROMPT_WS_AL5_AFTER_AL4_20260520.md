# Prompt WS - AL5 after-AL4

Estamos en:

`C:\Users\Admin\Desktop\SPH-Tesis`

Objetivo:
Ejecutar AL5 como lote productivo dirigido, no convergencia, para cerrar brackets y vacios despues del reentrenamiento GP after-AL4 hecho en laptop.

Contexto metodologico fijo:
- Resolucion productiva: `dp=0.003 m`.
- Criterio primario: `classification_mode=displacement_only`.
- `reference_time_s=0.5`.
- Umbral de movimiento: `Dmax > 5% d_eq`.
- Pendiente fija: `1:20`.
- Orientacion fija: `rot_z=0`.
- Geometria base fija: `BLIR3.stl`.
- `boulder_mass` se usa como `m*` operativo: 0.85, 1.00, 1.15, 1.25.
- La WS solo ejecuta simulaciones y exporta resultados. No reentrenar GP en la WS.
- No usar `run_production.py --pilot --prod`.
- No usar `--retrain-gp`.

Evidencia laptop:
- GP after-AL4 entrenado con 64 casos oficiales dentro del dominio.
- LOO accuracy: 0.875.
- MAE LOO: 2.56 `% d_eq`.
- AL5 mezcla cierre de brackets observados y llenado de cortes H-m* faltantes.

Tareas:

1. Sincronizar y revisar
```powershell
cd C:\Users\Admin\Desktop\SPH-Tesis
git pull origin master
git status --short
```
Solo revisar estado; no limpiar ni revertir nada.

2. Confirmar archivos
- Debe existir `config\al_batch5_after_al4_20260520.csv`.
- Debe existir `scripts\run_production.py`.
- Confirmar que no hay procesos productivos activos:
```powershell
Get-Process | Where-Object { $_.ProcessName -match "DualSPHysics|GenCase|python" } |
  Select Id,ProcessName,StartTime,CPU
```

3. Dry-run obligatorio
```powershell
python scripts\run_production.py --prod --matrix config\al_batch5_after_al4_20260520.csv --max-cases 8 --dry-run --no-notify
```

Verificar que el dry-run liste exactamente:
- 8 casos.
- `dp=0.003`.
- matriz explicita `config\al_batch5_after_al4_20260520.csv`.
- `classification_mode=displacement_only`.
- `reference_time_s=0.5`.
- columnas: `case_id,dam_height,boulder_mass,boulder_rot_z,friction_coefficient,slope_inv`.

Si el dry-run muestra otra matriz, otra cantidad de casos, otro `dp` o intenta usar `experiment_matrix.csv`, detenerse y reportar.

4. Lanzamiento real
Solo si el dry-run es correcto:
```powershell
python scripts\run_production.py --prod --matrix config\al_batch5_after_al4_20260520.csv --max-cases 8 --no-notify
```

5. Monitoreo
```powershell
Get-Content data\production_status.json
Get-Content data\production_YYYYMMDD_HHMM.log -Tail 100 -Wait
```

No borrar outputs, no relanzar automaticamente un caso fallido sin diagnosticar.

6. Al terminar
Crear export liviano:

`exports/al_batch5_after_al4_YYYYMMDD/`

Debe incluir:
- `README.md`
- `al_batch5_summary.csv`
- `al_batch5_summary.md`
- `production_status.json`
- `production_log_tail.txt`
- `config/al_batch5_after_al4_20260520.csv`
- inventario liviano de `data/processed/al5_*`
- `Run.csv` y `RunPARTs.csv` por caso si existen

No incluir:
- `cases/`
- `_out/`
- `.bi4`
- `.ibi4`
- VTK
- `Part*`
- outputs crudos pesados

7. Actualizar APOS
Actualizar:
- `.apos/STATUS.md`
- `.apos/HANDOFF.md`
- `.apos/PLAN.md`
- `.apos/JOURNAL.md`

Debe quedar claro:
- AL5 es productivo/active learning, no convergencia.
- La laptop reentrena el GP despues.
- La WS no debe usar `--retrain-gp`.

8. Subir a Git
Subir export liviano, `data/results.sqlite`, matriz y APOS.

Entrega final:
- dry-run OK o no.
- hora de inicio real.
- casos completados/fallidos.
- ruta del log.
- ruta del export.
- commit subido.

Matriz esperada:

```csv
case_id,dam_height,boulder_mass,boulder_rot_z,friction_coefficient,slope_inv
al5_highH_m085_mu0900,0.225,0.85,0,0.9000,20
al5_base_m085_mu0795,0.200,0.85,0,0.7950,20
al5_midH_m100_mu0744,0.210,1.00,0,0.7440,20
al5_highH_m100_mu08625,0.225,1.00,0,0.8625,20
al5_midH_m115_mu0700,0.210,1.15,0,0.7000,20
al5_highH_m115_mu0755,0.225,1.15,0,0.7550,20
al5_midH_m125_mu0660,0.210,1.25,0,0.6600,20
al5_highH_m125_mu0690,0.225,1.25,0,0.6900,20
```
