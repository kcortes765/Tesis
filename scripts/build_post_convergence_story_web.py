from __future__ import annotations

import html
import shutil
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "docs" / "post_convergence_story_web"
FIG = OUT / "figures"
DATA = OUT / "data"
PRODUCTION = ROOT / "data" / "figures" / "production_story_graphics"
CONVERGENCE_WEB = ROOT / "docs" / "convergence_story_web"


FIGURES = [
    ("01_response_map_h_mu_by_mass", "Mapa H-mu-masa", "Mapa operacional por masa relativa. Verde = estable; rojo = fallo; gris = parcial."),
    ("02_margin_vs_mu_by_mass_and_h", "Margen al umbral", "Margen continuo respecto de 5% de d_eq, con lectura absoluta en mm."),
    ("03_batch_story_margin_strip", "Historia de lotes", "Secuencia compacta desde piloto hasta AL1, separando exploracion y cierre de brackets."),
    ("04_local_hydraulics_vs_displacement", "Hidraulica local", "Relacion entre hmax/Umax locales y desplazamiento del bloque."),
    ("05_forces_vs_displacement", "Fuerzas diagnosticas", "Fuerzas SPH y contacto contra desplazamiento primario."),
    ("06_rotation_diagnostic_vs_displacement", "Rotacion diagnostica", "Rotacion acumulada frente al criterio displacement_only."),
    ("08_mass_effect_displacement_summary", "Efecto de masa", "Resumen del desplazamiento por masa relativa."),
]


def init() -> None:
    for path in (OUT, FIG, DATA):
        path.mkdir(parents=True, exist_ok=True)
    for folder in (FIG, DATA):
        for old in folder.glob("*"):
            if old.is_file():
                old.unlink()


def copy_assets() -> None:
    for stem, _title, _caption in FIGURES:
        for ext in ("png", "svg"):
            src = PRODUCTION / f"{stem}.{ext}"
            if src.exists():
                shutil.copy2(src, FIG / f"{stem}.{ext}")
    for name in ("master_production_story.csv", "figure_index.csv", "FIGURE_INDEX.md"):
        src = PRODUCTION / name
        if src.exists():
            shutil.copy2(src, DATA / name)


def load_master() -> pd.DataFrame:
    path = PRODUCTION / "master_production_story.csv"
    if not path.exists():
        return pd.DataFrame()
    df = pd.read_csv(path)
    for col in ("is_official", "is_partial"):
        if col in df:
            df[col] = df[col].astype(str).str.lower().isin({"true", "1", "yes"})
    return df


def summary_cards(df: pd.DataFrame) -> str:
    if df.empty:
        return ""
    official = df[df["is_official"]] if "is_official" in df else df
    partial = df[df["is_partial"]] if "is_partial" in df else df.iloc[0:0]
    stable = int((official["criterion_class"].astype(str).str.upper() == "ESTABLE").sum())
    fail = int((official["criterion_class"].astype(str).str.upper() == "FALLO").sum())
    batches = int(official["family"].nunique()) if "family" in official else 0
    cases = int(len(official))
    return f"""
      <div><dt>Casos oficiales</dt><dd>{cases}</dd></div>
      <div><dt>Estables</dt><dd>{stable}</dd></div>
      <div><dt>Fallos</dt><dd>{fail}</dd></div>
      <div><dt>Lotes cerrados</dt><dd>{batches}</dd></div>
      <div><dt>Parciales</dt><dd>{len(partial)}</dd></div>
    """


def _fmt_levels(values: pd.Series, decimals: int = 3) -> str:
    vals = pd.to_numeric(values, errors="coerce").dropna().sort_values().unique()
    if len(vals) == 0:
        return "sin dato"
    if len(vals) <= 6:
        return ", ".join(f"{v:.{decimals}f}" for v in vals)
    return f"{vals.min():.{decimals}f} a {vals.max():.{decimals}f} ({len(vals)} niveles)"


