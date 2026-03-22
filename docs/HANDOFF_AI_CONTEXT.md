# HANDOFF_AI_CONTEXT.md

Documento maestro para traspasar este proyecto a otra IA sin perder contexto tecnico, cientifico ni operativo.

Actualizado al: 2026-03-11
Workspace auditado: `C:\Seba\Tesis`

## 1. Que es este proyecto

`SPH-IncipientMotion` es una tesis de Ingenieria Civil UCN 2026 para determinar umbrales criticos de movimiento de bloques costeros bajo flujos tipo tsunami usando:

- DualSPHysics v5.4.x
- acoplamiento Chrono (`RigidAlgorithm=3`)
- pipeline Python de generacion de casos, corrida batch, ETL y surrogate modeling

Objetivo final:
- generar una relacion util entre parametros hidraulicos/geometricos y movimiento del boulder
- evitar simular exhaustivamente cada combinacion usando un surrogate posterior

## 2. Estado real del proyecto al 11 de marzo de 2026

### Lo que esta implementado

El pipeline base SI esta implementado:

- `src/geometry_builder.py`
  - lee STL con `trimesh`
  - calcula volumen, centro de masa, bbox e inercia
  - modifica XML de DualSPHysics
  - inyecta `massbody`, `center`, `inertia`, `fillbox`, `FtPause`

- `src/batch_runner.py`
  - corre `GenCase` y `DualSPHysics`
  - verifica CSVs de salida
  - copia outputs a `data/processed`
  - limpia binarios en `finally`

- `src/data_cleaner.py`
  - parsea `ChronoExchange`, `ChronoBody_forces`, `GaugesVel`, `GaugesMaxZ`
  - calcula desplazamiento, rotacion, velocidad, fuerzas, gauge mas cercano
  - decide falla/estabilidad
  - guarda resultados en SQLite

- `src/main_orchestrator.py`
  - genera o lee matriz LHS
  - ejecuta el pipeline completo por caso

- `src/ml_surrogate.py`
  - entrena un Gaussian Process
  - genera figuras
  - exporta `gp_surrogate.pkl`

### Lo que existe como soporte adicional

- scripts de convergencia formal
- scripts de produccion para workstation
- scripts de UQ
- scripts de render y visualizacion
- 5 capitulos de tesis ya escritos

## 3. La distincion critica: estado local vs estado de workstation

Este es el punto mas importante para otra IA.

### Localmente en este repo hay

- `config/template_base.xml` ya actualizado a canal de **30 m**
- 5 casos LHS locales (`lhs_001` a `lhs_005`)
- 1 caso `test_diego_reference`
- `data/processed/` con 6 carpetas locales
- `data/results_ws_15cases.csv` con 15 resultados historicos
- `data/results.sqlite` vacio

### Lo que NO esta sincronizado localmente

La campana reiniciada en workstation el **28 de febrero de 2026** con canal de 30 m no esta consolidada en este workspace.

Implicacion:
- no se puede inferir desde este repo cuantos casos de 30 m terminaron realmente
- no se puede asumir que el GP/UQ actual representa el estado final de la tesis
- no se puede asumir que `results.sqlite` local sea la base maestra

## 4. Hechos tecnicos confirmados

### Motor y estrategia numerica

- DualSPHysics estable: 5.4.x
- No usar beta 6.0
- Integracion rigida con Chrono: `RigidAlgorithm=3`
- Los CSVs principales salen automaticamente durante la simulacion
- `FloatingInfo` y `ComputeForces` no son la fuente principal del pipeline final

### Correcciones fisicas obligatorias

Estas decisiones ya estan incorporadas en el proyecto y no deben revertirse:

1. `massbody` en vez de `rhopbody`
2. inercia del boulder desde `trimesh`
3. `FtPause >= 0.5`
4. `fillbox void` para rellenar el STL
5. usar Chrono como base del movimiento rigid body

### Propiedades del STL base `BLIR3.stl`

Verificadas localmente con `geometry_builder.py`:

- volumen: `0.00053023 m^3`
- densidad implicita del caso Diego corregido: ~`2000 kg/m^3`
- diametro equivalente: `0.100421 m`
- bounding box escalado (`scale=0.04`):
  - `0.1710 x 0.2100 x 0.0399 m`

## 5. Que documentos siguen siendo validos

### Muy vigentes

- `AGENTS.md`
- `RETOMAR.md`
- `AUDITORIA_FISICA.md`
- `EDUCACION_TECNICA.md`
- `DEFENSA_TECNICA.md`
- `src/*.py`
- `config/template_base.xml`
- `config/param_ranges.json`

### Vigentes pero historicos/parciales

