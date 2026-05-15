from __future__ import annotations

import html
import shutil
from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.patches import Ellipse, FancyArrowPatch, Polygon, Rectangle
import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "docs" / "convergence_story_web"
FIG = OUT / "figures"
DATA = OUT / "data"
PROCESSED = ROOT / "data" / "processed"
RESULTS = ROOT / "data" / "results"
HYDRAULIC_BENCH = ROOT / "data" / "benchmarks" / "hydraulic_20260508"
VERIFICATION = ROOT / "data" / "verification_preproduction_20260508"
ANALYTIC_PREPROD = ROOT / "data" / "analytic_comparison" / "20260508_preproduction"
PRODUCTION_STORY = ROOT / "data" / "figures" / "production_story_graphics"

D_EQ = 0.100421
REF_TIME = 0.5

GREEN = "#2f7d4f"
RED = "#b73b3b"
BLUE = "#2b6f9f"
AMBER = "#b98524"
GRAY = "#687385"
INK = "#17202a"

TEMPORAL_CASES = {
    0.006: "conv3_f05_full_dp0006",
    0.005: "conv3_f05_full_dp0005",
    0.004: "conv3_f05_full_dp0004",
    0.003: "conv3_f05_full_dp0003",
    0.002: "conv3_f05_full_dp0002",
}

CONVERGENCE_CASE_SPEC = [
    ("Fuente auditada", "data/logs/conv3_f05_full.log"),
    ("Serie", "conv3_f05_full"),
    ("Altura de presa / columna inicial", "0.20 m"),
    ("Masa del bloque", "1.00 kg"),
    ("Coeficiente de fricción bloque-playa", "mu = 0.50"),
    ("Pendiente de playa", "1:20"),
    ("Rotación adicional del bloque", "rot_z = 0.0 deg"),
    ("Rotación STL registrada", "(0.0, 0.0, 0.0) deg"),
    ("Posición inicial nominal", "(x, y, z) = (6.5, 0.5, 0.025) m"),
    ("Bloque", "BLIR3.stl, escala = 0.04"),
    ("Volumen / densidad", "0.00053023 m3 / 1886.0 kg/m3"),
    ("Diámetro equivalente", "d_eq = 0.100421 m"),
    ("Bbox bloque", "0.1710 x 0.2100 x 0.0399 m"),
    ("Canal", "L_flat=6.0 m, L_ramp=9.0 m, L_end=15.0 m, W=1.0 m, H=1.5 m"),
    ("Gauges", "12 velocity + 8 maxZ, reubicados según posición del bloque"),
    ("Resoluciones barridas", "dp = 0.010, 0.008, 0.006, 0.005, 0.004, 0.003, 0.002 m"),
]


def init() -> None:
    for path in [OUT, FIG, DATA]:
        path.mkdir(parents=True, exist_ok=True)
    for old in FIG.glob("*"):
        if old.suffix.lower() in {".png", ".svg"}:
            old.unlink()
    plt.rcParams.update(
        {
            "figure.dpi": 150,
            "savefig.dpi": 220,
            "font.family": "DejaVu Sans",
            "axes.titlesize": 11,
            "axes.labelsize": 9,
            "xtick.labelsize": 8,
            "ytick.labelsize": 8,
            "legend.fontsize": 8,
            "axes.spines.top": False,
            "axes.spines.right": False,
            "axes.grid": True,
            "grid.alpha": 0.18,
        }
    )


def save(name: str) -> None:
    for ext in ("png", "svg"):
        plt.savefig(FIG / f"{name}.{ext}", bbox_inches="tight", facecolor="white")
    plt.close()


def copy_verification_assets() -> None:
    assets = {
        HYDRAULIC_BENCH / "figures" / "front_position_benchmark.png": FIG / "09_benchmark_hidraulico.png",
        VERIFICATION / "figures" / "contact_sanity_timeseries.png": FIG / "10_contact_sanity.png",
        ANALYTIC_PREPROD / "figures" / "psi_vs_displacement.png": FIG / "11_comparacion_analitica.png",
    }
    for src, dst in assets.items():
        if src.exists():
            shutil.copy2(src, dst)


def copy_production_story_assets() -> None:
    assets = {
        "01_response_map_h_mu_by_mass": "12_mapa_productivo_h_mu_masa",
        "02_margin_vs_mu_by_mass_and_h": "13_margen_productivo_por_masa",
        "03_batch_story_margin_strip": "14_historia_lotes_al",
        "04_local_hydraulics_vs_displacement": "15_hidraulica_local_vs_desplazamiento",
        "05_forces_vs_displacement": "16_fuerzas_vs_desplazamiento",
        "06_rotation_diagnostic_vs_displacement": "17_rotacion_diagnostica_vs_desplazamiento",
        "08_mass_effect_displacement_summary": "18_efecto_masa_resumen",
    }
    for src_stem, dst_stem in assets.items():
        for ext in ("png", "svg"):
            src = PRODUCTION_STORY / f"{src_stem}.{ext}"
            if src.exists():
                shutil.copy2(src, FIG / f"{dst_stem}.{ext}")
    for name in ("master_production_story.csv", "figure_index.csv", "FIGURE_INDEX.md"):
        src = PRODUCTION_STORY / name
        if src.exists():
            shutil.copy2(src, DATA / name)


def read_csv(path: Path, **kwargs) -> pd.DataFrame:
    return pd.read_csv(path, **kwargs)


def speed(df: pd.DataFrame, prefix: str) -> pd.Series:
    return np.sqrt(df[f"{prefix}.x [m/s]"] ** 2 + df[f"{prefix}.y [m/s]"] ** 2 + df[f"{prefix}.z [m/s]"] ** 2)


def load_chrono(case_dir: str) -> pd.DataFrame:
    df = read_csv(PROCESSED / case_dir / "ChronoExchange_mkbound_51.csv", sep=";")
    t0 = df["time [s]"].iloc[0]
    x0 = df["fcenter.x [m]"].iloc[0]
    y0 = df["fcenter.y [m]"].iloc[0]
    z0 = df["fcenter.z [m]"].iloc[0]
    df["t_rel"] = df["time [s]"] - t0 + REF_TIME
    df["disp_pct"] = (
        np.sqrt(
            (df["fcenter.x [m]"] - x0) ** 2
            + (df["fcenter.y [m]"] - y0) ** 2
            + (df["fcenter.z [m]"] - z0) ** 2
        )
        / D_EQ
        * 100
    )
    df["block_speed"] = np.sqrt(df["fvel.x [m/s]"] ** 2 + df["fvel.y [m/s]"] ** 2 + df["fvel.z [m/s]"] ** 2)
    omega = np.sqrt(
        df["fomega.x [rad/s]"] ** 2
        + df["fomega.y [rad/s]"] ** 2
        + df["fomega.z [rad/s]"] ** 2
    )
    dt = df["time [s]"].diff().fillna(0)
    df["rotation_deg"] = (omega * dt).cumsum() * 180 / np.pi
    return df


def load_gauge(case_dir: str, file_name: str) -> pd.DataFrame:
    df = read_csv(PROCESSED / case_dir / file_name, sep=";")
    if "zmax [m]" in df:
        df.loc[df["zmax [m]"] < -1e20, "zmax [m]"] = np.nan
    if {"velx [m/s]", "vely [m/s]", "velz [m/s]"}.issubset(df.columns):
        df["vel_mag"] = np.sqrt(df["velx [m/s]"] ** 2 + df["vely [m/s]"] ** 2 + df["velz [m/s]"] ** 2)
    return df


def load_frontier() -> pd.DataFrame:
    path = DATA / "master_convergence_frontier.csv"
    if path.exists():
        return read_csv(path)
    raise FileNotFoundError("No existe master_convergence_frontier.csv")


def load_productive() -> pd.DataFrame:
    master = PRODUCTION_STORY / "master_production_story.csv"
    if master.exists():
        df = read_csv(master)
        if "is_official" in df.columns:
            official = df["is_official"].astype(str).str.lower().isin({"true", "1", "yes"})
            partial = df.get("is_partial", pd.Series(False, index=df.index)).astype(str).str.lower().isin({"true", "1", "yes"})
            df = df[official | partial].copy()
        if "lote" not in df.columns:
            df["lote"] = df.get("family_label", df.get("family", "produccion"))
        return df
    frames = []
    pilot = DATA / "pilot_summary.csv"
    batch2 = DATA / "batch2_summary.csv"
    if pilot.exists():
        p = read_csv(pilot)
        p["lote"] = "piloto"
        frames.append(p)
    if batch2.exists():
        b = read_csv(batch2)
        b["lote"] = "batch2"
        frames.append(b)
    return pd.concat(frames, ignore_index=True, sort=False) if frames else pd.DataFrame()


