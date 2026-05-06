# DECISIONS — Thesis OS

Append-only. Si algo cambia, no se borra: se marca como revertido o supersedido.

---

## DEC-001: Chrono obligatorio
**Fecha:** 2026-02-20
**Decisión:** Usar RigidAlgorithm=3 (Chrono) para toda simulación. No usar floating bodies básicos de SPH.
**Razón:** Chrono maneja dinámica de cuerpo rígido, colisiones y fricción. Genera CSVs automáticamente.
**Implicación:** FloatingInfo y ComputeForces NO se usan.

## DEC-002: massbody > rhopbody
**Fecha:** 2026-02-20
**Decisión:** Siempre usar `<massbody>` (masa explícita en kg), nunca `<rhopbody>` (densidad).
**Razón:** La discretización de partículas introduce errores de volumen. Diego usaba densidad incorrecta (800 vs 2000 kg/m³).

## DEC-003: Inercia desde trimesh
**Fecha:** 2026-02-20
**Decisión:** Inyectar inercia calculada por trimesh, no la de GenCase.
**Razón:** GenCase sobreestima inercia 2-3x a dp grueso.

## DEC-004: FtPause >= 0.5
**Fecha:** 2026-02-20
**Decisión:** Siempre FtPause >= 0.5s.
**Razón:** Diego tenía 0.0 — sin settling gravitacional antes del impacto de ola.

## DEC-005: dp producción = 0.004
**Fecha:** 2026-02-21
**Decisión:** dp=0.004 para producción, dp=0.01 para render.
**Razón:** Convergencia alcanzada (delta <5% vs dp=0.003). dp=0.003 toma 812 min/caso sin mejora significativa.

## DEC-006: Contact force NO es criterio
**Fecha:** 2026-02-21
**Decisión:** No usar fuerza de contacto como criterio de falla.
**Razón:** CV=82%, no converge. Es hallazgo científico, no bug.

## DEC-007: GP para tesis, GNN para papers
**Fecha:** 2026-02-25
**Decisión:** GP (datos tabulares → resultado escalar) para la tesis. GNN (simulación completa partícula por partícula) para papers posteriores.
**Razón:** Complementarios. GP responde "qué resultado"; GNN predice "la simulación completa".

## DEC-008: SPH para costas, MPM para tailings
**Fecha:** 2026-02-25
**Decisión:** DualSPHysics para boulders costeros. CB-Geo MPM para tailings (Paper 2).
**Razón:** Mejor herramienta para cada problema. MPM es estándar en geotecnia para licuefacción.

## DEC-009: Transfer Learning es bonus
**Fecha:** 2026-02-25
**Decisión:** TL SPH→MPM es hipótesis no probada. Paper 2 se sostiene con Diff-GNS solo.
**Razón:** Si TL funciona, paper sube de nivel. Si no, Diff-GNS inverso ya está validado (Kumar).

## DEC-010: Entrenamiento GNN incremental
**Fecha:** 2026-02-25
**Decisión:** Empezar GNN con 5 casos, no esperar 50.
**Razón:** Adaptive sampling > batch. Cada caso nuevo se agrega al training.

## DEC-011: 50+50 adaptive sampling
**Fecha:** 2026-02-25
**Decisión:** Analizar primeros 50 casos, diseñar siguientes 50 concentrados en zona de transición.
**Razón:** Active learning natural con GP varianza.

## DEC-012: Canal extendido a 30m
**Fecha:** 2026-02-28
**Decisión:** Canal extendido de 15m a 30m. Campaña reiniciada desde cero.
**Razón:** Saturación detectada a 6.4m por fin de dominio en canal de 15m.

## DEC-013: No v6.0 beta
**Fecha:** 2026-02-20
**Decisión:** Mantenerse en DualSPHysics v5.4.x estable.
**Razón:** Estabilidad para la tesis. v6.0 beta existe pero no está validada.

## DEC-014: fillbox void obligatorio
**Fecha:** 2026-02-20
**Decisión:** Todo STL necesita `fillbox void` + `massbody`.
**Razón:** `drawfilestl` solo crea partículas de superficie. `autofill="true"` es unreliable para geometría compleja.

## DEC-015: Disk cleanup en try/finally
**Fecha:** 2026-02-20
**Decisión:** Limpieza de .bi4/.vtk siempre en try/finally.
**Razón:** 10M partículas pueden generar ~64 GB por simulación.

## DEC-016: Governance distribuida
**Fecha:** 2026-03-19
**Decisión:** .apos/ viaja con el proyecto (C:\Seba\tesis\.apos\). seba_os/tesis/ es solo POINTER.md.
**Razón:** Proyectos con repo propio llevan governance local.

