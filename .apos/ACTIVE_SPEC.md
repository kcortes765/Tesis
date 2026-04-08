# ACTIVE_SPEC — Thesis OS

## Tarea activa
Cerrar el criterio metodológico de convergencia y decidir cómo justificar el `dp` de producción en la configuración 5D actual.

## Entregables esperados
1. Resumen técnico corto para Moris:
   - por qué la convergencia nueva difiere de la anterior
   - qué sí converge
   - qué no converge
   - qué opciones hay
2. Criterio claro de decisión:
   - onset / incipient motion, o
   - trayectoria completa post-falla
3. Ruta elegida:
   - justificar `dp=0.003` con la v2 existente, o
   - definir una v3 corta cerca de la frontera
4. Deuda técnica identificada:
   - SQLite `convergence_v2`
   - trazabilidad de la convergencia original

## Criterios de aceptación
- Se puede explicar en 1 minuto por qué la convergencia nueva y la vieja no son equivalentes
- Se puede responder qué observable define el `dp`
- Existe una siguiente acción inequívoca después de la reunión con Moris

## Pre-requisito
Tener a mano:
- `data/results/convergencia_v2.csv`
- `data/logs/convergencia_v2.log`
- `data/figures/convergencia_v2_analisis.md`
- `.apos/DECISIONS.md`

## No incluido
- Correr aún la v3 de convergencia
- Lanzar Round 3
- Redactar Cap 6
