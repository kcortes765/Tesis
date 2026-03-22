# Research: GP + Active Learning para Estimacion de Contorno

**Proyecto:** SPH-IncipientMotion (Tesis UCN 2026)
**Compilado:** 2026-03-20
**Objetivo:** Encontrar el umbral critico de movimiento incipiente de boulder costero en espacio 2D (dam_height, boulder_mass) con ~25-30 simulaciones SPH.

---

## 1. Kernel GP Recomendado

### 1.1 Matern 5/2 (Recomendacion)

**Kernel seleccionado:** Matern con nu=5/2.

**Formula:**

```
k(r) = sigma^2 * (1 + sqrt(5)*r/l + 5*r^2/(3*l^2)) * exp(-sqrt(5)*r/l)
```

donde `r = ||x - x'||` es la distancia euclidiana y `l` es el length-scale.

**Justificacion:**

1. **Suavidad controlada:** El Matern 5/2 produce funciones *dos veces diferenciables* (C^2). Esto es apropiado para la fisica del problema: el desplazamiento del boulder es una funcion suave de (dam_h, mass) pero NO infinitamente diferenciable (hay transiciones abruptas cerca del umbral de movimiento).

2. **RBF (nu=inf) es demasiado suave:** El kernel RBF (Squared Exponential) produce funciones infinitamente diferenciables (C^inf), lo que puede sobresuavizar la transicion entre "movimiento" y "no-movimiento", perdiendo la nitidez del contorno umbral.

3. **Matern 3/2 podria ser demasiado rugoso:** Produce funciones solo una vez diferenciables (C^1), lo que podria causar contornos irregulares innecesarios.

4. **Default en Bayesian Optimization:** Matern 5/2 es el kernel default en BoTorch, Optuna, y la mayoria de frameworks modernos de BO. La razon formal: para procesos fisicos, la funcion objetivo es tipicamente continua y al menos una vez diferenciable, lo que requiere que el kernel sea al menos dos veces diferenciable (nu >= 5/2). Para nu >= 7/2 el Matern ya es indistinguible del RBF.

5. **Referencia clave:** Rasmussen & Williams (2006), "Gaussian Processes for Machine Learning", Cap. 4. Recomiendan Matern sobre RBF para la mayoria de aplicaciones practicas por ser "less smooth and hence more realistic".

### 1.2 Configuracion practica

```python
from sklearn.gaussian_process.kernels import Matern, ConstantKernel

kernel = ConstantKernel(1.0, (1e-3, 1e3)) * Matern(
    length_scale=[1.0, 1.0],   # un length-scale por dimension (ARD)
    length_scale_bounds=(1e-2, 1e2),
    nu=2.5
)
```

**ARD (Automatic Relevance Determination):** Usar un length-scale independiente por dimension. Esto permite que el GP aprenda que dam_h tiene mas influencia que mass (o viceversa), capturando anisotropia en el espacio parametrico.

### 1.3 Alternativa: kernel compuesto

Si la respuesta tiene un componente de tendencia global mas variaciones locales:

```python
kernel = ConstantKernel() * Matern(nu=2.5) + WhiteKernel(noise_level=1e-5)
```

El `WhiteKernel` captura ruido numerico (jitter) de las simulaciones SPH. Incluso para simulaciones deterministicas, un pequeno nugget (1e-5 a 1e-8) mejora la estabilidad numerica de la inversion de la matriz de covarianza.

---

## 2. Tamano del Batch Inicial

### 2.1 Regla 10d de Loeppky (2009)

**Referencia:** Loeppky, J.L., Sacks, J., Welch, W.J. (2009). "Choosing the Sample Size of a Computer Experiment: A Practical Guide." *Technometrics*, 51(4), 366-376.

**Regla:** Para un GP con `d` dimensiones de entrada, el tamano minimo del diseno inicial es `n = 10d`.

- d = 2 --> n = 20 puntos

**Fundamentacion de Loeppky:**
- La regla de 10d fue usada informalmente por Chapman et al. (1994) y Jones et al. (1998) sin justificacion teorica.
- Loeppky et al. la validan empiricamente mostrando que con menos de 10d puntos, los length-scales del GP quedan mal estimados (la verosimilitud marginal tiene multiples optimos locales).
- La regla asume que NO todas las dimensiones son igualmente activas. Si todas lo fueran, se necesitarian mas puntos.

**Para nuestro caso 2D:** 20 puntos es el minimo. Con un budget total de 30, quedan 10 para active learning, que es razonable para un espacio 2D.

### 2.2 Estrategias de muestreo inicial

| Estrategia | Descripcion | Pros | Contras |
|------------|-------------|------|---------|
| **LHS puro** | Latin Hypercube Sampling, n=20 | Buena cobertura uniforme, garantia de proyeccion 1D | Puede dejar esquinas sin cubrir |
| **LHS maximin** | LHS optimizado para maximizar la distancia minima entre puntos | Mejor cobertura espacial que LHS aleatorio | Mas costoso de generar |
| **Esquinas + centro + LHS** | 4 esquinas + 1 centro + 15 LHS interiores | Ancla extremos, evita extrapolacion | Rompe propiedades estrictas de LHS |
| **Grid regular** | Grilla 4x5 o 5x4 | Simetrico, facil de analizar | Pobre en diagonal, no cubre bien el interior |
| **Random uniforme** | Puntos completamente aleatorios | Simple, sin patologia LHS en baja dim | Posibles clusters y huecos |
| **Sobol/Halton** | Secuencias quasi-aleatorias | Mejor discrepancia que LHS | Overkill para d=2, n=20 |

