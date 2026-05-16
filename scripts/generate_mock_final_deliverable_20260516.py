from __future__ import annotations

from math import erf, sqrt
from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "docs" / "mock_final_deliverable_20260516"
FIG = OUT / "figures"
DATA = OUT / "data"


def normal_cdf(x: np.ndarray | float, mean: float, std: float) -> np.ndarray | float:
    z = (np.asarray(x) - mean) / (std * sqrt(2.0))
    return 0.5 * (1.0 + np.vectorize(erf)(z))


def mu_crit(h: np.ndarray | float, mstar: float) -> np.ndarray | float:
    h = np.asarray(h)
    # Synthetic state-limit surface: stronger hydraulic forcing raises mu_crit;
    # heavier blocks lower mu_crit. This is only a visual mock.
    return 0.565 + 4.25 * (h - 0.175) + 0.45 * (1.0 - mstar) + 0.018 * np.sin((h - 0.175) * 60)


def make_dirs() -> None:
    for path in (OUT, FIG, DATA):
        path.mkdir(parents=True, exist_ok=True)
    for folder in (FIG, DATA):
        for old in folder.glob("*"):
            if old.is_file():
                old.unlink()


def synthetic_cases() -> pd.DataFrame:
    rng = np.random.default_rng(1616)
    rows = []
    for mstar in [0.85, 1.0, 1.15, 1.25]:
        for h in [0.175, 0.2, 0.21, 0.225]:
            center = float(mu_crit(h, mstar))
            for dmu in [-0.045, -0.015, 0.018, 0.055]:
                mu = np.clip(center + dmu + rng.normal(0, 0.006), 0.55, 0.9)
                margin = 55 * (mu - center) + rng.normal(0, 0.7)
                cls = "ESTABLE" if margin > 0 else "FALLO"
                rows.append(
                    {
                        "H": h,
                        "mu": mu,
                        "mstar": mstar,
                        "g_margin_pct_deq": margin,
                        "Dmax_pct_deq": 5 - margin,
                        "class": cls,
                    }
                )
    return pd.DataFrame(rows)


def save(fig: plt.Figure, name: str) -> None:
    fig.savefig(FIG / f"{name}.png", dpi=260, bbox_inches="tight")
    fig.savefig(FIG / f"{name}.svg", bbox_inches="tight")
    plt.close(fig)


def plot_frontier(cases: pd.DataFrame) -> None:
    h_grid = np.linspace(0.175, 0.225, 160)
    mu_grid = np.linspace(0.55, 0.9, 160)
    hh, mm = np.meshgrid(h_grid, mu_grid)

    fig, axes = plt.subplots(2, 2, figsize=(12, 8.4), sharex=True, sharey=True)
    axes = axes.ravel()
    for ax, mstar in zip(axes, [0.85, 1.0, 1.15, 1.25]):
        g = 55 * (mm - mu_crit(hh, mstar))
        ax.contourf(mu_grid, h_grid, g.T, levels=[-12, -8, -4, 0, 4, 8, 12], cmap="RdYlGn", alpha=0.82)
        ax.contour(mu_grid, h_grid, g.T, levels=[0], colors="#101820", linewidths=2.4)
        sub = cases[cases["mstar"] == mstar]
        for cls, marker, color in [("ESTABLE", "o", "#2F7D4F"), ("FALLO", "^", "#B73B3B")]:
            s = sub[sub["class"] == cls]
            ax.scatter(s["mu"], s["H"], s=72, marker=marker, color=color, edgecolor="white", linewidth=0.9, label=cls)
        ax.set_title(f"m* = {mstar:.2f}")
        ax.set_xlabel("friccion bloque-suelo, mu")
        ax.grid(True, alpha=0.18)
        ax.text(0.02, 0.03, "DATOS SINTETICOS", transform=ax.transAxes, fontsize=8.5, color="#6d5b00")
    axes[0].set_ylabel("altura hidraulica H (m)")
    axes[2].set_ylabel("altura hidraulica H (m)")
    handles, labels = axes[0].get_legend_handles_labels()
    fig.legend(handles[:2], labels[:2], loc="lower center", ncol=2, frameon=True)
    fig.suptitle("Resultado final esperado: frontera de movimiento incipiente")
    save(fig, "fig01_frontera_estado_limite")


