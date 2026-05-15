# Stitch package for SPH thesis visuals

This folder contains the material to give Stitch a clear, controlled brief. The goal is to improve the visual quality of the thesis web pages without letting a design agent invent scientific data or change methodology.

## Use this in layers

Do not paste everything into Stitch at once. Use this order:

1. Attach or paste `DESIGN.md`.
2. Paste `PROMPT_01_GLOBAL_DESIGN_SYSTEM.md`.
3. Attach current screenshots/images of the target page.
4. Paste either:
   - `PROMPT_02_CONVERGENCIA_PAGE.md`, or
   - `PROMPT_03_POST_CONVERGENCIA_PAGE.md`.
5. If the goal is graph redesign, paste `PROMPT_04_GRAPH_REDESIGN_BRIEF.md`.
6. After Stitch proposes a design, use `PROMPT_05_CODEX_IMPLEMENTATION_HANDOFF.md` to convert the design into precise implementation instructions for Codex/WS.

## Should current graph images be attached?

Yes, but with a very specific role.

Attach current PNG screenshots or exported figures as visual references, not as data sources. Stitch should use them to understand:

- current layout;
- what feels crowded or unclear;
- where labels overlap;
- current color usage;
- current figure hierarchy;
- what needs to become more thesis/paper quality.

Do not ask Stitch to read numeric values from images. Numeric values must come from CSV/HTML/scripts.

## Minimum images to attach

For convergence:

- `docs/convergence_story_web/figures/00_setup_planta_elevacion.png`
- `docs/convergence_story_web/figures/01_variables_defendibles_dp003.png`
- `docs/convergence_story_web/figures/02_tendencia_variables_principales.png`
- `docs/convergence_story_web/figures/03_curvas_temporales_finas.png`
- `docs/convergence_story_web/figures/05_costo_vs_dp.png`

For post-convergence:

- `docs/post_convergence_story_web/figures/01_response_map_h_mu_by_mass.png`
- `docs/post_convergence_story_web/figures/02_margin_vs_mu_by_mass_and_h.png`
- `docs/post_convergence_story_web/figures/03_batch_story_margin_strip.png`
- `docs/post_convergence_story_web/figures/04_local_hydraulics_vs_displacement.png`
- `docs/post_convergence_story_web/figures/05_forces_vs_displacement.png`
- `docs/post_convergence_story_web/figures/06_rotation_diagnostic_vs_displacement.png`
- `docs/post_convergence_story_web/figures/08_mass_effect_displacement_summary.png`

## Minimum data/context to attach or paste

For convergence:

- `docs/convergence_story_web/data/convergence_case_physical_setup.csv`
- `docs/convergence_story_web/data/convergence_case_table.csv`
- `docs/convergence_story_web/data/convergence_max_differences_vs_dp0002.csv`
- `docs/convergence_story_web/data/convergence_temporal_errors_vs_dp0002.csv`
- `docs/convergence_story_web/data/stl_boulder_outline_metadata.csv`

For post-convergence:

- `docs/post_convergence_story_web/data/master_production_story.csv`
- `docs/post_convergence_story_web/data/FIGURE_INDEX.md`

## What Stitch may improve

- Visual hierarchy.
- Layout rhythm.
- Spacing.
- Captions.
- Figure cards.
- Table readability.
- Legend placement.
- Annotation strategy.
- Responsive behavior.
- Storytelling sequence.
- Design system consistency.

## What Stitch must not change

- Scientific numbers.
- Classification criterion.
- dp decision.
- Meaning of stable/failure.
- Meaning of rotation.
- Source data.
- Claims about convergence.

## Current live pages

- Convergence: https://kcortes765.github.io/convergencia-dp/
- Post-convergence: https://kcortes765.github.io/convergencia-dp/post-convergencia/