def parameter_scope(df: pd.DataFrame) -> str:
    if df.empty:
        return ""
    official = df[df["is_official"]] if "is_official" in df else df
    if official.empty:
        official = df

    h = _fmt_levels(official.get("dam_height", pd.Series(dtype=float)), 3)
    mu = _fmt_levels(official.get("friction_coefficient", pd.Series(dtype=float)), 3)
    mass = _fmt_levels(official.get("boulder_mass", pd.Series(dtype=float)), 2)
    slope = _fmt_levels(official.get("slope_inv", pd.Series(dtype=float)), 0)
    dp = _fmt_levels(official.get("dp", pd.Series(dtype=float)), 3)
    mode = ", ".join(sorted(official.get("classification_mode", pd.Series(["displacement_only"])).dropna().astype(str).unique()))
    ref = _fmt_levels(official.get("reference_time_s", pd.Series(dtype=float)), 3)

    return f"""
    <div class="scope-panel">
      <article>
        <h3>Variables barridas</h3>
        <dl>
          <div><dt>Altura hidraulica H (m)</dt><dd>{h}</dd></div>
          <div><dt>Friccion bloque-playa, mu</dt><dd>{mu}</dd></div>
          <div><dt>Masa relativa m*</dt><dd>{mass}</dd></div>
          <div><dt>Pendiente evaluada</dt><dd>1:{slope}</dd></div>
        </dl>
      </article>
      <article>
        <h3>Condiciones metodologicas comunes</h3>
        <dl>
          <div><dt>Resolucion</dt><dd>dp = {dp} m</dd></div>
          <div><dt>Criterio primario</dt><dd>{html.escape(mode)}</dd></div>
          <div><dt>Referencia temporal</dt><dd>t_ref = {ref} s</dd></div>
          <div><dt>Clase de movimiento</dt><dd>Dmax &gt; 5% d_eq</dd></div>
        </dl>
      </article>
    </div>
    """


def family_rows(df: pd.DataFrame) -> str:
    if df.empty or "family_label" not in df:
        return ""
    official = df[df["is_official"]] if "is_official" in df else df
    rows = []
    for label, sub in official.groupby("family_label", sort=False):
        stable = int((sub["criterion_class"].astype(str).str.upper() == "ESTABLE").sum())
        fail = int((sub["criterion_class"].astype(str).str.upper() == "FALLO").sum())
        med = sub["disp_pct_deq"].median() if "disp_pct_deq" in sub else float("nan")
        rows.append(
            "<tr>"
            f"<td>{html.escape(str(label))}</td>"
            f"<td>{len(sub)}</td>"
            f"<td><span class='pill stable'>{stable}</span></td>"
            f"<td><span class='pill fail'>{fail}</span></td>"
            f"<td>{med:.2f}%</td>"
            "</tr>"
        )
    return "\n".join(rows)


def figure_html() -> str:
    blocks = []
    for stem, title, caption in FIGURES:
        zoom_src = f"figures/{stem}.svg" if (FIG / f"{stem}.svg").exists() else f"figures/{stem}.png"
        blocks.append(
            f"""
      <figure class="zoomable-figure">
        <button class="figure-open" type="button" data-zoom-src="{zoom_src}" data-zoom-title="{html.escape(title)}" aria-label="Ampliar grafico: {html.escape(title)}">
          <img src="figures/{stem}.png" alt="{html.escape(title)}">
          <span class="zoom-chip">Ampliar grafico</span>
        </button>
        <figcaption><strong>{html.escape(title)}.</strong> {html.escape(caption)}</figcaption>
      </figure>
            """.strip()
        )
    return "\n".join(blocks)


def zoom_modal_html() -> str:
    return """
<div class="zoom-modal" id="figureZoom" role="dialog" aria-modal="true" aria-hidden="true" aria-label="Grafico ampliado">
  <div class="zoom-modal__panel">
    <div class="zoom-modal__bar">
      <p id="figureZoomTitle">Grafico ampliado</p>
      <div class="zoom-controls" aria-label="Controles de zoom">
        <button type="button" data-zoom-action="out" aria-label="Alejar">-</button>
        <button type="button" data-zoom-action="reset" aria-label="Restablecer zoom">100%</button>
        <button type="button" data-zoom-action="in" aria-label="Acercar">+</button>
        <button type="button" data-zoom-action="close" aria-label="Cerrar visor">Cerrar</button>
      </div>
    </div>
    <div class="zoom-modal__stage">
      <img id="figureZoomImage" alt="">
    </div>
    <p class="zoom-help">Rueda/trackpad para zoom, arrastrar para mover, doble clic para acercar, Esc para cerrar.</p>
  </div>
</div>
"""