def interp_valid(t: np.ndarray, y: np.ndarray, common_t: np.ndarray) -> np.ndarray:
    mask = np.isfinite(t) & np.isfinite(y)
    t = t[mask]
    y = y[mask]
    if len(t) < 2:
        return np.full_like(common_t, np.nan, dtype=float)
    order = np.argsort(t)
    t = t[order]
    y = y[order]
    inside = (common_t >= t.min()) & (common_t <= t.max())
    out = np.full_like(common_t, np.nan, dtype=float)
    out[inside] = np.interp(common_t[inside], t, y)
    return out


def temporal_variable(case_dir: str, variable: str) -> tuple[np.ndarray, np.ndarray]:
    if variable in {"disp_pct", "block_speed", "rotation_deg"}:
        df = load_chrono(case_dir)
        return df["t_rel"].to_numpy(float), df[variable].to_numpy(float)
    if variable == "flow_speed":
        df = load_gauge(case_dir, "GaugesVel_V05.csv")
        return df["time [s]"].to_numpy(float), df["vel_mag"].to_numpy(float)
    if variable == "water_height":
        df = load_gauge(case_dir, "GaugesMaxZ_hmax03.csv")
        return df["time [s]"].to_numpy(float), df["zmax [m]"].to_numpy(float)
    raise ValueError(variable)


def temporal_error_table() -> pd.DataFrame:
    variables = {
        "disp_pct": "Desplazamiento",
        "block_speed": "Velocidad bloque",
        "flow_speed": "Velocidad flujo",
        "water_height": "Altura/cota agua",
        "rotation_deg": "Rotación",
    }
    fine_case = TEMPORAL_CASES[0.002]
    rows = []
    for var, label in variables.items():
        tf, yf = temporal_variable(fine_case, var)
        for dp, case_dir in TEMPORAL_CASES.items():
            t, y = temporal_variable(case_dir, var)
            t_min = max(np.nanmin(tf), np.nanmin(t))
            t_max = min(np.nanmax(tf), np.nanmax(t))
            common_t = np.linspace(t_min, t_max, 1500)
            yf_i = interp_valid(tf, yf, common_t)
            y_i = interp_valid(t, y, common_t)
            mask = np.isfinite(yf_i) & np.isfinite(y_i)
            if mask.sum() < 10:
                rmse_pct = np.nan
            else:
                scale = np.nanmax(yf_i[mask]) - np.nanmin(yf_i[mask])
                if scale <= 1e-12:
                    scale = max(np.nanmax(np.abs(yf_i[mask])), 1.0)
                rmse_pct = np.sqrt(np.nanmean((y_i[mask] - yf_i[mask]) ** 2)) / scale * 100
            rows.append({"dp": dp, "variable": var, "label": label, "temporal_rmse_pct": rmse_pct})
    return pd.DataFrame(rows)


def max_difference_table(summary: pd.DataFrame) -> pd.DataFrame:
    specs = {
        "max_displacement_m": "Desplazamiento máximo",
        "max_velocity_ms": "Velocidad bloque máx.",
        "max_flow_velocity_ms": "Velocidad flujo máx.",
        "max_water_height_m": "Altura/cota agua máx.",
        "max_rotation_deg": "Rotación máxima",
    }
    fine = summary.loc[np.isclose(summary["dp"], 0.002)].iloc[0]
    rows = []
    for col, label in specs.items():
        ref = float(fine[col])
        for _, row in summary.iterrows():
            value = float(row[col])
            rows.append(
                {
                    "dp": float(row["dp"]),
                    "variable": col,
                    "label": label,
                    "value": value,
                    "reference_dp": 0.002,
                    "reference_value": ref,
                    "delta_vs_fine_pct": (value - ref) / ref * 100 if ref else np.nan,
                }
            )
    return pd.DataFrame(rows)


def cls_color(value: str) -> str:
    return RED if str(value).upper() == "FALLO" else GREEN


def label_class(value: str) -> str:
    return "F" if str(value).upper() == "FALLO" else "E"


def disp_pct_to_mm(value: float | np.ndarray) -> float | np.ndarray:
    return np.asarray(value) * D_EQ * 1000.0 / 100.0


def disp_mm_to_pct(value: float | np.ndarray) -> float | np.ndarray:
    return np.asarray(value) * 100.0 / (D_EQ * 1000.0)


def add_disp_mm_yaxis(ax: plt.Axes, label: str = "Desplazamiento máximo (mm)") -> plt.Axes:
    sec = ax.secondary_yaxis("right", functions=(disp_pct_to_mm, disp_mm_to_pct))
    sec.set_ylabel(label)
    return sec


def add_disp_mm_xaxis(ax: plt.Axes, label: str = "Desplazamiento máximo (mm)") -> plt.Axes:
    sec = ax.secondary_xaxis("top", functions=(disp_pct_to_mm, disp_mm_to_pct))
    sec.set_xlabel(label)
    return sec


def add_relative_yaxis(ax: plt.Axes, reference_value: float, label: str = "Relativo a dp=0.002 (%)") -> plt.Axes:
    ref = float(reference_value)

    def to_pct(value: float | np.ndarray) -> float | np.ndarray:
        return np.asarray(value) / ref * 100.0 if ref else np.asarray(value) * np.nan

    def to_abs(value: float | np.ndarray) -> float | np.ndarray:
        return np.asarray(value) * ref / 100.0

    sec = ax.secondary_yaxis("right", functions=(to_pct, to_abs))
    sec.set_ylabel(label)
    return sec


def abs_delta_label(row: pd.Series) -> str:
    delta = float(row["value"] - row["reference_value"])
    variable = str(row["variable"])
    if variable == "max_displacement_m":
        return f"{delta * 1000:+.2f} mm"
    if variable in {"max_velocity_ms", "max_flow_velocity_ms"}:
        return f"{delta:+.3f} m/s"
    if variable == "max_water_height_m":
        return f"{delta * 1000:+.1f} mm"
    if variable == "max_rotation_deg":
        return f"{delta:+.2f} deg"
    return f"{delta:+.3g}"


def plot_00_setup_layout() -> None:
    fig, axes = plt.subplots(2, 1, figsize=(11.5, 6.6), constrained_layout=True)
    plan, elev = axes

    # Plan view: 30 m channel, 1 m width, boulder centered near the beach toe.
    plan.set_aspect("equal")
    plan.add_patch(Rectangle((0, 0), 30, 1.0, facecolor="#f7fbff", edgecolor="#32465a", linewidth=1.2))
    plan.add_patch(Rectangle((0, 0), 1.5, 1.0, facecolor="#9ecae1", edgecolor="none", alpha=0.72))
    plan.add_patch(Rectangle((1.5, 0), 4.5, 1.0, facecolor="#dbeafe", edgecolor="none", alpha=0.55))
    plan.add_patch(Rectangle((6.0, 0), 9.0, 1.0, facecolor="#efe5d1", edgecolor="none", alpha=0.78))
    plan.add_patch(Rectangle((15.0, 0), 15.0, 1.0, facecolor="#f4f1ea", edgecolor="none", alpha=0.82))
    plan.add_patch(Ellipse((6.50, 0.50), 0.22, 0.17, angle=0, facecolor="#6b5b4b", edgecolor="#241f1b", linewidth=1.0))
    plan.add_patch(FancyArrowPatch((0.55, 0.50), (6.05, 0.50), arrowstyle="->", mutation_scale=14, color=BLUE, linewidth=1.8))
    plan.text(0.75, 0.63, "flujo", color=BLUE, fontsize=9, weight="bold")
    plan.text(0.75, 0.12, "reservorio", color="#245d7a", fontsize=8)
    plan.text(6.55, 0.68, "bloque", color="#241f1b", fontsize=8, ha="center")
    plan.text(10.5, 0.08, "playa 1:20", color="#66512d", fontsize=8, ha="center")
    plan.text(22.5, 0.08, "zona final", color="#66512d", fontsize=8, ha="center")
    plan.set_xlim(-0.25, 30.25)
    plan.set_ylim(-0.15, 1.15)
    plan.set_title("Planta del canal numerico")
    plan.set_xlabel("x (m)")
    plan.set_ylabel("ancho y (m)")
    plan.set_yticks([0, 0.5, 1.0])

    # Elevation view: same x scale, exaggerated z for readability.
    elev.set_aspect("auto")
    bed = np.array([[0, 0], [6, 0], [15, 0.45], [30, 0.45], [30, -0.08], [0, -0.08]])
    elev.add_patch(Polygon(bed, closed=True, facecolor="#e8dcc6", edgecolor="#6b5b3e", linewidth=1.2))
    water = np.array([[0, 0], [1.5, 0], [1.5, 0.20], [0, 0.20]])
    elev.add_patch(Polygon(water, closed=True, facecolor="#9ecae1", edgecolor="#4f8bad", alpha=0.70))
    xb = 6.5
    zb = (xb - 6.0) / 20.0
    slope_angle = np.degrees(np.arctan(1 / 20))
    elev.add_patch(Ellipse((xb, zb + 0.030), 0.28, 0.070, angle=slope_angle, facecolor="#6b5b4b", edgecolor="#241f1b", linewidth=1.0))
    elev.add_patch(FancyArrowPatch((0.65, 0.18), (5.95, 0.025), arrowstyle="->", mutation_scale=14, color=BLUE, linewidth=1.8))
    elev.plot([6, 15], [0, 0.45], color="#8d7442", lw=1.2)
    elev.text(10.5, 0.30, "pendiente 1:20", color="#66512d", fontsize=8, rotation=slope_angle, ha="center")
    elev.text(xb, zb + 0.090, "bloque paralelo\na la playa", color="#241f1b", fontsize=8, ha="center")
    elev.text(0.6, 0.215, "H", color="#245d7a", fontsize=9, weight="bold")
    elev.set_xlim(-0.25, 30.25)
    elev.set_ylim(-0.05, 0.58)
    elev.set_title("Elevacion longitudinal")
    elev.set_xlabel("x (m)")
    elev.set_ylabel("z (m)")
    elev.text(
        0.99,
        0.04,
        "Esquema a escala en planta; elevacion con z realzado solo para lectura.",
        transform=elev.transAxes,
        ha="right",
        va="bottom",
        fontsize=8,
        color=GRAY,
    )
    fig.suptitle("Setup fisico: canal, playa y bloque irregular", fontsize=13, fontweight="bold")
    save("00_setup_planta_elevacion")


