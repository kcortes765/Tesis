# Prompt 02 - Convergence page redesign

Task:

Redesign the convergence page of the SPH thesis. The page explains why dp=0.003 m is adopted as the operational resolution. This is not a generic landing page. It is a scientific narrative.

Use:

- `DESIGN.md`
- current convergence screenshots/figures
- current convergence CSVs
- current page HTML only as reference, not as a constraint

Scientific message:

The convergence study supports dp=0.003 m as an operational resolution. It does not prove perfect or universal asymptotic convergence. The fine dp=0.002 m case is the local reference. The dp=0.003 case is close enough in main continuous variables relative to computational cost.

Must include:

## Section 1 - Physical case

Show a physical setup figure and a compact case table.

The physical case table must include:

- source log / source CSV;
- series name;
- dam height / initial water column;
- block mass;
- friction coefficient mu;
- beach slope;
- additional block rotation rot_z;
- STL name and scale;
- equivalent diameter d_eq;
- nominal position;
- channel geometry;
- gauges;
- dp values tested.

The setup figure must:

- use the real STL-derived block outline if possible;
- show plant and longitudinal elevation;
- make the block appear supported by the beach, not upright, floating, or embedded;
- label flow direction, beach slope, reservoir/water column, and block;
- state clearly if the global elevation uses vertical exaggeration.

## Section 2 - Resolution comparison

Show the key resolution evidence.

Every normalized metric must also show absolute units:

- displacement: mm and percent d_eq;
- velocity: m/s;
- water height/cota: m;
- delta versus fine reference: absolute and relative.

Do not use a table that feels like a raw database. The table should be decision-oriented.

Recommended columns:

- dp;
- role: coarse, transition, adopted, fine reference;
- Dmax mm;
- Dmax percent d_eq;
- Delta Dmax versus dp=0.002 in mm and percent;
- V block max in m/s;
- h water max in m;
- U flow max in m/s;
- accumulated rotation in deg;
- cost: particles, GPU memory, time;
- interpretation.

## Section 3 - Temporal curves

Show temporal curves for the fine range.

Needs:

- displacement in mm with secondary axis percent d_eq;
- velocity in m/s;
- water height/cota in m;
- annotations for:
  - threshold 5% d_eq = 5.02 mm;
  - dp=0.003 adopted;
  - dp=0.002 fine reference;
  - max separation if useful.

Do not make axes visually misleading. If displacement is far above the threshold in this convergence case, explain that this convergence case is not the stability frontier case.

## Section 4 - Cost and decision

Make the cost tradeoff visually obvious:

- dp=0.002 is much more expensive.
- dp=0.003 is adopted as operational.
- The decision is pragmatic and bounded.

Final page conclusion:

Use wording like:

"dp=0.003 m is adopted as the operational resolution. The main continuous variables stabilize relative to dp=0.002 m at a computational cost suitable for the production campaign. This is a resolution-sensitivity decision, not a claim of perfect asymptotic convergence."

Do not say:

- "perfect convergence";
- "universal convergence";
- "all future cases are converged";
- "stable/failure class is converged everywhere".

Deliver:

1. Proposed page layout.
2. Revised figure/card/table designs.
3. Specific text edits.
4. Graph annotation strategy.
5. HTML/CSS/component recommendations.
6. Any suggested changes to the Python figure generator.

