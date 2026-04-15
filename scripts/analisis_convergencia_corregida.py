"""
analisis_convergencia_corregida.py - Figuras para la historia corregida de convergencia.

Genera un paquete de figuras orientado a reunion/presentacion usando:
- scouts corregidos a dp=0.004 (scout_fix2_* y scout_fix3_*)
- convergencias corregidas conv_fix_f0700_full y conv_fix_f0710_full
- temporales de esas convergencias cuando existan

Soporta datos parciales: si mu=0.710 aun no tiene dp=0.002, igual grafica lo disponible
y lo deja explicitado en el resumen.
"""

from __future__ import annotations

import re
from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt


PROJECT = Path(__file__).resolve().parent.parent
RESULTS = PROJECT / "data" / "results"
FIG = PROJECT / "data" / "figures" / "corrected_story"
FIG.mkdir(parents=True, exist_ok=True)

DEQ_M = 0.100421
DISP_THRESHOLD_M = 0.05 * DEQ_M
DISP_THRESHOLD_MM = DISP_THRESHOLD_M * 1000.0
ROT_THRESHOLD_DEG = 5.0

MU_COLORS = {
    0.700: "#1f77b4",
    0.710: "#d62728",
}
DP_COLORS = {
    0.004: "#2ca02c",
    0.003: "#ff7f0e",
    0.002: "#9467bd",
}


def parse_mu_from_name(name: str) -> float | None:
    match = re.search(r"_f(\d+)(?:r)?_dp", name)
    if not match:
        return None
    digits = match.group(1)
    return int(digits) / (10 ** (len(digits) - 1))


def scout_generation_rank(name: str) -> int:
    if name.startswith("scout_fix3_"):
        return 3
    if name.startswith("scout_fix2_"):
        return 2
    if name.startswith("scout_fix_"):
        return 1
    return 0


def classify_joint(disp_m: float, rot_deg: float | None = None) -> str:
    rot_deg = np.nan if rot_deg is None else rot_deg
    if disp_m > DISP_THRESHOLD_M:
        return "FALLO"
    if pd.notna(rot_deg) and rot_deg > ROT_THRESHOLD_DEG:
        return "FALLO"
    return "ESTABLE"


def load_scouts() -> pd.DataFrame:
    rows: list[dict] = []
    for path in sorted(RESULTS.glob("scout_fix*_dp0004.csv")):
        try:
            df = pd.read_csv(path, sep=";")
        except Exception:
            continue
        if df.empty:
            continue
        row = df.iloc[0].to_dict()
        mu = parse_mu_from_name(path.name)
        rows.append(
            {
                "file": path.name,
                "mu": mu,
                "generation_rank": scout_generation_rank(path.name),
                "repeat": "r" in path.stem,
                "status": row.get("status"),
                "dp": row.get("dp"),
                "disp_m": row.get("max_displacement_m"),
                "disp_mm": row.get("max_displacement_m", np.nan) * 1000.0,
                "rot_deg": row.get("max_rotation_deg"),
                "vel_ms": row.get("max_velocity_ms"),
                "sph_N": row.get("max_sph_force_N"),
                "time_min": row.get("tiempo_min"),
            }
        )
    out = pd.DataFrame(rows)
    if out.empty:
        raise FileNotFoundError("No se encontraron scouts corregidos en data/results.")
    latest_rank = out.groupby("mu")["generation_rank"].transform("max")
    out = out[out["generation_rank"] == latest_rank].copy()
    out = out.sort_values(["mu", "repeat", "file"]).reset_index(drop=True)
    out["class_joint"] = out.apply(
        lambda r: classify_joint(r["disp_m"], r["rot_deg"]), axis=1
    )
    return out


