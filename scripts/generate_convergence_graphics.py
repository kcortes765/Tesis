"""
Generate publication-style convergence/frontier graphics from local results.

Inputs are intentionally restricted to lightweight local artifacts:
- data/results/conv_edge_*.csv
- data/results/conv_reassure_*.csv
- data/results/conv_repeat_*.csv
- data/results/conv_probe_*.csv
- data/results/conv_edge_*_gci.json
- data/results.sqlite

No simulations are run and no heavy DualSPHysics outputs are read.
"""

from __future__ import annotations

import json
import math
import re
import sqlite3
from dataclasses import dataclass
from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


PROJECT = Path(__file__).resolve().parent.parent
RESULTS_DIR = PROJECT / "data" / "results"
SQLITE_PATH = PROJECT / "data" / "results.sqlite"
OUTDIR = PROJECT / "data" / "figures" / "derived_convergence_graphics"

D_EQ_M = 0.100421
DISP_THRESHOLD_PCT = 5.0
DISP_THRESHOLD_MM = D_EQ_M * 1000.0 * DISP_THRESHOLD_PCT / 100.0
ROT_THRESHOLD_DEG = 5.0

DP_COLORS = {
    0.002: "#0072B2",
    0.003: "#D55E00",
    0.004: "#009E73",
    0.005: "#CC79A7",
}
CLASS_COLORS = {"ESTABLE": "#2E7D32", "FALLO": "#C62828"}
ROLE_MARKERS = {
    "edge_grid": "o",
    "frontier_refinement": "D",
    "repeatability_check": "X",
    "fine_probe": "^",
}

plt.rcParams.update(
    {
        "figure.dpi": 140,
        "savefig.dpi": 220,
        "font.size": 10,
        "axes.titlesize": 12,
        "axes.labelsize": 10,
        "legend.fontsize": 8,
        "xtick.labelsize": 9,
        "ytick.labelsize": 9,
        "axes.grid": True,
        "grid.alpha": 0.25,
        "axes.spines.top": False,
        "axes.spines.right": False,
        "figure.facecolor": "white",
        "axes.facecolor": "white",
    }
)


@dataclass
class FigureRecord:
    name: str
    png: str
    svg: str
    priority: str
    shows: str
    why: str
    caution: str = ""


def classify_family(prefix: str) -> tuple[str, str]:
    if prefix.startswith("conv_edge_"):
        return "conv_edge", "edge_grid"
    if prefix.startswith("conv_reassure_"):
        return "conv_reassure", "frontier_refinement"
    if prefix.startswith("conv_repeat_"):
        return "conv_repeat", "repeatability_check"
    if prefix.startswith("conv_probe_"):
        return "conv_probe", "fine_probe"
    return "other", "exploratory"


def parse_mu_from_prefix(prefix: str) -> float:
    match = re.search(r"_f(\d+)", prefix)
    if not match:
        return float("nan")
    digits = match.group(1).lstrip("0")
    if not digits:
        return float("nan")
    return int(digits) / (10 ** len(digits))


def sqlite_lookup() -> dict[str, dict]:
    lookup: dict[str, dict] = {}
    if not SQLITE_PATH.exists():
        return lookup

    conn = sqlite3.connect(SQLITE_PATH)
    cur = conn.cursor()
    tables = [
        row[0]
        for row in cur.execute(
            "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name"
        ).fetchall()
    ]
    for table in tables:
        if not (
            table.startswith("convergence_conv_edge_")
            or table.startswith("convergence_conv_reassure_")
            or table.startswith("convergence_conv_repeat_")
            or table.startswith("convergence_conv_probe_")
        ):
            continue
        cols = [row[1] for row in cur.execute(f"PRAGMA table_info({table})").fetchall()]
        rows = cur.execute(f"SELECT * FROM {table}").fetchall()
        for values in rows:
            record = dict(zip(cols, values))
            lookup[str(record["case_name"])] = record
    conn.close()
    return lookup


def load_master() -> pd.DataFrame:
    lookup = sqlite_lookup()
    files = sorted(
        list(RESULTS_DIR.glob("conv_edge_*.csv"))
        + list(RESULTS_DIR.glob("conv_reassure_*.csv"))
        + list(RESULTS_DIR.glob("conv_repeat_*.csv"))
        + list(RESULTS_DIR.glob("conv_probe_*.csv"))
    )
    frames: list[pd.DataFrame] = []
    for path in files:
        df = pd.read_csv(path, sep=";")
        if df.empty:
            continue
        prefix = path.stem
        family, role = classify_family(prefix)
        df["family"] = family
        df["group"] = role
        df["prefix"] = prefix
        df["source_csv"] = path.name
        df["mu"] = np.nan
        df["disp_pct_deq"] = np.nan
        df["failed"] = np.nan
        for idx, row in df.iterrows():
            rec = lookup.get(str(row["case_name"]), {})
            mu = rec.get("friction_coefficient", parse_mu_from_prefix(prefix))
            rel = rec.get(
                "max_displacement_rel",
                float(row["max_displacement_m"]) / D_EQ_M * 100.0,
            )
            failed = rec.get("failed", 1 if row["criterion_class"] == "FALLO" else 0)
            df.loc[idx, "mu"] = float(mu)
            df.loc[idx, "disp_pct_deq"] = float(rel)
            df.loc[idx, "failed"] = int(failed)
        frames.append(df)

    if not frames:
        raise RuntimeError("No convergence CSVs found.")

    out = pd.concat(frames, ignore_index=True)
    out["dp"] = out["dp"].astype(float)
    out["disp_mm"] = out["max_displacement_m"].astype(float) * 1000.0
    out["disp_margin_mm"] = out["disp_mm"] - DISP_THRESHOLD_MM
    out["criterion_class"] = out["criterion_class"].astype(str)
    out["criterion_mode"] = out["criterion_mode"].astype(str)
    out["moved"] = out["moved"].map(lambda x: str(x).lower() == "true")
    out["rotated"] = out["rotated"].map(lambda x: str(x).lower() == "true")
    scope_by_family = {
        "conv_edge": "principal_frontier",
        "conv_reassure": "frontier_refinement",
        "conv_repeat": "repeatability_check",
        "conv_probe": "supplemental_fine_probe",
    }
    out["evidence_scope"] = out["family"].map(scope_by_family).fillna("exploratory")
    out = out.sort_values(["family", "mu", "dp", "source_csv"]).reset_index(drop=True)
    return out


