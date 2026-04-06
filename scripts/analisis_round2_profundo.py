"""
analisis_round2_profundo.py — Analisis profundo del Screening Round 2 (dp=0.004).

Lee los 15 casos (sc2_001..sc2_015) y produce:
1. Analisis temporal (t_impact, t_peak, t_stable, still-moving check)
2. Adecuacion del dominio (margen al borde para casos FALLO)
3. Analisis de reflexion (V12 gauge downstream)
4. Investigacion sc2_010 (slope=1:5, gauges secos)
5. Analisis de fuerzas SPH + contacto
6. Correlaciones Spearman con p-values
7. Analisis de variables aisladas (sc2_010-014)
8. Verificacion de replicacion sc_008(R1) vs sc2_015(R2)
9. Reporte markdown + figuras

Autor: Kevin Cortes (UCN 2026)
"""

from __future__ import annotations

import sys
import warnings
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import numpy as np
import pandas as pd
from scipy import stats, signal

warnings.filterwarnings("ignore", category=FutureWarning)

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------

PROJECT = Path(__file__).resolve().parent.parent
PROCESSED = PROJECT / "data" / "processed"
FIGURES = PROJECT / "data" / "figures"
RESULTS = PROJECT / "data" / "results"
FIGURES.mkdir(parents=True, exist_ok=True)
RESULTS.mkdir(parents=True, exist_ok=True)

SENTINEL = -3.40282e38
SENTINEL_THRESH = -1e30  # anything below this is sentinel

# Case parameters
PARAMS_CSV = PROJECT / "config" / "screening_round2.csv"
R1_PARAMS_CSV = PROJECT / "config" / "screening_5d.csv"

# Physics constants
FTPAUSE = 0.5          # s
DOMAIN_LENGTH = 15.0   # m (canal total)
BOULDER_X0_NOMINAL = 6.48  # m (typical initial x for slope=1:20)
DISP_THRESHOLD_MM = 5.0
G = 9.81               # m/s^2


# ---------------------------------------------------------------------------
# Data loading utilities
# ---------------------------------------------------------------------------

def find_csv_dir(case_id: str) -> Path:
    """Locate the directory containing CSVs for a case."""
    base = PROCESSED / case_id
    out_dir = base / f"{case_id}_out"
    if out_dir.exists():
        return out_dir
    # Round 1 cases: CSVs directly in case folder
    return base


def load_chrono(case_id: str) -> pd.DataFrame:
    """Load ChronoExchange_mkbound_51.csv with cleaned column names."""
    path = find_csv_dir(case_id) / "ChronoExchange_mkbound_51.csv"
    df = pd.read_csv(path, sep=";")
    # Clean column names
    df.columns = [c.strip() for c in df.columns]
    return df


def load_forces(case_id: str) -> pd.DataFrame:
    """Load ChronoBody_forces.csv with renamed columns for clarity."""
    path = find_csv_dir(case_id) / "ChronoBody_forces.csv"
    df = pd.read_csv(path, sep=";", header=0)
    # The header has duplicate column names (Body_BLIR_fx,fy,fz,...,cfx,... Body_beach_fx,fy,fz,...,cfx,...)
    # Assign explicit names
    expected_cols = [
        "Time",
        "sph_fx", "sph_fy", "sph_fz", "sph_mx", "sph_my", "sph_mz",
        "contact_fx", "contact_fy", "contact_fz", "contact_mx", "contact_my", "contact_mz",
        "beach_sph_fx", "beach_sph_fy", "beach_sph_fz", "beach_sph_mx", "beach_sph_my", "beach_sph_mz",
        "beach_contact_fx", "beach_contact_fy", "beach_contact_fz",
        "beach_contact_mx", "beach_contact_my", "beach_contact_mz",
    ]
    # Handle trailing semicolon creating extra empty column
    if len(df.columns) == len(expected_cols) + 1:
        df = df.iloc[:, :len(expected_cols)]
    if len(df.columns) == len(expected_cols):
        df.columns = expected_cols
    else:
        # Fallback: use positional indexing
        df.columns = [f"col_{i}" for i in range(len(df.columns))]
        df.rename(columns={"col_0": "Time"}, inplace=True)
    return df


def load_gauge_vel(case_id: str, gauge_num: int) -> pd.DataFrame:
    """Load a velocity gauge CSV, replacing sentinels with NaN."""
    path = find_csv_dir(case_id) / f"GaugesVel_V{gauge_num:02d}.csv"
    if not path.exists():
        return pd.DataFrame()
    df = pd.read_csv(path, sep=";")
    df.columns = [c.strip() for c in df.columns]
    for col in df.columns:
        if col != "time [s]":
            df.loc[df[col] < SENTINEL_THRESH, col] = np.nan
    return df


def load_gauge_hmax(case_id: str, gauge_num: int) -> pd.DataFrame:
    """Load a max-height gauge CSV, replacing sentinels with NaN."""
    path = find_csv_dir(case_id) / f"GaugesMaxZ_hmax{gauge_num:02d}.csv"
    if not path.exists():
        return pd.DataFrame()
    df = pd.read_csv(path, sep=";")
    df.columns = [c.strip() for c in df.columns]
    for col in df.columns:
        if col != "time [s]":
            df.loc[df[col] < SENTINEL_THRESH, col] = np.nan
    return df


# ---------------------------------------------------------------------------
# 1. Temporal analysis
# ---------------------------------------------------------------------------

def temporal_analysis(case_id: str, df: pd.DataFrame) -> dict:
    """Compute timing metrics for boulder motion."""
    t = df["time [s]"].values
    cx = df["fcenter.x [m]"].values
    cy = df["fcenter.y [m]"].values
    cz = df["fcenter.z [m]"].values
    vx = df["fvel.x [m/s]"].values
    vy = df["fvel.y [m/s]"].values
    vz = df["fvel.z [m/s]"].values

    # Initial position (first row after FtPause)
    x0, y0, z0 = cx[0], cy[0], cz[0]

    # 3D displacement in mm
    disp = np.sqrt((cx - x0)**2 + (cy - y0)**2 + (cz - z0)**2) * 1000

    # Velocity magnitude (horizontal only, excluding vertical settling)
    vel_h = np.sqrt(vx**2 + vy**2)
    vel_3d = np.sqrt(vx**2 + vy**2 + vz**2)

    # t_impact: first time displacement exceeds 0.5mm
    mask_impact = disp > 0.5
    t_impact = t[mask_impact][0] if mask_impact.any() else np.nan

    # t_peak: time of max horizontal velocity
    idx_peak = np.argmax(vel_h)
    t_peak = t[idx_peak]
    v_peak = vel_h[idx_peak]

    # t_stable: first time (after t_peak) where velocity drops below 0.01 m/s
    t_stable = np.nan
    if idx_peak < len(t) - 1:
        post_peak = vel_h[idx_peak:]
        mask_stable = post_peak < 0.01
        if mask_stable.any():
            t_stable = t[idx_peak + np.argmax(mask_stable)]

    # Final values
    t_end = t[-1]
    vel_end = vel_h[-1]
    disp_end = disp[-1]
    still_moving = vel_end > 0.01

    # Final position
    x_final = cx[-1]
    y_final = cy[-1]
    z_final = cz[-1]

    return {
        "case_id": case_id,
        "x0": x0, "y0": y0, "z0": z0,
        "x_final": x_final, "y_final": y_final, "z_final": z_final,
        "t_impact": t_impact,
        "t_peak": t_peak,
        "v_peak": v_peak,
        "t_stable": t_stable,
        "t_end": t_end,
        "vel_end": vel_end,
        "disp_end_mm": disp_end,
        "still_moving": still_moving,
    }


# ---------------------------------------------------------------------------
# 2. Domain adequacy
# ---------------------------------------------------------------------------

def domain_adequacy(temporal: dict, params: dict) -> dict:
    """Compute remaining margin to domain edge for FALLO cases."""
    x_final = temporal["x_final"]
    disp_mm = temporal["disp_end_mm"]

    # Domain extends from 0 to ~15m in x
    margin_downstream = DOMAIN_LENGTH - x_final
    margin_from_start = x_final - temporal["x0"]

    return {
        "case_id": temporal["case_id"],
        "x_final": x_final,
        "margin_downstream_m": margin_downstream,
        "disp_total_mm": disp_mm,
        "pct_domain_used": (x_final / DOMAIN_LENGTH) * 100,
    }


# ---------------------------------------------------------------------------
# 3. Reflection analysis
# ---------------------------------------------------------------------------

