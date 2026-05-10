# Verificacion preproduccion sin experimento real

Fecha: 2026-05-08  
Objetivo: aumentar la defensibilidad antes de la campana productiva con tres controles independientes:
benchmark hidraulico, sanity de contacto y comparacion analitica preliminar.

## 1. Benchmark SPH/DualSPHysics

Se ejecuto el caso oficial `examples/main/01_DamBreak/CaseDambreakVal2D` de DualSPHysics v5.4.3 y se comparo
la posicion del frente de agua contra la referencia experimental incluida de Koshizuka y Oka (1996).

Resultado:

- puntos de referencia: 15
- RMSE posicion del frente: 0.2573 m
- MAE posicion del frente: 0.2401 m
- error relativo medio: 10.19 %
- error relativo maximo: 17.18 %
- error relativo final: 3.42 %
- particulas: 21001
- `dp`: 0.01 m

Lectura: valida que la instalacion local, GenCase, DualSPHysics, GPU y postproceso de gauges reproducen un caso
hidraulico conocido. No valida el bloque irregular ni Chrono.

Archivos:

- `data/benchmarks/hydraulic_20260508/benchmark_hydraulic_report.md`
- `data/benchmarks/hydraulic_20260508/figures/front_position_benchmark.png`
- `data/benchmarks/hydraulic_20260508/figures/front_position_error.png`

## 2. Chequeo de contacto bloque-suelo

Se intento un caso sin agua (`dam_height=0`), pero DualSPHysics no acepta ausencia total de particulas de fluido.
Luego se ejecuto una columna minima de 1 cm, corta y lejos del bloque, para mantener el solver activo sin impacto
hidraulico sobre el bloque.

Resultado:

- caso: `contact_sanity_lowwater_20260508_dp0003`
- `dp`: 0.003 m
- desplazamiento maximo: 0.001232 m
- desplazamiento relativo: 1.23 % de `d_eq`
- umbral de movimiento: 5.00 % de `d_eq`
- rotacion maxima: 2.11 deg
- fuerza SPH maxima: 0.0000 N
- flujo maximo en gauge del bloque: 0.0000 m/s
- agua maxima en gauge del bloque: 0.0000 m

Lectura: el bloque no se mueve por mala condicion inicial o contacto espurio. El pequeno desplazamiento queda
por debajo del umbral y ocurre sin forzante SPH local.

Archivos:

- `data/verification_preproduction_20260508/contact_sanity_report.md`
- `data/verification_preproduction_20260508/figures/contact_sanity_timeseries.png`

## 3. Comparacion analitica preliminar

Se compararon casos del piloto y batch2 contra un indice de movilidad de bajo orden:

```text
Psi = fuerza motriz aproximada / resistencia friccional efectiva
```

La comparacion usa una banda lower-central-upper de coeficientes de arrastre, sustentacion y area proyectada.
No reclasifica los casos; solo busca contradicciones de orden de magnitud.

Resultado:

- casos consolidados: 20
- casos utiles para analitica: 14
- contradicciones fuertes: 0/14
- fallos SPH con banda completamente movil: 10/12
- estables SPH con resistencia posible en la banda: 2/2
- mediana `Psi_central` en estables: 1.5
- mediana `Psi_central` en fallos: 1.6e+02

Lectura: no aparecen contradicciones fuertes entre la banda analitica y la clase SPH. Esto aporta coherencia
fisica preliminar, pero no reemplaza validacion experimental ni la campana productiva.

Archivos:

- `data/analytic_comparison/20260508_preproduction/analytic_comparison_report.md`
- `data/analytic_comparison/20260508_preproduction/figures/psi_vs_displacement.png`
- `data/analytic_comparison/20260508_preproduction/figures/ordered_mobility_cases.png`

## Conclusion operativa

Estos tres controles cubren cosas distintas:

1. El benchmark valida el pipeline hidraulico basico.
2. El sanity valida que el contacto inicial no genera movimiento espurio relevante.
3. La comparacion analitica valida coherencia fisica de orden de magnitud.

Con esto la campana productiva queda mejor defendida, pero las afirmaciones deben seguir siendo conservadoras:
la frontera final sera condicionada a la resolucion `dp=0.003`, al modelo de contacto, a la geometria fija y a las
distribuciones/variables consideradas.

## Fuentes metodologicas usadas

- SPHERIC benchmark tests: https://www.spheric-sph.org/validation-tests
- SPHERIC Test 05 wet-bottom dam break: https://www.spheric-sph.org/tests/test-05
- DualSPHysics SPH formulation and Chrono coupling: https://github.com/DualSPHysics/DualSPHysics/wiki/3.-SPH-formulation
- Project Chrono introduction/contact capabilities: https://api.chrono.projectchrono.org/introduction_chrono.html
- NASA/NPARC grid convergence and GCI tutorial: https://www.grc.nasa.gov/www/wind/valid/tutorial/spatconv.html
- Bressan et al. incipient boulder motion: https://pearl.plymouth.ac.uk/secam-research/1746
- Cox et al. critique of common boulder hydrodynamic equations: https://www.frontiersin.org/articles/10.3389/fmars.2020.00004/full
