# Informe: Factibilidad de Refinamiento Adicional (dp < 0.003)

**Proyecto:** SPH-IncipientMotion · **Solver:** DualSPHysics v5.4 + Chrono · **Marzo 2026**

---

## 1. Datos del estudio de convergencia

Se evaluaron 7 niveles de dp con geometría, condiciones de borde y parámetros físicos idénticos:

| dp (m) | Partículas | Desplaz. (m) | Δ% | Vel. (m/s) | F_sph (N) | F_cont (N) | t (min) |
|--------|----------:|------------:|---:|-----------:|----------:|----------:|--------:|
| 0.020  |     209 K |       3.495 |  — |      1.161 |     166.4 |      2254 |      13 |
| 0.015  |     496 K |       3.434 | 1.8 |      1.269 |      77.0 |      4915 |      12 |
| 0.010  |    1.67 M |       3.069 | 10.6 |      1.119 |      45.3 |       131 |      24 |
| 0.008  |    3.27 M |       2.408 | 21.5 |      1.138 |      34.9 |      3229 |      30 |
| 0.005  |    13.4 M |       1.725 | 28.4 |      1.158 |      23.0 |      3083 |     118 |
| 0.004  |    26.1 M |       1.615 |  6.4 |      1.168 |      22.8 |       359 |     260 |
| 0.003  |    62.0 M |       1.553 |  3.9 |      1.177 |      22.2 |       450 |     812 |

## 2. Análisis GCI

El Grid Convergence Index (Roache, 1994; Celik et al., 2008) es un indicador estandarizado por ASME que cuantifica cuánta incertidumbre introduce el uso de una resolución finita en vez de infinita. El procedimiento requiere mínimo 3 niveles de resolución y calcula: (1) el orden aparente de convergencia, (2) el valor extrapolado a resolución infinita mediante Richardson extrapolation, y (3) el GCI propiamente tal, que expresa la incertidumbre como porcentaje incluyendo un factor de seguridad de 1.25.

Los umbrales aceptados son: GCI < 5% para estudios detallados, **GCI < 10% para estudios paramétricos** (Celik et al., 2008).

Aplicado sobre los tres niveles más finos (dp = 0.005, 0.004, 0.003):

- **Orden aparente:** p = 1.99 ≈ 2.0, consistente con el orden formal del kernel Wendland (Rossi et al., 2023). Esto confirma que la convergencia observada es coherente con la teoría del método.
- **Valor extrapolado (Richardson):** 1.47 m — estimación del desplazamiento a resolución infinita.

| Métrica | Δ% (dp=0.004 → 0.003) | GCI fino |
|---------|:-----:|:------:|
| Desplazamiento | 3.9% | 6.4% |
| Velocidad | 0.8% | 1.4% |
| Fuerza SPH | 2.8% | 4.6% |

Las tres métricas primarias varían menos de 5% entre los dos niveles más finos, y los tres GCI están dentro del rango aceptable (< 10%).

En el caso de referencia de la convergencia, dp=0.003 da 1.55 m de desplazamiento, a 5.4% del valor extrapolado. Bajar a dp=0.0025, si fuera posible, mejoraría ~3 cm — un orden de magnitud menor que las variaciones esperadas entre casos del estudio paramétrico, donde las diferencias en desplazamiento son del orden de metros.

**Rotación** presenta convergencia oscilatoria (60°–97°), por lo que el GCI no es aplicable. **Fuerza de contacto** tiene CV = 82% y no converge a ninguna resolución, consistente con la naturaleza discreta de la interacción boulder-fondo en Chrono/DEM.

## 3. Límite de hardware

DualSPHysics requiere que todas las partículas residan en VRAM simultáneamente. Las partículas escalan como 1/dp³:

| dp (m) | Partículas | VRAM est. | Tiempo est. | RTX 5090 (32 GB) |
|--------|----------:|---------:|------------:|:---------:|
| 0.003  |      62 M |   ~24 GB |     812 min | Viable |
| 0.0025 |    ~107 M |   ~40 GB |  ~1,700 min | No cabe |
| 0.002  |    ~209 M |   ~78 GB |  ~4,100 min | No cabe |

La estimación de VRAM (~350-400 bytes/partícula) es consistente con reportes empíricos en los foros oficiales de DualSPHysics, donde usuarios con Tesla A100 (80 GB) alcanzan el límite a ~180M partículas.

## 4. Multi-resolución

DualSPHysics v5.4 incluye un modelo de resolución variable por descomposición de dominios, pero este **no es compatible con floating bodies acoplados a Chrono** (confirmado en foros oficiales del proyecto). La técnica de particle splitting/merging permanece en desarrollo. No existe versión release ni beta que resuelva esta limitación.

Cambiar de solver (SPHinXsys u otro) para acceder a multi-resolución invalidaría la cadena de validación existente. Vacondio et al. (2021) identifican la multi-resolución como uno de los "grand challenges" abiertos de SPH.

## 5. Alternativas de reducción de dominio

- **Reducir largo:** El canal se extendió de 15 a 30 m para corregir la saturación de desplazamiento a 6.4 m. Acortarlo reintroduce el problema.
- **Reducir ancho:** Modifica el confinamiento lateral y altera la interacción ola-paredes.
- **En ambos casos:** Los 7 niveles existentes usan el mismo dominio. Si el nivel más fino usa un dominio distinto, la comparación entre niveles no es válida. Para mantener consistencia, habría que re-correr toda la serie con el nuevo dominio.

## 6. Conclusión

La convergencia está demostrada con 7 niveles de dp (el doble de lo habitual en la literatura SPH), GCI ≤ 6.4%, y orden de convergencia consistente con la teoría. El refinamiento adicional está impedido por la capacidad de VRAM y la incompatibilidad de la multi-resolución con Chrono. Las alternativas de reducción de dominio comprometen la validez física o la consistencia del estudio. Se valida dp = 0.004 m como producción y dp = 0.003 m como referencia fina.

---

## Referencias

- Celik, I. B., Ghia, U., Roache, P. J. & Freitas, C. J. (2008). Procedure for Estimation and Reporting of Uncertainty Due to Discretization in CFD Applications. *J. Fluids Eng.*, 130(7), 078001.
- Roache, P. J. (1994). Perspective: A Method for Uniform Reporting of Grid Refinement Studies. *J. Fluids Eng.*, 116(3), 405-413.
- Rossi, E. et al. (2023). Implementation of improved spatial derivative discretization in DualSPHysics: simulation and convergence study. *Comp. Part. Mech.*, 10, 1685-1706.
- Vacondio, R. et al. (2021). Grand challenges for Smoothed Particle Hydrodynamics numerical schemes. *Comp. Part. Mech.*, 8, 575-588.
