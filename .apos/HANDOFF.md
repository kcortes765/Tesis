# HANDOFF

## Proxima accion recomendada
1. Traer por Git el export liviano `exports/batch3_productivo_20260509/`.
2. Auditar cientificamente piloto + batch2 + batch3 juntos.
3. Revisar si el siguiente paso es mini-batch adicional, comparacion analitica, benchmark/sanity, o surrogate exploratorio.
4. No lanzar otra tanda antes de esa lectura.

## Contexto minimo para continuar
- Convergencia cerrada: `dp=0.003` queda como malla operativa.
- Criterio primario: `displacement_only`.
- Referencia temporal: `reference_time_s=0.5`.
- Rotacion: diagnostico.
- Piloto productivo: 5/5 OK, export en `exports/pilot_productivo_20260501/`.
- Batch2 productivo chico: 8/8 OK, export en `exports/batch2_productivo_20260505/`.
- Batch3 productivo dirigido: 10/10 OK, 0 fallos numericos, 42.03 h, export en `exports/batch3_productivo_20260509/`.
- Batch3 produjo 6 FALLO y 4 ESTABLE por desplazamiento.
- Base `H=0.20`, `slope=1:20`: FALLO en `mu=0.678` y `0.680`; ESTABLE en `mu=0.682`.
- `H=0.175`: ESTABLE en `mu=0.600`, `0.640`, `0.660`.
- `H=0.210`: FALLO en `mu=0.700`, `0.740`.
- `H=0.225`: FALLO en `mu=0.760`, `0.800`.
- Guardas de seguridad ya incorporadas en `scripts/run_production.py`.
- Las skills visibles repo-locales son solo tres: `/apos`, `/apos-status` y `/guardar`.

## Archivos a leer primero
1. `.apos/CONTEXT_POLICY.md`
2. `.apos/INDEX.md`
3. `.apos/STATUS.md`
4. `.apos/HANDOFF.md`
5. `exports/batch3_productivo_20260509/batch3_summary.md`
6. `exports/batch3_productivo_20260509/batch3_summary.csv`
7. `exports/batch2_productivo_20260505/batch2_summary.csv`
8. `exports/pilot_productivo_20260501/pilot_summary.csv`
9. `config/batch3_productivo.csv`
10. `scripts/run_production.py`

## Comandos sugeridos
```powershell
Get-Content exports\batch3_productivo_20260509\batch3_summary.md

Import-Csv exports\batch3_productivo_20260509\batch3_summary.csv |
  Select case_id,dam_height,friction_coefficient,slope_inv,criterion_class,disp_pct_deq,max_rotation_deg

Get-Content exports\batch3_productivo_20260509\production_status.json

Get-Process | Where-Object { $_.ProcessName -match "DualSPHysics|GenCase|python" } |
  Select Id,ProcessName,StartTime,CPU
```

## Senales de exito
- Batch3 queda versionado como export liviano y trazable para la IA/local.
- La lectura cientifica separa produccion dirigida de convergencia.
- No se mezcla rotacion diagnostica con falla por desplazamiento.

## No hacer todavia
- No correr mas convergencia.
- No lanzar campana parametrica grande.
- No lanzar otra tanda antes de revisar batch3.
- No borrar `cases/batch3_*` ni `data/processed/batch3_*`.
- No modificar skills globales ni `.system`.
- No versionar outputs pesados.
- No interpretar fallos numericos como fallos fisicos.

## Riesgos inmediatos
- Estado APOS historico desfasado en `BOOTSTRAP.md`; priorizar `STATUS/HANDOFF` y archivos reales.
- Posible drift entre documentacion vieja y codigo actual.
- Riesgo de sobreinterpretar batch2/batch3 como mapa completo de fragilidad.
- `data/results.sqlite` cambio localmente, pero el paquete seguro para Git es el export liviano.