def load_gci_summary() -> pd.DataFrame:
    rows = []
    for path in sorted(RESULTS_DIR.glob("conv_edge_*_gci.json")):
        prefix = path.stem.replace("_gci", "")
        mu = parse_mu_from_prefix(prefix)
        with open(path, "r", encoding="utf-8") as handle:
            data = json.load(handle)
        for metric, rec in data.items():
            rows.append(
                {
                    "prefix": prefix,
                    "mu": mu,
                    "metric": metric,
                    "column": rec.get("col", ""),
                    "conv_type": rec.get("conv_type", ""),
                    "in_asymptotic": str(rec.get("in_asymptotic", "")),
                    "GCI_fine": rec.get("GCI_fine", np.nan),
                    "GCI_med": rec.get("GCI_med", np.nan),
                    "AR": rec.get("AR", np.nan),
                    "is_primary": bool(rec.get("is_primary", False)),
                }
            )
    return pd.DataFrame(rows)


def save_fig(fig: plt.Figure, name: str, records: list[FigureRecord],
             priority: str, shows: str, why: str, caution: str = "") -> None:
    png = OUTDIR / f"{name}.png"
    svg = OUTDIR / f"{name}.svg"
    fig.savefig(png, bbox_inches="tight")
    fig.savefig(svg, bbox_inches="tight")
    plt.close(fig)
    records.append(
        FigureRecord(
            name=name,
            png=str(png.relative_to(PROJECT)),
            svg=str(svg.relative_to(PROJECT)),
            priority=priority,
            shows=shows,
            why=why,
            caution=caution,
        )
    )


def style_axis(ax: plt.Axes, xlabel: str, ylabel: str, title: str) -> None:
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    ax.set_title(title, fontweight="bold")
    ax.grid(True, alpha=0.25)


def add_threshold_pct(ax: plt.Axes) -> None:
    ax.axhline(
        DISP_THRESHOLD_PCT,
        color="black",
        linestyle="--",
        linewidth=1.1,
        label="umbral 5% d_eq",
    )


def add_threshold_mm(ax: plt.Axes) -> None:
    ax.axhline(
        DISP_THRESHOLD_MM,
        color="black",
        linestyle="--",
        linewidth=1.1,
        label=f"umbral {DISP_THRESHOLD_MM:.2f} mm",
    )


def scatter_by_dp(ax: plt.Axes, df: pd.DataFrame, y: str, ylabel: str,
                  title: str, threshold: str | None = None,
                  data: pd.DataFrame | None = None) -> None:
    plot_df = df if data is None else data
    for dp, sub in plot_df.groupby("dp"):
        color = DP_COLORS.get(round(float(dp), 3), "#666666")
        for role, role_df in sub.groupby("group"):
            marker = ROLE_MARKERS.get(role, "o")
            ax.scatter(
                role_df["mu"],
                role_df[y],
                s=62,
                color=color,
                marker=marker,
                edgecolor="white",
                linewidth=0.7,
                alpha=0.92,
                label=f"dp={dp:.3f}, {role}",
            )
    if threshold == "pct":
        add_threshold_pct(ax)
    if threshold == "mm":
        add_threshold_mm(ax)
    style_axis(ax, "mu [-]", ylabel, title)
    ax.legend(ncol=2, fontsize=7, frameon=True)


def plot_frontier_mu_disp_pct(df: pd.DataFrame, records: list[FigureRecord]) -> None:
    fig, ax = plt.subplots(figsize=(8.5, 5.2))
    scatter_by_dp(
        ax,
        df,
        "disp_pct_deq",
        "Desplazamiento maximo [% d_eq]",
        "Frontera practica por desplazamiento",
        threshold="pct",
    )
    save_fig(
        fig,
        "01_mu_vs_disp_pct_by_dp",
        records,
        "essential",
        "mu versus desplazamiento relativo, con umbral 5% d_eq",
        "Es la figura base para ubicar FALLO/ESTABLE bajo displacement_only.",
    )


def plot_frontier_mu_disp_mm(df: pd.DataFrame, records: list[FigureRecord]) -> None:
    fig, ax = plt.subplots(figsize=(8.5, 5.2))
    scatter_by_dp(
        ax,
        df,
        "disp_mm",
        "Desplazamiento maximo [mm]",
        "Desplazamiento absoluto cerca de la frontera",
        threshold="mm",
    )
    save_fig(
        fig,
        "02_mu_vs_disp_mm_by_dp",
        records,
        "essential",
        "mu versus desplazamiento en mm, con umbral fisico",
        "Traduce el criterio porcentual a una magnitud medible.",
    )


