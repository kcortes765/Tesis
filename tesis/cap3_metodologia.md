# Capítulo 3: Metodología Numérica

## 3.1 Introducción

El presente capítulo describe la metodología numérica empleada para simular la interacción entre un flujo tipo tsunami y un bloque costero irregular mediante Hidrodinámica de Partículas Suavizadas (SPH). Se detalla la configuración del dominio computacional, las propiedades del bloque, los parámetros del solver, la integración con el motor de cuerpos rígidos ProjectChrono, y el estudio de convergencia de malla que valida la resolución espacial seleccionada para la campaña paramétrica.

Todas las simulaciones fueron realizadas con DualSPHysics v5.4.355 (GenCase v5.4.354.01), utilizando aceleración GPU y acoplamiento Chrono para la dinámica del cuerpo rígido.

---

## 3.2 Dominio Computacional

### 3.2.1 Geometría del Canal

El dominio computacional reproduce un canal con playa inclinada, diseñado para generar un flujo tipo dam-break que impacta un bloque posicionado en la zona de rompiente.

**Dimensiones del dominio:**
- Longitud: 15.0 m
- Ancho: 1.0 m
- Altura: 1.55 m
- Límites: x ∈ [-0.05, 15.05], y ∈ [-0.05, 1.05], z ∈ [-0.15, 1.55]

**Geometría del fondo:**
La playa se modela mediante un archivo STL (`Canal_Playa_1esa20_750cm.stl`) con pendiente 1:20, representativo de un perfil costero suave. Las paredes laterales, frontal y trasera se generan como partículas de contorno (boundary) tipo `drawbox` con relleno `bottom|left|right|front|back`.

### 3.2.2 Columna de Agua (Dam-Break)

La condición inicial del flujo se genera mediante una columna de agua estática que colapsa por gravedad en t = 0, produciendo una onda tipo bore que se propaga hacia la playa.

**Parámetros de la columna de agua:**
- Altura: 0.3 m (configurable en rango [0.10, 0.50] m)
- Longitud: 3.0 m
- Ancho: completo del canal (1.0 m)
- Generación: `fillbox` con semilla interior y modo `void`

Esta configuración tipo dam-break es ampliamente utilizada en la literatura para simular flujos tipo tsunami a escala de laboratorio (Noji et al., 1993; Imamura et al., 2008).

### 3.2.3 Instrumentación Virtual

Se distribuyeron 20 sensores virtuales (gauges) a lo largo del canal:

| Tipo | Cantidad | Variable | Intervalo de muestreo |
|------|----------|----------|----------------------|
| Velocidad | 12 (V01-V12) | Velocidad del flujo (m/s) | 0.001 s |
| Altura máxima | 8 (hmax01-hmax08) | Elevación máxima del agua (m) | 0.001 s |

Los gauges se posicionan automáticamente a distancias incrementales desde la posición del bloque, permitiendo caracterizar el campo de velocidades y alturas del flujo incidente.

---

## 3.3 Bloque Costero

### 3.3.1 Geometría

Se emplea un bloque irregular digitalizado mediante escaneo 3D (modelo BLIR3), representativo de un canto rodado costero.

**Propiedades geométricas (escaladas ×0.04):**

| Propiedad | Valor | Unidad |
|-----------|-------|--------|
| Dimensiones (bbox) | 17.1 × 21.0 × 4.0 | cm |
| Volumen | 0.530 | L (5.30 × 10⁻⁴ m³) |
| Diámetro equivalente (d_eq) | 10.04 | cm |
| Vértices / Caras | 1,198 / 2,392 | — |
| Estanqueidad (watertight) | Sí | — |

El diámetro equivalente se calcula como:

$$d_{eq} = \left(\frac{6V}{\pi}\right)^{1/3}$$

### 3.3.2 Propiedades Físicas

Las propiedades de masa e inercia se calculan a partir de la geometría STL usando la librería `trimesh`, que integra sobre la malla triangular cerrada para obtener valores exactos del sólido continuo.

| Propiedad | Valor | Método |
|-----------|-------|--------|
| Masa | 1.061 kg | Explícita (`massbody`) |
| Densidad implícita | 2000 kg/m³ | M/V desde trimesh |
| Centro de masa (local) | (-0.020, 0.012, 0.018) m | trimesh |
| Inercia Ixx | 0.00219 kg·m² | trimesh |
| Inercia Iyy | 0.00158 kg·m² | trimesh |
| Inercia Izz | 0.00361 kg·m² | trimesh |

**Corrección crítica:** Se identificó que GenCase sobreestima la inercia en un factor de 1.85× a 3.01× cuando se usa dp grueso (dp = 0.05 m), debido a que la discretización SPH agranda el volumen efectivo del cuerpo. Por esta razón, se inyectan los valores de inercia calculados por trimesh directamente en el XML mediante la etiqueta `<inertia>`, en lugar de usar los valores auto-calculados por GenCase.

**Posición en el dominio:**
- Posición inicial: (8.5, 0.5, 0.1) m
- Rotación inicial: configurable (0°, 0°, 0°) por defecto

### 3.3.3 Problema del Cuerpo Hueco

La importación de geometría STL mediante `drawfilestl` en DualSPHysics genera únicamente partículas en la superficie del cuerpo, dejando el interior vacío. Un bloque hueco tiene un comportamiento dinámico radicalmente diferente a un sólido (menor masa efectiva, inercia incorrecta).

**Solución implementada:** Después de importar la superficie STL, se aplica un `fillbox` con modo `void` cuya semilla se ubica en el centroide del mesh (calculado por trimesh). Esto rellena el interior con partículas de contorno, produciendo un sólido completo. Adicionalmente, se especifica la masa real del cuerpo mediante `massbody` para evitar errores de discretización volumétrica.

---

## 3.4 Parámetros del Solver SPH

### 3.4.1 Configuración General