def plot_00_method_flow() -> None:
    fig, ax = plt.subplots(figsize=(10.6, 2.8))
    ax.axis("off")
    boxes = [
        ("1", "Convergencia de\nvariables continuas", "desplazamiento, velocidad,\naltura de agua, rotación"),
        ("2", "Selección de\nresolución SPH", "balance entre similitud de\nrespuesta y costo"),
        ("3", "Aplicación posterior:\nestabilidad", "frontera estable/fallo\ncon dp adoptado"),
    ]
    xs = [0.16, 0.50, 0.84]
    for x, (num, title, body) in zip(xs, boxes):
        ax.text(
            x,
            0.62,
            f"{num}. {title}",
            ha="center",
            va="center",
            fontsize=11,
            fontweight="bold",
            color=INK,
            bbox=dict(boxstyle="round,pad=0.55", fc="#ffffff", ec="#cfd8e3", lw=1.1),
        )
        ax.text(x, 0.23, body, ha="center", va="center", fontsize=8.5, color=GRAY)
    arrow_y = 0.62
    for x0, x1 in [(0.29, 0.37), (0.61, 0.71)]:
        ax.annotate(
            "",
            xy=(x1, arrow_y),
            xytext=(x0, arrow_y),
            arrowprops=dict(arrowstyle="->", lw=1.35, color=BLUE, shrinkA=0, shrinkB=0),
        )
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.set_title("Orden metodológico usado en la lectura final", fontsize=12, fontweight="bold", pad=8)
    save("00_orden_metodologico")


def plot_01_defensible_variables(diff: pd.DataFrame, errors: pd.DataFrame) -> None:
    labels = ["Altura/cota agua máx.", "Velocidad bloque máx.", "Desplazamiento máximo"]
    y = np.arange(len(labels))
    max_vals = [
        float(diff[(diff["label"] == label) & np.isclose(diff["dp"], 0.003)]["delta_vs_fine_pct"].iloc[0])
        for label in labels
    ]
    max_rows = [
        diff[(diff["label"] == label) & np.isclose(diff["dp"], 0.003)].iloc[0]
        for label in labels
    ]
    err_label_map = {
        "Altura/cota agua máx.": "Altura/cota agua",
        "Velocidad bloque máx.": "Velocidad bloque",
        "Desplazamiento máximo": "Desplazamiento",
    }
    err_vals = [
        float(errors[(errors["label"] == err_label_map[label]) & np.isclose(errors["dp"], 0.003)]["temporal_rmse_pct"].iloc[0])
        for label in labels
    ]

    fig, axes = plt.subplots(1, 2, figsize=(12.2, 5.0))
    axes[0].axvspan(-5, 5, color=GREEN, alpha=0.12, label="±5%")
    axes[0].axvspan(-7, 7, color=AMBER, alpha=0.10, label="zona cercana ±7%")
    axes[0].axvline(0, color=INK, lw=0.8)
    axes[0].barh(y, max_vals, color=[GREEN, GREEN, AMBER], alpha=0.9)
    for yi, val, row in zip(y, max_vals, max_rows):
        axes[0].text(
            val + (0.35 if val >= 0 else -0.35),
            yi,
            f"{val:+.1f}%\n{abs_delta_label(row)}",
            va="center",
            ha="left" if val >= 0 else "right",
            fontsize=8.4,
        )
    axes[0].set_yticks(y, labels)
    axes[0].set_xlabel("Diferencia relativa vs dp=0.002 (%) + diferencia absoluta")
    axes[0].set_title("A. Máximos: cuánto cambia cada variable")
    axes[0].text(
        0.98,
        0.98,
        "Verde: dentro de ±5%\nAmarillo: cercano (±5 a ±7%)",
        transform=axes[0].transAxes,
        ha="right",
        va="top",
        fontsize=8,
        color=GRAY,
        bbox=dict(fc="white", ec="#d8dee8", alpha=0.86, pad=4),
    )

    axes[1].axvspan(0, 5, color=GREEN, alpha=0.12, label="≤5%")
    axes[1].axvspan(5, 7, color=AMBER, alpha=0.10, label="cercano")
    axes[1].barh(y, err_vals, color=[GREEN, AMBER, AMBER], alpha=0.9)
    for yi, val in zip(y, err_vals):
        axes[1].text(val + 0.18, yi, f"{val:.1f}%", va="center", fontsize=9)
    axes[1].set_yticks(y, [""] * len(labels))
    axes[1].set_xlabel("Error relativo de la curva completa (RMSE, %)\nmenor = curva temporal más parecida a dp=0.002")
    axes[1].set_title("B. Forma temporal: cuánto se parece la curva")
    axes[1].text(
        0.98,
        0.98,
        "Verde: error ≤5%\nAmarillo: cercano (5 a 7%)",
        transform=axes[1].transAxes,
        ha="right",
        va="top",
        fontsize=8,
        color=GRAY,
        bbox=dict(fc="white", ec="#d8dee8", alpha=0.86, pad=4),
    )
    fig.suptitle("Comparación de dp=0.003 contra la referencia fina dp=0.002", fontsize=13, fontweight="bold")
    fig.subplots_adjust(left=0.18, right=0.98, top=0.80, bottom=0.17, wspace=0.30)
    save("01_variables_defendibles_dp003")


