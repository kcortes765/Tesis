# Plan de verificación y robustecimiento preproducción sin experimento propio

Fecha: 2026-05-08  
Proyecto: Tesis SPH-DualSPHysics-Chrono, movimiento incipiente de bloque costero  
Estado: plan técnico previo a campaña productiva grande

## 1. Decisión ejecutiva

Sí: antes de expandir la campaña productiva conviene hacer las tres piezas de verificación posibles sin experimento propio:

1. **Benchmark hidráulico SPH/DualSPHysics**: comprobar que la instalación, el solver y el postproceso reproducen un caso hidráulico conocido.
2. **Chequeo de contacto bloque-suelo-Chrono**: comprobar que el bloque no se mueve por mala condición inicial, apoyo, penetración, fricción o relajación numérica.
3. **Comparación analítica preliminar**: comprobar que las tendencias observadas tienen coherencia física con balances de fuerzas y momentos de bajo orden.

Esto no reemplaza un experimento físico propio. Lo que sí logra es construir una defensa metodológica fuerte:

- el solver hidráulico se contrasta contra un benchmark externo;
- el contacto del bloque se controla con un caso nulo/sanity;
- la frontera estable/fallo no queda como una clasificación puramente numérica;
- la campaña con `dp=0.003` se vuelve más defendible;
- el subconjunto fino `dp=0.002` queda reservado para verificación estratégica, no para rehacer toda la tesis.

La formulación recomendada es:

> Se realizó una verificación de solución por sensibilidad de resolución para escoger `dp=0.003` como resolución operativa, seguida de verificaciones independientes del pipeline hidráulico, del contacto bloque-suelo y de la coherencia física mediante criterios analíticos. La validación experimental completa queda fuera del alcance por no existir un experimento propio equivalente, pero se reduce el riesgo numérico mediante benchmarks, chequeos de contacto, comparación analítica, análisis de incertidumbre y controles finos a `dp=0.002`.

## 2. Qué valida cada pieza y qué no valida

| Pieza | Qué valida | Qué no valida |
|---|---|---|
| Benchmark hidráulico | Instalación, configuración DualSPHysics, gauges, postproceso hidráulico, escalas de altura/velocidad/fuerza en un caso conocido. | No valida el bloque irregular ni el contacto Chrono específico de la tesis. |
| Contact sanity | Condición inicial del bloque, apoyo sobre la playa, fricción, ausencia de desplazamiento espurio antes del impacto. | No valida la respuesta frente a flujo extremo. |
| Comparación analítica | Coherencia de orden de magnitud: si mayor velocidad/altura, mayor fricción o mayor masa producen tendencias físicas razonables. | No predice exactamente el desplazamiento ni reemplaza SPH-Chrono. |
| `dp=0.002` subset | Incertidumbre de resolución en casos representativos y frontera. | No convierte toda la campaña en convergencia asintótica fuerte. |
| Surrogate + UQ | Interpolación, incertidumbre predictiva y fragilidad dentro del dominio simulado. | No reemplaza simulaciones fuera del dominio ni valida física no simulada. |

## 3. Marco metodológico correcto

Hay que separar cuatro conceptos:

### 3.1 Verificación de solución por resolución

Esto es lo que ya se empezó con `dp`: se mira cómo cambian variables continuas al refinar la discretización SPH.

Variables adecuadas:

- desplazamiento del bloque en el tiempo;
- velocidad del bloque;
- altura/cota de agua en gauges;
- velocidad de flujo en gauges;
- rotación, pero solo como variable observada.

En CFD, la extrapolación de Richardson y GCI funcionan mejor cuando hay refinamiento sistemático y comportamiento relativamente suave. La guía de NASA sobre convergencia espacial destaca que se busca ver si la solución se acerca a un valor asintótico al refinar, pero también advierte que este límite numérico no equivale necesariamente a la solución física real. En este caso, por superficie libre, contacto, cuerpo irregular y umbral estable/fallo, no conviene vender una convergencia fuerte de clase.

Conclusión correcta para la tesis:

> `dp=0.003` se adopta como resolución operativa por similitud práctica de variables principales y costo computacional; la frontera estable/fallo se reporta condicionada por esa resolución.

### 3.2 Benchmark hidráulico

Esto responde una pregunta distinta:

> ¿Mi instalación de DualSPHysics y mi postproceso reproducen un caso hidráulico conocido?