| Parámetro | Valor | Justificación |
|-----------|-------|---------------|
| Kernel | Wendland (C2) | Estándar para cuerpos flotantes en SPH |
| Integración temporal | Symplectic (2° orden) | Mayor precisión que Verlet |
| Viscosidad | Artificial, α = 0.05 | Estabiliza sin excesiva disipación |
| Difusión de densidad | Fourtakas (DDT tipo 2), δ = 0.1 | Reduce ruido en campo de presión |
| CFL | 0.2 | Conservador, garantiza estabilidad |
| Coeficiente h | 0.75 | h = 0.75 × √(3 × dp²) |
| Precisión posicional | Doble (`posdouble:1`) | Necesario para dominios > 10 m |

### 3.4.2 Dinámica del Cuerpo Rígido (ProjectChrono)

La interacción entre el fluido SPH y el bloque rígido se resuelve mediante el acoplamiento con ProjectChrono (`RigidAlgorithm = 3`), que maneja:

- Dinámica de cuerpo rígido (traslación y rotación)
- Detección y resolución de colisiones
- Fuerzas de fricción en el contacto bloque-fondo

**Parámetros de Chrono:**

| Parámetro | Valor |
|-----------|-------|
| Método de contacto | NSC (Non-Smooth Contacts) |
| Margen de colisión | 0.5 × dp |
| Intervalo de guardado CSV | 0.001 s |
| Cuerpos | BLIR (flotante), beach (fijo) |

**Propiedades de material (PVC/Acero — configuración de laboratorio):**

| Material | Módulo Young (Pa) | Poisson | Restitución | Fricción cinética |
|----------|-------------------|---------|-------------|-------------------|
| PVC (bloque) | 3.0 × 10⁹ | 0.30 | 0.60 | 0.15 |
| Acero (canal) | 2.1 × 10¹¹ | 0.35 | 0.80 | 0.35 |

**Nota:** Los valores de fricción corresponden a una configuración de laboratorio (PVC sobre acero). Para escenarios de campo, se deberán ajustar a materiales tipo caliza (μ ≈ 0.35-0.50).

### 3.4.3 Tiempo de Asentamiento (FtPause)

Se implementa un período de congelamiento de 0.5 s (`FtPause = 0.5`) durante el cual el bloque permanece inmóvil. Esto permite que:

1. El fluido se asiente bajo gravedad
2. Las presiones hidrostáticas se estabilicen
3. Se eliminen perturbaciones numéricas iniciales

Sin este período, el bloque experimenta aceleraciones espurias al inicio de la simulación que no tienen origen físico.

---

## 3.5 Datos de Salida

### 3.5.1 Cinemática del Bloque (ChronoExchange)

El archivo `ChronoExchange_mkbound_51.csv` se genera automáticamente durante la simulación y contiene, para cada paso de tiempo (Δt = 0.001 s):

| Variable | Columnas | Unidades |
|----------|----------|----------|
| Posición centro de masa | fcenter.x, .y, .z | m |
| Velocidad lineal | fvel.x, .y, .z | m/s |
| Velocidad angular | fomega.x, .y, .z | rad/s |
| Aceleración lineal | face.x, .y, .z | m/s² |
| Aceleración angular | fomegaace.x, .y, .z | rad/s² |

### 3.5.2 Fuerzas sobre el Bloque (ChronoBody_forces)

El archivo `ChronoBody_forces.csv` registra las fuerzas hidrodinámicas SPH y las fuerzas de contacto Chrono por separado:

| Componente | Variables | Unidades |
|------------|-----------|----------|
| Fuerza total SPH (incluye gravedad) | fx, fy, fz | N |
| Momento total SPH | mx, my, mz | N·m |
| Fuerza de contacto (Chrono) | cfx, cfy, cfz | N |
| Momento de contacto (Chrono) | cmx, cmy, cmz | N·m |

**Nota importante:** Las columnas fx, fy, fz incluyen la contribución gravitacional. En reposo sin fluido, fz = −m·g. Para obtener la fuerza hidrodinámica neta, se debe restar el peso propio del bloque.

**Formato CSV:** Separador punto y coma (`;`), decimal punto (`.`), precisión 6 cifras significativas.

### 3.5.3 Criterio de Fallo (Movimiento Incipiente)

Se define movimiento incipiente cuando el bloque excede un umbral de desplazamiento relativo a su diámetro equivalente:

$$\frac{\Delta_{CM}}{d_{eq}} > \text{umbral}$$

donde Δ_CM es la distancia euclidiana del centro de masa respecto a su posición inicial.

Los umbrales específicos (% del diámetro equivalente para desplazamiento y grados para rotación) están pendientes de validación académica con el director de tesis.

**Nota sobre fuerza de contacto:** El estudio de convergencia (Sección 3.6) demostró que la fuerza de contacto Chrono no converge con el refinamiento de malla (CV = 82%), por lo que **no se utiliza como criterio de fallo**. Este hallazgo se discute en detalle en el Capítulo 4.

---

## 3.6 Estudio de Convergencia de Malla

### 3.6.1 Objetivo

Antes de la campaña paramétrica, se realizó un estudio de convergencia de malla para determinar la resolución espacial (dp) mínima que produce resultados independientes de la discretización.

### 3.6.2 Resoluciones Evaluadas

Se evaluaron 7 resoluciones espaciales, desde dp = 0.020 m (gruesa) hasta dp = 0.003 m (fina):

| dp (m) | Partículas | dim_min/dp | Tiempo GPU (min) |
|--------|------------|------------|------------------|
| 0.020 | 209,103 | 2.0 | 13.2 |
| 0.015 | 495,652 | 2.7 | 11.7 |
| 0.010 | 1,672,824 | 4.0 | 23.7 |
| 0.008 | 3,267,234 | 5.0 | 30.3 |
| 0.005 | 13,382,592 | 8.0 | 117.8 |
| 0.004 | 26,137,875 | 10.0 | 260.1 |
| 0.003 | 61,956,444 | 13.3 | 812.1 |

donde dim_min/dp es el número de partículas en la dimensión mínima del bloque (4.0 cm).

