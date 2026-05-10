# Comparación analítica preliminar preproducción

Fecha: 2026-05-08  
Datos usados: piloto productivo liviano y `data/results/results_round2.csv` si existe.  
Objetivo: control de coherencia física de bajo orden, no validación exacta.

## Resumen

- Casos consolidados: 20
- Casos con velocidad de flujo útil para la comparación: 14
- Contradicciones fuertes entre banda analítica y clase SPH: 0/14
- Fallos SPH con banda completamente móvil (`Psi_lower > 1`): 10/12
- Estables SPH con resistencia posible en la banda (`Psi_lower < 1`): 2/2
- Mediana `Psi_central` en casos ESTABLE: 1.5
- Mediana `Psi_central` en casos FALLO: 164

## Lectura técnica

El índice `Psi` compara una fuerza motriz analítica aproximada contra una resistencia friccional efectiva:

```text
Psi = F_drive / F_resist
```

La lectura de referencia es:

- `Psi < 1`: resistencia mayor que forzante;
- `Psi > 1`: condición favorable al movimiento bajo los coeficientes asumidos;
- banda `lower-central-upper`: sensibilidad a coeficientes de arrastre, sustentación, área proyectada y efecto de pendiente.

La banda es más importante que el valor central. Si un caso estable tiene `Psi_central > 1`, pero `Psi_lower < 1`,
eso no se interpreta como contradicción fuerte: significa que con coeficientes conservadores todavía hay resistencia
analítica suficiente. La comparación se usa para detectar órdenes de magnitud incompatibles, no para reclasificar casos.

## Límites

Esta comparación no valida numéricamente el desplazamiento del bloque. Usa coeficientes hidráulicos no calibrados,
áreas proyectadas aproximadas y velocidades de gauge/postproceso. Su función es verificar coherencia de tendencia:
los casos con mayor movilidad analítica deberían tender a mostrar mayor desplazamiento o clase de falla.

## Advertencias de datos

Los casos con `flow_velocity_mps <= 0.01` o `water_height_m <= 0.01` se mantienen en el CSV maestro, pero no se usan
para la comparación principal, porque el índice analítico depende de una velocidad y una submergencia representativas.

## Archivos generados

- `analytic_mobility_summary.csv`
- `analytic_parameters.json`
- `figures/psi_vs_displacement.png`
- `figures/ordered_mobility_cases.png`

