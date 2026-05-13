# Prompt WS - Batch4 masa / densidad

Objetivo: ejecutar primero un precheck corto de masa/contacto y, solo si pasa, lanzar batch4 productivo de 12 casos para incorporar la tercera variable fisica m* al surrogate principal `[H, mu, m*]`.

Reglas fijas:
- Resolucion productiva: `dp=0.003 m`.
- Criterio primario: `classification_mode=displacement_only`.
- `reference_time_s=0.5`.
- Rotacion diagnostica, no criterio de falla.
- No usar `run_production.py --pilot --prod`.
- Dry-run siempre con `--prod`; sin `--prod` el script usa `dp_dev=0.02`.

Precheck:
```powershell
python scripts\run_production.py --prod --matrix config\batch4_precheck_mass_sanity_20260510.csv --max-cases 2 --dry-run --no-notify
python scripts\run_production.py --prod --matrix config\batch4_precheck_mass_sanity_20260510.csv --max-cases 2 --no-notify
```

Batch4, solo si pasa el precheck:
```powershell
python scripts\run_production.py --prod --matrix config\batch4_mass_probe_20260510.csv --max-cases 12 --dry-run --no-notify
python scripts\run_production.py --prod --matrix config\batch4_mass_probe_20260510.csv --max-cases 12 --no-notify
```
