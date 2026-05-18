# Prompt WS - AL4 after-AL3

Estamos en:

```powershell
C:\Users\Admin\Desktop\SPH-Tesis
```

Objetivo:
Ejecutar `AL4` como lote dirigido despues de incorporar AL3 y reentrenar localmente el GP after-AL3 en la laptop. La WS solo debe simular y exportar resultados livianos; no debe reentrenar modelos.

## Contexto fijo

- Resolucion productiva: `dp=0.003 m`.
- Criterio primario: `classification_mode=displacement_only`.
- `reference_time_s=0.5`.
- Umbral de movimiento: `Dmax > 5% d_eq`.
- La rotacion se reporta como variable observada, no como criterio de falla.
- Geometria base, orientacion `rot_z=0` y pendiente `1:20` se mantienen.
- No usar `run_production.py --pilot --prod`.
- No usar `--retrain-gp`.
- No modificar scripts metodologicos salvo que un error real impida correr; si pasa, detener y reportar.

## Racional de AL4

AL3 salio 8/8 ESTABLE. Eso cerro el lado seguro de varios brackets, pero ahora falta ubicar con mas precision el cambio de clase. AL4 baja levemente `mu` dentro de brackets ya observados, no expande el dominio.

Brackets que se busca cerrar:

- `H=0.175, m*=0.85`: entre `mu=0.560` FALLO y `mu=0.572` ESTABLE.
- `H=0.200, m*=0.85`: entre `mu=0.780` FALLO y `mu=0.800` ESTABLE.
- `H=0.210, m*=0.85`: entre `mu=0.880` FALLO y `mu=0.900` ESTABLE.
- `H=0.210, m*=1.00`: entre `mu=0.740` FALLO y `mu=0.755` ESTABLE.
- `H=0.225, m*=1.00`: entre `mu=0.860` FALLO y `mu=0.870` ESTABLE.
- `H=0.225, m*=1.15`: entre `mu=0.740` FALLO y `mu=0.760` ESTABLE.
- `H=0.225, m*=1.25`: entre `mu=0.660` FALLO y `mu=0.700` ESTABLE.
- `H=0.200, m*=1.00`: chequeo fino cerca de la transicion base historica `0.6806` FALLO / `0.6810` ESTABLE.

`m*` es masa relativa respecto del caso base: `m*=1.00` es 1.0 kg, `m*=0.85` es 15% mas liviano y `m*=1.25` es 25% mas pesado. El pipeline debe mantener coherentes masa, densidad efectiva e inercia.

## Matriz

Usar el archivo versionado:

```powershell
config\al_batch4_after_al3_20260518.csv
```

Contenido esperado:

```csv
case_id,dam_height,boulder_mass,boulder_rot_z,friction_coefficient,slope_inv
al4_lowH_m085_mu0566,0.175,0.85,0,0.566,20
al4_base_m085_mu0790,0.200,0.85,0,0.790,20
al4_midH_m085_mu0890,0.210,0.85,0,0.890,20
al4_midH_m100_mu0748,0.210,1.00,0,0.748,20
al4_highH_m100_mu0865,0.225,1.00,0,0.865,20
al4_highH_m115_mu0750,0.225,1.15,0,0.750,20
al4_highH_m125_mu0680,0.225,1.25,0,0.680,20
al4_base_m100_mu06808,0.200,1.00,0,0.6808,20
```

## Antes de correr

1. Sincronizar:

```powershell
git pull origin master
```

2. Confirmar que no hay produccion activa:

```powershell
Get-Process | Where-Object { $_.ProcessName -match "DualSPHysics|GenCase|python" } |
  Select-Object Id,ProcessName,StartTime,CPU
```

Si hay una produccion activa, no lanzar AL4.

3. Revisar estado Git solo para diagnostico:

```powershell
git status --short
```

No limpiar, no resetear, no borrar outputs.

4. Confirmar que existe el CSV y tiene exactamente 8 casos:

```powershell
Get-Content config\al_batch4_after_al3_20260518.csv
```

## Dry-run obligatorio

Ejecutar:

```powershell
python scripts\run_production.py --prod --matrix config\al_batch4_after_al3_20260518.csv --max-cases 8 --dry-run --no-notify
```

Verificar explicitamente:

- lista 8 casos;
- `dp=0.003`;
- `classification_mode=displacement_only`;
- `reference_time_s=0.5`;
- usa la matriz `config\al_batch4_after_al3_20260518.csv`;
- no usa `config\experiment_matrix.csv`;
- no llama GenCase ni DualSPHysics durante dry-run;
- no aparece `--retrain-gp`.

Si algo no coincide, detenerse y reportar.

## Lanzamiento real

Solo si el dry-run es correcto:

```powershell
python scripts\run_production.py --prod --matrix config\al_batch4_after_al3_20260518.csv --max-cases 8 --no-notify
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
exports/al_batch4_after_al3_YYYYMMDD/
```

Debe incluir:

- `README.md`;
- `al_batch4_summary.csv`;
- `al_batch4_summary.md`;
- `production_status.json`;
- tail del log productivo;
- `config/al_batch4_after_al3_20260518.csv`;
- inventario liviano de `data/processed/al4_*`;
- `Run.csv` y `RunPARTs.csv` por caso si existen;
- no incluir `.bi4`, `.ibi4`, VTK, `Part*`, `*_out` ni outputs pesados.

Actualizar APOS:

- `.apos/STATUS.md`;
- `.apos/HANDOFF.md`;
- `.apos/PLAN.md`;
- `.apos/JOURNAL.md`;
- `.apos/SOURCES.md` si corresponde.

Debe quedar claro:

- AL4 es simulacion productiva dirigida por GP after-AL3 y brackets observados;
- la WS no reentreno modelo;
- la laptop reentrenara el GP cuando AL4 vuelva por Git;
- `dp=0.003`, `displacement_only`, `reference_time_s=0.5`.

## Entrega final esperada

Reportar:

- resultado del dry-run;
- si AL4 quedo corriendo o termino;
- casos OK/fallidos;
- ruta del log;
- ruta del export liviano si termino;
- cualquier advertencia sobre masa, inercia, contacto, gauges o postproceso.
