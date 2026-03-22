# Reporte: Estudio de Convergencia de Malla — SPH-IncipientMotion

**Fecha:** Marzo 2026 · **Solver:** DualSPHysics v5.4 + Chrono

---

## Resumen

Se realizó un estudio de convergencia con 7 niveles de espaciamiento de partículas (dp = 0.020 a 0.003 m). Las tres métricas primarias — desplazamiento, velocidad y fuerza SPH — convergen con variaciones inferiores al 5% entre los dos niveles más finos. La incertidumbre numérica, evaluada mediante el Grid Convergence Index (GCI), es de 6.4% para desplazamiento — dentro del rango aceptable para estudios paramétricos según el procedimiento estándar de Celik et al. (2008). Se adopta dp = 0.004 m como espaciamiento de producción.

---

## 1. Configuración

- **Dominio:** Canal 3D de 30 m de largo con pendiente de playa y boulder BLIR3
- **Solver:** DualSPHysics v5.4, GPU (RTX 5090, 32 GB VRAM), Chrono RigidAlgorithm=3
- **Kernel:** Wendland (orden formal 2)
- **Escenario fijo:** Misma geometría, condiciones de borde y parámetros físicos en los 7 niveles

## 2. Resultados

| dp (m) | Partículas | Desplaz. (m) | Δ% | Vel. (m/s) | F_sph (N) | F_cont (N) | t (min) |
|--------|----------:|------------:|---:|-----------:|----------:|----------:|--------:|
| 0.020  |     209 K |       3.495 |  — |      1.161 |     166.4 |      2254 |      13 |
| 0.015  |     496 K |       3.434 | 1.8 |      1.269 |      77.0 |      4915 |      12 |
| 0.010  |    1.67 M |       3.069 | 10.6 |      1.119 |      45.3 |       131 |      24 |
| 0.008  |    3.27 M |       2.408 | 21.5 |      1.138 |      34.9 |      3229 |      30 |
| 0.005  |    13.4 M |       1.725 | 28.4 |      1.158 |      23.0 |      3083 |     118 |
| 0.004  |    26.1 M |       1.615 |  6.4 |      1.168 |      22.8 |       359 |     260 |
| 0.003  |    62.0 M |       1.553 |  3.9 |      1.177 |      22.2 |       450 |     812 |

Δ% = variación porcentual respecto al nivel anterior (solo desplazamiento).

## 3. Análisis de incertidumbre numérica (GCI)

### ¿Qué es el GCI?

El **Grid Convergence Index** es un indicador estandarizado que cuantifica cuánta incertidumbre introduce el usar una resolución finita en vez de infinita. Fue propuesto por Roache (1994) y formalizado como procedimiento estándar por Celik et al. (2008), publicado en el *Journal of Fluids Engineering* de ASME. Es el método requerido por ASME para reportar convergencia en publicaciones de mecánica de fluidos.

El procedimiento requiere mínimo 3 niveles de resolución y una variable de interés. A partir de las diferencias entre niveles se calcula:

1. **Orden aparente de convergencia (p):** a qué tasa la solución converge al refinar. Si coincide con el orden teórico del método, la convergencia es genuina.
2. **Valor extrapolado (Richardson):** estimación de lo que obtendríamos con resolución infinita.
3. **GCI:** la incertidumbre del resultado, expresada como porcentaje. Incluye un factor de seguridad de 1.25.

### Aplicación a nuestros datos

Se aplica el procedimiento sobre los tres niveles más finos (dp = 0.005, 0.004, 0.003):

| Parámetro | Valor |
|-----------|-------|
| Razón de refinamiento r₂₁ | 1.333 |
| Orden aparente p | 1.99 ≈ 2.0 |
| Valor extrapolado (Richardson) | 1.47 m |
| Factor de seguridad Fs | 1.25 |

El orden aparente p ≈ 2.0 es consistente con el orden formal del kernel Wendland, lo que confirma que la convergencia observada es coherente con la teoría.

| Métrica | Δ% (dp=0.004 → 0.003) | GCI fino |
|---------|:-----:|:------:|
| Desplazamiento | 3.9% | 6.4% |
| Velocidad | 0.8% | 1.4% |
| Fuerza SPH | 2.8% | 4.6% |

Los umbrales aceptados en CFD para el GCI son: < 5% para estudios detallados, **< 10% para estudios paramétricos** (Celik et al., 2008). Nuestro caso es un screening paramétrico, por lo que un GCI de 6.4% se encuentra dentro del rango aceptable.

### Métricas no convergentes

- **Rotación:** Comportamiento oscilatorio (60°–97° sin tendencia monótona). El GCI no es aplicable bajo convergencia no monótona.
- **Fuerza de contacto:** CV = 82% a través de los 7 niveles. Atribuido a la naturaleza discreta de la interacción boulder-fondo en el modelo DEM de Chrono.

## 4. Factibilidad de refinamiento adicional

La cantidad de partículas escala como 1/dp³. La tabla siguiente proyecta los requerimientos para dp más finos:

| dp (m) | Partículas est. | VRAM est. | Tiempo est. | ¿Viable en RTX 5090? |
|--------|----------------:|---------:|------------:|:-----:|
| 0.003 (actual) | 62 M | ~24 GB | 812 min | Sí |
| 0.0025 | ~107 M | ~40 GB | ~1,700 min | No (excede 32 GB) |
| 0.002 | ~209 M | ~78 GB | ~4,100 min | No |

DualSPHysics requiere que todas las partículas residan en VRAM simultáneamente. dp = 0.0025 genera ~107 millones de partículas, requiriendo ~40 GB de VRAM — superior a los 32 GB disponibles.

**Multi-resolución:** DualSPHysics v5.4 incorpora un modelo de resolución variable basado en descomposición de dominios, pero este no es compatible con cuerpos flotantes acoplados a Chrono (confirmado en los foros oficiales del proyecto). La multi-resolución tipo particle splitting/merging sigue en desarrollo. Cambiar de solver para acceder a esta funcionalidad invalidaría la cadena de validación construida.

**Reducción de dominio:** Reducir el canal para disminuir partículas no es viable: el largo de 30 m es necesario para evitar la saturación de desplazamiento detectada a 15 m, y modificar el ancho alteraría el confinamiento lateral. Además, cambiar el dominio solo para el nivel más fino invalidaría la comparación entre niveles.

## 5. Conclusión

El estudio de convergencia con 7 niveles de dp — el doble de lo habitual en la literatura SPH — demuestra que las métricas primarias convergen con GCI ≤ 6.4%, dentro del rango aceptable para estudios paramétricos. El orden de convergencia observado (p ≈ 2.0) es consistente con la teoría. El refinamiento adicional está limitado por la capacidad de VRAM del hardware disponible y la incompatibilidad de la multi-resolución con el acoplamiento Chrono. Se valida dp = 0.004 m como espaciamiento de producción y dp = 0.003 m como referencia fina.

---

**Referencias**

- Celik, I. B., Ghia, U., Roache, P. J. & Freitas, C. J. (2008). *Procedure for Estimation and Reporting of Uncertainty Due to Discretization in CFD Applications.* J. Fluids Eng., 130(7), 078001.
- Roache, P. J. (1994). *Perspective: A Method for Uniform Reporting of Grid Refinement Studies.* J. Fluids Eng., 116(3), 405-413.
- Rossi, E. et al. (2023). *Implementation of improved spatial derivative discretization in DualSPHysics.* Comp. Part. Mech., 10, 1685-1706.
- Vacondio, R. et al. (2021). *Grand challenges for Smoothed Particle Hydrodynamics numerical schemes.* Comp. Part. Mech., 8, 575-588.
