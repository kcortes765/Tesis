# Plan GP + Active Learning: Batch Inicial y Loop Adaptativo

**Proyecto:** SPH-IncipientMotion (Tesis UCN 2026)
**Fecha:** 2026-03-20
**Autor:** Kevin Cortes

---

## 1. Objetivo

Encontrar el umbral critico de movimiento incipiente de un boulder costero (BLIR3) en el espacio 2D (dam_height, boulder_mass) usando un GP surrogate con Active Learning. La respuesta es **continua**: desplazamiento maximo del boulder en metros.

## 2. Espacio parametrico

| Parametro | Min | Max | Unidad | Justificacion |
|-----------|-----|-----|--------|---------------|
| `dam_height` | 0.10 | 0.50 | m | 0.10 = no-movimiento, 0.50 = transporte extremo |
| `boulder_mass` | 0.80 | 1.60 | kg | Densidades 1500-3100 kg/m3 para BLIR3@scale=0.04 |
| `boulder_rot_z` | 0 | 0 | deg | **FIJO en 0** para estudio 2D inicial |

**Respuesta:** `max_displacement` (metros), variable continua >= 0.

## 3. Batch inicial: 20 puntos

### 3.1 Justificacion del tamano

- **Regla de Loeppky (2009):** Para un GP con d dimensiones, el batch inicial minimo es ~10d. Con d=2, eso da 20 puntos.
- **Referencia:** Loeppky, J.L., Sacks, J., Welch, W.J. (2009). "Choosing the sample size of a computer experiment: A practical guide." *Technometrics*, 51(4), 366-376.

### 3.2 Estrategia de muestreo

- **LHS optimizado (maximin):** Se evaluaron 500 seeds de `scipy.stats.qmc.LatinHypercube` y se selecciono la con mayor distancia minima entre puntos en el espacio normalizado [0,1]^2.
- **Seed ganador:** 2287 (min_dist normalizada = 0.148).
- **5 puntos fijos inyectados:**
  - 4 esquinas del dominio (combinaciones de min/max de cada parametro)
  - 1 centro del dominio (dam_h=0.30, mass=1.20)
- Los puntos fijos reemplazan a los puntos LHS mas cercanos, manteniendo las propiedades de cobertura del LHS.

### 3.3 Por que esquinas + centro

1. **Esquinas** anclan la prediccion del GP en los extremos, evitando extrapolacion peligrosa.
2. **Centro** da un punto de referencia en la zona de mayor interes (probable frontera).
3. Las 4 esquinas cubren los 4 regimenes fisicos esperados:
   - `(0.10, 0.80)`: ola debil + boulder liviano -> movimiento leve o nulo
   - `(0.10, 1.60)`: ola debil + boulder pesado -> sin movimiento
   - `(0.50, 0.80)`: ola fuerte + boulder liviano -> transporte completo
   - `(0.50, 1.60)`: ola fuerte + boulder pesado -> movimiento moderado

### 3.4 Matriz generada

Archivo: `config/gp_initial_batch.csv`

```
case_id  dam_height  boulder_mass  boulder_rot_z
gp_001   0.1000      1.6000        0.0    <- esquina (baja, pesado)
gp_002   0.5000      1.6000        0.0    <- esquina (alta, pesado)
gp_003   0.3000      1.2000        0.0    <- centro
gp_004   0.1000      0.8000        0.0    <- esquina (baja, liviano)
gp_005   0.5000      0.8000        0.0    <- esquina (alta, liviano)
gp_006   0.2397      1.4988        0.0    <- LHS interior
gp_007   0.2608      1.3521        0.0    <- LHS interior
gp_008   0.1022      1.2745        0.0    <- LHS interior
gp_009   0.3113      0.9756        0.0    <- LHS interior
gp_010   0.4046      1.2812        0.0    <- LHS interior
gp_011   0.4841      1.0743        0.0    <- LHS interior
gp_012   0.2887      0.8082        0.0    <- LHS interior
gp_013   0.1343      1.3856        0.0    <- LHS interior
gp_014   0.2072      1.0261        0.0    <- LHS interior
gp_015   0.4244      1.4391        0.0    <- LHS interior
gp_016   0.3662      0.9094        0.0    <- LHS interior
gp_017   0.1924      1.1846        0.0    <- LHS interior
gp_018   0.3818      1.1160        0.0    <- LHS interior
gp_019   0.3223      1.4584        0.0    <- LHS interior
gp_020   0.2487      1.1480        0.0    <- LHS interior
```

### 3.5 Compatibilidad con el pipeline

