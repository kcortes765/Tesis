# AL batch1 hibrido - justificacion tecnica

Fecha: 2026-05-13

## Decision

No se acepta la matriz automatica del GP seed como lanzamiento directo. El GP entrenado con piloto + batch2 + batch3 + batch4 tiene valor para ubicar incertidumbre, pero aun muestra error LOO alto (`MAE ~= 3.8` y `RMSE ~= 6.0` puntos porcentuales de `d_eq` sobre `g_train_clip_pct`). Por eso el siguiente lote debe ser hibrido: puntos informados por el GP, pero anclados a brackets fisicos claros.

## Lectura de batch4

- `m=0.85`: 4/4 casos oficiales fallan. Masa baja requiere mayor resistencia/friccion o menor intensidad hidraulica.
- `m=1.15`: 3/3 casos oficiales estables. Es el primer nivel donde aparece estabilizacion robusta en H bajo/base/medio.
- `m=1.25`: 2/2 casos oficiales estables; el caso `mu=0.860` queda fuera por ser parcial.
- En `H=0.225`, `m=1.0, mu=0.860` falla marginalmente, pero `m=1.25, mu=0.800` es estable. Falta ubicar la transicion de masa/friccion.

## Matriz propuesta

| Caso | Objetivo |
|---|---|
| `al1_lowH_m085_mu0620` | Cerrar bracket de H bajo para masa baja: `m=0.85, mu=0.560` fallo marginal; `m=1.0, mu=0.600` fue estable. |
| `al1_base_m085_mu0780` | Ver si la masa baja puede estabilizarse en condicion base al subir friccion. |
| `al1_base_m115_mu0620` | Medir cuanto baja la friccion critica al subir masa a `m=1.15`. |
| `al1_base_m125_mu0600` | Ancla de masa alta/friccion baja en condicion base; separa efecto masa de efecto friccion. |
| `al1_midH_m100_mu0800` | Bracket de H medio para masa nominal: `mu=0.700/0.740` fallaron; falta saber si `0.800` estabiliza. |
| `al1_midH_m115_mu0730` | Cierra transicion entre `m=1.0` fallante y `m=1.15` estable en H medio. |
| `al1_highH_m115_mu0800` | Punto clave: mismo `H=0.225, mu=0.800`, entre `m=1.0` fallante y `m=1.25` estable. |
| `al1_highH_m125_mu0740` | Bracket de friccion para masa alta en H alto: si falla, la frontera queda entre `mu=0.740` y `0.800`; si es estable, masa alta domina. |

## Gates antes de lanzar

- No relanzar el caso 12 parcial de batch4 todavia.
- No correr `dp=0.002` todavia.
- No cambiar criterio, `dp`, geometria ni orientacion.
- Ejecutar dry-run con `--prod`, matriz explicita y `--max-cases 8`.
- Si el dry-run usa `dp_dev` o una matriz distinta, detener.