### 2.3 Recomendacion: Esquinas + Centro + LHS

**Elegida: 4 esquinas + 1 centro + 15 puntos LHS (maximin).**

**Justificacion:**
1. Las **4 esquinas** son criticas porque anclan el GP en los extremos del dominio. Sin ellas, las predicciones en las fronteras del espacio parametrico serian extrapolacion pura.
2. El **centro** (dam_h=0.30, mass=1.20) es probablemente cercano a la frontera de movimiento, dando informacion directa sobre la zona de interes.
3. Los **15 puntos LHS** llenan el interior de forma cuasi-aleatoria con buena cobertura.
4. **Advertencia de Zhang et al. (2020):** Los disenos space-filling puros (maximin, LHS) pueden exhibir comportamiento patologico como seed designs para GP secuenciales, especialmente en baja dimension. La inclusion de esquinas y centro mitiga esto.

**Implementacion:**
- Generar 500 seeds de LHS, seleccionar el de mayor min-distance (maximin).
- Reemplazar los 5 puntos LHS mas cercanos a las esquinas/centro por los puntos fijos.
- Archivo generado: `config/gp_initial_batch.csv` (ya existe, ver PLAN_GP_AL_BATCH.md).

---

## 3. Acquisition Functions para Estimacion de Contornos

### 3.1 Straddle Heuristic (Bryan et al., 2005)

**Referencia:** Bryan, B., Schneider, J., Nichol, R., Miller, C., Genovese, C., Wasserman, L. (2005). "Active Learning for Identifying Function Threshold Boundaries." *NIPS 2005*.

**Problema:** Estimar el level set L = {x : f(x) >= h} donde h es un umbral conocido.

**Formula:**

```
a_straddle(x) = alpha * sigma(x) - |mu(x) - h|
```

**Regla de seleccion:**

```
x* = argmax_{x in D} [ alpha * sigma(x) - |mu(x) - h| ]
```

donde:
- `mu(x)` = media predictiva del GP en x
- `sigma(x)` = desviacion estandar predictiva del GP en x
- `h` = umbral (threshold) de interes
- `alpha` = parametro de exploracion (tipicamente 1.96 para intervalo de confianza del 95%)

**Interpretacion:**
- El termino `alpha * sigma(x)` favorece puntos con alta incertidumbre (exploracion).
- El termino `-|mu(x) - h|` favorece puntos cuya prediccion esta cerca del umbral (explotacion).
- Un punto "straddles" el umbral cuando su intervalo de confianza `[mu - alpha*sigma, mu + alpha*sigma]` contiene h.
- Valores altos de `a_straddle` indican puntos que probablemente estan en la frontera Y donde el GP es mas incierto.

**Implementacion en Python:**

```python
def straddle(mu, sigma, threshold, alpha=1.96):
    """Bryan et al. 2005 straddle heuristic."""
    return alpha * sigma - np.abs(mu - threshold)

# Seleccionar siguiente punto
mu, sigma = gp.predict(X_candidates, return_std=True)
scores = straddle(mu, sigma, threshold=T)
next_idx = np.argmax(scores)
```

**Ventajas:**
- Simple de implementar (una linea).
- Intuitivo: selecciona donde el intervalo de confianza "cruza" el umbral.
- Barato computacionalmente.

**Limitaciones:**
- No tiene fundamento teorico formal (heuristica pura).
- El parametro alpha requiere calibracion.
- No considera la reduccion global de incertidumbre, solo local.

### 3.2 U-function (Echard et al., 2011)

**Referencia:** Echard, B., Gayton, N., Lemaire, M. (2011). "AK-MCS: An active learning reliability method combining Kriging and Monte Carlo Simulation." *Structural Safety*, 33(2), 145-154.

**Contexto:** Desarrollado para analisis de confiabilidad estructural. La "limit state function" g(x) = 0 separa la region de falla de la region segura. Adaptable a nuestro problema donde g(x) = f(x) - T separa movimiento de no-movimiento.

**Formula:**

```
U(x) = |mu(x) - T| / sigma(x)
```

donde:
- `mu(x)` = media predictiva del GP (Kriging) en x
- `sigma(x)` = desviacion estandar predictiva en x
- `T` = umbral (en reliability: T=0, la limit state surface)

**Regla de seleccion:**

```
x* = argmin_{x in S} U(x)
```

donde S es el conjunto de puntos candidatos (en AK-MCS original, la poblacion Monte Carlo; en nuestro caso, una grilla regular).

**Interpretacion geometrica:**
- U(x) mide cuantas desviaciones estandar separan la prediccion media del umbral.
- U(x) < 2 significa que la probabilidad de clasificacion incorrecta es > 2.28% (no se puede distinguir f(x) > T de f(x) < T con 95% de confianza).
- U(x) >= 2 significa que el GP tiene al menos ~97.7% de confianza en que el punto esta de un lado u otro del umbral.