El CSV tiene las mismas columnas que `experiment_matrix.csv`:
- `case_id`: prefijo `gp_` (diferencia de `lhs_` para los 50 casos anteriores)
- `dam_height`, `boulder_mass`, `boulder_rot_z`: columnas esperadas por `main_orchestrator.py`

Para ejecutar:
```bash
# En la WS UCN:
python src/main_orchestrator.py --prod
# (modificar main_orchestrator.py para leer gp_initial_batch.csv
#  o copiar sobre experiment_matrix.csv)
```

## 4. Sanity checks post-batch inicial

**OBLIGATORIO** antes de iniciar el AL loop. Verificar:

| Check | Expectativa | Si falla |
|-------|-------------|----------|
| `gp_005` (h=0.50, m=0.80) | Maximo desplazamiento de todos | Revisar setup |
| `gp_001` (h=0.10, m=1.60) | Desplazamiento ~ 0 | Revisar FtPause, settling |
| Monotonia en dam_h | Mayor dam_h -> mayor desplazamiento (a masa fija) | Revisar energia dam-break |
| Monotonia en mass | Mayor mass -> menor desplazamiento (a dam_h fijo) | Revisar massbody vs rhopbody |
| Orden de magnitud | Desplazamiento en [0, ~15] metros | Revisar canal 30m, time_max |
| Sin NaN/Inf | Todos los casos completan | Revisar CSV parsing |

**10 figuras minimas del sanity check:**
1. Scatter dam_h vs displacement (color = mass)
2. Scatter mass vs displacement (color = dam_h)
3. Heatmap 2D (dam_h, mass) -> displacement
4. Timeseries de desplazamiento para esquinas
5. Timeseries de velocidad del flujo para esquinas
6. Histograma de desplazamientos
7. Comparacion con Ritter (velocidad dam-break analitica)
8. Froude number vs displacement
9. Energia cinetica del flujo vs resistencia del boulder
10. Residuos del GP inicial (LOO)

## 5. Active Learning Loop

### 5.1 Arquitectura

```
                    +------------------+
                    |  Batch inicial   |
                    |  (20 sims SPH)   |
                    +--------+---------+
                             |
                             v
                    +------------------+
              +---->|  Entrenar GP     |
              |     |  (Matern 2.5)    |
              |     +--------+---------+
              |              |
              |              v
              |     +------------------+
              |     | Evaluar U(x) en  |
              |     | grilla candidata |
              |     +--------+---------+
              |              |
              |              v
              |     +------------------+
              |     | U_min >= 2?      |---> SI --> PARAR
              |     +--------+---------+
              |              | NO
              |              v
              |     +------------------+
              |     | Seleccionar      |
              |     | x* = argmin U(x) |
              |     +--------+---------+
              |              |
              |              v
              |     +------------------+
              |     | Simular x* (SPH) |
              |     +--------+---------+
              |              |
              |              +--------+
              +---------------------------+
```

### 5.2 Acquisition function: U-function (Echard 2011)

Para respuesta continua (no clasificacion binaria), se adapta la U-function al problema de encontrar un umbral `T` de desplazamiento que separe "movimiento" de "no-movimiento":

```
U(x) = |mu(x) - T| / sigma(x)
```

Donde:
- `mu(x)` = prediccion media del GP en el punto x
- `sigma(x)` = desviacion estandar del GP en x
- `T` = umbral de movimiento (definir: propuesta T = d_eq del boulder, ~0.10 m)

**Interpretacion:** U(x) mide cuantas desviaciones estandar separan la prediccion del umbral. U < 2 significa que el GP no tiene confianza suficiente (95%) para clasificar ese punto.

**Alternativa (si T no esta claro):** Usar **Expected Improvement for Contour (EIC)** de Ranjan (2008), que busca puntos donde la frontera es mas incierta sin necesitar un T fijo. O simplemente **maxima varianza** (sigma-based) para las primeras iteraciones.

### 5.3 Criterio de parada

1. **U >= 2 para todos los candidatos** en la grilla de evaluacion (Echard 2011). Esto significa que el GP tiene al menos 95% de confianza en su clasificacion para todo el dominio.
2. **Budget maximo: 30 simulaciones totales** (20 iniciales + 10 AL). Cada sim a dp=0.004 tarda ~45-90 min en la RTX 5090.
3. **Lo que ocurra primero.**

### 5.4 Puntos por iteracion: 1 (secuencial puro)

**Decision:** 1 punto por iteracion AL.

