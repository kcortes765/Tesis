# Analisis frontera practica - dam_h 0.20, masa 1.0 kg, slope 1:20

Fecha: 2026-04-26  
Fuente principal: archivos locales en `data/results/` y criterio en `src/data_cleaner.py`.

## Alcance y criterio

Este memo reconstruye el analisis desde archivos locales de la WS. Los archivos `CODEX_START_HERE.md` y `.codex_context/*` no se usan como fuente de verdad; solo pueden servir como indice de nombres de corridas.

El criterio de clasificacion esta definido en `src/data_cleaner.py`: `moved = max_disp > disp_threshold_m`, `rotated = max_rot > rot_threshold_deg`; para `classification_mode="displacement_only"`, `failed = moved`. Por tanto, en estos runs la rotacion se reporta como diagnostico, pero no cambia el estado ESTABLE/FALLO.

Parametros del caso:

- `dam_height = 0.20 m`
- `mass = 1.0 kg`
- `slope = 1:20`
- `classification_mode = displacement_only`
- `d_eq ~= 0.100421 m`
- umbral de desplazamiento: `0.05*d_eq ~= 0.005021 m`

## Evidencia principal comparable para frontera

Todos los registros listados abajo tienen `classification_mode=displacement_only`. Esta tabla deja fuera las corridas `repeat_*`, que se usan mas abajo solo como chequeo de robustez y no como evidencia independiente para localizar la frontera.

| Grupo | Prefix | mu | dp | Estado | moved | rotated | disp (m) | disp (%d_eq) | rot (deg) | vel max (m/s) | Fsph max (N) | duracion (min) |
|---|---|---:|---:|---|---|---|---:|---:|---:|---:|---:|---:|
| edge | conv_edge_f0675_full | 0.67500 | 0.002 | ESTABLE | False | True | 0.002264 | 2.25 | 7.59 | 0.0698 | 8.5210 | 1140.4 |
| edge | conv_edge_f0675_full | 0.67500 | 0.003 | FALLO | True | True | 0.006016 | 5.99 | 5.33 | 0.1000 | 8.2871 | 249.6 |
| edge | conv_edge_f0675_full | 0.67500 | 0.004 | FALLO | True | True | 0.009313 | 9.27 | 5.56 | 0.1000 | 16.3481 | 89.9 |
| edge | conv_edge_f0675_full | 0.67500 | 0.005 | ESTABLE | False | False | 0.004691 | 4.67 | 3.66 | 0.1000 | 10.5747 | 48.3 |
| edge | conv_edge_f0680_full | 0.68000 | 0.002 | ESTABLE | False | True | 0.003329 | 3.32 | 7.91 | 0.0698 | 7.9995 | 1144.2 |
| edge | conv_edge_f0680_full | 0.68000 | 0.003 | FALLO | True | True | 0.008121 | 8.09 | 5.86 | 0.1000 | 8.3732 | 249.3 |
| edge | conv_edge_f0680_full | 0.68000 | 0.004 | FALLO | True | False | 0.006819 | 6.79 | 4.96 | 0.1000 | 16.4816 | 89.1 |
| edge | conv_edge_f0680_full | 0.68000 | 0.005 | FALLO | True | False | 0.005265 | 5.24 | 3.67 | 0.1000 | 10.1018 | 48.1 |
| edge | conv_edge_f0681_full | 0.68100 | 0.002 | ESTABLE | False | True | 0.001836 | 1.83 | 7.12 | 0.0699 | 8.4019 | 1134.1 |
| edge | conv_edge_f0681_full | 0.68100 | 0.003 | ESTABLE | False | True | 0.004296 | 4.28 | 5.20 | 0.1000 | 8.3522 | 249.0 |
| edge | conv_edge_f0681_full | 0.68100 | 0.004 | FALLO | True | True | 0.007365 | 7.33 | 5.36 | 0.1000 | 16.4628 | 89.1 |
| edge | conv_edge_f0681_full | 0.68100 | 0.005 | FALLO | True | False | 0.005966 | 5.94 | 4.29 | 0.1000 | 12.0024 | 47.8 |
| edge | conv_edge_f0685_full | 0.68500 | 0.002 | ESTABLE | False | True | 0.001979 | 1.97 | 7.43 | 0.0699 | 9.0072 | 1139.4 |
| edge | conv_edge_f0685_full | 0.68500 | 0.003 | ESTABLE | False | False | 0.003798 | 3.78 | 4.76 | 0.1000 | 8.2466 | 249.9 |
| edge | conv_edge_f0685_full | 0.68500 | 0.004 | FALLO | True | True | 0.010343 | 10.30 | 5.58 | 0.1000 | 16.4787 | 89.7 |
| edge | conv_edge_f0685_full | 0.68500 | 0.005 | FALLO | True | False | 0.005324 | 5.30 | 3.87 | 0.1000 | 10.5064 | 48.8 |
| reassure | conv_reassure_dp003_f068025 | 0.68025 | 0.003 | FALLO | True | True | 0.009926 | 9.88 | 6.18 | 0.1000 | 9.1486 | 248.9 |
| reassure | conv_reassure_dp003_f068050 | 0.68050 | 0.003 | FALLO | True | True | 0.005317 | 5.29 | 5.23 | 0.1000 | 8.4980 | 249.2 |
| reassure | conv_reassure_dp003_f068075 | 0.68075 | 0.003 | ESTABLE | False | False | 0.004051 | 4.03 | 4.82 | 0.1000 | 9.0153 | 247.4 |
| reassure | conv_reassure_dp003_f068125 | 0.68125 | 0.003 | ESTABLE | False | True | 0.003628 | 3.61 | 5.17 | 0.1000 | 9.2262 | 249.4 |
| reassure | conv_reassure_dp002_f068025 | 0.68025 | 0.002 | ESTABLE | False | True | 0.002288 | 2.28 | 7.21 | 0.0698 | 8.1780 | 1132.6 |
| reassure | conv_reassure_dp002_f068050 | 0.68050 | 0.002 | ESTABLE | False | True | 0.002649 | 2.64 | 7.98 | 0.0698 | 7.8908 | 1158.9 |
| reassure | conv_reassure_dp002_f068075 | 0.68075 | 0.002 | ESTABLE | False | True | 0.002422 | 2.41 | 8.49 | 0.0698 | 8.1631 | 1144.3 |

