# Preparación Reunión Moris — 13 marzo 2026
> Documento de estudio personal. Léelo completo antes de entrar.

---

## TU NARRATIVA DE APERTURA (di esto primero, de memoria)

> "Profesor, durante febrero hice tres cosas: un estudio de convergencia para validar la resolución de las simulaciones, una primera campaña de 15 casos para explorar el espacio de parámetros, y al detectar un problema con el dominio lo corregí y corrí 5 casos más con el canal extendido. Hoy no tengo máquina disponible porque Diego retomó su PC y el mío aún no llega. Le quiero mostrar los resultados y aprovechar para alinear algunas definiciones antes de que viaje."

---

## BLOQUE 1 — ESTUDIO DE CONVERGENCIA (dp)

### ¿Qué es dp? (entiéndelo así)

DualSPHysics simula el fluido como miles de **partículas esféricas** en lugar de una malla. El parámetro **dp** es la distancia entre esas partículas — como el "tamaño de píxel" de la simulación.

- **dp grande** (ej. 0.05 m) = pocas partículas, rápido, pero impreciso. El boulder queda representado por solo ~30 partículas.
- **dp chico** (ej. 0.003 m) = muchas partículas, lento, pero preciso. El boulder tiene miles de partículas.

El problema: usar dp muy chico sin necesidad es desperdiciar semanas de cómputo. Usar dp muy grande produce resultados incorrectos.

**La solución: estudio de convergencia.** Corres la misma simulación con dp cada vez más chico, y cuando el resultado deja de cambiar significativamente, encontraste el dp mínimo necesario.

### ¿Qué hiciste exactamente?

Corriste **7 simulaciones** de la misma escena (mismo boulder, misma ola), variando solo dp:

| dp (m) | Tiempo aprox |
|--------|-------------|
| 0.050  | ~2 min      |
| 0.020  | ~15 min     |
| 0.015  | ~35 min     |
| 0.010  | ~90 min     |
| 0.008  | ~180 min    |
| 0.005  | ~400 min    |
| 0.004  | ~540 min    |
| 0.003  | ~812 min    |

En cada simulación mediste: desplazamiento máximo, velocidad máxima, rotación máxima, fuerza SPH, fuerza de contacto.

### ¿Qué encontraste?

**Resultado principal: dp=0.004 m es suficiente para producción.**

Entre dp=0.004 y dp=0.003 (el más fino que probaste):
- Desplazamiento: diferencia de **3.9%** ✓ (< 5%)
- Fuerza SPH: diferencia de **2.8%** ✓ (< 5%)
- Velocidad: diferencia de **0.8%** ✓ (< 5%)
- Rotación: diferencia de **6.3%** ≈ (borderline, aceptable)

Esto significa: afinar más el dp no mejora los resultados de forma significativa. **Converge en dp=0.004.**

**Hallazgo adicional (científicamente interesante):**
La **fuerza de contacto** (boulder golpeando el fondo) NO converge — su variación entre dp fue de 82%. No es un error: es una limitación conocida de SPH en impactos puntuales. El hallazgo es que **no se puede usar la fuerza de contacto como criterio de movimiento incipiente**.

**Implicación práctica:**
- dp=0.004 tarda ~540 min/caso (~9h)
- dp=0.003 tardaría ~812 min/caso (~14h) para mejorar solo un 4%
- Ahorro de 34% del tiempo de cómputo sin pérdida real de precisión

### Qué mostrarle a Moris

