# AL batch1 hibrido - resumen liviano

Fecha de export: 2026-05-14

## Estado

- Matriz objetivo: 8 casos productivos con `dp=0.003`.
- Casos oficiales postprocesados en SQLite: 8/8.
- Fallos numericos: 0.
- Tiempo total reportado: 34.37 h.
- Criterio primario: `displacement_only`; rotacion diagnostica.

## Conteo por estado/clase

| status | criterion_class | n |
|---|---:|---:|
| OK_SQLITE | ESTABLE | 7 |
| OK_SQLITE | FALLO | 1 |

## Lectura tecnica corta

AL batch1 fue un lote hibrido orientado por GP seed y brackets fisicos. El lote produjo 1 FALLO y 7 ESTABLE por desplazamiento. El unico fallo fue: al1_base_m085_mu0780.

El resultado ayuda a cerrar regiones donde batch4 dejo incertidumbre: masa alta y media estabilizan varios puntos incluso en H medio/alto, mientras masa baja en condicion base aun puede fallar al subir la friccion a `mu=0.780`.

## Archivos clave

- `al_batch1_summary.csv`: tabla principal de los 8 casos.
- `results_sqlite_al_batch1_extract.csv`: extracto directo de SQLite en columnas normalizadas.
- `production_status.json`: estado final del runner.
- `production_log_tail.txt`: cola del log productivo.
- `processed_inventory.csv`: inventario liviano de outputs procesados.