**Criterio de parada:**

```
PARAR si min_{x in S} U(x) >= 2
```

Esto garantiza que TODOS los puntos candidatos tienen al menos 95% de confianza en su clasificacion respecto al umbral.

**Probabilidad de misclasificacion:** Cuando U >= 2, la probabilidad de que el signo de (f(x) - T) sea incorrecto es:

```
P(misclass) = Phi(-U) < Phi(-2) = 0.0228 = 2.28%
```

**Implementacion en Python:**

```python
def u_function(mu, sigma, threshold):
    """Echard et al. 2011 U-learning function."""
    return np.abs(mu - threshold) / sigma

# Loop de active learning
mu, sigma = gp.predict(X_candidates, return_std=True)
U = u_function(mu, sigma, threshold=T)
u_min = np.min(U)

if u_min >= 2.0:
    print("CONVERGENCIA: U_min >= 2, parar AL")
else:
    next_idx = np.argmin(U)
    x_next = X_candidates[next_idx]
```

**Ventajas:**
- Tiene criterio de parada natural (U >= 2).
- Ampliamente usado y validado en ingenieria estructural (>2000 citas).
- Simple de implementar.
- Interpretacion probabilistica clara.

**Limitaciones:**
- Requiere un umbral T fijo a priori.
- No optimiza globalmente la incertidumbre; es un criterio local (puntual).
- El criterio de parada puede ser conservador (requiere confianza en TODO el dominio).

### 3.3 Expected Improvement for Contour (Ranjan et al., 2008)

**Referencia:** Ranjan, P., Bingham, D., Michailidis, G. (2008). "Sequential Experiment Design for Contour Estimation from Complex Computer Codes." *Technometrics*, 50(4), 527-541.

**Idea:** Adapta la funcion de Expected Improvement (EI) clasica de optimizacion al problema de estimacion de contornos. Define una "mejora" como reduccion en la distancia al contorno objetivo.

**Formula:**

Sea `a` el valor del contorno objetivo (umbral T), `epsilon = alpha * sigma_hat(x)` con alpha > 0. Definimos:

```
u1 = (a - mu_hat(x) - epsilon) / sigma_hat(x)
u2 = (a - mu_hat(x) + epsilon) / sigma_hat(x)
```

Entonces:

```
EI_contour(x) = [epsilon^2 - (mu_hat(x) - a)^2 - sigma_hat(x)^2] * [Phi(u2) - Phi(u1)]
              + sigma_hat(x)^2 * [u2*phi(u2) - u1*phi(u1)]
              + 2*(mu_hat(x) - a)*sigma_hat(x) * [phi(u1) - phi(u2)]
```

donde:
- `Phi` = CDF de la normal estandar
- `phi` = PDF de la normal estandar
- `mu_hat(x)`, `sigma_hat(x)` = media y desviacion estandar predictivas del GP
- `alpha` = parametro de tuning (controla ancho de la banda alrededor del contorno)

**Regla de seleccion:**

```
x* = argmax_{x in D} EI_contour(x)
```

**Implementacion en Python:**

```python
from scipy.stats import norm

def ei_contour(mu, sigma, threshold, alpha=1.0):
    """Ranjan et al. 2008 Expected Improvement for contour."""
    eps = alpha * sigma
    a = threshold
    u1 = (a - mu - eps) / sigma
    u2 = (a - mu + eps) / sigma

    term1 = (eps**2 - (mu - a)**2 - sigma**2) * (norm.cdf(u2) - norm.cdf(u1))
    term2 = sigma**2 * (u2 * norm.pdf(u2) - u1 * norm.pdf(u1))
    term3 = 2 * (mu - a) * sigma * (norm.pdf(u1) - norm.pdf(u2))

    return term1 + term2 + term3
```

**Ventajas:**
- Fundamento teorico solido (maximizacion de mejora esperada).
- Balancea exploracion (sigma grande) y explotacion (mu cerca de a).
- El parametro alpha controla el ancho de la banda de interes.

**Limitaciones:**
- Mas complejo de implementar que straddle o U-function.
- No tiene criterio de parada natural como U >= 2.
- El tuning de alpha puede ser delicado.

### 3.4 Expected Feasibility Function — EFF (Bichon et al., 2008)

**Referencia:** Bichon, B.J., Eldred, M.S., Swiler, L.P., Mahadevan, S., McFarland, J.M. (2008). "Efficient Global Reliability Analysis for Nonlinear Implicit Performance Functions." *AIAA Journal*, 46(10), 2459-2468.

**Idea:** Adapta la EI clasica al problema de encontrar la limit state surface g(x) = 0 (o g(x) = T). Se define la "feasibility" como la proximidad al umbral.

**Formula:** La EFF se calcula como:

```
EFF(x) = (mu - T) * [2*Phi(z2) - Phi(z1) - Phi(z3)]
       - sigma * [2*phi(z2) - phi(z1) - phi(z3)]
       + epsilon * [Phi(z3) - Phi(z1)]
```

donde:
```
z1 = (T - epsilon - mu) / sigma
z2 = (T - mu) / sigma
z3 = (T + epsilon - mu) / sigma
epsilon = 2 * sigma  (tipicamente)
```

