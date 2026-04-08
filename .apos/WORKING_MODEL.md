# WORKING_MODEL — Thesis OS

**Última actualización:** 2026-04-08

## Comprensión vigente

### Thread 1 — Pipeline y física actual
El pipeline 5D vigente usa canal paramétrico, slope variable, fricción Chrono y posición del boulder derivada geométricamente. La convergencia de Fase 2 no puede transferirse automáticamente porque resolvía otro problema numérico.

### Thread 2 — Screening 5D
R1 y R2 ya cumplieron su rol exploratorio. R2 mostró que fricción domina, masa es secundaria y la frontera es multidimensional. Round 3 quedó diseñado para verificar rotación, transición y descomposición de casos sorpresa, pero está en espera hasta cerrar el dp.

### Thread 3 — Convergencia dp v2
La convergencia nueva ya corrió en WS con 7/8 niveles exitosos (`0.010` a `0.002`; `0.0015` falló en GenCase). El forcing hidráulico y el onset parecen converger bastante bien entre `0.004`, `0.003` y `0.002`. La trayectoria post-falla a 10 s no converge limpio en el caso Moris (`dam_h=0.30`), especialmente en desplazamiento máximo y respuesta rotacional.

### Thread 4 — Métricas y criterio científico
La tesis es sobre incipient motion, no sobre trayectoria completa de transporte masivo. Por eso hay una tensión real entre:
- lo que hoy mide la convergencia v2 (`max_displacement`, `max_velocity`, `SPH force` pico a 10 s)
- y lo que realmente importa para la pregunta científica (onset, cruce de umbral, clasificación ESTABLE/FALLO cerca de la frontera)

### Thread 5 — Limitaciones de observables
`max_rotation` actual no es ángulo neto físico: integra `|omega|`, así que acumula rocking aunque revierta. `SPH force` pico es muy sensible a spikes locales y no es una primaria robusta para cerrar resolución fina en este caso. El forcing hidráulico (`flow`, `water_h`) es útil como diagnóstico de que la ola ya está resuelta.

### Thread 6 — Estado metodológico
La lectura más honesta de la v2 es:
- no falló el solver
- no falló toda la convergencia
- sí falló la expectativa de que una trayectoria post-falla larga en un caso fuertemente inestable converja monótonamente

La pregunta abierta ya no es “¿corre?” sino “¿con qué observable debo justificar el dp de producción?”.

## Tensiones actuales
- **Onset vs trayectoria** — el observable de convergencia puede estar mal alineado con la tesis
- **Caso Moris vs frontera** — el caso de referencia del profe no necesariamente es el caso más informativo para cerrar dp
- **Rigor vs costo** — `dp=0.002` aporta información, pero cuesta muchísimo; `dp=0.003` es mucho más utilizable para campaña
- **Persistencia** — el log dice que SQLite guardó `convergence_v2`, pero la base local no lo refleja

## Hipótesis operativa
1. Aclarar con Moris si el dp se defenderá con métricas de onset o con trayectoria completa
2. Si onset basta, explotar la v2 ya corrida y justificar `dp=0.003`
3. Si quiere cierre en frontera, correr una v3 corta (`0.004`, `0.003`, `0.002`) en 1–2 casos cerca del umbral
4. Luego lanzar Round 3 con el dp ya defendido

## Qué no hacer
- No tratar la convergencia vieja como si fuera evidencia directa para el setup 5D
- No declarar `dp=0.003` cerrado solo porque `0.004→0.003` fue chico
- No usar `max_rotation` actual como observable principal
- No confundir “caso Moris” con “caso óptimo para convergencia de incipient motion”
