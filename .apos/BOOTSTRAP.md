# BOOTSTRAP — Thesis OS

**Versión:** 1.0
**Última actualización:** 2026-04-08
**Ubicación:** `C:\Seba\tesis\.apos\` (governance viaja con el proyecto)
**Governance global:** `C:\Seba\seba_os\meta\`

---

## IDENTIDAD DEL PROYECTO

Tesis UCN 2026 — simulación SPH de movimiento incipiente de bloques costeros bajo flujos tipo tsunami. DualSPHysics + Chrono + GP surrogate con active learning.

Ver `PROJECT_BRIEF.md` para detalle completo.

---

## TIER ACTIVO

Tier 3 (continuidad fuerte, handoff explícito, decisiones trazables).

---

## ESTADO ACTUAL

**Fase:** Fase 3 — Convergencia dp nueva completada, pero criterio final de dp aún abierto.

**Progreso real:**
- Pipeline **5D** verificado con canal paramétrico
- Screening R1 **completo** (24/25 dp=0.005)
- Screening R2 **completo** (15/15 dp=0.004) con análisis profundo
- Convergencia anterior válida para Fase 2, pero **no transferible** al setup actual 5D
- Convergencia v2 corrida con 7/8 dp exitosos; `dp=0.0015` falló en GenCase
- Resultado clave: **forcing y onset convergen mejor que la trayectoria post-falla**
- Round 3 diseñado, pero en espera hasta definir criterio y dp

**Bloqueado:** No, pero la decisión de `dp` sigue metodológicamente abierta.
**Riesgo:** estar mezclando una pregunta de incipient motion con una métrica post-falla a 10 s.

---

## SIGUIENTE ACCIÓN

1. **Hablar con Moris** y cerrar esto:
   - ¿el `dp` debe justificarse con onset/incidental motion o con trayectoria completa?
   - ¿quiere un chequeo cerca de la frontera ESTABLE/FALLO?
2. **Según esa respuesta:**
   - extraer métricas de onset de la convergencia v2 ya corrida, o
   - diseñar/correr una convergencia v3 corta en 1–2 casos de frontera
3. **Luego** elegir `dp` producción
4. **Después** lanzar Round 3 o ajustar su diseño

---

## ARCHIVOS QUE DEBES LEER AHORA

Leer en orden, detenerse cuando haya contexto suficiente:

1. **Este `BOOTSTRAP.md`**
2. **`HANDOFF.md`**
3. **`STATUS.md`**
4. **`DECISIONS.md`**
5. **`WORKING_MODEL.md`**
6. **`data/results/convergencia_v2.csv`**
7. **`data/logs/convergencia_v2.log`**
8. **`data/figures/convergencia_v2_analisis.md`**

Si vas a tocar **código:**
9. **`../CLAUDE.md`**
10. **`../src/*.py`**

---

## WARNINGS / CONTEXTO CRÍTICO

1. **No asumir que la convergencia anterior sirve para el setup actual.** La física/configuración cambió.
2. **No interpretar `max_rotation` actual como ángulo neto.** En `data_cleaner.py` integra `|omega|`.
3. **No vender `dp=0.003` como cerrado** antes de hablar con Moris o al menos fijar el criterio de convergencia.
4. **El worktree sigue sucio.** No resetear sin confirmación.
5. **Hay inconsistencia en SQLite:** el log v2 dice que guardó en `convergence_v2`, pero la base local no muestra esa tabla.