**Relacion con otros criterios:**
- EFF es equivalente a la formulacion de Ranjan cuando se usa epsilon = alpha * sigma.
- Ambas son extensiones de la EI clasica (Jones et al., 1998) al problema de contorno.
- EFF fue desarrollada independientemente en el contexto de ingenieria de confiabilidad.

### 3.5 Otros criterios relevantes

#### tMSE (Targeted Mean Square Error) — Picheny et al. (2010)

**Referencia:** Picheny, V., Ginsbourger, D., Roustant, O., Haftka, R.T., Kim, N.H. (2010). "Adaptive Designs of Experiments for Accurate Approximation of a Target Region." *Journal of Mechanical Design*, 132(7).

**Formula:**
```
tMSE(x) = sigma^2(x) * W(x)
```
donde W(x) es una funcion peso que concentra la atencion cerca del contorno:
```
W(x) = phi((mu(x) - T) / sqrt(sigma^2(x) + tau^2))
```
con tau un parametro de regularizacion.

**Ventaja:** Mas suave que la U-function; evita singularidades cuando sigma -> 0.

#### SUR (Stepwise Uncertainty Reduction) — Bect et al. (2012)

**Referencia:** Bect, J., Ginsbourger, D., Li, L., Picheny, V., Vazquez, E. (2012). "Sequential Design of Computer Experiments for the Estimation of a Probability of Failure." *Statistics and Computing*, 22(3), 773-793.

**Idea:** Seleccionar el punto que maximiza la reduccion esperada de una medida global de incertidumbre (no solo local como U o straddle). El criterio SUR es:

```
x* = argmin_{x in D} E[H_{n+1} | X_{n+1} = x]
```

donde H_n es una medida integral de incertidumbre sobre el dominio.

**Ventaja:** Optimalidad global (considera todo el dominio, no solo el punto candidato).
**Desventaja:** Computacionalmente caro (requiere integracion numerica en cada iteracion).

#### EIGF (Expected Improvement for Global Fit) — Lam (2008)

**Referencia:** Lam, C.Q. (2008). "Sequential Adaptive Designs in Computer Experiments for Response Surface Model Fit." PhD Thesis, Ohio State University.

**Idea:** Combina informacion de la varianza predictiva con la diferencia cuadrada de la respuesta, inspirado en EI pero orientado a mejorar el ajuste global (no el contorno).

**Para nuestro caso:** EIGF es menos relevante que los criterios de contorno especificos (U, EFF, tMSE). Puede ser util como criterio de warm-up en las primeras iteraciones cuando el GP aun no tiene buen ajuste global.

### 3.6 Comparacion resumen

| Criterio | Complejidad | Criterio de parada | Tipo | Mejor para |
|----------|-------------|-------------------|------|------------|
| **Straddle** (Bryan 2005) | Muy baja | No natural | Heuristica | Prototipado rapido |
| **U-function** (Echard 2011) | Baja | U >= 2 (natural) | Puntual | Confiabilidad, clasificacion binaria |
| **EI contour** (Ranjan 2008) | Media | No natural | Puntual | Contornos suaves |
| **EFF** (Bichon 2008) | Media | No natural | Puntual | Limit state surfaces |
| **tMSE** (Picheny 2010) | Media | No natural | Puntual | Regularizacion en contorno |
| **SUR** (Bect 2012) | Alta | Convergencia integral | Global | Optimalidad formal |

### 3.7 Recomendacion para la tesis

**Criterio primario: U-function (Echard 2011).**

Razones:
1. Criterio de parada natural (U >= 2) que es facil de justificar y reportar.
2. Ampliamente validado en ingenieria estructural — los revisores lo conocen.
3. Simple de implementar (una linea de codigo).
4. Se adapta directamente a nuestro problema: la "limit state" es f(x) = T.

**Criterio secundario (para comparacion en la tesis): Straddle (Bryan 2005).**

Razones:
1. Complementa la discusion: straddle no tiene criterio de parada formal.
2. Comparar visualmente que puntos selecciona cada criterio enriquece el analisis.
3. Trivial de implementar en paralelo.

---

## 4. Criterio de Parada

### 4.1 U >= 2 (Echard 2011)

**Criterio principal.** Parar cuando:

```
min_{x in S} U(x) >= 2.0
```

**Significado:** Todo punto candidato en el dominio tiene al menos 97.7% de probabilidad de estar correctamente clasificado (arriba o abajo del umbral T).

**Consideraciones practicas:**
- En la practica, U >= 2 puede ser dificil de alcanzar si hay zonas del dominio poco exploradas. Con 20+10=30 sims en 2D, es alcanzable.
- Se evalua U sobre una grilla regular 50x50 = 2500 puntos candidatos.

### 4.2 Convergencia del contorno

**Criterio complementario.** Monitorear la estabilidad del contorno estimado entre iteraciones:

```
delta_contour = max_x |P_n(f(x) > T) - P_{n-1}(f(x) > T)|
```

Si `delta_contour < epsilon` (e.g., 0.01) durante 3 iteraciones consecutivas, el contorno se ha estabilizado.

**Implementacion practica:** Comparar el area de la region clasificada como "movimiento" entre iteraciones sucesivas. Si cambia menos de 1%, declarar convergencia.