## Frontera practica para dp=0.003

Los datos `dp=0.003` comparables muestran FALLO para `mu=0.67500`, `0.68000`, `0.68025` y `0.68050`, y ESTABLE para `mu=0.68075`, `0.68100`, `0.68125` y `0.68500`.

El bracket mas estrecho disponible queda entre:

- `mu=0.68050`: FALLO, `disp=0.005317 m` (`5.29 % d_eq`)
- `mu=0.68075`: ESTABLE, `disp=0.004051 m` (`4.03 % d_eq`)

La evidencia principal es este bracket: para `dp=0.003`, la transicion practica queda acotada en el intervalo `0.68050 < mu_crit < 0.68075`.

Como estimacion auxiliar, interpolando linealmente solo entre esos dos puntos contra el umbral `0.005021 m`, se obtiene:

- `mu_crit,dp003 ~= 0.680558`

Esta cifra debe presentarse como estimacion local/interpolada, no como coeficiente critico absoluto.

Como contexto adicional dentro del mismo conjunto comparable, el bracket menos refinado `mu=0.68000` FALLO y `mu=0.68100` ESTABLE da `mu_crit ~= 0.680811`. El nuevo refinamiento con `mu=0.68050` y `mu=0.68075` reduce el intervalo y entrega la estimacion auxiliar `~0.6806`.

## Lectura de dp=0.002

En `dp=0.002`, todos los puntos comparables disponibles entre `mu=0.67500` y `mu=0.68500` son ESTABLE por desplazamiento:

- `mu=0.67500`: `disp=0.002264 m`
- `mu=0.68000`: `disp=0.003329 m`
- `mu=0.68025`: `disp=0.002288 m`
- `mu=0.68050`: `disp=0.002649 m`
- `mu=0.68075`: `disp=0.002422 m`
- `mu=0.68100`: `disp=0.001836 m`
- `mu=0.68500`: `disp=0.001979 m`

Por tanto, con los datos actuales no existe un bracket FALLO/ESTABLE que permita estimar una frontera fina en ese rango. Lo que si puede afirmarse es que, respecto de `dp=0.003`, el refinamiento reduce el desplazamiento maximo y es consistente con un corrimiento de la transicion hacia fricciones menores. Sin embargo, esa transicion no queda localizada con los datos actuales.

La rotacion aumenta en `dp=0.002` y se mantiene aproximadamente entre `7.1` y `8.5 deg` en los puntos nuevos, pero en `classification_mode=displacement_only` eso no cambia el estado. Debe discutirse como respuesta rotacional/rocking diagnostica, no como falla bajo el criterio declarado.

## Robustez y repeticiones

Las repeticiones marginales son consistentes con los `conv_edge` equivalentes:

| Prefix | mu | dp | Estado | moved | rotated | disp (m) | disp (%d_eq) | rot (deg) | vel max (m/s) | Fsph max (N) | duracion (min) |
|---|---:|---:|---|---|---|---:|---:|---:|---:|---:|---:|
| conv_repeat_dp003_f0680_r2 | 0.68000 | 0.003 | FALLO | True | True | 0.008121 | 8.09 | 5.86 | 0.1000 | 8.3732 | 249.5 |
| conv_repeat_dp003_f0681_r2 | 0.68100 | 0.003 | ESTABLE | False | True | 0.004296 | 4.28 | 5.20 | 0.1000 | 8.3522 | 248.5 |
| conv_repeat_dp002_f0680_r2 | 0.68000 | 0.002 | ESTABLE | False | True | 0.003329 | 3.32 | 7.91 | 0.0698 | 7.9995 | 1144.5 |