**Tiempo total de cómputo GPU:** 1,269 minutos (21.1 horas) en RTX 5090 (32 GB VRAM).

### 3.6.3 Criterio de Convergencia

Se emplea el criterio de cambio relativo (delta porcentual) entre resoluciones consecutivas:

$$\delta_{\%} = \frac{|f_{dp_i} - f_{dp_{i-1}}|}{|f_{dp_{i-1}}|} \times 100$$

Se considera convergida una métrica cuando δ% < 5% entre las dos resoluciones más finas.

### 3.6.4 Métricas Evaluadas

Se monitorearon cinco métricas independientes:

1. **Desplazamiento máximo del centro de masa** (métrica primaria)
2. **Fuerza hidrodinámica SPH máxima**
3. **Velocidad máxima del bloque**
4. **Rotación total acumulada**
5. **Fuerza de contacto máxima**

### 3.6.5 Resultados

| Métrica | δ% (dp=0.004 → 0.003) | Veredicto |
|---------|------------------------|-----------|
| Desplazamiento | 3.9% | **CONVERGIDO** |
| Fuerza SPH | 2.8% | **CONVERGIDA** |
| Velocidad | 0.8% | **CONVERGIDA** |
| Rotación | 6.3% | Estabilizada |
| Fuerza de contacto | CV = 82% | **NO CONVERGE** |

Las tres métricas primarias (desplazamiento, fuerza SPH, velocidad) presentan δ% < 5% entre las dos resoluciones más finas, confirmando convergencia.

**Hallazgo: No convergencia de la fuerza de contacto.** La fuerza de contacto entre el bloque y el fondo presenta un coeficiente de variación del 82% entre las 7 resoluciones, sin tendencia monótona. Este comportamiento es inherente a la naturaleza discreta del contacto en SPH, donde la geometría de las partículas en la interfaz cambia con cada resolución. Este hallazgo tiene implicancias para estudios de impacto en SPH y se documenta como contribución científica de esta tesis. Ver Figuras 3.1 a 3.9.

### 3.6.6 Resolución Seleccionada

Se selecciona **dp = 0.004 m** para la campaña paramétrica por las siguientes razones:

1. **Convergencia verificada:** δ < 5% en las tres métricas primarias respecto a dp = 0.003
2. **Resolución adecuada:** 10 partículas en la dimensión mínima del bloque (criterio mínimo)
3. **Eficiencia computacional:** 260 min por caso vs. 812 min para dp = 0.003 (3.1× más rápido)
4. **Viabilidad de producción:** 50 casos × 260 min = 217 horas (9 días) en RTX 5090

---

## 3.7 Pipeline Computacional

### 3.7.1 Arquitectura

El pipeline se implementa en Python y consta de 4 módulos desacoplados:

```
┌────────────┐   ┌────────────┐   ┌────────────┐   ┌────────────┐   ┌──────────┐
│  Geometry  │──►│   Batch    │──►│    Data    │──►│     ML     │──►│    UQ    │
│  Builder   │   │   Runner   │   │  Cleaner   │   │ Surrogate  │   │ (Sobol+  │
│ (STL→XML)  │   │ (GPU SPH)  │   │ (CSV→SQL)  │   │ (GP + AL)  │   │  MC+CI)  │
└────────────┘   └────────────┘   └────────────┘   └────────────┘   └──────────┘
                       ▲                                  │
                       └────── Active Learning loop ──────┘
```

**Módulo 1 — Geometry Builder:** Toma la geometría STL del bloque y una plantilla XML base. Usando `trimesh`, calcula centro de masa, volumen, e inercia del bloque. Inyecta estos valores junto con los parámetros del experimento (altura de columna, masa, rotación) en el XML mediante `lxml`.

**Módulo 2 — Batch Runner:** Ejecuta la cadena GenCase → DualSPHysics para cada caso. Maneja timeouts, captura logs, y garantiza la limpieza de archivos binarios temporales (`.bi4`) en un bloque `try/finally`. Los archivos `.bi4` pueden generar hasta 17 GB por simulación.

**Módulo 3 — Data Cleaner (ETL):** Extrae cinemática del bloque desde `ChronoExchange_mkbound_51.csv`, fuerzas desde `ChronoBody_forces.csv`, y datos del flujo desde los archivos Gauge. Aplica criterios de fallo y almacena resultados en SQLite.

**Módulo 4 — ML Surrogate + Active Learning:** Entrena un regresor de procesos gaussianos (GP) sobre los resultados disponibles y evalúa la función de adquisición U (Echard et al., 2011) para seleccionar el siguiente punto a simular. El ciclo adaptativo re-entrena el GP tras cada nueva observación y repite hasta alcanzar el criterio de parada (Secciones 3.8 y 3.9).

