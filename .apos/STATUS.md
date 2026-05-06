# STATUS

Ultima actualizacion: 2026-05-06
Proyecto: SPH-IncipientMotion / Tesis UCN 2026
Ruta: C:\Users\Admin\Desktop\SPH-Tesis
Estado actual: convergencia cerrada; piloto productivo exportado; batch2 productivo chico completado/exportado; sincronizacion Git WS->PC preparada.

## Hechos verificados
- Convergencia cerrada para uso productivo: `dp=0.003`, `classification_mode=displacement_only`, `reference_time_s=0.5`.
- El piloto productivo termino `completed`, 5/5 casos OK, 0 fallos numericos, tiempo total 22.11 h.
- `exports/pilot_productivo_20260501/` contiene export liviano trazable del piloto.
- `config/batch2_productivo_20260503.csv` contiene 8 casos para refinar frontera base, sensibilidad hidraulica moderada y chequeo `slope_inv=10`.
- Batch2 termino `completed`, 8/8 casos OK, 0 fallos numericos, tiempo total 34.55 h.
- `data/production_status.json` reporta `phase=completed`, `completed=8`, `failed=0`, `progress=8/8`.
- No hay procesos `DualSPHysics`, `GenCase` ni `python` corriendo.
- `exports/batch2_productivo_20260505/` fue creado como export liviano trazable: 24 archivos, ~69 KB.
- `exports/batch2_productivo_20260505/batch2_summary.csv` contiene 8 filas: 3 FALLO y 5 ESTABLE por `displacement_only`.
- Batch2 base `H=0.20`, `slope=1:20`: `mu=0.675` falla; `mu=0.685` y `mu=0.700` son estables.
- Batch2 hidraulica fuerte `H=0.225`, `slope=1:20`: `mu=0.680` y `mu=0.720` fallan.
- Batch2 hidraulica debil `H=0.175`, `mu=0.680`, `slope=1:20` es estable.
- Batch2 `slope=1:10`, `H=0.20`, `mu=0.600` y `mu=0.650` son estables por desplazamiento, con rotacion diagnostica > 5 deg.
- `docs/CONFIGURACION_PRODUCTIVA_TESIS.md` existe como documento de configuracion productiva oficial.
- `scripts/run_production.py` acepta `--matrix`, `--max-cases`, `--allow-large` y `--dry-run`.
- `.agents/skills` contiene solo tres skills visibles: `apos`, `apos-status` y `guardar`.
- `apos-system/` existe como semilla local APOS-X con docs, adaptador Codex y `apos-run`.
- Se hizo commit y push a `origin/master`: `646c567 Sync WS thesis results and batch2 export`.

## Decisiones activas
- Adoptar `dp=0.003` como malla operativa de produccion, sin vender convergencia asintotica fuerte.
- Usar `classification_mode=displacement_only` como criterio primario.
- Usar `reference_time_s=0.5` para medir desplazamiento desde una referencia temporal posterior al settling inicial.
- Tratar la rotacion como diagnostico, no como criterio primario de falla.
- No correr mas convergencia por ahora.
- No lanzar campana parametrica grande hasta revisar cientificamente piloto + batch2.
- Mantener tandas futuras con matriz explicita, `--max-cases`, dry-run previo y export liviano.

## Inferencias vigentes
- Batch2 confirma que el pipeline productivo ya puede producir resultados mixtos e informativos sin fallos numericos.
- La frontera base para `H=0.20`, `slope=1:20` queda reforzada entre `mu=0.675` y `mu=0.685`.
- `H=0.225` desplaza la frontera a fricciones mayores que `mu=0.720` en los puntos ensayados.
- `slope=1:10` no debe interpretarse solo con intuicion de pendiente: en estos casos el desplazamiento fue bajo aunque la rotacion diagnostica supero 5 deg.

## Pendientes criticos
- Auditar cientificamente `exports/batch2_productivo_20260505/batch2_summary.csv`.
- Decidir si el siguiente paso es un mini-batch dirigido o entrenar un primer surrogate exploratorio con piloto + batch2 + convergencia comparable.
- Si se disena otro lote, hacerlo con matriz explicita y dry-run; no campana grande.
- Completar evals APOS-X sobre las tres skills repo-locales y endurecer `apos-run`.

## Riesgos activos
- Un comando productivo sin matriz explicita o sin limite de casos podria lanzar demasiadas simulaciones.
- La memoria APOS historica tiene encoding mojibake y estado desfasado; no debe usarse como fuente unica.
- Las rutas globales historicas `C:\Seba` y `C:\Users\kevin` no existen en esta WS.
- Riesgo interpretativo: mezclar rotacion diagnostica con criterio primario `displacement_only`.
- Riesgo interpretativo: leer batch2 como campana parametrica completa; es solo lote chico dirigido.

## Evidencia reciente
- `data/production_status.json`
- `data/production_20260503_1838.log`
- `data/results.sqlite`
- `data/processed/batch2_*`
- `config/batch2_productivo_20260503.csv`
- `exports/batch2_productivo_20260505/README.md`
- `exports/batch2_productivo_20260505/batch2_summary.csv`
- `exports/batch2_productivo_20260505/batch2_summary.md`
- `exports/batch2_productivo_20260505/production_status.json`
- `exports/batch2_productivo_20260505/production_log_tail.txt`
- Git commit `646c567`
