# Stitch visual package - SPH thesis

Fecha: 2026-05-15

Este paquete es liviano y esta preparado para subir a Stitch/Google Labs como contexto de diseno. No contiene outputs crudos de DualSPHysics ni binarios pesados.

## Objetivo

Dar a Stitch todo lo necesario para proponer una mejora visual de nivel tesis/paper para:

1. la pagina de convergencia de resolucion `dp`;
2. la pagina post-convergencia con frontera operacional y lotes dirigidos;
3. los graficos cientificos asociados.

## Orden recomendado de uso en Stitch

1. Subir o pegar `DESIGN.md`.
2. Subir los prompts en `prompts/`.
3. Para convergencia, subir:
   - `convergence/figures/*.png`
   - `convergence/data/*.csv`
   - `convergence/current_page/index.html`
   - `convergence/current_page/styles.css`
4. Para post-convergencia, subir:
   - `post_convergence/figures/*.png`
   - `post_convergence/data/*.csv`
   - `post_convergence/current_page/index.html`
   - `post_convergence/current_page/styles.css`
5. Pedir a Stitch que use las imagenes solo como referencia visual y los CSV/HTML/scripts como fuente de verdad.

## Regla critica

Las imagenes actuales son referencia de diseno. No deben usarse para leer valores numericos. Los valores numericos salen de los CSV y del codigo generador.

## Que puede mejorar Stitch

- Jerarquia visual.
- Espaciado.
- Layout de secciones.
- Tablas.
- Captions.
- Legendas.
- Anotaciones.
- Consistencia de colores.
- Estetica cientifica.
- UX de inspeccion/zoom.

## Que no puede cambiar Stitch

- Datos.
- Criterio de falla.
- `dp=0.003 m` como resolucion operativa.
- `classification_mode=displacement_only`.
- `reference_time_s=0.5`.
- Rotacion como diagnostico.
- Interpretacion metodologica conservadora.

## Archivos clave

- `DESIGN.md`: contrato visual.
- `prompts/README_STITCH_PACKAGE.md`: instrucciones completas.
- `prompts/STITCH_INPUT_MANIFEST.md`: que adjuntar y por que.
- `prompts/PROMPT_02_CONVERGENCIA_PAGE.md`: rediseño de convergencia.
- `prompts/PROMPT_03_POST_CONVERGENCIA_PAGE.md`: rediseño post-convergencia.
- `prompts/PROMPT_04_GRAPH_REDESIGN_BRIEF.md`: rediseño grafico detallado.
- `prompts/PROMPT_05_CODEX_IMPLEMENTATION_HANDOFF.md`: como pasar el resultado de Stitch a Codex para implementarlo.

## Resultado esperado de Stitch

No pedir a Stitch que implemente directamente en el repo. Pedirle:

1. propuesta visual;
2. estructura de pagina;
3. cambios concretos por figura;
4. reglas de layout;
5. instrucciones de implementacion para Codex.

Luego se implementa en:

- `scripts/build_convergence_story_web.py`
- `scripts/build_post_convergence_story_web.py`
- `docs/convergence_story_web/`
- `docs/post_convergence_story_web/`

