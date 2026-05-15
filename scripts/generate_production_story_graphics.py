"""
Generate publication-style figures for the production / active-learning stage.

Inputs are restricted to lightweight exported summaries:
- exports/pilot_productivo_20260501/pilot_summary.csv
- exports/batch2_productivo_20260505/batch2_summary.csv
- exports/batch3_productivo_20260509/batch3_summary.csv
- exports/batch4_mass_probe_20260513/batch4_summary.csv
- exports/al_batch1_hybrid_20260514/al_batch1_summary.csv

The script intentionally excludes live/running batches until they have an
official lightweight export. Heavy DualSPHysics outputs are not read.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.ticker import FuncFormatter, MaxNLocator
import numpy as np
import pandas as pd


PROJECT = Path(__file__).resolve().parent.parent
OUTDIR = PROJECT / "data" / "figures" / "production_story_graphics"

D_EQ_M = 0.100421
D_EQ_MM = D_EQ_M * 1000.0
DISP_THRESHOLD_PCT = 5.0
DISP_THRESHOLD_MM = D_EQ_MM * DISP_THRESHOLD_PCT / 100.0
MARGIN_YLIM = (-20.0, 7.0)
DISP_PCT_XLIM = (-0.5, 20.0)
DISP_PCT_YLIM = (-0.5, 20.0)

EXPORT_SPECS = [
    ("pilot", "Piloto", PROJECT / "exports" / "pilot_productivo_20260501" / "pilot_summary.csv"),
    ("batch2", "Batch2", PROJECT / "exports" / "batch2_productivo_20260505" / "batch2_summary.csv"),
    ("batch3", "Batch3", PROJECT / "exports" / "batch3_productivo_20260509" / "batch3_summary.csv"),
    ("batch4", "Batch4 masa", PROJECT / "exports" / "batch4_mass_probe_20260513" / "batch4_summary.csv"),
    ("al1", "AL1", PROJECT / "exports" / "al_batch1_hybrid_20260514" / "al_batch1_summary.csv"),
]

CLASS_COLORS = {
    "ESTABLE": "#2F7D4F",
    "FALLO": "#B73B3B",
    "PARCIAL": "#777777",
    "UNKNOWN": "#999999",
}
CLASS_MARKERS = {"ESTABLE": "o", "FALLO": "^", "PARCIAL": "s", "UNKNOWN": "x"}
FAMILY_COLORS = {
    "pilot": "#6A3D9A",
    "batch2": "#009E73",
    "batch3": "#E69F00",
    "batch4": "#56B4E9",
    "al1": "#D55E00",
}
MASS_COLORS = {
    0.85: "#8C5E3C",
    1.00: "#2B6F9F",
    1.15: "#B98524",
    1.25: "#6A4C93",
}


plt.rcParams.update(
    {
        "figure.dpi": 170,
        "savefig.dpi": 340,
        "font.size": 10.2,
        "axes.titlesize": 12.2,
        "axes.labelsize": 10.4,
        "legend.fontsize": 8.4,
        "xtick.labelsize": 9.2,
        "ytick.labelsize": 9.2,
        "axes.grid": True,
        "grid.alpha": 0.18,
        "grid.linewidth": 0.7,
        "axes.spines.top": False,
        "axes.spines.right": False,
        "figure.facecolor": "white",
        "axes.facecolor": "white",
        "axes.edgecolor": "#444444",
        "axes.labelcolor": "#222222",
        "xtick.color": "#333333",
        "ytick.color": "#333333",
        "legend.framealpha": 0.96,
        "legend.facecolor": "white",
        "legend.edgecolor": "#D5D5D5",
        "axes.titleweight": "bold",
        "figure.constrained_layout.use": True,
        "svg.fonttype": "none",
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


def pct_to_mm(pct: float | np.ndarray) -> float | np.ndarray:
    return np.asarray(pct) * D_EQ_MM / 100.0


def mm_to_pct(mm: float | np.ndarray) -> float | np.ndarray:
    return np.asarray(mm) * 100.0 / D_EQ_MM


def fmt_pct(x: float, _pos: object = None) -> str:
    return f"{x:.1f}%"


def fmt_mm(x: float, _pos: object = None) -> str:
    return f"{x:.1f}"


def coerce_bool(value: object) -> bool:
    if isinstance(value, bool):
        return value
    text = str(value).strip().lower()
    return text in {"true", "1", "yes", "si", "y"}


def normalize_class(value: object, status: object) -> str:
    text = str(value).strip().upper()
    if text in {"ESTABLE", "FALLO"}:
        return text
    if "PARTIAL" in str(status).upper() or "PARCIAL" in str(status).upper():
        return "PARCIAL"
    return "UNKNOWN"


def load_export_csv(family: str, label: str, path: Path) -> pd.DataFrame:
    if not path.exists():
        return pd.DataFrame()
    df = pd.read_csv(path)
    if df.empty:
        return pd.DataFrame()
    df["family"] = family
    df["family_label"] = label
    df["source_csv"] = str(path.relative_to(PROJECT))
    return df


def load_master() -> pd.DataFrame:
    frames = [load_export_csv(*spec) for spec in EXPORT_SPECS]
    frames = [df for df in frames if not df.empty]
    if not frames:
        return pd.DataFrame()
    master = pd.concat(frames, ignore_index=True, sort=False)

    if "max_displacement_pct_deq" in master.columns:
        master["disp_pct_deq"] = master["disp_pct_deq"].fillna(
            master["max_displacement_pct_deq"]
        )
    for col in [
        "dam_height",
        "boulder_mass",
        "boulder_rot_z",
        "friction_coefficient",
        "slope_inv",
        "dp",
        "reference_time_s",
        "max_displacement_m",
        "disp_pct_deq",
        "max_rotation_deg",
        "max_velocity_ms",
        "max_sph_force_N",
        "max_contact_force_N",
        "max_flow_velocity_ms",
        "max_water_height_m",
        "tiempo_min",
        "n_particles",
        "mem_gpu_mb",
    ]:
        if col in master.columns:
            master[col] = pd.to_numeric(master[col], errors="coerce")

    if "disp_pct_deq" not in master.columns:
        master["disp_pct_deq"] = np.nan
    if "max_displacement_m" not in master.columns:
        master["max_displacement_m"] = np.nan
    master["disp_mm"] = master["max_displacement_m"] * 1000.0
    missing_disp_mm = master["disp_mm"].isna() & master["disp_pct_deq"].notna()
    master.loc[missing_disp_mm, "disp_mm"] = pct_to_mm(
        master.loc[missing_disp_mm, "disp_pct_deq"]
    )
    missing_pct = master["disp_pct_deq"].isna() & master["disp_mm"].notna()
    master.loc[missing_pct, "disp_pct_deq"] = mm_to_pct(
        master.loc[missing_pct, "disp_mm"]
    )
    master["margin_pct"] = DISP_THRESHOLD_PCT - master["disp_pct_deq"]
    master["margin_mm"] = DISP_THRESHOLD_MM - master["disp_mm"]
    master["criterion_class"] = [
        normalize_class(cls, status)
        for cls, status in zip(
            master.get("criterion_class", pd.Series([""] * len(master))),
            master.get("status", pd.Series([""] * len(master))),
        )
    ]
    for col in ["moved", "rotated", "failed"]:
        if col in master.columns:
            master[col] = master[col].map(coerce_bool)
    master["is_official"] = master["status"].astype(str).str.upper().str.startswith("OK")
    master["is_partial"] = master["status"].astype(str).str.upper().str.contains(
        "PARTIAL|PARCIAL", regex=True
    )

    columns = [
        "family",
        "family_label",
        "source_csv",
        "case_id",
        "status",
        "is_official",
        "is_partial",
        "dam_height",
        "boulder_mass",
        "boulder_rot_z",
        "friction_coefficient",
        "slope_inv",
        "dp",
        "classification_mode",
        "reference_time_s",
        "criterion_class",
        "moved",
        "rotated",
        "failed",
        "max_displacement_m",
        "disp_mm",
        "disp_pct_deq",
        "margin_mm",
        "margin_pct",
        "max_rotation_deg",
        "max_velocity_ms",
        "max_sph_force_N",
        "max_contact_force_N",
        "max_flow_velocity_ms",
        "max_water_height_m",
        "sim_time_reached",
        "n_timesteps",
        "tiempo_min",
        "n_particles",
        "mem_gpu_mb",
        "quality_flags",
    ]
    for col in columns:
        if col not in master.columns:
            master[col] = np.nan
    return master[columns].sort_values(
        ["family", "dam_height", "boulder_mass", "friction_coefficient", "case_id"]
    )


def save_figure(fig: plt.Figure, name: str) -> tuple[str, str]:
    OUTDIR.mkdir(parents=True, exist_ok=True)
    png = OUTDIR / f"{name}.png"
    svg = OUTDIR / f"{name}.svg"
    fig.savefig(png, bbox_inches="tight")
    fig.savefig(svg, bbox_inches="tight")
    plt.close(fig)
    return png.name, svg.name


def add_disp_secondary_y(ax: plt.Axes) -> None:
    sec = ax.secondary_yaxis("right", functions=(pct_to_mm, mm_to_pct))
    sec.set_ylabel("desplazamiento absoluto (mm)")
    sec.yaxis.set_major_formatter(FuncFormatter(fmt_mm))


def add_disp_secondary_x(ax: plt.Axes) -> None:
    sec = ax.secondary_xaxis("top", functions=(pct_to_mm, mm_to_pct))
    sec.set_xlabel("desplazamiento absoluto (mm)")
    sec.xaxis.set_major_formatter(FuncFormatter(fmt_mm))


def add_margin_secondary_y(ax: plt.Axes) -> None:
    sec = ax.secondary_yaxis("right", functions=(pct_to_mm, mm_to_pct))
    sec.set_ylabel("margen absoluto a umbral (mm)")
    sec.yaxis.set_major_formatter(FuncFormatter(fmt_mm))


def point_size(disp_pct: pd.Series) -> np.ndarray:
    values = disp_pct.fillna(0).clip(lower=0, upper=40).to_numpy()
    return 45.0 + 4.2 * values


def clipped_margin(values: pd.Series) -> pd.Series:
    return values.clip(lower=MARGIN_YLIM[0] + 0.8, upper=MARGIN_YLIM[1] - 0.4)


def note_out_of_scale(ax: plt.Axes, count: int, where: str = "lower left") -> None:
    if count <= 0:
        return
    locs = {
        "lower left": (0.02, 0.05, "left", "bottom"),
        "upper right": (0.98, 0.96, "right", "top"),
        "upper left": (0.02, 0.96, "left", "top"),
    }
    x, y, ha, va = locs.get(where, locs["lower left"])
    ax.text(
        x,
        y,
        f"{count} caso(s) extremo(s)\nfuera de escala",
        transform=ax.transAxes,
        ha=ha,
        va=va,
        fontsize=8.3,
        color="#555555",
        bbox=dict(boxstyle="round,pad=0.25", fc="white", ec="#DDDDDD", lw=0.5),
    )


def class_legend() -> list[Line2D]:
    return [
        Line2D(
            [0],
            [0],
            marker=CLASS_MARKERS[key],
            color="none",
            markerfacecolor=color,
            markeredgecolor="#222222",
            markersize=8,
            label=key.capitalize(),
        )
        for key, color in CLASS_COLORS.items()
        if key != "UNKNOWN"
    ]


def family_legend() -> list[Line2D]:
    return [
        Line2D([0], [0], color=color, lw=3, label=label)
        for family, label, _path in EXPORT_SPECS
        for key, color in FAMILY_COLORS.items()
        if family == key
    ]


def plot_response_map(df: pd.DataFrame) -> FigureRecord:
    official = df[df["is_official"]].copy()
    masses = sorted(official["boulder_mass"].dropna().unique())
    n = max(1, len(masses))
    fig, axes = plt.subplots(1, n, figsize=(4.1 * n, 4.3), sharey=True)
    axes = np.atleast_1d(axes)

    for ax, mass in zip(axes, masses):
        sub = official[np.isclose(official["boulder_mass"], mass)]
        for cls, cls_df in sub.groupby("criterion_class"):
            ax.scatter(
                cls_df["friction_coefficient"],
                cls_df["dam_height"],
                s=point_size(cls_df["disp_pct_deq"]),
                marker=CLASS_MARKERS.get(cls, "o"),
                c=CLASS_COLORS.get(cls, "#999999"),
                edgecolors="#222222",
                linewidths=0.75,
                alpha=0.9,
            )
        ax.set_title(f"m* = {mass:g}")
        ax.set_xlabel("coeficiente de friccion mu")
        ax.xaxis.set_major_locator(MaxNLocator(5))
        ax.yaxis.set_major_locator(MaxNLocator(5))
        ax.set_xlim(
            official["friction_coefficient"].min() - 0.025,
            official["friction_coefficient"].max() + 0.025,
        )
        ax.set_ylim(official["dam_height"].min() - 0.006, official["dam_height"].max() + 0.006)
        if ax is axes[0]:
            ax.set_ylabel("altura hidraulica H (m)")
        ax.text(
            0.02,
            0.02,
            "tamano = Dmax",
            transform=ax.transAxes,
            fontsize=8.5,
            color="#555555",
            ha="left",
            va="bottom",
        )

    fig.suptitle("Mapa operativo de estabilidad por masa relativa")
    handles = class_legend()
    size_handles = [
        Line2D([0], [0], marker="o", color="none", markerfacecolor="#BBBBBB", markeredgecolor="#333333", markersize=6, label="~1% d_eq (1.0 mm)"),
        Line2D([0], [0], marker="o", color="none", markerfacecolor="#BBBBBB", markeredgecolor="#333333", markersize=10, label="~5% d_eq (5.0 mm)"),
        Line2D([0], [0], marker="o", color="none", markerfacecolor="#BBBBBB", markeredgecolor="#333333", markersize=14, label=">10% d_eq (>10 mm)"),
    ]
    fig.legend(
        handles + size_handles,
        [h.get_label() for h in handles + size_handles],
        loc="outside lower center",
        ncol=6,
        frameon=True,
    )
    png, svg = save_figure(fig, "01_response_map_h_mu_by_mass")
    return FigureRecord(
        "01_response_map_h_mu_by_mass",
        png,
        svg,
        "esencial",
        "Mapa H-mu separado por masa relativa; color/forma indica clase y tamano indica Dmax.",
        "Resume la frontera operacional aprendida por lotes dirigidos usando todos los casos oficiales hasta AL1.",
        "No interpolar visualmente: los puntos son simulaciones discretas, no una superficie continua validada.",
    )


def plot_margin_by_mu(df: pd.DataFrame) -> FigureRecord:
    official = df[df["is_official"]].copy()
    masses = sorted(official["boulder_mass"].dropna().unique())
    n = max(1, len(masses))
    fig, axes = plt.subplots(1, n, figsize=(4.2 * n, 4.2), sharey=True)
    axes = np.atleast_1d(axes)
    cmap = plt.get_cmap("viridis")
    h_values = sorted(official["dam_height"].dropna().unique())
    h_colors = {h: cmap(i / max(1, len(h_values) - 1)) for i, h in enumerate(h_values)}

    for ax, mass in zip(axes, masses):
        sub_mass = official[np.isclose(official["boulder_mass"], mass)]
        for h, sub in sub_mass.groupby("dam_height"):
            sub = sub.sort_values("friction_coefficient")
            plot_y = clipped_margin(sub["margin_pct"])
            ax.plot(
                sub["friction_coefficient"],
                plot_y,
                color=h_colors[h],
                lw=1.6,
                alpha=0.65,
            )
            ax.scatter(
                sub["friction_coefficient"],
                plot_y,
                s=72,
                c=[CLASS_COLORS.get(c, "#999999") for c in sub["criterion_class"]],
                marker="o",
                edgecolors="#222222",
                linewidths=0.65,
                zorder=3,
            )
            out = sub["margin_pct"] < MARGIN_YLIM[0]
            if out.any():
                ax.scatter(
                    sub.loc[out, "friction_coefficient"],
                    np.full(int(out.sum()), MARGIN_YLIM[0] + 0.8),
                    s=54,
                    c="#222222",
                    marker="v",
                    edgecolors="white",
                    linewidths=0.45,
                    zorder=4,
                )
        ax.axhline(0, color="#222222", lw=1.2)
        ax.set_ylim(*MARGIN_YLIM)
        ax.set_title(f"m* = {mass:g}")
        ax.set_xlabel("mu")
        ax.xaxis.set_major_locator(MaxNLocator(5))
        ax.yaxis.set_major_formatter(FuncFormatter(fmt_pct))
        if ax is axes[0]:
            ax.set_ylabel("margen al umbral (5% d_eq - Dmax)")
        if ax is axes[-1]:
            add_margin_secondary_y(ax)
        note_out_of_scale(ax, int((sub_mass["margin_pct"] < MARGIN_YLIM[0]).sum()))

    h_handles = [
        Line2D([0], [0], color=h_colors[h], lw=2.5, label=f"H={h:.3f} m")
        for h in h_values
    ]
    fig.legend(
        h_handles + class_legend()[:2],
        [h.get_label() for h in h_handles + class_legend()[:2]],
        loc="outside lower center",
        ncol=min(7, len(h_handles) + 2),
        frameon=True,
    )
    fig.suptitle("Margen de movilidad: positivo es estable, negativo es fallo")
    png, svg = save_figure(fig, "02_margin_vs_mu_by_mass_and_h")
    return FigureRecord(
        "02_margin_vs_mu_by_mass_and_h",
        png,
        svg,
        "esencial",
        "Margen continuo contra mu, con eje secundario en mm.",
        "Evita reducir la fisica a una clase binaria; muestra cuan lejos queda cada punto del umbral.",
        "Las lineas unen puntos de la misma H solo como ayuda visual, no como interpolacion formal.",
    )


def plot_batch_story_strip(df: pd.DataFrame) -> FigureRecord:
    official = df[df["is_official"]].copy()
    family_order = {family: i for i, (family, _label, _path) in enumerate(EXPORT_SPECS)}
    official["family_order"] = official["family"].map(family_order)
    official = official.sort_values(
        ["family_order", "dam_height", "boulder_mass", "friction_coefficient"]
    ).reset_index(drop=True)
    official["x"] = np.arange(len(official))

    fig, ax = plt.subplots(figsize=(13.8, 5.2))
    colors = [CLASS_COLORS.get(c, "#999999") for c in official["criterion_class"]]
    plot_margin = clipped_margin(official["margin_pct"])
    bars = ax.bar(
        official["x"],
        plot_margin,
        color=colors,
        edgecolor="#333333",
        linewidth=0.45,
        alpha=0.9,
    )
    ax.axhline(0, color="#222222", lw=1.25)
    ax.set_ylabel("margen al umbral (%)")
    add_margin_secondary_y(ax)
    ax.set_xlabel("casos ordenados por lote")
    ax.set_title("Historia de lotes: del piloto a AL1")
    ax.yaxis.set_major_formatter(FuncFormatter(fmt_pct))
    ax.set_xticks([])
    ax.set_ylim(*MARGIN_YLIM)

    for family, label, _path in EXPORT_SPECS:
        sub = official[official["family"] == family]
        if sub.empty:
            continue
        x0, x1 = sub["x"].min(), sub["x"].max()
        ax.axvspan(x0 - 0.5, x1 + 0.5, color=FAMILY_COLORS[family], alpha=0.055, lw=0)
        ax.text(
            (x0 + x1) / 2,
            ax.get_ylim()[1],
            label,
            ha="center",
            va="top",
            fontsize=9,
            color="#333333",
            bbox=dict(boxstyle="round,pad=0.22", fc="white", ec="#DDDDDD", lw=0.5),
        )
    out = official["margin_pct"] < MARGIN_YLIM[0]
    if out.any():
        ax.scatter(
            official.loc[out, "x"],
            np.full(int(out.sum()), MARGIN_YLIM[0] + 0.8),
            marker="v",
            s=34,
            c="#222222",
            edgecolors="white",
            linewidths=0.4,
            zorder=4,
        )
        note_out_of_scale(ax, int(out.sum()), where="lower left")
    png, svg = save_figure(fig, "03_batch_story_margin_strip")
    return FigureRecord(
        "03_batch_story_margin_strip",
        png,
        svg,
        "esencial",
        "Secuencia de lotes con margen continuo al umbral, en % y mm.",
        "Cuenta visualmente como el experimento dirigido paso de extremos a puntos de frontera.",
        "No representa orden temporal exacto de cada simulacion, sino orden logico por lote.",
    )


def plot_hydraulic_response(df: pd.DataFrame) -> FigureRecord:
    official = df[df["is_official"]].copy()
    fig, axes = plt.subplots(1, 2, figsize=(12.5, 4.7), sharey=True)
    for ax, xcol, xlabel in [
        (axes[0], "max_water_height_m", "altura maxima local hmax (m)"),
        (axes[1], "max_flow_velocity_ms", "velocidad maxima local Umax (m/s)"),
    ]:
        sub_all = official.dropna(subset=[xcol, "disp_pct_deq"])
        for cls, sub in sub_all.groupby("criterion_class"):
            ax.scatter(
                sub[xcol],
                sub["disp_pct_deq"],
                s=point_size(sub["disp_pct_deq"]),
                c=[MASS_COLORS.get(round(m, 2), "#999999") for m in sub["boulder_mass"]],
                marker=CLASS_MARKERS.get(cls, "o"),
                edgecolors="#222222",
                linewidths=0.7,
                alpha=0.88,
                label=cls,
            )
        ax.axhline(DISP_THRESHOLD_PCT, color="#222222", lw=1.15, ls="--")
        ax.set_ylim(*DISP_PCT_YLIM)
        ax.set_xlabel(xlabel)
        ax.yaxis.set_major_formatter(FuncFormatter(fmt_pct))
    axes[0].set_ylabel("Dmax (% d_eq)")
    add_disp_secondary_y(axes[-1])
    fig.suptitle("Respuesta del bloque frente a la hidraulica local")
    handles = [
        Line2D([0], [0], marker="o", color="none", markerfacecolor=color, markeredgecolor="#222222", markersize=8, label=f"m*={m:g}")
        for m, color in MASS_COLORS.items()
    ] + class_legend()[:2]
    fig.legend(
        handles,
        [h.get_label() for h in handles],
        loc="outside lower center",
        ncol=6,
        frameon=True,
    )
    png, svg = save_figure(fig, "04_local_hydraulics_vs_displacement")
    return FigureRecord(
        "04_local_hydraulics_vs_displacement",
        png,
        svg,
        "apoyo",
        "Relacion entre hmax/Umax locales y desplazamiento del bloque.",
        "Ayuda a explicar fisicamente los fallos mas alla de H nominal.",
        "Las gauges son diagnosticas: no sustituyen ChronoExchange como evidencia primaria del movimiento.",
    )


def plot_force_velocity_panels(df: pd.DataFrame) -> FigureRecord:
    official = df[df["is_official"]].copy()
    fig, axes = plt.subplots(1, 2, figsize=(12.2, 4.8), sharex=True)
    panels = [
        ("max_sph_force_N", "fuerza SPH maxima (N)", axes[0]),
        ("max_contact_force_N", "fuerza de contacto maxima (N)", axes[1]),
    ]
    for col, ylabel, ax in panels:
        sub_all = official.dropna(subset=["disp_pct_deq", col])
        for cls, sub in sub_all.groupby("criterion_class"):
            ax.scatter(
                sub["disp_pct_deq"],
                sub[col],
                s=70,
                c=[MASS_COLORS.get(round(m, 2), "#999999") for m in sub["boulder_mass"]],
                marker=CLASS_MARKERS.get(cls, "o"),
                edgecolors="#222222",
                linewidths=0.7,
                alpha=0.88,
            )
        ax.axvline(DISP_THRESHOLD_PCT, color="#222222", lw=1.15, ls="--")
        ax.set_xlim(*DISP_PCT_XLIM)
        note_out_of_scale(ax, int((sub_all["disp_pct_deq"] > DISP_PCT_XLIM[1]).sum()), where="upper right")
        ax.set_xlabel("Dmax (% d_eq)")
        ax.set_ylabel(ylabel)
        ax.xaxis.set_major_formatter(FuncFormatter(fmt_pct))
        add_disp_secondary_x(ax)
    fig.suptitle("Fuerzas reportadas frente al desplazamiento primario")
    handles = [
        Line2D([0], [0], marker="o", color="none", markerfacecolor=color, markeredgecolor="#222222", markersize=8, label=f"m*={m:g}")
        for m, color in MASS_COLORS.items()
    ] + class_legend()[:2]
    fig.legend(handles, [h.get_label() for h in handles], loc="outside lower center", ncol=6, frameon=True)
    png, svg = save_figure(fig, "05_forces_vs_displacement")
    return FigureRecord(
        "05_forces_vs_displacement",
        png,
        svg,
        "suplementaria",
        "Fuerza SPH y contacto contra Dmax, con eje superior en mm.",
        "Muestra que las fuerzas son diagnosticas y deben leerse junto al desplazamiento.",
        "Contacto no se usa como criterio de falla por su variabilidad; se reporta solo como diagnostico.",
    )


def plot_rotation_diagnostic(df: pd.DataFrame) -> FigureRecord:
    official = df[df["is_official"]].copy()
    fig, ax = plt.subplots(figsize=(7.6, 5.4))
    sub_all = official.dropna(subset=["disp_pct_deq", "max_rotation_deg"])
    offscale = (
        (sub_all["disp_pct_deq"] > DISP_PCT_XLIM[1])
        | (sub_all["max_rotation_deg"] > 22.0)
    )
    sub_plot = sub_all[~offscale]
    for cls, sub in sub_plot.groupby("criterion_class"):
        ax.scatter(
            sub["disp_pct_deq"],
            sub["max_rotation_deg"],
            s=point_size(sub["disp_pct_deq"]),
            c=[MASS_COLORS.get(round(m, 2), "#999999") for m in sub["boulder_mass"]],
            marker=CLASS_MARKERS.get(cls, "o"),
            edgecolors="#222222",
            linewidths=0.7,
            alpha=0.88,
        )
    ax.axvline(DISP_THRESHOLD_PCT, color="#222222", lw=1.2, ls="--")
    ax.axhline(5.0, color="#666666", lw=1.0, ls=":")
    ax.set_xlim(*DISP_PCT_XLIM)
    ax.set_ylim(0, 22)
    ax.set_xlabel("Dmax (% d_eq)")
    ax.set_ylabel("rotacion acumulada maxima (deg)")
    ax.xaxis.set_major_formatter(FuncFormatter(fmt_pct))
    add_disp_secondary_x(ax)
    ax.text(
        0.02,
        0.96,
        "clase decidida por desplazamiento; rotacion = diagnostico",
        transform=ax.transAxes,
        ha="left",
        va="top",
        fontsize=9,
        color="#444444",
        bbox=dict(boxstyle="round,pad=0.28", fc="white", ec="#DDDDDD", lw=0.5),
    )
    note_out_of_scale(ax, int(offscale.sum()), where="upper right")
    fig.suptitle("Rotacion diagnostica frente al criterio displacement_only")
    handles = [
        Line2D([0], [0], marker="o", color="none", markerfacecolor=color, markeredgecolor="#222222", markersize=8, label=f"m*={m:g}")
        for m, color in MASS_COLORS.items()
    ] + class_legend()[:2]
    fig.legend(handles, [h.get_label() for h in handles], loc="outside lower center", ncol=6, frameon=True)
    png, svg = save_figure(fig, "06_rotation_diagnostic_vs_displacement")
    return FigureRecord(
        "06_rotation_diagnostic_vs_displacement",
        png,
        svg,
        "esencial",
        "Rotacion acumulada maxima contra desplazamiento, con umbrales visuales.",
        "Evita la confusion metodologica: rotar no equivale a fallar bajo displacement_only.",
        "La rotacion se integra de la velocidad angular y se reporta como diagnostico acumulado.",
    )


def plot_cost_landscape(df: pd.DataFrame) -> FigureRecord:
    official = df[df["is_official"]].copy()
    fig, axes = plt.subplots(1, 2, figsize=(12.0, 4.5))
    for ax, col, ylabel in [
        (axes[0], "tiempo_min", "duracion (min)"),
        (axes[1], "mem_gpu_mb", "memoria GPU (MB)"),
    ]:
        sub_all = official.dropna(subset=[col, "family"])
        x_positions = {family: i for i, (family, _label, _path) in enumerate(EXPORT_SPECS)}
        xs = sub_all["family"].map(x_positions)
        jitter = (sub_all["dam_height"].fillna(0.2) - 0.2) * 7.5
        ax.scatter(
            xs + jitter,
            sub_all[col],
            s=65,
            c=[CLASS_COLORS.get(c, "#999999") for c in sub_all["criterion_class"]],
            edgecolors="#222222",
            linewidths=0.55,
            alpha=0.86,
        )
        ax.set_xticks(list(x_positions.values()))
        ax.set_xticklabels([label for _family, label, _path in EXPORT_SPECS], rotation=20)
        ax.set_ylabel(ylabel)
        ax.set_xlabel("lote")
    fig.suptitle("Costo computacional de la evidencia productiva")
    fig.legend(class_legend()[:2], ["Estable", "Fallo"], loc="outside lower center", ncol=2, frameon=True)
    png, svg = save_figure(fig, "07_computational_cost_by_batch")
    return FigureRecord(
        "07_computational_cost_by_batch",
        png,
        svg,
        "apoyo",
        "Tiempo y memoria de los lotes productivos oficiales.",
        "Justifica por que el refinamiento y active learning se hacen en lotes pequenos.",
        "Los campos de costo faltan en algunos exports; esos puntos se omiten.",
    )


def plot_mass_effect_summary(df: pd.DataFrame) -> FigureRecord:
    official = df[df["is_official"]].copy()
    fig, ax = plt.subplots(figsize=(8.6, 5.2))
    sub = official.dropna(subset=["boulder_mass", "disp_pct_deq", "friction_coefficient"])
    scatter = ax.scatter(
        sub["boulder_mass"],
        sub["disp_pct_deq"],
        c=sub["friction_coefficient"],
        cmap="cividis",
        s=point_size(sub["disp_pct_deq"]),
        marker="o",
        edgecolors=[CLASS_COLORS.get(c, "#999999") for c in sub["criterion_class"]],
        linewidths=1.35,
        alpha=0.9,
    )
    ax.axhline(DISP_THRESHOLD_PCT, color="#222222", lw=1.15, ls="--")
    ax.set_ylim(*DISP_PCT_YLIM)
    note_out_of_scale(ax, int((sub["disp_pct_deq"] > DISP_PCT_YLIM[1]).sum()), where="upper right")
    ax.set_xlabel("masa relativa m*")
    ax.set_ylabel("Dmax (% d_eq)")
    ax.yaxis.set_major_formatter(FuncFormatter(fmt_pct))
    add_disp_secondary_y(ax)
    cbar = fig.colorbar(scatter, ax=ax, pad=0.02)
    cbar.set_label("mu")
    ax.set_title("Efecto de masa relativa sobre movilidad")
    png, svg = save_figure(fig, "08_mass_effect_displacement_summary")
    return FigureRecord(
        "08_mass_effect_displacement_summary",
        png,
        svg,
        "apoyo",
        "Dmax contra m*, coloreado por mu y con borde por clase.",
        "Resume el aprendizaje central de batch4/AL1: m* baja aumenta criticidad.",
        "No controla por H en un solo panel; usar junto al mapa H-mu por masa.",
    )


def write_index(records: list[FigureRecord], master: pd.DataFrame) -> None:
    rows = [record.__dict__ for record in records]
    pd.DataFrame(rows).to_csv(OUTDIR / "figure_index.csv", index=False)
    official = master[master["is_official"]]
    partial = master[master["is_partial"]]
    lines = [
        "# Production Story Graphics",
        "",
        "Figuras derivadas de exports livianos oficiales: piloto, batch2, batch3, batch4 y AL1.",
        "",
        "## Regla visual aplicada",
        f"- El desplazamiento normalizado usa `Dmax (% d_eq)` y siempre muestra equivalente absoluto en mm cuando aparece como eje o escala principal.",
        f"- Umbral primario: `5% d_eq = {DISP_THRESHOLD_MM:.2f} mm`.",
        "- Colores de clase: verde = ESTABLE, rojo = FALLO, gris = parcial/no oficial.",
        "- La rotacion se muestra como diagnostico acumulado; no define la clase.",
        "- Las gauges hidraulicas explican contexto fisico, pero ChronoExchange sigue siendo la fuente primaria del movimiento del bloque.",
        "",
        "## Dataset",
        f"- Casos oficiales incluidos: {len(official)}.",
        f"- Casos parciales documentados pero no usados como evidencia principal: {len(partial)}.",
        f"- Rango H: {official['dam_height'].min():.3f} a {official['dam_height'].max():.3f} m.",
        f"- Rango mu: {official['friction_coefficient'].min():.3f} a {official['friction_coefficient'].max():.3f}.",
        f"- Rango m*: {official['boulder_mass'].min():.2f} a {official['boulder_mass'].max():.2f}.",
        "",
        "## Figuras esenciales",
    ]
    for record in records:
        if record.priority == "esencial":
            lines.extend(
                [
                    f"- `{record.png}` / `{record.svg}`",
                    f"  - Muestra: {record.shows}",
                    f"  - Importa: {record.why}",
                    f"  - Cautela: {record.caution}",
                ]
            )
    lines.extend(["", "## Figuras de apoyo y suplementarias"])
    for record in records:
        if record.priority != "esencial":
            lines.extend(
                [
                    f"- `{record.png}` / `{record.svg}` ({record.priority})",
                    f"  - Muestra: {record.shows}",
                    f"  - Importa: {record.why}",
                    f"  - Cautela: {record.caution}",
                ]
            )
    lines.extend(
        [
            "",
            "## Advertencias metodologicas",
            "- Estas figuras describen la frontera operacional a `dp=0.003`, no una frontera universal independiente de resolucion.",
            "- Los puntos unidos por lineas son guias visuales; la superficie formal debe venir de surrogate/GP y validacion posterior.",
            "- AL2 esta en ejecucion y no se incluye hasta tener export oficial.",
        ]
    )
    (OUTDIR / "FIGURE_INDEX.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    OUTDIR.mkdir(parents=True, exist_ok=True)
    master = load_master()
    if master.empty:
        raise SystemExit("No lightweight production exports found.")
    master.to_csv(OUTDIR / "master_production_story.csv", index=False)

    records = [
        plot_response_map(master),
        plot_margin_by_mu(master),
        plot_batch_story_strip(master),
        plot_hydraulic_response(master),
        plot_force_velocity_panels(master),
        plot_rotation_diagnostic(master),
        plot_cost_landscape(master),
        plot_mass_effect_summary(master),
    ]
    write_index(records, master)
    print(f"Generated {len(records)} production-story figures in {OUTDIR}")
    print(f"Master rows: {len(master)}")


if __name__ == "__main__":
    main()