def plot_02_principal_trends(diff: pd.DataFrame) -> None:
    specs = [
        ("Desplazamiento máximo", "Desplazamiento máximo", 1000.0, "Dmax (mm)", BLUE, "mm"),
        ("Velocidad bloque máx.", "Velocidad del bloque", 1.0, "Vmax (m/s)", GREEN, "m/s"),
        ("Altura/cota agua máx.", "Altura/cota de agua", 1000.0, "hmax03 (mm)", AMBER, "mm"),
    ]
    fig, axes = plt.subplots(1, 3, figsize=(13.8, 4.6), constrained_layout=True)
    for ax, (label, title, scale, ylabel, color, unit) in zip(axes, specs):
        part = diff[(diff["label"] == label) & (diff["dp"] <= 0.006)].sort_values("dp").copy()
        part["abs_value"] = part["value"] * scale
        reference = float(part.loc[np.isclose(part["dp"], 0.002), "abs_value"].iloc[0])
        ax.plot(part["dp"], part["abs_value"], marker="o", lw=1.7, color=color)
        ax.axhspan(reference * 0.95, reference * 1.05, color=GREEN, alpha=0.12)
        ax.axhline(reference, color=INK, lw=0.8)
        ax.axvline(0.003, color=BLUE, ls=":", lw=1.1)
        row003 = part[np.isclose(part["dp"], 0.003)]
        if not row003.empty:
            row = row003.iloc[0]
            ax.scatter([row["dp"]], [row["abs_value"]], s=45, color=RED, zorder=4, edgecolor="white", linewidth=0.7)
            offset_y = 18 if label == "Desplazamiento máximo" else 12
            ax.annotate(
                f"{row['abs_value']:.2f} {unit}\n{100 + row['delta_vs_fine_pct']:.1f}%",
                xy=(row["dp"], row["abs_value"]),
                xytext=(10, offset_y),
                textcoords="offset points",
                fontsize=7.4,
                color=GRAY,
                va="center",
                ha="left",
                bbox=dict(fc="white", ec="none", alpha=0.82, pad=1.2),
            )
        add_relative_yaxis(ax, reference)
        ax.invert_xaxis()
        ax.set_xticks([0.006, 0.005, 0.004, 0.003, 0.002])
        ax.set_xticklabels(["0.006", "0.005", "0.004", "0.003", "0.002"], rotation=0)
        ax.set_xlabel("dp (m)")
        ax.set_ylabel(ylabel)
        ax.set_title(title)
    fig.suptitle(
        "Tendencia de variables principales en unidades físicas\n"
        "franja verde = +/-5% respecto de dp=0.002; eje derecho = valor relativo",
        fontsize=12.5,
        fontweight="bold",
    )
    save("02_tendencia_variables_principales")


def plot_03_temporal_curves_fine_set() -> None:
    dps = [0.004, 0.003, 0.002]
    fig, axes = plt.subplots(1, 3, figsize=(12.0, 4.0), constrained_layout=True)
    for dp in dps:
        case_dir = TEMPORAL_CASES[dp]
        chrono = load_chrono(case_dir)
        hmax = load_gauge(case_dir, "GaugesMaxZ_hmax03.csv")
        label = f"dp={dp:.3f}"
        axes[0].plot(chrono["t_rel"], disp_pct_to_mm(chrono["disp_pct"]), lw=1.35, label=label)
        axes[1].plot(chrono["t_rel"], chrono["block_speed"], lw=1.25, label=label)
        axes[2].plot(hmax["time [s]"], hmax["zmax [m]"] * 1000.0, lw=1.25, label=label)
    axes[0].axhline(0.05 * D_EQ * 1000.0, color=RED, ls="--", lw=1.0)
    axes[0].set_title("Desplazamiento")
    axes[0].set_ylabel("D(t) (mm)")
    sec = axes[0].secondary_yaxis("right", functions=(disp_mm_to_pct, disp_pct_to_mm))
    sec.set_ylabel("D(t) (% d_eq)")
    axes[0].text(
        0.04,
        0.94,
        "linea roja: 5% d_eq = 5.02 mm",
        transform=axes[0].transAxes,
        ha="left",
        va="top",
        fontsize=7.2,
        color=RED,
        bbox=dict(fc="white", ec="none", alpha=0.78, pad=1.2),
    )
    axes[1].set_title("Velocidad del bloque")
    axes[1].set_ylabel("V(t) (m/s)")
    axes[2].set_title("Altura/cota de agua")
    axes[2].set_ylabel("zmax hmax03 (mm)")
    for ax in axes:
        ax.set_xlabel("Tiempo (s)")
    axes[1].legend(frameon=False, fontsize=7)
    fig.suptitle("Curvas temporales del rango fino en unidades físicas", fontsize=12, fontweight="bold")
    save("03_curvas_temporales_finas")


def plot_04_sensitive_outputs(diff: pd.DataFrame, errors: pd.DataFrame) -> None:
    fig, axes = plt.subplots(1, 2, figsize=(10.0, 4.0), constrained_layout=True)
    for ax, label, color in [
        (axes[0], "Velocidad flujo máx.", BLUE),
        (axes[1], "Rotación máxima", AMBER),
    ]:
        part = diff[diff["label"] == label].sort_values("dp")
        ax.axhspan(-5, 5, color=GREEN, alpha=0.10)
        ax.axhline(0, color=INK, lw=0.8)
        ax.plot(part["dp"], part["delta_vs_fine_pct"], marker="o", color=color, lw=1.6)
        ax.scatter([0.003], part.loc[np.isclose(part["dp"], 0.003), "delta_vs_fine_pct"], color=RED, zorder=4)
        row003 = part[np.isclose(part["dp"], 0.003)]
        if not row003.empty:
            row = row003.iloc[0]
            ax.text(
                0.00305,
                row["delta_vs_fine_pct"],
                abs_delta_label(row),
                fontsize=8,
                color=GRAY,
                va="center",
                ha="left",
                bbox=dict(fc="white", ec="none", alpha=0.76, pad=1.4),
            )
        ax.invert_xaxis()
        ax.set_xlabel("dp (m)")
        ax.set_ylabel("Cambio vs dp=0.002 (%)")
        ax.set_title(label)
    fig.suptitle("Salidas sensibles: se reportan, pero no sostienen solas la decisión", fontsize=12, fontweight="bold")
    save("04_salidas_sensibles")


def plot_05_cost_vs_dp(summary: pd.DataFrame) -> None:
    df = summary.sort_values("dp")
    fig, axes = plt.subplots(1, 3, figsize=(10.2, 3.5), constrained_layout=True)
    specs = [
        ("n_particles", "Partículas"),
        ("mem_gpu_mb", "Memoria GPU (MB)"),
        ("tiempo_min", "Tiempo (min)"),
    ]
    for ax, (col, title) in zip(axes, specs):
        ax.plot(df["dp"], df[col], marker="o", color=AMBER, lw=1.5)
        ax.axvline(0.003, color=BLUE, ls=":", lw=1.2)
        ax.invert_xaxis()
        ax.set_xlabel("dp (m)")
        ax.set_title(title)
    fig.suptitle("Costo computacional del refinamiento", fontsize=12, fontweight="bold")
    save("05_costo_vs_dp")


def plot_06_frontier_after_resolution(frontier: pd.DataFrame) -> None:
    df = frontier[
        (frontier["dp"].round(3) == 0.003)
        & (frontier["mu"].between(0.674, 0.686))
        & (frontier["evidence_scope"].isin(["principal_frontier", "frontier_refinement", "repeatability_check"]))
    ].copy()
    df = df.sort_values("mu")
    fig, ax = plt.subplots(figsize=(7.4, 4.4))
    for _, row in df.iterrows():
        ax.scatter(row["mu"], row["disp_pct_deq"], s=58, color=cls_color(row["criterion_class"]), edgecolor="white", linewidth=0.8, zorder=3)
        ax.text(row["mu"], row["disp_pct_deq"] + 0.24, label_class(row["criterion_class"]), ha="center", fontsize=8)
    ax.axhline(5, color=RED, linestyle="--", linewidth=1.1, label="umbral 5% d_eq")
    ax.axvspan(0.68050, 0.68075, color=AMBER, alpha=0.20, label="intervalo de transición")
    ax.annotate(
        "frontera práctica\nacotada",
        xy=(0.680625, 9.2),
        xytext=(0.6762, 8.4),
        arrowprops=dict(arrowstyle="->", lw=0.9, color=AMBER),
        fontsize=8,
        color="#74510f",
    )
    ax.set_xlabel("Coeficiente de fricción bloque-suelo, μ")
    ax.set_ylabel("Desplazamiento máximo (% d_eq)")
    add_disp_mm_yaxis(ax)
    ax.set_title("Uso posterior del dp adoptado: frontera de estabilidad")
    ax.set_xlim(0.674, 0.686)
    ax.set_ylim(0, 10.6)
    ax.legend(frameon=False, loc="lower right")
    save("06_frontera_posterior_dp003")


