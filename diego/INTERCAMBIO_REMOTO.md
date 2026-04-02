# Intercambio remoto con el PC de Diego

Este flujo sirve para investigar una carpeta remota en otro PC y traer solo lo necesario a esta maquina.

## Archivos

- `intercambio_remoto.ps1`: inventario y exportacion selectiva.
- `seleccion_remota_ejemplo.txt`: plantilla de seleccion.

## Fase 1: inventario completo

En el PC de Diego:

```powershell
powershell -ExecutionPolicy Bypass -File .\intercambio_remoto.ps1 `
  -RootPath "C:\ruta\real\de\Diego" `
  -Mode inventory `
  -OutDir "C:\ruta\salida\diego_exchange_inventory"
```

Eso genera una carpeta con:

- `inventory_manifest.csv`
- `inventory_manifest.json`
- `inventory_tree.txt`
- `inventory_by_extension.csv`
- `inventory_by_top_level.csv`
- `session_info.json`

Traeme esa carpeta y con eso te digo exactamente que pedir en la siguiente vuelta.

## Fase 2: exportacion selectiva

Despues de revisar el inventario, preparamos un archivo de seleccion y en el PC de Diego se corre:

```powershell
powershell -ExecutionPolicy Bypass -File .\intercambio_remoto.ps1 `
  -RootPath "C:\ruta\real\de\Diego" `
  -Mode export `
  -SelectionFile ".\seleccion_remota_ejemplo.txt" `
  -OutDir "C:\ruta\salida\diego_exchange_export"
```

Eso genera:

- manifiestos de inventario
- `selected_manifest.csv`
- `selected_tree.txt`
- `payload\...` con la misma estructura relativa que tenia la carpeta original

## Recomendacion practica

1. Primera vuelta: solo `inventory`.
2. Revisamos aqui el manifest.
3. Te devuelvo una seleccion concreta.
4. Segunda vuelta: `export`.
5. Si falta algo, repetimos con otra seleccion sin tocar el inventario original.