def plot_class_by_mu_dp(df: pd.DataFrame, records: list[FigureRecord]) -> None:
    fig, ax = plt.subplots(figsize=(8.5, 4.8))
    class_y = {"ESTABLE": 0, "FALLO": 1}
    for dp, sub in df.groupby("dp"):
        x_jitter = (float(dp) - 0.0035) * 0.07
        ax.scatter(
            sub["mu"] + x_jitter,
            sub["criterion_class"].map(class_y),
            s=70,
            color=DP_COLORS.get(round(float(dp), 3), "#666"),
            edgecolor="white",
            label=f"dp={dp:.3f}",
            alpha=0.9,
        )
    ax.set_yticks([0, 1])
    ax.set_yticklabels(["ESTABLE", "FALLO"])
    style_axis(ax, "mu [-]", "Clase", "Clase por friccion y resolucion")
    ax.legend(ncol=4, frameon=True)
    save_fig(
        fig,
        "03_class_by_mu_dp",
        records,
        "essential",
        "Clase ESTABLE/FALLO para cada mu y dp",
        "Muestra directamente la frontera practica sin convertirla en curva suave.",
    )


def plot_class_heatmap(df: pd.DataFrame, records: list[FigureRecord]) -> None:
    grouped = (
        df.groupby(["mu", "dp"])["failed"]
        .agg(lambda x: 1 if all(v == 1 for v in x) else 0 if all(v == 0 for v in x) else 0.5)
        .reset_index()
    )
    mus = sorted(grouped["mu"].unique())
    dps = sorted(grouped["dp"].unique(), reverse=True)
    grid = np.full((len(dps), len(mus)), np.nan)
    for _, row in grouped.iterrows():
        i = dps.index(row["dp"])
        j = mus.index(row["mu"])
        grid[i, j] = row["failed"]
    fig, ax = plt.subplots(figsize=(9.5, 4.8))
    cmap = matplotlib.colors.ListedColormap(["#2E7D32", "#FFC107", "#C62828"])
    cmap.set_bad("#F1F1F1")
    bounds = [-0.1, 0.25, 0.75, 1.1]
    norm = matplotlib.colors.BoundaryNorm(bounds, cmap.N)
    masked = np.ma.masked_invalid(grid)
    im = ax.imshow(masked, aspect="auto", cmap=cmap, norm=norm)
    ax.set_xticks(np.arange(len(mus)))
    ax.set_xticklabels([f"{m:.5f}".rstrip("0").rstrip(".") for m in mus], rotation=45, ha="right")
    ax.set_yticks(np.arange(len(dps)))
    ax.set_yticklabels([f"{d:.3f}" for d in dps])
    for i, dp in enumerate(dps):
        for j, mu in enumerate(mus):
            val = grid[i, j]
            if np.isnan(val):
                txt = "-"
                color = "#777777"
            elif val == 1:
                txt = "F"
                color = "white"
            elif val == 0:
                txt = "E"
                color = "white"
            else:
                txt = "M"
                color = "black"
            ax.text(j, i, txt, ha="center", va="center", fontsize=9, color=color, fontweight="bold")
    style_axis(ax, "mu [-]", "dp [m]", "Mapa de clase en el plano mu-dp")
    cbar = fig.colorbar(im, ax=ax, ticks=[0, 0.5, 1])
    cbar.ax.set_yticklabels(["ESTABLE", "mixto", "FALLO"])
    ax.text(
        0.01,
        -0.22,
        "E=ESTABLE, F=FALLO, -=sin corrida en esa combinacion",
        transform=ax.transAxes,
        fontsize=8,
        color="#555555",
    )
    save_fig(
        fig,
        "04_heatmap_class_mu_dp",
        records,
        "essential",
        "Heatmap mu x dp con clase displacement_only",
        "Condensa la frontera y evidencia la sensibilidad por resolucion.",
    )


def plot_margin_mu_by_dp(df: pd.DataFrame, records: list[FigureRecord]) -> None:
    fig, ax = plt.subplots(figsize=(8.5, 5.0))
    scatter_by_dp(
        ax,
        df,
        "disp_margin_mm",
        "Margen vs umbral [mm]",
        "Margen de desplazamiento respecto al umbral",
        threshold=None,
    )
    ax.axhline(0, color="black", linestyle="--", linewidth=1.1, label="umbral")
    ax.legend(ncol=2, fontsize=7, frameon=True)
    save_fig(
        fig,
        "05_displacement_margin_mu_by_dp",
        records,
        "support",
        "Margen positivo/negativo respecto del umbral de desplazamiento",
        "Hace visible cuan marginales son los casos cerca del 5% d_eq.",
    )


def plot_zoom_fine(df: pd.DataFrame, records: list[FigureRecord]) -> None:
    sub = df[df["dp"].isin([0.002, 0.003])].copy()
    fig, ax = plt.subplots(figsize=(8.0, 5.0))
    scatter_by_dp(
        ax,
        df,
        "disp_pct_deq",
        "Desplazamiento maximo [% d_eq]",
        "Zoom fino: dp=0.003 y dp=0.002",
        threshold="pct",
        data=sub,
    )
    ax.set_xlim(0.674, 0.6865)
    save_fig(
        fig,
        "06_zoom_fine_dp003_dp002",
        records,
        "essential",
        "Solo mallas finas en el rango de frontera",
        "Muestra que dp=0.002 reduce desplazamiento y cambia la transicion aparente.",
    )


