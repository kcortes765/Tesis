# Stitch input manifest

Use this manifest to decide what to attach and what each asset means.

## Global design source

- `DESIGN.md`
  - Role: persistent visual design contract.
  - Use: always attach/paste first.

## Convergence page

### Existing page

- `docs/convergence_story_web/index.html`
- `docs/convergence_story_web/styles.css`
- `scripts/build_convergence_story_web.py`

### Key images

- `00_setup_planta_elevacion.png`
  - Shows physical setup: canal, reservoir, beach slope, real STL-derived boulder outline.
  - Use as current-state reference.
  - Important critique target: block orientation/support must look physically correct and not generic.

- `01_variables_defendibles_dp003.png`
  - Main evidence for adopting dp=0.003.
  - Must show relative and absolute differences.

- `02_tendencia_variables_principales.png`
  - Shows trend versus dp.
  - Must not imply perfect convergence.

- `03_curvas_temporales_finas.png`
  - Fine range temporal curves.
  - Must show displacement in mm and percent of d_eq.

- `05_costo_vs_dp.png`
  - Cost tradeoff.
  - Should make dp=0.003 vs dp=0.002 cost difference obvious.

### Key data

- `convergence_case_physical_setup.csv`
  - Physical case values: H, mass, mu, slope, rot_z, STL, d_eq, channel, gauges.

- `convergence_case_table.csv`
  - Resolution table: dp, Dmax, percent, delta vs fine, cost.

- `convergence_max_differences_vs_dp0002.csv`
  - Max-difference audit versus fine reference.

- `convergence_temporal_errors_vs_dp0002.csv`
  - Temporal-curve error audit versus fine reference.

- `stl_boulder_outline_metadata.csv`
  - Real STL metadata for setup figure.

## Post-convergence page

### Existing page

- `docs/post_convergence_story_web/index.html`
- `docs/post_convergence_story_web/styles.css`
- `scripts/build_post_convergence_story_web.py`

### Key images

- `01_response_map_h_mu_by_mass.png`
  - Operational H-mu-m* map.
  - Stable green, failure red, partial gray.

- `02_margin_vs_mu_by_mass_and_h.png`
  - Continuous margin to movement threshold.
  - Most important post-convergence figure.

- `03_batch_story_margin_strip.png`
  - Batch chronology and evidence accumulation.

- `04_local_hydraulics_vs_displacement.png`
  - Links local hydraulic metrics with displacement.

- `05_forces_vs_displacement.png`
  - Diagnostic hydrodynamic/contact force plot.
  - Must separate SPH force from contact force.

- `06_rotation_diagnostic_vs_displacement.png`
  - Rotation is diagnostic, not criterion.

- `08_mass_effect_displacement_summary.png`
  - Shows effect of mass m*.

### Key data

- `master_production_story.csv`
  - Main post-convergence dataset currently used by the page.

- `FIGURE_INDEX.md`
  - Existing figure index and interpretations.

## Attachment strategy

If Stitch has limited attachment capacity:

### For convergence only

Attach:

1. `DESIGN.md`
2. `00_setup_planta_elevacion.png`
3. `01_variables_defendibles_dp003.png`
4. `03_curvas_temporales_finas.png`
5. `convergence_case_physical_setup.csv`
6. `convergence_case_table.csv`
7. `PROMPT_02_CONVERGENCIA_PAGE.md`

### For post-convergence only

Attach:

1. `DESIGN.md`
2. `01_response_map_h_mu_by_mass.png`
3. `02_margin_vs_mu_by_mass_and_h.png`
4. `06_rotation_diagnostic_vs_displacement.png`
5. `master_production_story.csv`
6. `PROMPT_03_POST_CONVERGENCIA_PAGE.md`

### For full redesign

Attach:

1. `DESIGN.md`
2. all PNGs listed above;
3. both master CSVs;
4. `PROMPT_01_GLOBAL_DESIGN_SYSTEM.md`;
5. `PROMPT_02_CONVERGENCIA_PAGE.md`;
6. `PROMPT_03_POST_CONVERGENCIA_PAGE.md`.

