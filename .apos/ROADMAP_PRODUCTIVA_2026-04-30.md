# ROADMAP PRODUCTIVA - 2026-04-30

## Ejecucion registrada

Al 2026-04-30 se ejecuto el siguiente paso inmediato:

- graficos/tablas de convergencia regenerados en `data/figures/derived_convergence_graphics/`;
- `conv_probe_dp002_f06625` incorporado como `supplemental_fine_probe`;
- documento oficial creado en `docs/CONFIGURACION_PRODUCTIVA_TESIS.md`;
- `src/main_orchestrator.py` ajustado para usar `classification_mode="displacement_only"` y `reference_time_s=0.5` en el postproceso productivo;
- no se corrieron simulaciones nuevas ni campana parametrica.

## Estado de partida

La convergencia de frontera ya cuenta con el caso adicional:

- `conv_probe_dp002_f06625`
- `mu = 0.6625`
- `dp = 0.002`
- `classification_mode = displacement_only`
- `reference_time_s = 0.5`
- estado: `OK`
- clasificacion: `ESTABLE`
- `max_displacement_m = 0.002837`
- `disp_pct_deq = 2.82%`
- `moved = False`
- `rotated = True`

Este caso confirma que, a `dp=0.002`, incluso `mu=0.6625` permanece estable por desplazamiento. Por tanto, no hay bracket fino de falla para `dp=0.002` en el rango ensayado. La lectura metodologica debe conservar `dp=0.003` como frontera practica operativa y tratar `dp=0.002` como evidencia diagnostica de sensibilidad de resolucion, no como convergencia asintotica cerrada.

## Fase 1: Cerrar convergencia

Objetivo: dejar la decision de `dp` documentada y trazable.

Acciones:

1. Verificar que `conv_probe_dp002_f06625` quedo guardado como `OK`.
2. Regenerar graficos/tablas de convergencia incluyendo ese caso.
3. Separar claramente:
   - evidencia principal: frontera practica en `dp=0.003`;
   - evidencia diagnostica: sensibilidad al refinar a `dp=0.002`;
   - rotacion: diagnostico, no criterio de falla.
4. Actualizar memo/informe de convergencia.

Resultado esperado:

- Carpeta de figuras lista.
- CSV maestro actualizado.
- Conclusion clara: `dp=0.003` se adopta como malla operativa.

## Fase 2: Congelar configuracion productiva

Objetivo: definir la configuracion oficial que se usara en la campana grande.

Fijar:

- geometria corregida;
- bloque alineado con pendiente;
- apoyo exacto sobre la playa;
- `dp = 0.003`;
- `classification_mode = displacement_only`;
- `reference_time_s = 0.5`;
- tiempo de simulacion;
- `chrono_savadata`;
- material;
- masa/inercia;
- posicion inicial;
- pendiente base;
- gauges;
- nombres de casos.

Acciones:

1. Guardar la configuracion en un documento o archivo de control.
2. Revisar que el pipeline use esos valores por defecto.

Resultado esperado:

- Una configuracion oficial de produccion.
- Nada depende de memoria o comandos sueltos.

## Fase 3: Definir espacio parametrico

Objetivo: decidir que variables se van a barrer en la campana productiva.

Variables del Formulario B:

- altura de presa / nivel de agua;
- masa del bloque;
- orientacion del bloque;
- friccion bloque-fondo;
- pendiente de playa.

Acciones:

1. Definir rangos fisicos para cada variable.
2. Definir niveles iniciales o distribucion de muestreo.
3. Decidir si se hara:
   - grilla completa;
   - Latin Hypercube;
   - muestreo adaptativo / active learning;
   - combinacion.
4. Separar parametros fijos de parametros variables.

Resultado esperado:

- Tabla de diseno experimental preliminar.
- Numero estimado de simulaciones.

## Fase 4: Definir salidas del modelo

Objetivo: decidir que se va a aprender o explicar con las simulaciones.

Salidas principales posibles:

- clase: estable/falla;
- desplazamiento maximo;
- margen al umbral de desplazamiento;
- probabilidad de falla;
- rotacion maxima como diagnostico;
- fuerza SPH maxima;
- velocidad del flujo cercana al bloque.

