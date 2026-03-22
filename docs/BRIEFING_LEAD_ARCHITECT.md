# BRIEFING PARA LEAD ARCHITECT — Estado Completo Feb 2026
> Generado: 2026-02-25, sesion 18
> Nota de vigencia (2026-03-11): este briefing sigue siendo util como resumen estrategico, pero ya NO debe usarse como snapshot operativo principal del repo. Para handoff actualizado usar primero `HANDOFF_AI_CONTEXT.md`, `CONTEXT_BASE_FILES.md` y `RETOMAR.md`.

## QUIEN SOY
Sebastian Cortes, ingenieria civil UCN Chile. Tesis sobre simulacion SPH de transporte de boulders costeros bajo tsunami. Fondecyt del Dr. Moris. Objetivo personal: emigrar a Canada con perfil de elite (2 papers Q1 + portfolio).

## HARDWARE DISPONIBLE
- **WS UCN**: i9-14900KF + RTX 5090 32GB VRAM (24/7 corriendo sims)
- **Laptop**: i7-14650HX + RTX 4060 8GB + 16GB RAM (ociosa, para ML)
- **Vast.ai**: RTX 4090 a $0.40/h para escalar cuando necesite

## QUE ESTA HECHO

### Pipeline completo (funcional)
- `geometry_builder.py`: STL + template XML → caso parametrico con masa, inercia, fillbox
- `batch_runner.py`: GenCase → DualSPHysics GPU → cleanup .bi4
- `data_cleaner.py`: ChronoExchange CSV → metricas → SQLite
- `main_orchestrator.py`: LHS matrix → loop completo → results.sqlite
- Notificaciones automaticas via ntfy.sh

### Convergencia de malla (COMPLETADA)
- 7 niveles de dp testeados
- **dp=0.004 es produccion** (convergido, delta <5% vs dp=0.003)
- Contact force NO converge (CV=82%) — no usar como criterio
- Hallazgo cientifico documentado

### Screening 50 casos LHS (CORRIENDO)
- 50 combinaciones (dam_h, mass, rot_z) con 1 forma (BLIR3)
- dp=0.004 en RTX 5090
- **6/50 completados**, 0 fallidos, 100% exito
- Promedio: 314.7 min/caso (~5.2h)
- **ETA: 7 marzo 2026**
- Los 5 primeros: todos MOVIMIENTO

### Tesis escrita (5/7 capitulos)
- Cap 1: Introduccion
- Cap 2: Marco Teorico (30+ refs)
- Cap 3: Metodologia Numerica
- Cap 4: Resultados Convergencia
- Cap 5: Pipeline Computacional
- **Faltan**: Cap 6 (Resultados Parametricos), Cap 7 (Conclusiones) — dependen de las 50 sims

### Render pipeline (funcional)
- DualSPHysics CPU → PartVTK → IsoSurface → VTK→PLY → Blender 4.2
- 21 frames generados, render ~30s/frame en i9
- Camara necesita ajuste (cosmetico)
- ParaView 6.0.1 disponible para visualizacion interactiva

## INVESTIGACION SOTA COMPLETADA (verificada con fuentes reales)

### Lo que SI existe y sirve para nuestro caso (particulas SPH/MPM)
| Herramienta | Que es | Por que sirve |
|-------------|--------|---------------|
| **Geoelements GNS** | GNN para particulas (UT Austin, Kumar) | 5000x speedup, validada en dams reales (San Fernando, La Marquesa). PyTorch. MIT license. |
| **Neural SPH** | GNN mejorada con ecuaciones SPH (TU Munich, ICML 2024) | Resuelve clustering de particulas, mejora rollout largo |
| **Diff-GNS** | GNN diferenciable para problemas inversos (Kumar 2024-2025) | 145x speedup vs MPM, ya aplicada a falla de presas |
| **LagrangeBench** | Benchmark con datasets SPH incluidos (NeurIPS 2023) | Para validar nuestro modelo |

