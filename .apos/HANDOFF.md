# HANDOFF — Thesis OS

**Última sesión:** 2026-04-08 (sesión 10)

## Qué se hizo

### Convergencia dp v2 corrida e importada
- La WS ejecutó `scripts/run_convergence_v2.py` y se importaron 7/8 casos exitosos.
- Resultados disponibles en `data/results/convergencia_v2.csv`, `data/results/convergencia_v2_gci.json`, `data/logs/convergencia_v2.log` y `data/results/convergencia_v2_temporal/`.
- `dp=0.0015` falló en GenCase; `dp=0.001` no se corrió.

### Diagnóstico técnico de la convergencia nueva
- El forcing hidráulico converge bien en los dp finos: `max_flow_velocity` y `max_water_height` cambian muy poco entre `dp=0.004`, `0.003` y `0.002`.
- El onset también converge razonablemente: los tiempos de cruce de `5% d_eq` y `50 mm` son muy cercanos entre `dp=0.004`, `0.003` y `0.002`.
- Lo que NO converge limpio es la trayectoria post-falla a 10 s del caso Moris (`dam_h=0.30`): `max_displacement` baja de `1.966 m` a `1.753 m` entre `dp=0.003` y `0.002`, y la respuesta rotacional cambia de rama.
- `SPH force` pico es oscilatoria y no sirve como primaria robusta para decidir dp en este caso.
- La métrica actual de rotación acumula `|omega|`, no ángulo neto; sirve como diagnóstico bruto, pero no como observable fino.

### Revisión de la convergencia anterior
- La convergencia anterior SÍ llegó a `dp=0.003` y fue válida para su configuración original.
- No es transferible a la configuración actual 5D: canal paramétrico, slope, fricción Chrono y nueva posición del bloque cambian el problema numérico.
- Se detectó desalineación de trazabilidad: los documentos finales viejos muestran 7 dp, pero algunos scripts versionados aún reflejan una etapa intermedia.

### Preparación para reunión con Moris
- Se armó la línea técnica: el problema no parece ser el solver, sino la métrica elegida para convergencia.
- La pregunta central para el profe es si el dp debe justificarse con métricas de onset/incidental motion o con trayectoria completa post-falla.

## Qué cambió
- `data/results/convergencia_v2.csv` — tabla consolidada de convergencia nueva
- `data/results/convergencia_v2_gci.json` — GCI / Richardson v2
- `data/results/convergencia_v2_temporal/` — series temporales exchange/forces por dp
- `data/logs/convergencia_v2.log` — log completo de ejecución
- `scripts/analisis_convergencia_v2.py` — análisis local profundo de la v2
- `data/figures/convergencia_v2_analisis.md` + figuras `conv2_*` — diagnóstico visual y textual

## Qué debe hacer el siguiente agente
1. Tomar la reunión con Moris y aclarar criterio metodológico:
   - ¿Definir dp por onset/incidental motion o por trayectoria completa post-falla?
   - ¿Quiere validación cerca de la frontera ESTABLE/FALLO?
2. Si el profe acepta onset como criterio principal:
   - extraer formalmente las métricas de onset de la v2 ya corrida
   - redactar el argumento metodológico para justificar `dp=0.003` como resolución de trabajo
3. Si el profe pide cierre riguroso en frontera:
   - diseñar una convergencia v3 corta con `dp=0.004`, `0.003`, `0.002` en 1–2 casos cerca del umbral
4. Corregir persistencia/documentación secundaria:
   - revisar por qué el log reporta guardado en `convergence_v2` pero la `results.sqlite` local no muestra esa tabla
   - dejar una versión reproducible y limpia del análisis viejo/nuevo

## Qué no debe asumir
- La convergencia v2 NO “falló” en bloque; mostró convergencia de forcing/onset pero no de trayectoria post-falla larga.
- `dp=0.003` todavía NO está cerrado formalmente como producción en la configuración nueva.
- La convergencia anterior no está invalidada históricamente; está invalidada como evidencia transferible al setup actual.
- `max_rotation` actual no representa un ángulo neto físico; integra `|omega|`.
- `dp=0.0015` no es una referencia útil de convergencia: falló en GenCase y su escalamiento apunta a límite de memoria/tamaño.

## Contexto mínimo para retomar
Leer: `BOOTSTRAP.md` → este `HANDOFF.md` → `data/results/convergencia_v2.csv` → `data/logs/convergencia_v2.log` → `data/figures/convergencia_v2_analisis.md` → `.apos/DECISIONS.md`