def plot_07_resolution_sensitivity(frontier: pd.DataFrame) -> None:
    df = frontier[
        (frontier["dp"].round(3).isin([0.002, 0.003]))
        & (frontier["mu"].between(0.674, 0.686))
        & (frontier["evidence_scope"].isin(["principal_frontier", "frontier_refinement", "repeatability_check"]))
    ].copy()
    fig, axes = plt.subplots(1, 2, figsize=(9.6, 4.0), sharey=True, constrained_layout=True)
    for ax, dp in zip(axes, [0.003, 0.002]):
        part = df[df["dp"].round(3) == dp].sort_values("mu")
        for _, row in part.iterrows():
            ax.scatter(row["mu"], row["disp_pct_deq"], s=52, color=cls_color(row["criterion_class"]), edgecolor="white", linewidth=0.8)
            ax.text(row["mu"], row["disp_pct_deq"] + 0.28, label_class(row["criterion_class"]), ha="center", fontsize=8)
        ax.axhline(5, color=RED, linestyle="--", linewidth=1.1)
        ax.set_title(f"dp={dp:.3f} m")
        ax.set_xlabel("μ")
        ax.set_xlim(0.674, 0.686)
        ax.set_ylim(0, 10.6)
    axes[0].set_ylabel("Desplazamiento máximo (% d_eq)")
    add_disp_mm_yaxis(axes[-1])
    axes[0].axvspan(0.68050, 0.68075, color=AMBER, alpha=0.18)
    axes[1].text(0.6744, 8.6, "en dp=0.002 los casos\ncercanos quedan bajo 5%", fontsize=8, color=BLUE)
    fig.suptitle("Sensibilidad de la clasificación al cambiar resolución", fontsize=12, fontweight="bold")
    save("07_sensibilidad_frontera_dp")


def plot_08_productive(prod: pd.DataFrame) -> None:
    if prod.empty:
        return
    fig, axes = plt.subplots(1, 2, figsize=(10.2, 4.0), constrained_layout=True)
    def mark_threshold(ax) -> None:
        ax.axhline(5, color=RED, linestyle="--", linewidth=1.1)
        ax.text(
            0.98,
            5,
            "umbral de movimiento: 5% d_eq",
            transform=ax.get_yaxis_transform(),
            ha="right",
            va="bottom",
            fontsize=8,
            color=RED,
            bbox=dict(fc="white", ec="none", alpha=0.78, pad=2),
        )

    base = prod[(prod["dam_height"].round(3) == 0.2) & (prod["slope_inv"].round(0) == 20)].copy()
    for _, row in base.sort_values("friction_coefficient").iterrows():
        axes[0].scatter(row["friction_coefficient"], row["disp_pct_deq"], s=58, color=cls_color(row["criterion_class"]), edgecolor="white", linewidth=0.8)
    mark_threshold(axes[0])
    axes[0].set_title("Condición base posterior")
    axes[0].set_xlabel("μ")
    axes[0].set_ylabel("Desplazamiento máximo (% d_eq)")
    hcases = prod[(prod["slope_inv"].round(0) == 20) & (prod["friction_coefficient"].between(0.67, 0.73))].copy()
    for _, row in hcases.sort_values("dam_height").iterrows():
        axes[1].scatter(row["dam_height"], row["disp_pct_deq"], s=58, color=cls_color(row["criterion_class"]), edgecolor="white", linewidth=0.8)
        if row["disp_pct_deq"] > 10:
            axes[1].text(row["dam_height"], row["disp_pct_deq"] + 4, f"{row['disp_pct_deq']:.0f}%", ha="center", fontsize=8)
    mark_threshold(axes[1])
    axes[1].set_title("Variación hidráulica posterior")
    axes[1].set_xlabel("Altura inicial H (m)")
    axes[1].set_ylabel("Desplazamiento máximo (% d_eq)")
    fig.suptitle("Lotes posteriores con dp=0.003", fontsize=12, fontweight="bold")
    save("08_lotes_posteriores")


def productive_rows(prod: pd.DataFrame) -> str:
    if prod.empty:
        return ""
    rows = []
    for _, row in prod.sort_values(["lote", "dam_height", "friction_coefficient", "slope_inv"]).iterrows():
        cls = "fail" if str(row["criterion_class"]).upper() == "FALLO" else "stable"
        rows.append(
            f"<tr><td>{row['lote']}</td><td><code>{row['case_id']}</code></td>"
            f"<td>{row['dam_height']:.3f}</td><td>{row['friction_coefficient']:.4f}</td>"
            f"<td>1:{row['slope_inv']:.0f}</td><td><span class='pill {cls}'>{row['criterion_class']}</span></td>"
            f"<td>{row['disp_pct_deq']:.2f}%</td><td>{row['max_rotation_deg']:.2f}°</td></tr>"
        )
    return "\n".join(rows)


LIGHTBOX = """
<div id="lightbox" class="lightbox" aria-hidden="true">
  <button class="lightbox-close" type="button" aria-label="Cerrar">×</button>
  <img alt="">
  <p></p>
</div>
<script>
  const lightbox = document.getElementById('lightbox');
  const lightboxImg = lightbox.querySelector('img');
  const lightboxCaption = lightbox.querySelector('p');
  const closeLightbox = () => {
    lightbox.classList.remove('open');
    lightbox.setAttribute('aria-hidden', 'true');
    lightboxImg.removeAttribute('src');
  };
  document.querySelectorAll('figure img').forEach((img) => {
    img.setAttribute('tabindex', '0');
    img.setAttribute('role', 'button');
    img.setAttribute('title', 'Clic para ampliar');
    const open = () => {
      lightboxImg.src = img.src;
      lightboxImg.alt = img.alt || '';
      const caption = img.closest('figure')?.querySelector('figcaption')?.textContent || '';
      lightboxCaption.textContent = caption;
      lightbox.classList.add('open');
      lightbox.setAttribute('aria-hidden', 'false');
    };
    img.addEventListener('click', open);
    img.addEventListener('keydown', (event) => {
      if (event.key === 'Enter' || event.key === ' ') {
        event.preventDefault();
        open();
      }
    });
  });
  lightbox.addEventListener('click', (event) => {
    if (event.target === lightbox || event.target.classList.contains('lightbox-close')) closeLightbox();
  });
  document.addEventListener('keydown', (event) => {
    if (event.key === 'Escape') closeLightbox();
  });
</script>
"""


def productive_rows(prod: pd.DataFrame) -> str:
    if prod.empty:
        return ""
    rows = []
    data = prod.copy()
    for col in ("lote", "dam_height", "boulder_mass", "friction_coefficient", "slope_inv"):
        if col not in data.columns:
            data[col] = np.nan if col != "lote" else "produccion"
    data = data.sort_values(["lote", "dam_height", "boulder_mass", "friction_coefficient", "slope_inv"], na_position="last")
    for _, row in data.iterrows():
        cls = "fail" if str(row["criterion_class"]).upper() == "FALLO" else "stable"
        disp_mm = row.get("disp_mm", np.nan)
        if pd.isna(disp_mm):
            disp_mm = float(row["disp_pct_deq"]) / 100 * D_EQ * 1000
        mass = row.get("boulder_mass", np.nan)
        rows.append(
            f"<tr><td>{row['lote']}</td><td><code>{row['case_id']}</code></td>"
            f"<td>{row['dam_height']:.3f}</td><td>{mass:.2f}</td><td>{row['friction_coefficient']:.4f}</td>"
            f"<td>1:{row['slope_inv']:.0f}</td><td><span class='pill {cls}'>{row['criterion_class']}</span></td>"
            f"<td>{row['disp_pct_deq']:.2f}%</td><td>{disp_mm:.2f} mm</td><td>{row['max_rotation_deg']:.2f} deg</td></tr>"
        )
    return "\n".join(rows)


def convergence_case_spec_rows() -> str:
    return "\n".join(
        f"<tr><th>{html.escape(name)}</th><td>{html.escape(value)}</td></tr>"
        for name, value in CONVERGENCE_CASE_SPEC
    )


def convergence_rows(summary: pd.DataFrame) -> str:
    rows = []
    cols = [
        "dp",
        "case_name",
        "status",
        "max_displacement_m",
        "max_velocity_ms",
        "max_water_height_m",
        "max_flow_velocity_ms",
        "max_rotation_deg",
        "sim_time_s",
        "n_timesteps",
        "n_particles",
        "mem_gpu_mb",
        "tiempo_min",
    ]
    df = summary[cols].copy().sort_values("dp", ascending=False)
    df["disp_mm"] = df["max_displacement_m"] * 1000.0
    df["disp_pct"] = df["max_displacement_m"] / D_EQ * 100.0
    for _, row in df.iterrows():
        rows.append(
            "<tr>"
            f"<td>{row['dp']:.3f}</td>"
            f"<td><code>{row['case_name']}</code></td>"
            f"<td>{row['status']}</td>"
            f"<td>{row['disp_mm']:.2f}</td>"
            f"<td>{row['disp_pct']:.1f}%</td>"
            f"<td>{row['max_velocity_ms']:.3f}</td>"
            f"<td>{row['max_water_height_m']:.3f}</td>"
            f"<td>{row['max_flow_velocity_ms']:.3f}</td>"
            f"<td>{row['max_rotation_deg']:.2f}</td>"
            f"<td>{row['sim_time_s']:.3f}</td>"
            f"<td>{row['n_timesteps']:.0f}</td>"
            f"<td>{row['n_particles'] / 1e6:.2f} M</td>"
            f"<td>{row['mem_gpu_mb'] / 1024:.1f} GB</td>"
            f"<td>{row['tiempo_min']:.1f}</td>"
            "</tr>"
        )
    return "\n".join(rows)