- `BRIEFING_LEAD_ARCHITECT.md`
- `data/results_ws_15cases.csv`
- `cases/lhs_001` a `lhs_005`
- `data/processed/lhs_001` a `lhs_005`

### No usar como unico estado actual

- `PLAN.md`
  - bueno para marco conceptual
  - no representa el estado operativo actual por si solo

- `data/results.sqlite`
  - hoy esta vacio en este workspace

- `data/gp_surrogate.pkl`
  - revisar con cautela; no asumir automaticamente que fue entrenado solo con datos reales reconciliados

## 6. Estado cientifico de los resultados

### Convergencia

Segun los documentos operativos del proyecto:

- el estudio de convergencia ya se considera cerrado
- la resolucion de produccion es `dp=0.004`
- `dp=0.01` se usa como resolucion mas liviana para render
- la fuerza de contacto no converge bien y no debe usarse como criterio principal

### Screening LHS

Existe una matriz de 50 casos en `config/experiment_matrix.csv` con variables:

- `dam_height`
- `boulder_mass`
- `boulder_rot_z`

De esos, localmente solo hay trazas claras de:

- 5 casos LHS locales completos en `cases/` y `data/processed/`
- 15 resultados historicos de workstation en `data/results_ws_15cases.csv`

Los 15 resultados historicos indican:

- todos los casos movieron
- `dam_height` domina
- `mass` tiene efecto menor
- `rot_z` tiene efecto casi nulo

Pero esos 15 casos corresponden al canal de 15 m, antes de corregir la saturacion por fin de dominio.

## 7. Trampas frecuentes para otra IA

1. Confundir la plantilla actual de 30 m con los casos guardados de 15 m.
2. Leer `PLAN.md` y creer que el proyecto sigue en pre-implementacion.
3. Tomar `results.sqlite` local como base maestra.
4. Creer que el GP/UQ actual ya es definitivo para la tesis.
5. Ignorar que el repositorio tiene worktree sucio y archivos nuevos no trackeados.

## 8. Estado del worktree

Durante la auditoria se observo worktree sucio. Habia, al menos:

- archivos modificados:
  - `RETOMAR.md`
  - `scripts/blender_render.py`
  - `tesis/cap2_marco_teorico.md`

- archivos o carpetas no trackeados:
  - `AGENTS.md`
  - `BRIEFING_LEAD_ARCHITECT.md`
  - `ENTREGA_KEVIN/`
  - `cases/`
  - varias carpetas de `data/figuras_*`
  - algunos scripts auxiliares

Implicacion:
- no asumir repositorio limpio
- no resetear ni revertir sin confirmacion explicita

## 9. Si la otra IA va a escribir codigo

Debe cargar como minimo:

1. `AGENTS.md`
2. `AUDITORIA_FISICA.md`
3. `HANDOFF_AI_CONTEXT.md`
4. `RETOMAR.md`
5. `src/*.py`
6. `config/template_base.xml`
7. `config/param_ranges.json`

Y debe asumir:

- Chrono manda
- no se usan APIs Python de DualSPHysics
- toda la integracion es CLI
- el estado local no equivale al estado completo de workstation

## 10. Si la otra IA va a escribir tesis o informe

Debe cargar ademas:

- `tesis/cap1_introduccion.md`
- `tesis/cap2_marco_teorico.md`
- `tesis/cap3_metodologia.md`
- `tesis/cap4_resultados_convergencia.md`
- `tesis/cap5_pipeline.md`
- `DEFENSA_TECNICA.md`

Y debe entender que:

- los capitulos 6 y 7 siguen pendientes o dependen de resultados reconciliados
- no conviene redactar conclusiones finales sin resolver el estado de la campana 30 m

## 11. Proximo trabajo recomendado

### Si el objetivo es cerrar la tesis

1. Recuperar el estado real de la workstation.
2. Reconstruir una base consolidada de resultados reales.
3. Regenerar `results.sqlite`.
4. Reentrenar GP/UQ con datos reales suficientes.
5. Escribir caps 6 y 7.

### Si el objetivo es mantener el software

1. Normalizar y versionar mejor el handoff.
2. Separar claramente datos historicos 15 m vs campana 30 m.
3. Agregar validaciones para evitar usar artefactos viejos como si fueran actuales.
4. Consolidar un README tecnico reproducible.

## 12. Resumen ejecutivo para otra IA

Este proyecto ya tiene:

- pipeline implementado
- base fisica razonablemente bien corregida
- resultados parciales
- tesis avanzada

Pero el repo local esta desalineado respecto a la campana productiva mas reciente. La prioridad para trabajo serio no es reinventar el pipeline, sino reconciliar el estado local con la workstation y separar claramente:

- diseno
- implementacion
- resultados historicos
- resultados vigentes
