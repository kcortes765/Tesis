# STATUS

Ultima actualizacion: 2026-05-01
Proyecto: SPH-IncipientMotion / Tesis UCN 2026
Ruta: C:\Users\Admin\Desktop\SPH-Tesis
Estado actual: convergencia cerrada; piloto productivo de 5 casos completado; export liviano listo para sincronizar.

## Hechos verificados
- El piloto productivo termino `completed`, 5/5 casos OK, 0 fallos numericos, tiempo total 22.11 h.
- `data/production_status.json` reporta `phase=completed`, `completed=5`, `failed=0`, `progress=5/5`.
- `exports/pilot_productivo_20260501/` contiene export liviano trazable de 18 archivos y ~55 KB.
- La convergencia de frontera ya incluye el probe fino `conv_probe_dp002_f06625`, que termino OK y estable por `displacement_only`.
- La carpeta `data/figures/derived_convergence_graphics/` contiene figuras/tablas regeneradas con `conv_edge_*`, `conv_reassure_*`, `conv_repeat_*` y `conv_probe_*`.
- `docs/CONFIGURACION_PRODUCTIVA_TESIS.md` existe como documento de configuracion productiva oficial.
- `config/pilot_productivo_20260430.csv` existe como matriz piloto explicita de 5 casos.
- `scripts/run_production.py` ya acepta `--matrix`, `--max-cases`, `--allow-large` y `--dry-run`.
- `apos-system/` existe como semilla local APOS-X con docs, adaptador Codex y `apos-run`.
- `.agents/skills` contiene solo tres skills visibles: `apos`, `apos-status` y `guardar`.
- `apos-run` bloqueo correctamente `run_production.py --pilot --prod` en preflight.

## Decisiones activas
- Adoptar `dp=0.003` como malla operativa de produccion, sin vender convergencia asintotica fuerte.
- Usar `classification_mode=displacement_only` como criterio primario.
- Usar `reference_time_s=0.5` para medir desplazamiento desde una referencia temporal posterior al settling inicial.
- Tratar la rotacion como diagnostico, no como criterio primario de falla.
- No correr mas convergencia por ahora.
- No lanzar campana parametrica grande hasta validar el piloto productivo.
- Migrar APOS localmente hacia APOS-X sin tocar skills globales/system.

## Inferencias vigentes
- El piloto productivo debe servir como prueba operacional completa del pipeline antes de cualquier tanda grande.
- APOS local necesita modernizacion: los archivos historicos quedaron desfasados y faltan componentes APOS-X.
- El safe-harness debe envolver o complementar las guardas ya agregadas a `run_production.py`.

## Pendientes criticos
- Revisar cientificamente el export del piloto antes de definir primera tanda productiva.
- Sincronizar por Git solo codigo/config/docs/APOS/exports livianos.
- Completar instalacion local APOS-X: estructura, politica, ledger append-only y evidencia de migracion.
- Completar evals APOS-X sobre las tres skills repo-locales y endurecer `apos-run`.

## Riesgos activos
- Un comando productivo sin matriz explicita o sin limite de casos podria lanzar demasiadas simulaciones.
- La memoria APOS historica tiene encoding mojibake y estado desfasado; no debe usarse como fuente unica.
- Las rutas globales historicas `C:\Seba` y `C:\Users\kevin` no existen en esta WS.
- El piloto actual consume GPU; no abrir otra tanda encima.

## Evidencia reciente
- `data/production_status.json`
- `data/production_20260430_1758.log`
- `exports/pilot_productivo_20260501/pilot_summary.csv`
- `exports/pilot_productivo_20260501/pilot_summary.md`
- `data/results/conv_probe_dp002_f06625.csv`
- `data/figures/derived_convergence_graphics/master_convergence_frontier.csv`
- `docs/CONFIGURACION_PRODUCTIVA_TESIS.md`
- `config/pilot_productivo_20260430.csv`
