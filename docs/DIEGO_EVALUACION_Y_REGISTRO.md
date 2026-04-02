# Diego: evaluacion y registro

> Fecha: 2026-04-02
> Alcance: scripts `Pangea` y `Columbia` entregados por Diego, mas su relacion con esta repo.

## Contexto

La linea de Diego corresponde a una convergencia de malla orientada a postproceso de:

- gauges de velocidad y altura (`Pangea`)
- cinematica y fuerzas del bloque (`Columbia`)

No reemplaza el pipeline principal de esta repo (`src/`, `cases/`, `data/`, `docs/`), pero usa las mismas familias de archivos DualSPHysics/Chrono y por eso conviene dejarla ordenada y tecnicamente alineada.

## Hallazgos principales

1. Los cuatro scripts venian con rutas hardcodeadas a OneDrive de Diego.
2. `Pangea` no limpiaba el valor centinela de DualSPHysics (`-3.40282e+38`) en gauges.
3. `Columbia` parseaba fuerzas de forma fragil, asumiendo posiciones fijas de columnas.
4. La logica de metadatos y limpieza estaba duplicada entre scripts.
5. Los scripts quedaban acoplados a `print()` y al `input()` final, lo que dificulta automatizacion.
6. No existia documentacion interna que dejara trazabilidad de cambios y supuestos.

## Validacion con la repo actual

Se uso `data/processed/test_diego_reference/` como fuente real para revisar formatos:

- `ChronoExchange_mkbound_51.csv` trae separador `;` y, en este caso, solo filas `predictor=False`.
- `ChronoBody_forces.csv` trae headers repetidos por cuerpo (`Body_BLIR_...`, `Body_beach_...`).
- `GaugesMaxZ_hmax03.csv` a `GaugesMaxZ_hmax08.csv` contienen el valor centinela de DualSPHysics.

Ese ultimo punto era el bug mas importante para `Pangea`: sin limpieza, las series quedan contaminadas y cualquier derivada basada en magnitudes puede volverse fisicamente absurda.

## Cambios implementados

1. Se creo `diego/convergence_tools.py` como modulo comun para lectura, limpieza, resumenes, exportacion y graficos.
2. Se mantuvieron las cuatro rutas originales (`armar_*`, `graficar_*`) como wrappers finos para no romper la forma en que Diego los ubica.
3. Se agrego `diego/default_limestone_metadata.csv` para sacar los `dp` del codigo y dejarlos editables.
4. Se agrego `diego/README.md` con uso, estructura y ejemplo de metadatos custom.
5. `Pangea` ahora limpia el centinela de gauges antes de calcular velocidades y Hmax.
6. `Columbia` ahora normaliza el header de `ChronoBody_forces.csv` y selecciona el cuerpo del bloque de forma robusta.
7. `ChronoExchange` ahora filtra filas `predictor=True` si aparecen.
8. Ambos flujos generan respaldos CSV y logs por ejecucion, ademas del Excel.
9. `Columbia` agrega una tabla de errores de convergencia y controla el limite de filas de Excel.

## Archivos modificados o agregados

- `diego/armar_Pangea (1).py`
- `diego/armar_Columbia (1).py`
- `diego/graficar_Pangea (1).py`
- `diego/graficar_Columbia (1).py`
- `diego/convergence_tools.py`
- `diego/default_limestone_metadata.csv`
- `diego/README.md`
- `docs/DIEGO_EVALUACION_Y_REGISTRO.md`

## Decision de organizacion

Se dejo la implementacion nueva dentro de `diego/` y no dentro de `src/` por una razon simple:

- esta linea esta relacionada con la tesis principal, pero sigue siendo una variante separada de postproceso
- conviene compartir criterios tecnicos con la repo principal sin acoplar el pipeline core a una rama de trabajo externa

## Riesgos o mejoras futuras

1. Si Diego usa nombres de casos no numericos, debe pasar `--metadata-file` o editar `default_limestone_metadata.csv`.
2. Si aparecen mas de dos cuerpos en `ChronoBody_forces.csv`, el parametro `--body-hint` permite elegir el correcto.
3. Si despues se quiere integrar esto con SQLite o con los reportes de `src/data_cleaner.py`, ya hay una base comun de parsing para hacerlo sin reescribir los wrappers.
