# HANDOFF

## Proxima accion recomendada
1. Hacer commit/push desde la WS con el export AL4 liviano y `data/results.sqlite` actualizado.
2. En laptop: `git pull`.
3. En laptop: reentrenar GP after-AL4 usando datos oficiales hasta AL4.
4. Decidir si corresponde AL5, holdout o checks finos `dp=0.002`.

## Contexto minimo para continuar
- AL4 after-AL3 termino limpio: `8/8` OK, `0` fallos numericos, `35.5 h`.
- AL4 no fue convergencia: fue lote productivo dirigido para cerrar brackets after-AL3.
- Metodologia fija: `dp=0.003`, `classification_mode=displacement_only`, `reference_time_s=0.5`, rotacion diagnostica.
- Resultado AL4: 5 ESTABLE y 3 FALLO.
- Fallos AL4:
  - `al4_base_m085_mu0790`: `Dmax=6.18% d_eq`.
  - `al4_highH_m115_mu0750`: `Dmax=5.45% d_eq`.
  - `al4_highH_m125_mu0680`: `Dmax=6.20% d_eq`.
- Estables cercanos:
  - `al4_highH_m100_mu0865`: `Dmax=4.86% d_eq`.
  - `al4_base_m100_mu06808`: `Dmax=3.57% d_eq`.
- Export liviano WS: `exports/al_batch4_after_al3_20260520/`.
- La laptop debe reentrenar el GP; la WS no debe usar `--retrain-gp`.

## Archivos a leer primero
- `.apos/STATUS.md`
- `.apos/PLAN.md`
- `exports/al_batch4_after_al3_20260520/al_batch4_summary.md`
- `exports/al_batch4_after_al3_20260520/al_batch4_summary.csv`
- `config/al_batch4_after_al3_20260518.csv`
- `data/results.sqlite`

## Comandos sugeridos para laptop
```powershell
git pull
Get-Content exports\al_batch4_after_al3_20260520\al_batch4_summary.md
Import-Csv exports\al_batch4_after_al3_20260520\al_batch4_summary.csv |
  Select case_name,dam_height,boulder_mass,friction_coefficient,criterion_class,disp_pct_deq,margin_pct_deq
```

## Senales de exito
- Laptop ve `exports/al_batch4_after_al3_20260520/`.
- Laptop ve `data/results.sqlite` con filas `al4_*`.
- GP after-AL4 se entrena solo en laptop.
- Siguiente lote se decide con brackets actualizados, no por intuicion.

## No hacer todavia
- No lanzar AL5 antes de reentrenar y revisar AL4.
- No abrir pendiente/orientacion/forma antes de cerrar el analisis AL4.
- No tratar el GP como resultado SPH directo.
- No versionar crudos pesados.
- No usar `--retrain-gp` en WS.

## Riesgos inmediatos
- AL4 incluye puntos muy cercanos al umbral; pequenas diferencias de resolucion/contacto pueden cambiar clase.
- Rotacion supera 5 grados en varios casos, pero no decide la clase bajo `displacement_only`.
- Si el GP after-AL4 propone puntos fuera de brackets observados, revisar que sea realmente necesario.
