# HANDOFF

## Proxima accion recomendada
1. Revisar `exports/pilot_productivo_20260501/pilot_summary.md` y `pilot_summary.csv`.
2. Confirmar lectura cientifica del piloto: 5/5 OK, 3 FALLO y 2 ESTABLE por `displacement_only`.
3. Decidir matriz del siguiente batch solo despues de revisar rangos y hacer dry-run.
4. Completar siguiente sprint APOS-X: evals y endurecimiento de `apos-run`.

## Contexto minimo para continuar
- Convergencia cerrada: `dp=0.003` queda como malla operativa.
- Criterio primario: `displacement_only`.
- Referencia temporal: `reference_time_s=0.5`.
- Rotacion: diagnostico.
- Piloto real completado con matriz explicita de 5 casos:
  `config/pilot_productivo_20260430.csv`.
- Export liviano listo en `exports/pilot_productivo_20260501/`.
- Guardas de seguridad ya incorporadas en `scripts/run_production.py`.
- APOS se esta migrando localmente a APOS-X; no tocar global/system sin confirmacion.
- `apos-system/` ya existe como semilla local y `apos-run` ya bloquea el caso ambiguo `run_production.py --pilot --prod`.
- Las skills visibles repo-locales son solo tres: `/apos`, `/apos-status` y `/guardar`.

## Archivos a leer primero
1. `.apos/CONTEXT_POLICY.md`
2. `.apos/INDEX.md`
3. `.apos/STATUS.md`
4. `.apos/HANDOFF.md`
5. `.apos/PLAN.md`
6. `.apos/RISKS.md`
7. `.apos/OPEN_QUESTIONS.md`
8. `docs/CONFIGURACION_PRODUCTIVA_TESIS.md`
9. `config/pilot_productivo_20260430.csv`
10. `scripts/run_production.py`
11. `apos-system/harness/apos-run.py`

## Comandos sugeridos
```powershell
Get-Content data\production_status.json

Get-Content exports\pilot_productivo_20260501\pilot_summary.md
```

## Senales de exito
- El export liviano sincroniza por Git sin arrastrar binarios ni CSVs crudos grandes.
- La siguiente tanda usa matriz explicita, dry-run y `--max-cases`.
- APOS-X local permite retomar sin depender del chat.

## No hacer todavia
- No correr mas convergencia.
- No lanzar campana parametrica grande hasta revisar el export del piloto.
- No modificar skills globales ni `.system`.
- No borrar outputs del piloto ni carpetas de casos.
- No interpretar fallos numericos como fallos fisicos.

## Riesgos inmediatos
- GPU ocupada por el piloto.
- Estado APOS historico desfasado.
- Posible drift entre documentacion vieja y codigo actual.
