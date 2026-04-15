"""
plot_03_convergence_metrics_only.py

Genera solo el grafico 03 de convergencia corregida, en una version mas limpia:
- eje x categorico por dp
- caso parcial mu=0.710 soportado sin deformar el eje
- anotaciones compactas por punto
"""

from __future__ import annotations

from pathlib import Path

import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

matplotlib.use("Agg")


PROJECT = Path(__file__).resolve().parent.parent
RESULTS = PROJECT / "data" / "results"
OUTDIR = PROJECT / "data" / "figures" / "corrected_story"
OUTDIR.mkdir(parents=True, exist_ok=True)

DEQ_M = 0.100421
DISP_THRESHOLD_MM = 0.05 * DEQ_M * 1000.0
ROT_THRESHOLD_DEG = 5.0

DP_ORDER = [0.004, 0.003, 0.002]
DP_LABELS = ["0.004", "0.003", "0.002"]
XPOS = np.arange(len(DP_ORDER))

MU_COLORS = {
    0.700: "#1f77b4",
    0.710: "#d62728",
}


def classify_joint(disp_m: float, rot_deg: float) -> str:
    if disp_m > 0.05 * DEQ_M:
        return "FALLO"
    if pd.notna(rot_deg) and rot_deg > ROT_THRESHOLD_DEG:
        return "FALLO"
    return "ESTABLE"


def load_conv(prefix: str, mu: float) -> pd.DataFrame:
    path = RESULTS / f"{prefix}.csv"
    if not path.exists():
        return pd.DataFrame()

    df = pd.read_csv(path, sep=";")
    if df.empty:
        return pd.DataFrame()

    df = df[df["status"] == "OK"].copy()
    if df.empty:
        return pd.DataFrame()

    df["mu"] = mu
    df["disp_mm"] = df["max_displacement_m"] * 1000.0
    df["class_joint"] = df.apply(
        lambda r: classify_joint(r["max_displacement_m"], r["max_rotation_deg"]),
        axis=1,
    )
    df["dp"] = df["dp"].astype(float)
    df["x"] = df["dp"].map({dp: i for i, dp in enumerate(DP_ORDER)})
    return df.sort_values("x").reset_index(drop=True)


def annotate_points(ax: plt.Axes, df: pd.DataFrame, col: str, color: str) -> None:
    for i, row in df.iterrows():
        dx = 0.03 if row["mu"] == 0.700 else -0.03
        dy = 0.0
        if col == "disp_mm":
            dy = 0.06
        elif col == "max_velocity_ms":
            dy = 0.0006
        elif col == "max_sph_force_N":
            dy = 0.12
        elif col == "max_rotation_deg":
            dy = 0.05

        ha = "left" if row["mu"] == 0.700 else "right"
        ax.text(
            row["x"] + dx,
            row[col] + dy,
            row["class_joint"],
            fontsize=8,
            color=color,
            ha=ha,
            va="bottom",
        )


def plot_metric(ax: plt.Axes, col: str, ylabel: str, conv700: pd.DataFrame, conv710: pd.DataFrame) -> None:
    for mu, df in [(0.700, conv700), (0.710, conv710)]:
        if df.empty:
            continue
        color = MU_COLORS[mu]
        ax.plot(
            df["x"],
            df[col],
            marker="o",
            linewidth=2.0,
            markersize=6,
            color=color,
            label=f"mu={mu:.3f}",
        )
        annotate_points(ax, df, col, color)

    if col == "disp_mm":
        ax.axhline(DISP_THRESHOLD_MM, color="black", linestyle="--", linewidth=1.0, label="umbral disp")
    if col == "max_rotation_deg":
        ax.axhline(ROT_THRESHOLD_DEG, color="black", linestyle="--", linewidth=1.0, label="umbral rot")

    ax.set_xticks(XPOS)
    ax.set_xticklabels(DP_LABELS)
    ax.set_xlabel("dp [m]")
    ax.set_ylabel(ylabel)
    ax.set_title(ylabel)
    ax.grid(True, alpha=0.25)
    ax.legend(fontsize=8)


def main() -> None:
    conv700 = load_conv("conv_fix_f0700_full", 0.700)
    conv710 = load_conv("conv_fix_f0710_full", 0.710)

    fig, axes = plt.subplots(2, 2, figsize=(12, 9))
    plot_metric(axes[0, 0], "disp_mm", "Desplazamiento maximo [mm]", conv700, conv710)
    plot_metric(axes[0, 1], "max_velocity_ms", "Velocidad maxima [m/s]", conv700, conv710)
    plot_metric(axes[1, 0], "max_sph_force_N", "Fuerza SPH maxima [N]", conv700, conv710)
    plot_metric(axes[1, 1], "max_rotation_deg", "Rotacion acumulada [deg]", conv700, conv710)

    fig.suptitle(
        "Convergencias corregidas en los dos casos marginales",
        fontsize=14,
        fontweight="bold",
    )

    out = OUTDIR / "03_corrected_convergence_metrics_clean.png"
    fig.savefig(out, dpi=180, bbox_inches="tight")
    plt.close(fig)
    print(out)


if __name__ == "__main__":
    main()
