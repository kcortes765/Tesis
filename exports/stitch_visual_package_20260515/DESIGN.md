---
version: alpha
name: SPH Thesis Scientific Editorial
description: Visual system for the SPH-Chrono coastal boulder thesis, convergence web, post-convergence web, and thesis-ready figures.
colors:
  ink: "#17202A"
  ink_soft: "#344252"
  muted: "#5B6770"
  paper: "#FAFAF7"
  panel: "#FFFFFF"
  panel_alt: "#F4F6F9"
  line: "#D8DEE8"
  grid: "#E7EBF0"
  water: "#2B7BB9"
  water_light: "#BBD9EA"
  beach: "#B59A63"
  beach_light: "#E8DDC5"
  boulder: "#5E5042"
  stable: "#2E7D32"
  failure: "#C62828"
  partial: "#7A7F87"
  operational: "#C77C02"
  fine_reference: "#1565C0"
  diagnostic: "#6B7280"
typography:
  headline:
    family: "Inter, Arial, Helvetica, sans-serif"
    size: "34px"
    weight: 720
    line_height: 1.12
    letter_spacing: "0"
  section:
    family: "Inter, Arial, Helvetica, sans-serif"
    size: "23px"
    weight: 680
    line_height: 1.22
    letter_spacing: "0"
  body:
    family: "Inter, Arial, Helvetica, sans-serif"
    size: "16px"
    weight: 400
    line_height: 1.55
    letter_spacing: "0"
  data:
    family: "IBM Plex Mono, Consolas, monospace"
    size: "13px"
    weight: 500
    line_height: 1.35
    letter_spacing: "0"
radii:
  small: "4px"
  medium: "6px"
spacing:
  xs: "4px"
  sm: "8px"
  md: "16px"
  lg: "24px"
  xl: "40px"
---

# SPH Thesis Scientific Editorial

This file is the visual contract for the thesis web pages and scientific figures. It is designed for agentic design tools such as Stitch, Codex, or any frontend agent. It must be treated as the visual source of truth unless the user explicitly changes it.

## Project Identity

The project is a numerical coastal engineering thesis: incipient motion of irregular coastal boulders under tsunami-like flows using DualSPHysics v5.4 + Chrono. There is no physical laboratory dataset. The visual language must therefore be precise, auditable, conservative, and thesis/paper appropriate.

The design should feel like a high-quality scientific supplement, not a marketing landing page. Beauty comes from clean hierarchy, good spacing, readable plots, direct labels, consistent colors, and honest uncertainty.

## Core Visual Promise

Every visual must answer three questions quickly:

1. What physical case or family of cases is shown?
2. What metric is being compared, with units?
3. What conclusion is allowed, and what is not allowed?

## Color Semantics

Use color consistently:

- Stable: green `stable`.
- Failure: red `failure`.
- Partial or non-official result: gray `partial`.
- Operational resolution dp=0.003: amber/orange `operational`.
- Fine reference dp=0.002: blue `fine_reference`.
- Diagnostic variables such as rotation/contact force: gray `diagnostic`.
- Water/hydraulics: blue `water`.
- Beach/slope: sand/brown `beach`.
- Boulder/STL: dark brown `boulder`.

Never rely on color alone. Always pair stable/failure with text labels, shape, or annotation.

## Typography Rules

- Use restrained scientific typography.
- No negative letter spacing.
- No viewport-scaled font sizes that break labels.
- Titles should be short and claim-oriented.
- Figure labels must be readable on projector and laptop.
- Tables use data font only for case ids, paths, or numeric compact columns.

## Layout Rules

- Prefer a single-column editorial story.
- Use full-width sections rather than nested cards.
- Cards are allowed only for repeated summaries, metrics, or figure panels.
- Do not put cards inside cards.
- Keep border radius at 4-6 px.
- Use white or near-white backgrounds for print compatibility.
- Use enough whitespace, but avoid large empty hero gaps.
- Avoid decorative orbs, gradients, bokeh, vague science backgrounds, or generic stock visuals.

