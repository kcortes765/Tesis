# STATUS

Ultima actualizacion: 2026-05-16 17:30
Proyecto: SPH-IncipientMotion / Tesis UCN 2026
Ruta canonica WS: C:\Users\Admin\Desktop\SPH-Tesis
Estado actual: AL batch2 bracket-closing termino 10/10 OK y quedo exportado de forma liviana para sincronizar con laptop.

## Hechos verificados
- Convergencia cerrada para uso productivo: `dp=0.003`, `classification_mode=displacement_only`, `reference_time_s=0.5`.
- Piloto, batch2, batch3, batch4, AL1 y AL2 tienen exports livianos versionables.
- AL batch2 corrio con `config/al_batch2_bracket_closing_20260514.csv`.
- AL batch2 termino el 2026-05-16 17:09:33: 10/10 OK, 0 fallos numericos, tiempo total 44.66 h.
- AL batch2 produjo 5 ESTABLE y 5 FALLO por `displacement_only`.
- Export liviano AL batch2 creado en `exports/al_batch2_bracket_closing_20260516/`.
- `exports/al_batch2_bracket_closing_20260516/al_batch2_summary.csv` contiene los 10 casos oficiales extraidos desde SQLite.
- Casos AL2 mas cercanos al umbral: `al2_midH_m085_mu0880` FALLO con Dmax=5.19% d_eq y `al2_midH_m100_mu0770` ESTABLE con Dmax=4.31% d_eq.
- El reentrenamiento GP automatico al final de `run_production.py` fue desactivado en commit `414621d`; ahora solo ocurre con `--retrain-gp` explicito.
- El modelo GP generado automaticamente el 2026-05-16 fue removido del path canonico `data/gp_surrogate.pkl` y queda solo en cuarentena local ignorada por Git: `data/quarantine_auto_gp_retrain_20260516_1709/`.
- Paquete Stitch visual creado y versionado en `exports/stitch_visual_package_20260515/`.

## Decisiones activas
- Adoptar `dp=0.003` como resolucion operativa de produccion, sin vender convergencia asintotica fuerte.
- Usar `classification_mode=displacement_only` como criterio primario.
- Usar `reference_time_s=0.5`.
- Tratar rotacion, fuerza SPH/contacto y gauges como diagnosticos, no como criterio primario.
- No entrenar surrogate automaticamente al terminar produccion; cualquier GP nuevo debe ser deliberado y trazable.
- Mantener tandas futuras con matriz explicita, `--max-cases`, dry-run previo y export liviano.

## Inferencias vigentes
- Piloto + batch2 + batch3 + batch4 + AL1 + AL2 ya dan base suficiente para un analisis consolidado y un surrogate exploratorio deliberado.
- AL2 cerro brackets utiles pero no reemplaza una validacion global.
- La frontera debe analizarse con margen continuo al umbral, no solo clase binaria.

## Pendientes criticos
- Hacer `git pull` en laptop principal para traer `exports/al_batch2_bracket_closing_20260516/`, `data/results.sqlite` y el bloqueo del reentreno automatico.
- Auditar cientificamente piloto + batch2 + batch3 + batch4 + AL1 + AL2 juntos.
- Regenerar figuras productivas/AL incorporando AL2.
- Decidir si repetir/reprocesar oficialmente `batch4_mass_m125_H0225_mu0860`.
- Entrenar surrogate nuevo de forma deliberada, con variables y target correctos, no usando el reentreno legacy automatico.
- Decidir siguiente mini-batch solo despues del analisis consolidado.

## Riesgos activos
- Riesgo interpretativo: AL2 es lote dirigido de cierre de brackets, no mapa global completo.
- Riesgo de usar accidentalmente un GP legacy; `data/gp_surrogate.pkl` fue retirado para evitarlo.
- Riesgo de mezclar rotacion diagnostica con falla por desplazamiento.
- Riesgo de tratar el caso parcial de batch4 como oficial.

## Evidencia reciente
- `exports/al_batch2_bracket_closing_20260516/README.md`
- `exports/al_batch2_bracket_closing_20260516/al_batch2_summary.md`
- `exports/al_batch2_bracket_closing_20260516/al_batch2_summary.csv`
- `exports/al_batch2_bracket_closing_20260516/production_status.json`
- `exports/al_batch2_bracket_closing_20260516/production_log_tail.txt`
- `config/al_batch2_bracket_closing_20260514.csv`
- `data/production_20260514_2030.log`
- `scripts/run_production.py`
- `414621d Disable automatic GP retraining after production`
