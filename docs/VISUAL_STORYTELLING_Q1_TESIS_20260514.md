# Guia visual Q1 para figuras de tesis

Fecha: 2026-05-14

Objetivo: definir una gramatica visual reproducible para las figuras de
convergencia, produccion y active learning de la tesis. Esta guia no reemplaza
los datos; traduce buenas practicas de visualizacion cientifica en reglas
concretas para este repositorio.

## Fuentes revisadas

- Rougier, Droettboom y Bourne (2014), "Ten Simple Rules for Better Figures",
  PLOS Computational Biology. https://doi.org/10.1371/journal.pcbi.1003833
- Crameri, Shephard y Heron (2020), "The misuse of colour in science
  communication", Nature Communications. https://doi.org/10.1038/s41467-020-19160-7
- Segel y Heer (2010), "Narrative Visualization: Telling Stories with Data",
  IEEE TVCG. https://doi.org/10.1109/TVCG.2010.179
- Franconeri, Padilla, Shah, Zacks y Hullman (2021), "The Science of Visual
  Data Communication: What Works", Psychological Science in the Public Interest.
  https://doi.org/10.1177/15291006211051956

## Principios adoptados

1. Una figura, una pregunta.
   - Cada figura debe responder una pregunta concreta: frontera, sensibilidad,
     costo, diagnostico de rotacion, hidraulica local o efecto de masa.
   - Evitar figuras que intenten demostrar todo a la vez.

2. Dato normalizado siempre con unidad fisica.
   - Si aparece `Dmax (% d_eq)`, debe aparecer tambien su equivalente absoluto
     en mm.
   - Umbral principal: `5% d_eq = 5.02 mm`.
   - Los graficos de margen deben mostrar margen porcentual y margen absoluto.

3. Color no debe distorsionar el dato.
   - Evitar rainbow y mapas no uniformes.
   - Usar mapas perceptualmente razonables (`viridis`, `cividis`) para variables
     continuas.
   - Para clases discretas usar color mas forma:
     - azul + circulo: ESTABLE;
     - vermillion + triangulo: FALLO.
   - No depender solo de rojo/verde.

4. La clase no debe ocultar el margen.
   - Mostrar `g = 5% - Dmax/d_eq` como variable continua.
   - La clase ESTABLE/FALLO sirve para lectura rapida, pero el margen explica
     cercania al umbral.

5. Los outliers se declaran, no se esconden.
   - Si un fallo extremo aplasta la escala de frontera, se usa zoom operativo y
     se marca explicitamente "caso extremo fuera de escala".
   - El valor completo queda en el CSV maestro.

6. La narrativa visual debe ir por capas.
   - Capa 1: convergencia/resolucion (`dp=0.003` como operativa, no verdad
     asintotica universal).
   - Capa 2: frontera operacional H-mu-m*.
   - Capa 3: hidraulica local y fuerzas diagnosticas.
   - Capa 4: rotacion como diagnostico, no criterio primario.
   - Capa 5: costo computacional y justificacion de active learning.
   - Capa 6: surrogate/uncertainty, cuando este entrenado.

7. No interpolar sin decirlo.
   - Puntos simulados son evidencia discreta.
   - Lineas entre puntos son guias visuales.
   - Superficies o mapas continuos deben venir de GP/surrogate con incertidumbre
     y validacion.

8. Legibilidad antes que decoracion.
   - Fondo blanco, grilla leve, tipografia consistente, leyendas cortas.
   - Evitar etiquetas de caso en todos los puntos; usar CSV/tabla para detalle.
   - En slides, preferir 1 idea por lamina y graficos con poco texto embebido.

## Aplicacion actual en el repo

### Convergencia

Carpeta:

`data/figures/derived_convergence_graphics/`

Reglas aplicadas:

- Todo eje en `% d_eq` tiene equivalente en mm o anotacion absoluta.
- El umbral se rotula como `5% d_eq = 5.02 mm`.
- La rotacion se muestra como diagnostico separado.
- `dp=0.003` se comunica como resolucion operativa, no como convergencia
  perfecta.

### Produccion y active learning

Carpeta:

`data/figures/production_story_graphics/`

Fuente de datos:

- `exports/pilot_productivo_20260501/pilot_summary.csv`
- `exports/batch2_productivo_20260505/batch2_summary.csv`
- `exports/batch3_productivo_20260509/batch3_summary.csv`
- `exports/batch4_mass_probe_20260513/batch4_summary.csv`
- `exports/al_batch1_hybrid_20260514/al_batch1_summary.csv`

AL2 no se incluye hasta que tenga export oficial.

Archivos clave:

- `master_production_story.csv`
- `FIGURE_INDEX.md`
- `01_response_map_h_mu_by_mass`
- `02_margin_vs_mu_by_mass_and_h`
- `03_batch_story_margin_strip`
- `04_local_hydraulics_vs_displacement`
- `06_rotation_diagnostic_vs_displacement`

## Figuras recomendadas para tesis/defensa

1. Convergencia: figura resumen de sensibilidad de resolucion.
2. Convergencia: figura de frontera practica en `dp=0.003`.
3. Produccion: mapa H-mu por masa relativa.
4. Produccion: margen continuo contra mu por masa/H.
5. Produccion: historia de lotes desde piloto a AL1.
6. Produccion: hidraulica local vs desplazamiento.
7. Produccion: rotacion diagnostica vs desplazamiento.
8. Costo: costo computacional por lote o por dp.

## Frases metodologicas sugeridas

> Las figuras reportan la frontera operacional a `dp=0.003 m`; esta resolucion
> fue seleccionada por sensibilidad de resolucion y costo computacional, no como
> prueba de convergencia asintotica universal.

> El criterio primario es el desplazamiento maximo relativo al diametro
> equivalente (`Dmax > 5% d_eq`, equivalente a 5.02 mm). La rotacion acumulada se
> reporta como diagnostico dinamico, pero no define por si sola la clase.

> Los casos extremos se mantienen en el dataset maestro y se indican en figuras
> de frontera como fuera de escala para preservar legibilidad sin ocultar
> evidencia.

