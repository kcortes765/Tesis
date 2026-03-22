# BOOTSTRAP — Thesis OS

**Versión:** 1.0
**Última actualización:** 2026-03-20
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

**Fase:** Fase 3 en ejecución. GP+AL implementado y verificado. Listo para producción en WS.

**Progreso real:**
- Pipeline completo y **verificado end-to-end** en laptop (7 módulos en src/)
- Convergencia CERRADA: dp=0.004 producción
- GP+AL implementado: src/gp_active_learning.py (Matérn 5/2, U-function, LOO Q2=0.92)
- Sanity checks: src/sanity_checks.py (5 checks, todos PASS con datos reales)
- SQLite: 6 resultados reales (5 validación dp=0.02 + 1 referencia)
- Figuras GP generadas: data/figures/gp/ (6 PNG+PDF)
- Batch producción diseñado: 20 casos LHS (config/gp_initial_batch.csv)
- Deploy script: scripts/deploy_ws.py (creado, no ejecutado)
- Cap 3 expandido: 647 líneas con GP+AL
- Research persistido en docs/RESEARCH_*.md
- Sistema autónomo probado: agente.ps1 -All (8/8 features)

**Bloqueado:** No.
**Riesgo:** Deploy a WS pendiente. Resultados actuales son dp=0.02 (dev).

---

## SIGUIENTE ACCIÓN

1. **Deploy a WS**: `python scripts/deploy_ws.py` → copiar ZIP a WS UCN
2. **Lanzar batch producción**: 20 casos dp=0.004 en RTX 5090
3. **Recolectar resultados** → SQLite local
4. **Re-entrenar GP** con 20+ puntos → LOO, Sobol, figuras
5. **AL loop**: proponer puntos → simular → repetir hasta U_min >= 2.0
6. **Cap 6**: resultados paramétricos con figuras finales

---

## ARCHIVOS QUE DEBES LEER AHORA

Leer en orden, detenerse cuando haya contexto suficiente:

1. **Este `BOOTSTRAP.md`** — entrada al sistema
2. **`HANDOFF.md`** — estado exacto de la última sesión
3. **`STATUS.md`** — estado operativo
4. **`PLAN.md`** — fases y prioridades
5. **`DECISIONS.md`** — decisiones técnicas acumuladas (no revertir sin registrar)
6. **`WORKING_MODEL.md`** — comprensión vigente y tensiones

Si vas a tocar **código:**
7. **`../CLAUDE.md`** — reglas técnicas del proyecto, arquitectura del pipeline, XML reference
8. **`../src/*.py`** — fuente de verdad de implementación

Si vas a tocar **la tesis:**
9. **`../tesis/cap1_*.md` a `cap5_*.md`**
10. **`../docs/DEFENSA_TECNICA.md`**

Si necesitas **marco científico profundo:**
11. **`../docs/AUDITORIA_FISICA.md`** — correcciones físicas obligatorias
12. **`../docs/EDUCACION_TECNICA.md`** — SPH, Chrono, DualSPHysics en detalle

### Referencia histórica (no usar como estado actual)
- `docs/PLAN_MAESTRO.md` — plan original extenso (marco conceptual, no estado operativo)
- `docs/HANDOFF_AI_CONTEXT.md` — handoff pre-APOS (supersedido por este sistema)
- `docs/CONTEXT_BASE_FILES.md` — orden de carga pre-APOS (supersedido)
- `docs/BRIEFING_LEAD_ARCHITECT.md` — briefing estratégico feb 2026

---

## ESTRUCTURA DEL REPO

```
C:\Seba\tesis\
├── .apos/              # Governance APOS (este sistema)
├── CLAUDE.md           # Reglas técnicas para Claude Code
├── RETOMAR.md          # Resumen ejecutivo rápido (puntero a .apos/)
├── src/                # Pipeline (7 módulos) — NO TOCAR sin leer CLAUDE.md
├── config/             # template_base.xml, param_ranges.json, experiment_matrix.csv
├── cases/              # Casos LHS locales (5 + 1 referencia)
├── models/             # STLs (BLIR3.stl, canales)
├── data/
│   ├── processed/      # CSVs limpios por caso
│   ├── results/        # CSVs consolidados de resultados
│   ├── figures/        # Figuras generadas (convergencia, ML, UQ, etc.)
│   ├── renders/        # Renders 3D (Blender)
│   ├── logs/           # Logs de producción y monitoreo
│   ├── results.sqlite  # Base maestra (6 filas: 5 validación + 1 referencia)
│   └── gp_surrogate.pkl # GP entrenado (revisar con cautela)
├── tesis/              # Capítulos 1-5 en markdown
├── scripts/            # Scripts auxiliares (análisis, render, producción)
├── docs/               # Documentación de referencia (archivada desde raíz)
├── archive/            # Material legacy (ENTREGA_KEVIN, Tesis_v2, .agente/)
└── .venv-gnn/          # Virtualenv para GNN
```

---

## ARCHIVOS QUE NO DEBES TOCAR SIN PERMISO

- `CLAUDE.md` (instrucciones canónicas del proyecto)
- `docs/AUDITORIA_FISICA.md` (correcciones físicas validadas)
- Decisiones vigentes en `DECISIONS.md` (no revertir, solo superseder)
- `config/template_base.xml` (plantilla validada)

Sí puedes modificar:
- Archivos `.apos/` (siguiendo protocolo)
- `src/*.py` (con justificación técnica)
- `scripts/*.py`
- `data/` (generación de resultados)
- `tesis/` (redacción)

---

## WARNINGS / CONTEXTO CRÍTICO

1. **`data/results.sqlite` tiene 6 filas** (5 validación dp=0.02 + 1 referencia). Producción dp=0.004 pendiente.
2. **`data/gp_surrogate.pkl`** fue generado con soporte sintético en algún punto. No tratar como resultado final.
3. **Los 15 casos en `data/results/results_ws_15cases.csv`** son de canal 15m (pre-extensión). Incluyen anomalía de saturación a 6.4m.
4. **El worktree git está sucio.** No resetear sin confirmación.
5. **La campaña real corre en WS remota.** Este repo local no refleja el progreso real post-28 feb.
6. **Cowork Windows:** solo accede a C:\Users\kevin\. Migración con reverse junction preparada pero NO ejecutada.
7. **Notificaciones push:** implementadas y funcionando via `seba_os/scripts/notifier.py` + ntfy.sh.
8. **Research de agentes → persistir a disco.** Outputs de agentes background son efímeros. Si un agente genera research valioso, debe escribir a `docs/RESEARCH_*.md` directamente. Verificar en `/guardar` que no queden hallazgos solo en tasks.
