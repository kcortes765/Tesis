# Export liviano AL batch1 hibrido

Este directorio contiene artefactos livianos para sincronizar por Git. No incluye binarios DualSPHysics pesados, VTK, Part*, ni carpetas `_out` completas.

## Contenido

- `al_batch1_summary.csv`
- `al_batch1_summary.md`
- `results_sqlite_al_batch1_extract.csv`
- `production_status.json`
- `production_log_tail.txt`
- `al_batch1_hybrid_20260513.csv`
- `processed_inventory.csv`
- `processed_run_metrics/*/Run.csv` y `RunPARTs.csv` cuando existen
- `source_manifest.csv`

## Nota metodologica

AL batch1 es produccion dirigida post batch4, no convergencia de `dp` ni sensibilidad de forma. La resolucion operativa se mantiene en `dp=0.003`.