DualSPHysics incluye casos oficiales de prueba, entre ellos dam-break 2D con datos experimentales y dam-break 3D impactando una estructura. La documentación oficial indica que el caso 01_DAMBREAK incluye reproducción de datos experimentales de Koshizuka y Oka para el caso 2D, además de velocidades, presiones y fuerzas en el caso 3D.

También existe el benchmark SPHERIC Test 02: un dam-break 3D con evolución de superficie libre y datos experimentales descargables. Este benchmark es útil porque es externo a tu caso y es reconocido dentro de la comunidad SPH.

### 3.3 Chequeo de contacto

Esto responde:

> ¿El bloque se mueve por el flujo o ya nace con un problema de contacto?

En tu tesis esto es crítico porque el problema depende de una frontera de movimiento incipiente. Un desplazamiento pequeño por apoyo imperfecto puede contaminar la decisión estable/fallo.

El sanity test no es una simulación productiva. Es un control de calidad:

- mismo bloque;
- misma playa;
- misma fricción/contacto;
- sin impacto hidráulico o con condición hidráulica nula/controlada;
- se mide si el bloque deriva, rota o penetra.

### 3.4 Comparación analítica

Esto responde:

> ¿Lo que SPH-Chrono predice tiene sentido frente a un balance físico simple?

La literatura de transporte de bloques usa ecuaciones de arrastre, sustentación, peso sumergido, fricción y momentos para estimar inicio de movimiento. Nandasena, Paris y Tanaka reevalúan ecuaciones hidrodinámicas para velocidades mínimas de transporte en modos como deslizamiento, rodadura y saltación. Bressan et al. muestran experimentalmente que el movimiento incipiente depende fuertemente de peso, geometría, orientación, velocidad y profundidad, y que los coeficientes de arrastre/sustentación usados en fórmulas simples pueden ser inadecuados sin calibración. Cox et al. advierten que las ecuaciones tipo Nott/Nandasena no deben usarse de forma acrítica para distinguir tormenta/tsunami o reconstruir alturas de ola.

Por eso la comparación analítica debe ser prudente:

- útil como referencia física;
- útil para explicar tendencias;
- útil para detectar resultados raros;
- no es validación exacta del bloque irregular.

## 4. Benchmark hidráulico SPH/DualSPHysics

### 4.1 Objetivo

Demostrar que la instalación local de DualSPHysics, los ejecutables, los gauges y el postproceso reproducen un caso hidráulico conocido antes de confiar en campañas costosas de tesis.

### 4.2 Benchmark recomendado

Se propone una estrategia en dos niveles.

#### Nivel A0: testcase oficial DualSPHysics

Usar primero un ejemplo oficial liviano:

- `01_DAMBREAK` 2D con datos experimentales de posición de frente/altura de agua;
- o `01_DAMBREAK` 3D con obstáculo para velocidades, presiones y fuerzas.

Ventaja:

- ya viene en la distribución;
- permite detectar problemas de instalación/postproceso rápido;
- no requiere diseñar un caso nuevo desde cero.

Limitación:

- valida el flujo de trabajo de DualSPHysics, no necesariamente un benchmark externo completo preparado para publicación.

#### Nivel A1: SPHERIC Test 02

Usar como benchmark principal si los datos se pueden descargar y postprocesar con tiempo razonable:

- dam-break 3D;
- evolución de superficie libre;
- datos experimentales descargables;
- usado en publicaciones SPH.

Ventaja:

- externo a tu pipeline;
- más defendible en tesis/paper;
- permite comparar curvas temporales de altura/cota de agua y evolución de superficie libre.

Limitación:

- puede requerir más trabajo de adaptación;
- no valida Chrono/contacto del bloque.

### 4.3 Métricas a calcular

Métricas mínimas:

- curva temporal de altura de agua en probes/gauges;
- posición del frente de agua si está disponible;
- tiempo de llegada del frente;
- máximo de altura/cota;
- error relativo del máximo;
- RMSE temporal normalizado;
- desfase temporal del máximo;
- comparación visual de forma temporal.

Si el caso 3D con obstáculo está disponible:

- fuerza horizontal sobre estructura;
- presión en puntos correctos;
- velocidad en puntos internos;
- curva de fuerza vs tiempo.

### 4.4 Criterios de aceptación

No imponer un 5% universal. Ese 5% es el umbral de movimiento del bloque, no una regla general de convergencia o validación hidráulica.

Criterios recomendados:

- forma temporal comparable;
- tiempo de llegada razonable;
- máximos dentro de un rango defendible para SPH libre-superficie;
- sin errores de unidades, signo, gauge o postproceso;
- si hay datos experimentales claros, reportar error relativo y RMSE, no ocultarlo.

Rangos orientativos:

- error de máximo hidráulico menor a 10-15%: razonable para benchmark libre-superficie sin calibración fina;
- error menor a 5-10%: muy bueno si el caso y los datos son limpios;
- error mayor a 20%: revisar configuración, resolución, viscosidad, gauges o postproceso.

Estos rangos no son una ley. Deben compararse con lo reportado por el benchmark y con la resolución usada.

### 4.5 Entregables

Carpeta sugerida:

```text
data/benchmarks/hydraulic_YYYYMMDD/
```

Archivos:

```text
benchmark_hydraulic_summary.csv
benchmark_hydraulic_metrics.json
benchmark_hydraulic_report.md
figures/
  water_height_timeseries.png
  front_position_timeseries.png
  force_if_available.png
  error_summary.png
```

Documento:

```text
docs/BENCHMARK_HIDRAULICO_DUALSPHYSICS_YYYYMMDD.md
```

## 5. Chequeo de contacto bloque-suelo-Chrono

### 5.1 Objetivo

Verificar que el bloque no se mueve de forma espuria por:

- apoyo mal definido;
- penetración inicial;
- falta de equilibrio gravitacional;
- fricción mal aplicada;
- error en masa/inercia;
- ruido de contacto Chrono;
- referencia temporal mal elegida.

### 5.2 Casos mínimos

#### S00: bloque en playa sin impacto hidráulico

Mismo bloque, misma playa, misma pendiente, misma fricción base, mismo `dp=0.003`, pero sin dam-break efectivo o con condición hidráulica nula/controlada.

Objetivo:

- medir desplazamiento y rotación por contacto puro.

#### S01: bloque con agua estática/controlada

Si el solver requiere fluido para mantener el caso comparable, usar agua sin impacto sobre el bloque o con altura insuficiente para moverlo.

Objetivo:

- descartar que presión hidrostática o contacto fluido mínimo generen deriva no física.

#### S02: repetición corta con fricción baja y alta

Opcional:

- `mu` bajo;
- `mu` alto;
- sin impacto.

Objetivo:

- verificar que la fricción no se está aplicando con signo, escala o cuerpo equivocado.

### 5.3 Métricas

Medir:

- `D_max` desde `reference_time_s=0.5`;
- `D_max/d_eq`;
- desplazamiento final;
- rotación acumulada;
- velocidad máxima del bloque;
- fuerza de contacto máxima;
- fuerza SPH máxima si hay fluido;
- penetración/contacto anómalo si el output lo permite;
- drift antes de llegada del flujo.

### 5.4 Criterios de aceptación

Condición mínima:

```text
D_max / d_eq << 0.05
```

Recomendación práctica:

- ideal: `D_max/d_eq < 0.005` (menos de 0.5% de `d_eq`);
- aceptable: `D_max/d_eq < 0.01` si se puede justificar como settling/contacto menor;
- no aceptable: cercano al 5% o rotación sostenida sin flujo.

Si S00 falla, no lanzar campaña productiva. Primero revisar:

- apoyo exacto;
- `FtPause`;
- posición inicial;
- normal de playa;
- masa/inercia;
- geometría de colisión;
- material Chrono;
- fricción;
- referencia temporal.

### 5.5 Entregables

Carpeta:

```text
data/sanity/contact_YYYYMMDD/
```

Archivos:

```text
contact_sanity_summary.csv
contact_sanity_report.md
figures/
  displacement_contact_timeseries.png
  rotation_contact_timeseries.png
  contact_force_timeseries.png
```

Documento:

```text
docs/CHEQUEO_CONTACTO_CHRONO_YYYYMMDD.md
```

## 6. Comparación analítica preliminar

### 6.1 Objetivo

Construir un modelo físico de bajo orden para interpretar los resultados SPH-Chrono.

No se busca que el modelo analítico prediga el desplazamiento exacto. Se busca que ordene tendencias:

- mayor intensidad hidráulica debería aumentar movilidad;
- mayor fricción debería reducir movilidad;
- mayor masa/densidad debería reducir movilidad;
- pendiente y orientación pueden desplazar la frontera;
- casos con mayor índice de movilidad deberían tener mayor `D_max/d_eq`.

### 6.2 Modelo de deslizamiento

Definir una fuerza motriz aproximada:

```text
F_drive(t) = F_D(t) + W' * sin(beta)
```