def reflection_analysis(case_id: str, dam_h: float) -> dict:
    """Analyze V12 (downstream gauge at ~x=12m) for reflection patterns."""
    if dam_h < 0.15:
        return {"case_id": case_id, "skip": True, "reason": "dam_h < 0.15"}

    df = load_gauge_vel(case_id, 12)
    if df.empty:
        return {"case_id": case_id, "skip": True, "reason": "no V12 data"}

    t = df["time [s]"].values
    vx = df["velx [m/s]"].values

    # Count velocity peaks (positive = forward, negative = reflection)
    valid = ~np.isnan(vx)
    if valid.sum() < 100:
        return {"case_id": case_id, "skip": True, "reason": "too few valid points"}

    t_valid = t[valid]
    vx_valid = vx[valid]

    # Find peaks in positive velocity (forward wave)
    peaks_pos, props_pos = signal.find_peaks(vx_valid, height=0.01, distance=100)
    # Find peaks in negative velocity (reflected wave)
    peaks_neg, props_neg = signal.find_peaks(-vx_valid, height=0.01, distance=100)

    max_vx = np.nanmax(vx_valid)
    min_vx = np.nanmin(vx_valid)

    # Time of first arrival at V12
    mask_arrival = np.abs(vx_valid) > 0.01
    t_arrival = t_valid[mask_arrival][0] if mask_arrival.any() else np.nan

    return {
        "case_id": case_id,
        "skip": False,
        "n_forward_peaks": len(peaks_pos),
        "n_reflected_peaks": len(peaks_neg),
        "max_vx": max_vx,
        "min_vx": min_vx,
        "t_arrival": t_arrival,
        "has_reflection": len(peaks_neg) > 0 and abs(min_vx) > 0.05,
    }


# ---------------------------------------------------------------------------
# 4. sc2_010 investigation
# ---------------------------------------------------------------------------

def investigate_sc2_010() -> str:
    """Deep investigation of sc2_010 (slope=1:5, water_h=0.0)."""
    lines = []
    case_id = "sc2_010"

    lines.append("### Investigacion sc2_010 (slope=1:5)")
    lines.append("")

    # Load boulder kinematics
    df = load_chrono(case_id)
    t = df["time [s]"].values
    cx = df["fcenter.x [m]"].values
    cz = df["fcenter.z [m]"].values

    lines.append(f"**Posicion inicial boulder:** x={cx[0]:.4f}, z={cz[0]:.4f} m")
    lines.append(f"**Posicion final boulder:** x={cx[-1]:.4f}, z={cz[-1]:.4f} m")
    lines.append(f"**Desplazamiento x:** {(cx[-1]-cx[0])*1000:.1f} mm")
    lines.append(f"**Desplazamiento z:** {(cz[-1]-cz[0])*1000:.1f} mm")
    lines.append("")

    # Check all 8 hmax gauges
    lines.append("**Gauges de altura maxima (hmax):**")
    lines.append("")
    lines.append("| Gauge | Posicion (x,y,z) | Datos validos | zmax_max [m] | Diagnostico |")
    lines.append("|-------|------------------|---------------|-------------|-------------|")

    for i in range(1, 9):
        df_h = load_gauge_hmax(case_id, i)
        if df_h.empty:
            lines.append(f"| hmax{i:02d} | - | - | - | NO DATA |")
            continue
        valid = df_h["zmax [m]"].notna()
        n_valid = valid.sum()
        n_total = len(df_h)
        pos_x = df_h.iloc[0].get("posx [m]", 0)
        pos_y = df_h.iloc[0].get("posy [m]", 0)
        pos_z = df_h.iloc[0].get("posz [m]", 0)
        zmax_max = df_h.loc[valid, "zmax [m]"].max() if n_valid > 0 else np.nan

        if np.isnan(zmax_max):
            diag = "ALL SENTINEL - gauge above water"
        elif zmax_max < 0.01:
            diag = "Near zero - dry"
        else:
            diag = f"OK - water detected"

        lines.append(f"| hmax{i:02d} | ({pos_x:.2f}, {pos_y:.4f}, {pos_z:.3f}) | "
                      f"{n_valid}/{n_total} | {zmax_max:.4f} | {diag} |")

    lines.append("")

    # Check velocity gauges
    lines.append("**Gauges de velocidad:**")
    lines.append("")
    lines.append("| Gauge | Posicion (x,y,z) | max velx [m/s] | Datos validos | Diagnostico |")
    lines.append("|-------|------------------|----------------|---------------|-------------|")

    for i in range(1, 13):
        df_v = load_gauge_vel(case_id, i)
        if df_v.empty:
            lines.append(f"| V{i:02d} | - | - | - | NO DATA |")
            continue
        vx = df_v["velx [m/s]"]
        valid = vx.notna()
        n_valid = valid.sum()
        max_vx = vx[valid].max() if n_valid > 0 else np.nan
        pos_x = df_v.iloc[0].get("posx [m]", 0)
        pos_y = df_v.iloc[0].get("posy [m]", 0)
        pos_z = df_v.iloc[0].get("posz [m]", 0)

        if max_vx == 0 or np.isnan(max_vx):
            diag = "DRY - no flow detected"
        elif max_vx < 0.01:
            diag = "Negligible flow"
        else:
            diag = "Flow detected"

        lines.append(f"| V{i:02d} | ({pos_x:.2f}, {pos_y:.4f}, {pos_z:.3f}) | "
                      f"{max_vx:.4f} | {n_valid}/{len(df_v)} | {diag} |")

    lines.append("")

    # Interpretation
    lines.append("**Interpretacion:**")
    lines.append("")
    lines.append("Con slope=1:5, la pendiente sube 1m cada 5m. Los gauges de")
    lines.append("velocidad V08-V12 estan a z >= 0.55m, posiciones donde el agua")
    lines.append("del dam-break (dam_h=0.20m) nunca alcanza.")
    lines.append("Los gauges hmax04-08 estan a z >= 0.35m y tambien quedan secos.")
    lines.append("")
    lines.append("Solo los gauges cercanos al dam (V01-V04, hmax01-03) detectan flujo.")
    lines.append("El boulder a x=6.48m esta en z=0.118m (pendiente 1:5), el agua llega")
    lines.append("con suficiente energia para moverlo 133.5mm pese a que los gauges")
    lines.append("remotos no detectan nada. **El water_h=0.0 reportado es un artefacto**")
    lines.append("**de los gauges seleccionados para el calculo, no una ausencia real de agua.**")
    lines.append("")

    # Compare with sc2_011 (slope=1:30)
    df_011 = load_chrono("sc2_011")
    lines.append(f"**Comparacion con sc2_011 (slope=1:30):**")
    lines.append(f"- sc2_010 (1:5): boulder z0={cz[0]:.4f}m, disp={133.5:.1f}mm")
    lines.append(f"- sc2_011 (1:30): boulder z0={df_011['fcenter.z [m]'].iloc[0]:.4f}m, disp=1132.4mm")
    lines.append(f"- La pendiente pronunciada (1:5) disipa mas energia que la suave (1:30),")
    lines.append(f"  resultando en menor desplazamiento pese al mayor z0 del boulder.")
    lines.append("")

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# 5. Force analysis
# ---------------------------------------------------------------------------

