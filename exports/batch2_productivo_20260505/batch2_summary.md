# Batch2 productivo 20260505 - resumen liviano

## Estado operativo

- Estado final: `completed`.
- Casos: 8/8 OK.
- Fallos numericos: 0.
- Tiempo total: 34.55 h.
- Malla: dp=0.003.
- Modo: `prod`.

## Resultado cientifico minimo

- Clases por `displacement_only`: 3 FALLO, 5 ESTABLE.
- Casos con rotacion diagnostica > 5 deg: 5/8.
- La rotacion no define la clase en este lote; se reporta como diagnostico.
- El lote fue informativo: no quedo todo estable ni todo fallo.

## Tabla resumida

| case | H | mu | slope | clase | disp %d_eq | rot deg | nota |
|---|---:|---:|---:|---|---:|---:|---|
| `batch2_base_mu0675` | 0.200 | 0.6750 | 1:20 | FALLO | 5.99 | 5.33 |  |
| `batch2_base_mu0685` | 0.200 | 0.6850 | 1:20 | ESTABLE | 3.78 | 4.76 |  |
| `batch2_base_mu0700` | 0.200 | 0.7000 | 1:20 | ESTABLE | 2.31 | 4.87 |  |
| `batch2_h0175_mu0680` | 0.175 | 0.6800 | 1:20 | ESTABLE | 1.23 | 4.56 |  |
| `batch2_h0225_mu0680` | 0.225 | 0.6800 | 1:20 | FALLO | 111.28 | 16.89 |  |
| `batch2_h0225_mu0720` | 0.225 | 0.7200 | 1:20 | FALLO | 62.87 | 13.39 |  |
| `batch2_slope10_mu0600` | 0.200 | 0.6000 | 1:10 | ESTABLE | 1.50 | 7.60 | rotation_diagnostic_only |
| `batch2_slope10_mu0650` | 0.200 | 0.6500 | 1:10 | ESTABLE | 1.42 | 7.44 | rotation_diagnostic_only |

## Lectura conservadora

1. En la condicion base `H=0.20`, `slope=1:20`, el lote refuerza una frontera local entre `mu=0.675` y `mu=0.685`: `mu=0.675` falla y `mu=0.685/0.700` son estables.
2. Con hidraulica moderadamente mas fuerte (`H=0.225`, `slope=1:20`), los dos casos ensayados fallan incluso con `mu=0.720`, por lo que esa altura desplaza la frontera hacia fricciones mayores.
3. Con hidraulica mas debil (`H=0.175`, `mu=0.680`, `slope=1:20`), el bloque queda estable con margen amplio.
4. Los casos `slope=1:10` con `mu=0.600` y `mu=0.650` quedan estables por desplazamiento, aunque rotan mas de 5 deg; esto debe tratarse como diagnostico, no como falla fisica bajo el criterio activo.

## Advertencias metodologicas

- No interpretar este lote como campana parametrica completa.
- No usar contacto maximo como criterio de falla.
- No mezclar rotacion diagnostica con `criterion_class`.
- No lanzar una campana grande antes de auditar este resumen y decidir el siguiente diseno.