def plot_bracket_dp003(df: pd.DataFrame, records: list[FigureRecord]) -> None:
    sub = df[(df["dp"].round(3) == 0.003) & (df["mu"].between(0.6795, 0.6815))].copy()
    fig, ax = plt.subplots(figsize=(8.0, 4.8))
    for role, role_df in sub.groupby("group"):
        ax.scatter(
            role_df["mu"],
            role_df["disp_pct_deq"],
            s=90,
            marker=ROLE_MARKERS.get(role, "o"),
            color=[CLASS_COLORS[c] for c in role_df["criterion_class"]],
            edgecolor="white",
            linewidth=0.8,
            label=role,
        )
        for _, r in role_df.iterrows():
            ax.text(r["mu"], r["disp_pct_deq"] + 0.12, r["criterion_class"], ha="center", fontsize=8)
    add_threshold_pct(ax)
    ax.axvspan(0.68050, 0.68075, color="#777777", alpha=0.12, label="bracket principal")
    style_axis(ax, "mu [-]", "Desplazamiento maximo [% d_eq]", "Bracket fino en dp=0.003")
    ax.legend(frameon=True, fontsize=8)
    save_fig(
        fig,
        "07_bracket_dp003_fine",
        records,
        "essential",
        "Bracket 0.68050-0.68075 para dp=0.003",
        "Figura directa para defender la frontera practica en la malla dp=0.003.",
    )


def plot_resolution_metric(df: pd.DataFrame, records: list[FigureRecord],
                           y: str, ylabel: str, name: str, title: str,
                           threshold: str | None = None) -> None:
    sub = df[df["family"] == "conv_edge"].copy()
    fig, ax = plt.subplots(figsize=(8.4, 5.0))
    for mu, g in sub.groupby("mu"):
        g = g.sort_values("dp", ascending=False)
        ax.plot(g["dp"], g[y], marker="o", linewidth=1.8, label=f"mu={mu:.3f}")
    ax.invert_xaxis()
    if threshold == "pct":
        add_threshold_pct(ax)
    elif threshold == "mm":
        add_threshold_mm(ax)
    elif threshold == "rot":
        ax.axhline(ROT_THRESHOLD_DEG, color="black", linestyle="--", linewidth=1.1, label="umbral rot")
    style_axis(ax, "dp [m] (mas fino hacia la derecha)", ylabel, title)
    ax.legend(ncol=2, frameon=True)
    save_fig(
        fig,
        name,
        records,
        "support",
        f"Resolucion versus {ylabel}",
        "Usa solo conv_edge para no mezclar corridas de una sola malla.",
        "No interpretar como convergencia asintotica si la tendencia es oscilatoria.",
    )


def relative_change_df(df: pd.DataFrame, metric: str) -> pd.DataFrame:
    rows = []
    sub = df[df["family"] == "conv_edge"].copy()
    for mu, g in sub.groupby("mu"):
        g = g.sort_values("dp", ascending=False).reset_index(drop=True)
        for i in range(len(g) - 1):
            coarse = g.iloc[i]
            fine = g.iloc[i + 1]
            denom = abs(float(coarse[metric]))
            if denom == 0:
                pct = np.nan
            else:
                pct = (float(fine[metric]) - float(coarse[metric])) / denom * 100.0
            rows.append(
                {
                    "mu": mu,
                    "pair": f"{coarse['dp']:.3f}->{fine['dp']:.3f}",
                    "change_pct": pct,
                }
            )
    return pd.DataFrame(rows)


def plot_relative_change(df: pd.DataFrame, records: list[FigureRecord],
                         metric: str, name: str, title: str) -> None:
    r = relative_change_df(df, metric)
    fig, ax = plt.subplots(figsize=(8.8, 4.8))
    pairs = list(r["pair"].drop_duplicates())
    x = np.arange(len(pairs))
    width = 0.18
    for k, (mu, g) in enumerate(r.groupby("mu")):
        vals = [g[g["pair"] == p]["change_pct"].iloc[0] if p in set(g["pair"]) else np.nan for p in pairs]
        ax.bar(x + (k - 1.5) * width, vals, width=width, label=f"mu={mu:.3f}")
    ax.axhline(0, color="black", linewidth=1.0)
    ax.set_xticks(x)
    ax.set_xticklabels(pairs)
    style_axis(ax, "par de refinamiento", "Cambio relativo [%]", title)
    ax.legend(ncol=2, frameon=True)
    save_fig(
        fig,
        name,
        records,
        "supplementary",
        f"Cambio relativo de {metric} entre dp consecutivos",
        "Sirve como diagnostico de sensibilidad, no como prueba formal de convergencia.",
        "Comportamiento oscilatorio en algunos casos.",
    )


def plot_edge_vs_repeat(df: pd.DataFrame, records: list[FigureRecord]) -> None:
    cases = [
        (0.680, 0.003, "0.680 @ 0.003"),
        (0.681, 0.003, "0.681 @ 0.003"),
        (0.680, 0.002, "0.680 @ 0.002"),
    ]
    rows = []
    for mu, dp, label in cases:
        sub = df[(np.isclose(df["mu"], mu)) & (np.isclose(df["dp"], dp))]
        for _, r in sub.iterrows():
            rows.append(
                {
                    "label": label,
                    "group": r["group"],
                    "disp_pct_deq": r["disp_pct_deq"],
                    "criterion_class": r["criterion_class"],
                }
            )
    comp = pd.DataFrame(rows)
    fig, ax = plt.subplots(figsize=(8.0, 4.8))
    labels = [c[2] for c in cases]
    x = np.arange(len(labels))
    width = 0.32
    for offset, group in [(-width / 2, "edge_grid"), (width / 2, "repeatability_check")]:
        vals = []
        colors = []
        for label in labels:
            s = comp[(comp["label"] == label) & (comp["group"] == group)]
            vals.append(float(s["disp_pct_deq"].iloc[0]) if not s.empty else np.nan)
            colors.append(CLASS_COLORS.get(str(s["criterion_class"].iloc[0]), "#999") if not s.empty else "#ddd")
        ax.bar(x + offset, vals, width=width, label=group, color=colors, alpha=0.9)
    add_threshold_pct(ax)
    ax.set_xticks(x)
    ax.set_xticklabels(labels)
    style_axis(ax, "caso repetido", "Desplazamiento maximo [% d_eq]", "Repeticiones marginales")
    ax.legend(frameon=True)
    save_fig(
        fig,
        "17_edge_vs_repeat_side_by_side",
        records,
        "essential",
        "Comparacion lado a lado entre corrida edge y repeticion",
        "Verifica consistencia operativa de los casos marginales repetidos.",
    )