def zoom_script_html() -> str:
    return """
<script>
(() => {
  const modal = document.getElementById("figureZoom");
  const img = document.getElementById("figureZoomImage");
  const title = document.getElementById("figureZoomTitle");
  if (!modal || !img || !title) return;

  let scale = 1;
  let panX = 0;
  let panY = 0;
  let dragging = false;
  let startX = 0;
  let startY = 0;
  let originX = 0;
  let originY = 0;

  const clampScale = (value) => Math.min(6, Math.max(0.75, value));
  const applyTransform = () => {
    img.style.transform = `translate(${panX}px, ${panY}px) scale(${scale})`;
    modal.dataset.zoomed = scale > 1.01 ? "true" : "false";
  };
  const resetZoom = () => {
    scale = 1;
    panX = 0;
    panY = 0;
    applyTransform();
  };
  const zoomBy = (factor) => {
    scale = clampScale(scale * factor);
    if (scale <= 1.01) {
      panX = 0;
      panY = 0;
    }
    applyTransform();
  };
  const openZoom = (button) => {
    const src = button.dataset.zoomSrc || button.querySelector("img")?.src;
    const label = button.dataset.zoomTitle || button.querySelector("img")?.alt || "Grafico ampliado";
    if (!src) return;
    img.src = src;
    img.alt = label;
    title.textContent = label;
    resetZoom();
    modal.classList.add("is-open");
    modal.setAttribute("aria-hidden", "false");
    document.body.classList.add("modal-open");
    modal.querySelector('[data-zoom-action="close"]')?.focus();
  };
  const closeZoom = () => {
    modal.classList.remove("is-open");
    modal.setAttribute("aria-hidden", "true");
    document.body.classList.remove("modal-open");
    img.removeAttribute("src");
  };

  document.querySelectorAll(".figure-open").forEach((button) => {
    button.addEventListener("click", () => openZoom(button));
  });

  modal.addEventListener("click", (event) => {
    if (event.target === modal) closeZoom();
  });

  modal.querySelectorAll("[data-zoom-action]").forEach((button) => {
    button.addEventListener("click", () => {
      const action = button.dataset.zoomAction;
      if (action === "in") zoomBy(1.25);
      if (action === "out") zoomBy(0.8);
      if (action === "reset") resetZoom();
      if (action === "close") closeZoom();
    });
  });

  modal.addEventListener("wheel", (event) => {
    if (!modal.classList.contains("is-open")) return;
    event.preventDefault();
    zoomBy(event.deltaY < 0 ? 1.12 : 0.9);
  }, { passive: false });

  img.addEventListener("dblclick", () => {
    if (scale < 1.5) zoomBy(2);
    else resetZoom();
  });

  img.addEventListener("pointerdown", (event) => {
    if (scale <= 1.01) return;
    dragging = true;
    startX = event.clientX;
    startY = event.clientY;
    originX = panX;
    originY = panY;
    img.setPointerCapture(event.pointerId);
  });
  img.addEventListener("pointermove", (event) => {
    if (!dragging) return;
    panX = originX + event.clientX - startX;
    panY = originY + event.clientY - startY;
    applyTransform();
  });
  img.addEventListener("pointerup", () => { dragging = false; });
  img.addEventListener("pointercancel", () => { dragging = false; });

  window.addEventListener("keydown", (event) => {
    if (!modal.classList.contains("is-open")) return;
    if (event.key === "Escape") closeZoom();
    if (event.key === "+" || event.key === "=") zoomBy(1.25);
    if (event.key === "-" || event.key === "_") zoomBy(0.8);
    if (event.key === "0") resetZoom();
  });
})();
</script>
"""


def write_page(df: pd.DataFrame) -> None:
    cards = summary_cards(df)
    scope = parameter_scope(df)
    rows = family_rows(df)
    html_text = f"""<!doctype html>
<html lang="es">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Post-convergencia SPH</title>
  <link rel="stylesheet" href="styles.css">
</head>
<body>
<main class="page">
  <header class="top">
    <p class="meta">Tesis UCN · SPH-Chrono</p>
    <h1>Post-convergencia: frontera operacional y lotes dirigidos</h1>
    <p>Esta pagina concentra lo que viene despues de fijar <code>dp=0.003 m</code>: piloto, batch2, batch3, batch4 y AL1. AL2 no se incluye hasta que termine y exista export oficial.</p>
    <p><a href="https://kcortes765.github.io/convergencia-dp/">Volver a convergencia de dp</a></p>
  </header>

  <section>
    <h2>1. Marco de lectura</h2>
    <dl class="cards">{cards}</dl>
    <p>La clase se decide por <code>displacement_only</code>: fallo si <code>Dmax &gt; 5% d_eq</code>. La rotacion, las fuerzas y las gauges son diagnosticas. En todos los graficos relevantes el desplazamiento aparece en porcentaje y en milimetros.</p>
    <p>La geometria base del canal y el bloque se mantiene como marco comun, pero esta pagina no representa una simulacion unica. Resume una familia de casos con condiciones hidraulicas, friccion y masa barridas.</p>
    {scope}
  </section>

  <section>
    <h2>2. Figuras principales</h2>
    <div class="figure-stack">
      {figure_html()}
    </div>
  </section>

  <section>
    <h2>3. Resumen por lote</h2>
    <div class="table-wrap">
      <table>
        <thead><tr><th>Lote</th><th>Casos OK</th><th>Estables</th><th>Fallos</th><th>Dmax mediano</th></tr></thead>
        <tbody>{rows}</tbody>
      </table>
    </div>
    <p class="note">Los datos fuente estan en <a href="data/master_production_story.csv">master_production_story.csv</a>. Los casos parciales se conservan como diagnostico, no como evidencia oficial para entrenar o cerrar frontera.</p>
  </section>

  <section>
    <h2>4. Lectura metodologica corta</h2>
    <p>Esta pagina no prueba convergencia adicional de <code>dp</code>. Usa la resolucion operativa ya elegida para construir una frontera practica en <code>H</code>, <code>mu</code> y <code>m*</code>. La evidencia fuerte es el margen continuo al umbral; la clase estable/fallo es una discretizacion de ese margen.</p>
    <p>Convencion visual: verde = <span class="inline-stable">ESTABLE</span>, rojo = <span class="inline-fail">FALLO</span>, gris = parcial/no oficial.</p>
  </section>
</main>
{zoom_modal_html()}
{zoom_script_html()}
</body>
</html>
"""
    (OUT / "index.html").write_text(html_text, encoding="utf-8")