## Scientific Figure Rules

Every figure must have:

- A short title.
- Axes with units.
- Direct labels whenever possible.
- A concise caption that states what the viewer should learn.
- Source note or data path when the figure is derived.
- Consistent colors for stable/failure/operational/reference.

If a plot uses a normalized percentage, it must also show an absolute quantity:

- Displacement: mm and percent of d_eq.
- Margin: percent of d_eq and mm.
- Velocity: m/s; if normalized, include m/s.
- Height/cota: m; if normalized, include m.
- Force: N; separate SPH hydrodynamic force from contact force.
- Rotation: accumulated degrees; label it as diagnostic.

## Convergence Page Rules

Purpose: justify dp=0.003 m as an operational resolution.

Allowed claim:

`dp=0.003 m is adopted as an operational resolution because the main continuous variables are close enough to the fine dp=0.002 m reference relative to the available computational cost.`

Forbidden claims:

- Do not say convergence is perfect.
- Do not say convergence is asymptotically proven for all production cases.
- Do not say stable/failure class itself converged universally.

The convergence page must separate:

1. Physical case used for convergence.
2. Continuous variable comparison by dp.
3. Cost of refinement.
4. Operational decision.
5. Limitations and later selective dp=0.002 checks.

The setup diagram must use the actual `models/BLIR3.stl` outline or clearly state if it is schematic. The block must appear supported on the beach with its long/base direction approximately parallel to the local beach, not upright or embedded.

## Post-Convergence Page Rules

Purpose: summarize production/pilot/active-learning evidence after dp selection.

Allowed claim:

`At dp=0.003 m, directed batches map a practical stability boundary in H, mu, and m*.`

Forbidden claims:

- Do not present post-convergence batches as new dp convergence.
- Do not use rotation as the primary class criterion.
- Do not hide partial runs.
- Do not mix old non-comparable runs into the main frontier.

The post-convergence page must make clear:

- It summarizes multiple cases, not one physical setup.
- Common methodology: dp=0.003, displacement_only, reference_time_s=0.5.
- Inputs varied: H, mu, m*, slope only where relevant.
- Class rule: failure if Dmax > 5% d_eq.
- Rotation is diagnostic.

## Tables

Tables should not be dumps. They should be compressed decision aids.

For convergence:

- Include a physical-case table: H, mass, mu, slope, rot_z, STL, d_eq, position, simulation time, gauges.
- Include a resolution table: dp, Dmax mm, Dmax percent d_eq, delta vs dp=0.002 in mm and percent, Vmax, hmax, Umax, accumulated rotation, particles, GPU memory, runtime, interpretation.
- Remove internal columns such as case id unless the table is explicitly for audit.

For post-convergence:

- Include family/batch summary.
- Include main official cases or downloadable CSV, not all rows on the landing view.
- Clearly mark partial/non-official data.

## Interaction

The post-convergence page should allow graph inspection:

- Click a graph to open a zoom modal.
- Prefer SVG in zoom mode.
- Provide zoom in/out/reset/close.
- Support pan/drag when zoomed.
- Keyboard Esc closes modal.

Do not use heavy JS frameworks unless necessary.

## Accessibility

- Maintain contrast suitable for projection and print.
- Provide alt text for all images.
- Do not encode stable/failure only through red/green.
- Keep tables horizontally scrollable on mobile.
- Do not overlap annotations.
- Avoid rotated tick labels unless absolutely necessary.

## Implementation Guidance

The data source remains the local repository:

- `docs/convergence_story_web/data/*.csv`
- `docs/post_convergence_story_web/data/*.csv`
- `data/results/*.csv`
- `data/results.sqlite`
- scripts that generate figures

Stitch may propose layout and visual hierarchy, but should not invent or modify scientific values.