**Carpeta:** `C:\Seba\Tesis\data\figuras_7dp_es\pngs\`

Abre estas imágenes en orden:

1. **`fig07_tabla_resumen.png`** — tabla con todos los valores de cada dp. Muéstrala primero. Es la evidencia directa.
2. **`fig08_historia_completa.png`** — gráfico de cómo cambia el desplazamiento al afinar dp. Se ve que la curva se aplana después de dp=0.005.
3. **`fig09_veredicto.png`** — veredicto final "CONVERGENCIA ALCANZADA".
4. **`fig04_fuerza_contacto_diagnostico.png`** — solo si pregunta por la fuerza de contacto.

### Qué decir al mostrar esto

> "Acá está la tabla de convergencia. Probé 7 resoluciones distintas. La columna muestra el cambio relativo entre resoluciones consecutivas. En dp=0.004, las métricas principales tienen menos del 5% de diferencia con el dp más fino. Ahí declaré convergencia. Elegí dp=0.004 para producción porque dp=0.003 cuesta 34% más tiempo sin mejorar los resultados."

Si pregunta por la fuerza de contacto:
> "La fuerza de contacto no convergió — variación del 82% entre resoluciones. Investigué y es una limitación conocida de SPH en impactos puntuales. Por eso no la uso como criterio de movimiento."

---

## BLOQUE 2 — 15 SIMULACIONES (canal 15 m)

### ¿Qué hiciste exactamente?

Después de validar dp=0.004, quisiste explorar el espacio de parámetros: ¿qué variables del problema afectan más el transporte del boulder?

Diseñaste **50 combinaciones** de parámetros usando **LHS (Latin Hypercube Sampling)** — una técnica estadística para distribuir los experimentos de forma eficiente dentro del rango de interés.

**Los 3 parámetros que variaste:**

| Parámetro | Rango | Qué significa |
|-----------|-------|---------------|
| `dam_height` | 0.10 – 0.50 m | Altura inicial de la columna de agua (el "tsunami") |
| `boulder_mass` | 0.80 – 1.50 kg | Masa del boulder |
| `boulder_rot_z` | 0° – 90° | Orientación inicial del boulder |

**¿Qué es LHS?** Divide cada variable en 50 intervalos iguales y los combina de manera que ninguna combinación se repita en ningún eje. Garantiza cobertura uniforme del espacio de parámetros con el mínimo de experimentos — es lo que se usa en ingeniería de diseño de experimentos.

Corriste los primeros **15 casos** de los 50 planificados en el PC de Diego (RTX 5090, GPU de alta gama).

### ¿Qué encontraste?

**Todos los 15 casos mostraron movimiento del boulder.** No encontraste ningún caso de "no movimiento" con estos rangos.

Los resultados clave:

| Caso | dam_height (m) | Masa (kg) | Desplazamiento (m) |
|------|----------------|-----------|-------------------|
| lhs_004 | 0.136 | 0.890 | 0.81 m — poco movimiento |
| lhs_010 | **0.108** | 1.294 | **0.05 m — casi no se mueve** |
| lhs_006 | 0.458 | 1.111 | **6.39 m — ⚠ saturado** |
| lhs_009 | 0.494 | 1.437 | **6.40 m — ⚠ saturado** |
| lhs_012 | 0.473 | 1.417 | **6.03 m — ⚠ saturado** |
| lhs_015 | 0.462 | 0.827 | **6.40 m — ⚠ saturado** |

**Correlaciones (qué parámetro importa más):**
- `dam_height` → r = **0.97** — domina completamente
- `boulder_mass` → r ≈ **−0.20** — efecto secundario (más masa = un poco menos movimiento)
- `boulder_rot_z` → r ≈ **0** — prácticamente irrelevante

**Caso interesante: lhs_010**
Con `dam_height=0.108 m`, el boulder se desplazó solo 5 cm. La velocidad de flujo registrada fue casi cero, lo que sugiere que la ola apenas llegó al boulder. Es el caso más cercano a "no movimiento" que tienes.

### El problema que detectaste

**4 casos (lhs_006, 009, 012, 015) llegaron al extremo del canal.** El canal medía 15 m. Con olas altas, el boulder viajaba hasta el final del dominio y el desplazamiento quedaba truncado artificialmente en ~6.4 m — no es el desplazamiento real, es el límite del canal.

Esto contamina el análisis estadístico.

**Solución aplicada:** Extendiste el canal de 15 m a 30 m. El boulder ahora tiene 21.5 m de espacio libre. Los 4 casos saturados deberían dar desplazamientos reales (posiblemente mayores) con el canal extendido.

### Qué mostrarle a Moris

**Carpeta:** `C:\Seba\Tesis\data\figuras_piloto\`

Abre en orden:

1. **`fig03_correlacion_parametros.png`** — muestra visualmente que dam_height domina.
2. **`fig02_distribucion_resultados.png`** — distribución de desplazamientos de los 15 casos.
3. **`fig07_tabla_resumen.png`** — tabla resumen de todos los casos.

También puedes abrir: **`data\results_ws_15cases.csv`** en Excel para mostrar los números crudos.

### Qué decir al mostrar esto

> "Estos son los 15 casos preliminares. Todos mostraron movimiento. La correlación más fuerte es con la altura de columna — prácticamente lo explica todo. La masa tiene efecto secundario, y la orientación inicial no importa."
>
> "El problema: 4 casos llegaron al extremo del canal de 15 m. El desplazamiento quedó truncado en 6.4 m. Extendí el canal a 30 m para corregir eso."

---

## BLOQUE 3 — 5 SIMULACIONES (canal 30 m)

### ¿Qué hiciste exactamente?

Extendiste el canal de 15 m a 30 m modificando el modelo 3D del canal y el archivo de configuración XML. Reiniciaste la campaña de 50 casos desde el caso 1 el **28 de febrero**.

Alcanzaste a correr **5 casos** (lhs_001 a lhs_005) antes de que Diego retomara el PC.

**Resultado de los 5 casos con canal 30 m:**
- Los 5 muestran movimiento
- **Ninguno saturó** — ninguno llegó al extremo del canal de 30 m
- Confirman que la corrección funciona correctamente

### Estado actual

**No tienes PC disponible.** Diego retomó el suyo, el tuyo aún no llega. Los 45 casos restantes están pendientes.

### Qué mostrarle a Moris

**Carpeta:** `C:\Seba\Tesis\data\figuras_lhs_001\`

Abre:
1. **`12_dashboard_summary.png`** — resumen visual de una simulación completa: posición, velocidad, rotación del boulder en el tiempo.
2. **`01_displacement_vs_time.png`** — el boulder acelerando y frenando, con trayectoria clara.

También puedes abrir brevemente:
**`cases\lhs_001\lhs_001_out\ChronoExchange_mkbound_51.csv`** para mostrar el dato crudo.

### Qué decir al mostrar esto

> "Este es un ejemplo de la salida de una simulación con el canal extendido. Cada fila del CSV es la posición y velocidad del boulder en un instante. El pipeline extrae estas métricas automáticamente y las consolida."
>
> "Alcancé a correr 5 casos antes de que Diego retomara el PC. Están bien — sin saturación. Pero para continuar los 45 restantes necesito acceso a una máquina."

---

## PREGUNTAS QUE NECESITAS QUE MORIS RESPONDA

### 1. El PC — dilo antes de que se vaya a Valparaíso
> "Para continuar necesito acceso a una máquina con GPU. ¿Hay algún equipo del laboratorio o del Fondecyt que pueda usar mientras llega el mío? Cada simulación toma unas 9 horas."

### 2. STLs (los 7 modelos de boulder)
> "Diego me mencionó que habría 7 formas distintas para el Fondecyt. ¿Cuándo me los podría enviar? Sin esos archivos no puedo empezar la etapa de múltiples formas."

### 3. Criterio de movimiento incipiente
> "Tengo un caso donde el boulder se desplazó solo 5 cm. ¿Eso cuenta como 'inicio de movimiento'? Estoy usando provisionalmente 5% del diámetro equivalente (~1 cm) y 5° de rotación, pero prefiero alinearlo con su criterio antes de definirlo en la tesis."

### 4. Rangos del canal físico
> "Para diseñar bien los experimentos necesito saber: ¿cuál es la altura mínima y máxima de columna que el canal físico permite? ¿Y hasta qué masa pueden fabricar el boulder para validación?"

### 5. Validación del plan
> "Le quiero mostrar el plan general para que me dé su opinión."

---

## TU PLAN (preséntalo al final)

```
ETAPA 1 — En curso (feb-abr):
  50 simulaciones con 1 forma (BLIR3)
  Variables: altura de ola, masa, orientación
  Resultado: qué parámetros dominan el movimiento
  → Análisis GP → Capítulo 6 de tesis