def write_page(prod: pd.DataFrame, summary: pd.DataFrame) -> None:
    html = f"""<!doctype html>
<html lang="es">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Convergencia de resolución SPH</title>
  <link rel="stylesheet" href="styles.css">
</head>
<body>
<main class="page">
  <header class="top">
    <div>
      <p class="meta">Tesis UCN · modelo SPH-Chrono</p>
      <h1>Convergencia de resolución SPH</h1>
      <p>Esta pagina resume por que se adopta <code>dp=0.003 m</code> como resolucion operativa. La produccion dirigida y active learning quedan en una pagina separada.</p>
    </div>
  </header>

    <section>
      <h2>1. Enfoque del estudio</h2>
      <dl class="key-strip">
        <div><dt>Resolución adoptada</dt><dd>dp = 0.003 m</dd></div>
        <div><dt>Convergencia</dt><dd>variables temporales y máximos</dd></div>
        <div><dt>Estabilidad</dt><dd>análisis posterior al dp elegido</dd></div>
        <div><dt>Post-convergencia</dt><dd><a href="https://kcortes765.github.io/convergencia-dp/post-convergencia/">pagina dedicada</a></dd></div>
      </dl>
      <figure>
        <img src="figures/00_setup_planta_elevacion.png" alt="Planta y elevacion del setup SPH">
        <figcaption>Setup fisico usado en la lectura: canal, playa 1:20 y bloque irregular apoyado sobre la playa. La planta mantiene escala horizontal; la elevacion realza z para legibilidad.</figcaption>
      </figure>
      <p>SPH no usa una malla fija; usa partículas. Por eso aquí <code>dp</code> significa <strong>espaciamiento inicial entre partículas</strong> y se interpreta como resolución espacial del modelo.</p>
      <p>El análisis se ordena así: primero se comparan variables continuas para distintos <code>dp</code>, como desplazamiento del bloque, velocidad del bloque, velocidad del flujo y altura de agua en gauges. Esa es la parte de convergencia o sensibilidad de resolución.</p>
      <p>Luego, con una resolución seleccionada por equilibrio entre respuesta y costo, se analiza si el bloque inicia movimiento bajo un criterio operacional. Esa segunda parte es el estudio de estabilidad, no el reemplazo del análisis de convergencia.</p>
      <div class="callout">
        <h3>Qué exige una convergencia clásica</h3>
        <p>En un estudio CFD ideal, al refinar la discretización las variables deberían acercarse a un valor asintótico. Con tres o más resoluciones se puede estimar orden de convergencia, extrapolación de Richardson y una banda tipo GCI. Ese enfoque es el marco de referencia correcto.</p>
        <p>En este caso se adapta a SPH usando <code>dp</code> como escala de resolución. Sin embargo, la clasificación estable/fallo no es una variable suave: depende de contacto, superficie libre y un umbral de desplazamiento. Por eso la convergencia se evalúa primero sobre variables continuas, no sobre la clase final.</p>
      </div>
      <figure>
        <img src="figures/00_orden_metodologico.png" alt="Orden metodológico del análisis">
        <figcaption>La lectura final separa convergencia de variables, selección de resolución y análisis posterior de estabilidad.</figcaption>
      </figure>
    </section>

  <section>
    <h2>2. Variables que sostienen la resolución adoptada</h2>
    <p>La lectura de convergencia se concentró en variables continuas, antes de clasificar estabilidad. Para defender <code>dp=0.003 m</code> no se usan todas las salidas con el mismo peso: se priorizan las que describen el movimiento principal del bloque y el forzante hidráulico.</p>
    <p>El caso <code>dp=0.002 m</code> se usa como referencia fina. La lectura no es que la convergencia sea perfecta: en <code>dp=0.003 m</code>, la altura/cota de agua y la velocidad máxima del bloque quedan dentro o muy cerca de una banda de 5%, mientras que el desplazamiento máximo queda levemente fuera, con una diferencia cercana a 6%. Esta evidencia sostiene una <strong>estabilización práctica</strong> de las variables principales, suficiente para adoptar una resolución operativa con cautela.</p>
      <figure>
        <img src="figures/01_variables_defendibles_dp003.png" alt="Variables principales que sostienen dp 0.003">
      <figcaption>Variables principales en <code>dp=0.003 m</code> comparadas con <code>dp=0.002 m</code>. Cada diferencia porcentual incluye su diferencia absoluta: mm para desplazamiento/altura y m/s para velocidad.</figcaption>
      <div class="read-guide">
        <strong>Cómo leer esta figura:</strong>
        <ul>
          <li><strong>Panel A:</strong> compara solo el valor máximo. Cero significa igual al caso fino <code>dp=0.002 m</code>; las etiquetas agregan la diferencia absoluta.</li>
          <li><strong>Panel B:</strong> compara la forma completa de la curva temporal. Menor porcentaje significa curva más parecida al caso fino.</li>
          <li><strong>Conclusión:</strong> el agua y la velocidad del bloque son las evidencias más limpias; el desplazamiento queda cercano y se acepta con cautela.</li>
        </ul>
      </div>
    </figure>
    <h3>Ficha del caso físico usado para la convergencia</h3>
    <p>Todos los valores de la tabla por resolución corresponden a este mismo caso físico; lo único que cambia entre filas es <code>dp</code>.</p>
    <div class="table-wrap compact-table">
      <table>
        <tbody>{convergence_case_spec_rows()}</tbody>
      </table>
    </div>
    <p class="note">Ficha reconstruida desde <code>data/logs/conv3_f05_full.log</code>. Esta es la condición específica usada para la convergencia continua; no representa todos los casos productivos posteriores.</p>
    <h3>Resultados por resolución</h3>
    <div class="table-wrap">
      <table>
        <thead>
          <tr>
            <th>dp (m)</th>
            <th>Caso corrido</th>
            <th>Estado</th>
            <th>Dmax (mm)</th>
            <th>Dmax (% d_eq)</th>
            <th>V bloque max (m/s)</th>
            <th>h agua max (m)</th>
            <th>U flujo max (m/s)</th>
            <th>Rot. acum. max (deg)</th>
            <th>t sim (s)</th>
            <th>pasos</th>
            <th>Particulas</th>
            <th>Mem GPU</th>
            <th>Tiempo (min)</th>
          </tr>
        </thead>
        <tbody>{convergence_rows(summary)}</tbody>
      </table>
    </div>
    <p class="note">Tabla derivada de <code>data/results/conv3_f05_full.csv</code>. Cada fila corresponde al caso realmente corrido para una resolucion <code>dp</code>; el desplazamiento se muestra en mm y normalizado por <code>d_eq=0.100421 m</code>.</p>
    <div class="figure-stack">
      <figure>
        <img src="figures/02_tendencia_variables_principales.png" alt="Tendencia de variables principales hacia el caso fino">
        <figcaption>En el rango fino, las variables principales se muestran en unidades físicas: Dmax en mm, velocidad en m/s y altura/cota en mm. El eje derecho conserva la lectura relativa respecto de <code>dp=0.002 m</code>.</figcaption>
      </figure>
      <figure>
        <img src="figures/03_curvas_temporales_finas.png" alt="Curvas temporales de desplazamiento, velocidad del bloque y altura de agua">
        <figcaption>Curvas temporales del rango fino en unidades absolutas: desplazamiento en mm, velocidad del bloque en m/s y altura/cota de agua en mm. El porcentaje del desplazamiento queda solo como eje auxiliar.</figcaption>
      </figure>
    </div>
  </section>

  <section>
    <h2>3. Salidas sensibles y límite de la conclusión</h2>
    <p>No todas las salidas tienen el mismo nivel de cierre. La velocidad de flujo puntual en un gauge y la rotación acumulada del bloque son más sensibles al refinamiento. Por eso se muestran como límite del análisis, pero no se usan como base principal para fijar <code>dp</code> ni para clasificar el movimiento.</p>
    <div class="grid">
      <figure>
        <img src="figures/04_salidas_sensibles.png" alt="Salidas sensibles al refinamiento de dp">
        <figcaption>La velocidad de flujo puntual y la rotación muestran mayor sensibilidad. Esto se declara explícitamente para no presentar una convergencia más fuerte que la observada.</figcaption>
      </figure>
      <figure>
        <img src="figures/05_costo_vs_dp.png" alt="Costo computacional contra dp">
        <figcaption>El refinamiento reduce <code>dp</code>, pero aumenta fuertemente partículas, memoria y tiempo. El caso <code>dp=0.002 m</code> es útil como referencia fina, pero costoso como resolución productiva.</figcaption>
      </figure>
    </div>
    <p class="note"><strong>Lectura defendible:</strong> <code>dp=0.003 m</code> se adopta porque las variables principales se estabilizan en el rango fino y el costo de <code>dp=0.002 m</code> crece mucho. La conclusión no es “todo converge perfectamente”, sino “la resolución es suficientemente cercana al caso fino para continuar con un análisis productivo conservador, manteniendo controles puntuales a <code>dp=0.002 m</code>”.</p>
  </section>

  <section>
    <h2>4. Uso posterior: estabilidad y frontera</h2>
    <p>Una vez fijado <code>dp=0.003 m</code>, se puede estudiar estabilidad. Aquí <strong>frontera</strong> significa el intervalo de fricción <code>μ</code> donde, bajo la misma geometría y forzante, el bloque cambia entre no superar y superar el umbral de movimiento.</p>
    <p>El umbral usado es <code>D_max &gt; 5% d_eq</code>, donde <code>D_max</code> es el desplazamiento máximo del bloque y <code>d_eq</code> su diámetro equivalente. La rotación se informa aparte como variable observada.</p>
    <div class="figure-stack">
      <figure>
        <img src="figures/06_frontera_posterior_dp003.png" alt="Frontera posterior con dp 0.003">
        <figcaption>Con <code>dp=0.003 m</code>, la condición base queda acotada entre <code>μ=0.68050</code> y <code>μ=0.68075</code>.</figcaption>
      </figure>
      <figure>
        <img src="figures/07_sensibilidad_frontera_dp.png" alt="Sensibilidad de la frontera al cambiar dp">
        <figcaption>Al refinar a <code>dp=0.002 m</code>, los casos cercanos quedan bajo el umbral. Esto se reporta como sensibilidad de resolución de la frontera.</figcaption>
      </figure>
    </div>
  </section>

  <section>
    <h2>5. Post-convergencia separado</h2>
    <p>Los lotes productivos, el efecto de masa, la hidraulica local, las fuerzas, la rotacion diagnostica y active learning se movieron a una pagina dedicada para no mezclar la seleccion de <code>dp</code> con el analisis posterior.</p>
    <p><a class="button-link" href="https://kcortes765.github.io/convergencia-dp/post-convergencia/">Abrir pagina post-convergencia</a></p>
  </section>

  <section>
    <h2>6. Analisis final y literatura usada</h2>
    <p>Sin un experimento fisico propio del bloque, la tesis no debe afirmar validacion experimental directa del caso completo. La defensa se arma por capas: sensibilidad de resolucion, benchmark hidraulico externo, sanity de contacto bloque-suelo y comparacion analitica de orden de magnitud. Cada capa responde una pregunta distinta.</p>
    <div class="table-wrap">
      <table>
        <thead><tr><th>Capa</th><th>Que permite afirmar</th><th>Que no permite afirmar</th><th>Base de literatura</th></tr></thead>
        <tbody>
          <tr><td>Convergencia/sensibilidad de <code>dp</code></td><td>Las variables continuas principales se estabilizan en el rango fino y <code>dp=0.003 m</code> es una resolucion operativa defendible.</td><td>No demuestra convergencia asintotica fuerte de la clase estable/fallo.</td><td>Richardson/Roache-GCI y tutorial NASA WIND sobre refinamiento espacial.</td></tr>
          <tr><td>Benchmark hidraulico</td><td>La instalacion local de GenCase/DualSPHysics/GPU/postproceso reproduce un dam-break conocido.</td><td>No valida contacto, friccion ni movimiento del bloque irregular.</td><td>Testcases oficiales DualSPHysics y benchmarks SPHERIC de dam-break.</td></tr>
          <tr><td>Sanity de contacto</td><td>El bloque no supera el umbral por apoyo inicial, penetracion o contacto numerico sin impacto hidraulico local.</td><td>No valida el movimiento bajo tsunami ni coeficientes de friccion reales.</td><td>Acoplamiento DualSPHysics-Chrono y documentacion de contacto/cuerpos rigidos.</td></tr>
          <tr><td>Comparacion analitica</td><td>Los casos SPH no contradicen un balance fisico de arrastre, peso, pendiente y friccion a nivel de orden de magnitud.</td><td>No reemplaza SPH-Chrono ni predice exactamente desplazamiento/rotacion.</td><td>Nott/Nandasena para bloques costeros, experimentos de Bressan, datos moved/unmoved de Iwai & Goto y advertencias de Cox et al.</td></tr>
        </tbody>
      </table>
    </div>
    <div class="source-grid">
      <article>
        <h3>SPH y benchmark hidraulico</h3>
        <p>Los <a href="https://github.com/DualSPHysics/DualSPHysics/wiki/7.-Testcases">testcases oficiales de DualSPHysics</a> y los <a href="https://www.spheric-sph.org/validation-tests">benchmarks SPHERIC</a> justifican usar casos dam-break como verificacion hidraulica del solver y del postproceso. En esta pagina se usa para validar el entorno, no el bloque.</p>
      </article>
      <article>
        <h3>Convergencia numerica</h3>
        <p>El marco clasico de refinamiento se toma de Richardson/Roache-GCI, resumido por el tutorial de <a href="https://www.grc.nasa.gov/www/wind/valid/tutorial/spatconv.html?force_isolation=true">NASA WIND</a>. En SPH se adapta usando <code>dp</code> como escala de resolucion y evaluando variables continuas antes de hablar de estabilidad.</p>
      </article>
      <article>
        <h3>Contacto y cuerpo rigido</h3>
        <p>DualSPHysics documenta la <a href="https://github.com/DualSPHysics/DualSPHysics/wiki/3.-SPH-formulation">integracion con Project Chrono</a> para cuerpos rigidos y contacto. Por eso el chequeo correcto no es otro dam-break, sino comprobar que el bloque no se desplaza por una condicion inicial defectuosa.</p>
      </article>
      <article>
        <h3>Bloques costeros</h3>
        <p><a href="https://research.uaeu.ac.ae/en/publications/reassessment-of-hydrodynamic-equations-minimum-flow-velocity-to-i/">Nandasena, Paris & Tanaka</a> plantean balances de fuerzas para inicio de movimiento; <a href="https://pearl.plymouth.ac.uk/secam-research/1746">Bressan et al.</a> muestran experimentalmente la influencia de profundidad, velocidad, peso, forma y orientacion; <a href="https://www.nature.com/articles/s41598-021-92917-2">Iwai & Goto</a> refuerzan la importancia de casos movidos/no movidos; <a href="https://www.frontiersin.org/articles/10.3389/fmars.2020.00004/full">Cox et al.</a> advierten que esos balances no deben venderse como validacion absoluta. Por eso aqui se usan como coherencia fisica, no como prueba final.</p>
      </article>
    </div>
    <p class="note"><strong>Frase defendible:</strong> el modelo fue verificado numericamente por resolucion, contrastado con un benchmark hidraulico externo, revisado con un sanity de contacto y comparado con balances analiticos. No queda validado experimentalmente para este bloque especifico; la frontera final debe reportarse condicionada a <code>dp=0.003 m</code>, geometria fija, criterio <code>displacement_only</code> y parametros de contacto usados.</p>
  </section>

  <section>
    <h2>7. Términos usados</h2>
    <dl class="terms">
      <div><dt>dp</dt><dd>Espaciamiento inicial entre partículas SPH. Menor <code>dp</code> implica mayor resolución y mayor costo computacional.</dd></div>
      <div><dt>Resolución SPH</dt><dd>Nivel de detalle espacial dado por el tamaño/separación de partículas, no por una malla fija.</dd></div>
      <div><dt>μ</dt><dd>Coeficiente de fricción bloque-suelo usado para explorar el inicio de movimiento.</dd></div>
      <div><dt>d_eq</dt><dd>Diámetro equivalente del bloque, usado para normalizar desplazamientos.</dd></div>
      <div><dt>Umbral de movimiento</dt><dd>Condición operacional <code>D_max &gt; 5% d_eq</code>.</dd></div>
      <div><dt>Frontera</dt><dd>Intervalo de valores de <code>μ</code> donde cambia la respuesta estable/falla para una resolución y condición física dadas.</dd></div>
      <div><dt>Rotación observada</dt><dd>Variable física que se reporta para interpretar el comportamiento del bloque; no decide sola la clase de movimiento.</dd></div>
    </dl>
  </section>
</main>
{LIGHTBOX}
</body>
</html>
"""
    (OUT / "index.html").write_text(html, encoding="utf-8")