def plot_marginal_repeats(df: pd.DataFrame, records: list[FigureRecord]) -> None:
    sub = df[
        ((np.isclose(df["mu"], 0.680)) & (df["dp"].isin([0.002, 0.003])))
        | ((np.isclose(df["mu"], 0.681)) & (np.isclose(df["dp"], 0.003)))
    ].copy()
    sub["case_label"] = sub.apply(lambda r: f"mu={r['mu']:.3f}, dp={r['dp']:.3f}", axis=1)
    fig, ax = plt.subplots(figsize=(8.4, 4.8))
    for role, g in sub.groupby("group"):
        ax.scatter(
            g["case_label"],
            g["disp_pct_deq"],
            marker=ROLE_MARKERS.get(role, "o"),
            s=90,
            label=role,
            color=[CLASS_COLORS[c] for c in g["criterion_class"]],
            edgecolor="white",
        )
    add_threshold_pct(ax)
    style_axis(ax, "caso", "Desplazamiento maximo [% d_eq]", "Patron de repeticiones marginales")
    ax.tick_params(axis="x", rotation=20)
    ax.legend(frameon=True)
    save_fig(
        fig,
        "18_marginal_repeats_highlight",
        records,
        "support",
        "Puntos repetidos marginales con su clase",
        "Resalta que las repeticiones conservan el patron de clase.",
    )


def plot_repeat_dumbbell(df: pd.DataFrame, records: list[FigureRecord]) -> None:
    pairs = [
        (0.680, 0.003, "mu=0.680, dp=0.003"),
        (0.681, 0.003, "mu=0.681, dp=0.003"),
        (0.680, 0.002, "mu=0.680, dp=0.002"),
    ]
    fig, ax = plt.subplots(figsize=(8.0, 4.8))
    y_positions = np.arange(len(pairs))
    for y, (mu, dp, label) in zip(y_positions, pairs):
        sub = df[(np.isclose(df["mu"], mu)) & (np.isclose(df["dp"], dp))]
        vals = []
        for role in ["edge_grid", "repeatability_check"]:
            s = sub[sub["group"] == role]
            if not s.empty:
                vals.append(float(s["disp_pct_deq"].iloc[0]))
        if len(vals) == 2:
            ax.plot(vals, [y, y], color="#777", linewidth=1.5)
        for role, s in sub.groupby("group"):
            ax.scatter(
                s["disp_pct_deq"],
                [y] * len(s),
                s=95,
                marker=ROLE_MARKERS.get(role, "o"),
                color=[CLASS_COLORS[c] for c in s["criterion_class"]],
                edgecolor="white",
                label=role if y == 0 else None,
            )
    ax.axvline(DISP_THRESHOLD_PCT, color="black", linestyle="--", linewidth=1.1)
    ax.set_yticks(y_positions)
    ax.set_yticklabels([p[2] for p in pairs])
    style_axis(ax, "Desplazamiento maximo [% d_eq]", "caso", "Dumbbell de repetibilidad")
    ax.legend(frameon=True)
    save_fig(
        fig,
        "19_repeat_dumbbell",
        records,
        "support",
        "Distancia entre corrida original y repeticion en casos marginales",
        "Hace visible la reproducibilidad numerica reportada.",
    )


def plot_cost_metric(df: pd.DataFrame, records: list[FigureRecord],
                     y: str, ylabel: str, name: str, title: str) -> None:
    fig, ax = plt.subplots(figsize=(8.0, 4.8))
    for role, g in df.groupby("group"):
        ax.scatter(
            g["dp"],
            g[y],
            s=58,
            marker=ROLE_MARKERS.get(role, "o"),
            alpha=0.85,
            label=role,
            edgecolor="white",
        )
    means = df.groupby("dp")[y].mean().sort_index(ascending=False)
    ax.plot(means.index, means.values, color="black", linewidth=1.8, label="media por dp")
    ax.invert_xaxis()
    style_axis(ax, "dp [m] (mas fino hacia la derecha)", ylabel, title)
    ax.legend(frameon=True)
    save_fig(
        fig,
        name,
        records,
        "support",
        f"Costo computacional: {ylabel}",
        "Cuantifica el precio de refinar la malla.",
    )


