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

**Fase:** Fase 3 — Convergencia dp nueva lista para WS → Round 3 → Producción 5D.

**Progreso real:**
- Pipeline **5D** verificado con canal paramétrico
- Screening R1 **completo** (24/25 dp=0.005): dominio ok, TimeMax ok, sin reflexión
- Screening R2 **completo** (15/15 dp=0.004): fricción domina (rho=-0.92), frontera multidimensional
- Convergencia anterior descartada (configuración cambió). **Nueva convergencia preparada.**
- Round 3 diseñado (10 casos) pero **en espera** hasta dp convergido
- Script convergencia v2 validado y pusheado

**Bloqueado:** No. WS libre para lanzar convergencia.
**Riesgo:** dp=0.0015/0.001 probablemente no caben en VRAM 32GB.

---

## SIGUIENTE ACCIÓN

1. **Lanzar convergencia dp v2 en WS** (`python scripts/run_convergence_v2.py`)
2. **Analizar convergencia**: GCI/Richardson → elegir dp producción
3. **Lanzar Round 3** al dp convergido (10 casos verificación)
4. **Analizar Round 3**: decidir 4D o 5D para producción
5. **Diseñar LHS 5D** (o 4D) → **campaña producción** al dp convergido
6. **AL loop**: proponer puntos → simular → repetir hasta convergencia GP
7. **Cap 6**: resultados paramétricos con figuras finales

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