Definir resistencia:

```text
F_resist(t) = mu * (W' * cos(beta) - F_L(t))
```

donde:

```text
F_D(t) = 0.5 * rho_w * C_D * A_D * U(t)^2
F_L(t) = 0.5 * rho_w * C_L * A_L * U(t)^2
W' = peso efectivo o peso sumergido aproximado
beta = ángulo de la pendiente
mu = fricción bloque-suelo
```

Índice de movilidad:

```text
Psi(t) = F_drive(t) / F_resist(t)
```

Lectura:

- `Psi < 1`: resistencia mayor que forzante;
- `Psi > 1`: condición favorable al deslizamiento;
- `Psi_max`: intensidad máxima instantánea;
- `I_Psi = integral(max(0, Psi(t)-1) dt)`: duración/intensidad excedente.

### 6.3 Modelo de rotación/vuelco

Como diagnóstico:

```text
R_M(t) = M_hidro(t) / M_resistente(t)
```

No usarlo como criterio primario porque la tesis clasifica por desplazamiento.

Lectura:

- un caso puede rotar sin cruzar el umbral de desplazamiento;
- eso no invalida la clase bajo `displacement_only`;
- sí puede explicar rocking, ajuste de apoyo o sensibilidad de contacto.

### 6.4 Incertidumbres obligatorias

El modelo analítico debe correrse con bandas, no con un único valor:

- `C_D` variable;
- `C_L` variable;
- área proyectada variable;
- sumergencia efectiva variable;
- punto de aplicación de fuerza variable;
- coeficiente de fricción como input;
- velocidad local tomada de gauges, no del campo completo.

No presentar:

> El criterio analítico valida la simulación.

Presentar:

> El criterio analítico entrega una referencia de escala y tendencia; las diferencias esperadas se explican por forma irregular, flujo transitorio, submergencia parcial, turbulencia, contacto friccional y coeficientes no calibrados.

### 6.5 Datos a usar

Para piloto/batch2/productivo:

- `max_displacement_m`;
- `disp_over_deq`;
- `criterion_class`;
- `max_rotation_deg`;
- `max_velocity_mps`;
- `h_max_gauge`;
- `u_max_gauge`;
- curvas temporales de gauges cercanos al bloque;
- masa, volumen, `d_eq`, bbox, pendiente, `mu`;
- tiempo de llegada del flujo;
- contacto/fuerzas si están limpias.

Si localmente falta batch2, usar el export disponible y luego repetir tras sincronizar WS.

### 6.6 Figuras recomendadas

Figuras mínimas:

1. `Psi_max` vs `D_max/d_eq`.
2. `I_Psi` vs `D_max/d_eq`.
3. Banda analítica estable/posible/favorable vs puntos SPH.
4. Comparación por clase: estable/fallo según SPH vs rango de `Psi`.
5. Sensibilidad tornado de `C_D`, `C_L`, área y sumergencia.

### 6.7 Entregables

Carpeta:

```text
data/analytic_comparison/YYYYMMDD/
```

Archivos:

```text
analytic_mobility_summary.csv
analytic_parameter_ranges.json
analytic_comparison_report.md
figures/
  psi_vs_displacement.png
  impulse_psi_vs_displacement.png
  analytic_band_vs_sph_class.png
  coefficient_sensitivity.png
```

Documento:

```text
docs/COMPARACION_ANALITICA_PRELIMINAR_YYYYMMDD.md
```

## 7. Subconjunto fino `dp=0.002`

### 7.1 Objetivo

Usar `dp=0.002` como verificación fina estratégica, no como campaña principal.

Esto mejora mucho la defensibilidad porque permite decir:

> La campaña principal se ejecutó a `dp=0.003` por costo y trazabilidad, pero se usó un subconjunto fino `dp=0.002` para cuantificar la sensibilidad de resolución en puntos representativos y cercanos a la frontera.

### 7.2 Cuándo correrlo

No conviene lanzarlo antes de tener:

- benchmark hidráulico revisado;
- sanity de contacto OK;
- primer surrogate/active learning con frontera aproximada;
- candidatos marginales elegidos.

### 7.3 Cuántos casos

Recomendación:

- mínimo defendible: 4-6 casos;
- ideal para paper: 8-12 casos;
- más de 12 solo si hay una razón científica clara.

Distribución:

