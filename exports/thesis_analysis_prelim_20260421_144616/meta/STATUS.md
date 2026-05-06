# STATUS — Thesis OS

**Última actualización:** 2026-04-08 (sesión 10)

## Estado general
Activo — Convergencia dp v2 completada; criterio final de dp aún abierto.

## Fase actual
Fase 3 — Interpretar convergencia nueva → decidir criterio de dp con Moris → Round 3 / v3 focalizada si hace falta.

## Qué está listo
- Pipeline 5D verificado con canal paramétrico
- Screening R1 completo (24/25 dp=0.005) + análisis
- Screening R2 completo (15/15 dp=0.004) + análisis profundo
- R2 hallazgos: fricción domina, masa segunda, frontera multidimensional
- Round 3 diseñado (10 casos, `config/screening_round3.csv`)
- Convergencia v2 corrida: 7/8 dp exitosos, `dp=0.0015` falló en GenCase
- Datos completos v2 importados (`convergencia_v2.csv`, `convergencia_v2_gci.json`, temporales, log)
- Diagnóstico técnico preliminar: forcing y onset convergen mejor que la trayectoria post-falla

## Qué falta
- **Definir criterio de convergencia válido para la tesis** (onset vs trayectoria completa)
- **Elegir dp producción** en la configuración nueva
- **Reunión con Moris** para cerrar enfoque metodológico
- **Round 3** o convergencia v3 focalizada, según lo que pida el profe
- Diseñar LHS 5D (o 4D si rot_z no importa tras R3)
- Campaña producción + AL loop
- Cap 6 con resultados paramétricos

## Riesgos activos
- El caso Moris `dam_h=0.30` puede no ser el caso correcto para decidir dp si la pregunta científica es incipient motion
- `SPH force` pico y `max_rotation` actual no son métricas robustas para convergencia fina
- `dp=0.002` es muy costoso (~34 h) y `dp=0.0015` parece exceder límites prácticos
- Persistencia inconsistente: el log reporta guardado en `convergence_v2`, pero la `results.sqlite` local no muestra esa tabla

## Próximo hito
Reunión con Moris → criterio metodológico claro → decisión: extraer onset de v2 o correr v3 cerca de la frontera.
