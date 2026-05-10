# STATUS

Ultima actualizacion: 2026-05-09
Proyecto: SPH-IncipientMotion / Tesis UCN 2026
Ruta: C:\Users\Admin\Desktop\SPH-Tesis
Estado actual: convergencia cerrada; piloto, batch2 y batch3 productivos exportados livianos; listo para sincronizar por Git y revisar cientificamente antes de otra tanda.

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
- `config/batch3_productivo.csv` fue creado con 10 casos dirigidos para produccion, no convergencia.
- El dry-run de batch3 fue correcto: 10 casos, `dp=0.003`, `classification_mode=displacement_only`, `reference_time_s=0.5`, matriz explicita `config/batch3_productivo.csv`.
- Batch3 real fue lanzado el 2026-05-07 19:33 aprox. con `python scripts\run_production.py --prod --matrix config\batch3_productivo.csv --max-cases 10 --no-notify`.
- Batch3 termino el 2026-05-09 13:35:25: `phase=completed`, 10/10 OK, 0 fallos numericos, tiempo total 42.03 h.
- Batch3 produjo 6 FALLO y 4 ESTABLE por `displacement_only`.
- Batch3 base `H=0.20`, `slope=1:20`: FALLO en `mu=0.678` y `mu=0.680`; ESTABLE en `mu=0.682`.
- Batch3 `H=0.175`: ESTABLE en `mu=0.600`, `0.640` y `0.660`.
- Batch3 `H=0.210`: FALLO en `mu=0.700` y `mu=0.740`.
- Batch3 `H=0.225`: FALLO en `mu=0.760` y `mu=0.800`.
- `exports/batch3_productivo_20260509/` fue creado como export liviano trazable: resumen CSV/MD, matriz, status, tail de log, inventario y Run.csv/RunPARTs.csv por caso.
- No hay procesos `DualSPHysics`, `GenCase` ni `python` de produccion activos tras terminar batch3.

## Decisiones activas
- Adoptar `dp=0.003` como malla operativa de produccion, sin vender convergencia asintotica fuerte.
- Usar `classification_mode=displacement_only` como criterio primario.
- Usar `reference_time_s=0.5` para medir desplazamiento desde una referencia temporal posterior al settling inicial.
- Tratar la rotacion como diagnostico, no como criterio primario de falla.
- No correr mas convergencia por ahora.
- No lanzar otra tanda antes de revisar cientificamente piloto + batch2 + batch3.
- No lanzar campana parametrica grande hasta revisar cientificamente piloto + batch2 + batch3.
- Mantener tandas futuras con matriz explicita, `--max-cases`, dry-run previo y export liviano.

## Inferencias vigentes
- Batch2 confirma que el pipeline productivo ya puede producir resultados mixtos e informativos sin fallos numericos.
- Batch3 afina la frontera base a un intervalo estrecho alrededor de `0.680 < mu_crit < 0.682` para `H=0.20`, `slope=1:20`, `dp=0.003`.
- La frontera base para `H=0.20`, `slope=1:20` queda reforzada entre `mu=0.675` y `mu=0.685`.
- `H=0.225` desplaza la frontera a fricciones mayores que `mu=0.720` en los puntos ensayados.
- `slope=1:10` no debe interpretarse solo con intuicion de pendiente: en estos casos el desplazamiento fue bajo aunque la rotacion diagnostica supero 5 deg.

## Pendientes criticos
- Auditar cientificamente `exports/pilot_productivo_20260501/`, `exports/batch2_productivo_20260505/` y `exports/batch3_productivo_20260509/` juntos.
- Decidir si el siguiente paso es un mini-batch dirigido o entrenar un primer surrogate exploratorio con piloto + batch2 + convergencia comparable.
- Si se disena otro lote, hacerlo con matriz explicita y dry-run; no campana grande.
- Completar evals APOS-X sobre las tres skills repo-locales y endurecer `apos-run`.

## Riesgos activos
- Un comando productivo sin matriz explicita o sin limite de casos podria lanzar demasiadas simulaciones.
- La memoria APOS historica tiene encoding mojibake y estado desfasado; no debe usarse como fuente unica.
- Las rutas globales historicas `C:\Seba` y `C:\Users\kevin` no existen en esta WS.
- Riesgo interpretativo: mezclar rotacion diagnostica con criterio primario `displacement_only`.
- Riesgo interpretativo: leer batch2/batch3 como campana parametrica completa; son lotes dirigidos.
- No usar `batch3` como mapa completo de fragilidad; sigue siendo lote dirigido.

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
- `config/batch3_productivo.csv`
- `data/production_20260507_1933.log`
- `data/production_status.json`
- `data/logs/batch3_productivo_20260507_193347_stdout.log`
- `data/logs/batch3_productivo_20260507_193347_stderr.log`
- `exports/batch3_productivo_20260509/README.md`
- `exports/batch3_productivo_20260509/batch3_summary.csv`
- `exports/batch3_productivo_20260509/batch3_summary.md`
- `exports/batch3_productivo_20260509/production_status.json`