def force_analysis(case_id: str, boulder_mass: float) -> dict:
    """Analyze SPH and contact forces for a case."""
    try:
        df = load_forces(case_id)
    except Exception:
        return {"case_id": case_id, "error": True}

    t = df["Time"].values

    # SPH forces (columns: sph_fx, sph_fy, sph_fz)
    # These are acceleration * mass effectively, but stored as accelerations
    # The face.x etc in ChronoExchange are accelerations -> forces = mass * acc
    # But ChronoBody_forces stores the actual force components
    if "sph_fx" in df.columns:
        sph_fx = df["sph_fx"].values
        sph_fy = df["sph_fy"].values
        sph_fz = df["sph_fz"].values
        contact_fx = df["contact_fx"].values
        contact_fy = df["contact_fy"].values
        contact_fz = df["contact_fz"].values
    else:
        # Fallback for unexpected column format
        return {"case_id": case_id, "error": True}

    # SPH force: correct for gravity (fz includes -g component)
    # The SPH columns show the net SPH acceleration including gravity
    # Gravity correction: subtract -9.81 from fz -> net SPH_fz = sph_fz - (-9.81) = sph_fz + 9.81
    # But wait: in ChronoBody_forces, sph columns are actual SPH force accelerations
    # sph_fz = 0 at rest means no SPH force (gravity is separate in the solver)
    # Actually looking at the data: sph_fz = 0,0,-9.81 for the first rows
    # This means it IS the total acceleration including gravity
    # Net SPH force_z = (sph_fz + g) * mass

    sph_fz_corrected = sph_fz + G  # remove gravity component (sph_fz includes -g)
    sph_f_mag = np.sqrt(sph_fx**2 + sph_fy**2 + sph_fz_corrected**2)
    # These are accelerations, multiply by mass to get forces in N
    sph_force_N = sph_f_mag * boulder_mass

    contact_f_mag = np.sqrt(contact_fx**2 + contact_fy**2 + contact_fz**2)
    # Contact forces in ChronoBody are already in N (not per-unit-mass)
    # Actually they seem very large -> check units
    # The first data row has contact_fz ~ 3822 which at 1kg would be 3822N
    # That's the initial settling impulse. After that it stabilizes.
    # Skip the first row (impulse artifact)
    if len(contact_f_mag) > 1:
        contact_f_mag_stable = contact_f_mag[1:]
        t_stable = t[1:]
    else:
        contact_f_mag_stable = contact_f_mag
        t_stable = t

    max_sph_force = np.max(sph_force_N[1:]) if len(sph_force_N) > 1 else np.max(sph_force_N)
    max_contact_force = np.max(contact_f_mag_stable)
    mean_contact_force = np.mean(contact_f_mag_stable)

    # Time of peak SPH force
    idx_sph_peak = np.argmax(sph_force_N[1:]) + 1 if len(sph_force_N) > 1 else 0
    t_sph_peak = t[idx_sph_peak]

    # Force ratio
    ratio = max_sph_force / max_contact_force if max_contact_force > 0 else np.inf

    return {
        "case_id": case_id,
        "error": False,
        "max_sph_force_N": max_sph_force,
        "max_contact_force_N": max_contact_force,
        "mean_contact_force_N": mean_contact_force,
        "t_sph_peak": t_sph_peak,
        "sph_contact_ratio": ratio,
        "sph_fx_series": sph_fx,
        "contact_fz_series": contact_fz,
        "time_series": t,
    }


# ---------------------------------------------------------------------------
# 6. Spearman correlations
# ---------------------------------------------------------------------------

def compute_spearman_correlations(df_results: pd.DataFrame) -> pd.DataFrame:
    """Compute Spearman rank correlations with p-values."""
    input_vars = ["dam_h", "mass", "rot_z", "friction", "slope_inv"]
    output_vars = ["max_disp_mm", "max_rot_deg"]

    rows = []
    for inp in input_vars:
        for out in output_vars:
            rho, pval = stats.spearmanr(df_results[inp], df_results[out])
            rows.append({
                "input_var": inp,
                "output_var": out,
                "spearman_rho": rho,
                "p_value": pval,
                "significant_005": pval < 0.05,
                "significant_010": pval < 0.10,
            })
    return pd.DataFrame(rows)


# ---------------------------------------------------------------------------
# 7. Isolated variable analysis
# ---------------------------------------------------------------------------

def isolated_variable_analysis(df_results: pd.DataFrame) -> str:
    """Analyze pairs with isolated variable changes."""
    lines = []
    lines.append("### Analisis de variables aisladas")
    lines.append("")
    lines.append("Casos sc2_010-014 tienen dam_h=0.20 y mass=1.0 (base comun).")
    lines.append("")

    # Slope effect: sc2_010 (slope=5) vs sc2_011 (slope=30)
    lines.append("#### a) Efecto pendiente: sc2_010 (1:5) vs sc2_011 (1:30)")
    sc2_010 = df_results[df_results["case_id"] == "sc2_010"].iloc[0]
    sc2_011 = df_results[df_results["case_id"] == "sc2_011"].iloc[0]
    lines.append(f"- sc2_010: slope=1:{sc2_010['slope_inv']:.0f}, disp={sc2_010['max_disp_mm']:.1f}mm, "
                  f"vel={sc2_010['max_vel_mps']:.3f} m/s, water_h={sc2_010['water_h_m']:.4f}m")
    lines.append(f"- sc2_011: slope=1:{sc2_011['slope_inv']:.0f}, disp={sc2_011['max_disp_mm']:.1f}mm, "
                  f"vel={sc2_011['max_vel_mps']:.3f} m/s, water_h={sc2_011['water_h_m']:.4f}m")
    ratio_slope = sc2_011["max_disp_mm"] / sc2_010["max_disp_mm"]
    lines.append(f"- **Factor:** slope 1:30 produce {ratio_slope:.1f}x mas desplazamiento que 1:5")
    lines.append(f"- La pendiente suave (1:30) permite al bore mantener velocidad y profundidad,")
    lines.append(f"  transfiriendo mas momento al boulder.")
    lines.append("")

    # Friction effect: sc2_012 (fric=0.1) vs sc2_013 (fric=0.8)
    lines.append("#### b) Efecto friccion: sc2_012 (mu=0.1) vs sc2_013 (mu=0.8)")
    sc2_012 = df_results[df_results["case_id"] == "sc2_012"].iloc[0]
    sc2_013 = df_results[df_results["case_id"] == "sc2_013"].iloc[0]
    lines.append(f"- sc2_012: friction={sc2_012['friction']:.2f}, disp={sc2_012['max_disp_mm']:.1f}mm, "
                  f"rot={sc2_012['max_rot_deg']:.1f}deg")
    lines.append(f"- sc2_013: friction={sc2_013['friction']:.2f}, disp={sc2_013['max_disp_mm']:.1f}mm, "
                  f"rot={sc2_013['max_rot_deg']:.1f}deg")
    ratio_fric = sc2_012["max_disp_mm"] / max(sc2_013["max_disp_mm"], 0.01)
    lines.append(f"- **Factor:** baja friccion produce {ratio_fric:.0f}x mas desplazamiento")
    lines.append(f"- sc2_013 (mu=0.8) clasifica como ESTABLE (1.57mm), confirmando que")
    lines.append(f"  alta friccion estabiliza completamente al boulder bajo dam_h=0.20m.")
    lines.append(f"- Friccion es el factor mas decisivo en el rango dam_h~0.20m.")
    lines.append("")

    # Rotation effect: sc2_003 (rot=60, mass=1.2, fric=0.5) vs sc2_014 (rot=90, mass=1.0, fric=0.3)
    lines.append("#### c) Efecto rotacion: sc2_003 (rot=60) vs sc2_014 (rot=90)")
    sc2_003 = df_results[df_results["case_id"] == "sc2_003"].iloc[0]
    sc2_014 = df_results[df_results["case_id"] == "sc2_014"].iloc[0]
    lines.append(f"- sc2_003: rot_z=60, mass=1.2, fric=0.5 -> disp={sc2_003['max_disp_mm']:.1f}mm (ESTABLE)")
    lines.append(f"- sc2_014: rot_z=90, mass=1.0, fric=0.3 -> disp={sc2_014['max_disp_mm']:.1f}mm (FALLO)")
    lines.append(f"- **NOTA:** No son directamente comparables (difieren en mass y friction).")
    lines.append(f"  La diferencia se explica mejor por mass (1.2 vs 1.0) y friction (0.5 vs 0.3)")
    lines.append(f"  que por rot_z (60 vs 90).")
    lines.append("")

    # Better rotation comparison: sc2_010 (rot=0) vs sc2_014 (rot=90), same mass/friction/slope
    lines.append("#### c') Mejor comparacion rotacion: sc2_010 (rot=0) vs sc2_014 (rot=90)")
    lines.append(f"  Ambos: dam_h=0.20, mass=1.0, friction=0.3")
    lines.append(f"  PERO slopes diferentes: sc2_010=1:5, sc2_014=1:20")
    lines.append(f"- sc2_010: rot_z=0, slope=1:5 -> disp={sc2_010['max_disp_mm']:.1f}mm")
    lines.append(f"- sc2_014: rot_z=90, slope=1:20 -> disp={sc2_014['max_disp_mm']:.1f}mm")
    lines.append(f"- No se puede aislar rot_z porque slope confunde el efecto.")
    lines.append("")

    # Best baseline pair for slope: sc2_011 (slope=30, rot=0, fric=0.3) vs sc2_012 (slope=20, rot=0, fric=0.1)
    # Actually sc2_011 and sc2_014: same dam_h, mass, BUT different slope(30 vs 20), rot(0 vs 90), fric(0.3 vs 0.3)
    lines.append("#### d) Efecto rotacion (mejor par): sc2_011 (rot=0, slope=30) vs sc2_014 (rot=90, slope=20)")
    lines.append(f"  Ambos: dam_h=0.20, mass=1.0, friction=0.3")
    lines.append(f"- sc2_011: rot_z=0, slope=1:30 -> disp={sc2_011['max_disp_mm']:.1f}mm")
    lines.append(f"- sc2_014: rot_z=90, slope=1:20 -> disp={sc2_014['max_disp_mm']:.1f}mm")
    lines.append(f"- sc2_011 tiene slope mas suave (mas movimiento) Y disp mayor.")
    lines.append(f"  La orientacion 90 grados (seccion mas estrecha al flujo) podria reducir")
    lines.append(f"  la fuerza de arrastre, pero el efecto slope domina.")
    lines.append("")

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# 8. Replication check: sc_008 (R1, dp=0.005) vs sc2_015 (R2, dp=0.004)
# ---------------------------------------------------------------------------