def write_css() -> None:
    css = """
:root {
  --ink: #17202a;
  --muted: #536171;
  --line: #d8dee8;
  --bg: #f4f6f9;
  --paper: #ffffff;
  --red: #b73b3b;
  --green: #2f7d4f;
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
  width: min(1120px, calc(100% - 32px));
  margin: 0 auto;
  padding: 22px 0 48px;
}
.top {
  display: block;
  border-bottom: 1px solid var(--line);
  padding-bottom: 14px;
  margin-bottom: 12px;
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
  font-size: clamp(28px, 3.4vw, 38px);
  line-height: 1.08;
  max-width: 780px;
}
h2 {
  font-size: 22px;
  margin: 0 0 12px;
}
p { margin: 0 0 12px; }
section {
  background: var(--paper);
  border: 1px solid var(--line);
  border-radius: 4px;
  padding: 20px;
  margin: 18px 0;
}
.key-strip {
  background: #fbfcfe;
  border: 1px solid var(--line);
  padding: 10px 14px;
  border-radius: 4px;
  margin: 0 0 16px;
}
.key-strip {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 0;
}
.key-strip div {
  display: grid;
  gap: 2px;
  border-bottom: 0;
  border-right: 1px solid var(--line);
  padding: 2px 14px;
}
.key-strip div:first-child { padding-left: 0; }
.key-strip div:last-child { border-right: 0; padding-right: 0; }
dt { font-weight: 700; color: var(--ink); }
dd { margin: 0; color: var(--muted); }
.grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 18px;
}
.figure-stack {
  display: grid;
  grid-template-columns: minmax(0, 1fr);
  gap: 18px;
  justify-items: center;
}
.figure-stack figure {
  width: min(1040px, 100%);
}
figure {
  margin: 16px 0 6px;
  border: 1px solid var(--line);
  background: white;
  padding: 10px;
  border-radius: 4px;
}
figure img {
  display: block;
  width: 100%;
  height: auto;
  cursor: zoom-in;
}
figcaption {
  color: var(--muted);
  font-size: 13px;
  margin-top: 8px;
}
.note {
  border-left: 4px solid #aab4c0;
  background: #f7f9fc;
  padding: 10px 12px;
  margin-top: 14px;
}
.callout {
  background: #f8fafc;
  border: 1px solid var(--line);
  border-left: 4px solid #315f8f;
  padding: 12px 14px;
  margin: 14px 0 18px;
}
.callout h3 {
  margin: 0 0 6px;
  font-size: 16px;
}
.callout p {
  margin: 6px 0;
}
.read-guide {
  margin-top: 10px;
  border-top: 1px solid var(--line);
  padding-top: 10px;
  font-size: 13px;
  color: var(--muted);
}
.read-guide ul {
  margin: 6px 0 0 18px;
  padding: 0;
}
.read-guide li { margin: 4px 0; }
.table-wrap { overflow-x: auto; border: 1px solid var(--line); }
.compact-table { max-width: 920px; }
table {
  width: 100%;
  border-collapse: collapse;
  font-size: 13px;
}
th, td {
  border-bottom: 1px solid var(--line);
  padding: 8px 9px;
  text-align: left;
}
th { background: #eef2f6; }
.compact-table th { width: 270px; white-space: nowrap; }
.compact-table td { color: var(--muted); }
.pill {
  display: inline-block;
  border-radius: 3px;
  padding: 2px 6px;
  font-weight: 700;
  font-size: 12px;
}
.pill.fail { color: #7c1f1f; background: #f8e6e6; }
.pill.stable { color: #1f5a39; background: #e5f2ea; }
.source-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 12px;
  margin: 16px 0;
}
.source-grid article {
  border: 1px solid var(--line);
  background: #f8fafc;
  padding: 12px 14px;
}
.source-grid h3 {
  margin: 0 0 6px;
  font-size: 15px;
}
.source-grid p {
  margin: 0;
  font-size: 14px;
}
a {
  color: #255f91;
  text-decoration-thickness: 1px;
  text-underline-offset: 2px;
}
.button-link {
  display: inline-block;
  background: #255f91;
  color: white;
  text-decoration: none;
  padding: 8px 12px;
  border-radius: 4px;
  font-weight: 700;
}
.terms {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 12px 22px;
  margin: 0;
}
.terms div {
  border-top: 1px solid var(--line);
  padding-top: 10px;
}
code {
  background: #eef2f6;
  padding: 1px 4px;
  border-radius: 3px;
}
.lightbox {
  position: fixed;
  inset: 0;
  display: none;
  align-items: center;
  justify-content: center;
  background: rgba(8, 12, 18, .88);
  z-index: 1000;
  padding: 24px;
}
.lightbox.open { display: flex; flex-direction: column; }
.lightbox img {
  max-width: min(96vw, 1500px);
  max-height: 86vh;
  background: white;
  border-radius: 4px;
  object-fit: contain;
}
.lightbox p {
  color: white;
  max-width: min(96vw, 1100px);
  margin: 12px 0 0;
  font-size: 14px;
}
.lightbox-close {
  position: fixed;
  top: 12px;
  right: 18px;
  width: 42px;
  height: 42px;
  border: 1px solid rgba(255,255,255,.45);
  background: rgba(255,255,255,.12);
  color: white;
  border-radius: 4px;
  font-size: 30px;
  line-height: 1;
  cursor: pointer;
}
@media (max-width: 860px) {
  .grid, .source-grid, .terms, .key-strip { grid-template-columns: 1fr; }
  .key-strip div {
    border-right: 0;
    border-bottom: 1px solid var(--line);
    padding: 8px 0;
  }
  .key-strip div:last-child { border-bottom: 0; }
  section { padding: 16px; }
}
"""
    (OUT / "styles.css").write_text(css, encoding="utf-8")