Estas repeticiones reproducen el mismo patron y los mismos valores a la precision reportada. Esto confirma consistencia operativa de la configuracion y del postproceso en los casos repetidos, pero no debe venderse como estadistica de variabilidad aleatoria.

## Convergencia y limitaciones

Los JSON GCI de `conv_edge_*_full_gci.json` no sostienen una afirmacion fuerte de convergencia asintotica para la frontera:

- El desplazamiento muestra comportamiento oscilatorio/divergente en varios casos o GCI muy alto.
- La fuerza SPH maxima es oscilatoria en varios casos y no debe usarse como criterio principal de frontera.
- La velocidad maxima del boulder cambia sistematicamente entre `dp=0.003` y `dp=0.002` (`~0.100 m/s` vs `~0.070 m/s`), lo que refuerza que hay sensibilidad de resolucion.
- `dp=0.002` es mucho mas caro: alrededor de `1130-1160 min` por corrida, contra `~248-250 min` para `dp=0.003`.

Por eso, la formulacion defendible no es "convergencia fuerte demostrada", sino:

1. Para `dp=0.003`, la frontera practica bajo el criterio `displacement_only` queda acotada entre `mu=0.68050` y `mu=0.68075`; `mu_crit ~= 0.68056` es solo una estimacion auxiliar.
2. Al refinar a `dp=0.002`, los desplazamientos bajan y los resultados son consistentes con una transicion hacia fricciones menores, pero esa transicion no queda localizada.
3. La diferencia `dp=0.003` vs `dp=0.002` debe presentarse como sensibilidad numerica relevante de un problema de movimiento incipiente cerca de umbral, no como contradiccion del resultado.

## Texto listo para tesis

Para el caso `dam_height=0.20 m`, `m=1.0 kg` y pendiente `1:20`, se evaluo la estabilidad del bloque con un criterio primario de desplazamiento, definido como falla cuando el desplazamiento maximo supera el `5 %` del diametro equivalente (`d_eq ~= 0.100421 m`, umbral `0.005021 m`). La rotacion se registro como variable diagnostica, pero no se uso para clasificar la respuesta en los casos reportados (`classification_mode=displacement_only`).

En la resolucion `dp=0.003 m`, los casos cercanos al umbral acotan la transicion entre `mu=0.68050`, que falla por desplazamiento (`0.005317 m`, `5.29 % d_eq`), y `mu=0.68075`, que permanece estable (`0.004051 m`, `4.03 % d_eq`). Por tanto, la evidencia principal es el intervalo `0.68050 < mu_crit < 0.68075`. Una interpolacion lineal local entre ambos puntos entrega `mu_crit ~= 0.68056` como estimacion auxiliar, no como valor critico absoluto.

Al refinar a `dp=0.002 m`, todos los casos comparables disponibles en el rango `0.67500 <= mu <= 0.68500` permanecen estables por desplazamiento. Por tanto, con los datos actuales no existe un bracket FALLO/ESTABLE que permita estimar una frontera fina en ese rango. Lo que si puede afirmarse es que, respecto de `dp=0.003 m`, el refinamiento reduce el desplazamiento maximo y es consistente con un corrimiento de la transicion hacia fricciones menores. Sin embargo, esa transicion no queda localizada con los datos actuales. A la vez, las rotaciones acumuladas aumentan en la malla mas fina, lo que sugiere una respuesta de rocking mas marcada; bajo el criterio `displacement_only`, esa rotacion no modifica la clasificacion final.

En consecuencia, los resultados justifican reportar una frontera practica acotada entre `mu=0.68050` y `mu=0.68075` para `dp=0.003 m`, con `mu_crit ~= 0.68056` como estimacion auxiliar. La comparacion con `dp=0.002 m` evidencia sensibilidad de resolucion y desaconseja presentar el resultado como convergencia asintotica cerrada.

## Proximos runs minimos

No hace falta otro run para defender la frontera practica `dp=0.003`: el bracket `0.68050` FALLO / `0.68075` ESTABLE es suficientemente estrecho para el objetivo actual.

Si se exige encerrar tambien la frontera `dp=0.002`, el siguiente run deberia bajar la friccion por debajo del menor estable actual (`mu=0.67500`). Para un bracketing eficiente:

1. `dp=0.002`, `mu=0.66250`: si falla, acota la frontera fina entre `0.66250` y `0.67500`; si permanece estable, la transicion esta por debajo de `0.66250`.
2. Solo si el punto anterior permanece estable y se insiste en localizar la frontera fina: `dp=0.002`, `mu=0.65000`.

Evitaria correr `dp=0.003` adicional salvo que se pida una cifra interpolada mas fina; metodologicamente el intervalo actual ya es estrecho frente a la sensibilidad observada entre resoluciones.
