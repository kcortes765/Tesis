# NOTIFICATIONS.md — SPH-IncipientMotion

**Ultima actualizacion:** 2026-03-20
**Topic:** sph-kevin-tesis-2026

---

## Configuracion

```yaml
topic: "sph-kevin-tesis-2026"
enabled: true
quiet_hours: true
```

---

## Eventos

### Simulacion y pipeline

- **sim_completed**
  - Trigger: DualSPHysics termina una simulacion individual
  - Priority: default
  - Tags: white_check_mark,ocean
  - Titulo: "Sim completada: {detail}"

- **batch_completed**
  - Trigger: Todos los casos del batch/campana terminaron
  - Priority: urgent
  - Tags: tada,rocket
  - Titulo: "BATCH COMPLETADO"

- **pipeline_error**
  - Trigger: Error no recuperable en pipeline (GenCase, solver, cleanup)
  - Priority: urgent
  - Tags: rotating_light,warning
  - Titulo: "ERROR PIPELINE: {detail}"

### ML / Surrogate

- **gp_converged**
  - Trigger: GP surrogate alcanza criterio de convergencia (U >= 2 en active learning)
  - Priority: high
  - Tags: chart_with_upwards_trend,brain
  - Titulo: "GP Convergido"

- **al_iteration_done**
  - Trigger: Active learning completa una iteracion (nueva sim + refit)
  - Priority: low
  - Tags: gear
  - Titulo: "AL iteracion {detail}"

### Sesion APOS

- **session_close**
  - Trigger: Protocolo de cierre APOS ejecutado (/guardar)
  - Priority: low
  - Tags: floppy_disk
  - Titulo: "Sesion guardada: tesis"

- **session_emergency**
  - Trigger: Cierre de emergencia por contexto lleno
  - Priority: high
  - Tags: warning
  - Titulo: "Cierre emergencia: tesis"

### Render y visualizacion

- **render_completed**
  - Trigger: Blender render completa (blender_render.py)
  - Priority: default
  - Tags: movie_camera
  - Titulo: "Render completado: {detail}"
