# PROMPT WS - AL batch1 hibrido post batch4

Estamos en:

```text
C:\Users\Admin\Desktop\SPH-Tesis
```

Objetivo:
Lanzar un lote productivo corto y dirigido de 8 casos para reducir incertidumbre del surrogate principal `[H, mu, m*]` despues de batch4. Este lote es `AL batch1 hibrido`: usa el GP seed como orientacion, pero prioriza brackets fisicos claros de masa/friccion/hidraulica.

Contexto fijo:

- No es convergencia de `dp`.
- No es sensibilidad de forma.
- Resolucion productiva: `dp=0.003 m`.
- Criterio primario: `classification_mode=displacement_only`.
- `reference_time_s=0.5`.
- Umbral de movimiento: `D_max > 5% d_eq`.
- Rotacion se reporta como variable observada, no como criterio de falla.
- Geometria base, orientacion `boulder_rot_z=0`, pendiente `slope_inv=20`.
- No usar `run_production.py --pilot --prod`.
- No relanzar todavia `batch4_mass_m125_H0225_mu0860`; queda como diagnostico parcial.

Preflight obligatorio:

1. Confirmar que no hay procesos productivos activos:

```powershell
Get-Process | Where-Object { $_.ProcessName -match "DualSPHysics|GenCase|python" } |
  Select-Object Id,ProcessName,StartTime,CPU
```

2. Revisar estado Git solo para diagnostico:

```powershell
git status -sb
git log --oneline -3
```

No limpiar, revertir ni borrar nada sin confirmacion.

3. Confirmar que existe el export batch4:

```powershell
Test-Path exports\batch4_mass_probe_20260513\batch4_summary.csv
```

4. Confirmar que `scripts/run_production.py` existe y que el dry-run con `--prod` usa `dp=0.003`.

Crear archivo:

```text
config/al_batch1_hybrid_20260513.csv
```

con exactamente:

```csv
case_id,dam_height,boulder_mass,boulder_rot_z,friction_coefficient,slope_inv
al1_lowH_m085_mu0620,0.175,0.85,0,0.620,20
al1_base_m085_mu0780,0.200,0.85,0,0.780,20
al1_base_m115_mu0620,0.200,1.15,0,0.620,20
al1_base_m125_mu0600,0.200,1.25,0,0.600,20
al1_midH_m100_mu0800,0.210,1.00,0,0.800,20
al1_midH_m115_mu0730,0.210,1.15,0,0.730,20
al1_highH_m115_mu0800,0.225,1.15,0,0.800,20
al1_highH_m125_mu0740,0.225,1.25,0,0.740,20
```

Dry-run obligatorio:

```powershell
python scripts\run_production.py --prod --matrix config\al_batch1_hybrid_20260513.csv --max-cases 8 --dry-run --no-notify
```

Verificar que el dry-run liste exactamente:

- 8 casos;
- `dp=0.003`;
- matriz explicita `config/al_batch1_hybrid_20260513.csv`;
- `classification_mode=displacement_only`;
- `reference_time_s=0.5`;
- columnas correctas: `case_id`, `dam_height`, `boulder_mass`, `boulder_rot_z`, `friction_coefficient`, `slope_inv`.

Si el dry-run muestra otra cantidad de casos, otro `dp`, otra matriz, `dp_dev`, o intenta usar `config/experiment_matrix.csv`, detenerse y reportar.

Solo si el dry-run es correcto, lanzar:

```powershell
python scripts\run_production.py --prod --matrix config\al_batch1_hybrid_20260513.csv --max-cases 8 --no-notify
```

Monitoreo:

```powershell
Get-Content data\production_status.json
Get-Content data\production_YYYYMMDD_HHMM.log -Tail 100 -Wait
```

Al terminar, crear export liviano:

```text
exports/al_batch1_hybrid_YYYYMMDD/
```

Debe incluir:

- `README.md`;
- `al_batch1_summary.csv`;
- `al_batch1_summary.md`;
- `production_status.json`;
- tail del log productivo;
- `config/al_batch1_hybrid_20260513.csv`;
- inventario liviano de `data/processed/al1_*`;
- `Run.csv` y `RunPARTs.csv` por caso si existen;
- no incluir `.bi4`, `.ibi4`, VTK, `Part*`, `_out/` ni outputs pesados.

Actualizar APOS:

- `.apos/STATUS.md`;
- `.apos/HANDOFF.md`;
- `.apos/PLAN.md`;
- `.apos/JOURNAL.md`;
- `.apos/RISKS.md`;
- `.apos/SOURCES.md` si corresponde.

Entrega final:

- si dry-run fue correcto;
- hora de inicio del lote real;
- si quedo corriendo o termino;
- ruta de `production_status.json`;
- ruta del log;
- casos completados/fallidos;
- ruta del export liviano si termino;
- advertencias metodologicas.

Restricciones:

- No correr `run_production.py --pilot --prod`.
- No correr una campana distinta de estos 8 casos.
- No borrar outputs.
- No limpiar Git.
- No hacer cambios metodologicos nuevos.
- No cambiar `dp`.
- No cambiar criterio de clasificacion.
