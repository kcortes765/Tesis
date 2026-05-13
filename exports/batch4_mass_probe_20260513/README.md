# Export liviano batch4 mass probe

Este directorio contiene solo artefactos livianos y trazables para sincronizar por Git. No incluye binarios DualSPHysics pesados (`.bi4`, `.vtk`, `Part*`, carpetas `_out` completas).

## Contenido

- `batch4_summary.csv`
- `batch4_summary.md`
- `batch4_precheck_summary.csv`
- `batch4_case12_partial_recovery.csv` si existe recuperacion parcial
- `results_sqlite_batch4_extract_plus_partial.csv`
- `production_status.json`
- `production_log_tail.txt`
- `config/batch4_*.csv` copiados en raiz del export
- `processed_inventory.csv`
- `processed_run_metrics/*/Run.csv` y `RunPARTs.csv` cuando existen
- `source_manifest.csv`

## Advertencia

El batch4 quedo con 11/12 casos oficiales en SQLite. El caso 12 (`batch4_mass_m125_H0225_mu0860`) tiene CSVs crudos parciales y se entrega como diagnostico, no como resultado oficial completo.