ETAPA 2 — Cuando lleguen los STLs (may-jun):
  245 simulaciones con 7 formas distintas (7 × 35)
  → Datos para el Fondecyt
  → Efecto de la forma en el transporte

DEFENSA: diciembre 2026
```

> "Con las 50 sims de la Etapa 1 termino el análisis de sensibilidad para la tesis. La Etapa 2 es la que se alinea con el Fondecyt — esas 245 simulaciones son directamente útiles para usted también. ¿Le parece razonable este esquema?"

---

## CONCEPTOS QUE PODRÍAS NECESITAR IMPROVISAR

**Si pregunta "¿qué es ProjectChrono?"**
> "Es un motor de física de cuerpo rígido que se acopla a DualSPHysics. Maneja el boulder como un sólido rígido con masa, inercia, y colisiones realistas con el fondo. Diego también lo usaba."

**Si pregunta "¿qué es el GP surrogate?"**
> "Es un modelo estadístico que aprende la relación entre los parámetros de entrada y el resultado. Con las 50 simulaciones como datos de entrenamiento, puede predecir resultados de combinaciones no simuladas y además da la incertidumbre de cada predicción."

**Si pregunta algo que no sabes:**
> "Eso lo tengo documentado en detalle en la metodología. Le puedo enviar ese capítulo esta semana."

---

## TABLA RÁPIDA DE ARCHIVOS

| Qué mostrar | Ruta |
|-------------|------|
| Convergencia: tabla con números | `data\figuras_7dp_es\pngs\fig07_tabla_resumen.png` |
| Convergencia: curva que se aplana | `data\figuras_7dp_es\pngs\fig08_historia_completa.png` |
| Convergencia: veredicto | `data\figuras_7dp_es\pngs\fig09_veredicto.png` |
| 15 casos: correlaciones | `data\figuras_piloto\fig03_correlacion_parametros.png` |
| 15 casos: distribución | `data\figuras_piloto\fig02_distribucion_resultados.png` |
| 15 casos: tabla | `data\figuras_piloto\fig07_tabla_resumen.png` |
| Ejemplo sim completa | `data\figuras_lhs_001\12_dashboard_summary.png` |
| Datos crudos 15 casos | `data\results_ws_15cases.csv` |

---

## LO QUE NO MENCIONES

- GNN, Paper 2, Transfer Learning → demasiado prematuro
- "La IA lo hizo" → tú lo diseñaste e implementaste
- Timelines de publicación → no te comprometas

---

## RESULTADO MÍNIMO ACEPTABLE

Si sales con estas 3 cosas, la reunión fue exitosa:

1. **Moris aprueba el plan** (50 + 245 sims)
2. **Moris define el criterio de movimiento incipiente**
3. **Tienes un camino para conseguir PC** (laboratorio, Fondecyt, o fecha de llegada del tuyo)