### 4.3 Budget maximo

**Hard stop: 30 simulaciones totales** (20 batch inicial + 10 AL).

Justificacion:
- Cada sim a dp=0.004 tarda 45-90 min en la RTX 5090.
- 30 sims = 22.5-45 horas = 1-2 dias en la WS UCN.
- Suficiente para un estudio 2D con GP (Loeppky: 10d=20, mas 10 adaptivos).

### 4.4 Criterio combinado (recomendado)

```
PARAR si:
  (1) min(U) >= 2.0                          [confianza suficiente]
  OR (2) delta_contour < 0.01 por 3 iters    [contorno estable]
  OR (3) n_total >= 30                        [budget agotado]
```

Reportar cual criterio se activo.

---

## 5. Implementacion Practica

### 5.1 Comparacion de librerias

| Libreria | Ventajas | Desventajas | Recomendada |
|----------|----------|-------------|-------------|
| **scikit-learn** (`GaussianProcessRegressor`) | Simple, bien documentado, estable, integrado con el ecosistema sklearn | No escala a >1000 puntos (O(n^3)), kernel selection limitada | **SI** para n<=30 |
| **GPy** | Kernels avanzados, variacional, multi-output | Mas lento que sklearn por overhead Python, desarrollo discontinuado | No |
| **GPyTorch** | GPU-acelerado, escalable, composable kernels | Overkill para n=30, API mas compleja, requiere PyTorch | No |
| **BoTorch** | Acquisition functions pre-implementadas, integracion con GPyTorch | Demasiado pesado para este problema, forzaria PyTorch como dependencia | No |
| **GPflow** | Backend TensorFlow, variacional | Mismo problema que GPyTorch: overkill | No |

### 5.2 Recomendacion: scikit-learn

**Para n <= 30 puntos en 2D, scikit-learn es la opcion optima.**

Razones:
1. Ya esta instalado en el proyecto (`pip install scikit-learn`).
2. O(n^3) con n=30 es O(27000) operaciones — instantaneo (<1ms).
3. `predict(X, return_std=True)` da mu y sigma directamente.
4. Soporte nativo de Matern(nu=2.5) con ARD.
5. `log_marginal_likelihood` para diagnostico.
6. LOO cross-validation implementable con la formula analitica.

### 5.3 Esqueleto de implementacion

```python
import numpy as np
import pandas as pd
from sklearn.gaussian_process import GaussianProcessRegressor
from sklearn.gaussian_process.kernels import Matern, ConstantKernel, WhiteKernel
from sklearn.preprocessing import StandardScaler
from scipy.stats import norm

# ---- CONFIGURACION ----
THRESHOLD = 0.10        # T: umbral de movimiento (metros)
U_STOP = 2.0            # Criterio de parada de Echard
MAX_SIMS = 30           # Budget maximo
GRID_SIZE = 50          # Grilla de evaluacion: 50x50

# ---- KERNEL ----
kernel = ConstantKernel(1.0, (1e-3, 1e3)) * Matern(
    length_scale=[1.0, 1.0],
    length_scale_bounds=(1e-2, 1e2),
    nu=2.5
) + WhiteKernel(noise_level=1e-5, noise_level_bounds=(1e-10, 1e-1))

# ---- PREPROCESAMIENTO ----
# Normalizar inputs a [0, 1], outputs a media 0, var 1
def normalize_inputs(X, bounds):
    """Normalizar a [0, 1]."""
    return (X - bounds[:, 0]) / (bounds[:, 1] - bounds[:, 0])

def standardize_outputs(y):
    """Estandarizar a media 0, var 1."""
    return (y - y.mean()) / y.std(), y.mean(), y.std()

# ---- GP TRAINING ----
def train_gp(X, y, kernel):
    """Entrenar GP con normalizacion."""
    gp = GaussianProcessRegressor(
        kernel=kernel,
        n_restarts_optimizer=20,      # Importante: multiples restarts
        normalize_y=True,             # sklearn lo hace internamente
        alpha=1e-6,                   # Jitter para estabilidad numerica
        random_state=42
    )
    gp.fit(X, y)
    return gp

# ---- ACQUISITION FUNCTIONS ----
def u_function(mu, sigma, threshold):
    """Echard et al. 2011: U-learning function."""
    return np.abs(mu - threshold) / np.maximum(sigma, 1e-10)

def straddle(mu, sigma, threshold, alpha=1.96):
    """Bryan et al. 2005: Straddle heuristic."""
    return alpha * sigma - np.abs(mu - threshold)

# ---- GRILLA DE CANDIDATOS ----
def make_candidate_grid(bounds, n=GRID_SIZE):
    """Grilla regular en el espacio parametrico."""
    x1 = np.linspace(bounds[0, 0], bounds[0, 1], n)
    x2 = np.linspace(bounds[1, 0], bounds[1, 1], n)
    X1, X2 = np.meshgrid(x1, x2)
    return np.column_stack([X1.ravel(), X2.ravel()])

# ---- ACTIVE LEARNING LOOP ----
def al_iteration(gp, X_train, y_train, X_cand, threshold):
    """Una iteracion del loop AL."""
    mu, sigma = gp.predict(X_cand, return_std=True)
    U = u_function(mu, sigma, threshold)
    u_min = np.min(U)

    if u_min >= U_STOP:
        return None, u_min  # Convergencia

    next_idx = np.argmin(U)
    return X_cand[next_idx], u_min

# ---- LOO CROSS-VALIDATION ----
def loo_cv(gp, X, y):
    """Leave-one-out via formula analitica para GP."""
    K = gp.kernel_(X)
    K_inv = np.linalg.inv(K + gp.alpha * np.eye(len(X)))
    alpha_vec = K_inv @ y

    loo_mean = y - alpha_vec / np.diag(K_inv)
    loo_var = 1.0 / np.diag(K_inv)

    residuals = y - loo_mean
    rmse_loo = np.sqrt(np.mean(residuals**2))

    return loo_mean, loo_var, rmse_loo
```

