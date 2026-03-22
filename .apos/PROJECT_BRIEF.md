# PROJECT_BRIEF — Thesis OS

## Nombre
SPH-IncipientMotion

## Qué es
Tesis UCN 2026 (Sebastián Cortés). Determinar umbrales críticos de movimiento de bloques costeros irregulares bajo flujos tipo tsunami usando simulación SPH (DualSPHysics v5.4 + Chrono) y construir un surrogate probabilístico (GP) para reducir el costo de exploración paramétrica.

Enmarcada en Fondecyt Iniciación 2025 del Dr. Joaquín Moris (FaCIC-UCN).

## Alcance
100% simulación numérica — no hay trabajo de laboratorio físico. El "canal" y "tanque" son dominios computacionales definidos en XML.

## Stack
- **Motor:** DualSPHysics 5.4.x + ProjectChrono (RigidAlgorithm=3)
- **Pipeline:** Python (geometry_builder → batch_runner → data_cleaner → ml_surrogate)
- **Surrogate:** Gaussian Processes (scikit-learn) con Matérn 5/2 + Sobol sensitivity
- **Active Learning:** GP varianza predictiva indica dónde simular next
- **Continuidad:** APOS + Claude Code

## Hardware
| Equipo | Specs | Rol |
|--------|-------|-----|
| WS UCN | i9-14900KF, RTX 5090 32GB | Sims pesadas 24/7 |
| Laptop | i7-14650HX, RTX 4060 8GB, 16GB RAM | ML, GNN, análisis, desarrollo |

## Resultado esperado
1. Pipeline reproducible de simulación
2. Dataset bien estructurado (50 screening + 245 multi-forma)
3. Loop de active learning operativo
4. Surrogate GP + análisis Sobol
5. Tesis escrita (7 capítulos)
6. Base para Paper 1 (GNN) y Paper 2 (tailings)

## Éxito del proyecto
- Simulaciones se lanzan reproduciblemente
- Dataset se genera limpio
- El sistema acumula conocimiento entre sesiones
- Claude Code puede retomar sin reconstruir contexto
- Tesis defendible con resultados sólidos

## Restricciones
- No sobreingeniería temprana
- Priorizar reproducibilidad
- Separar simulación, extracción, dataset y modelado
- Todo output importante debe persistirse
- No usar DualSPHysics v6.0 beta