### Lo que NO sirve (requiere grillas regulares, no particulas)
- **Walrus** (Polymathic AI, 1.3B params): requiere grillas uniformes. Los datos SPH de The Well fueron voxelizados a 64x64x64 antes de entrar. NO compatible con nuestros datos.
- **GPhyT**: solo 2D, solo grillas regulares
- **FNO / DeepONet**: para campos en grillas, no para nubes de puntos
- **Ningun foundation model actual** trabaja con particulas Lagrangianas nativamente

### Claims de otras IAs que SON FALSOS (verificado)
- "GNS-v3 Multi-Scale Graph Transformers" de DeepMind → **NO EXISTE**
- "Modulus 2026" de NVIDIA → **se llama PhysicsNeMo desde 2024**
- "Generative Physical Simulation con diffusion" de NVIDIA → **exagerado**, solo para weather downscaling
- "Foundation Models for Physics" de DeepMind → **engañoso**, Genie aprende de video, no de simulacion
- "AlphaGeometry para diseño estructural" → **FALSO**, es para geometria matematica de olimpiadas
- "AlphaFold para polimeros de concreto" → **FALSO**, es para estructura de proteinas

### Lo que SI es real de Google/NVIDIA (2025-2026)
- **AlphaEarth Foundations** (jul 2025): satelite virtual, 10m res, gratis en Google Earth Engine
- **Google Flood Hub**: prediccion inundaciones, 150+ paises, API disponible
- **WeatherNext 2** (nov 2025): mejor modelo de huracanes temporada 2025, adoptado por NHC
- **NVIDIA PhysicsNeMo**: framework open-source (FNO, DeepONet, GNN, diffusion)
- **NVIDIA Earth-2 + cBottle** (jun 2025): primer modelo generativo de clima global km-scale
- **Microsoft Aurora** (2025): foundation model atmosfera 1.3B params, publicado en Nature

## PLAN DE PAPERS (DEFINIDO Y VALIDADO)

### Tesis (para titularse — GP surrogate)
- GP con Matern 5/2 + Sobol sensitivity
- Datos: 50 sims screening
- Pregunta: que parametros dominan el transporte incipiente para 1 forma de boulder
- GP es la herramienta CORRECTA: datos tabulares (parametros → metricas), 50 puntos, necesita incertidumbre y Sobol

### Paper 1: Boulder transport + GNN learned simulator
- **Target**: Coastal Engineering o CMAME (Q1)
- **Datos**: 50 sims + 245 sims multi-forma (7 formas × 35 casos, Fondecyt)
- **Metodo**: Geoelements GNS + Neural SPH enhancement
- **Contribucion**: primer simulador aprendido para transporte de boulders costeros
- **GP vs GNN**: son complementarios. GP mapea parametros→resultado (escalar). GNN predice la simulacion completa particula por particula (campo).
- Las 245 sims del Fondecyt SON los datos de entrenamiento — no es trabajo extra

### Paper 2: Tailings inverse analysis + Transfer Learning
- **Target**: CMAME o Computers and Geotechnics (Q1)
- **Core (se sostiene solo)**: Diff-GNS analisis inverso de colapso de relave. Dado el area de inundacion observada → infiere propiedades del material (viscosidad, yield stress). Esto es lo que mineras pagarian millones por saber post-accidente.
- **Forward surrogate**: prediccion rapida de run-out para GISTM compliance (toda mina lo necesita)
- **Bonus (TL)**: Transfer Learning desde GNN de boulders. Si funciona (~20-40% speedup probable), paper sube de nivel. Si no funciona, paper se sostiene con Diff-GNS.
- **Simulador optimo**: MPM (CB-Geo) para tailings, NO DualSPHysics. MPM es el estandar en geotecnia para licuefaccion y grandes deformaciones. Usar la herramienta correcta para cada problema (el codigo es commodity en 2026 con IA).
- **Validacion**: datos publicos de Fundao 2015 o Brumadinho 2019

