# Batch4 mass probe - resumen liviano

Fecha de export: 2026-05-13

## Estado

- Matriz objetivo: 12 casos productivos con `dp=0.003`.
- Casos oficiales postprocesados en SQLite: 11/12.
- Casos recuperados parcialmente desde CSV crudos: 1/12.
- Caso parcial: `batch4_mass_m125_H0225_mu0860`, con `sim_time_reached` menor a 10 s; usar solo como diagnostico hasta repetir o reprocesar oficialmente.
- Precheck masa/contacto: 2/2 OK en `batch4_precheck_summary.csv`.

## Conteo por estado/clase

| status | criterion_class | n |
|---|---:|---:|
| OK_SQLITE | ESTABLE | 6 |
| OK_SQLITE | FALLO | 5 |
| PARTIAL_RECOVERED_NOT_SQLITE | ESTABLE | 1 |

## Lectura tecnica corta

Batch4 incorpora `boulder_mass` como tercera variable fisica junto a `dam_height` y `friction_coefficient`. Los 11 casos oficiales muestran transicion clara: masas menores (`0.85 kg`) fallan con desplazamientos altos en varios escenarios, mientras masas mayores estabilizan gran parte del dominio ensayado.

El caso 12 no fue guardado por el runner en `data/processed` ni en SQLite. Hay CSVs crudos hasta aproximadamente 9.5 s y se entrega una recuperacion parcial separada para no perder informacion, pero no debe mezclarse como resultado oficial completo.

## Archivos clave

- `batch4_summary.csv`: tabla principal, 11 oficiales + caso 12 parcial marcado.
- `batch4_precheck_summary.csv`: sanity de masa/contacto.
- `batch4_case12_partial_recovery.csv`: recuperacion diagnostica del caso 12.
- `production_status.json`: estado del runner al cierre observado.
- `production_log_tail.txt`: cola del log productivo.
- `processed_inventory.csv`: inventario liviano de outputs procesados.
