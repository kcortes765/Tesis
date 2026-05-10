# Resumen batch3 productivo 20260509

## Estado

- Lote: `batch3_productivo`.
- Estado final: `completed`.
- Casos OK: 10/10.
- Fallos numericos: 0.
- Tiempo total: 42.03 h.
- Resolucion: `dp=0.003 m`.
- Criterio primario: `classification_mode=displacement_only`.
- Referencia temporal: `reference_time_s=0.5`.
- Rotacion: diagnostica, no criterio primario.

## Resultado fisico corto

- FALLO por desplazamiento: 6 casos.
- ESTABLE por desplazamiento: 4 casos.
- Base H=0.20, pendiente 1:20: falla en `mu=0.678` y `mu=0.680`; estable en `mu=0.682`. Esto afina la frontera base a `0.680 < mu_crit < 0.682` para este lote.
- H=0.175: todos los puntos corridos (`mu=0.600`, `0.640`, `0.660`) son estables.
- H=0.210: los puntos `mu=0.700` y `mu=0.740` fallan.
- H=0.225: los puntos `mu=0.760` y `mu=0.800` fallan.

## Advertencia metodologica

Este lote es produccion dirigida, no un nuevo estudio de convergencia. Usa `dp=0.003` como resolucion operativa. No afirmar convergencia asintotica fuerte. La rotacion puede superar 5 grados en varios casos, pero la clase se decide por desplazamiento (`moved`) bajo `displacement_only`.

## Archivos incluidos

- `batch3_summary.csv`: una fila por caso desde `data/results.sqlite` y `Run.csv`.
- `batch3_productivo.csv`: matriz explicita usada.
- `production_status.json`: estado final del runner.
- `production_log_tail.txt`: tail liviano del log.
- `processed_inventory.csv`: inventario de archivos procesados existentes.
- `processed_run_metrics/`: copias livianas de `Run.csv` y `RunPARTs.csv` por caso.
- `source_manifest.csv`: trazabilidad de origen.

## No incluye

- `cases/` completo.
- `ChronoExchange`, `ChronoBody_forces` ni gauges completos.
- `*.bi4`, `*.ibi4`, VTK, `Part*`, ni carpetas `*_out/`.
