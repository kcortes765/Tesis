# Prompt 01 - Global scientific design system

You are designing the visual system for a numerical coastal engineering thesis web experience.

Read `DESIGN.md` first and follow it as the design contract.

The project:

- Thesis about incipient motion of irregular coastal boulders.
- Numerical model: DualSPHysics v5.4 + Chrono.
- No physical laboratory validation dataset.
- The web must communicate numerical verification, convergence, production batches, and active learning evidence.

Design goal:

Create a visual language that feels like a high-quality scientific paper supplement and thesis defense artifact: precise, elegant, readable, conservative, and visually impressive without being decorative.

Target audience:

- Thesis committee.
- Coastal engineering researchers.
- Numerical modeling readers.
- Future paper reviewers.

Non-negotiable scientific conventions:

- Stable = green.
- Failure = red.
- Partial/non-official = gray.
- dp=0.003 operational = amber/orange.
- dp=0.002 fine reference = blue.
- Rotation is diagnostic, not the primary failure criterion.
- Displacement is the primary class metric.
- Failure if Dmax > 5% d_eq.
- If a chart uses percent, it must also show absolute units.

Please produce:

1. A refined design direction.
2. Recommended page structure.
3. Component rules for:
   - hero/header;
   - key metrics;
   - physical setup figure;
   - scientific figure blocks;
   - tables;
   - annotations;
   - figure captions;
   - zoom/inspection behavior;
   - mobile layout.
4. A list of design anti-patterns to avoid.
5. A concise implementation handoff that Codex can apply to HTML/CSS/Python figure generators.

Do not invent data.
Do not change the scientific conclusions.
Do not rewrite the thesis methodology.
Focus on visual clarity, hierarchy, scientific trust, and elegance.