Recomendacion actual:

- salida fisica principal: desplazamiento maximo o margen al umbral;
- salida de clasificacion: estable/falla por `displacement_only`;
- salidas diagnosticas: rotacion, fuerza, velocidad.

Resultado esperado:

- Dataset definido con columnas claras.
- Variable objetivo del surrogate definida antes de correr miles de casos.

## Fase 5: Piloto productivo

Objetivo: probar la campana real a pequena escala.

Acciones:

1. Correr 3 a 5 casos representativos:
   - uno estable claro;
   - uno fallido claro;
   - uno cerca del umbral;
   - uno con friccion baja;
   - uno con condicion hidraulica mas fuerte.
2. Verificar:
   - GenCase corre;
   - DualSPHysics termina;
   - Chrono escribe CSV completo;
   - el analisis clasifica bien;
   - SQLite/CSV guardan todos los campos;
   - los nombres son trazables.

Resultado esperado:

- Pipeline productivo validado.
- Si algo falla, se corrige antes de lanzar campana grande.

## Fase 6: Campana parametrica principal

Objetivo: generar el dataset base de la tesis.

Acciones:

1. Lanzar tandas controladas, no todo de una.
2. Monitorear fallos.
3. Guardar resultados por tanda.
4. Consolidar CSV/SQLite.
5. Marcar casos fallidos como fallo numerico, no fisico.
6. Mantener logs.

Resultado esperado:

- Dataset principal de simulaciones SPH.

## Fase 7: Modelo sustituto / surrogate

Objetivo: aproximar la respuesta del sistema sin correr infinitas simulaciones.

Acciones:

1. Entrenar modelos para:
   - desplazamiento maximo;
   - margen al umbral;
   - probabilidad de falla o clase.
2. Probar modelos simples primero:
   - random forest;
   - gradient boosting;
   - Gaussian process si el dataset es pequeno;
   - regresion logistica para frontera.
3. Validar con train/test o cross-validation.
4. Identificar regiones de incertidumbre.

Resultado esperado:

- Modelo predictivo de estabilidad del bloque.
- Frontera de falla estimada en espacio parametrico.

## Fase 8: Active learning

Objetivo: elegir nuevas simulaciones donde mas aporten.

Acciones:

1. Usar el surrogate para detectar zonas cerca de la frontera.
2. Proponer nuevos casos donde:
   - la incertidumbre sea alta;
   - el margen al umbral sea cercano a cero;
   - haya contradicciones entre modelos.
3. Correr solo esos casos nuevos.
4. Actualizar dataset y surrogate.

Resultado esperado:

- Mejor frontera con menos simulaciones.

## Fase 9: Sensibilidad y fragilidad

Objetivo: responder que variables controlan mas el movimiento.

Acciones:

1. Calcular importancia de variables.
2. Hacer analisis de sensibilidad:
   - global;
   - local cerca del umbral;
   - por escenarios hidraulicos.
3. Construir curvas o mapas de fragilidad:
   - probabilidad de movimiento vs altura de flujo;
   - probabilidad de movimiento vs friccion;
   - efecto de masa y orientacion.

Resultado esperado:

- Jerarquia de variables.
- Curvas de fragilidad defendibles.

## Fase 10: Comparacion con formulas analiticas

Objetivo: conectar la simulacion SPH con criterios clasicos.

Acciones:

1. Calcular umbrales con formulas tipo Nott/Nandasena u otras.
2. Comparar:
   - prediccion analitica;
   - resultado SPH;
   - diferencias por geometria irregular;
   - rol de rotacion/desplazamiento.
3. Discutir limites de ambos enfoques.

Resultado esperado:

- Capitulo comparativo.
- Aporte de usar SPH frente a criterios simplificados.

## Orden inmediato recomendado

No lanzar campana grande todavia. Orden inmediato:

1. Cerrar convergencia con figuras actualizadas.
2. Crear documento de configuracion productiva.
3. Revisar que script existe para campana parametrica.
4. Disenar mini piloto de 3 a 5 casos.
5. Solo despues lanzar la primera tanda productiva.
