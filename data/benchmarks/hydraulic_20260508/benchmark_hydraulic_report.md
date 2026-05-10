# Benchmark hidráulico DualSPHysics 2D

Fecha: 2026-05-08  
Caso: `examples/main/01_DamBreak/CaseDambreakVal2D`  
Referencia incluida: Koshizuka y Oka (1996), posición del frente de dam-break.  

## Qué valida

Este benchmark verifica que la instalación local de DualSPHysics, GenCase, GPU y postproceso de gauges reproducen
un caso hidráulico documentado incluido con la distribución oficial. No valida el bloque irregular ni el contacto
Chrono de la tesis.

## Resultado cuantitativo

- Puntos de referencia usados: 15
- RMSE posición frente: 0.2573 m
- MAE posición frente: 0.2401 m
- Error relativo medio: 10.19 %
- Error relativo máximo: 17.18 %
- Error relativo final: 3.42 %
- Partículas: 21001
- `dp`: 0.01 m
- `TimeMax`: 2.0 s

## Lectura

La curva simulada reproduce la evolución temporal del frente de agua con errores de orden menor a una decena de
centímetros en el rango comparado. Esto es suficiente como benchmark hidráulico operativo del entorno local, siempre
declarando que se trata de un caso 2D simple y no de validación del bloque costero.

## Archivos

- `front_position_comparison.csv`
- `front_position_simulation_full.csv`
- `front_position_reference.csv`
- `benchmark_metrics.json`
- `figures/front_position_benchmark.png`
- `figures/front_position_error.png`