def write_data(
    summary: pd.DataFrame,
    frontier: pd.DataFrame,
    prod: pd.DataFrame,
    max_diff: pd.DataFrame,
    temporal_errors: pd.DataFrame,
) -> None:
    summary.to_csv(DATA / "continuous_convergence_summary.csv", index=False)
    pd.DataFrame(CONVERGENCE_CASE_SPEC, columns=["parametro", "valor"]).to_csv(
        DATA / "convergence_case_physical_setup.csv", index=False
    )
    table = summary.copy()
    table["disp_mm"] = table["max_displacement_m"] * 1000.0
    table["disp_pct_deq"] = table["max_displacement_m"] / D_EQ * 100.0
    table.to_csv(DATA / "convergence_case_table.csv", index=False)
    max_diff.to_csv(DATA / "convergence_max_differences_vs_dp0002.csv", index=False)
    temporal_errors.to_csv(DATA / "convergence_temporal_errors_vs_dp0002.csv", index=False)
    frontier.to_csv(DATA / "master_convergence_frontier.csv", index=False)
    if not prod.empty:
        prod.to_csv(DATA / "productive_lots_combined.csv", index=False)
    else:
        for stale in [
            DATA / "productive_lots_combined.csv",
            DATA / "master_production_story.csv",
            DATA / "figure_index.csv",
            DATA / "FIGURE_INDEX.md",
        ]:
            stale.unlink(missing_ok=True)


def main() -> None:
    init()
    summary = read_csv(RESULTS / "conv3_f05_full.csv", sep=";")
    frontier = load_frontier()
    prod = pd.DataFrame()
    max_diff = max_difference_table(summary)
    temporal_errors = temporal_error_table()
    plot_00_setup_layout()
    plot_00_method_flow()
    plot_01_defensible_variables(max_diff, temporal_errors)
    plot_02_principal_trends(max_diff)
    plot_03_temporal_curves_fine_set()
    plot_04_sensitive_outputs(max_diff, temporal_errors)
    plot_05_cost_vs_dp(summary)
    plot_06_frontier_after_resolution(frontier)
    plot_07_resolution_sensitivity(frontier)
    copy_verification_assets()
    write_data(summary, frontier, prod, max_diff, temporal_errors)
    write_css()
    write_page(prod, summary)
    print(f"Web generated: {OUT / 'index.html'}")


if __name__ == "__main__":
    main()
