# OPEN_QUESTIONS

## Q-20260501-001 - Resultado completo del piloto productivo

Estado: resuelta
Tipo: tecnica
Contexto: el piloto de 5 casos esta corriendo.
Que evidencia falta:
- `production_status.json` final.
- logs finales.
- CSVs procesados por caso.
Resolucion: piloto completado y exportado en `exports/pilot_productivo_20260501/`.

## Q-20260501-002 - Instalacion de skills APOS-X

Estado: resuelta
Tipo: requisito
Contexto: se preparo memoria APOS-X local, pero no se instalaron skills repo-locales ni globales.
Que evidencia falta:
- decision del usuario sobre instalar `.agents/skills`.
- resultado de evals locales.
Resolucion: el runtime APOS de tesis quedo simplificado a tres skills repo-locales: `/apos`, `/guardar`, `/apos-status`.

## Q-20260501-003 - Alcance de `apos-system/`

Estado: resuelta
Tipo: tecnica
Contexto: la especificacion APOS-X define una fuente versionada `apos-system/`.
Que evidencia falta:
- decidir si vive en este repo, en repo separado, o como paquete personal.
Resolucion: para tesis, `apos-system/` no es runtime vivo; APOS canonico es `.apos/` mas tres skills repo-locales.

## Q-20260516-001 - Cuanto expandir pendiente, orientacion y forma

Estado: resuelta parcialmente
Tipo: tecnica
Contexto: se decidio que el plan no debe cerrar con el minimo de simulaciones si hay 6 meses y WS potente. Pendiente, orientacion y forma importan, pero deben entrar de forma jerarquica.
Que evidencia falta:
- resultados de AL5 y posible AL6;
- reentrenamiento GP after-AL5;
- holdout base;
- analisis geometrico/STL actualizado para determinar si conviene usar las 10 formas o un subconjunto;
- presupuesto actualizado de tiempo por simulacion.
Resolucion: se adopta plan ambicioso por etapas; no se lanzara factorial 6D. La forma entra como extension fuerte, idealmente con las 10 formas, si pasan analisis geometrico y sanity de contacto.

## Q-20260520-001 - Usar las 10 formas STL o subconjunto representativo

Estado: abierta
Tipo: tecnica
Contexto: el usuario quiere idealmente aprovechar las 10 formas disponibles para que el efecto de forma tenga peso cientifico. Antes se propuso usar pocas formas por prudencia metodologica.
Que evidencia falta:
- revisar/actualizar analisis geometrico de las 10 STL;
- medir volumen, d_eq, bbox, ratios L/B/T, solidez, huella inferior, centroide e inercia;
- verificar que el pipeline genera masa/inercia/apoyo correcto por forma;
- correr sanity de contacto por forma;
- decidir si todas las formas son suficientemente distintas o si algunas son redundantes.
Resolucion: pendiente; objetivo ideal es usar las 10, pero no sin filtros geometricos/contacto.