**Módulo 5 — Cuantificación de Incertidumbre (UQ):** Una vez entrenado el GP surrogate, se propagan las incertidumbres de los parámetros de entrada mediante Monte Carlo (10,000 muestras evaluadas sobre el GP en segundos). Se calculan intervalos de confianza al 95% y se realiza análisis de sensibilidad global mediante índices de Sobol (Sobol', 2001; Saltelli, 2002), identificando qué parámetros dominan la variabilidad del resultado. Este enfoque sigue el precedente de Salmanidou et al. (2017, 2020), quienes aplicaron GP + Monte Carlo + Sobol a simulaciones SPH de tsunami.

### 3.7.2 Diseño de Experimentos

La campaña paramétrica emplea Muestreo por Hipercubo Latino (LHS) con `scipy.stats.qmc.LatinHypercube` (semilla = 42) para distribuir uniformemente los casos en el espacio de parámetros.

**Parámetros de entrada (pendientes de validación):**

| Parámetro | Rango | Unidad | Estado |
|-----------|-------|--------|--------|
| Altura columna de agua | 0.10 – 0.50 | m | Tentativo |
| Masa del bloque | 0.80 – 1.60 | kg | Tentativo |
| Ángulo de rotación Z | 0 – 90 | grados | Tentativo |

**Número de casos:** 50 (modo producción)

### 3.7.3 Hardware

| Componente | Desarrollo (laptop) | Producción (workstation) |
|------------|---------------------|--------------------------|
| GPU | RTX 4060 (8 GB VRAM) | RTX 5090 (32 GB VRAM) |
| CPU | i7-14650HX | i9-14900KF |
| Uso | Pruebas, dp ≥ 0.02 | Campaña completa, dp = 0.004 |

---

## 3.8 Modelo Surrogate: Procesos Gaussianos

### 3.8.1 Motivación

Cada simulación SPH a la resolución de producción (dp = 0.004 m) requiere entre 45 y 90 minutos en una GPU RTX 5090. Un barrido exhaustivo del espacio paramétrico mediante fuerza bruta resulta prohibitivo: evaluar una grilla de 50 × 50 puntos demandaría más de 100 días de cómputo continuo. Para superar esta limitación, se emplea un modelo surrogate basado en Procesos Gaussianos (GP), capaz de interpolar la respuesta del simulador a partir de un número reducido de evaluaciones (~25-30 simulaciones) y proporcionar estimaciones de incertidumbre en cada predicción (Rasmussen y Williams, 2006).

El GP actúa como un emulador del simulador SPH: dados los parámetros de entrada $(h_d, m_b)$ —altura de la columna de agua y masa del bloque—, predice el desplazamiento máximo del centro de masa $\Delta_{CM}$ junto con una banda de confianza asociada. Esta capacidad de cuantificar la incertidumbre es fundamental para el esquema de aprendizaje activo descrito en la Sección 3.9.

### 3.8.2 Formulación del Proceso Gaussiano

Un Proceso Gaussiano define una distribución de probabilidad sobre funciones $f: \mathbb{R}^d \rightarrow \mathbb{R}$, especificada completamente por una función media $m(\mathbf{x})$ y una función de covarianza (kernel) $k(\mathbf{x}, \mathbf{x}')$:

$$f(\mathbf{x}) \sim \mathcal{GP}\left(m(\mathbf{x}),\; k(\mathbf{x}, \mathbf{x}')\right)$$

Dadas $n$ observaciones $\mathcal{D} = \{(\mathbf{x}_i, y_i)\}_{i=1}^{n}$ donde $y_i = f(\mathbf{x}_i) + \varepsilon_i$ con $\varepsilon_i \sim \mathcal{N}(0, \sigma_n^2)$, la distribución predictiva en un punto nuevo $\mathbf{x}_*$ es Gaussiana:

$$f(\mathbf{x}_*) \mid \mathcal{D} \sim \mathcal{N}\left(\mu(\mathbf{x}_*),\; \sigma^2(\mathbf{x}_*)\right)$$

con media y varianza predictivas:

$$\mu(\mathbf{x}_*) = \mathbf{k}_*^T \left(\mathbf{K} + \sigma_n^2 \mathbf{I}\right)^{-1} \mathbf{y}$$

$$\sigma^2(\mathbf{x}_*) = k(\mathbf{x}_*, \mathbf{x}_*) - \mathbf{k}_*^T \left(\mathbf{K} + \sigma_n^2 \mathbf{I}\right)^{-1} \mathbf{k}_*$$

donde $\mathbf{K}$ es la matriz de covarianza entre las observaciones, $\mathbf{k}_*$ es el vector de covarianzas entre $\mathbf{x}_*$ y las observaciones, $\mathbf{y}$ es el vector de respuestas observadas, y $\sigma_n^2$ es la varianza del ruido (nugget).

### 3.8.3 Kernel Matérn 5/2 con ARD

Se selecciona el kernel Matérn con parámetro de suavidad $\nu = 5/2$, que produce funciones dos veces diferenciables ($C^2$). Su expresión es:

$$k_{\text{M52}}(r) = \sigma_f^2 \left(1 + \sqrt{5}\,r + \frac{5}{3}\,r^2\right) \exp\left(-\sqrt{5}\,r\right)$$

donde $\sigma_f^2$ es la varianza de señal y $r$ es la distancia ponderada entre puntos. Se emplea la variante ARD (Automatic Relevance Determination) con un *length-scale* independiente por dimensión:

$$r = \sqrt{\sum_{j=1}^{d} \frac{(x_j - x_j')^2}{\ell_j^2}}$$

Los *length-scales* $\ell_1$ (asociado a $h_d$) y $\ell_2$ (asociado a $m_b$) se optimizan durante el entrenamiento, permitiendo que el GP aprenda automáticamente la anisotropía del espacio paramétrico; es decir, qué variable de entrada tiene mayor influencia sobre la respuesta.

**Justificación de Matérn 5/2 sobre RBF:** El kernel RBF (Squared Exponential, equivalente a $\nu \to \infty$) produce funciones infinitamente diferenciables, lo que puede sobre-suavizar la transición entre zonas de movimiento y no-movimiento del bloque. El kernel Matérn 3/2 ($\nu = 3/2$) genera funciones solo una vez diferenciables, potencialmente demasiado rugosas. Matérn 5/2 representa el balance óptimo para procesos físicos que son suaves pero no analíticos (Rasmussen y Williams, 2006, Cap. 4), y es el kernel predeterminado en la mayoría de frameworks de optimización bayesiana modernos.

El kernel completo incluye un término de ruido (White kernel) para estabilidad numérica:

$$k(\mathbf{x}, \mathbf{x}') = \sigma_f^2 \, k_{\text{M52}}(\mathbf{x}, \mathbf{x}') + \sigma_n^2 \, \delta(\mathbf{x}, \mathbf{x}')$$

donde $\sigma_n^2 \sim 10^{-5}$ actúa como jitter para regularizar la inversión de la matriz de covarianza. Aunque las simulaciones SPH son determinísticas, el nugget previene inestabilidades numéricas y captura variaciones menores asociadas a la discretización.

### 3.8.4 Entrenamiento y Optimización de Hiperparámetros

Los hiperparámetros del kernel $\boldsymbol{\theta} = \{\sigma_f^2, \ell_1, \ell_2, \sigma_n^2\}$ se estiman maximizando la log-verosimilitud marginal (log-marginal likelihood):

$$\log p(\mathbf{y} \mid \mathbf{X}, \boldsymbol{\theta}) = -\frac{1}{2} \mathbf{y}^T \mathbf{K}_\theta^{-1} \mathbf{y} - \frac{1}{2} \log |\mathbf{K}_\theta| - \frac{n}{2} \log 2\pi$$

La optimización se realiza mediante L-BFGS-B con 20 reinicializaciones aleatorias para mitigar óptimos locales, lo cual es especialmente importante con pocas observaciones ($n \leq 30$) donde la superficie de verosimilitud puede ser multimodal (Loeppky et al., 2009).

Se emplea la implementación `GaussianProcessRegressor` de scikit-learn, que para $n \leq 30$ tiene complejidad $O(n^3) \approx O(27000)$, resultando en tiempos de entrenamiento del orden de milisegundos. Esto permite re-entrenar el GP en cada iteración del ciclo de aprendizaje activo sin costo computacional significativo.

### 3.8.5 Validación: Leave-One-Out Cross-Validation

La capacidad predictiva del GP se evalúa mediante validación cruzada Leave-One-Out (LOO-CV). Para cada observación $i$, se entrena el GP con las $n-1$ observaciones restantes y se predice $\hat{y}_i$. La métrica principal es el coeficiente de determinación LOO:

$$R^2_{\text{LOO}} = 1 - \frac{\sum_{i=1}^{n} (y_i - \hat{y}_i)^2}{\sum_{i=1}^{n} (y_i - \bar{y})^2}$$

Adicionalmente, se verifica la calibración del GP: los intervalos de confianza al 95% deben contener aproximadamente el 95% de las observaciones LOO. Una cobertura significativamente inferior indicaría sobreconfianza del modelo, mientras que una cobertura excesiva señalaría un GP demasiado conservador.

Para el GP con kernel Matérn, la predicción LOO se puede obtener analíticamente sin re-entrenar el modelo $n$ veces, usando las ecuaciones de Duvenaud (2014):

$$\hat{y}_i^{\text{LOO}} = y_i - \frac{[\mathbf{K}^{-1} \mathbf{y}]_i}{[\mathbf{K}^{-1}]_{ii}}, \quad \sigma_i^{\text{LOO}} = \frac{1}{\sqrt{[\mathbf{K}^{-1}]_{ii}}}$$

lo que permite calcular la validación LOO completa en una sola inversión matricial.

---

## 3.9 Aprendizaje Activo para Estimación de Contorno

### 3.9.1 Concepto

El aprendizaje activo (Active Learning) es una estrategia de diseño secuencial de experimentos donde el modelo surrogate guía la selección del siguiente punto a evaluar, concentrando las simulaciones costosas en las regiones del espacio paramétrico donde la incertidumbre es mayor o donde se espera que se ubique el contorno de interés (Bryan et al., 2005; Echard et al., 2011). A diferencia del muestreo pasivo (p. ej., LHS puro), el aprendizaje activo adapta la distribución de las observaciones a la estructura de la función objetivo, logrando la misma precisión con significativamente menos evaluaciones.

En este trabajo, el contorno de interés es la **frontera de movimiento incipiente**: el conjunto de puntos $(h_d, m_b)$ donde el desplazamiento del bloque iguala un umbral predefinido $T$. Formalmente:

$$\mathcal{C}_T = \left\{(h_d, m_b) \in \Omega : f(h_d, m_b) = T\right\}$$

donde $f$ es la función de respuesta (desplazamiento máximo) y $\Omega = [0.10, 0.50] \times [0.80, 1.60]$ es el dominio paramétrico.

### 3.9.2 Función de Adquisición: U-function

Se adopta la función U (U-learning function) propuesta por Echard et al. (2011) en el contexto de análisis de confiabilidad estructural (método AK-MCS). La U-function cuantifica la confianza del GP en la clasificación de cada punto respecto al umbral $T$:

$$U(\mathbf{x}) = \frac{|\mu(\mathbf{x}) - T|}{\sigma(\mathbf{x})}$$

donde $\mu(\mathbf{x})$ y $\sigma(\mathbf{x})$ son la media y desviación estándar predictivas del GP en el punto $\mathbf{x}$.

**Interpretación geométrica:** $U(\mathbf{x})$ mide cuántas desviaciones estándar separan la predicción media del umbral. Un valor $U < 2$ indica que el intervalo de confianza al 95% del GP contiene el umbral $T$, es decir, el modelo no puede distinguir con suficiente certeza si $f(\mathbf{x}) > T$ o $f(\mathbf{x}) < T$. La probabilidad de clasificación errónea en un punto con valor $U$ es:

$$P(\text{error}) = \Phi(-U)$$

donde $\Phi$ es la función de distribución acumulada de la normal estándar. Para $U \geq 2$, $P(\text{error}) \leq \Phi(-2) = 0.0228$ (2.3%).

**Regla de selección:** En cada iteración del ciclo de aprendizaje activo, se selecciona para simulación el punto con menor valor de $U$ sobre un conjunto de candidatos $\mathcal{S}$:

$$\mathbf{x}^* = \arg\min_{\mathbf{x} \in \mathcal{S}} U(\mathbf{x})$$

Este punto corresponde a la ubicación donde el GP tiene mayor incertidumbre sobre la clasificación respecto al umbral, maximizando el valor informativo de la siguiente simulación.

### 3.9.3 Comparación con Otras Funciones de Adquisición

La U-function se seleccionó tras evaluar alternativas reportadas en la literatura:

| Criterio | Referencia | Tipo | Criterio de parada | Complejidad |
|----------|-----------|------|-------------------|-------------|
| Straddle | Bryan et al. (2005) | Heurístico | No natural | Muy baja |
| **U-function** | **Echard et al. (2011)** | **Puntual** | **$U \geq 2$ (natural)** | **Baja** |
| EI contour | Ranjan et al. (2008) | Puntual | No natural | Media |
| tMSE | Picheny et al. (2010) | Puntual | No natural | Media |
| SUR | Bect et al. (2012) | Global | Convergencia integral | Alta |

La heurística de *straddle* (Bryan et al., 2005) selecciona puntos donde el intervalo de confianza del GP "cruza" el umbral: $a_{\text{straddle}}(\mathbf{x}) = \alpha \sigma(\mathbf{x}) - |\mu(\mathbf{x}) - T|$, con $\alpha = 1.96$. Aunque simple, carece de criterio de parada formal. La Expected Improvement for Contour (Ranjan et al., 2008) maximiza la reducción esperada de distancia al contorno, pero su implementación es más compleja y no ofrece un criterio de convergencia natural. El criterio SUR (Bect et al., 2012) es teóricamente óptimo al minimizar una medida global de incertidumbre, pero computacionalmente prohibitivo para aplicaciones iterativas.

La U-function combina simplicidad de implementación, interpretación probabilística directa, criterio de parada integrado, y amplia validación en ingeniería estructural (más de 2000 citas), lo que la convierte en la elección natural para este estudio.

### 3.9.4 Criterio de Parada

Se emplea un criterio combinado para la terminación del ciclo de aprendizaje activo:

1. **Convergencia de clasificación ($U \geq 2$):** El ciclo se detiene cuando el mínimo de $U$ sobre todos los candidatos alcanza o supera 2.0:

$$\min_{\mathbf{x} \in \mathcal{S}} U(\mathbf{x}) \geq 2.0$$

Esto garantiza que todos los puntos del dominio tienen al menos 97.7% de probabilidad de estar correctamente clasificados respecto al umbral $T$.

2. **Estabilidad del contorno:** El contorno estimado se considera estable cuando la variación máxima de la probabilidad de excedencia entre iteraciones consecutivas es inferior a 1% durante 3 iteraciones:

$$\max_{\mathbf{x} \in \mathcal{S}} \left|P_n(f(\mathbf{x}) > T) - P_{n-1}(f(\mathbf{x}) > T)\right| < 0.01, \quad \text{por 3 iteraciones consecutivas}$$

3. **Presupuesto computacional:** Máximo de 30 simulaciones totales (20 del batch inicial + 10 del ciclo adaptativo). A dp = 0.004 m, cada simulación demanda entre 45 y 90 minutos en la RTX 5090, totalizando un presupuesto de 22.5 a 45 horas.

El ciclo termina cuando se activa cualquiera de los tres criterios, reportando cuál fue el criterio determinante.

### 3.9.5 Umbral de Movimiento

Se define el umbral de movimiento incipiente como $T = d_{eq}$, donde $d_{eq}$ es el diámetro equivalente esférico del bloque. Para el bloque BLIR3 a escala 0.04, $d_{eq} \approx 0.10$ m. Un desplazamiento del centro de masa superior a su propio diámetro equivalente se interpreta como transporte efectivo del bloque.

Una ventaja del enfoque basado en GP con respuesta continua es que el umbral $T$ puede ajustarse *a posteriori* sin necesidad de re-ejecutar simulaciones. La frontera de movimiento $\mathcal{C}_T$ se recalcula instantáneamente para cualquier valor de $T$, permitiendo explorar distintas definiciones de movimiento incipiente ($T = 0.5\,d_{eq}$, $T = d_{eq}$, $T = 2\,d_{eq}$) sobre el mismo modelo surrogate.

### 3.9.6 Arquitectura del Ciclo Adaptativo

El ciclo de aprendizaje activo opera de la siguiente forma:

```
                    ┌──────────────────┐
                    │  Batch inicial   │
                    │  (20 sims SPH)   │
                    └────────┬─────────┘
                             │
                             v
                    ┌──────────────────┐
              ┌────>│  Entrenar GP     │
              │     │  (Matérn 5/2)    │
              │     └────────┬─────────┘
              │              │
              │              v
              │     ┌──────────────────┐
              │     │ Evaluar U(x) en  │
              │     │ grilla candidata │
              │     └────────┬─────────┘
              │              │
              │              v
              │     ┌──────────────────┐
              │     │ ¿Criterio de     │──── SÍ ──> DETENER
              │     │  parada?         │
              │     └────────┬─────────┘
              │              │ NO
              │              v
              │     ┌──────────────────┐
              │     │ Seleccionar      │
              │     │ x* = argmin U(x) │
              │     └────────┬─────────┘
              │              │
              │              v
              │     ┌──────────────────┐
              │     │ Simular x* (SPH) │
              │     └────────┬─────────┘
              │              │
              └──────────────┘
```

La grilla de candidatos $\mathcal{S}$ consiste en una malla regular de $50 \times 50 = 2500$ puntos sobre el dominio $\Omega$, con resolución $\Delta h_d = 0.008$ m y $\Delta m_b = 0.016$ kg. Se excluyen puntos ya simulados (distancia mínima en espacio normalizado $> 0.01$). En cada iteración se selecciona un único punto para simulación (modo secuencial puro), ya que con $d = 2$ dimensiones cada nueva observación actualiza significativamente el GP, y el re-entrenamiento ($< 1$ ms) es despreciable frente al tiempo de simulación (Echard et al., 2011).

---

## 3.10 Diseño Experimental: Batch Inicial

### 3.10.1 Espacio Paramétrico

El estudio se formula en un espacio paramétrico bidimensional:

| Parámetro | Símbolo | Mínimo | Máximo | Unidad | Justificación |
|-----------|---------|--------|--------|--------|---------------|
| Altura de columna de agua | $h_d$ | 0.10 | 0.50 | m | 0.10 m = sin movimiento; 0.50 m = transporte extremo |
| Masa del bloque | $m_b$ | 0.80 | 1.60 | kg | Densidades de 1500 a 3100 kg/m³ para BLIR3 a escala 0.04 |

La rotación del bloque respecto al eje vertical ($\theta_z$) se mantiene fija en 0° para el estudio 2D inicial. La **variable de respuesta** es el desplazamiento máximo del centro de masa $\Delta_{CM}$ (en metros), tratada como respuesta continua $\geq 0$.

### 3.10.2 Tamaño del Batch Inicial

El tamaño del batch inicial sigue la regla empírica de Loeppky et al. (2009): para un GP con $d$ dimensiones de entrada, el número mínimo de observaciones iniciales es $n_0 = 10d$. Para $d = 2$:

$$n_0 = 10 \times 2 = 20 \text{ puntos}$$

Esta regla se fundamenta en que con menos de $10d$ puntos, los *length-scales* del GP quedan mal estimados debido a que la superficie de verosimilitud marginal presenta múltiples óptimos locales (Loeppky et al., 2009). Con un presupuesto total de 30 simulaciones, los 10 restantes se asignan al ciclo de aprendizaje activo.

### 3.10.3 Estrategia de Muestreo

Se emplea una estrategia híbrida de Muestreo por Hipercubo Latino optimizado (LHS-maximin) con puntos fijos en las esquinas y centro del dominio:

- **4 puntos en las esquinas** del dominio: anclan la predicción del GP en los extremos, evitando extrapolación. Cubren los cuatro regímenes físicos esperados:
  - $(h_d, m_b) = (0.10, 0.80)$: ola débil + bloque liviano → movimiento leve o nulo
  - $(h_d, m_b) = (0.10, 1.60)$: ola débil + bloque pesado → sin movimiento
  - $(h_d, m_b) = (0.50, 0.80)$: ola fuerte + bloque liviano → transporte completo
  - $(h_d, m_b) = (0.50, 1.60)$: ola fuerte + bloque pesado → movimiento moderado

- **1 punto en el centro** $(0.30, 1.20)$: referencia en la zona de mayor interés, presumiblemente cercana a la frontera de movimiento.

- **15 puntos LHS interiores**: generados con `scipy.stats.qmc.LatinHypercube`, optimizados evaluando 500 semillas y seleccionando aquella con la máxima distancia mínima entre puntos en el espacio normalizado $[0,1]^2$ (criterio maximin). Los 5 puntos LHS más cercanos a las posiciones fijas se reemplazan por éstas, preservando la cobertura general del diseño.

Esta estrategia mitiga el comportamiento patológico que pueden exhibir los diseños *space-filling* puros como *seed designs* para GP secuenciales en baja dimensión (Zhang et al., 2020), al garantizar observaciones en los extremos del dominio.

### 3.10.4 Compatibilidad con el Pipeline

La matriz del batch inicial se almacena en `config/gp_initial_batch.csv` con las mismas columnas que `experiment_matrix.csv` (`case_id`, `dam_height`, `boulder_mass`, `boulder_rot_z`), lo que permite su ejecución directa por `main_orchestrator.py` sin modificaciones al pipeline existente. Los identificadores de caso usan el prefijo `gp_` (p. ej., `gp_001` a `gp_020`) para distinguirlos de los casos LHS previos.

---

## 3.11 Validación Física y Sanity Checks

### 3.11.1 Propósito

Antes de iniciar el ciclo de aprendizaje activo, se ejecuta un conjunto de verificaciones de consistencia física (*sanity checks*) sobre los resultados del batch inicial. Estas verificaciones no constituyen una validación experimental (no se dispone de datos de laboratorio para esta configuración específica), sino una confrontación de los resultados numéricos con predicciones teóricas y tendencias físicas esperadas. El objetivo es detectar errores sistemáticos en la simulación o en el post-procesamiento antes de que se propaguen al modelo surrogate.

### 3.11.2 Ecuación de Ritter: Velocidad Analítica del Dam-Break

La solución analítica de Ritter (1892) para un dam-break instantáneo sobre lecho seco proporciona la velocidad del frente de onda:

$$v_{\text{frente}} = 2\sqrt{g \, h_0}$$

donde $g = 9.81$ m/s² y $h_0$ es la altura inicial del reservorio. La celeridad de la onda es $c_0 = \sqrt{g \, h_0}$.

| $h_d$ [m] | $c_0$ [m/s] | $v_{\text{frente}}$ (Ritter) [m/s] | $v_{\text{SPH}}$ esperada [m/s] |
|-----------|-------------|-----------------------------------|-------------------------------|
| 0.10 | 0.990 | 1.981 | 1.7 – 1.9 |
| 0.30 | 1.716 | 3.431 | 2.9 – 3.3 |
| 0.50 | 2.215 | 4.429 | 3.8 – 4.2 |

La solución de Ritter sobreestima la velocidad real al ignorar la fricción con el fondo, la viscosidad del fluido y los efectos tridimensionales. Se espera que la velocidad pico registrada por los gauges de velocidad en DualSPHysics sea un 5-15% inferior a la predicción analítica. Una velocidad SPH **superior** a la de Ritter indicaría un error en la configuración.

### 3.11.3 Ecuaciones de Nandasena (2011): Velocidad Mínima de Flujo

Nandasena et al. (2011) derivaron la velocidad mínima de flujo (MFV) necesaria para iniciar el transporte de un bloque, distinguiendo tres modos para un bloque subaéreo no confinado sobre superficie plana ($\theta = 0$):

**Deslizamiento (*sliding*):**

$$u_{\text{slide}}^2 = \frac{2g\left(\frac{\rho_s}{\rho_w} - 1\right) c \, \mu_s}{C_d \frac{c}{b} + \mu_s C_l}$$

**Vuelco (*rolling/overturning*):**

$$u_{\text{roll}}^2 = \frac{2g\left(\frac{\rho_s}{\rho_w} - 1\right) c}{C_d \left(\frac{c}{b}\right)^2 + C_l}$$

**Levantamiento (*lifting/saltation*):**

$$u_{\text{lift}}^2 = \frac{2g\left(\frac{\rho_s}{\rho_w} - 1\right) c}{C_l}$$

donde $\rho_s$ es la densidad del bloque, $\rho_w$ la densidad del agua, $c$ el eje menor del bloque (altura), $b$ el eje intermedio, $\mu_s$ el coeficiente de fricción estática, y $C_d$, $C_l$ los coeficientes de arrastre y sustentación respectivamente. Los valores estándar de la literatura son $C_d = 1.95$ (Einstein y El-Samni, 1949; Nott, 2003) y $C_l = 0.178$ (Einstein y El-Samni, 1949).

Estas ecuaciones se emplean como verificación de orden de magnitud: la velocidad del flujo registrada en la simulación debe superar $u_{\text{slide}}$ para que se observe movimiento del bloque.

### 3.11.4 Limitaciones de las Ecuaciones Empíricas

Cox et al. (2020) demostraron mediante una revisión sistemática que las ecuaciones de Nott (2003) y Nandasena (2011) presentan limitaciones fundamentales:

1. El parámetro $\delta = Fr^2$ (número de Froude al cuadrado) no es constante sino que varía continuamente según la batimetría y topografía local.
2. Los coeficientes hidrodinámicos ($C_d$, $C_l$) son altamente inciertos; en particular, $C_l$ puede alcanzar valores de hasta 2.0 en lugar del estándar 0.178.
3. Las ecuaciones no pueden reconstruir las condiciones de oleaje a partir de depósitos de bloques (*hindcast*).

Estas limitaciones constituyen una motivación central del presente trabajo: la simulación numérica SPH resuelve las ecuaciones de Navier-Stokes completas sin asumir coeficientes constantes ni número de Froude fijo, mientras que el acoplamiento con Chrono captura la dinámica del contacto de forma mecánica.

### 3.11.5 Protocolo de Verificación

Se definen las siguientes verificaciones obligatorias sobre los resultados del batch inicial de 20 simulaciones:

| Verificación | Resultado esperado | Acción si falla |
|--------------|-------------------|-----------------|
| Caso $(0.50, 0.80)$ | Máximo desplazamiento de los 20 casos | Revisar configuración |
| Caso $(0.10, 1.60)$ | Desplazamiento $\approx 0$ | Revisar FtPause y asentamiento |
| Monotonicidad en $h_d$ | Mayor $h_d$ → mayor desplazamiento (a $m_b$ fijo) | Revisar energía del dam-break |
| Monotonicidad en $m_b$ | Mayor $m_b$ → menor desplazamiento (a $h_d$ fijo) | Revisar massbody vs rhopbody |
| Orden de magnitud | $\Delta_{CM} \in [0, \sim 15]$ m | Revisar canal 30 m y tiempo máximo |
| Completitud | Sin NaN ni Inf en los 20 casos | Revisar parsing de CSV |
| $v_{\text{SPH}} < v_{\text{Ritter}}$ | Velocidad SPH menor que analítica | Revisar viscosidad y CFL |
| Curvas temporales suaves | Sin oscilaciones de alta frecuencia | Revisar estabilidad numérica |

---

## 3.12 Análisis de Sensibilidad Global

### 3.12.1 Propagación de Incertidumbre vía Monte Carlo

Una vez entrenado el GP final con todas las observaciones ($\sim$25-30 puntos), se propagan las incertidumbres de los parámetros de entrada mediante muestreo Monte Carlo. Se generan $N = 10\,000$ muestras uniformes sobre $\Omega$ y se evalúan sobre el GP surrogate, obteniendo en segundos una distribución empírica de $\Delta_{CM}$ que incluye la incertidumbre epistémica del modelo.

### 3.12.2 Índices de Sobol

La contribución relativa de cada parámetro de entrada a la variabilidad de la respuesta se cuantifica mediante los índices de Sobol (Sobol', 2001; Saltelli, 2002). El índice de primer orden $S_i$ mide la fracción de la varianza total explicada por el parámetro $i$:

$$S_i = \frac{\text{Var}_{\mathbf{x}_i}\left[\mathbb{E}_{\mathbf{x}_{\sim i}}(f \mid \mathbf{x}_i)\right]}{\text{Var}(f)}$$

mientras que el índice de efecto total $S_{T_i}$ captura la contribución del parámetro $i$ incluyendo todas sus interacciones:

$$S_{T_i} = 1 - \frac{\text{Var}_{\mathbf{x}_{\sim i}}\left[\mathbb{E}_{\mathbf{x}_i}(f \mid \mathbf{x}_{\sim i})\right]}{\text{Var}(f)}$$

Los índices se estiman evaluando el GP surrogate con los esquemas de muestreo de Saltelli (2002), lo cual es computacionalmente viable gracias a la velocidad de evaluación del GP. Este enfoque sigue el precedente de Salmanidou et al. (2017, 2020), quienes aplicaron GP + Monte Carlo + Sobol a simulaciones SPH de tsunami.

---

## 3.13 Figuras del Capítulo

| Figura | Archivo | Descripción |
|--------|---------|-------------|
| Fig. 3.1 | `fig01_desplazamiento_convergencia.png` | Convergencia del desplazamiento vs. dp |
| Fig. 3.2 | `fig02_fuerza_sph_convergencia.png` | Convergencia de la fuerza SPH vs. dp |
| Fig. 3.3 | `fig03_tasa_convergencia.png` | Tasa de cambio (δ%) por métrica |
| Fig. 3.4 | `fig04_fuerza_contacto_diagnostico.png` | Diagnóstico de no-convergencia de F_contacto |
| Fig. 3.5 | `fig05_velocidad_rotacion.png` | Velocidad y rotación del bloque |
| Fig. 3.6 | `fig06_costo_computacional.png` | Costo computacional vs. resolución |
| Fig. 3.7 | `fig07_tabla_resumen.png` | Tabla resumen de convergencia |
| Fig. 3.8 | `fig08_historia_completa.png` | Historia temporal completa (7 dp) |
| Fig. 3.9 | `fig09_veredicto.png` | Veredicto de convergencia |

Todas las figuras se encuentran en `data/figuras_7dp_es/pngs/` (versión en español).