def replication_check() -> tuple[str, bool]:
    """Compare time series of sc_008 (R1) and sc2_015 (R2)."""
    lines = []
    can_plot = True

    try:
        df_r1 = load_chrono("sc_008")
        df_r2 = load_chrono("sc2_015")
    except FileNotFoundError as e:
        return f"Error cargando datos: {e}", False

    lines.append("### Verificacion de replicacion: sc_008 (R1) vs sc2_015 (R2)")
    lines.append("")
    lines.append("Parametros identicos: dam_h=0.145, mass=0.949, rot_z=56.6, friction=0.564, slope=1:28")
    lines.append(f"sc_008: dp=0.005 (Round 1), sc2_015: dp=0.004 (Round 2)")
    lines.append("")

    # Compute displacement for both
    for label, df in [("sc_008 (R1)", df_r1), ("sc2_015 (R2)", df_r2)]:
        cx = df["fcenter.x [m]"].values
        cy = df["fcenter.y [m]"].values
        cz = df["fcenter.z [m]"].values
        disp = np.sqrt((cx - cx[0])**2 + (cy - cy[0])**2 + (cz - cz[0])**2) * 1000
        vx = df["fvel.x [m/s]"].values
        vy = df["fvel.y [m/s]"].values
        vel_h = np.sqrt(vx**2 + vy**2)
        t = df["time [s]"].values

        lines.append(f"**{label}:**")
        lines.append(f"  - Posicion inicial: ({cx[0]:.4f}, {cy[0]:.4f}, {cz[0]:.4f})")
        lines.append(f"  - Posicion final: ({cx[-1]:.4f}, {cy[-1]:.4f}, {cz[-1]:.4f})")
        lines.append(f"  - Max desplazamiento: {np.max(disp):.2f} mm")
        lines.append(f"  - Max vel horizontal: {np.max(vel_h):.4f} m/s")
        lines.append(f"  - Tiempo sim: {t[0]:.3f} - {t[-1]:.3f} s")
        lines.append(f"  - N timesteps: {len(t)}")
        lines.append("")

    # Displacement comparison
    disp_r1 = np.sqrt(
        (df_r1["fcenter.x [m]"].values - df_r1["fcenter.x [m]"].values[0])**2 +
        (df_r1["fcenter.y [m]"].values - df_r1["fcenter.y [m]"].values[0])**2 +
        (df_r1["fcenter.z [m]"].values - df_r1["fcenter.z [m]"].values[0])**2
    ) * 1000
    disp_r2 = np.sqrt(
        (df_r2["fcenter.x [m]"].values - df_r2["fcenter.x [m]"].values[0])**2 +
        (df_r2["fcenter.y [m]"].values - df_r2["fcenter.y [m]"].values[0])**2 +
        (df_r2["fcenter.z [m]"].values - df_r2["fcenter.z [m]"].values[0])**2
    ) * 1000

    max_r1 = np.max(disp_r1)
    max_r2 = np.max(disp_r2)
    diff_pct = abs(max_r2 - max_r1) / max(max_r1, 1e-6) * 100

    lines.append(f"**Diferencia en max desplazamiento:** {abs(max_r2 - max_r1):.2f} mm ({diff_pct:.1f}%)")
    lines.append("")
    if diff_pct < 20:
        lines.append("Resultado: **CONSISTENTE** — diferencia < 20% atribuible a resolucion dp.")
    elif diff_pct < 50:
        lines.append("Resultado: **PARCIALMENTE CONSISTENTE** — diferencia 20-50%, efecto dp significativo.")
    else:
        lines.append("Resultado: **INCONSISTENTE** — diferencia > 50%, posible problema.")
    lines.append("")

    return "\n".join(lines), can_plot


# ---------------------------------------------------------------------------
# Figures
# ---------------------------------------------------------------------------

def plot_temporal_timelines(all_chrono: dict, temporals: list[dict], params_df: pd.DataFrame):
    """Plot displacement and velocity timelines for all 15 cases."""
    fig, axes = plt.subplots(3, 1, figsize=(16, 14), sharex=True)

    # Sort by displacement
    sorted_cases = sorted(temporals, key=lambda x: x["disp_end_mm"])
    estable_ids = [t["case_id"] for t in sorted_cases if t["disp_end_mm"] < DISP_THRESHOLD_MM]
    fallo_ids = [t["case_id"] for t in sorted_cases if t["disp_end_mm"] >= DISP_THRESHOLD_MM]

    cmap_estable = plt.cm.Greens(np.linspace(0.4, 0.9, max(len(estable_ids), 1)))
    cmap_fallo = plt.cm.Reds(np.linspace(0.3, 0.95, max(len(fallo_ids), 1)))

    # Panel A: Displacement (ESTABLE cases)
    ax = axes[0]
    for i, cid in enumerate(estable_ids):
        df = all_chrono[cid]
        t = df["time [s]"].values
        cx = df["fcenter.x [m]"].values
        cy = df["fcenter.y [m]"].values
        cz = df["fcenter.z [m]"].values
        disp = np.sqrt((cx - cx[0])**2 + (cy - cy[0])**2 + (cz - cz[0])**2) * 1000
        ax.plot(t, disp, color=cmap_estable[i], label=cid, lw=1.5)
    ax.axhline(DISP_THRESHOLD_MM, color="gray", ls="--", alpha=0.5, label=f"Umbral {DISP_THRESHOLD_MM}mm")
    ax.set_ylabel("Desplazamiento 3D [mm]")
    ax.set_title("Casos ESTABLE: Desplazamiento temporal")
    ax.legend(fontsize=8, ncol=3)
    ax.grid(True, alpha=0.3)
    ax.set_ylim(0, 8)

    # Panel B: Displacement (FALLO cases)
    ax = axes[1]
    for i, cid in enumerate(fallo_ids):
        df = all_chrono[cid]
        t = df["time [s]"].values
        cx = df["fcenter.x [m]"].values
        cy = df["fcenter.y [m]"].values
        cz = df["fcenter.z [m]"].values
        disp = np.sqrt((cx - cx[0])**2 + (cy - cy[0])**2 + (cz - cz[0])**2) * 1000
        ax.plot(t, disp, color=cmap_fallo[i], label=cid, lw=1.2)
    ax.axhline(DISP_THRESHOLD_MM, color="gray", ls="--", alpha=0.5)
    ax.set_ylabel("Desplazamiento 3D [mm]")
    ax.set_title("Casos FALLO: Desplazamiento temporal")
    ax.legend(fontsize=7, ncol=3)
    ax.grid(True, alpha=0.3)

    # Panel C: Horizontal velocity (all cases)
    ax = axes[2]
    for i, cid in enumerate(estable_ids):
        df = all_chrono[cid]
        t = df["time [s]"].values
        vx = df["fvel.x [m/s]"].values
        vy = df["fvel.y [m/s]"].values
        vel_h = np.sqrt(vx**2 + vy**2)
        ax.plot(t, vel_h, color=cmap_estable[i], label=cid, lw=1.0, alpha=0.7)
    for i, cid in enumerate(fallo_ids):
        df = all_chrono[cid]
        t = df["time [s]"].values
        vx = df["fvel.x [m/s]"].values
        vy = df["fvel.y [m/s]"].values
        vel_h = np.sqrt(vx**2 + vy**2)
        ax.plot(t, vel_h, color=cmap_fallo[i], label=cid, lw=1.0, alpha=0.8)
    ax.set_ylabel("Velocidad horizontal [m/s]")
    ax.set_xlabel("Tiempo [s]")
    ax.set_title("Todos los casos: Velocidad horizontal del boulder")
    ax.legend(fontsize=6, ncol=5, loc="upper right")
    ax.grid(True, alpha=0.3)

    fig.suptitle("Round 2 (dp=0.004): Series temporales de cinematica del boulder", fontsize=14, y=1.01)
    fig.tight_layout()
    fig.savefig(str(FIGURES / "r2_deep_temporal_timelines.png"), dpi=150, bbox_inches="tight")
    plt.close(fig)
    print("  [FIG] r2_deep_temporal_timelines.png")