## DEC-017: Reorganización de repo
**Fecha:** 2026-03-19
**Decisión:** docs/ para referencia, archive/ para legacy, data/ reorganizado en subdirectorios.
**Razón:** Raíz tenía 12 markdowns sueltos mezclando contextos. data/ era cajón de sastre.

## DEC-018: dp=0.003 es límite de hardware
**Fecha:** 2026-03-20
**Decisión:** dp=0.003 es la referencia más fina alcanzable. dp=0.004 producción. No se baja más.
**Razón:** dp=0.0025 requiere ~107M partículas (~40 GB VRAM), excede RTX 5090 (32 GB). Multi-resolución de v5.4 no compatible con Chrono floating bodies. Confirmado empíricamente: dp≈0.002 pegó la WS a 27h+. Correo enviado a Moris con justificación GCI + informe adjunto.

## DEC-019: Estrategia cambia de LHS-50 ciego a GP + Active Learning
**Fecha:** 2026-03-20
**Decisión:** No correr 50 casos LHS de una. Usar GP + active learning iterativo.
**Razón:** Campaña 50-LHS cancelada (solo 5 corridos). Active learning concentra cómputo en zona de umbral (~25-30 sims vs 50). Straddle heuristic o U-function (Echard 2011) para encontrar frontera de movimiento incipiente.

## DEC-020: Empezar en 2D (dam_h, mass), rot_z después
**Fecha:** 2026-03-20
**Decisión:** Fase inicial del GP usa solo dam_h y boulder_mass. Rotación se agrega después.
**Razón:** 2D es más eficiente (10d = 20 pts vs 30), visualizable, y rot_z tiene efecto secundario (~10%). El umbral en 2D es una curva; en 3D es una superficie más difícil de validar.

## DEC-021: Sanity check físico con batch inicial
**Fecha:** 2026-03-20
**Decisión:** Verificar tendencias físicas, magnitudes y curvas temporales antes de entrar al loop de active learning.
**Razón:** Validación de la otra IA (razonable): convergencia ≠ validación física. Checks: ↑dam_h→↑disp, ↑mass→↓disp, magnitudes vs Ritter/Nandasena, curvas suaves. Costo = 1 figura + 1 párrafo, protege contra "modelo funciona de casualidad".

