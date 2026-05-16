# Prompt WS - AL3 after-AL2

Estamos en:

```powershell
C:\Users\Admin\Desktop\SPH-Tesis
```

Objetivo:
Ejecutar el lote `AL3` propuesto desde la laptop despues de incorporar AL2 y reentrenar localmente el GP after-AL2. La WS solo debe simular y exportar resultados livianos; no debe reentrenar modelos.

## Contexto fijo

- Resolucion productiva: `dp=0.003 m`.
- Criterio primario: `classification_mode=displacement_only`.
- `reference_time_s=0.5`.
- Umbral de movimiento: `Dmax > 5% d_eq`.
- La rotacion se reporta como variable observada, no como criterio de falla.
- La geometria base, orientacion y pendiente de este lote no se cambian.
- No usar `run_production.py --pilot --prod`.
- No usar `--retrain-gp`.
- No modificar scripts metodologicos salvo que un error real impida correr; si pasa, detener y reportar.

## Racional de AL3

AL3 cierra brackets y zonas de incertidumbre detectadas por el GP after-AL2:

- `m*=0.85`: cerrar baja altura/base y probar si `H=0.210, mu=0.900` vuelve a estabilidad.
- `m*=1.00`: afinar la transicion en `H=0.210` y verificar `H=0.225` cerca de `mu=0.870`.
- `m*=1.15`: cerrar el bracket alto entre `mu=0.740` fallante y zonas estables esperadas.
- `m*=1.25`: comprobar si aumentar masa estabiliza `H=0.225` alrededor de `mu=0.700`.

`m*` es masa relativa respecto del caso base: `m*=1.00` es 1.0 kg, `m*=0.85` es 15% mas liviano y `m*=1.25` es 25% mas pesado. El pipeline debe mantener coherentes masa, densidad efectiva e inercia.

## Matriz

Usar el archivo versionado:

```powershell
config\al_batch3_gp_after_al2_20260516.csv
```

Contenido esperado:

```csv
case_id,dam_height,boulder_mass,boulder_rot_z,friction_coefficient,slope_inv
al3_lowH_m085_mu0572,0.175,0.85,0,0.572,20
al3_base_m085_mu0800,0.200,0.85,0,0.800,20
al3_midH_m085_mu0900,0.210,0.85,0,0.900,20
al3_midH_m100_mu0755,0.210,1.00,0,0.755,20
al3_highH_m100_mu0870,0.225,1.00,0,0.870,20
al3_highH_m115_mu0760,0.225,1.15,0,0.760,20
al3_highH_m115_mu0780,0.225,1.15,0,0.780,20
al3_highH_m125_mu0700,0.225,1.25,0,0.700,20
```

## Antes de correr

1. Sincronizar:

```powershell
git pull origin master
```

2. Confirmar estado de procesos:

```powershell
Get-Process | Where-Object { $_.ProcessName -match "DualSPHysics|GenCase|python" } |
  Select-Object Id,ProcessName,StartTime,CPU
```

Si hay una produccion activa, no lanzar AL3.

3. Revisar estado Git solo para diagnostico:

```powershell
git status --short
```

No limpiar, no resetear, no borrar outputs.

4. Confirmar que existe el CSV:

```powershell
Get-Content config\al_batch3_gp_after_al2_20260516.csv
```

Debe tener exactamente 8 casos.

## Dry-run obligatorio

Ejecutar:

```powershell
python scripts\run_production.py --prod --matrix config\al_batch3_gp_after_al2_20260516.csv --max-cases 8 --dry-run --no-notify
```

Verificar explicitamente:

- lista 8 casos;
- `dp=0.003`;
- `classification_mode=displacement_only`;
- `reference_time_s=0.5`;
- usa la matriz `config\al_batch3_gp_after_al2_20260516.csv`;
- no usa `config\experiment_matrix.csv`;
- no llama GenCase ni DualSPHysics durante dry-run;
- no aparece `--retrain-gp`.

Si algo no coincide, detenerse y reportar.

## Lanzamiento real

Solo si el dry-run es correcto:

```powershell
python scripts\run_production.py --prod --matrix config\al_batch3_gp_after_al2_20260516.csv --max-cases 8 --no-notify
```

No agregar `--retrain-gp`.

## Monitoreo

```powershell
Get-Content data\production_status.json
Get-Content data\production_YYYYMMDD_HHMM.log -Tail 100 -Wait
```

Reportar:

- hora de inicio;
- caso actual;
- completados/fallidos/pendientes;
- ruta de log;
- ruta de `production_status.json`.

Si falla un caso, no relanzar automaticamente sin diagnosticar.

## Al terminar

Crear export liviano:

```text
exports/al_batch3_gp_after_al2_YYYYMMDD/
```

Debe incluir:

- `README.md`;
- `al_batch3_summary.csv`;
- `al_batch3_summary.md`;
- `production_status.json`;
- tail del log productivo;
- `config/al_batch3_gp_after_al2_20260516.csv`;
- inventario liviano de `data/processed/al3_*`;
- `Run.csv` y `RunPARTs.csv` por caso si existen;
- no incluir `.bi4`, `.ibi4`, VTK, `Part*`, `*_out` ni outputs pesados.

Actualizar APOS:

- `.apos/STATUS.md`;
- `.apos/HANDOFF.md`;
- `.apos/PLAN.md`;
- `.apos/JOURNAL.md`;
- `.apos/SOURCES.md` si corresponde.

Debe quedar claro:

- AL3 es simulacion productiva dirigida por GP after-AL2;
- la WS no reentreno modelo;
- la laptop reentrenara el GP cuando AL3 vuelva por Git;
- `dp=0.003`, `displacement_only`, `reference_time_s=0.5`.

## Entrega final esperada

Reportar:

- resultado del dry-run;
- si AL3 quedo corriendo o termino;
- casos OK/fallidos;
- ruta del log;
- ruta del export liviano si termino;
- cualquier advertencia sobre masa, inercia, contacto, gauges o postproceso.