### 5.4 Normalizacion de datos (best practices)

1. **Inputs:** Normalizar a [0, 1] dividiendo por el rango. Esto asegura que los length-scales del kernel sean comparables entre dimensiones.

2. **Outputs:** Estandarizar a media 0, varianza 1 (o usar `normalize_y=True` en sklearn, que lo hace internamente y revierte antes de predecir).

3. **Priors de hiperparametros:** Con datos normalizados, priors N(0, 3) en log-espacio para length-scales y varianza del kernel son razonables.

4. **Nugget/jitter:** Incluso para simulaciones deterministicas, usar `alpha=1e-6` para estabilidad numerica de la factorizacion de Cholesky.

---

## 6. Validacion del GP

### 6.1 LOO Cross-Validation

**Metodo principal de validacion** cuando n es pequeno (20-30 puntos) y no se puede separar un test set.

**Mecanismo:**
- Para cada punto i, entrenar el GP con los otros n-1 puntos.
- Predecir el punto i y comparar con el valor real.
- Repetir para todos los puntos.

**Eficiencia:** Para un GP exacto, LOO puede calcularse analiticamente a partir de la factorizacion de Cholesky de la matriz de covarianza completa, sin re-entrenar n veces:

```
mu_LOO_i = y_i - (K^{-1} y)_i / (K^{-1})_{ii}
sigma^2_LOO_i = 1 / (K^{-1})_{ii}
```

**Costo:** O(n^3) (igual que entrenar una vez). Para n=30, instantaneo.

**Metricas a reportar:**
- **RMSE_LOO:** Error cuadratico medio de las predicciones LOO.
- **Q^2 (coeficiente de determinacion LOO):** Q^2 = 1 - RMSE_LOO^2 / Var(y). Q^2 > 0.9 es aceptable; Q^2 > 0.95 es bueno.
- **Standardized LOO residuals:** (y_i - mu_LOO_i) / sigma_LOO_i. Deben seguir N(0,1) si el modelo es correcto.

### 6.2 Predictive Variance Checks

**Verificar que la incertidumbre del GP es calibrada:**

1. **Cobertura del intervalo de confianza:** El 95% CI del GP debe contener ~95% de los valores reales en LOO. Si la cobertura es >> 95%, el GP es sobreconservador (sigma sobreestimada). Si es << 95%, el GP es sobreconfiado.

2. **Grafico de calibracion:** Plotear la fraccion de puntos LOO dentro del CI vs. el nivel de confianza nominal (20%, 40%, 60%, 80%, 95%). Idealmente, la curva sigue la diagonal.

3. **PIT histogram (Probability Integral Transform):** Para cada punto LOO, calcular Phi((y_i - mu_LOO_i) / sigma_LOO_i). La distribucion debe ser uniforme en [0,1].

### 6.3 Diagnosticos del kernel

1. **Log-marginal likelihood:** Reportar el valor optimizado. Comparar entre diferentes kernels o configuraciones.

2. **Length-scales estimados:** Reportar los length-scales del Matern 5/2 para cada dimension. Un length-scale mucho mayor en una dimension indica que esa dimension tiene menos influencia.

3. **Varianza del kernel (signal variance):** Reportar sigma_f^2 estimado. Debe ser del mismo orden que la varianza de los datos.

4. **Nugget estimado:** Si es >> 1e-5, puede indicar ruido numerico significativo en las simulaciones.

---

## 7. Figuras Esperadas por Revisores

### 7.1 Figuras del GP Surrogate

| # | Figura | Descripcion | Importancia |
|---|--------|-------------|-------------|
| 1 | **Superficie GP media** | Heatmap 2D de mu(dam_h, mass). Datos de entrenamiento como puntos. | Esencial |
| 2 | **Superficie GP incertidumbre** | Heatmap 2D de sigma(dam_h, mass). Debe ser baja cerca de datos, alta lejos. | Esencial |
| 3 | **Contorno umbral** | Linea de contorno f(x) = T sobre el heatmap de mu. Con banda de confianza. | Esencial |
| 4 | **LOO predicted vs actual** | Scatter de y_LOO vs y_real. Linea 1:1. R^2 y RMSE. | Esencial |
| 5 | **LOO residuos estandarizados** | Histogram de (y - mu_LOO)/sigma_LOO. Superponer N(0,1). | Importante |
| 6 | **Cobertura del CI** | Curva de calibracion: cobertura real vs. nominal. | Importante |