| Tipo | Casos | Motivo |
|---|---:|---|
| Estables robustos | 1-2 | Confirmar que no todo cambia al refinar. |
| Fallos robustos | 1-2 | Confirmar que fallos fuertes se mantienen. |
| Cercanos a frontera | 4-6 | Cuantificar sensibilidad de clase y margen. |
| Hidráulica fuerte | 1 | Ver si el refinamiento cambia casos muy energéticos. |
| Repetición | 1 | Separar ruido numérico/procedural de resolución. |

### 7.4 Métricas

Para cada par `dp=0.003` / `dp=0.002`:

```text
delta_D = D_003 - D_002
delta_g = g_003 - g_002
delta_class = class_003 != class_002
delta_hmax
delta_umax
delta_rotation
```

Usar el resultado para definir zona gris:

```text
epsilon_g = max(0.005, estadística robusta de |delta_g|)
```

### 7.5 Cómo reportarlo

No decir:

> `dp=0.002` prueba que `dp=0.003` converge perfectamente.

Decir:

> `dp=0.002` se usa como control fino de sensibilidad. Los cambios de clase cerca del umbral se interpretan como incertidumbre de resolución de la frontera, no como falla metodológica.

## 8. Active learning, surrogate e incertidumbre

### 8.1 Por qué active learning es razonable

La alternativa bruta en 3 variables sería:

```text
5 niveles por variable  -> 125 casos
6 niveles por variable  -> 216 casos
8 niveles por variable  -> 512 casos
```

Con simulaciones SPH de varias horas, eso no es eficiente.

Un esquema razonable:

```text
piloto / anclas / direccionales: 12-18 casos
active learning: 18-30 casos
validación interna: 4-8 casos
dp=0.002 subset: 6-12 casos
```

Total:

```text
~35-55 casos dp=0.003
+ 6-12 casos dp=0.002
```

Esto es una reducción aproximada de 60-80% respecto de una grilla de 125-216 casos, concentrando simulaciones donde importan: cerca del estado límite.

### 8.2 Variable objetivo

Usar margen:

```text
g = 0.05 - D_max / d_eq
```

Lectura:

- `g > 0`: estable;
- `g < 0`: fallo;
- `g = 0`: frontera de movimiento;
- `|g|` pequeño: zona gris o frontera.

Esto calza con AK-MCS y confiabilidad: la literatura de active learning con Kriging/GP se enfoca en reducir llamadas al modelo caro cerca del estado límite `G(x)=0`.

### 8.3 Modelo

Modelo principal:

- Gaussian Process Regression;
- kernel Matérn 3/2 o 5/2;
- WhiteKernel/nugget pequeño;
- entradas normalizadas;
- salida `g` estandarizada.

La documentación de scikit-learn permite obtener media y desviación estándar predictiva (`return_std=True`), lo que habilita mapas de incertidumbre y selección de puntos activos.

### 8.4 Sensibilidad

Una vez entrenado el surrogate:

- Sobol si el modelo está estable y se quieren índices globales;
- Morris si se quiere screening robusto;
- permutation importance como chequeo;
- SHAP solo si se usan árboles como modelo challenger.

SALib soporta métodos como Sobol y Morris, lo que es suficiente para un análisis de sensibilidad sobre surrogate.

### 8.5 Fragilidad

Monte Carlo se hace sobre el surrogate, no con SPH directo:

```text
H_star, mu, m_star -> GP(g) -> P(g < 0)
```

Reportar:

- curvas `P_f(H*)`;
- mapas `P_f(H*, mu)` para valores de masa;
- banda de incertidumbre;
- sensibilidad de `P_f` a supuestos de distribución.

## 9. Orden operativo recomendado

### Fase 0: sincronización y auditoría local

Antes de correr nada:

- no mezclar PC local y WS;
- sincronizar solo si el árbol local está protegido;
- confirmar qué export de batch2 existe;
- no subir binarios pesados.

### Fase 1: benchmark hidráulico

1. Correr testcase oficial DualSPHysics liviano.
2. Generar curvas de referencia vs simulación.
3. Si sale bien, correr/adaptar SPHERIC Test 02.
4. Guardar informe.

### Fase 2: sanity de contacto

1. S00 sin impacto hidráulico.
2. S01 agua quieta/controlada si aplica.
3. Validar drift, rotación y fuerzas.
4. Si falla, detener producción.

### Fase 3: comparación analítica piloto/batch2

1. Consolidar piloto/batch2.
2. Extraer `h(t)` y `U(t)` cerca del bloque.
3. Calcular `Psi(t)`, `Psi_max`, `I_Psi`.
4. Graficar contra `D_max/d_eq`.
5. Reportar incertidumbre de coeficientes.