def plot_fragility() -> None:
    h = np.linspace(0.175, 0.225, 180)
    fig, ax = plt.subplots(figsize=(9.4, 5.4))
    for mstar, color in [(0.85, "#8C5E3C"), (1.0, "#2B6F9F"), (1.15, "#B98524"), (1.25, "#6A4C93")]:
        central = normal_cdf(mu_crit(h, mstar), mean=0.72, std=0.055)
        lower = normal_cdf(mu_crit(h, mstar), mean=0.735, std=0.06)
        upper = normal_cdf(mu_crit(h, mstar), mean=0.705, std=0.05)
        ax.plot(h, central, color=color, lw=2.5, label=f"m*={mstar:.2f}")
        ax.fill_between(h, lower, upper, color=color, alpha=0.13, linewidth=0)
    ax.set_ylim(0, 1)
    ax.set_xlabel("altura hidraulica H (m)")
    ax.set_ylabel("probabilidad condicional de movimiento, Pf")
    ax.set_title("Curvas de fragilidad condicional derivadas del surrogate")
    ax.grid(True, alpha=0.2)
    ax.legend(frameon=True, ncol=2)
    ax.text(0.176, 0.06, "DATOS SINTETICOS: ejemplo de forma del resultado", fontsize=9, color="#6d5b00")
    save(fig, "fig02_fragilidad_condicional")


def plot_validation() -> None:
    labels = [
        "Benchmark\nhidraulico",
        "Sanity\ncontacto",
        "Analitico\norden magnitud",
        "Holdout\nGP",
        "dp=0.002\nselectivo",
        "Repeticion\nfrontera",
    ]
    values = np.array([0.86, 0.92, 0.78, 0.84, 0.74, 0.70])
    colors = ["#2F7D4F", "#2F7D4F", "#B98524", "#2B6F9F", "#B98524", "#B98524"]
    fig, ax = plt.subplots(figsize=(10.6, 4.6))
    ax.bar(labels, values * 100, color=colors, edgecolor="#252525", linewidth=0.6)
    ax.axhline(70, color="#555555", lw=1.0, ls="--")
    ax.set_ylim(0, 100)
    ax.set_ylabel("puntaje / cumplimiento sintetico (%)")
    ax.set_title("Cierre metodologico por capas")
    ax.grid(axis="y", alpha=0.18)
    for i, value in enumerate(values):
        ax.text(i, value * 100 + 2, f"{value*100:.0f}%", ha="center", fontsize=9)
    ax.text(-0.45, 8, "DATOS SINTETICOS", fontsize=9, color="#6d5b00")
    save(fig, "fig03_cierre_metodologico")