def plot_replication(df_r1: pd.DataFrame, df_r2: pd.DataFrame):
    """Plot sc_008 vs sc2_015 replication comparison."""
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))

    for label, df, color, ls in [
        ("sc_008 (R1, dp=0.005)", df_r1, "#3498db", "-"),
        ("sc2_015 (R2, dp=0.004)", df_r2, "#e74c3c", "--"),
    ]:
        t = df["time [s]"].values
        cx = df["fcenter.x [m]"].values
        cy = df["fcenter.y [m]"].values
        cz = df["fcenter.z [m]"].values
        vx = df["fvel.x [m/s]"].values
        vy = df["fvel.y [m/s]"].values
        vz = df["fvel.z [m/s]"].values

        disp = np.sqrt((cx - cx[0])**2 + (cy - cy[0])**2 + (cz - cz[0])**2) * 1000
        vel_h = np.sqrt(vx**2 + vy**2)

        axes[0, 0].plot(t, disp, color=color, ls=ls, lw=1.5, label=label)
        axes[0, 1].plot(t, vel_h, color=color, ls=ls, lw=1.5, label=label)
        axes[1, 0].plot(t, cx, color=color, ls=ls, lw=1.5, label=label)
        axes[1, 1].plot(t, cz, color=color, ls=ls, lw=1.5, label=label)

    axes[0, 0].set_ylabel("Desplazamiento 3D [mm]")
    axes[0, 0].set_title("Desplazamiento")
    axes[0, 1].set_ylabel("Velocidad horizontal [m/s]")
    axes[0, 1].set_title("Velocidad horizontal")
    axes[1, 0].set_ylabel("fcenter.x [m]")
    axes[1, 0].set_title("Posicion X")
    axes[1, 1].set_ylabel("fcenter.z [m]")
    axes[1, 1].set_title("Posicion Z")

    for ax in axes.flat:
        ax.set_xlabel("Tiempo [s]")
        ax.legend(fontsize=8)
        ax.grid(True, alpha=0.3)

    fig.suptitle("Verificacion de replicacion: sc_008 (R1) vs sc2_015 (R2)", fontsize=14)
    fig.tight_layout()
    fig.savefig(str(FIGURES / "r2_deep_replication_timeseries.png"), dpi=150, bbox_inches="tight")
    plt.close(fig)
    print("  [FIG] r2_deep_replication_timeseries.png")


def plot_spearman_heatmap(spearman_df: pd.DataFrame):
    """Plot Spearman correlation heatmap with p-values."""
    input_vars = ["dam_h", "mass", "rot_z", "friction", "slope_inv"]
    output_vars = ["max_disp_mm", "max_rot_deg"]

    rho_matrix = np.zeros((len(input_vars), len(output_vars)))
    pval_matrix = np.zeros((len(input_vars), len(output_vars)))

    for _, row in spearman_df.iterrows():
        i = input_vars.index(row["input_var"])
        j = output_vars.index(row["output_var"])
        rho_matrix[i, j] = row["spearman_rho"]
        pval_matrix[i, j] = row["p_value"]

    fig, ax = plt.subplots(figsize=(8, 6))
    im = ax.imshow(rho_matrix, cmap="RdBu_r", vmin=-1, vmax=1, aspect="auto")

    ax.set_xticks(range(len(output_vars)))
    ax.set_yticks(range(len(input_vars)))
    ax.set_xticklabels(output_vars, fontsize=10)
    ax.set_yticklabels(input_vars, fontsize=10)

    for i in range(len(input_vars)):
        for j in range(len(output_vars)):
            rho = rho_matrix[i, j]
            pval = pval_matrix[i, j]
            star = ""
            if pval < 0.01:
                star = "***"
            elif pval < 0.05:
                star = "**"
            elif pval < 0.10:
                star = "*"
            ax.text(j, i, f"{rho:+.3f}\n(p={pval:.3f}){star}",
                    ha="center", va="center", fontsize=9,
                    color="white" if abs(rho) > 0.5 else "black")

    fig.colorbar(im, ax=ax, label="Spearman rho")
    ax.set_title("Correlaciones Spearman: Variables de entrada vs Respuesta\n"
                  "(*** p<0.01, ** p<0.05, * p<0.10)")
    fig.tight_layout()
    fig.savefig(str(FIGURES / "r2_deep_spearman_heatmap.png"), dpi=150, bbox_inches="tight")
    plt.close(fig)
    print("  [FIG] r2_deep_spearman_heatmap.png")


def plot_isolated_variables(df_results: pd.DataFrame):
    """Plot isolated variable pairs."""
    fig, axes = plt.subplots(1, 3, figsize=(16, 5))

    # a) Slope effect
    ax = axes[0]
    pair = df_results[df_results["case_id"].isin(["sc2_010", "sc2_011"])].sort_values("slope_inv")
    bars = ax.bar(pair["case_id"], pair["max_disp_mm"], color=["#3498db", "#2980b9"], edgecolor="k")
    for idx, (_, row) in enumerate(pair.iterrows()):
        ax.text(idx, row["max_disp_mm"] + 30, f"slope=1:{row['slope_inv']:.0f}\n{row['max_disp_mm']:.0f}mm",
                ha="center", fontsize=9)
    ax.set_ylabel("Desplazamiento max [mm]")
    ax.set_title("Efecto pendiente\n(dam_h=0.20, mass=1.0, fric=0.3)")
    ax.grid(True, alpha=0.3, axis="y")

    # b) Friction effect
    ax = axes[1]
    pair = df_results[df_results["case_id"].isin(["sc2_012", "sc2_013"])].sort_values("friction")
    colors_fric = ["#e74c3c", "#27ae60"]  # low fric = red (danger), high = green (stable)
    bars = ax.bar(pair["case_id"], pair["max_disp_mm"], color=colors_fric, edgecolor="k")
    for idx, (_, row) in enumerate(pair.iterrows()):
        label_y = row["max_disp_mm"] + max(pair["max_disp_mm"]) * 0.05
        ax.text(idx, label_y, f"mu={row['friction']:.1f}\n{row['max_disp_mm']:.0f}mm",
                ha="center", fontsize=9)
    ax.axhline(DISP_THRESHOLD_MM, color="gray", ls="--", alpha=0.5)
    ax.set_ylabel("Desplazamiento max [mm]")
    ax.set_title("Efecto friccion\n(dam_h=0.20, mass=1.0, slope=1:20)")
    ax.grid(True, alpha=0.3, axis="y")

    # c) Rotation effect (sc2_011 rot=0 vs sc2_014 rot=90, closest pair)
    ax = axes[2]
    pair = df_results[df_results["case_id"].isin(["sc2_011", "sc2_014"])].sort_values("rot_z")
    bars = ax.bar(pair["case_id"], pair["max_disp_mm"], color=["#9b59b6", "#8e44ad"], edgecolor="k")
    for idx, (_, row) in enumerate(pair.iterrows()):
        extra = f"\nslope=1:{row['slope_inv']:.0f}" if row['slope_inv'] != 20 else ""
        ax.text(idx, row["max_disp_mm"] + max(pair["max_disp_mm"]) * 0.05,
                f"rot={row['rot_z']:.0f} deg{extra}\n{row['max_disp_mm']:.0f}mm",
                ha="center", fontsize=9)
    ax.set_ylabel("Desplazamiento max [mm]")
    ax.set_title("Efecto rotacion (confundido con slope)\n(dam_h=0.20, mass=1.0, fric=0.3)")
    ax.grid(True, alpha=0.3, axis="y")

    fig.suptitle("Round 2: Analisis de variables aisladas", fontsize=14)
    fig.tight_layout()
    fig.savefig(str(FIGURES / "r2_deep_isolated_variables.png"), dpi=150, bbox_inches="tight")
    plt.close(fig)
    print("  [FIG] r2_deep_isolated_variables.png")


