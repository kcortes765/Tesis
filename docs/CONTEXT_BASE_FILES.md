# CONTEXT_BASE_FILES.md

Guia corta para traspasar contexto completo y actualizado de este proyecto a otra IA.

## Objetivo

Evitar que otra IA pierda tiempo leyendo documentos historicos o quede desalineada por la mezcla de:

- diseno original
- implementacion real en `src/`
- resultados historicos de canal 15 m
- campana reiniciada en workstation con canal 30 m

## Orden recomendado de carga

### 1. Reglas y arquitectura base
1. `AGENTS.md`

Por que:
- Resume el proyecto, restricciones fisicas y decisiones tecnicas obligatorias.
- Es el mejor punto de entrada para cualquier agente que vaya a tocar codigo.

### 2. Estado actual del repo y handoff
2. `HANDOFF_AI_CONTEXT.md`
3. `RETOMAR.md`

Por que:
- `HANDOFF_AI_CONTEXT.md` es el documento maestro de contexto actualizado.
- `RETOMAR.md` sirve como resumen ejecutivo para continuidad de trabajo.

### 3. Marco tecnico y cientifico
4. `AUDITORIA_FISICA.md`
5. `EDUCACION_TECNICA.md`
6. `DEFENSA_TECNICA.md`

Por que:
- Fijan la base fisica y numerica que no se debe romper.
- Explican por que se usan Chrono, `massbody`, `FtPause`, inercia de `trimesh`, etc.

### 4. Estado operativo real del software
7. `src/geometry_builder.py`
8. `src/batch_runner.py`
9. `src/data_cleaner.py`
10. `src/main_orchestrator.py`
11. `src/ml_surrogate.py`

Por que:
- El codigo en `src/` es la fuente de verdad para lo que realmente esta implementado.

### 5. Configuracion vigente
12. `config/template_base.xml`
13. `config/param_ranges.json`
14. `config/experiment_matrix.csv`
15. `config/dsph_config.json`

Por que:
- Definen el caso base, la campana LHS y los defaults de ejecucion.

### 6. Datos locales utiles
16. `data/results_ws_15cases.csv`
17. `data/processed/lhs_001/` a `data/processed/lhs_005/`
18. `cases/lhs_001/` a `cases/lhs_005/`

Por que:
- Permiten validar formatos reales de CSV/XML.
- Son historicos y parciales; utiles para ETL y debugging.

## Archivos que SI son base

- `AGENTS.md`
- `HANDOFF_AI_CONTEXT.md`
- `RETOMAR.md`
- `AUDITORIA_FISICA.md`
- `EDUCACION_TECNICA.md`
- `DEFENSA_TECNICA.md`
- `src/*.py`
- `config/template_base.xml`
- `config/param_ranges.json`
- `config/experiment_matrix.csv`
- `data/results_ws_15cases.csv`

## Archivos que NO deben tomarse como unica fuente de verdad

### `PLAN.md`
Usarlo como documento de diseno y riesgos. No como estado actual del proyecto.

### `BRIEFING_LEAD_ARCHITECT.md`
Util como resumen estrategico, pero ya no reemplaza el handoff maestro.

### `data/results.sqlite`
Actualmente esta vacio en este workspace local.

### `data/gp_surrogate.pkl` y `data/figuras_uq/uq_summary.json`
Revisar con cautela. No asumir automaticamente que representan el resultado final de tesis con datos reales reconciliados.

### `tesis/cap1_*` a `cap5_*`
Son base solo si la tarea es escritura de tesis. No si la tarea es reconstruir estado tecnico.

## Paquete minimo para otra IA

Si quieres copiar lo minimo indispensable a otra IA, entrega al menos:

1. `AGENTS.md`
2. `HANDOFF_AI_CONTEXT.md`
3. `RETOMAR.md`
4. `AUDITORIA_FISICA.md`
5. `src/geometry_builder.py`
6. `src/batch_runner.py`
7. `src/data_cleaner.py`
8. `src/main_orchestrator.py`
9. `config/template_base.xml`
10. `config/param_ranges.json`
11. `data/results_ws_15cases.csv`

## Paquete completo recomendado

Si quieres contexto realmente robusto para otra IA:

1. Todo el paquete minimo
2. `EDUCACION_TECNICA.md`
3. `DEFENSA_TECNICA.md`
4. `src/ml_surrogate.py`
5. `config/experiment_matrix.csv`
6. `config/dsph_config.json`
7. `cases/`
8. `data/processed/`
9. `tesis/` si la IA tambien va a escribir o defender la tesis