**Justificacion:**
- Con solo d=2 dimensiones, cada nueva observacion actualiza significativamente el GP.
- 1 punto permite re-entrenar el GP y recalcular U(x) con maxima informacion.
- La sim tarda 45-90 min; el re-entrenamiento del GP tarda <1 segundo. No hay beneficio en batch.
- Batch >1 introduce redundancia (puntos similares seleccionados simultaneamente).
- Referencia: Echard (2011) usa 1 punto por iteracion para problemas de confiabilidad.

**Excepcion:** Si se quiere paralelizar en 2 GPUs, usar **Kriging Believer** (Ginsbourger 2010): simular el punto de menor U, "creer" la prediccion del GP como si fuera real, recalcular U, seleccionar el segundo punto. Pero con 1 GPU esto no aplica.

### 5.5 Grilla de candidatos

- Grilla regular 50x50 = 2500 puntos en [0.10, 0.50] x [0.80, 1.60].
- Resolucion: delta_h = 0.008 m, delta_m = 0.016 kg.
- Suficiente para identificar la zona de minimo U.
- Se excluyen puntos ya simulados (distancia minima > 0.01 en espacio normalizado).

### 5.6 Umbral de movimiento T

**Propuesta:** T = 1 * d_eq (diametro equivalente esferico del boulder).

Para BLIR3@scale=0.04, d_eq ~ 0.10 m. Un desplazamiento mayor a su propio diametro equivalente se considera "movimiento incipiente".

**Alternativa:** T = 0.5 * d_eq (conservador) o T basado en la literatura de boulder transport (Nandasena 2011 usa desplazamiento > 0 como criterio).

**Nota:** El valor exacto de T se puede ajustar post-hoc sin re-simular, ya que la respuesta del GP es continua. La frontera se recalcula instantaneamente para cualquier T.

## 6. Estimacion de costo computacional

| Fase | Sims | Tiempo/sim (dp=0.004) | Tiempo total |
|------|------|-----------------------|--------------|
| Batch inicial | 20 | 45-90 min | 15-30 horas |
| AL loop (peor caso) | 10 | 45-90 min | 7.5-15 horas |
| **Total** | **30** | | **22.5-45 horas** |

En la WS UCN corriendo 24/7: 1-2 dias para todo el estudio.

## 7. Implementacion: pasos concretos

### Fase 1: Ejecutar batch inicial (WS UCN)
1. Copiar `config/gp_initial_batch.csv` a la WS
2. Modificar `main_orchestrator.py` para leer este CSV (o renombrar)
3. Ejecutar con `--prod` (dp=0.004)
4. Verificar que los 20 casos completen sin errores

### Fase 2: Sanity check
1. Descargar resultados a laptop
2. Ejecutar sanity checks (seccion 4)
3. Si algo falla, diagnosticar ANTES de continuar

### Fase 3: AL loop
1. Entrenar GP con los 20 resultados
2. Evaluar U(x) en la grilla 50x50
3. Si U_min >= 2: PARAR (poco probable con solo 20 puntos)
4. Seleccionar x* = argmin U(x)
5. Generar caso `gp_021`, simular en WS
6. Agregar resultado, volver al paso 1
7. Repetir hasta U_min >= 2 o total=30

### Fase 4: Post-procesamiento
1. GP final con todos los datos (~25-30 puntos)
2. Frontera de movimiento para varios valores de T
3. Analisis de sensibilidad (Sobol indices via GP)
4. Figuras para Cap 6 de la tesis

## 8. Archivos generados

| Archivo | Descripcion |
|---------|-------------|
| `config/gp_initial_batch.csv` | Matriz de 20 casos (este plan) |
| `data/results.sqlite` | Resultados de todas las sims |
| `data/gp_surrogate.pkl` | Modelo GP entrenado |
| `data/figures/` | Figuras del sanity check y AL |

## 9. Referencias

- Bryan, A.M. et al. (2005). Bayesian experimental design using GP. *Biometrika*.
- Echard, B. et al. (2011). "AK-MCS: An active learning reliability method." *Structural Safety*, 33(2), 145-154.
- Loeppky, J.L. et al. (2009). "Choosing the sample size of a computer experiment." *Technometrics*, 51(4), 366-376.
- Ranjan, P. et al. (2008). "Sequential experiment design for contour estimation." *Technometrics*, 50(4), 527-541.
- Ginsbourger, D. et al. (2010). "Kriging is well-suited to parallelize optimization." *Computational Intelligence in Expensive Optimization Problems*.
- Nandasena, N.A.K. et al. (2011). "Reassessment of hydrodynamic equations." *Coastal Engineering*, 58(10), 947-962.
