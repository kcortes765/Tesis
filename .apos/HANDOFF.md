# HANDOFF

## Proxima accion recomendada
1. Leer `exports/batch2_productivo_20260505/batch2_summary.csv` y `batch2_summary.md`.
2. En el PC local, ejecutar `git pull origin master` para recibir el commit `646c567`.
3. Auditar cientificamente el patron piloto + batch2: frontera base, efecto de `H`, efecto de `slope_inv=10`, y rotacion diagnostica.
4. Decidir si el siguiente paso es:
   - mini-batch dirigido de pocos casos, o
   - primer surrogate exploratorio con los datos existentes.
5. Si se corre otro lote, crear matriz explicita, ejecutar dry-run y mantener `--max-cases`.

## Contexto minimo para continuar
- Convergencia cerrada: `dp=0.003` queda como malla operativa.
- Criterio primario: `displacement_only`.
- Referencia temporal: `reference_time_s=0.5`.
- Rotacion: diagnostico.
- Piloto productivo: 5/5 OK, export en `exports/pilot_productivo_20260501/`.
- Batch2 productivo chico: 8/8 OK, export en `exports/batch2_productivo_20260505/`.
- Sincronizacion Git WS->PC: push a `origin/master` en commit `646c567`.
- Batch2 produjo 3 FALLO y 5 ESTABLE por desplazamiento.
- Frontera base reforzada: `H=0.20`, `slope=1:20`, FALLO en `mu=0.675`, ESTABLE en `mu=0.685` y `0.700`.
- Hidraulica fuerte `H=0.225` fallo en `mu=0.680` y `0.720`.
- `slope=1:10` con `mu=0.600` y `0.650` fue ESTABLE por desplazamiento, con rotacion diagnostica.
- Guardas de seguridad ya incorporadas en `scripts/run_production.py`.
- Las skills visibles repo-locales son solo tres: `/apos`, `/apos-status` y `/guardar`.

## Archivos a leer primero
1. `.apos/CONTEXT_POLICY.md`
2. `.apos/INDEX.md`
3. `.apos/STATUS.md`
4. `.apos/HANDOFF.md`
5. `exports/batch2_productivo_20260505/batch2_summary.csv`
6. `exports/batch2_productivo_20260505/batch2_summary.md`
7. `exports/pilot_productivo_20260501/pilot_summary.csv`
8. `docs/CONFIGURACION_PRODUCTIVA_TESIS.md`
9. `scripts/run_production.py`
10. `apos-system/harness/apos-run.py`

## Comandos sugeridos
```powershell
Get-Content exports\batch2_productivo_20260505\batch2_summary.md

Import-Csv exports\batch2_productivo_20260505\batch2_summary.csv |
  Select case_id,dam_height,friction_coefficient,slope_inv,criterion_class,disp_pct_deq,max_rotation_deg

Get-Content data\production_status.json
```

## Senales de exito
- Se interpreta batch2 sin mezclar rotacion diagnostica con falla por desplazamiento.
- Se decide el siguiente diseno con pocos casos o se prepara surrogate exploratorio.
- No se abre campana grande sin una matriz revisada y dry-run.

## No hacer todavia
- No correr mas convergencia.
- No lanzar campana parametrica grande.
- No borrar `cases/batch2_*` ni `data/processed/batch2_*`.
- No modificar skills globales ni `.system`.
- No versionar outputs pesados.
- No interpretar fallos numericos como fallos fisicos.

## Riesgos inmediatos
- Estado APOS historico desfasado en `BOOTSTRAP.md`; priorizar `STATUS/HANDOFF` y archivos reales.
- Posible drift entre documentacion vieja y codigo actual.
- Riesgo de sobreinterpretar batch2 como mapa completo de fragilidad.