def plot_cost_precision_panel(df: pd.DataFrame, records: list[FigureRecord]) -> None:
    fig, axes = plt.subplots(1, 2, figsize=(11.0, 4.8))
    ax = axes[0]
    for dp, g in df.groupby("dp"):
        ax.scatter(
            g["tiempo_min"],
            g["disp_pct_deq"],
            color=DP_COLORS.get(round(float(dp), 3), "#666"),
            s=70,
            edgecolor="white",
            label=f"dp={dp:.3f}",
        )
    add_threshold_pct(ax)
    style_axis(ax, "Tiempo [min]", "Desplazamiento [% d_eq]", "Costo vs criterio")

    ax = axes[1]
    for dp, g in df.groupby("dp"):
        ax.scatter(
            g["tiempo_min"],
            g["disp_margin_mm"].abs(),
            color=DP_COLORS.get(round(float(dp), 3), "#666"),
            s=70,
            edgecolor="white",
            label=f"dp={dp:.3f}",
        )
    style_axis(ax, "Tiempo [min]", "|margen al umbral| [mm]", "Costo vs cercania al umbral")
    axes[0].legend(frameon=True, ncol=2)
    save_fig(
        fig,
        "23_cost_vs_practical_precision_panel",
        records,
        "essential",
        "Panel costo frente a desplazamiento y margen al umbral",
        "Conecta el argumento metodologico con el costo computacional.",
        "El margen pequeno no implica mayor precision si la respuesta es oscilatoria.",
    )


def plot_margin_vs_cost(df: pd.DataFrame, records: list[FigureRecord]) -> None:
    fig, ax = plt.subplots(figsize=(8.0, 4.8))
    for cls, g in df.groupby("criterion_class"):
        ax.scatter(
            g["tiempo_min"],
            g["disp_margin_mm"],
            color=CLASS_COLORS.get(cls, "#777"),
            s=70,
            edgecolor="white",
            label=cls,
            alpha=0.9,
        )
    ax.axhline(0, color="black", linestyle="--", linewidth=1.1)
    style_axis(ax, "Tiempo [min]", "Margen vs umbral [mm]", "Margen de desplazamiento versus costo")
    ax.legend(frameon=True)
    save_fig(
        fig,
        "24_displacement_margin_vs_cost",
        records,
        "support",
        "Margen al umbral frente al tiempo de corrida",
        "Ayuda a discutir si el costo adicional cambia la decision practica.",
    )


def plot_summary_frontier(df: pd.DataFrame, records: list[FigureRecord]) -> None:
    fig, axes = plt.subplots(1, 2, figsize=(12.0, 4.8), gridspec_kw={"width_ratios": [1.2, 1]})
    ax = axes[0]
    sub = df[(df["dp"].isin([0.002, 0.003])) & (df["mu"].between(0.6795, 0.6815))]
    for dp, g in sub.groupby("dp"):
        g = g.sort_values(["mu", "group"])
        ax.scatter(
            g["mu"],
            g["disp_pct_deq"],
            marker="o",
            s=70,
            color=DP_COLORS.get(round(float(dp), 3), "#666"),
            edgecolor="white",
            label=f"dp={dp:.3f}",
        )
    add_threshold_pct(ax)
    ax.axvspan(0.68050, 0.68075, color="#777", alpha=0.12, label="bracket dp=0.003")
    style_axis(ax, "mu [-]", "Desplazamiento [% d_eq]", "Frontera practica")
    ax.legend(frameon=True)

    ax = axes[1]
    stable_rot = df[(df["criterion_class"] == "ESTABLE") & (df["rotated"])]
    ax.scatter(
        df["max_rotation_deg"],
        df["disp_pct_deq"],
        color=[CLASS_COLORS[c] for c in df["criterion_class"]],
        s=62,
        edgecolor="white",
        alpha=0.9,
    )
    ax.scatter(
        stable_rot["max_rotation_deg"],
        stable_rot["disp_pct_deq"],
        facecolors="none",
        edgecolors="black",
        s=110,
        linewidth=1.2,
        label="rotated=True, clase ESTABLE",
    )
    ax.axhline(DISP_THRESHOLD_PCT, color="black", linestyle="--", linewidth=1.0)
    ax.axvline(ROT_THRESHOLD_DEG, color="#666", linestyle=":", linewidth=1.0)
    style_axis(ax, "Rotacion acumulada [deg]", "Desplazamiento [% d_eq]", "Rotacion diagnostica")
    ax.legend(frameon=True)
    save_fig(
        fig,
        "25_summary_practical_frontier",
        records,
        "essential",
        "Resumen principal de frontera y rotacion diagnostica",
        "Es la figura integradora mas defendible para tesis/presentacion.",
    )


def plot_summary_resolution(df: pd.DataFrame, records: list[FigureRecord]) -> None:
    fig, axes = plt.subplots(2, 2, figsize=(11.5, 8.0))
    metrics = [
        ("disp_pct_deq", "Desplazamiento [% d_eq]", "Desplazamiento"),
        ("max_rotation_deg", "Rotacion [deg]", "Rotacion diagnostica"),
        ("max_velocity_ms", "Velocidad [m/s]", "Velocidad del bloque"),
        ("max_sph_force_N", "Fuerza SPH [N]", "Fuerza SPH"),
    ]
    edge = df[df["family"] == "conv_edge"]
    for ax, (col, ylabel, title) in zip(axes.ravel(), metrics):
        for mu, g in edge.groupby("mu"):
            g = g.sort_values("dp", ascending=False)
            ax.plot(g["dp"], g[col], marker="o", linewidth=1.5, label=f"mu={mu:.3f}")
        ax.invert_xaxis()
        if col == "disp_pct_deq":
            add_threshold_pct(ax)
        if col == "max_rotation_deg":
            ax.axhline(ROT_THRESHOLD_DEG, color="black", linestyle="--", linewidth=1.0)
        style_axis(ax, "dp [m]", ylabel, title)
    axes[0, 0].legend(ncol=2, frameon=True)
    save_fig(
        fig,
        "26_summary_resolution_sensitivity",
        records,
        "essential",
        "Panel de sensibilidad por resolucion en metricas principales",
        "Muestra honestamente la no monotonia y el cambio al refinar.",
        "No debe presentarse como prueba de convergencia asintotica.",
    )