### 7.2 Figuras del Active Learning

| # | Figura | Descripcion | Importancia |
|---|--------|-------------|-------------|
| 7 | **Secuencia de puntos AL** | Scatter 2D mostrando orden de seleccion (color = iteracion). Batch inicial en un color, AL en otro. | Esencial |
| 8 | **Evolucion de U_min** | Line plot de min(U) vs iteracion. Linea horizontal en U=2. | Esencial |
| 9 | **Heatmap de U(x) progresivo** | 3-4 snapshots del heatmap de U(x) en iteraciones clave (inicio, mitad, final). | Muy util |
| 10 | **Evolucion del contorno** | Overlay de contornos estimados en iteraciones 0, 5, 10, final. Convergen a uno. | Esencial |
| 11 | **Mapa de acquisition function** | Heatmap de straddle(x) o U(x) con el proximo punto seleccionado marcado. | Util |

### 7.3 Figuras del analisis fisico

| # | Figura | Descripcion | Importancia |
|---|--------|-------------|-------------|
| 12 | **Frontera de movimiento** | Contorno f = T en espacio (dam_h, mass) con banda de incertidumbre (95% CI). | Esencial |
| 13 | **Probabilidad de movimiento** | Heatmap de P(f(x) > T) derivada del GP. | Esencial |
| 14 | **Sensibilidad 1D slices** | Prediccion GP + CI para dam_h fijo (variando mass) y mass fijo (variando dam_h). | Importante |
| 15 | **Sobol indices** | Barplot de indices de Sobol S1 y ST para dam_h y mass (calculados via GP). | Importante |
| 16 | **Comparacion con ecuaciones empiricas** | Superponer umbral de Nandasena 2011 / Nott 2003 sobre la frontera GP. | Muy util |

### 7.4 Figuras de convergencia/diagnostico

| # | Figura | Descripcion | Importancia |
|---|--------|-------------|-------------|
| 17 | **Convergencia RMSE_LOO** | RMSE_LOO vs numero de puntos de entrenamiento. | Util |
| 18 | **Length-scales vs iteracion** | Evolucion de los length-scales del kernel durante AL. | Util |
| 19 | **Log-marginal likelihood** | LML vs iteracion. Debe estabilizarse. | Opcional |

**Total: ~15-19 figuras** cubren exhaustivamente lo que un revisor espera de un estudio GP+AL.

---

## 8. Flujo Completo Propuesto

```
[1] Generar batch inicial (20 puntos LHS+esquinas)
 |
[2] Ejecutar 20 sims SPH en WS UCN (~15-30 horas)
 |
[3] Sanity check: monotonias, ordenes de magnitud, timeseries
 |
[4] Entrenar GP (Matern 5/2, ARD, normalize_y=True)
 |
[5] LOO cross-validation → RMSE, Q^2, residuos
 |
[6] Evaluar U(x) en grilla 50x50
 |
[7] ¿U_min >= 2?
 |     |
 SI    NO → [8] Seleccionar x* = argmin U(x)
 |              |
 |         [9] Simular x* en WS UCN (~1 hora)
 |              |
 |         [10] Agregar resultado → volver a [4]
 |
[11] GP final con todos los datos
 |
[12] Post-procesamiento:
      - Frontera de movimiento para T = 0.05, 0.10, 0.20 m
      - Probabilidad de movimiento P(f > T)
      - Sobol indices via GP
      - Comparacion con ecuaciones empiricas
      - Generar todas las figuras (seccion 7)
```

---

## 9. Sobol Indices via GP Surrogate

Una vez que el GP esta entrenado, se pueden calcular los Sobol indices (analisis de sensibilidad global) de forma muy eficiente sin simulaciones adicionales:

### 9.1 Metodo Monte Carlo sobre el GP

```python
from SALib.sample import saltelli
from SALib.analyze import sobol

# Generar muestras Sobol
problem = {
    'num_vars': 2,
    'names': ['dam_height', 'boulder_mass'],
    'bounds': [[0.10, 0.50], [0.80, 1.60]]
}

X_sobol = saltelli.sample(problem, N=4096)  # 4096*(2*2+2) = 24576 evaluaciones
Y_sobol = gp.predict(X_sobol)               # Instantaneo (GP, no SPH)

Si = sobol.analyze(problem, Y_sobol)
print(f"S1 dam_height: {Si['S1'][0]:.3f}")
print(f"S1 boulder_mass: {Si['S1'][1]:.3f}")
print(f"ST dam_height: {Si['ST'][0]:.3f}")
print(f"ST boulder_mass: {Si['ST'][1]:.3f}")
```

### 9.2 Metodo analitico (Oakley & O'Hagan, 2004)

Para un GP con kernel estacionario, los indices de Sobol se pueden calcular analiticamente integrando la funcion de covarianza. Esto evita el muestreo Monte Carlo, pero es mas complejo de implementar.

**Referencia:** Oakley, J.E. & O'Hagan, A. (2004). "Probabilistic sensitivity analysis of complex models: a Bayesian approach." *JRSS-B*, 66(3), 751-769.

---

## 10. Consideraciones para Extension Futura a 3D

