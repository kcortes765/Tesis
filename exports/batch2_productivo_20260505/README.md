# Export liviano batch2 productivo 20260505

Este paquete resume el lote chico `batch2` sin copiar outputs pesados de DualSPHysics.

## Incluye

- `batch2_summary.csv`: una fila por caso, desde `data/results.sqlite` y metricas `Run.csv`.
- `batch2_summary.md`: lectura cientifica corta y conservadora.
- `batch2_productivo_20260503.csv`: matriz explicita usada para el lote.
- `production_status.json`: estado final de la ejecucion.
- `production_log_tail.txt`: tail relevante del log productivo.
- `processed_inventory.csv`: inventario liviano de archivos procesados.
- `processed_run_metrics/`: solo `Run.csv` y `RunPARTs.csv` por caso.
- `source_manifest.csv`: origen de cada artefacto exportado.

## No incluye

- `cases/`.
- `ChronoExchange`, `ChronoBody_forces` ni gauges completos.
- `*.bi4`, `*.ibi4`, VTK, `Part*`, ni carpetas `*_out/`.

## Estado

- Final: completed.
- OK: 8/8.
- Fallos numericos: 0.
- Tiempo total: 34.55 h.