def plot_summary_cost(df: pd.DataFrame, records: list[FigureRecord]) -> None:
    fig, axes = plt.subplots(1, 3, figsize=(13.0, 4.5))
    for ax, col, ylabel in [
        (axes[0], "tiempo_min", "Tiempo [min]"),
        (axes[1], "n_particles", "Numero de particulas"),
        (axes[2], "mem_gpu_mb", "Memoria GPU [MB]"),
    ]:
        means = df.groupby("dp")[col].mean().sort_index(ascending=False)
        ax.plot(means.index, means.values, marker="o", color="#222", linewidth=2)
        ax.invert_xaxis()
        style_axis(ax, "dp [m]", ylabel, ylabel)
    save_fig(
        fig,
        "27_summary_refinement_cost",
        records,
        "essential",
        "Costo de refinamiento de malla",
        "Cuantifica la diferencia practica entre dp=0.003 y dp=0.002.",
    )


def plot_rotation_diagnostic(df: pd.DataFrame, records: list[FigureRecord]) -> None:
    fig, ax = plt.subplots(figsize=(8.0, 5.3))
    for cls, g in df.groupby("criterion_class"):
        ax.scatter(
            g["max_rotation_deg"],
            g["disp_pct_deq"],
            s=75,
            color=CLASS_COLORS.get(cls, "#777"),
            edgecolor="white",
            label=cls,
            alpha=0.9,
        )
    ax.axhline(DISP_THRESHOLD_PCT, color="black", linestyle="--", linewidth=1.1, label="umbral desplazamiento")
    ax.axvline(ROT_THRESHOLD_DEG, color="#666", linestyle=":", linewidth=1.1, label="umbral rot diagnostico")
    style_axis(ax, "Rotacion acumulada [deg]", "Desplazamiento [% d_eq]", "Rotacion diagnostica vs criterio primario")
    ax.legend(frameon=True)
    save_fig(
        fig,
        "28_rotation_diagnostic_vs_displacement_only",
        records,
        "essential",
        "Rotacion frente a desplazamiento y clase final",
        "Aclara que la rotacion no gobierna la clase en displacement_only.",
    )


def plot_dp002_probe_context(df: pd.DataFrame, records: list[FigureRecord]) -> None:
    sub = df[np.isclose(df["dp"], 0.002)].copy()
    if sub.empty or "conv_probe" not in set(sub["family"]):
        return
    fig, ax = plt.subplots(figsize=(8.5, 5.0))
    for scope, g in sub.groupby("evidence_scope"):
        ax.scatter(
            g["mu"],
            g["disp_pct_deq"],
            s=85 if scope == "supplemental_fine_probe" else 65,
            marker=ROLE_MARKERS.get(str(g["group"].iloc[0]), "o"),
            color=[CLASS_COLORS[c] for c in g["criterion_class"]],
            edgecolor="black" if scope == "supplemental_fine_probe" else "white",
            linewidth=1.1 if scope == "supplemental_fine_probe" else 0.7,
            alpha=0.93,
            label=scope,
        )
        for _, r in g[g["family"] == "conv_probe"].iterrows():
            ax.text(
                r["mu"],
                r["disp_pct_deq"] + 0.18,
                "probe fino",
                ha="center",
                fontsize=8,
                color="#333333",
            )
    add_threshold_pct(ax)
    style_axis(
        ax,
        "mu [-]",
        "Desplazamiento maximo [% d_eq]",
        "Probe fino dp=0.002 en contexto",
    )
    ax.legend(frameon=True, fontsize=8)
    save_fig(
        fig,
        "30_dp002_probe_context",
        records,
        "support",
        "Contexto del probe conv_probe_dp002_f06625 dentro de dp=0.002",
        "Documenta que el probe fino es evidencia suplementaria y no bracket principal.",
        "No usar este punto para redefinir la frontera principal dp=0.003.",
    )


def plot_gci_overview(gci: pd.DataFrame, records: list[FigureRecord]) -> None:
    if gci.empty:
        return
    fig, ax = plt.subplots(figsize=(9.5, 4.8))
    x_labels = []
    vals = []
    colors = []
    for _, r in gci.iterrows():
        x_labels.append(f"mu={r['mu']:.3f}\n{r['metric']}")
        vals.append(float(r["GCI_fine"]) if pd.notna(r["GCI_fine"]) else np.nan)
        colors.append("#0072B2" if str(r["conv_type"]) == "monotonic" else "#D55E00")
    ax.bar(np.arange(len(vals)), vals, color=colors, alpha=0.9)
    ax.set_xticks(np.arange(len(vals)))
    ax.set_xticklabels(x_labels, rotation=75, ha="right")
    style_axis(ax, "caso-metrica", "GCI fine [-]", "Resumen GCI disponible solo para conv_edge")
    save_fig(
        fig,
        "29_gci_available_edge_only",
        records,
        "supplementary",
        "GCI fine por caso y metrica donde existe JSON",
        "Documenta que el GCI no respalda una convergencia fuerte general.",
        "No hay GCI JSON para conv_reassure ni conv_repeat.",
    )


