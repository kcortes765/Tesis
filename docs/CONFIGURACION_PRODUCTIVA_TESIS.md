# Configuracion productiva oficial para la tesis

## Objetivo

Este documento fija la configuracion numerica y metodologica que se usara como base para la campana productiva de simulaciones SPH de movimiento incipiente de bloques. Su proposito es evitar que la campana dependa de memoria, comandos sueltos o decisiones implicitas.

La configuracion se apoya en los resultados locales de convergencia/frontera guardados en:

- `data/results/conv_edge_*.csv`
- `data/results/conv_reassure_*.csv`
- `data/results/conv_repeat_*.csv`
- `data/results/conv_probe_dp002_f06625.csv`
- `data/results.sqlite`
- `data/figures/derived_convergence_graphics/`

No se usan binarios pesados ni archivos `Part*.bi4` como fuente metodologica de esta decision.

## Decision principal

Se adopta `dp = 0.003 m` como malla operativa para la campana productiva.

La evidencia principal es la frontera practica observada en `dp=0.003`, donde la transicion por desplazamiento queda acotada entre:

- `mu = 0.68050`: `FALLO`
- `mu = 0.68075`: `ESTABLE`

La estimacion interpolada de la frontera puede reportarse como valor auxiliar, pero la conclusion defendible es el bracket practico y no un valor critico absoluto.

El refinamiento `dp=0.002` se conserva como evidencia diagnostica de sensibilidad de resolucion. En particular, el caso `conv_probe_dp002_f06625_dp0002` termino `OK` y fue `ESTABLE` por desplazamiento:

- `mu = 0.6625`
- `dp = 0.002 m`
- `max_displacement = 0.002837 m`
- `disp_pct_deq = 2.82%`
- `moved = False`
- `rotated = True`
- `criterion_class = ESTABLE`

Esto muestra que, al refinar a `dp=0.002`, la transicion aparente se desplaza hacia fricciones menores. No se presenta como convergencia asintotica fuerte.

## Definicion de `dp`

`dp` es el espaciamiento inicial de particulas usado por GenCase/DualSPHysics para discretizar el fluido, las fronteras y el cuerpo rigido. Reducir `dp` aumenta fuertemente el costo computacional.

En los resultados de frontera:

- `dp=0.003` entrega una frontera practica compacta y util para la tesis.
- `dp=0.002` aumenta el costo por corrida a alrededor de 19 h en la WS y cambia la respuesta cerca del umbral.
- La no monotonia observada no debe ocultarse ni presentarse como una prueba formal de convergencia.

Por balance entre trazabilidad, costo y estabilidad metodologica, `dp=0.003` queda congelado como malla productiva.

## Criterio de clasificacion

La campana productiva usara:

- `classification_mode = displacement_only`
- `reference_time_s = 0.5`
- umbral de desplazamiento: `5% d_eq`

La clase se define por el desplazamiento maximo del centro de masa del bloque respecto de la referencia temporal:

- `moved = max_displacement > 0.05 * d_eq`
- `ESTABLE` si `moved = False`
- `FALLO` si `moved = True`

La rotacion se calcula y reporta como diagnostico, pero no define la clase final bajo `displacement_only`.

## Referencia temporal

`reference_time_s = 0.5` fija la posicion de referencia despues del periodo inicial de asentamiento gravitacional (`FtPause=0.5`). Esto evita medir como desplazamiento de falla ajustes iniciales asociados al contacto y al settling del cuerpo antes del impacto hidrodinamico.

El postproceso guarda la referencia usada como `criterion_reference_time_s`.

## Geometria oficial

La geometria productiva es la configuracion corregida:

- canal/playa parametrico con pendiente controlada;
- bloque `BLIR3.stl` escalado a `0.04`;
- bloque alineado con la pendiente mediante rotacion de pitch;
- apoyo ajustado para contacto exacto sobre la playa;
- cuerpo rigido con Chrono (`RigidAlgorithm=3`);
- STL rellenado con `fillbox void`;
- masa impuesta con `massbody`;
- inercia calculada desde la geometria escalada/rotada;
- gauges reubicados automaticamente segun la posicion del bloque.

Para la pendiente base `1:20`, la rotacion de pitch usada es aproximadamente:

- `boulder_rot = (0.0, -2.8624 deg, rot_z)`

La posicion base del bloque se obtiene desde `src/canal_generator.py` y se mantiene trazable desde los scripts de corrida.

## Parametros congelados

Valores operativos para la campana productiva:

| Parametro | Valor productivo | Nota |
|---|---:|---|
| `dp` | `0.003 m` | Malla operativa adoptada |
| `classification_mode` | `displacement_only` | Criterio primario |
| `reference_time_s` | `0.5 s` | Referencia post-settling |
| `disp_threshold_pct` | `5% d_eq` | Umbral de movimiento |
| `rot_threshold_deg` | `5 deg` | Solo diagnostico |
| `time_max` | `10.0 s` | Default validado en convergencia |
| `ft_pause` | `0.5 s` | Settling gravitacional |
| `chrono_savedata` | `0.001 s` | Frecuencia de salida Chrono |
| `material` | `pvc` | Material Chrono usado por el wrapper |
| `dam_length` | `1.5 m` | Default del wrapper de frontera |
| `slope_inv` base | `20` | Puede ser variable del Formulario B |
| `mass` base | `1.0 kg` | Puede ser variable del Formulario B |
| `friction` | variable | Variable central de frontera |
| `rot_z` | variable o `0 deg` base | Orientacion del bloque |

Los parametros que formen parte del espacio parametrico de la tesis deben declararse explicitamente en la matriz de diseno. Los demas deben quedar fijos al valor productivo indicado.

## Salidas del modelo

Salida fisica principal recomendada:

- `max_displacement_m`
- margen al umbral: `max_displacement_m - 0.05*d_eq`

Salida de clasificacion:

- `criterion_class` bajo `displacement_only`

Salidas diagnosticas:

- `max_rotation_deg`
- `max_sph_force_N`
- `max_contact_force_N`
- `max_velocity_ms`
- `max_flow_velocity_ms`
- `max_water_height_m`

Las metricas de gauges y fuerzas no deben reemplazar al desplazamiento del bloque como evidencia principal de movimiento incipiente.

## Trazabilidad de scripts y salidas

Scripts relevantes:

- `scripts/run_convergence_threshold.py`: wrapper usado para convergencia/frontera; acepta `--classification-mode` y `--reference-time`.
- `scripts/run_convergence_v2.py`: infraestructura base reutilizada por el wrapper.
- `src/geometry_builder.py`: genera XML/STL de caso, ajusta apoyo, masa, inercia, `FtPause`, `TimeMax`, `chrono_savedata` y gauges.
- `src/canal_generator.py`: define canal, pendiente, posicion y rotacion base del bloque.
- `src/data_cleaner.py`: procesa Chrono/Gauges, calcula desplazamiento/rotacion y clasifica.
- `scripts/generate_convergence_graphics.py`: genera figuras/tablas derivadas de convergencia.

Nota de implementacion: `src/main_orchestrator.py` queda configurado para llamar `process_case(...)` con `classification_mode="displacement_only"` y `reference_time_s=0.5` en el flujo productivo.

Salidas esperadas por corrida:

- CSV consolidado en `data/results/<prefix>.csv`
- GCI JSON si aplica en `data/results/<prefix>_gci.json`
- logs en `data/logs/<prefix>.log`
- tabla SQLite `convergence_<prefix>` en `data/results.sqlite`
- temporales livianos si el script los guarda

Convencion recomendada de nombres:

- `prod_<batch>_dh<...>_m<...>_mu<...>_s<...>_rz<...>`

La convencion final debe quedar fijada antes del piloto productivo.

## Estado final de convergencia

La etapa de convergencia se cierra de forma conservadora:

1. `dp=0.003` se adopta como malla operativa.
2. La frontera practica de `dp=0.003` queda acotada entre `mu=0.68050` y `mu=0.68075`.
3. `dp=0.002` demuestra sensibilidad de resolucion y desplaza la transicion aparente a fricciones menores.
4. El caso `conv_probe_dp002_f06625` confirma que no se localizo un bracket fino en `dp=0.002` dentro del rango perseguido.
5. No se continuara persiguiendo la frontera fina en `dp=0.002` para esta etapa.

## Que no se afirma

No afirmar:

- convergencia asintotica fuerte;
- un `mu_crit` absoluto independiente de resolucion;
- que la rotacion define la clase bajo `displacement_only`;
- que fuerzas, contacto o gauges son criterio primario de movimiento;
- que `dp=0.002` invalida la malla productiva.

Si se reporta un valor interpolado de `mu_crit`, debe presentarse como estimacion local auxiliar subordinada al bracket observado.

## Proximo paso

Antes de lanzar la campana principal:

1. Revisar scripts candidatos para campana parametrica.
2. Definir tabla de diseno experimental preliminar.
3. Ejecutar un piloto productivo de 3 a 5 casos.
4. Validar que CSV, SQLite, logs y nombres sean trazables.
5. Solo despues lanzar tandas productivas controladas.
