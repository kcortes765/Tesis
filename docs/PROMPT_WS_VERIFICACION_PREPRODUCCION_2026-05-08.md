# Prompt para WS: verificación preproducción sin experimento propio

Estamos en la workspace Windows de la tesis SPH-DualSPHysics-Chrono.

Objetivo:
Ejecutar el bloque de verificación preproducción antes de ampliar la campaña productiva. No lanzar una campaña grande. El propósito es robustecer científicamente el modelo sin experimento propio: benchmark hidráulico, chequeo de contacto y comparación analítica preliminar.

Contexto fijo:

- Resolución operativa de producción: `dp=0.003 m`.
- Criterio primario del bloque: `classification_mode=displacement_only`.
- Umbral de movimiento: `D_max > 0.05*d_eq`.
- `reference_time_s = 0.5`.
- Rotación: variable observada/diagnóstica, no criterio primario.
- `dp=0.002` queda reservado para subconjunto fino posterior, no campaña principal.
- No vender convergencia asintótica fuerte.
- No usar gauges como evidencia primaria de movimiento del bloque.
- No correr grilla grande ni active learning completo todavía.

Archivos locales que debes leer primero:

```text
docs/CONFIGURACION_PRODUCTIVA_TESIS.md
docs/PLAN_VERIFICACION_PREPRODUCCION_SIN_EXPERIMENTO_2026-05-08.md
config/pilot_productivo_20260430.csv
exports/pilot_productivo_20260501/
data/results.sqlite
scripts/run_production.py
scripts/run_convergence_threshold.py
src/main_orchestrator.py
src/data_cleaner.py
src/geometry_builder.py
```

Si existe export de batch2, leerlo también. No asumir que existe: verificar rutas reales.

Restricciones:

1. No lanzar campaña productiva grande.
2. No correr `run_production.py --pilot --prod`.
3. No borrar outputs.
4. No subir ni copiar binarios pesados.
5. No tocar `cases/`, `_out/`, `Part*.bi4`, `*.ibi4`, VTK o outputs crudos salvo lectura mínima justificada.
6. Si corres algo, debe estar explícitamente dentro de:
   - benchmark hidráulico;
   - sanity de contacto;
   - postproceso analítico.
7. Todo comando de corrida debe tener dry-run o preflight cuando aplique.
8. Separar hechos verificados, inferencias y recomendaciones.

Tarea A: Benchmark hidráulico DualSPHysics/SPHERIC

1. Inventariar ejemplos/testcases disponibles en la instalación local de DualSPHysics.
2. Identificar si existe `01_DAMBREAK` oficial y sus scripts Windows GPU/CPU.
3. Identificar si hay datos de validación incluidos, por ejemplo Koshizuka/Oka o datos del testcase.
4. Si es viable, ejecutar primero un benchmark liviano oficial de DualSPHysics.
5. Si es viable y no consume demasiado tiempo, preparar o ejecutar SPHERIC Test 02 como benchmark principal.
6. Postprocesar:
   - altura/cota de agua en gauges;
   - posición de frente si existe;
   - velocidades si existen;
   - fuerzas/presiones si existen.
7. Comparar con datos de referencia:
   - curvas temporales;
   - error de máximo;
   - RMSE temporal relativo;
   - tiempo de llegada/desfase.
8. Guardar outputs livianos en:

```text
data/benchmarks/hydraulic_YYYYMMDD/
docs/BENCHMARK_HIDRAULICO_DUALSPHYSICS_YYYYMMDD.md
```

Tarea B: Sanity de contacto bloque-suelo-Chrono

1. Diseñar caso S00 con la geometría oficial del bloque/playa, `dp=0.003`, sin impacto hidráulico o con condición hidráulica nula/controlada.
2. Mantener:
   - bloque alineado con pendiente;
   - apoyo exacto;
   - Chrono rígido;
   - `reference_time_s=0.5`;
   - `classification_mode=displacement_only`.
3. Ejecutar solo este/estos sanity tests si el setup está claro y acotado.
4. Medir:
   - `D_max/d_eq`;
   - desplazamiento final;
   - rotación acumulada;
   - velocidad máxima;
   - fuerza de contacto;
   - drift antes de flujo.
5. Criterio:
   - ideal: `D_max/d_eq < 0.005`;
   - aceptable con justificación: `< 0.01`;
   - si se acerca a 0.05, detener producción y revisar contacto.
6. Guardar en:

```text
data/sanity/contact_YYYYMMDD/
docs/CHEQUEO_CONTACTO_CHRONO_YYYYMMDD.md
```

Tarea C: Comparación analítica preliminar

1. Consolidar resultados livianos disponibles de piloto y batch2 si existe.
2. Extraer por caso:
   - `D_max/d_eq`;
   - clase estable/fallo;
   - `mu`;
   - masa/densidad;
   - pendiente;
   - altura y velocidad de gauges cercanos;
   - fuerza/velocidad del bloque si existe.
3. Implementar un cálculo analítico de movilidad:

```text
F_D(t) = 0.5*rho_w*C_D*A_D*U(t)^2
F_L(t) = 0.5*rho_w*C_L*A_L*U(t)^2
F_drive(t) = F_D(t) + W'*sin(beta)
F_resist(t) = mu*(W'*cos(beta) - F_L(t))
Psi(t) = F_drive(t)/F_resist(t)
I_Psi = integral(max(0, Psi(t)-1) dt)
```

4. No usar un único valor rígido de coeficientes. Evaluar bandas:
   - `C_D`;
   - `C_L`;
   - área proyectada;
   - sumergencia efectiva;
   - brazo de momento si se calcula vuelco.
5. Comparar:
   - `Psi_max` vs `D_max/d_eq`;
   - `I_Psi` vs `D_max/d_eq`;
   - bandas analíticas vs clases SPH.
6. Redactar explícitamente que esto es coherencia física de bajo orden, no validación exacta.
7. Guardar en:

```text
data/analytic_comparison/YYYYMMDD/
docs/COMPARACION_ANALITICA_PRELIMINAR_YYYYMMDD.md
```

Tarea D: preparar, no correr, subconjunto fino `dp=0.002`

1. Diseñar propuesta de 6-12 casos `dp=0.002` para más adelante:
   - 1-2 estables robustos;
   - 1-2 fallos robustos;
   - 4-6 marginales;
   - 1 hidráulico fuerte;
   - 1 repetición si sirve.
2. Elegirlos desde piloto/batch2/active learning, no a mano sin evidencia.
3. No correrlos todavía salvo instrucción explícita posterior.
4. Guardar propuesta en:

```text
docs/SUBCONJUNTO_FINO_DP002_PROPUESTO_YYYYMMDD.md
```

Entrega final esperada:

- Lista de archivos verificados.
- Qué se corrió y qué no se corrió.
- Resultados del benchmark hidráulico, si se ejecutó.
- Resultados del sanity de contacto, si se ejecutó.
- Resultados de la comparación analítica preliminar.
- Si algo falló, decisión clara: seguir, corregir o detener producción.
- Propuesta de próximos casos productivos solo si las verificaciones pasan.
- Advertencias metodológicas.
- Rutas exactas de outputs.

Tono:

- Conservador.
- Científico.
- Auditable desde archivos reales.
- No promocional.
- Separar verificación hidráulica, contacto, comparación analítica y estabilidad del bloque.