def load_conv(prefix: str, mu: float) -> pd.DataFrame:
    path = RESULTS / f"{prefix}.csv"
    if not path.exists():
        return pd.DataFrame()
    df = pd.read_csv(path, sep=";")
    if df.empty:
        return df
    df = df[df["status"] == "OK"].copy()
    df["mu"] = mu
    df["disp_mm"] = df["max_displacement_m"] * 1000.0
    df["class_joint"] = df.apply(
        lambda r: classify_joint(r["max_displacement_m"], r["max_rotation_deg"]), axis=1
    )
    return df.sort_values("dp", ascending=False).reset_index(drop=True)


def load_exchange_series(prefix: str, dp: float) -> pd.DataFrame | None:
    case_name = f"{prefix}_dp{str(dp).replace('.', '')}"
    path = RESULTS / f"{prefix}_temporal" / f"{case_name}_exchange.csv"
    if not path.exists():
        return None
    ex = pd.read_csv(path, sep=";")
    rename = {
        "time [s]": "t",
        "fvel.x [m/s]": "vx",
        "fvel.y [m/s]": "vy",
        "fvel.z [m/s]": "vz",
        "fcenter.x [m]": "cx",
        "fcenter.y [m]": "cy",
        "fcenter.z [m]": "cz",
        "fomega.x [rad/s]": "wx",
        "fomega.y [rad/s]": "wy",
        "fomega.z [rad/s]": "wz",
    }
    ex = ex.rename(columns=rename)
    cx0, cy0, cz0 = ex["cx"].iloc[0], ex["cy"].iloc[0], ex["cz"].iloc[0]
    ex["disp_mm"] = (
        np.sqrt((ex["cx"] - cx0) ** 2 + (ex["cy"] - cy0) ** 2 + (ex["cz"] - cz0) ** 2)
        * 1000.0
    )
    ex["vxy"] = np.sqrt(ex["vx"] ** 2 + ex["vy"] ** 2)
    ex["omega_mag"] = np.sqrt(ex["wx"] ** 2 + ex["wy"] ** 2 + ex["wz"] ** 2)
    dt = ex["t"].diff().fillna(0.0)
    ex["rot_cumul_deg"] = np.degrees(np.cumsum(ex["omega_mag"] * dt))
    return ex


def plot_scout_overview(scouts: pd.DataFrame) -> Path:
    fig, ax = plt.subplots(figsize=(10, 5.5))

    unique = scouts.drop_duplicates(subset=["mu"], keep="last").sort_values("mu")
    ax.plot(unique["mu"], unique["disp_mm"], color="#666666", linewidth=1.2, alpha=0.7)

    stable = scouts[scouts["class_joint"] == "ESTABLE"]
    fail = scouts[scouts["class_joint"] == "FALLO"]
    ax.scatter(stable["mu"], stable["disp_mm"], color="#2ca02c", s=70, label="ESTABLE")
    ax.scatter(fail["mu"], fail["disp_mm"], color="#d62728", s=70, label="FALLO")

    repeats = scouts[scouts["repeat"]]
    if not repeats.empty:
        ax.scatter(
            repeats["mu"],
            repeats["disp_mm"],
            facecolors="none",
            edgecolors="black",
            s=130,
            linewidth=1.2,
            label="repeat",
        )

    ax.axhline(DISP_THRESHOLD_MM, color="black", linestyle="--", linewidth=1.0,
               label=f"umbral = {DISP_THRESHOLD_MM:.3f} mm")
    ax.set_xlabel("Coeficiente de friccion, mu")
    ax.set_ylabel("Desplazamiento maximo [mm]")
    ax.set_title("Scouting corregido: frontera de friccion a dp = 0.004")
    ax.grid(True, alpha=0.25)
    ax.legend()

    out = FIG / "corrected_scout_overview.png"
    fig.savefig(out, dpi=180, bbox_inches="tight")
    plt.close(fig)
    return out