def write_css() -> None:
    css = """
:root {
  --ink: #17202a;
  --muted: #536171;
  --line: #d8dee8;
  --bg: #f4f6f9;
  --paper: #ffffff;
  --green: #2f7d4f;
  --red: #b73b3b;
}
* { box-sizing: border-box; }
body {
  margin: 0;
  font-family: Arial, Helvetica, sans-serif;
  color: var(--ink);
  background: var(--bg);
  line-height: 1.5;
}
.page {
  width: min(1160px, calc(100% - 32px));
  margin: 0 auto;
  padding: 22px 0 48px;
}
.top {
  border-bottom: 1px solid var(--line);
  padding-bottom: 16px;
  margin-bottom: 14px;
}
.meta {
  margin: 0 0 6px;
  color: var(--muted);
  font-size: 13px;
  text-transform: uppercase;
  letter-spacing: .04em;
}
h1 {
  margin: 0 0 10px;
  font-size: clamp(29px, 3.4vw, 40px);
  line-height: 1.08;
  max-width: 880px;
}
h2 { font-size: 22px; margin: 0 0 12px; }
p { margin: 0 0 12px; }
a { color: #255f91; text-underline-offset: 2px; }
section {
  background: var(--paper);
  border: 1px solid var(--line);
  border-radius: 4px;
  padding: 20px;
  margin: 18px 0;
}
.cards {
  display: grid;
  grid-template-columns: repeat(5, minmax(0, 1fr));
  gap: 0;
  margin: 0 0 16px;
  border: 1px solid var(--line);
  background: #fbfcfe;
}
.cards div {
  padding: 10px 14px;
  border-right: 1px solid var(--line);
}
.cards div:last-child { border-right: 0; }
.scope-panel {
  display: grid;
  grid-template-columns: minmax(0, 1fr) minmax(0, 1fr);
  gap: 14px;
  margin-top: 14px;
}
.scope-panel article {
  border: 1px solid var(--line);
  background: #fbfcfe;
  border-radius: 4px;
  padding: 14px;
}
.scope-panel h3 {
  margin: 0 0 10px;
  font-size: 16px;
}
.scope-panel dl {
  margin: 0;
}
.scope-panel dl div {
  display: grid;
  grid-template-columns: 190px minmax(0, 1fr);
  gap: 10px;
  padding: 7px 0;
  border-top: 1px solid #e4e9f0;
}
.scope-panel dl div:first-child { border-top: 0; }
dt { font-weight: 700; }
dd { margin: 2px 0 0; color: var(--muted); }
.figure-stack {
  display: grid;
  grid-template-columns: minmax(0, 1fr);
  gap: 18px;
  justify-items: center;
}
figure {
  width: min(1080px, 100%);
  margin: 14px 0 6px;
  border: 1px solid var(--line);
  background: white;
  padding: 10px;
  border-radius: 4px;
}
.figure-open {
  position: relative;
  display: block;
  width: 100%;
  padding: 0;
  border: 0;
  background: transparent;
  cursor: zoom-in;
}
.figure-open img {
  display: block;
  width: 100%;
  height: auto;
}
.figure-open:focus-visible {
  outline: 3px solid #255f91;
  outline-offset: 4px;
}
.zoom-chip {
  position: absolute;
  right: 10px;
  top: 10px;
  border: 1px solid rgba(23, 32, 42, .16);
  background: rgba(255, 255, 255, .92);
  color: var(--ink);
  border-radius: 999px;
  padding: 5px 10px;
  font-size: 12px;
  font-weight: 700;
  box-shadow: 0 2px 10px rgba(23, 32, 42, .08);
}
figcaption {
  color: var(--muted);
  font-size: 13px;
  margin-top: 8px;
}
.table-wrap { overflow-x: auto; border: 1px solid var(--line); }
table { width: 100%; border-collapse: collapse; font-size: 13px; }
th, td { border-bottom: 1px solid var(--line); padding: 8px 9px; text-align: left; }
th { background: #eef2f6; }
.pill {
  display: inline-block;
  border-radius: 3px;
  padding: 2px 6px;
  font-weight: 700;
  font-size: 12px;
}
.pill.fail, .inline-fail { color: #7c1f1f; background: #f8e6e6; }
.pill.stable, .inline-stable { color: #1f5a39; background: #e5f2ea; }
.inline-fail, .inline-stable { padding: 1px 5px; border-radius: 3px; font-weight: 700; }
.note {
  border-left: 4px solid #aab4c0;
  background: #f7f9fc;
  padding: 10px 12px;
  margin-top: 14px;
}
code {
  background: #eef2f6;
  padding: 1px 4px;
  border-radius: 3px;
}
body.modal-open { overflow: hidden; }
.zoom-modal {
  position: fixed;
  inset: 0;
  z-index: 50;
  display: none;
  align-items: center;
  justify-content: center;
  padding: 20px;
  background: rgba(13, 20, 29, .78);
}
.zoom-modal.is-open { display: flex; }
.zoom-modal__panel {
  width: min(1440px, 100%);
  max-height: min(900px, calc(100vh - 40px));
  display: grid;
  grid-template-rows: auto minmax(0, 1fr) auto;
  border: 1px solid rgba(255, 255, 255, .2);
  border-radius: 6px;
  background: #fbfcfe;
  box-shadow: 0 24px 70px rgba(0, 0, 0, .32);
  overflow: hidden;
}
.zoom-modal__bar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
  padding: 10px 12px;
  border-bottom: 1px solid var(--line);
  background: #ffffff;
}
.zoom-modal__bar p {
  margin: 0;
  font-weight: 700;
}
.zoom-controls {
  display: flex;
  gap: 6px;
  align-items: center;
  flex-wrap: wrap;
}
.zoom-controls button {
  border: 1px solid #c8d1dc;
  background: #f5f7fa;
  color: var(--ink);
  border-radius: 4px;
  padding: 6px 9px;
  font-weight: 700;
  cursor: pointer;
}
.zoom-controls button:hover,
.zoom-controls button:focus-visible {
  background: #e8eef5;
}
.zoom-modal__stage {
  min-height: 260px;
  overflow: hidden;
  display: grid;
  place-items: center;
  background:
    linear-gradient(90deg, rgba(216,222,232,.45) 1px, transparent 1px),
    linear-gradient(0deg, rgba(216,222,232,.45) 1px, transparent 1px),
    #f6f8fb;
  background-size: 32px 32px;
}
.zoom-modal__stage img {
  display: block;
  width: min(1360px, 92vw);
  max-height: 78vh;
  height: auto;
  transform-origin: center center;
  transition: transform .08s ease-out;
  user-select: none;
  touch-action: none;
  cursor: zoom-in;
}
.zoom-modal[data-zoomed="true"] .zoom-modal__stage img {
  cursor: grab;
}
.zoom-modal[data-zoomed="true"] .zoom-modal__stage img:active {
  cursor: grabbing;
}
.zoom-help {
  margin: 0;
  padding: 8px 12px 10px;
  color: var(--muted);
  font-size: 12px;
  border-top: 1px solid var(--line);
  background: #ffffff;
}
@media (max-width: 860px) {
  .cards { grid-template-columns: 1fr; }
  .cards div { border-right: 0; border-bottom: 1px solid var(--line); }
  .cards div:last-child { border-bottom: 0; }
  .scope-panel { grid-template-columns: 1fr; }
  .scope-panel dl div { grid-template-columns: 1fr; gap: 2px; }
  section { padding: 16px; }
  .zoom-modal { padding: 10px; }
  .zoom-modal__bar { align-items: flex-start; flex-direction: column; }
  .zoom-controls button { padding: 7px 9px; }
}
"""
    (OUT / "styles.css").write_text(css, encoding="utf-8")


def main() -> None:
    init()
    copy_assets()
    df = load_master()
    write_page(df)
    write_css()
    print(f"Post-convergence web generated: {OUT / 'index.html'}")


if __name__ == "__main__":
    main()
