# Export liviano - piloto productivo 2026-05-01

Este paquete contiene solo artefactos livianos para auditar y sincronizar por Git el piloto productivo de 5 casos.

## Incluye

- `pilot_summary.csv`: tabla maestra de una fila por caso, construida desde `data/results.sqlite` y `RunPARTs.csv`.
- `pilot_summary.md`: interpretacion corta.
- `pilot_productivo_20260430.csv`: matriz original del piloto.
- `production_status.json`: estado final del runner.
- `production_log_tail.txt`: tail relevante del log de produccion.
- `processed_inventory.csv`: inventario de CSVs procesados livianos/pesados existentes.
- `processed_run_metrics/`: solo `Run.csv` y `RunPARTs.csv` por caso.
- `source_manifest.csv`: archivos fuente auditados.

## No incluye

- `cases/`
- `*_out/` completos
- `*.bi4`, `*.ibi4`, VTK o `Part*`
- Chrono/Gauges completos salvo inventario
- binarios DualSPHysics

## Fuente de verdad

- SQLite: `data/results.sqlite`, tabla `results`, filas `prod_pilot_%`.
- Estado: `data/production_status.json`.
- Log: `data/production_20260430_1758.log`.

## Nota

Este export es para sincronizacion y auditoria. Para reprocesar series temporales completas, usar la WS con `data/processed/prod_pilot_*` o `cases/prod_pilot_*`, no este paquete.
