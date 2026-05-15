# Prompt 04 - Graph redesign brief

Task:

Provide a detailed visual redesign brief for the current scientific graphs. Focus on clarity, elegance, and paper-quality readability.

Use the attached current graph images as visual references and the attached CSV files as source data. Do not infer data from the images.

Global requirements:

- Use white or near-white background.
- Use stable green and failure red consistently.
- Use gray for diagnostic/partial.
- Use amber/orange for dp=0.003 operational.
- Use blue for dp=0.002 fine reference.
- Use direct labels where possible.
- Use units on every axis.
- Avoid label overlap.
- Avoid tiny legends.
- Avoid ambiguous color scales.
- Avoid rotated labels unless necessary.
- When percent is shown, also show absolute units.

## Convergence graphs

### Setup figure

The current setup figure should be improved to look precise, physical, and based on the real STL.

Needs:

- plant view and elevation view;
- real STL silhouette or explicitly labeled schematic;
- block supported on beach, not vertical or embedded;
- beach slope 1:20;
- flow direction;
- reservoir height H;
- block label;
- vertical exaggeration note if used.

### Variables defending dp=0.003

Needs:

- show percent difference and absolute difference;
- label dp=0.003 as operational;
- label dp=0.002 as fine reference;
- avoid making a 6% difference look identical to zero;
- clear takeaway: practical stabilization, not perfect convergence.

### Temporal fine curves

Needs:

- displacement in mm and percent d_eq;
- velocity in m/s;
- water height/cota in m;
- threshold annotation 5% d_eq = 5.02 mm;
- line labels close to curves;
- visual distinction between dp=0.003 and dp=0.002;
- explain if "max temporal separation" differs from "difference between global maxima".

### Cost plot

Needs:

- show runtime and particles/GPU cost cleanly;
- make dp=0.002 cost jump obvious;
- show why dp=0.003 is the practical choice.

## Post-convergence graphs

### H-mu-m* map

Needs:

- readable small multiples by mass;
- stable/failure/partial labels;
- not overpacked;
- visible frontier hints;
- clear indication that this is dp=0.003 operational.

### Margin plot

Needs:

- margin in percent d_eq and mm;
- threshold or zero-margin line;
- clear stable/failure regions;
- highlight near-frontier cases.

### Batch story strip

Needs:

- chronological flow;
- show batches as evidence accumulation;
- avoid "rainbow scatter" feel;
- separate exploratory from bracket-closing cases.

### Local hydraulics and forces

Needs:

- separate SPH hydrodynamic force from contact force;
- do not imply contact force is the failure criterion;
- show diagnostics as explanatory variables.

### Rotation diagnostic

Needs:

- clearly label "accumulated rotation";
- state "diagnostic, not class criterion";
- avoid visual design that makes rotation appear to override displacement.

Deliver:

1. Recommended chart types.
2. Annotation plan.
3. Color/legend plan.
4. Table/tooltip plan.
5. What to remove.
6. What to enlarge.
7. What to keep as supplementary.
8. Implementation notes for Python/Matplotlib/SVG/HTML.