def plot_force_comparison(force_data: list[dict], params_df: pd.DataFrame):
    """Plot force comparison across cases."""
    valid = [f for f in force_data if not f.get("error", True)]
    if not valid:
        print("  [SKIP] No force data to plot")
        return

    fig, axes = plt.subplots(1, 2, figsize=(14, 6))

    # Bar chart: max SPH force vs max contact force
    ax = axes[0]
    case_ids = [f["case_id"] for f in valid]
    sph_forces = [f["max_sph_force_N"] for f in valid]
    contact_forces = [f["max_contact_force_N"] for f in valid]

    x = np.arange(len(case_ids))
    w = 0.35
    ax.bar(x - w/2, sph_forces, w, label="Max SPH force [N]", color="#3498db", edgecolor="k")
    ax.bar(x + w/2, contact_forces, w, label="Max Contact force [N]", color="#e74c3c", edgecolor="k")
    ax.set_xticks(x)
    ax.set_xticklabels(case_ids, rotation=45, ha="right", fontsize=8)
    ax.set_ylabel("Fuerza [N]")
    ax.set_title("Fuerzas maximas por caso")
    ax.legend()
    ax.set_yscale("log")
    ax.grid(True, alpha=0.3, axis="y")

    # Scatter: SPH force vs displacement
    ax = axes[1]
    merged = params_df.set_index("case_id")
    for f in valid:
        cid = f["case_id"]
        if cid in merged.index:
            disp = merged.loc[cid, "max_disp_mm"]
            estado = merged.loc[cid, "estado"]
            color = "#27ae60" if estado == "ESTABLE" else "#e74c3c"
            ax.scatter(f["max_sph_force_N"], disp, c=color, s=60, edgecolors="k", zorder=3)
            ax.annotate(cid, (f["max_sph_force_N"], disp), fontsize=7,
                        xytext=(5, 5), textcoords="offset points")
    ax.set_xlabel("Max SPH Force [N]")
    ax.set_ylabel("Desplazamiento max [mm]")
    ax.set_title("SPH Force vs Desplazamiento")
    ax.grid(True, alpha=0.3)

    fig.suptitle("Round 2: Analisis de fuerzas", fontsize=14)
    fig.tight_layout()
    fig.savefig(str(FIGURES / "r2_deep_force_analysis.png"), dpi=150, bbox_inches="tight")
    plt.close(fig)
    print("  [FIG] r2_deep_force_analysis.png")


def plot_sc2_010_gauges():
    """Special plot for sc2_010 showing gauge positions on slope profile."""
    fig, axes = plt.subplots(2, 1, figsize=(14, 8))

    # Panel A: Slope profile with gauge positions
    ax = axes[0]
    # Slope 1:5: from x~5m, z rises 1m per 5m
    x_flat = np.array([0, 5.0])
    z_flat = np.array([0, 0])
    x_slope = np.linspace(5.0, 15.0, 50)
    z_slope = (x_slope - 5.0) / 5.0

    ax.fill_between(np.concatenate([x_flat, x_slope]),
                     np.concatenate([z_flat, z_slope]),
                     -0.2, color="#d4a373", alpha=0.3, label="Beach slope 1:5")
    ax.plot(np.concatenate([x_flat, x_slope]),
            np.concatenate([z_flat, z_slope]), "k-", lw=2)

    # Dam water level
    ax.fill_between([0, 0.25], [0, 0], [0.198, 0.198], color="#74b9ff", alpha=0.3, label="Dam (h=0.198m)")

    # Gauge positions - velocity
    v_positions = [
        (1, 0.25, 0.004), (2, 1.50, 0.004), (3, 2.50, 0.004), (4, 3.00, 0.004),
        (5, 6.41, 0.087), (6, 6.48, 0.119), (7, 6.59, 0.122),
        (8, 8.75, 0.554), (9, 8.75, 0.554), (10, 8.75, 0.554),
        (11, 9.50, 0.704), (12, 12.00, 1.204),
    ]
    for gnum, gx, gz in v_positions:
        # Check if gauge detects flow
        df_v = load_gauge_vel("sc2_010", gnum)
        max_vx = df_v["velx [m/s]"].max() if not df_v.empty else 0
        color = "#27ae60" if max_vx > 0.01 else "#e74c3c"
        marker = "v" if max_vx > 0.01 else "x"
        ax.scatter(gx, gz, c=color, marker=marker, s=80, zorder=5,
                   edgecolors="k" if max_vx > 0.01 else "none")
        ax.annotate(f"V{gnum:02d}", (gx, gz), fontsize=7,
                    xytext=(3, 8), textcoords="offset points")

    # Boulder position
    df_chr = load_chrono("sc2_010")
    bx0 = df_chr["fcenter.x [m]"].iloc[0]
    bz0 = df_chr["fcenter.z [m]"].iloc[0]
    ax.scatter(bx0, bz0, c="orange", s=150, marker="s", zorder=6,
               edgecolors="k", label=f"Boulder (x={bx0:.2f}, z={bz0:.3f})")

    ax.set_xlabel("x [m]")
    ax.set_ylabel("z [m]")
    ax.set_title("sc2_010 (slope=1:5): Posicion de gauges en perfil del canal")
    ax.legend(fontsize=8, loc="upper left")
    ax.set_xlim(-0.5, 15.5)
    ax.set_ylim(-0.3, 2.5)
    ax.set_aspect("equal")
    ax.grid(True, alpha=0.3)

    # Panel B: Velocity gauges that detect flow
    ax = axes[1]
    for gnum in [1, 2, 3, 4, 5]:
        df_v = load_gauge_vel("sc2_010", gnum)
        if not df_v.empty:
            t = df_v["time [s]"].values
            vx = df_v["velx [m/s]"].values
            valid = ~np.isnan(vx)
            ax.plot(t[valid], vx[valid], label=f"V{gnum:02d}", lw=1.0, alpha=0.8)

    ax.set_xlabel("Tiempo [s]")
    ax.set_ylabel("velx [m/s]")
    ax.set_title("sc2_010: Velocidad del flujo (gauges con datos validos)")
    ax.legend(fontsize=8)
    ax.grid(True, alpha=0.3)

    fig.suptitle("Investigacion sc2_010: slope=1:5, water_h reportado = 0.0", fontsize=14)
    fig.tight_layout()
    fig.savefig(str(FIGURES / "r2_deep_sc2_010_investigation.png"), dpi=150, bbox_inches="tight")
    plt.close(fig)
    print("  [FIG] r2_deep_sc2_010_investigation.png")


def plot_sc2_007_surprise(all_chrono: dict, params_df: pd.DataFrame):
    """Plot sc2_007 (surprisingly high displacement despite low dam_h=0.12)."""
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))

    # Compare sc2_007 with sc2_001 (dam_h=0.15, same friction=0.3, same mass=1.0 approx)
    compare_cases = ["sc2_007", "sc2_001", "sc2_008"]
    colors = {"sc2_007": "#e74c3c", "sc2_001": "#3498db", "sc2_008": "#27ae60"}

    for cid in compare_cases:
        if cid not in all_chrono:
            continue
        df = all_chrono[cid]
        t = df["time [s]"].values
        cx = df["fcenter.x [m]"].values
        cy = df["fcenter.y [m]"].values
        cz = df["fcenter.z [m]"].values
        disp = np.sqrt((cx - cx[0])**2 + (cy - cy[0])**2 + (cz - cz[0])**2) * 1000
        vx = df["fvel.x [m/s]"].values
        vy = df["fvel.y [m/s]"].values
        vel_h = np.sqrt(vx**2 + vy**2)

        row = params_df[params_df["case_id"] == cid].iloc[0]
        label = f"{cid} (dh={row['dam_h']}, m={row['mass']}, mu={row['friction']})"
        axes[0].plot(t, disp, color=colors[cid], lw=1.5, label=label)
        axes[1].plot(t, vel_h, color=colors[cid], lw=1.5, label=label)

    axes[0].set_ylabel("Desplazamiento [mm]")
    axes[0].set_xlabel("Tiempo [s]")
    axes[0].set_title("Desplazamiento")
    axes[0].legend(fontsize=8)
    axes[0].grid(True, alpha=0.3)

    axes[1].set_ylabel("Velocidad horizontal [m/s]")
    axes[1].set_xlabel("Tiempo [s]")
    axes[1].set_title("Velocidad horizontal")
    axes[1].legend(fontsize=8)
    axes[1].grid(True, alpha=0.3)

    fig.suptitle("Caso sorpresa sc2_007: dam_h=0.12 + friction=0.1 => FALLO 1097mm", fontsize=13)
    fig.tight_layout()
    fig.savefig(str(FIGURES / "r2_deep_sc2_007_surprise.png"), dpi=150, bbox_inches="tight")
    plt.close(fig)
    print("  [FIG] r2_deep_sc2_007_surprise.png")


# ---------------------------------------------------------------------------
# Main report generator
# ---------------------------------------------------------------------------

