# Sanity de contacto bloque-suelo

Fecha: 2026-05-08  
Caso aceptado: `contact_sanity_lowwater_20260508_dp0003`  
Intento sin agua: `contact_sanity_noflow_20260508_dp0003`

## Objetivo

Verificar que el bloque no inicia un movimiento relevante por una condicion inicial defectuosa,
interpenetracion, apoyo incorrecto o contacto bloque-suelo inestable. Esta prueba no busca representar
un tsunami; busca aislar el contacto.

## Diseno

- `dp = 0.003 m`
- `time_max = 2 s`
- `dam_height = 0.01 m`
- bloque en posicion oficial sobre playa 1:20
- `friction = 0.68`
- `reference_time_s = 0.5`

Primero se intento `dam_height = 0`, pero DualSPHysics no acepta un caso sin particulas de fluido:

```text
DualSPHysics fallo para caso 'contact_sanity_noflow_20260508_dp0003' (returncode=1): *** Exception (JSphGpuSingle::VisuConfig) at DualSPHysics/source/JSph.cpp:1707
Text: Constant 'b' cannot be zero.
'b' is zero when fluid height is zero (or fluid particles were not created)
```

Por eso se uso una columna minima de 1 cm, lejos del bloque y con corrida corta. Los gauges del bloque
reportaron velocidad de flujo y altura de agua maximas iguales a cero en el entorno del bloque.

## Resultado

- Estado: OK
- Desplazamiento maximo: 0.001232 m
- Desplazamiento relativo: 1.23 % de `d_eq`
- Umbral de movimiento usado en tesis: 5.00 % de `d_eq`
- Rotacion maxima: 2.11 deg
- Velocidad maxima del bloque: 0.1000 m/s
- Fuerza SPH maxima: 0.0000 N
- Fuerza de contacto maxima: 13271.24 N
- Velocidad de flujo en gauge representativo: 0.0000 m/s
- Altura/cota de agua en gauge representativo: 0.0000 m
- Particulas: 6901854
- Tiempo de corrida: 21.1 min

## Lectura

El bloque no supera el umbral de desplazamiento y no recibe forzante SPH en el entorno del bloque. El pequeno
desplazamiento observado queda como acomodacion/contacto inicial bajo Chrono y permanece muy por debajo del
criterio de movimiento. Esto valida el setup inicial bloque-suelo para continuar con casos hidraulicos.

## Limite

No valida el movimiento bajo impacto ni el acoplamiento fluido-bloque durante eventos fuertes. Solo prueba que
la condicion inicial y el contacto no generan una falla espuria por si solos.