## DEC-022: No reestructurar Seba OS para Cowork (aún)
**Fecha:** 2026-03-20
**Decisión:** Mantener arquitectura actual de Seba OS. APOS, ntfy.sh, tasks.json, calendar sync permanecen como están.
**Razón:** Cowork en Windows tiene bug de path (solo home dir, issue #24964). Sin fix no puede acceder a C:\Seba\. Además: APOS provee governance estructurada que Cowork memory no reemplaza; ntfy.sh es más confiable que las notificaciones de Cowork (inexistentes nativamente).
**Reevaluar cuando:** Anthropic arregle el path bug O se migre el repo con reverse junction.

## DEC-023: Migración Tesis con reverse junction (aprobada, no ejecutada)
**Fecha:** 2026-03-20
**Decisión:** Cuando se quiera usar Cowork con la tesis, mover archivos a C:\Users\kevin\projects\Tesis\ y crear junction C:\Seba\Tesis → allá.
**Razón:** fs.realpath() de Cowork resuelve symlinks/junctions al target. Si el target está en home dir, pasa validación. Junction inversa mantiene compatibilidad con todos los paths existentes.
**Estado:** Aprobada por Kevin, pendiente de ejecución.

## DEC-024: dsph_config.json con auto-detect de ejecutables
**Fecha:** 2026-03-21
**Decisión:** dsph_bin="auto" con lista de paths candidatos en dsph_bin_paths. batch_runner.load_config() resuelve automáticamente.
**Razón:** Permite usar el mismo config en laptop (C:\DualSPHysics_v5.4.3\...) y WS UCN (C:\Users\ProyBloq_Cortes\...) sin editar archivos.

## DEC-025: agente.ps1 -All para ejecución overnight autónoma
**Fecha:** 2026-03-21
**Decisión:** Usar agente.ps1 -All con feature_list.json + CONTEXT.md + coding_prompt.md para ejecutar features headless. Maneja rate limits automáticamente.
**Razón:** Probado 2026-03-21: 8/8 features completadas, 6 commits, rate limits manejados sin intervención. Features de código ~5 min, features con GPU toman horas por rate limits.

## DEC-026: APOS-auto staging para agente.ps1
**Fecha:** 2026-03-22
**Decisión:** agente.ps1 escribe a .apos-auto/ (staging) durante ejecución headless. Se promueve a .apos/ oficial solo con aprobación del usuario vía /guardar.
**Razón:** El agente headless no debe modificar governance oficial sin supervisión. Dos capas: auto (draft) y oficial (aprobado).

## DEC-027: Notifier integrado al repo Tesis
**Fecha:** 2026-03-22
**Decisión:** scripts/notifier.py + config/notifier_config.json viajan con el repo. No dependen de seba_os.
**Razón:** La WS UCN no tiene seba_os. El pipeline necesita notificaciones independientes. Config auto-detecta: repo config/ → seba_os fallback.

## DEC-028: WS UCN via Git (no ZIP)
**Fecha:** 2026-03-22
**Decisión:** Deploy a WS via git clone/pull, no ZIP/Copy-Item. Repo en C:\Users\Admin\Desktop\SPH-Tesis.
**Razón:** Git permite sync bidireccional laptop↔WS. Resultados viajan con git push/pull. El usuario Admin tiene Git + Python 3.10 instalados.

## DEC-029: dp producción = 0.003 (supersede DEC-005)
**Fecha:** 2026-03-25
**Decisión:** Producción cambia de dp=0.004 a dp=0.003. dp=0.01 para render se mantiene.
**Razón:** Con 2 semestres disponibles (precapstone + capstone) y WS RTX 5090 24/7, el costo extra (~13.5h/caso vs ~8h) es asumible. dp=0.003 es la resolución más fina alcanzable en hardware y ofrece mejor precisión para publicación. Convergencia monótona garantiza que dp=0.003 está convergido (delta vs dp=0.004 < 5%, delta vs dp=0.002 sería aún menor). Los 20 casos dp=0.004 ya corridos sirven como validación cruzada de convergencia.
**Supersede:** DEC-005 (dp=0.004 ya no es producción).

## DEC-030: Batch inicial 35 puntos (supersede 20)
**Fecha:** 2026-03-25
**Decisión:** Batch inicial LHS sube de 20 a 35 puntos (5 anclas + 30 LHS maximin).
**Razón:** Para paper, 20 puntos en 2D es el mínimo (10×d). 35 da GP más robusto desde el arranque, mejor estimación de Sobol, y reduce iteraciones AL necesarias. Con tiempo disponible, no hay razón para ser conservador.

## DEC-031: Plan orientado a publicación, no a aprobación
**Fecha:** 2026-03-25
**Decisión:** Todo el trabajo apunta a calidad de paper (Coastal Engineering / CMAME). La tesis es el vehículo, no el techo.
**Razón:** Kevin tiene 1 año completo, WS dedicada, y objetivo explícito de publicar. Las decisiones deben maximizar calidad científica, no minimizar esfuerzo.

## DEC-032: Convergencia dp v2 — descartar estudio anterior
**Fecha:** 2026-04-06
**Decisión:** La convergencia de Fase 2 (DEC-005/DEC-029, dp 0.020→0.005) queda descartada. Se rehace con la configuración actual: canal paramétrico 15m, slope 1:20, friction 0.3, BLIR3 @ 0.04.
**Razón:** El estudio anterior fue con canal fijo (sin slope paramétrico), posición del boulder hardcodeada, material lime-stone, sin fricción Chrono. La configuración cambió sustancialmente al agregar 5D. dp producción queda TBD hasta que la convergencia nueva lo confirme.
**Supersede:** DEC-029 queda provisional — el dp de producción saldrá de la convergencia v2.

## DEC-033: Convergencia dp — caso referencia Moris
**Fecha:** 2026-04-06
**Decisión:** Convergencia con dam_h=0.30m (especificación Moris), no 0.50m. Dominio 1.5m sin reducir.
**Razón:** dam_h=0.30 es el caso de referencia del tutor, está en zona FALLO (medible), y no hay evidencia de que el rango paramétrico necesite ir hasta 0.50m (R1/R2 muestran que >0.30 es FALLO obvio). El dominio se mantiene a 1.5m para condiciones comparables con producción.

## DEC-034: Métricas primarias de convergencia
**Fecha:** 2026-04-06
**Decisión:** Decidir dp con displacement + velocity + SPH force. Rotation como diagnóstico (promueve solo si monotónica). No usar contact_force, water_h ni flow_vel como criterio.
**Razón:** Rotation mostró comportamiento oscilatorio en el estudio anterior (GCI no aplica bajo Celik 2008). SPH force con baja variabilidad es buena señal en convergencia, no debilidad. Contact force descartada (DEC-006, CV=82%). water_h/flow_vel tienen debilidad de postproceso (gauge nearest).