Si se agrega `boulder_rot_z` como tercera dimension:
- Loeppky: n = 10 * 3 = 30 puntos iniciales (todo el budget actual).
- Se necesitaria budget de ~50 sims (30 + 20 AL).
- Los criterios (U, straddle, EI) se extienden trivialmente a 3D.
- La grilla de candidatos pasaria a 20x20x20 = 8000 puntos (aun manejable).
- Las figuras de contorno se volverian superficies 3D (menos intuitivas).

---

## 11. Referencias Completas

### Papers fundamentales

1. **Bryan, B. et al. (2005).** "Active Learning for Identifying Function Threshold Boundaries." *NIPS 2005*. [PDF](https://proceedings.neurips.cc/paper_files/paper/2005/file/8e930496927757aac0dbd2438cb3f4f6-Paper.pdf)

2. **Echard, B., Gayton, N., Lemaire, M. (2011).** "AK-MCS: An active learning reliability method combining Kriging and Monte Carlo Simulation." *Structural Safety*, 33(2), 145-154. [ScienceDirect](https://www.sciencedirect.com/science/article/abs/pii/S0167473011000038)

3. **Ranjan, P., Bingham, D., Michailidis, G. (2008).** "Sequential Experiment Design for Contour Estimation from Complex Computer Codes." *Technometrics*, 50(4), 527-541. [T&F Online](https://www.tandfonline.com/doi/abs/10.1198/004017008000000541)

4. **Loeppky, J.L., Sacks, J., Welch, W.J. (2009).** "Choosing the Sample Size of a Computer Experiment: A Practical Guide." *Technometrics*, 51(4), 366-376. [PDF](https://www.niss.org/sites/default/files/technicalreports/tr170.pdf)

5. **Bichon, B.J. et al. (2008).** "Efficient Global Reliability Analysis for Nonlinear Implicit Performance Functions." *AIAA Journal*, 46(10), 2459-2468. [ResearchGate](https://www.researchgate.net/publication/253769405)

6. **Gotovos, A., Casati, N., Hitz, G., Krause, A. (2013).** "Active Learning for Level Set Estimation." *IJCAI 2013*. [PDF](https://www.ijcai.org/Proceedings/13/Papers/202.pdf)

### Kernels y GP

7. **Rasmussen, C.E. & Williams, C.K.I. (2006).** *Gaussian Processes for Machine Learning.* MIT Press. [Libro completo online](http://www.gaussianprocess.org/gpml/)

8. **Duvenaud, D. (2014).** *Automatic Model Construction with Gaussian Processes.* PhD Thesis, Cambridge. [Kernel Cookbook](https://www.cs.toronto.edu/~duvenaud/cookbook/)

### Criterios avanzados

9. **Picheny, V. et al. (2010).** "Adaptive Designs of Experiments for Accurate Approximation of a Target Region." *J. Mech. Design*, 132(7).

10. **Bect, J. et al. (2012).** "Sequential Design of Computer Experiments for the Estimation of a Probability of Failure." *Statistics and Computing*, 22(3), 773-793.

11. **Chevalier, C. et al. (2014).** "KrigInv: An efficient and user-friendly implementation of batch-sequential inversion strategies based on Kriging." *Computational Statistics & Data Analysis*, 71, 1021-1034. [HAL](https://hal.science/hal-00713537/)

### Sensibilidad y UQ

12. **Oakley, J.E. & O'Hagan, A. (2004).** "Probabilistic sensitivity analysis of complex models: a Bayesian approach." *JRSS-B*, 66(3), 751-769.

### Ecuaciones empiricas boulder transport

13. **Nandasena, N.A.K. et al. (2011).** "Reassessment of hydrodynamic equations." *Coastal Engineering*, 58(10), 947-962.

14. **Cox, R. et al. (2020).** "Systematic Review of Boulder Transport by Storms." *Reviews of Geophysics*.

### Software

15. **scikit-learn.** [GaussianProcessRegressor docs](https://scikit-learn.org/stable/modules/generated/sklearn.gaussian_process.GaussianProcessRegressor.html)

16. **KrigInv (R package).** [CRAN](https://cran.r-project.org/web/packages/KrigInv/index.html) — Implementacion de referencia de todos los criterios (bichon, ranjan, tMSE, SUR).

---

## 12. Novedad Cientifica

**No existe publicacion previa que combine GP + Active Learning para SPH boulder transport.**

- La busqueda en Web of Science, Scopus y Google Scholar (realizada 2026-03-20) no arroja resultados para la combinacion de:
  - Gaussian process / Kriging surrogate
  - Active learning / sequential design
  - SPH / smoothed particle hydrodynamics
  - Boulder transport / incipient motion

- Los trabajos mas cercanos son:
  - Sarfaraz & Rossi (2020): GP surrogate para tsunami inundation, pero sin AL ni boulders.
  - Stefanakis et al. (2014): GP emulador de modelo de tsunami, pero para run-up, no transporte de boulders.
  - Echard et al. (2011) y derivados: AL + Kriging, pero para confiabilidad estructural generica.

**Contribucion de la tesis:** Primer uso de GP + AL con criterio U-function para estimar umbrales de movimiento incipiente de bloques costeros bajo flujos tipo tsunami, usando simulaciones SPH de alta fidelidad como funcion objetivo.
