# Ecuaciones Empiricas de Transporte de Boulders y Sanity Checks para Validacion SPH

> Compilado: 2026-03-20
> Contexto: Tesis UCN — SPH-IncipientMotion (DualSPHysics v5.4 + Chrono)
> Boulder: BLIR3, ~150 kg, densidad ~2000 kg/m3
> Canal: 30 m, dam-break con dam_h en [0.3, 0.8] m, boulder_mass en [50, 300] kg

---

## 1. Ecuacion de Ritter (1892) — Velocidad Analitica de Dam-Break

### 1.1 Formulacion

Ritter (1892) derivo la solucion exacta para un dam-break instantaneo sobre lecho seco,
asumiendo fluido ideal (sin friccion) y shallow water equations (SWE):

**Velocidad del frente de onda (wave front):**

```
v_front = 2 * sqrt(g * h0)
```

donde:
- `g` = 9.81 m/s2 (aceleracion gravitacional)
- `h0` = altura inicial del reservorio (dam height)

**Celeridad de la onda:**

```
c0 = sqrt(g * h0)
```

**Perfil de velocidad y profundidad (para -c0*t < x < 2*c0*t):**

```
u(x,t) = (2/3) * (c0 + x/t)
h(x,t) = (1/(9*g)) * (2*c0 - x/t)^2
```

**Onda negativa** se propaga hacia atras a velocidad `-c0`.
**Onda positiva** (frente) avanza a velocidad `2*c0`.

### 1.2 Valores Numericos para Nuestro Rango de dam_h

| dam_h [m] | c0 = sqrt(g*h0) [m/s] | v_front = 2*c0 [m/s] | Nota                      |
|-----------|------------------------|----------------------|---------------------------|
| 0.30      | 1.716                  | 3.431                | Limite inferior del rango |
| 0.40      | 1.981                  | 3.962                |                           |
| 0.50      | 2.215                  | 4.429                | Caso medio                |
| 0.60      | 2.426                  | 4.852                |                           |
| 0.80      | 2.801                  | 5.601                | Limite superior del rango |

### 1.3 Implicaciones para Validacion SPH

- La velocidad del frente en DualSPHysics debe estar **en el orden** de estos valores.
- La solucion de Ritter **sobreestima** ligeramente la velocidad real porque ignora:
  - Friccion con el fondo
  - Viscosidad del fluido
  - Efectos 3D
- En SPH se espera velocidad del frente **ligeramente menor** que Ritter (5-15% menos).
- La velocidad maxima del fluido NO es la del frente; ocurre **detras del frente** y puede ser mayor localmente.

### 1.4 Referencia

