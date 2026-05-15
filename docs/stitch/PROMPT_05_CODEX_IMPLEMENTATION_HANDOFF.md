# Prompt 05 - Codex implementation handoff after Stitch

Use this after Stitch gives a design direction.

We are implementing the design in:

- `C:\Users\Admin\Desktop\SPH-Tesis`
- convergence generator: `scripts/build_convergence_story_web.py`
- post-convergence generator: `scripts/build_post_convergence_story_web.py`
- convergence output: `docs/convergence_story_web/`
- post-convergence output: `docs/post_convergence_story_web/`
- GitHub Pages copy: `C:\Users\Admin\Desktop\convergencia-dp`

Implementation rules:

- Modify source generators, not only generated HTML.
- Regenerate pages after changes.
- Do not modify scientific values manually.
- Do not run simulations.
- Do not touch `cases/`, `_out/`, `.bi4`, `.ibi4`, VTK, Part files, or raw heavy outputs.
- Do not commit `data/results.sqlite` while simulations are running.
- Preserve zoom behavior in post-convergence figures.
- Preserve source CSV links.
- Use SVG/PNG exports from current figure pipeline.

Required verification:

1. Regenerate convergence page.
2. Regenerate post-convergence page.
3. Confirm no broken image paths.
4. Confirm post-convergence zoom modal still works.
5. Confirm stable/failure colors are consistent.
6. Confirm percentage metrics have absolute units.
7. Confirm captions do not overclaim convergence.
8. Copy to GitHub Pages repo.
9. Commit/push both repos.

Expected final report:

- files changed;
- figures regenerated;
- page links;
- key visual changes;
- any scientific caveats preserved;
- git commit hashes.

