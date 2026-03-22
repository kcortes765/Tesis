# Coding Prompt — SPH-IncipientMotion

## Reglas de codigo

1. **Python 3.8 compatible** — no usar `:=` (walrus), `match/case`, `type[X, Y]` (usar `Tuple[X, Y]` de typing o `from __future__ import annotations`)
2. **Imports al inicio** — nunca imports dentro de funciones excepto para dependencias opcionales
3. **Logging, no print** — usar `logging.getLogger(__name__)` para toda info del pipeline
4. **Docstrings** — solo en funciones publicas, formato Google style
5. **Type hints** — usar `from __future__ import annotations` al inicio si usas syntax moderna
6. **CSV separador `;`** — todos los CSVs de DualSPHysics usan punto y coma: `pd.read_csv(path, sep=';')`
7. **Sentinel → NaN** — valores `-3.40282e+38` en Gauges son "sin dato", reemplazar con `np.nan`

## Estructura de modulos

- Cada modulo en `src/` es independiente con su propio `if __name__ == '__main__'` para test
- Imports entre modulos: `from geometry_builder import CaseParams, build_case`
- Config siempre via `config/dsph_config.json` cargado con `batch_runner.load_config()`

## Verificacion

Antes de marcar la feature como completada:
1. El codigo debe ejecutar sin errores de sintaxis (`python -c "import modulo"`)
2. Si hay tests, deben pasar
3. Si genera archivos, verificar que existen y tienen contenido
4. Hacer commit con mensaje descriptivo: `feat(ID): descripcion`

## Que NO hacer

- NO refactorizar codigo existente que funciona — solo agregar/modificar lo pedido
- NO cambiar `config/template_base.xml` ni `config/dsph_config.json` sin razon explicita
- NO borrar archivos en `data/processed/` ni `cases/`
- NO instalar dependencias nuevas sin verificar que existen (`pip install` puede fallar headless)
- NO crear archivos markdown/docs a menos que la feature lo pida explicitamente
- NO hacer cambios cosmeticos (renombrar variables, agregar comments, reformatear)
