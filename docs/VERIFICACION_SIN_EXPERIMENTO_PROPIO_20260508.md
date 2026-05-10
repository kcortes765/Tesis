# Verificacion sin experimento propio - plan defendible

Fecha de consulta: 2026-05-08

## Objetivo

Construir una base metodologica defendible para la tesis sin afirmar validacion experimental propia del bloque. El lenguaje correcto es:

> El modelo fue verificado numericamente, contrastado con benchmarks hidraulicos externos, controlado con pruebas de contacto y comparado con estimaciones analiticas de orden de magnitud.

No debe escribirse que el modelo fue validado experimentalmente para este bloque especifico.

## Estado local verificado

- La produccion dirigida `batch3` esta corriendo en la WS con `dp=0.003`, `classification_mode=displacement_only` y `reference_time_s=0.5`.
- A la ultima revision, `batch3` iba en el caso 3/10 (`batch3_base_mu0682`) con 2 casos completados y 0 fallos numericos.
- No se deben lanzar benchmark hidraulico ni sanity de contacto mientras DualSPHysics este ocupado por `batch3`.
- No se encontraron en esta WS archivos locales nuevos de verificacion `*benchmark*20260508*`, `*analytical*20260508*` o `*sanity*20260508*`; por tanto esos resultados no se registran como ejecutados aqui.

## Paquete de verificacion recomendado

### 1. Verificacion de resolucion

Ya ejecutada para seleccionar `dp=0.003` como resolucion operativa. La conclusion debe ser conservadora:

- `dp=0.003` no demuestra convergencia asintotica perfecta.
- Las variables principales se estabilizan de forma practica frente a `dp=0.002`.
- La clasificacion estable/fallo es sensible porque depende de un umbral de desplazamiento.

### 2. Benchmark hidraulico DualSPHysics/SPHERIC

Objetivo: verificar instalacion, solver, gauges y postproceso hidraulico frente a un caso conocido.

Caso recomendado:

- `01_DamBreak / CaseDambreakVal2D` de DualSPHysics.
- Comparar posicion del frente de agua con `EXP_X-DamTipPosition_Koshizula&Oka1996.txt`.

Que valida:

- ejecucion GenCase + DualSPHysics;
- lectura de gauges;
- postproceso de superficie libre/frente de agua;
- consistencia general del pipeline hidraulico.

Que no valida:

- contacto bloque-playa;
- friccion especifica del bloque;
- frontera de estabilidad del bloque irregular.

### 3. Sanity de contacto bloque-suelo-Chrono

Objetivo: verificar que el bloque no se desplaza por mala condicion inicial, penetracion, apoyo incorrecto o artefactos de contacto.

Prueba recomendada:

- misma geometria corregida;
- bloque alineado con pendiente;
- apoyo exacto sobre la playa;
- `dp=0.003`;
- `classification_mode=displacement_only`;
- `reference_time_s=0.5`;
- condicion hidraulica nula o minima controlada, segun lo que permita DualSPHysics.

Criterio esperado:

- desplazamiento maximo claramente bajo `5% d_eq`;
- sin flujo significativo en gauges cercanos;
- rotacion, si aparece, reportada como diagnostico.

### 4. Comparacion analitica preliminar

Objetivo: evaluar coherencia fisica con balances de orden de magnitud, no reemplazar la simulacion SPH.

Base fisica:

- resistencia por friccion: proporcional a `mu (W - L)`;
- demanda hidraulica: arrastre y sustentacion dependientes de velocidad y area proyectada;
- posible lectura por momentos para inicio de vuelco/rocking.

Uso correcto:

- aplicar a piloto, batch2 y batch3 cuando termine;
- clasificar por bandas, no como predictor exacto;
- buscar contradicciones fuertes entre simulacion y orden de magnitud.

## Fuentes principales

| Fuente | Uso en tesis |
|---|---|
| DualSPHysics Wiki, Testcases, `01_DAMBREAK`: https://github.com/DualSPHysics/DualSPHysics/wiki/7.-Testcases | Justifica usar el dam-break 2D oficial con datos de Koshizuka y Oka como benchmark hidraulico externo. |
| SPHERIC Validation Tests: https://www.spheric-sph.org/validation-tests | Justifica que los dam-break/free-surface benchmarks son practica comun en SPH. |
| NASA WIND validation tutorial / Roache-GCI: https://www.grc.nasa.gov/www/wind/valid/tutorial/spatconv.html?force_isolation=true | Marco de refinamiento espacial, Richardson/GCI y advertencia sobre convergencia asintotica. |
| DualSPHysics Wiki, SPH formulation, Chrono coupling: https://github.com/DualSPHysics/DualSPHysics/wiki/3.-SPH-formulation | Justifica el uso de Chrono para cuerpos rigidos, contactos y friccion. |
| Project Chrono documentation: https://api.chrono.projectchrono.org/introduction_chrono.html | Confirma soporte de cuerpos rigidos, friccion de Coulomb, contacto y colisiones. |
| Literatura de transporte de bloques costeros, Nandasena/Nott y revisiones: https://www.mdpi.com/2076-3263/10/10/400 y https://www.frontiersin.org/journals/marine-science/articles/10.3389/fmars.2020.00004/full | Base para comparacion analitica de arrastre, sustentacion, friccion y peso, con advertencias sobre sus limites. |

## Redaccion defendible para tesis

La seleccion de `dp=0.003 m` se adopto como compromiso entre estabilidad de variables continuas y costo computacional. Dado que el problema incluye superficie libre, contacto rigido, friccion y un criterio de umbral, no se afirma convergencia asintotica perfecta. En cambio, se presenta una verificacion por capas: refinamiento de resolucion, benchmark hidraulico externo, sanity de contacto bloque-suelo y comparacion analitica de orden de magnitud. Esta estrategia permite defender la coherencia numerica y fisica del pipeline sin afirmar validacion experimental propia del bloque.

## Proximo paso seguro

1. Esperar a que termine `batch3`.
2. Exportar resumen liviano de `batch3`.
3. Ejecutar benchmark hidraulico externo y sanity de contacto solo cuando la GPU quede libre.
4. Aplicar comparacion analitica a piloto, batch2 y batch3.
5. Actualizar la web y el texto de tesis con resultados auditados, separando resultados ejecutados de plan metodologico.