### Fase 4: campaña productiva con active learning

1. Definir matriz inicial limpia.
2. Correr lote `dp=0.003`.
3. Entrenar GP sobre `g`.
4. Seleccionar puntos por incertidumbre/frontera.
5. Validar con casos holdout.

### Fase 5: subconjunto fino `dp=0.002`

1. Elegir puntos a partir de la frontera aprendida.
2. Correr 6-12 casos.
3. Cuantificar incertidumbre de resolución.
4. Ajustar zona gris.

## 10. Qué no hacer

No hacer ahora:

- no correr grilla factorial grande;
- no usar `dp=0.002` como campaña principal;
- no decir que la convergencia asintótica está cerrada;
- no usar rotación como criterio de clase;
- no usar gauges como evidencia primaria de movimiento;
- no usar criterio analítico como validación exacta;
- no mezclar benchmark hidráulico con validación del bloque;
- no correr producción antes de sanity de contacto si hay dudas del apoyo.

## 11. Redacción sugerida para tesis

Texto corto:

> La verificación del modelo se estructuró en tres niveles. Primero, se evaluó la sensibilidad de resolución SPH para seleccionar una resolución operativa (`dp=0.003`) capaz de reproducir de manera práctica las variables principales del problema con un costo computacional viable. Segundo, se propuso un benchmark hidráulico independiente para verificar que la instalación de DualSPHysics y el postproceso reproducen un caso de superficie libre documentado. Tercero, se incorporó un chequeo de contacto bloque-suelo y una comparación analítica de bajo orden para controlar que la respuesta del bloque no esté dominada por artefactos de apoyo o por tendencias físicamente incoherentes. Debido a la naturaleza umbral del movimiento incipiente, la frontera estable/fallo se reporta condicionada por la resolución y se acompaña de una zona de incertidumbre.

Texto para defensa:

> No estoy diciendo que `dp=0.003` sea la solución exacta de la física real. Estoy diciendo que, para este modelo SPH-Chrono, `dp=0.003` es la resolución operativa defendible después de mirar variables temporales, costo, sensibilidad de frontera y controles adicionales. La campaña productiva se interpreta dentro de esa resolución, y `dp=0.002` se reserva como verificación fina de puntos estratégicos.

## 12. Fuentes consultadas

- DualSPHysics Wiki, testcases oficiales, incluyendo dam-break 2D/3D, gauges, velocidades, presiones y fuerzas: https://github.com/DualSPHysics/DualSPHysics/wiki/7.-Testcases
- SPHERIC Test 02, dam-break 3D con datos experimentales descargables: https://www.spheric-sph.org/tests/test-02
- NASA WIND validation tutorial, convergencia espacial, Richardson/GCI y advertencias sobre interpretación de convergencia: https://www.grc.nasa.gov/www/wind/valid/tutorial/spatconv.html
- Martínez-Estévez et al. (2023), DualSPHysics-Chrono como acoplamiento bidireccional SPH/multicuerpo/contacto: https://www.sciencedirect.com/science/article/pii/S0010465522003009
- Nandasena, Paris y Tanaka (2011), ecuaciones hidrodinámicas revisadas para inicio de transporte de bloques: https://www.sciencedirect.com/science/article/abs/pii/S0025322711000259
- Bressan et al. (2018), experimento de movimiento incipiente de bloques por flujos costeros de alta energía: https://pearl.plymouth.ac.uk/secam-research/1746/
- Cox et al. (2020), crítica a usar ecuaciones hidrodinámicas simples como discriminador fuerte tormenta/tsunami: https://www.frontiersin.org/journals/marine-science/articles/10.3389/fmars.2020.00004/full
- Iwai y Goto (2021), datos de bloques movidos/no movidos por tsunami y relevancia de condiciones locales: https://www.nature.com/articles/s41598-021-92917-2
- Echard, Gayton y Lemaire (2011), AK-MCS, active learning con Kriging y Monte Carlo para reducir llamadas a modelos caros: https://www.sciencedirect.com/science/article/abs/pii/S0167473011000038
- scikit-learn GaussianProcessRegressor, predicción con incertidumbre (`return_std=True`): https://scikit-learn.org/stable/modules/generated/sklearn.gaussian_process.GaussianProcessRegressor.html
- SALib, métodos de sensibilidad global como Sobol y Morris: https://salib.readthedocs.io/