def write_index(records: list[FigureRecord], master: pd.DataFrame, gci: pd.DataFrame) -> None:
    lines = [
        "# Derived Convergence Graphics",
        "",
        "Fuente: archivos locales `data/results/conv_edge_*.csv`, `conv_reassure_*.csv`, `conv_repeat_*.csv`, `conv_probe_*.csv`, `data/results.sqlite` y `conv_edge_*_gci.json`.",
        "",
        "No se usaron binarios pesados ni se corrieron simulaciones nuevas.",
        "",
        "## Dataset",
        "",
        f"- Filas tabla maestra: {len(master)}",
        f"- Familias: {', '.join(sorted(master['family'].unique()))}",
        f"- Alcances de evidencia: {', '.join(sorted(master['evidence_scope'].unique()))}",
        f"- Modos de criterio: {', '.join(sorted(master['criterion_mode'].unique()))}",
        f"- GCI JSON disponibles: {0 if gci.empty else gci['prefix'].nunique()} prefixes conv_edge",
        f"- Umbral desplazamiento: {DISP_THRESHOLD_PCT:.1f}% d_eq = {DISP_THRESHOLD_MM:.3f} mm",
        "",
        "## Figuras esenciales",
        "",
    ]
    for r in records:
        if r.priority == "essential":
            lines.extend(
                [
                    f"### {r.name}",
                    f"- PNG: `{r.png}`",
                    f"- SVG: `{r.svg}`",
                    f"- Que muestra: {r.shows}",
                    f"- Por que importa: {r.why}",
                    f"- Advertencia: {r.caution or 'Ninguna especifica.'}",
                    "",
                ]
            )
    lines.extend(["## Figuras de apoyo y suplementarias", ""])
    for r in records:
        if r.priority != "essential":
            lines.extend(
                [
                    f"### {r.name} ({r.priority})",
                    f"- PNG: `{r.png}`",
                    f"- SVG: `{r.svg}`",
                    f"- Que muestra: {r.shows}",
                    f"- Por que importa: {r.why}",
                    f"- Advertencia: {r.caution or 'Ninguna especifica.'}",
                    "",
                ]
            )
    (OUTDIR / "FIGURE_INDEX.md").write_text("\n".join(lines), encoding="utf-8")

    fig_df = pd.DataFrame([r.__dict__ for r in records])
    fig_df.to_csv(OUTDIR / "figure_index.csv", index=False)


def main() -> None:
    OUTDIR.mkdir(parents=True, exist_ok=True)
    master = load_master()
    gci = load_gci_summary()

    master_path = OUTDIR / "master_convergence_frontier.csv"
    master.to_csv(master_path, index=False)
    if not gci.empty:
        gci.to_csv(OUTDIR / "gci_summary_edge.csv", index=False)

    records: list[FigureRecord] = []

    plot_frontier_mu_disp_pct(master, records)
    plot_frontier_mu_disp_mm(master, records)
    plot_class_by_mu_dp(master, records)
    plot_class_heatmap(master, records)
    plot_margin_mu_by_dp(master, records)
    plot_zoom_fine(master, records)
    plot_bracket_dp003(master, records)

    plot_resolution_metric(master, records, "disp_pct_deq", "Desplazamiento [% d_eq]", "08_dp_vs_disp_pct_by_mu", "Sensibilidad de desplazamiento por dp", threshold="pct")
    plot_resolution_metric(master, records, "max_displacement_m", "Desplazamiento [m]", "09_dp_vs_displacement_m_by_mu", "Desplazamiento absoluto por dp")
    plot_resolution_metric(master, records, "max_rotation_deg", "Rotacion [deg]", "10_dp_vs_rotation_by_mu", "Rotacion diagnostica por dp", threshold="rot")
    plot_resolution_metric(master, records, "max_velocity_ms", "Velocidad [m/s]", "11_dp_vs_velocity_by_mu", "Velocidad maxima por dp")
    plot_resolution_metric(master, records, "max_sph_force_N", "Fuerza SPH [N]", "12_dp_vs_sph_force_by_mu", "Fuerza SPH maxima por dp")

    plot_relative_change(master, records, "disp_pct_deq", "13_relative_change_displacement", "Cambio relativo de desplazamiento")
    plot_relative_change(master, records, "max_rotation_deg", "14_relative_change_rotation", "Cambio relativo de rotacion")
    plot_relative_change(master, records, "max_velocity_ms", "15_relative_change_velocity", "Cambio relativo de velocidad")
    plot_relative_change(master, records, "max_sph_force_N", "16_relative_change_sph_force", "Cambio relativo de fuerza SPH")

    plot_edge_vs_repeat(master, records)
    plot_marginal_repeats(master, records)
    plot_repeat_dumbbell(master, records)

    plot_cost_metric(master, records, "tiempo_min", "Tiempo [min]", "20_dp_vs_time_min", "Tiempo de corrida por dp")
    plot_cost_metric(master, records, "n_particles", "Numero de particulas", "21_dp_vs_n_particles", "Particulas por dp")
    plot_cost_metric(master, records, "mem_gpu_mb", "Memoria GPU [MB]", "22_dp_vs_mem_gpu", "Memoria GPU por dp")
    plot_cost_precision_panel(master, records)
    plot_margin_vs_cost(master, records)

    plot_summary_frontier(master, records)
    plot_summary_resolution(master, records)
    plot_summary_cost(master, records)
    plot_rotation_diagnostic(master, records)
    plot_dp002_probe_context(master, records)
    plot_gci_overview(gci, records)

    write_index(records, master, gci)
    print(f"OUTDIR={OUTDIR}")
    print(f"MASTER={master_path}")
    print(f"FIGURES={len(records)}")


if __name__ == "__main__":
    main()
