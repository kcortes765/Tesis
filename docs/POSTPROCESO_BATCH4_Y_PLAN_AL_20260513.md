# Postproceso batch4 y plan previo al siguiente lanzamiento WS

Fecha: 2026-05-13

## Estado de datos

Batch4 fue analizado desde `origin/master` commit `95d9468`, sin hacer `git pull` destructivo sobre la laptop. El repo local conserva cambios APOS/locales pendientes, por lo que este postproceso separa explicitamente:

- datos versionados WS/GitHub;
- analisis local en laptop;
- caso parcial batch4 como diagnostico, no resultado oficial.

Archivos generados:

- `data/analysis/batch4_postprocess_20260513/master_cases_20260513.csv`
- `data/analysis/batch4_postprocess_20260513/gp_seed_dataset_20260513.csv`
- `data/analysis/batch4_postprocess_20260513/batch4_diagnostics_table_20260513.csv`
- `data/analysis/batch4_postprocess_20260513/AL_BATCH1_HYBRID_RATIONALE_20260513.md`
- `config/al_batch1_hybrid_20260513.csv`
- `docs/PROMPT_WS_AL_BATCH1_HYBRID_20260513.md`

## Filtro usado para el dataset principal

El dataset para el surrogate principal incluye solo casos:

- oficiales completos;
- `dp=0.003`;
- geometria base;
- `slope_inv=20`;
- `boulder_rot_z=0`;
- `classification_mode=displacement_only`;
- dentro del dominio operativo `H=0.170-0.230`, `mu=0.55-0.90`, `m=0.85-1.25`.

El caso `batch4_mass_m125_H0225_mu0860` queda fuera porque fue recuperado parcialmente y no tiene postproceso oficial SQLite.

## Lectura de batch4

Batch4 cumplio su funcion: introdujo masa como tercera variable fisica.

- `m=0.85`: 4/4 casos oficiales fallan.
- `m=1.15`: 3/3 casos oficiales son estables.
- `m=1.25`: 2/2 casos oficiales son estables.
- En `H=0.225`, `m=1.0, mu=0.860` falla marginalmente, mientras `m=1.25, mu=0.800` es estable. Esto confirma que falta ubicar la transicion conjunta masa/friccion en el extremo hidraulico alto.

## GP seed

Se entreno un GP preliminar con 30 casos compatibles.

- Target continuo: `g_pct = 5 - disp_pct_deq`.
- Positivo: estable.
- Negativo: falla.
- Target de entrenamiento robusto: `clip(g_pct, -20, 8)`.
- Kernel ajustado: MatÃ©rn 5/2 con ARD.
- Error LOO aproximado: `MAE ~= 3.8`, `RMSE ~= 6.0` puntos porcentuales de `d_eq`.

Interpretacion: el GP sirve para orientar el proximo lote, pero no para aceptar ciegamente una matriz automatica. La siguiente corrida debe ser hibrida: active learning + brackets fisicos.

## Siguiente lote recomendado

Archivo listo:

```text
config/al_batch1_hybrid_20260513.csv
```

Matriz:

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

## Por que estos 8 casos

- Cerrar el bracket de masa baja en `H=0.175`.
- Ver si `m=0.85` puede estabilizarse en condicion base al subir `mu`.
- Medir cuanto baja la friccion critica con `m=1.15` y `m=1.25`.
- Cerrar H medio, donde `m=1.0` falla pero `m=1.15` ya estabilizo.
- Resolver el extremo `H=0.225`, donde la masa cambia la clase aun con fricciones altas.

## Gate antes de lanzar en WS

Lanzar solo si:

1. WS no tiene procesos productivos activos.
2. `git status -sb` se revisa sin limpiar ni revertir.
3. Existe `exports/batch4_mass_probe_20260513/batch4_summary.csv`.
4. Dry-run con `--prod` confirma exactamente 8 casos.
5. El dry-run usa `dp=0.003`, `displacement_only`, `reference_time_s=0.5`.

No lanzar si:

- intenta usar `dp_dev`;
- usa `config/experiment_matrix.csv`;
- lista otra cantidad de casos;
- hay procesos DualSPHysics activos;
- se intenta relanzar el caso parcial batch4 sin decision explicita.

## Despues del AL batch1

Si el lote termina limpio:

1. Export liviano WS.
2. Pull local controlado.
3. Reentrenar GP.
4. Decidir si AL batch2 ya puede ser puramente por adquisicion o si sigue haciendo falta lote dirigido.
5. Solo despues elegir 4-6 checks `dp=0.002`.