### Paper 3 (futuro): Cross-domain Transfer Learning
- GNN entrenada en costas (SPH agua) → transferida a mineria (MPM lodo)
- "La IA descubrio que la conservacion de momento es universal entre dominios y solvers"
- Este es el paper de mayor impacto potencial

### Sobre Nature Computational Science
- Rejection rate >95% para undergrads. No apuntar ahi.
- Targets realistas: Coastal Engineering (~IF 5), CMAME (~IF 7), Computers and Geotechnics (~IF 5)
- Estrategia: apuntar a CMAME, si rechazan → Computers and Geotechnics

## DECISIONES TECNICAS CLAVE

| Decision | Razon |
|----------|-------|
| GP para tesis, GNN para papers | GP responde "que resultado", GNN predice "la simulacion completa". Complementarios. |
| SPH para costas, MPM para tailings | Mejor herramienta para cada problema. El codigo no es constraint. |
| TL es bonus, no fundamento | Paper 2 se sostiene con Diff-GNS. TL cross-solver (SPH→MPM) es hipotesis no probada. |
| Entrenamiento GNN incremental | Empezar con 5 casos ya completados, no esperar las 50 sims. Adaptive sampling > batch. |
| 50+50 > 100 de una | Analizar primeros 50, diseñar los siguientes 50 concentrados en zona de transicion. |
| Active Learning natural | GP varianza predictiva indica donde simular next. No se necesita framework sofisticado. |
| dp=0.004 produccion | Convergido. dp=0.003 toma 812 min/caso sin mejora significativa (<5%). |
| Contact force NO criterio | CV=82%, no converge. Hallazgo cientifico, no bug. |
| Laptop para ML, WS para sims | RTX 4060 8GB es suficiente para entrenar GNN con PyTorch Geometric. |

## TIMELINE

```
FEB-MAR 2026:  50 sims screening corriendo (ETA 7 marzo)
               Setup GNN en laptop ← AHORA
               Entrenar GNN incrementalmente con datos parciales

MAR-ABR:       50 sims listas → Sobol + GP → escribir Caps 6-7
               Analizar zona de transicion
               Email Moris → 6 STLs adicionales

MAY-JUN:       245 sims multi-forma (7 formas, cuando lleguen STLs)
               GNN refinada con 245 casos
               Submit Paper 1 → Coastal Engineering
               Tesis lista para defensa

JUL:           Defensa tesis (o antes si esta listo)

AGO-OCT:       Instalar CB-Geo MPM
               Validar MPM para tailings (10 casos prueba primero)
               100-200 sims tailings si valida
               Diff-GNS + intentar TL

NOV:           Submit Paper 2 → CMAME
               Dashboard Streamlit (portfolio)

DIC:           Portfolio GitHub + LinkedIn
               Cold emails a profesores en Canada
               IELTS 7.5
```

## RIESGOS IDENTIFICADOS

| Riesgo | Mitigacion |
|--------|-----------|
| Moris tarda en entregar STLs | Presionar por email. Sin STLs no hay 245 sims ni Paper 1 completo. |
| TL SPH→MPM no funciona | Paper 2 se sostiene con Diff-GNS inverso (ya validado por Kumar). |
| DualSPH non-Newtonian CFL explota (n<0.5) | Probar 5 casos primero. Si falla, usar MPM exclusivamente. Desarrollador de DualSPH advierte problemas con n<0.5. |
| Sims crashean | 0 fallidos en 5 completados. Pipeline robusto con try/finally. |
| Reviewer pide experimentos | Validar contra datos publicados (Nott, Nandasena, Fundao). 100% numerico, no hay lab. |

## QUE NECESITO DE TI (LEAD ARCHITECT)

1. Validar este plan o proponer ajustes
2. Ayudar a diseñar la arquitectura GNN cuando empiece el setup en laptop
3. Estrategia para el email a Moris (como pedir los STLs sin parecer impaciente)
4. Review del Paper 1 draft cuando este listo
