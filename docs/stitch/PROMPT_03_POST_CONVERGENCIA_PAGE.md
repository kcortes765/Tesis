# Prompt 03 - Post-convergence page redesign

Task:

Redesign the post-convergence page of the SPH thesis. This page summarizes production pilot, batch2, batch3, batch4, and active-learning evidence after dp=0.003 was selected.

Use:

- `DESIGN.md`
- current post-convergence screenshots/figures
- `master_production_story.csv`
- `FIGURE_INDEX.md`

Scientific message:

This page is not another convergence study. It is the operational stability mapping page at dp=0.003 m.

Common methodology:

- dp=0.003 m;
- classification_mode=displacement_only;
- reference_time_s=0.5;
- failure if Dmax > 5% d_eq;
- rotation diagnostic only;
- SPH force diagnostic;
- contact force diagnostic and separate from hydrodynamic/SPH force.

Important narrative:

- Multiple cases are summarized; the page must not look like a single fixed setup.
- Inputs varied include H, mu, and m*.
- Stable/failure class is useful, but the continuous margin to the threshold is the stronger scientific signal.
- Partial cases must be visible as partial/non-official, not hidden.

Must include:

## Section 1 - Scope and method

Show:

- number of official cases;
- stable/failure counts;
- partial cases;
- variables covered;
- common method.

Avoid a huge physical setup diagram here unless it is clearly framed as "common model geometry", not "the one case shown".

## Section 2 - Main stability map

Figure: H-mu-m* response map.

Needs:

- stable/failure color consistency;
- direct labels or symbols;
- clear axes;
- no overloaded legends;
- partial case gray;
- concise caption.

## Section 3 - Margin to threshold

This is the key scientific figure.

Show:

- margin relative to threshold;
- Dmax percent d_eq;
- absolute margin in mm where possible;
- threshold line at zero margin or 5% d_eq.

Make this figure more important than class-only plots.

## Section 4 - Batch chronology

Show how evidence accumulated:

- pilot;
- batch2;
- batch3;
- batch4;
- AL1;
- AL2 only after official export exists.

This should read as a research process, not as random scatter.

## Section 5 - Diagnostics

Include diagnostic blocks:

- local hydraulics vs displacement;
- SPH hydrodynamic force vs displacement;
- contact force separate if shown;
- rotation diagnostic vs displacement.

Captions must say diagnostics do not override displacement_only.

## Section 6 - Interaction

Graphs should be inspectable:

- click to open zoom modal;
- use SVG for zoom;
- zoom/pan/reset/close controls;
- keyboard Esc closes modal.

Deliver:

1. Improved page structure.
2. Improved visual hierarchy.
3. Revised captions.
4. Suggestions for each current figure.
5. Mobile/responsive recommendations.
6. Specific implementation handoff.

Do not invent new cases or new scientific conclusions.