def write_html(cases: pd.DataFrame) -> None:
    cases.to_csv(DATA / "synthetic_cases.csv", index=False)
    html = """<!doctype html>
<html lang="es">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Mock entregable final - Tesis SPH-Chrono</title>
  <style>
    body { margin: 0; font-family: Arial, Helvetica, sans-serif; color: #17202a; background: #f4f6f9; line-height: 1.5; }
    main { width: min(1120px, calc(100% - 32px)); margin: 0 auto; padding: 24px 0 48px; }
    header, section { background: white; border: 1px solid #d8dee8; border-radius: 4px; padding: 20px; margin: 16px 0; }
    .meta { color: #526070; text-transform: uppercase; letter-spacing: .04em; font-size: 13px; margin: 0 0 6px; }
    h1 { margin: 0 0 10px; font-size: 34px; line-height: 1.1; }
    h2 { margin: 0 0 12px; font-size: 22px; }
    .notice { border-left: 5px solid #b98524; background: #fff8e7; padding: 10px 12px; }
    .cards { display: grid; grid-template-columns: repeat(4, 1fr); border: 1px solid #d8dee8; margin: 14px 0; }
    .cards div { padding: 12px; border-right: 1px solid #d8dee8; }
    .cards div:last-child { border-right: 0; }
    dt { font-weight: 700; }
    dd { margin: 2px 0 0; color: #526070; }
    code { background: #eef2f6; border-radius: 3px; padding: 1px 4px; }
    figure { margin: 18px 0; border: 1px solid #d8dee8; padding: 10px; background: white; }
    figure img { width: 100%; height: auto; display: block; }
    figcaption { color: #526070; font-size: 13px; margin-top: 8px; }
    table { width: 100%; border-collapse: collapse; font-size: 14px; }
    th, td { border-bottom: 1px solid #d8dee8; padding: 8px; text-align: left; }
    th { background: #eef2f6; }
    @media (max-width: 760px) { .cards { grid-template-columns: 1fr; } .cards div { border-right: 0; border-bottom: 1px solid #d8dee8; } }
  </style>
</head>
<body>
<main>
  <header>
    <p class="meta">Mock sintetico - no usar como resultado</p>
    <h1>Frontera probabilistica de movimiento incipiente de un bloque costero</h1>
    <p>Este mock muestra la forma esperada del entregable final: no seria solo una ecuacion ni solo un grafico, sino un paquete corto con estado limite, frontera, fragilidad, validacion y limites de interpretacion.</p>
    <p class="notice"><strong>Importante:</strong> las figuras usan datos sinteticos para ensayar presentacion. El formato busca mostrar que recibiria el profesor cuando la campana real este cerrada.</p>
  </header>

  <section>
    <h2>1. Resultado central</h2>
    <p>El resultado final se reportaria como una superficie de estado limite condicionada a la geometria base, contacto, pendiente y resolucion productiva:</p>
    <p><code>g(H, mu, m*) = 0.05 - Dmax(H, mu, m*) / d_eq</code></p>
    <p>Si <code>g &gt; 0</code>, el bloque queda bajo el umbral operacional de movimiento. Si <code>g &lt; 0</code>, supera el umbral. El GP no reemplaza las simulaciones: interpola el margen y entrega incertidumbre para decidir nuevos casos.</p>
    <dl class="cards">
      <div><dt>Variable hidraulica</dt><dd>H, altura inicial dam-break</dd></div>
      <div><dt>Resistencia</dt><dd>mu, friccion bloque-suelo</dd></div>
      <div><dt>Masa relativa</dt><dd>m* = m / m_base</dd></div>
      <div><dt>Salida primaria</dt><dd>Dmax / d_eq</dd></div>
    </dl>
  </section>

  <section>
    <h2>2. Frontera final</h2>
    <figure>
      <img src="figures/fig01_frontera_estado_limite.png" alt="Frontera sintetica de movimiento incipiente">
      <figcaption><strong>Figura final tipo 1.</strong> Cortes H-mu para distintas masas relativas. La curva negra es la frontera g=0. Verde indica margen estable; rojo indica movimiento. Los puntos son simulaciones SPH-Chrono.</figcaption>
    </figure>
  </section>

  <section>
    <h2>3. Fragilidad condicional</h2>
    <figure>
      <img src="figures/fig02_fragilidad_condicional.png" alt="Curvas sinteticas de fragilidad condicional">
      <figcaption><strong>Figura final tipo 2.</strong> Probabilidad condicional de movimiento contra H, integrando incertidumbre en mu y en el surrogate. Esto traduce la frontera a una lectura probabilistica.</figcaption>
    </figure>
  </section>

  <section>
    <h2>4. Validacion por capas</h2>
    <figure>
      <img src="figures/fig03_cierre_metodologico.png" alt="Cierre metodologico sintetico">
      <figcaption><strong>Figura final tipo 3.</strong> Resumen de defensibilidad: benchmark hidraulico, sanity de contacto, contraste analitico, holdout GP, checks finos de dp y repeticiones cercanas a frontera.</figcaption>
    </figure>
  </section>

  <section>
    <h2>5. Tabla que podria recibir el profesor</h2>
    <table>
      <thead><tr><th>Salida</th><th>Que entrega</th><th>Como se interpreta</th></tr></thead>
      <tbody>
        <tr><td>Superficie g=0</td><td>Frontera H-mu-m*</td><td>Indica combinaciones donde inicia movimiento segun Dmax &gt; 5% d_eq.</td></tr>
        <tr><td>Curvas Pf(H)</td><td>Fragilidad condicional</td><td>Probabilidad de movimiento bajo distribuciones asumidas de mu y m*.</td></tr>
        <tr><td>Holdout GP</td><td>Validacion interna</td><td>Mide si el surrogate predice casos no usados para entrenar.</td></tr>
        <tr><td>dp=0.002 selectivo</td><td>Sensibilidad de resolucion</td><td>Cuantifica cuanto se mueve la frontera cerca del umbral.</td></tr>
        <tr><td>Comparacion analitica</td><td>Coherencia fisica</td><td>Verifica orden de magnitud, no reemplaza SPH-Chrono.</td></tr>
      </tbody>
    </table>
  </section>

  <section>
    <h2>6. Frase final esperada</h2>
    <p>La contribucion no seria decir "el bloque falla en un mu exacto", sino entregar una frontera condicionada y cuantificada: para una geometria, resolucion y criterio definidos, el movimiento incipiente se describe por una superficie <code>g(H, mu, m*)=0</code>, con incertidumbre del surrogate, sensibilidad de resolucion y verificaciones independientes del pipeline numerico.</p>
  </section>
</main>
</body>
</html>
"""
    (OUT / "index.html").write_text(html, encoding="utf-8")


def main() -> None:
    make_dirs()
    cases = synthetic_cases()
    plot_frontier(cases)
    plot_fragility()
    plot_validation()
    write_html(cases)
    print(f"Mock final deliverable written to {OUT / 'index.html'}")


if __name__ == "__main__":
    main()
