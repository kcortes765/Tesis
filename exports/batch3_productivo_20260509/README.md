# Export liviano batch3 productivo 20260509

Este paquete resume el lote `batch3` sin copiar outputs pesados de DualSPHysics.

## Incluye

- `batch3_summary.csv`: metricas principales por caso.
- `batch3_summary.md`: lectura cientifica corta y conservadora.
- `batch3_productivo.csv`: matriz explicita usada para el lote.
- `production_status.json`: estado final de ejecucion.
- `production_log_tail.txt`: tail liviano del log productivo.
- `processed_inventory.csv`: inventario liviano de archivos procesados.
- `processed_run_metrics/`: solo `Run.csv` y `RunPARTs.csv` por caso.
- `source_manifest.csv`: origen de cada artefacto exportado.

## Estado

- Final: completed.
- OK: 10/10.
- Fallos numericos: 0.
- Tiempo total: 42.03 h.

## Lectura central

Batch3 afina la frontera base cerca de `mu=0.68`: con H=0.20 y pendiente 1:20, `mu=0.680` falla y `mu=0.682` queda estable. La altura hidraulica domina: H=0.175 queda estable en el rango probado, mientras H=0.210 y H=0.225 fallan incluso con fricciones altas.
