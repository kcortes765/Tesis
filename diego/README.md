# Diego

Scripts y utilidades para la linea de analisis de Diego.

## Que hay aca

- `armar_Pangea (1).py`: consolida `GaugesVel_V*.csv` y `GaugesMaxZ_hmax*.csv`.
- `armar_Columbia (1).py`: consolida `ChronoExchange_mkbound_*.csv` y `ChronoBody_forces.csv`.
- `graficar_Pangea (1).py`: genera figuras de convergencia para velocidades y Hmax.
- `graficar_Columbia (1).py`: genera figuras de convergencia para desplazamiento, velocidad y fuerzas.
- `convergence_tools.py`: modulo comun con lectura, limpieza, resumenes y exportacion.
- `default_limestone_metadata.csv`: metadatos base para los casos `00001` a `00010`.
- `intercambio_remoto.ps1`: inventario remoto y exportacion selectiva para traer datos desde otro PC.
- `INTERCAMBIO_REMOTO.md`: flujo recomendado para el ida y vuelta con el PC de Diego.

## Mejoras incluidas

- Limpieza del valor centinela de DualSPHysics en gauges (`-3.40282e+38`).
- Filtro de filas `predictor=True` en `ChronoExchange` si llegan a existir.
- Parseo robusto de `ChronoBody_forces.csv`, incluso con headers repetidos por cuerpo.
- Rutas configurables por CLI o variable `DIEGO_BASE_DIR`.
- Logs por ejecucion y respaldos CSV para no depender solo de Excel.
- Conservacion de las rutas originales de los cuatro scripts.

## Uso rapido

```powershell
python "C:\Seba\Tesis\diego\armar_Pangea (1).py" --base-dir "C:\ruta\a\casos"
python "C:\Seba\Tesis\diego\graficar_Pangea (1).py" --base-dir "C:\ruta\a\casos"
python "C:\Seba\Tesis\diego\armar_Columbia (1).py" --base-dir "C:\ruta\a\casos"
python "C:\Seba\Tesis\diego\graficar_Columbia (1).py" --excel-path "C:\ruta\a\casos\Columbia_Limestone.xlsx"
```

## Metadatos custom

Si los casos no se llaman `00001` ... `00010`, usa un CSV o JSON con columnas:

- `caso`
- `dp`
- `material`
- `observaciones`

Ejemplo:

```csv
caso,dp,material,observaciones
test_diego_reference,0.0200,limestone,caso de validacion local
```

Luego:

```powershell
python "C:\Seba\Tesis\diego\armar_Pangea (1).py" --base-dir "C:\Seba\Tesis\data\processed" --cases test_diego_reference --metadata-file "C:\ruta\metadata.csv"
```
