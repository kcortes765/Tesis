# SOURCES

## SRC-20260501-001 - Repositorio local SPH-Tesis

Fecha de consulta: 2026-05-01
Tipo: local
Fuente: `C:\Users\Admin\Desktop\SPH-Tesis`
Usado para: migracion APOS-X local y reconstruccion de estado operativo.
Claims soportados:
- Existen resultados, docs y scripts productivos locales.
- La memoria APOS historica esta parcial y desfasada.
Confianza: alta
Notas: Los archivos reales del repo tienen prioridad sobre chats previos.

## SRC-20260501-002 - Estado productivo local

Fecha de consulta: 2026-05-01
Tipo: local
Fuente: `data/production_status.json`
Usado para: confirmar que el piloto productivo sigue corriendo.
Claims soportados:
- `total_cases=5`
- `completed=1`
- `failed=0`
- `current_case=prod_pilot_fail_low_mu`
- `progress=2/5`
Confianza: alta
Notas: El archivo se actualiza cuando el runner recupera control entre casos.

## SRC-20260502-001 - Export piloto productivo

Fecha de consulta: 2026-05-02
Tipo: local
Fuente: `exports/pilot_productivo_20260501/`
Usado para: sincronizacion Git liviana y auditoria del piloto productivo.
Claims soportados:
- Piloto termino 5/5 OK.
- Tabla resumen viene de `data/results.sqlite` y `RunPARTs.csv`.
- Export excluye binarios y salidas completas.
Confianza: alta
Notas: Usar para revisar resultados en workspace local sin copiar outputs pesados.