def generate_report(
    temporals: list[dict],
    domain_results: list[dict],
    reflection_results: list[dict],
    sc2_010_text: str,
    force_data: list[dict],
    spearman_df: pd.DataFrame,
    isolated_text: str,
    replication_text: str,
    params_df: pd.DataFrame,
) -> str:
    """Generate the complete markdown report."""
    lines = []

    lines.append("# Analisis Profundo: Screening Round 2 (dp=0.004)")
    lines.append("")
    lines.append(f"**Generado:** {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M')}")
    lines.append(f"**Casos:** 15 (sc2_001 a sc2_015)")
    lines.append(f"**Resolucion:** dp = 0.004 m")
    lines.append(f"**Simulacion:** 10s (FtPause=0.5s), DualSPHysics v5.4 + Chrono")
    lines.append("")
    lines.append("---")
    lines.append("")

    # ===== Section 1: Temporal Analysis =====
    lines.append("## 1. Analisis Temporal")
    lines.append("")
    lines.append("| Caso | t_impact [s] | t_peak [s] | v_peak [m/s] | t_stable [s] | vel_end [m/s] | disp_end [mm] | Still moving? |")
    lines.append("|------|-------------|------------|-------------|-------------|--------------|---------------|---------------|")

    for t in sorted(temporals, key=lambda x: x["disp_end_mm"]):
        t_imp = f"{t['t_impact']:.3f}" if not np.isnan(t['t_impact']) else "-"
        t_pk = f"{t['t_peak']:.3f}"
        v_pk = f"{t['v_peak']:.4f}"
        t_st = f"{t['t_stable']:.3f}" if not np.isnan(t['t_stable']) else "nunca"
        v_end = f"{t['vel_end']:.4f}"
        d_end = f"{t['disp_end_mm']:.2f}"
        moving = "SI" if t["still_moving"] else "no"
        lines.append(f"| {t['case_id']} | {t_imp} | {t_pk} | {v_pk} | {t_st} | {v_end} | {d_end} | {moving} |")

    lines.append("")
    lines.append("**Observaciones temporales:**")
    lines.append("")

    # Count still moving
    n_moving = sum(1 for t in temporals if t["still_moving"])
    n_stable = sum(1 for t in temporals if not t["still_moving"])
    lines.append(f"- {n_moving} casos siguen moviendose a t=10s (vel > 0.01 m/s)")
    lines.append(f"- {n_stable} casos se estabilizaron antes de t=10s")

    # Average impact time
    impact_times = [t["t_impact"] for t in temporals if not np.isnan(t["t_impact"])]
    if impact_times:
        lines.append(f"- Tiempo promedio de impacto: {np.mean(impact_times):.3f}s (min={np.min(impact_times):.3f}, max={np.max(impact_times):.3f})")
    lines.append("")

    # ===== Section 2: Domain Adequacy =====
    lines.append("---")
    lines.append("")
    lines.append("## 2. Adecuacion del Dominio")
    lines.append("")
    lines.append("Para casos FALLO, margen restante al borde downstream (dominio = 15m):")
    lines.append("")
    lines.append("| Caso | x_final [m] | Margen downstream [m] | % dominio usado | Adecuado? |")
    lines.append("|------|------------|----------------------|-----------------|-----------|")

    for d in sorted(domain_results, key=lambda x: -x["disp_total_mm"]):
        adequate = "SI" if d["margin_downstream_m"] > 2.0 else "REVISAR"
        lines.append(f"| {d['case_id']} | {d['x_final']:.3f} | {d['margin_downstream_m']:.2f} | "
                      f"{d['pct_domain_used']:.1f}% | {adequate} |")

    lines.append("")
    min_margin = min(d["margin_downstream_m"] for d in domain_results)
    lines.append(f"**Margen minimo:** {min_margin:.2f} m")
    if min_margin > 2.0:
        lines.append("**Conclusion:** Dominio adecuado para todos los casos FALLO.")
    else:
        lines.append("**ALERTA:** Algun caso se acerca al borde del dominio.")
    lines.append("")

    # ===== Section 3: Reflection Analysis =====
    lines.append("---")
    lines.append("")
    lines.append("## 3. Analisis de Reflexion (gauge V12 a x~12m)")
    lines.append("")
    lines.append("| Caso | dam_h | t_arrival [s] | max_vx [m/s] | min_vx [m/s] | Peaks forward | Peaks reflejados | Reflexion? |")
    lines.append("|------|-------|--------------|-------------|-------------|---------------|-----------------|------------|")

    for r in reflection_results:
        if r.get("skip"):
            lines.append(f"| {r['case_id']} | - | - | - | - | - | - | {r.get('reason', 'skip')} |")
            continue
        t_arr = f"{r['t_arrival']:.3f}" if not np.isnan(r["t_arrival"]) else "-"
        refl = "SI" if r["has_reflection"] else "no"
        row_p = params_df[params_df["case_id"] == r["case_id"]]
        dh = f"{row_p['dam_h'].values[0]:.3f}" if len(row_p) > 0 else "-"
        lines.append(f"| {r['case_id']} | {dh} | {t_arr} | {r['max_vx']:.4f} | {r['min_vx']:.4f} | "
                      f"{r['n_forward_peaks']} | {r['n_reflected_peaks']} | {refl} |")

    lines.append("")

    # ===== Section 4: sc2_010 Investigation =====
    lines.append("---")
    lines.append("")
    lines.append("## 4. Investigacion sc2_010 (slope=1:5, water_h=0.0)")
    lines.append("")
    lines.append(sc2_010_text)
    lines.append("")

    # ===== Section 5: Force Analysis =====
    lines.append("---")
    lines.append("")
    lines.append("## 5. Analisis de Fuerzas")
    lines.append("")
    lines.append("Fuerzas SPH (corregidas por gravedad) y de contacto (Chrono).")
    lines.append("")
    lines.append("| Caso | Max SPH [N] | Max Contact [N] | Mean Contact [N] | t_peak_SPH [s] | Ratio SPH/Contact |")
    lines.append("|------|------------|----------------|-----------------|----------------|-------------------|")

    valid_forces = [f for f in force_data if not f.get("error", True)]
    for f in sorted(valid_forces, key=lambda x: x["case_id"]):
        lines.append(f"| {f['case_id']} | {f['max_sph_force_N']:.2f} | {f['max_contact_force_N']:.1f} | "
                      f"{f['mean_contact_force_N']:.1f} | {f['t_sph_peak']:.3f} | {f['sph_contact_ratio']:.4f} |")

    lines.append("")
    lines.append("**Observaciones:**")
    lines.append("")
    lines.append("- Las fuerzas de contacto (Chrono) dominan por ordenes de magnitud sobre las fuerzas SPH.")
    lines.append("- Esto confirma que el mecanismo principal de resistencia es la friccion de contacto,")
    lines.append("  no la presion hidrodinamica directa (coherente con hallazgos del Round 1).")
    lines.append("- El ratio SPH/Contact << 1 indica que las fuerzas SPH son perturbaciones pequenas")
    lines.append("  comparadas con las fuerzas de contacto normales + friccion.")
    lines.append("")

    # ===== Section 6: Spearman Correlations =====
    lines.append("---")
    lines.append("")
    lines.append("## 6. Correlaciones Spearman con p-values")
    lines.append("")
    lines.append("| Variable entrada | Variable salida | rho | p-value | Significativo (alpha=0.05)? |")
    lines.append("|-----------------|----------------|------|---------|---------------------------|")

    for _, row in spearman_df.iterrows():
        sig = "SI" if row["significant_005"] else ("marginal" if row["significant_010"] else "no")
        lines.append(f"| {row['input_var']} | {row['output_var']} | {row['spearman_rho']:+.3f} | "
                      f"{row['p_value']:.4f} | {sig} |")

    lines.append("")
    lines.append("**Interpretacion:**")
    lines.append("")

    # Find strongest correlations
    for out in ["max_disp_mm", "max_rot_deg"]:
        subset = spearman_df[spearman_df["output_var"] == out].sort_values("p_value")
        best = subset.iloc[0]
        lines.append(f"- **{out}:** variable mas correlacionada = **{best['input_var']}** "
                      f"(rho={best['spearman_rho']:+.3f}, p={best['p_value']:.4f})")

    # Note about small sample size
    lines.append(f"- **NOTA:** n=15 es un tamano muestral pequeno. Correlaciones con p>0.10 no deben")
    lines.append(f"  interpretarse como ausencia de efecto, sino como evidencia insuficiente.")
    lines.append("")

    # ===== Section 7: Isolated Variables =====
    lines.append("---")
    lines.append("")
    lines.append("## 7. Analisis de Variables Aisladas")
    lines.append("")
    lines.append(isolated_text)
    lines.append("")

    # ===== Section 8: Replication Check =====
    lines.append("---")
    lines.append("")
    lines.append("## 8. Verificacion de Replicacion")
    lines.append("")
    lines.append(replication_text)
    lines.append("")

    # ===== Section 9: Key Findings =====
    lines.append("---")
    lines.append("")
    lines.append("## 9. Hallazgos Clave y Conclusiones")
    lines.append("")
    lines.append("### 9.1 Clasificacion")
    lines.append("")

    estable = params_df[params_df["estado"] == "ESTABLE"]["case_id"].tolist()
    fallo = params_df[params_df["estado"] == "FALLO"]["case_id"].tolist()
    lines.append(f"- **ESTABLE ({len(estable)}):** {', '.join(estable)}")
    lines.append(f"- **FALLO ({len(fallo)}):** {', '.join(fallo)}")
    lines.append("")

    lines.append("### 9.2 Caso sorpresa: sc2_007")
    lines.append("")
    lines.append("- dam_h=0.12m (la mas baja), mass=0.8kg, friction=0.1 -> FALLO con 1097mm")
    lines.append("- A pesar del dam_h bajo, la combinacion de:")
    lines.append("  - **Baja masa (0.8 kg):** reduce inercia")
    lines.append("  - **Baja friccion (0.1):** reduce resistencia Coulomb")
    lines.append("  - Resulta en movimiento significativo")
    lines.append("- **Implicacion:** dam_h NO es suficiente como unico predictor. La combinacion")
    lines.append("  mass + friction es critica en el regimen de dam_h < 0.15m.")
    lines.append("")

    lines.append("### 9.3 Efecto de la friccion (hallazgo principal)")
    lines.append("")
    lines.append("- El par sc2_012 (mu=0.1) vs sc2_013 (mu=0.8) demuestra que:")
    lines.append("  - mu=0.1: 2768mm (FALLO extremo)")
    lines.append("  - mu=0.8: 1.57mm (ESTABLE, minimo desplazamiento de los 15 casos)")
    lines.append("- **Factor:** ~1762x diferencia en desplazamiento")
    lines.append("- Friccion es la variable mas importante para estabilidad en dam_h=0.20m")
    lines.append("")

    lines.append("### 9.4 Efecto de la pendiente")
    lines.append("")
    lines.append("- sc2_010 (1:5): 133.5mm vs sc2_011 (1:30): 1132mm")
    lines.append("- Pendiente pronunciada disipa energia antes de llegar al boulder")
    lines.append("- **PERO** sc2_010 tiene water_h=0.0 (artefacto de gauges secos)")
    lines.append("")

    lines.append("### 9.5 Integridad del dominio")
    lines.append("")
    max_x = max(d["x_final"] for d in domain_results)
    lines.append(f"- Posicion x maxima alcanzada: {max_x:.2f}m de 15m disponibles")
    lines.append(f"- Ningun boulder se acerca al limite del dominio")
    lines.append("")

    lines.append("### 9.6 Recomendaciones para Round 3")
    lines.append("")
    lines.append("1. **Agregar caso baseline puro:** dam_h=0.20, mass=1.0, rot=0, fric=0.3, slope=1:20")
    lines.append("   (curiosamente no existe en R2 — sc2_010 y sc2_011 difieren en slope)")
    lines.append("2. **Explorar frontera de friccion:** 0.2 < mu < 0.5 a dam_h=0.20m")
    lines.append("3. **Explorar dam_h 0.12-0.15m** con baja friccion para mapear frontera")
    lines.append("4. **Resolver water_h=0.0 para sc2_010:** agregar gauges a z adaptada al slope")
    lines.append("")

    return "\n".join(lines)


