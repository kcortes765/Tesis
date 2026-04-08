# HANDOFF — Thesis OS

**Última sesión:** 2026-04-08 (sesión 10, continuación)

## Qué se hizo

### Convergencia dp v2 corrida e importada
- La WS ejecutó `scripts/run_convergence_v2.py` y se importaron 7/8 casos exitosos (dp 0.010→0.002).
- Resultados en `data/results/convergencia_v2.csv`, `convergencia_v2_gci.json`, `convergencia_v2_temporal/`.
- `dp=0.0015` falló en GenCase (límite hardware); `dp=0.001` no se corrió.

### Diagnóstico técnico v2
- **Forcing y onset convergen bien:** max_flow_velocity ~2.58-2.60 m/s, t_onset(5%d_eq) ~1.60-1.64s entre dp=0.004/0.003/0.002.
- **Trayectoria post-falla NO converge:** displacement 0.003→0.002 sube de 2.5% a 10.8% delta. Rotación salta de 92° a 171° (rama dinámica distinta a dp=0.002).
- **SPH force oscilatoria**, rotation oscilatoria → GCI no aplica para esas métricas.
- **Diagnóstico:** el caso Moris (dam_h=0.30) es fallo masivo (~2m transporte). La no-convergencia es de la trayectoria post-contacto caótica, no del onset ni del forcing.

### Análisis profundo local
- `scripts/analisis_convergencia_v2.py` ejecutado → 4 figuras en `data/figures/conv2_*.png`
- Dashboard completo, comparación dp=0.003 vs 0.002, fuerzas, solver detail
- Reporte en `data/figures/convergencia_v2_analisis.md`

### Convergencia v3 lanzada (CORRIENDO EN WS)
- Se decidió correr convergencia en caso de **frontera** en vez de fallo masivo.
- Caso: dam_h=0.20, mass=1.0, friction=0.5, slope=1:20 (cerca de transición ESTABLE/FALLO).
- **7 dp completos:** 0.010, 0.008, 0.006, 0.005, 0.004, 0.003, 0.002.
- Comando: `python scripts/run_convergence_threshold.py --dps 0.010,...,0.002 --prefix conv3_f05_full`
- Prefix `conv3_f05_full` — no pisa datos de v2.
- Tiempo estimado: ~44h.
- **Hipótesis:** cerca de la frontera, la respuesta debería ser más compacta entre dp levels que en v2 (sin trayectoria post-falla caótica).

## Qué cambió
- `scripts/analisis_convergencia_v2.py` — análisis profundo v2 (nuevo)
- `scripts/run_convergence_threshold.py` — runner de convergencia focalizado (nuevo, de otra IA)
- `docs/CONTEXTO_CONVERGENCIA_V3_2026-04-08.md` — contexto completo para continuidad
- `data/figures/conv2_dashboard.png` + `conv2_003_vs_002.png` + `conv2_forces_detail.png` + `conv2_solver_detail.png`
- `data/figures/convergencia_v2_analisis.md`
- `.apos/` actualizado (HANDOFF, STATUS, BOOTSTRAP, PLAN, WORKING_MODEL, ACTIVE_SPEC)

## Qué debe hacer el siguiente agente
1. **Esperar conv3_f05_full** (~44h en WS)
2. **Importar resultados:** `collect_ws_results.py --prefix conv3_f05_full` en WS, luego pull
3. **Comparar v2 vs v3:**
   - ¿La curva de convergencia es más limpia en el caso de frontera?
   - ¿Los 3 dp finos (0.004/0.003/0.002) mantienen la misma clasificación?
   - ¿Los deltas entre dp=0.003→0.002 bajan respecto a v2?
4. **Si v3 converge limpia:** dp=0.003 queda defendible → comunicar a Moris con evidencia
5. **Si v3 no converge:** escalar a Moris con ambas evidencias (v2 + v3)
6. **Después:** Round 3 al dp elegido → producción 5D

## Qué no debe asumir
- conv3_f05_full está **corriendo**, no completada
- dp=0.003 **no está cerrado** como producción hasta que v3 lo confirme
- La v2 no "falló" — mostró que el caso Moris no es el adecuado para convergencia de incipient motion
- El script `run_convergence_threshold.py` fue escrito por otra IA, no por este agente — verificar si hay bugs
- Hay datos parciales de una corrida abortada `conv3_f05` (solo dp=0.004) que no debe mezclarse con `conv3_f05_full`

## Contexto mínimo para retomar
Leer: `BOOTSTRAP.md` → este `HANDOFF.md` → `docs/CONTEXTO_CONVERGENCIA_V3_2026-04-08.md` → `data/results/convergencia_v2.csv` → `data/figures/convergencia_v2_analisis.md`