- Ritter, A. (1892). Die Fortpflanzung der Wasserwellen. Zeitschrift des Vereines Deutscher Ingenieure, 36(33), 947-954.
- Castro-Orgaz, O. & Chanson, H. (2017). Ritter's dry-bed dam-break flows: positive and negative wave dynamics. Environmental Fluid Mechanics, 17(4), 665-694.
- Coastal Wiki: [Dam break flow](https://www.coastalwiki.org/wiki/Dam_break_flow)

---

## 2. Nandasena et al. (2011) — Velocidad Minima para Iniciar Movimiento

### 2.1 Contexto

Nandasena, Paris & Tanaka (2011) revisaron las ecuaciones de Nott (2003) y derivaron
formulas para la **velocidad minima de flujo (MFV)** necesaria para iniciar el transporte
de un boulder, distinguiendo cuatro modos de transporte:

1. **Sliding** (deslizamiento) — boulder no confinado
2. **Rolling/Overturning** (rodamiento/vuelco) — boulder no confinado
3. **Lifting/Saltation** (levantamiento) — boulder no confinado
4. **Lifting of joint-bounded** — boulder confinado en roca madre

### 2.2 Ecuaciones (Boulder Subaerial, No Confinado, Superficie Plana theta=0)

Las ecuaciones se derivan del balance de fuerzas sobre el boulder: drag + lift vs. peso + friccion.

**Parametros comunes:**

| Simbolo | Descripcion                    | Valor tipico        |
|---------|--------------------------------|---------------------|
| rho_s   | Densidad del boulder           | 2000 kg/m3 (BLIR3)  |
| rho_w   | Densidad del agua              | 1000-1025 kg/m3     |
| g       | Aceleracion gravitacional      | 9.81 m/s2           |
| a       | Eje mayor del boulder          | Variable            |
| b       | Eje intermedio del boulder     | Variable            |
| c       | Eje menor del boulder (altura) | Variable            |
| Cd      | Coeficiente de drag            | 1.95                |
| Cl      | Coeficiente de lift            | 0.178               |
| Cm      | Coeficiente de masa agregada   | 1.0                 |
| mu_s    | Coeficiente de friccion estatica | 0.6-0.7 (roca/roca) |
| theta   | Angulo de la pendiente         | 0 (plano)           |

**Nota sobre Cd:** Los valores en la literatura van de 1.0 a 2.5. El valor 1.95 es el mas
usado en aplicaciones de Nandasena y proviene de estudios previos (Einstein & El-Samni, 1949;
Nott, 2003). Algunos autores usan Cd = 1.5 (Imamura et al., 2008).

**Nota sobre Cl:** El valor 0.178 de Einstein & El-Samni (1949) es el estandar. Cox (2020)
argumenta que Cl puede ser mucho mayor (hasta 2.0), lo cual reduce drasticamente la velocidad
requerida.

#### 2.2.1 Modo Sliding (Deslizamiento)

Para theta = 0 (superficie plana):

```
u_sliding^2 = 2 * g * (rho_s/rho_w - 1) * c * mu_s / (Cd * (c/b) + mu_s * Cl)
```

Simplificacion: si el boulder es un cubo (a = b = c = L):

```
u_sliding^2 = 2 * g * (rho_s/rho_w - 1) * L * mu_s / (Cd + mu_s * Cl)
```

#### 2.2.2 Modo Rolling/Overturning (Vuelco)

```
u_rolling^2 = 2 * g * (rho_s/rho_w - 1) * c * (cos(theta) + (c/b)*sin(theta)) / (Cd * (c/b)^2 + Cl)
```

Para theta = 0:

```
u_rolling^2 = 2 * g * (rho_s/rho_w - 1) * c / (Cd * (c/b)^2 + Cl)
```

#### 2.2.3 Modo Lifting (Saltacion)

```
u_lifting^2 = 2 * g * (rho_s/rho_w - 1) * c * cos(theta) / Cl
```

Para theta = 0:

```
u_lifting^2 = 2 * g * (rho_s/rho_w - 1) * c / Cl
```

### 2.3 Aplicacion a Nuestro Boulder BLIR3

**Parametros del BLIR3:**
- Masa: ~150 kg
- Densidad: ~2000 kg/m3
- Volumen: ~0.075 m3
- Dimensiones aproximadas (a x b x c): ~0.60 x 0.45 x 0.28 m (estimado para bloque irregular)

**Calculo para sliding (rho_w = 1000, mu_s = 0.65, theta = 0):**

```
u_sliding^2 = 2 * 9.81 * (2000/1000 - 1) * 0.28 * 0.65 / (1.95 * (0.28/0.45) + 0.65 * 0.178)
            = 2 * 9.81 * 1.0 * 0.28 * 0.65 / (1.95 * 0.622 + 0.116)
            = 3.570 / (1.213 + 0.116)
            = 3.570 / 1.329
            = 2.685

u_sliding = 1.64 m/s
```

**Calculo para rolling (theta = 0):**

```
u_rolling^2 = 2 * 9.81 * 1.0 * 0.28 / (1.95 * (0.28/0.45)^2 + 0.178)
            = 5.494 / (1.95 * 0.387 + 0.178)
            = 5.494 / (0.755 + 0.178)
            = 5.494 / 0.933
            = 5.890

u_rolling = 2.43 m/s
```

**Calculo para lifting (theta = 0):**

```
u_lifting^2 = 2 * 9.81 * 1.0 * 0.28 / 0.178
            = 5.494 / 0.178
            = 30.86

u_lifting = 5.55 m/s
```

### 2.4 Resumen de Velocidades Minimas para BLIR3 (~150 kg)

| Modo de transporte | u_min [m/s] | Condicion                    |
|-------------------|-------------|------------------------------|
| Sliding           | ~1.6        | Mas facil de iniciar         |
| Rolling           | ~2.4        | Requiere mas velocidad       |
| Lifting           | ~5.6        | Requiere velocidad muy alta  |

**Sanity check:** Con dam_h = 0.3m, v_front(Ritter) = 3.4 m/s > u_sliding = 1.6 m/s.
Esto significa que **incluso el dam_h mas bajo deberia mover el boulder por sliding**.
Con dam_h = 0.8m, v_front = 5.6 m/s, cercano a u_lifting, lo que sugiere que a dam_h altos
el boulder podria experimentar saltacion.

### 2.5 Variacion con Masa del Boulder

Para un boulder mas pesado (300 kg, misma densidad), las dimensiones aumentan ~factor 1.26
(raiz cubica de 2), y c aumenta proporcionalmente, lo que **aumenta u_min** (proporcionalmente
a sqrt(c)). Un boulder de 300 kg necesitaria ~12% mas velocidad para iniciar sliding.

Para un boulder mas liviano (50 kg), c disminuye, y u_min **baja** ~27%.

### 2.6 Referencia

- Nandasena, N.A.K., Paris, R. & Tanaka, N. (2011). Reassessment of hydrodynamic equations: Minimum flow velocity to initiate boulder transport by high energy events (storms, tsunamis). Marine Geology, 281, 70-84.
- Nandasena, N.A.K., Tanaka, N. & Tanimoto, K. (2013). Boulder transport by the 2011 Great East Japan tsunami: Comprehensive field observations and whither model predictions? Marine Geology, 346, 292-309.

---

## 3. Nott (2003) — Altura de Ola Minima

### 3.1 Concepto

Nott (1997, 2003) desarrollo ecuaciones que estiman la **altura de ola minima** (tsunami o
tormenta) necesaria para transportar un boulder, basandose en sus dimensiones y densidad.

Tres escenarios de pre-transporte:
1. **SABS** (Sub-Aerial Block Scenario): boulder sobre la superficie, sin confinamiento
2. **SMBS** (Submerged Block Scenario): boulder sumergido
3. **JBBS** (Joint-Bounded Block Scenario): boulder confinado en roca, suelto en las juntas

### 3.2 Ecuacion General (Subaerial, Sliding)

La forma general de la ecuacion de Nott para el caso subaerial es:

```
H_t = 2 * c * (rho_s - rho_w) / (delta * rho_w * (Cd * (c/b) + mu * Cl))
```

donde:
- `H_t` = altura de ola (tsunami o tormenta)
- `c` = eje menor del boulder
- `delta` = parametro de tipo de ola (**CLAVE**)
  - delta = 4 para tsunami (Fr = 2, asumido supercritico)
  - delta = 1 para tormenta (Fr = 1, asumido critico)
- Otros parametros como en Nandasena

**Nota critica:** lo que Nott llama "wave height" es en realidad un **espesor de flujo**
(flow thickness), no una altura de ola orbital. Esta ambiguedad ha generado confusion
significativa en la literatura.

### 3.3 Aplicacion a BLIR3 (~150 kg)

```
H_tsunami = 2 * 0.28 * (2000 - 1000) / (4 * 1000 * (1.95*0.622 + 0.65*0.178))
          = 560 / (4 * 1000 * 1.329)
          = 560 / 5316
          = 0.105 m
```

```
H_storm = 2 * 0.28 * (2000 - 1000) / (1 * 1000 * 1.329)
        = 560 / 1329
        = 0.421 m
```

**Interpretacion para nuestra simulacion:** El dam-break con dam_h = 0.3m genera un
"espesor de flujo" que supera H_tsunami = 0.105 m, consistente con que se espera
movimiento del boulder en todos nuestros casos.

### 3.4 Limitaciones Fundamentales (ver Seccion 5 — Cox 2020)

- El parametro delta = Fr^2 NO es constante
- No se puede distinguir tsunami de tormenta con estas ecuaciones
- Los valores de H devueltos por la ecuacion son **no realistas** en muchos casos
- No hay base hidrodinamica para derivar altura de ola desde dimensiones del boulder

### 3.5 Referencia

- Nott, J. (2003). Waves, coastal boulder deposits and the importance of the pre-transport setting. Earth and Planetary Science Letters, 210, 269-276.
- Nott, J. (1997). Extremely high-energy wave deposits inside the Great Barrier Reef, Australia: determining the cause — tsunami or tropical cyclone. Marine Geology, 141, 193-207.

---

## 4. Imamura et al. (2008) — Modelo de Trayectoria

### 4.1 Descripcion del Modelo

Imamura, Goto & Ohkubo (2008) desarrollaron un **modelo numerico 2D** para el transporte
de un boulder por tsunami, basado en las ecuaciones originales de Noji et al. (1993).

El modelo acopla:
1. **Ecuaciones de aguas someras no lineales** (continuidad + momentum del fluido, depth-averaged)
2. **Ecuacion de momentum del boulder**

### 4.2 Ecuacion de Movimiento del Boulder

```
(M + M_a) * dV/dt = F_D + F_L_eff - F_f - F_g
```

donde:
- `M` = masa del boulder
- `M_a` = masa agregada = Cm * rho_w * Vol_boulder
- `F_D` = fuerza de drag = 0.5 * Cd * rho_w * A_frontal * |u - V| * (u - V)
- `F_L_eff` = efecto efectivo del lift (reduce peso normal)
- `F_f` = fuerza de friccion = mu(t) * (W - F_L) (variable en el tiempo)
- `F_g` = componente gravitacional en la pendiente

### 4.3 Innovacion: Coeficiente de Friccion Variable

El aporte clave de Imamura es el **coeficiente de friccion empirico variable** mu(t):
- Cuando el boulder se desliza: mu = mu_0 (friccion dinamica, constante)
- Cuando el boulder rueda o salta: mu disminuye con el tiempo de contacto reducido
- La relacion mu(t) se obtiene empiricamente de experimentos en canal

### 4.4 Coeficientes Usados por Imamura

| Coeficiente   | Valor | Nota                          |
|---------------|-------|-------------------------------|
| Cd (drag)     | 1.05  | Menor que Nandasena (1.95)    |
| Cm (masa)     | 1.67  | Masa agregada                 |
| mu_0          | 0.5   | Friccion dinamica base        |

**Nota:** Los valores de Cd difieren significativamente entre autores:
- Imamura: Cd = 1.05
- Nandasena: Cd = 1.95
- Rango en la literatura: 1.0 - 2.5

### 4.5 Que Predice el Modelo

- **Trayectoria completa** del boulder (posicion vs tiempo)
- **Velocidad** del boulder vs velocidad del flujo
- **Modo de transporte** (sliding vs rolling vs saltation)
- **Distancia final** de transporte

### 4.6 Hallazgos Experimentales

- El boulder es transportado principalmente por un **bore** (no por la ola directamente)
- El modo dominante es **rolling/saltation**, no sliding
- La velocidad del boulder **siempre es menor** que la del flujo
- Hay un **retardo temporal**: el boulder no se mueve inmediatamente al impacto de la ola

### 4.7 Limitaciones

1. **2D depth-averaged**: no captura efectos 3D (rotacion, contacto puntual)
2. **Forma simplificada**: usa bloques cubicos/rectangulares, no geometrias reales
3. **Friccion empirica**: la relacion mu(t) depende del material y configuracion
4. **Sin interaccion boulder-boulder**: solo un cuerpo
5. **Coeficientes constantes**: Cd y Cm no varian con Re o la configuracion

### 4.8 Relevancia para Nuestra Tesis

El modelo de Imamura es un **precursor conceptual** de lo que hacemos con SPH+Chrono:
- Nosotros resolvemos las ecuaciones de Navier-Stokes completas (no SWE)
- Chrono maneja dinamica rigida real (no ecuacion de momentum simplificada)
- SPH captura interaccion fluido-solido en 3D
- Nuestro enfoque es **superior** en realismo fisico pero **mucho mas costoso**

### 4.9 Referencia

- Imamura, F., Goto, K. & Ohkubo, S. (2008). A numerical model for the transport of a boulder by tsunami. Journal of Geophysical Research: Oceans, 113, C01008.
- Noji, M., Imamura, F. & Shuto, N. (1993). Numerical simulation of boulder transport by tsunamis. In Proc. IUGG/IOC Int. Tsunami Symp., 189-197.

---

## 5. Cox et al. (2020) — Critica Sistematica: Por Que las Ecuaciones Son "Flawed"

### 5.1 El Paper

Cox, R., Dias, K.A. & Feteira, J.F. (2020). "Systematic Review Shows That Work Done by
Storm Waves Can Be Misinterpreted as Tsunami-Related Because Commonly Used Hydrodynamic
Equations Are Flawed." Frontiers in Marine Science, 7, 4.

**Open access:** https://www.frontiersin.org/articles/10.3389/fmars.2020.00004/full

### 5.2 Tesis Central

Las ecuaciones de Nott (y sus derivaciones por Nandasena) son **invalidas** para:
1. Calcular alturas de ola a partir de dimensiones de boulders
2. Distinguir entre depositos de tsunami y de tormenta

### 5.3 Problemas Especificos Identificados

#### 5.3.1 El Parametro delta = Fr^2 No Es Constante

- Nott asume Fr = 2 para tsunami (delta = 4) y Fr = 1 para tormenta (delta = 1)
- En realidad, el Froude number **varia continuamente** segun:
  - Batimetria costera
  - Topografia local
  - Rotura de la ola
  - Interaccion ola-costa
- **No hay base fisica** para asumir que flujos de tormenta siempre tienen Fr mas bajo que tsunami
- Delta no es constante sino **variable** de un flujo a otro

#### 5.3.2 Velocidad de Ola de Tormenta Subestimada

- Nott asume que la velocidad del bore de tormenta nunca excede la velocidad de ola en aguas someras
- Esta asuncion esta **hard-wired** en las ecuaciones
- Ignora efectos locales de amplificacion (topografia, resonancia, focalizacion)

#### 5.3.3 Coeficiente de Lift Subestimado

- El valor estandar Cl = 0.178 (Einstein & El-Samni, 1949) es para particulas en lecho fluvial
- Para boulders reales, Cl puede ser **mucho mayor** (hasta 2.0)
- Aumentar Cl de 0.178 a 2.0 **reduce drasticamente** la altura de ola calculada
- Esto significa que olas de tormenta pueden mover boulders que Nott predice requieren tsunami

#### 5.3.4 "Wave Height" No Es Altura de Ola

- Lo que Nott llama "wave height" es en realidad un **espesor de flujo** (flow thickness)
- No se puede equiparar directamente con altura de ola orbital
- Esta confusion conceptual se ha propagado en toda la literatura derivada

#### 5.3.5 Validacion de Campo: Islas Aran

- Cox et al. usaron una base de datos de **boulders en las Islas Aran (Irlanda)** movidos por tormentas recientes **documentadas**
- Las ecuaciones de Nott retornan alturas de ola **no realistas y contradichas por los datos**
- En muchos casos, las ecuaciones predicen que se necesitarian olas imposiblemente grandes para mover boulders que de hecho fueron movidos por tormentas documentadas

#### 5.3.6 No Se Puede Hindcast

- Las ecuaciones **no pueden reconstruir** las condiciones de oleaje reales a partir de depositos de boulders
- No tienen valor analitico para determinar si un evento fue tsunami o tormenta

### 5.4 Implicaciones para Nuestra Tesis (**CLAVE**)

Esta critica es **fundamental** para justificar nuestro enfoque:

1. **Las ecuaciones empiricas son insuficientes** → justifica usar simulacion numerica (SPH)
2. **Los coeficientes (Cd, Cl, Cm) son inciertos** → justifica un estudio parametrico
3. **La geometria del boulder importa** → justifica usar STLs reales en vez de bloques cubicos
4. **El Froude number varia** → SPH lo resuelve naturalmente (sin asumir Fr constante)
5. **La interaccion fluido-estructura es compleja** → Chrono la resuelve mecanicamente
6. **Se necesita surrogate model** → GP + UQ para cubrir el espacio parametrico sin
   miles de simulaciones

**En el paper/tesis, citar Cox 2020 en la introduccion/motivacion para justificar por que
se necesita SPH en vez de ecuaciones simplificadas.**

### 5.5 Referencia

- Cox, R., Dias, K.A. & Feteira, J.F. (2020). Systematic Review Shows That Work Done by Storm Waves Can Be Misinterpreted as Tsunami-Related Because Commonly Used Hydrodynamic Equations Are Flawed. Frontiers in Marine Science, 7, 4. doi: 10.3389/fmars.2020.00004

---

## 6. Sanity Checks para Nuestros Resultados SPH

### 6.1 Monotonicidad de la Respuesta

| Check                        | Esperado                               | Metodo de verificacion         |
|------------------------------|----------------------------------------|-------------------------------|
| dam_h sube -> disp sube      | Monotonicamente creciente              | Scatter plot + correlacion    |
| mass sube -> disp baja       | Monotonicamente decreciente            | Scatter plot + correlacion    |
| dam_h sube -> fuerza sube    | Fuerza pico SPH crece con dam_h        | Boxplot / scatter             |
| mass sube -> aceleracion baja | Newton: misma fuerza, mas masa = menos acc | Time series comparacion     |

**Si alguna de estas tendencias NO se cumple, hay un error en la simulacion o en el
post-procesamiento.**

### 6.2 Velocidad del Frente vs Ritter

| Check                                          | Criterio                               |
|------------------------------------------------|----------------------------------------|
| v_frente(SPH) < v_frente(Ritter) = 2*sqrt(g*h) | SPH debe ser menor (friccion, 3D)     |
| Diferencia tipica: 5-15% menos que Ritter       | Si SPH > Ritter: algo esta mal        |
| Medicion: usar GaugesVel en posicion pre-boulder | Pico de velocidad del primer gauge    |

**Valores de referencia:**

| dam_h [m] | v_Ritter [m/s] | v_SPH esperado [m/s] |
|-----------|----------------|----------------------|
| 0.30      | 3.43           | 2.9 - 3.3            |
| 0.50      | 4.43           | 3.8 - 4.2            |
| 0.80      | 5.60           | 4.8 - 5.3            |

### 6.3 Desplazamiento — Orden de Magnitud

Para dam-break de laboratorio (~0.3-0.8m) contra un boulder de 150 kg:

| Check                                           | Valor esperado                              |
|-------------------------------------------------|---------------------------------------------|
| dam_h = 0.3m, mass = 150kg                      | Desplazamiento: 0.01 - 0.5 m (pequeho)     |
| dam_h = 0.8m, mass = 50kg                       | Desplazamiento: 1 - 5+ m (significativo)    |
| dam_h = 0.3m, mass = 300kg                      | Desplazamiento: ~0 (posiblemente sin movimiento) |
| dam_h = 0.8m, mass = 300kg                      | Desplazamiento: 0.1 - 2 m (moderado)       |
| Desplazamiento < 0                              | ERROR (boulder no puede ir contra el flujo) |
| Desplazamiento > longitud del canal (30m)       | ERROR (o dam_h/mass muy extremos)           |

**Nota:** estos son ordenes de magnitud estimados. Los valores exactos dependen de
la geometria, friccion, y configuracion especifica.

### 6.4 Fuerzas SPH vs Peso del Boulder

| Check                                           | Criterio                                     |
|-------------------------------------------------|----------------------------------------------|
| Peso del boulder: W = m*g                       | 150*9.81 = 1471.5 N                          |
| Fuerza SPH pico debe superar mu*W para mover    | mu*W = 0.65*1471.5 = 956.5 N                 |
| Fuerza SPH pico tipica (dam_h=0.5m)             | 500 - 5000 N (orden de magnitud)              |
| Si F_SPH_pico << mu*W y hay movimiento          | Inconsistencia (revisar fuerzas)              |
| Si F_SPH_pico >> 10*W y dam_h es bajo           | Posible error numerico                        |

**Nota sobre fuerzas de contacto:** Como se documento en la convergencia (7 dp study),
la fuerza de contacto Chrono tiene CV = 82% y NO converge con dp. Esto es un artefacto
numerico conocido y NO debe usarse como criterio de validacion.

### 6.5 Curvas Temporales Suaves

| Check                                           | Criterio                                     |
|-------------------------------------------------|----------------------------------------------|
| Desplazamiento vs tiempo                        | Curva monotonica (no oscila hacia atras)      |
| Velocidad del boulder vs tiempo                 | Pico seguido de decaimiento suave             |
| Fuerza SPH vs tiempo                            | Pico al impacto, luego decay, sin spikes espurios |
| Frecuencia de oscilacion                        | Si hay oscilaciones de alta frecuencia: ruido numerico |

**Signos de problemas:**
- Oscilaciones de alta frecuencia en la fuerza o posicion
- Velocidad del boulder que **supera** la velocidad del flujo (fisicamente imposible)
- Desplazamiento que retrocede significativamente (sin rebote de pared)
- Rotacion erratica sin causa fisica

### 6.6 Consistencia con Nandasena

| Check                                           | Criterio                                      |
|-------------------------------------------------|-----------------------------------------------|
| Boulder deberia moverse si v_flujo > u_sliding   | 1.6 m/s (BLIR3 150kg)                        |
| Si dam_h=0.3m (v~3.4 m/s) y boulder NO se mueve | Posible error en FtPause, masa, o geometria   |
| Si dam_h=0.8m y desplazamiento muy bajo          | Revisar friccion o contacto Chrono            |
| Modo de transporte dominante                     | Sliding para velocidades moderadas, rolling a altas |

### 6.7 Checklist Rapido Pre-Publicacion

```
[ ] Tendencia dam_h vs displacement es monotona creciente
[ ] Tendencia mass vs displacement es monotona decreciente
[ ] Velocidad del frente esta dentro de 85-100% de Ritter
[ ] Desplazamientos estan en orden de magnitud razonable
[ ] Fuerza SPH pico supera mu*W cuando hay movimiento
[ ] Curvas temporales son suaves (sin oscilaciones espurias)
[ ] Velocidad del boulder nunca supera velocidad del flujo
[ ] Boulder no retrocede significativamente
[ ] Energia cinetica del boulder < energia potencial del reservorio
[ ] Resultados de masa 50 kg y 300 kg son fisicamente consistentes
```

---

## 7. Figuras que un Revisor Espera en un Paper de Transporte de Boulders

### 7.1 Figuras del Setup Numerico

| # | Figura                                    | Proposito                                      |
|---|-------------------------------------------|------------------------------------------------|
| 1 | **Esquema del dominio computacional**      | Dimensiones, condiciones de borde, posicion del boulder |
| 2 | **Mesh/particle convergence study**        | Desplazamiento vs dp (al menos 3-4 resoluciones) |
| 3 | **Snapshot de la distribucion de particulas** | Mostrar dp, resolucion, geometria del boulder |
| 4 | **Render 3D del setup**                    | Boulder en el canal con agua pre-dam-break     |

### 7.2 Figuras de Validacion

| # | Figura                                    | Proposito                                      |
|---|-------------------------------------------|------------------------------------------------|
| 5 | **Velocidad del frente SPH vs Ritter**    | Validar que el solver reproduce dam-break correctamente |
| 6 | **Perfil de velocidad/profundidad en gauges** | Comparar con analitico o experimental si disponible |
| 7 | **Fuerza sobre el boulder vs tiempo**     | Mostrar perfil temporal de la fuerza hidrodinamica |

### 7.3 Figuras de Resultados Parametricos

| # | Figura                                    | Proposito                                      |
|---|-------------------------------------------|------------------------------------------------|
| 8  | **Desplazamiento final vs dam_h**         | Tendencia parametrica principal                |
| 9  | **Desplazamiento final vs mass**          | Segunda tendencia parametrica                  |
| 10 | **Mapa de calor 2D (dam_h x mass)**       | Superficie de respuesta                        |
| 11 | **Curvas de desplazamiento vs tiempo**     | Familias de curvas para distintos parametros   |
| 12 | **Snapshots temporales** (t = 0, 0.5, 1, 2, 5s) | Secuencia visual del transporte         |

### 7.4 Figuras del Surrogate Model (GP)

| # | Figura                                    | Proposito                                      |
|---|-------------------------------------------|------------------------------------------------|
| 13 | **Superficie GP con puntos de entrenamiento** | Mostrar el surrogate y la cobertura de datos |
| 14 | **Incertidumbre GP (sigma)**              | Mapa de donde el modelo es mas/menos confiable |
| 15 | **LOO cross-validation**                  | Predecido vs observado para cada punto         |
| 16 | **Frontera de decision**                  | Umbral critico (si se usa clasificacion binaria) |
| 17 | **Indices de Sobol**                      | Contribucion de cada parametro a la varianza   |

### 7.5 Figuras de Analisis Fisico

| # | Figura                                    | Proposito                                      |
|---|-------------------------------------------|------------------------------------------------|
| 18 | **Froude number vs posicion/tiempo**      | Mostrar que Fr NO es constante (rebate a Nott) |
| 19 | **Velocidad boulder vs velocidad flujo**  | Mostrar retardo y que v_boulder < v_flujo      |
| 20 | **Diagrama de fuerzas sobre el boulder**  | Drag, lift, peso, friccion vs tiempo           |
| 21 | **Comparacion con Nandasena**             | Desplazamiento SPH vs prediccion empirica      |

### 7.6 Figuras Opcionales de Alto Impacto

| # | Figura                                    | Proposito                                      |
|---|-------------------------------------------|------------------------------------------------|
| 22 | **Render Blender fotorrealista**          | Impacto visual (portada, presentacion)         |
| 23 | **Animacion** (como supplementary)        | Video del dam-break completo                   |
| 24 | **Histograma de desplazamientos (MC)**    | Si se hace UQ con Monte Carlo sobre el GP      |

---

## 8. Tabla Resumen de Ecuaciones y Parametros

| Ecuacion / Modelo     | Ano  | Que calcula                         | Coeficientes clave        | Limitaciones principales              |
|----------------------|------|-------------------------------------|---------------------------|---------------------------------------|
| Ritter               | 1892 | Velocidad del frente dam-break      | g, h0                     | Sin friccion, 1D, ideal               |
| Nott                 | 2003 | Altura de ola minima para transporte | Cd, Cl, delta (Fr^2)      | Fr constante, H != wave height        |
| Nandasena et al.     | 2011 | Velocidad minima para cada modo     | Cd, Cl, mu_s, dimensiones | Sin interaccion, forma simplificada   |
| Imamura et al.       | 2008 | Trayectoria del boulder             | Cd, Cm, mu(t)             | 2D, SWE, forma rectangular            |
| Cox et al. (critica) | 2020 | N/A — demuestra que Nott es invalido | N/A                       | Solo critica, no propone alternativa  |
| **SPH + Chrono**     | Este trabajo | Todo lo anterior + mas       | dp, viscosidad, Chrono params | Costo computacional (horas por sim) |

---

## 9. Argumento de Tesis: Por Que SPH en Vez de Ecuaciones

**Narrativa para la introduccion/motivacion:**

1. Las ecuaciones empiricas (Nott 2003, Nandasena 2011) son herramientas utiles pero
   tienen limitaciones fundamentales demostradas por Cox et al. (2020).

2. El Froude number no es constante; la geometria del boulder importa; la interaccion
   fluido-estructura es compleja y no puede reducirse a coeficientes constantes.

3. El modelo de Imamura (2008), aunque mas sofisticado, sigue usando SWE depth-averaged
   y formas simplificadas.

4. SPH (DualSPHysics) + mecanica rigida (Chrono) resuelve:
   - Navier-Stokes 3D completo (no SWE)
   - Geometria real del boulder (STL)
   - Interaccion fluido-estructura bidireccional
   - Froude number variable naturalmente
   - Modos de transporte emergen de la fisica

5. El costo computacional de SPH se mitiga con un **GP surrogate model**,
   permitiendo exploracion parametrica y UQ con ~25-50 simulaciones.

6. Esta combinacion (SPH + GP + Sobol) es **original**: no existe en la literatura
   para transporte de boulders costeros.

---

## 10. Referencias Completas

1. Ritter, A. (1892). Die Fortpflanzung der Wasserwellen. Z. Ver. Dtsch. Ing., 36(33), 947-954.
2. Nott, J. (1997). Extremely high-energy wave deposits inside the Great Barrier Reef, Australia: determining the cause -- tsunami or tropical cyclone. Marine Geology, 141, 193-207.
3. Nott, J. (2003). Waves, coastal boulder deposits and the importance of the pre-transport setting. Earth and Planetary Science Letters, 210, 269-276.
4. Imamura, F., Goto, K. & Ohkubo, S. (2008). A numerical model for the transport of a boulder by tsunami. J. Geophys. Res. Oceans, 113, C01008.
5. Nandasena, N.A.K., Paris, R. & Tanaka, N. (2011). Reassessment of hydrodynamic equations: Minimum flow velocity to initiate boulder transport by high energy events (storms, tsunamis). Marine Geology, 281, 70-84.
6. Nandasena, N.A.K., Tanaka, N. & Tanimoto, K. (2013). Boulder transport by the 2011 Great East Japan tsunami. Marine Geology, 346, 292-309.
7. Cox, R., Dias, K.A. & Feteira, J.F. (2020). Systematic Review Shows That Work Done by Storm Waves Can Be Misinterpreted as Tsunami-Related Because Commonly Used Hydrodynamic Equations Are Flawed. Frontiers in Marine Science, 7, 4.
8. Engel, M. & May, S.M. (2012). Bonaire's boulder fields revisited: evidence for Holocene tsunami impact on the Leeward Antilles. Quaternary Science Reviews, 54, 126-141.
9. Einstein, H.A. & El-Samni, E.S.A. (1949). Hydrodynamic forces on a rough wall. Reviews of Modern Physics, 21(3), 520-524.
10. Castro-Orgaz, O. & Chanson, H. (2017). Ritter's dry-bed dam-break flows: positive and negative wave dynamics. Environmental Fluid Mechanics, 17(4), 665-694.
11. Oetjen, J., Engel, M., Bruckner, H., Pudasaini, S.P. & Schuttrumpf, H. (2020). Significance of boulder shape, shoreline configuration and pre-transport setting for the transport of boulders by tsunamis. Earth Surface Processes and Landforms, 45, 2118-2133.
12. Bressan, L., Guerrero, M., Antonini, A., Petruzzelli, V., Archetti, R., Lamberti, A. & Tinti, S. (2018). A laboratory experiment on the incipient motion of boulders by high-energy coastal flows. Earth Surface Processes and Landforms, 43, 2935-2947.
