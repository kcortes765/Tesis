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

## SRC-20260510-001 - GitHub origin/master con exports WS

Fecha de consulta: 2026-05-10
Tipo: repo
Fuente: `origin/master` en commit `3c443e9 Add batch3 production export`
Usado para: reconciliar el repo local con los resultados livianos generados en la WS UCN.
Claims soportados:
- Piloto, batch2 y batch3 estan disponibles como exports livianos versionados.
- `batch3_productivo_20260509` termino 10/10 OK y excluye crudos pesados.
- La transferencia por Git no incluye `.bi4`, `.ibi4`, VTK, `Part*` ni carpetas `*_out/`.
Confianza: alta
Notas: GitHub/WS es fuente canonica para resultados livianos sincronizados; no reemplaza el storage de crudos.

## SRC-20260510-002 - Backup de reconciliacion local

Fecha de consulta: 2026-05-10
Tipo: local
Fuente: `C:\Seba\workspace_backups\tesis-reconcile-20260510_125339`
Usado para: asegurar que la limpieza del repo no pierda cambios locales, APOS previo ni archivos no trackeados en conflicto.
Claims soportados:
- Los cambios trackeados locales previos fueron respaldados antes del fast-forward.
- Los archivos no trackeados en conflicto fueron copiados antes de moverlos dentro del repo.
- La carpeta temporal limpia fue respaldada como evidencia, no como repo canonico.
Confianza: alta
Notas: No usar como fuente diaria de trabajo; solo como respaldo de recuperacion.

## SRC-20260510-003 - STL b02 y analisis geometrico local

Fecha de consulta: 2026-05-10
Tipo: local
Fuente: `models/bloques/b02_variantes_20260510/` y `data/geometry/bloques_b02_20260510/`
Usado para: registrar los bloques STL recibidos localmente y el espacio geometrico cubierto por esa familia.
Claims soportados:
- La familia `b02` contiene un original y nueve reducciones.
- El analisis escalado reporta metricas de volumen, area, bounding box, esfericidad/compacidad y diferencias relativas.
- `b02_Original.stl` coincide con el bloque activo de referencia segun el analisis local previo.
Confianza: media-alta
Notas: Las formas son utiles para variacion geometrica controlada, pero no cubren por si solas un dominio amplio de bloques costeros.

## SRC-20260514-001 - Visualizacion cientifica y storytelling

Fecha de consulta: 2026-05-14
Tipo: documentacion oficial | paper
Fuente: Rougier NP, Droettboom M, Bourne PE (2014), "Ten Simple Rules for Better Figures", PLOS Computational Biology. https://doi.org/10.1371/journal.pcbi.1003833
Usado para: reglas de legibilidad, mensaje unico por figura, adaptacion a audiencia y reduccion de ruido visual.
Claims soportados:
- Una figura cientifica debe actuar como interfaz clara entre datos y lector.
- El diseno de figura afecta interpretacion y no debe ser automatico ni decorativo.
Confianza: alta
Notas: Aplicado en `docs/VISUAL_STORYTELLING_Q1_TESIS_20260514.md`.

## SRC-20260514-002 - Color cientifico

Fecha de consulta: 2026-05-14
Tipo: paper
Fuente: Crameri F, Shephard GE, Heron PJ (2020), "The misuse of colour in science communication", Nature Communications. https://doi.org/10.1038/s41467-020-19160-7
Usado para: evitar rainbow/no uniformes, usar paletas perceptualmente razonables y no depender de rojo/verde.
Claims soportados:
- Paletas no uniformes pueden introducir distorsion visual y afectar conclusiones.
- La eleccion de color debe ajustarse al tipo de dato y ser legible de forma inclusiva.
Confianza: alta
Notas: Figuras productivas usan azul/vermillion + forma para clase, y `cividis`/`viridis` para continuas.

## SRC-20260514-003 - Narrative visualization

Fecha de consulta: 2026-05-14
Tipo: paper
Fuente: Segel E, Heer J (2010), "Narrative Visualization: Telling Stories with Data", IEEE TVCG. https://doi.org/10.1109/TVCG.2010.179
Usado para: ordenar la historia visual por capas: convergencia, frontera operacional, hidraulica local, diagnosticos y costo.
Claims soportados:
- La narrativa visual combina estructura, enfasis y lectura guiada para comunicar evidencia.
Confianza: alta
Notas: Aplicado en la separacion entre `derived_convergence_graphics` y `production_story_graphics`.

## SRC-20260514-004 - Ciencia de comunicacion visual de datos

Fecha de consulta: 2026-05-14
Tipo: review
Fuente: Franconeri SL, Padilla LM, Shah P, Zacks JM, Hullman J (2021), "The Science of Visual Data Communication: What Works", Psychological Science in the Public Interest. https://doi.org/10.1177/15291006211051956
Usado para: priorizar percepcion, comparacion visual limpia y diseno centrado en interpretacion.
Claims soportados:
- La comunicacion visual eficaz depende de como las personas perciben comparaciones, patrones y enfasis.
Confianza: alta
Notas: Se uso como respaldo conceptual para reducir etiquetas, evitar solapamientos y marcar outliers explicitamente.