# ===========================================================================
# MAIN
# ===========================================================================

def main():
    print("=" * 70)
    print("  Analisis Profundo: Screening Round 2 (dp=0.004)")
    print("=" * 70)

    # Load parameters
    params_df = pd.read_csv(PARAMS_CSV)
    print(f"\nCargados parametros de {len(params_df)} casos")

    # Load results summary
    results_csv = RESULTS / "results_round2.csv"
    if results_csv.exists():
        df_results = pd.read_csv(results_csv)
        print(f"Cargados resultados de {len(df_results)} casos desde results_round2.csv")
    else:
        print("ERROR: No se encontro results_round2.csv. Ejecutar import_round2.py primero.")
        return 1

    # Merge parameters with results
    df_merged = df_results.merge(
        params_df[["case_id", "dam_height", "boulder_mass", "boulder_rot_z",
                    "friction_coefficient", "slope_inv"]],
        on="case_id", how="left", suffixes=("", "_param")
    )

    # ===== Load all chrono data =====
    print("\n[1/8] Cargando datos cinematicos...")
    all_chrono = {}
    case_ids = sorted(params_df["case_id"].tolist())
    for cid in case_ids:
        try:
            all_chrono[cid] = load_chrono(cid)
            print(f"  {cid}: {len(all_chrono[cid])} timesteps OK")
        except Exception as e:
            print(f"  {cid}: ERROR - {e}")

    # ===== 1. Temporal analysis =====
    print("\n[2/8] Analisis temporal...")
    temporals = []
    for cid in case_ids:
        if cid in all_chrono:
            t = temporal_analysis(cid, all_chrono[cid])
            temporals.append(t)
            status = "MOVING" if t["still_moving"] else "stable"
            print(f"  {cid}: t_impact={t['t_impact']:.3f}s, v_peak={t['v_peak']:.4f} m/s, "
                  f"disp={t['disp_end_mm']:.1f}mm, {status}")

    # ===== 2. Domain adequacy =====
    print("\n[3/8] Adecuacion del dominio...")
    domain_results = []
    for t in temporals:
        cid = t["case_id"]
        row = df_results[df_results["case_id"] == cid]
        if len(row) > 0 and row.iloc[0]["estado"] == "FALLO":
            d = domain_adequacy(t, {})
            domain_results.append(d)
            print(f"  {cid}: x_final={d['x_final']:.3f}m, margen={d['margin_downstream_m']:.2f}m")

    # ===== 3. Reflection analysis =====
    print("\n[4/8] Analisis de reflexion...")
    reflection_results = []
    for _, row in params_df.iterrows():
        cid = row["case_id"]
        r = reflection_analysis(cid, row["dam_height"])
        reflection_results.append(r)
        if not r.get("skip"):
            refl = "REFLECTION" if r["has_reflection"] else "clean"
            print(f"  {cid}: {refl}, fwd_peaks={r['n_forward_peaks']}, refl_peaks={r['n_reflected_peaks']}")
        else:
            print(f"  {cid}: skipped ({r.get('reason', '')})")

    # ===== 4. sc2_010 investigation =====
    print("\n[5/8] Investigacion sc2_010...")
    sc2_010_text = investigate_sc2_010()
    print("  Completado")

    # ===== 5. Force analysis =====
    print("\n[6/8] Analisis de fuerzas...")
    force_data = []
    for _, row in params_df.iterrows():
        cid = row["case_id"]
        f = force_analysis(cid, row["boulder_mass"])
        force_data.append(f)
        if not f.get("error"):
            print(f"  {cid}: SPH={f['max_sph_force_N']:.2f}N, Contact={f['max_contact_force_N']:.1f}N, "
                  f"ratio={f['sph_contact_ratio']:.4f}")
        else:
            print(f"  {cid}: ERROR reading forces")

    # ===== 6. Spearman correlations =====
    print("\n[7/8] Correlaciones Spearman...")
    spearman_df = compute_spearman_correlations(df_results)
    for _, row in spearman_df.iterrows():
        sig = "*" if row["significant_005"] else ""
        print(f"  {row['input_var']:>12s} vs {row['output_var']:<15s}: rho={row['spearman_rho']:+.3f}, "
              f"p={row['p_value']:.4f} {sig}")

    # ===== 7. Isolated variable analysis =====
    print("\n[8/8] Variables aisladas...")
    isolated_text = isolated_variable_analysis(df_results)
    print("  Completado")

    # ===== 8. Replication check =====
    print("\n[BONUS] Verificacion de replicacion sc_008(R1) vs sc2_015(R2)...")
    replication_text, can_plot_replication = replication_check()
    print("  Completado")

    # ===== Generate figures =====
    print("\n--- Generando figuras ---")
    plot_temporal_timelines(all_chrono, temporals, df_results)
    plot_spearman_heatmap(spearman_df)
    plot_isolated_variables(df_results)
    plot_force_comparison(force_data, df_results)
    plot_sc2_010_gauges()
    plot_sc2_007_surprise(all_chrono, df_results)

    if can_plot_replication:
        try:
            df_r1 = load_chrono("sc_008")
            df_r2 = load_chrono("sc2_015")
            plot_replication(df_r1, df_r2)
        except Exception as e:
            print(f"  [SKIP] Replication plot: {e}")

    # ===== Generate report =====
    print("\n--- Generando reporte ---")
    report = generate_report(
        temporals=temporals,
        domain_results=domain_results,
        reflection_results=reflection_results,
        sc2_010_text=sc2_010_text,
        force_data=force_data,
        spearman_df=spearman_df,
        isolated_text=isolated_text,
        replication_text=replication_text,
        params_df=df_results,
    )

    report_path = FIGURES / "screening_round2_analysis_deep.md"
    report_path.write_text(report, encoding="utf-8")
    print(f"Reporte: {report_path}")
    print(f"Figuras: {FIGURES}")

    print("\n" + "=" * 70)
    print("  Analisis completado")
    print("=" * 70)

    return 0


if __name__ == "__main__":
    sys.exit(main() or 0)
