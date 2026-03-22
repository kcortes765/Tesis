# CLAUDE.md — SPH-IncipientMotion

## Continuidad

Este proyecto usa **APOS** para governance. Leer `.apos/BOOTSTRAP.md` primero.

## Project Overview

**SPH-IncipientMotion** — Tesis UCN 2026: umbrales críticos de movimiento de bloques costeros bajo flujos tipo tsunami usando SPH (DualSPHysics v5.4 + Chrono) + GP surrogate con active learning.

100% simulación numérica — no hay laboratorio físico.

## Estructura del repo

```
tesis/
├── .apos/              # Governance APOS (BOOTSTRAP, STATUS, PLAN, DECISIONS, etc.)
├── CLAUDE.md           # Este archivo — reglas técnicas
├── RETOMAR.md          # Puntero rápido a .apos/
├── src/                # Pipeline (NO TOCAR sin leer reglas abajo)
│   ├── geometry_builder.py   # STL + XML → caso paramétrico
│   ├── batch_runner.py       # GenCase → DualSPHysics → cleanup
│   ├── data_cleaner.py       # ChronoExchange CSV → métricas → SQLite
│   ├── main_orchestrator.py  # LHS matrix → loop completo
│   ├── ml_surrogate.py       # GP regression (legacy)
│   ├── gp_active_learning.py # GP Matérn 5/2 + U-function + AL loop
│   └── sanity_checks.py      # Validación física automática
├── config/
│   ├── template_base.xml     # Plantilla DualSPHysics (canal 30m)
│   ├── param_ranges.json     # Rangos corregidos para screening
│   ├── experiment_matrix.csv # Matriz LHS 50 casos
│   └── dsph_config.json      # Rutas ejecutables y defaults
├── cases/              # Casos LHS locales (5 + 1 referencia)
├── models/             # STLs (BLIR3.stl, canales)
├── data/
│   ├── processed/      # CSVs limpios por caso
│   ├── results/        # CSVs consolidados
│   ├── figures/        # Figuras generadas
│   ├── renders/        # Renders 3D (Blender)
│   ├── logs/           # Logs de producción
│   ├── results.sqlite  # Base maestra (6 filas: 5 validación + 1 referencia)
│   └── gp_surrogate.pkl  # Legacy — usar src/gp_active_learning.py
├── tesis/              # Capítulos 1-5 en markdown
├── scripts/            # Scripts auxiliares (deploy_ws.py, etc.)
├── docs/               # Referencia + research (RESEARCH_GP_AL.md, RESEARCH_EMPIRICAL_SANITY.md, etc.)
└── archive/            # Legacy (ENTREGA_KEVIN, Tesis_v2, .agente)
```

## Development Environment

**Python 3.10+.** Dependencias:
```bash
pip install numpy pandas trimesh lxml scipy sqlalchemy scikit-learn matplotlib
```

**Motor:** DualSPHysics **v5.4.355** + GenCase **v5.4.354.01**. **NO usar v6.0 beta.**
Interacción 100% CLI via `subprocess.run()`. No hay API Python nativa.

**Chrono (RigidAlgorithm=3):** obligatorio. Maneja dinámica rígida, colisiones, fricción. Genera CSVs automáticamente. **FloatingInfo y ComputeForces NO se usan.**

### Ejecutables clave
- `GenCase_win64.exe` — XML → partículas (.bi4)
- `DualSPHysics5.4_win64.exe` — solver SPH+GPU+Chrono

### Fuentes de datos primarias (generadas por Chrono)
- `ChronoExchange_mkbound_51.csv` — cinemática del boulder (separador: `;`)
- `ChronoBody_forces.csv` — fuerzas SPH + contacto (separador: `;`)
- `GaugesVel_V**.csv` — velocidad del flujo (separador: `;`)
- `GaugesMaxZ_hmax**.csv` — altura máxima del agua (separador: `;`)

### Hardware
- **WS UCN:** i9-14900KF + RTX 5090 32GB (sims 24/7)
- **Laptop:** i7-14650HX + RTX 4060 8GB (ML, desarrollo)