def plot_scout_zoom(scouts: pd.DataFrame) -> Path:
    zoom = scouts[(scouts["mu"] >= 0.68) & (scouts["mu"] <= 0.72)].copy()
    fig, ax = plt.subplots(figsize=(10, 5.5))

    ax.axhspan(0, DISP_THRESHOLD_MM, color="#2ca02c", alpha=0.08)
    ax.axhspan(DISP_THRESHOLD_MM, max(zoom["disp_mm"].max() * 1.1, 8), color="#d62728", alpha=0.06)

    for _, row in zoom.iterrows():
        color = "#2ca02c" if row["class_joint"] == "ESTABLE" else "#d62728"
        marker = "o" if not row["repeat"] else "s"
        ax.scatter(row["mu"], row["disp_mm"], color=color, s=85, marker=marker, zorder=3)
        ax.text(row["mu"], row["disp_mm"] + 0.15, f"{row['mu']:.3f}\n{row['disp_mm']:.2f}",
                fontsize=8, ha="center")

    ax.axhline(DISP_THRESHOLD_MM, color="black", linestyle="--", linewidth=1.0)
    ax.set_xlabel("Coeficiente de friccion, mu")
    ax.set_ylabel("Desplazamiento maximo [mm]")
    ax.set_title("Zoom de la banda irregular alrededor del umbral")
    ax.set_xlim(0.679, 0.721)
    ax.grid(True, alpha=0.25)

    out = FIG / "corrected_scout_zoom.png"
    fig.savefig(out, dpi=180, bbox_inches="tight")
    plt.close(fig)
    return out


def plot_convergence_metrics(conv700: pd.DataFrame, conv710: pd.DataFrame) -> Path:
    fig, axes = plt.subplots(2, 2, figsize=(12, 9))
    metrics = [
        ("disp_mm", "Desplazamiento maximo [mm]"),
        ("max_velocity_ms", "Velocidad maxima [m/s]"),
        ("max_sph_force_N", "Fuerza SPH maxima [N]"),
        ("max_rotation_deg", "Rotacion acumulada [deg]"),
    ]

    for ax, (col, ylabel) in zip(axes.ravel(), metrics):
        for mu, df in [(0.700, conv700), (0.710, conv710)]:
            if df.empty:
                continue
            ax.plot(df["dp"], df[col], "o-", color=MU_COLORS[mu], label=f"mu={mu:.3f}")
            for _, row in df.iterrows():
                ax.text(row["dp"], row[col], row["class_joint"], fontsize=7,
                        color=MU_COLORS[mu], ha="left", va="bottom")

        if col == "disp_mm":
            ax.axhline(DISP_THRESHOLD_MM, color="black", linestyle="--", linewidth=1.0)
        if col == "max_rotation_deg":
            ax.axhline(ROT_THRESHOLD_DEG, color="black", linestyle="--", linewidth=1.0)

        ax.set_xlabel("dp [m]")
        ax.set_ylabel(ylabel)
        ax.set_title(ylabel)
        ax.invert_xaxis()
        ax.grid(True, alpha=0.25)
        ax.legend(fontsize=8)

    fig.suptitle("Convergencias corregidas en los dos casos marginales", fontsize=14, fontweight="bold")
    out = FIG / "corrected_convergence_metrics.png"
    fig.savefig(out, dpi=180, bbox_inches="tight")
    plt.close(fig)
    return out


