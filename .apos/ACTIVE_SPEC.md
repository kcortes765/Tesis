# ACTIVE_SPEC — Thesis OS

## Tarea activa
Reconciliar estado local con workstation y cerrar la fase de screening LHS.

## Entregables esperados
1. Datos reales de campaña 30m recuperados de WS
2. `data/results.sqlite` reconstruido con datos reales
3. GP reentrenado con datos de 30m
4. Análisis Sobol con datos reales
5. Estructura lista para Caps 6-7

## Criterios de aceptación
- results.sqlite tiene >= 30 filas de datos reales de canal 30m
- GP R² > 0.95 sin soporte sintético
- Sobol indices calculados con datos reales
- Se puede responder: "¿qué parámetro domina el transporte?" con confianza

## Pre-requisito
Acceso a WS para recuperar datos (ChronoExchange CSVs, Run.csv de cada caso completado).

## No incluido
- Escritura de Caps 6-7 (siguiente ACTIVE_SPEC)
- Setup GNN (paralelo pero separado)
- Multi-forma (depende de STLs de Moris)