## Correcciones físicas obligatorias

Estas decisiones están incorporadas y **no deben revertirse** (ver `.apos/DECISIONS.md`):

1. **`massbody`** en vez de `rhopbody` — discretización introduce errores de volumen
2. **Inercia desde `trimesh`** — GenCase sobreestima 2-3x a dp grueso
3. **`FtPause >= 0.5`** — settling gravitacional antes de impacto
4. **`fillbox void`** para rellenar STL — `drawfilestl` solo crea superficie
5. **dp=0.004** producción, **dp=0.01** render
6. **Contact force NO criterio** — CV=82%, no converge
7. **Chrono (RigidAlgorithm=3)** — no usar floating bodies básicos

## Reglas de diseño

1. **No hardcoded XML** — variaciones inyectadas via `lxml` desde template
2. **Hollow shell fix obligatorio** — todo STL necesita `fillbox void` + `massbody`
3. **Criterio de falla algorítmico** — Python lee CSV, aplica umbrales numéricos
4. **Sin Excel** — DualSPHysics → Pandas → SQLite
5. **Disk cleanup en `try/finally`** — 10M partículas ≈ 64 GB por sim
6. **ChronoExchange es la fuente** — no FloatingInfo

## CSV format (DualSPHysics Chrono + Gauges)

- Separador: **`;`** (hardcoded, -csvsep:1 no aplica a Chrono)
- Decimal: **`.`**
- Headers con unidades: `time [s]`, `fvel.x [m/s]`, etc.
- Sentinel `-3.40282e+38` en Gauges = no data → reemplazar con NaN
- Leer con: `pd.read_csv(path, sep=';')`

## XML Structure Reference

```xml
<case>
  <casedef>
    <constantsdef>
      <gravity x="0" y="0" z="-9.81" />
      <rhop0 value="1000" />
      <cflnumber value="0.2" />
      <coefh value="0.75" />
    </constantsdef>
    <mkconfig boundcount="240" fluidcount="10" />
    <geometry>
      <definition dp="0.004">
        <pointmin x="..." y="..." z="..." />
        <pointmax x="..." y="..." z="..." />
      </definition>
      <commands>
        <mainlist>
          <setmkbound mk="0" />
          <drawbox>...</drawbox>
          <setmkfluid mk="0" />
          <fillbox>...</fillbox>
          <setmkbound mk="1" />
          <drawfilestl file="boulder.stl">
            <drawscale /><drawmove /><drawrotate />
          </drawfilestl>
          <fillbox><modefill>void</modefill>...</fillbox>
        </mainlist>
      </commands>
    </geometry>
    <floatings>
      <floating mkbound="1">
        <massbody value="150.0" />
        <center x="cx" y="cy" z="cz" />
        <inertia>
          <values v11="Ixx" v12="0" v13="0" />
          <values v21="0" v22="Iyy" v23="0" />
          <values v31="0" v32="0" v33="Izz" />
        </inertia>
      </floating>
    </floatings>
  </casedef>
  <execution>
    <parameters>
      <parameter key="RigidAlgorithm" value="3" />
      <parameter key="FtPause" value="0.5" />
      <!-- ... -->
    </parameters>
  </execution>
</case>
```

## DualSPHysics CLI flags

- `-gpu[:id]` — modo GPU
- `-symplectic` — integración temporal
- `-wendland` — kernel (preferido para floating bodies)
- `-viscoart:0.05` — viscosidad artificial (Visco=0.05 en template)
- `-deltasph:0.1` — difusión de densidad
- `-posdouble:1` — doble precisión posiciones
- `-partbegin:N dir` — restart desde checkpoint

## Documentación de referencia

Para contexto técnico y científico profundo, ver `docs/`:
- `AUDITORIA_FISICA.md` — correcciones físicas detalladas
- `EDUCACION_TECNICA.md` — marco técnico SPH/Chrono/DualSPHysics
- `DEFENSA_TECNICA.md` — argumento técnico para defensa
- `AGENTS.md` — restricciones y arquitectura (pre-APOS, referencia)
- `PLAN_MAESTRO.md` — plan original extenso