def plot_temporal(conv700: pd.DataFrame, conv710: pd.DataFrame) -> Path | None:
    fig, axes = plt.subplots(2, 2, figsize=(12, 8), sharex="col")
    available = False

    for mu, prefix, row_idx in [
        (0.700, "conv_fix_f0700_full", 0),
        (0.710, "conv_fix_f0710_full", 1),
    ]:
        for dp in [0.004, 0.003, 0.002]:
            ex = load_exchange_series(prefix, dp)
            if ex is None:
                continue
            available = True
            color = DP_COLORS[dp]
            axes[row_idx, 0].plot(ex["t"], ex["disp_mm"], color=color, label=f"dp={dp:.3f}")
            axes[row_idx, 1].plot(ex["t"], ex["rot_cumul_deg"], color=color, label=f"dp={dp:.3f}")

        axes[row_idx, 0].axhline(DISP_THRESHOLD_MM, color="black", linestyle="--", linewidth=0.9)
        axes[row_idx, 0].set_ylabel(f"mu={mu:.3f}\nDisp [mm]")
        axes[row_idx, 1].set_ylabel(f"mu={mu:.3f}\nRot acum [deg]")
        axes[row_idx, 0].grid(True, alpha=0.25)
        axes[row_idx, 1].grid(True, alpha=0.25)
        axes[row_idx, 0].legend(fontsize=8)
        axes[row_idx, 1].legend(fontsize=8)

    axes[1, 0].set_xlabel("Tiempo [s]")
    axes[1, 1].set_xlabel("Tiempo [s]")
    axes[0, 0].set_title("Desplazamiento temporal")
    axes[0, 1].set_title("Rotacion acumulada temporal")

    if not available:
        plt.close(fig)
        return None

    out = FIG / "corrected_temporal_fine.png"
    fig.savefig(out, dpi=180, bbox_inches="tight")
    plt.close(fig)
    return out


def write_summary(scouts: pd.DataFrame, conv700: pd.DataFrame, conv710: pd.DataFrame) -> Path:
    summary = []
    summary.append("# Historia corregida de convergencia\n")
    summary.append(f"- Umbral exacto: {DISP_THRESHOLD_MM:.3f} mm (0.05*d_eq)\n")
    summary.append("- Geometria corregida: bloque alineado con la pendiente y apoyo exacto.\n")
    summary.append("- Scouts usados: solo la generacion corregida mas reciente por mu (fix3 > fix2 > fix).\n")

    summary.append("\n## Scouts corregidos\n")
    for _, row in scouts.sort_values(["mu", "repeat"]).iterrows():
        tag = " repeat" if row["repeat"] else ""
        summary.append(
            f"- mu={row['mu']:.3f}{tag}: disp={row['disp_mm']:.3f} mm, "
            f"rot={row['rot_deg']:.2f} deg, class={row['class_joint']}\n"
        )

    def conv_block(title: str, df: pd.DataFrame) -> None:
        summary.append(f"\n## {title}\n")
        if df.empty:
            summary.append("- Sin datos.\n")
            return
        for _, row in df.sort_values("dp", ascending=False).iterrows():
            summary.append(
                f"- dp={row['dp']:.3f}: disp={row['disp_mm']:.3f} mm, "
                f"rot={row['max_rotation_deg']:.2f} deg, vel={row['max_velocity_ms']:.4f} m/s, "
                f"Fsph={row['max_sph_force_N']:.3f} N, class={row['class_joint']}\n"
            )

    conv_block("Convergencia corregida mu=0.700", conv700)
    conv_block("Convergencia corregida mu=0.710", conv710)
    if len(conv710) < 3:
        summary.append(
            f"- Nota: mu=0.710 sigue parcial; solo hay {len(conv710)} niveles dp consolidados.\n"
        )

    summary.append("\n## Figuras generadas\n")
    for name in [
        "corrected_scout_overview.png",
        "corrected_scout_zoom.png",
        "corrected_convergence_metrics.png",
        "corrected_temporal_fine.png",
    ]:
        if (FIG / name).exists():
            summary.append(f"- {name}\n")

    out = FIG / "corrected_story_summary.md"
    out.write_text("".join(summary), encoding="utf-8")
    return out


def main() -> None:
    scouts = load_scouts()
    conv700 = load_conv("conv_fix_f0700_full", 0.700)
    conv710 = load_conv("conv_fix_f0710_full", 0.710)

    generated = [
        plot_scout_overview(scouts),
        plot_scout_zoom(scouts),
        plot_convergence_metrics(conv700, conv710),
    ]
    temporal = plot_temporal(conv700, conv710)
    if temporal:
        generated.append(temporal)
    generated.append(write_summary(scouts, conv700, conv710))

    print("=" * 70)
    print("Figuras historia corregida")
    print("=" * 70)
    for path in generated:
        print(path)


if __name__ == "__main__":
    main()
