"""
Train the current thesis GP surrogate after AL batch3.

This script is intentionally specific to the current production campaign:

    inputs = [dam_height, friction_coefficient, boulder_mass]
    target = g = 5 - Dmax_percent_deq

where g > 0 means stable by the displacement-only criterion, and g < 0
means movement/failure. It does not touch the legacy data/gp_surrogate.pkl.

Outputs:
    data/analysis/gp_h_mu_mstar_after_al3_20260518/
    models/surrogates/gp_h_mu_mstar_after_al3_20260518.pkl
"""

from __future__ import annotations

import json
import math
import pickle
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Iterable

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.gaussian_process import GaussianProcessRegressor
from sklearn.gaussian_process.kernels import ConstantKernel, Matern, WhiteKernel
from sklearn.metrics import accuracy_score, mean_absolute_error, mean_squared_error
from sklearn.model_selection import LeaveOneOut
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import MinMaxScaler


PROJECT_ROOT = Path(__file__).resolve().parents[1]
ANALYSIS_ID = "gp_h_mu_mstar_after_al3_20260518"
OUT_DIR = PROJECT_ROOT / "data" / "analysis" / ANALYSIS_ID
FIG_DIR = OUT_DIR / "figures"
MODEL_DIR = PROJECT_ROOT / "models" / "surrogates"
MODEL_PATH = MODEL_DIR / "gp_h_mu_mstar_after_al3_20260518.pkl"

FEATURES = ["dam_height", "friction_coefficient", "boulder_mass"]
FEATURE_LABELS = {
    "dam_height": "H (m)",
    "friction_coefficient": "mu",
    "boulder_mass": "m*",
}
TARGET_RAW = "margin_pct_deq"
TARGET_TRAIN = "margin_train_pct_deq"

EXPORTS = [
    ("pilot", "exports/pilot_productivo_20260501/pilot_summary.csv"),
    ("batch2", "exports/batch2_productivo_20260505/batch2_summary.csv"),
    ("batch3", "exports/batch3_productivo_20260509/batch3_summary.csv"),
    ("batch4", "exports/batch4_mass_probe_20260513/batch4_summary.csv"),
    ("al1", "exports/al_batch1_hybrid_20260514/al_batch1_summary.csv"),
    ("al2", "exports/al_batch2_bracket_closing_20260516/al_batch2_summary.csv"),
    ("al3", "exports/al_batch3_gp_after_al2_20260518/al_batch3_summary.csv"),
]

DOMAIN_BOUNDS = {
    "dam_height": (0.175, 0.225),
    "friction_coefficient": (0.56, 0.90),
    "boulder_mass": (0.85, 1.25),
}
TRAIN_CLIP = (-20.0, 4.0)
DISPLACEMENT_THRESHOLD_PCT = 5.0
SEED = 11


@dataclass
class DatasetSummary:
    analysis_id: str
    n_master_rows: int
    n_used_rows: int
    n_excluded_rows: int
    n_fail: int
    n_stable: int
    domain_bounds: dict
    train_clip: tuple[float, float]
    features: list[str]
    target_raw: str
    target_train: str


def read_export(batch: str, rel_path: str) -> pd.DataFrame:
    path = PROJECT_ROOT / rel_path
    if not path.exists():
        raise FileNotFoundError(path)
    df = pd.read_csv(path)
    df["batch"] = batch
    df["source_file"] = rel_path.replace("\\", "/")
    if "case_id" not in df.columns and "case_name" in df.columns:
        df["case_id"] = df["case_name"]
    if "case_name" not in df.columns and "case_id" in df.columns:
        df["case_name"] = df["case_id"]
    return df


def numeric(df: pd.DataFrame, columns: Iterable[str]) -> None:
    for col in columns:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")


def build_master_dataset() -> pd.DataFrame:
    frames = [read_export(batch, rel_path) for batch, rel_path in EXPORTS]
    df = pd.concat(frames, ignore_index=True, sort=False)

    numeric(
        df,
        [
            "dam_height",
            "boulder_mass",
            "boulder_rot_z",
            "friction_coefficient",
            "slope_inv",
            "dp",
            "disp_pct_deq",
            "max_displacement_pct_deq",
            "max_displacement_m",
            "max_rotation_deg",
            "max_rotation",
            "max_velocity_ms",
            "max_velocity",
            "max_sph_force_N",
            "max_sph_force",
            "max_contact_force_N",
            "max_contact_force",
            "max_flow_velocity_ms",
            "max_flow_velocity",
            "max_water_height_m",
            "max_water_height",
        ],
    )

    df["disp_pct_deq_unified"] = df["disp_pct_deq"]
    if "max_displacement_pct_deq" in df.columns:
        df["disp_pct_deq_unified"] = df["disp_pct_deq_unified"].fillna(
            df["max_displacement_pct_deq"]
        )
    df[TARGET_RAW] = DISPLACEMENT_THRESHOLD_PCT - df["disp_pct_deq_unified"]
    df[TARGET_TRAIN] = df[TARGET_RAW].clip(*TRAIN_CLIP)
    df["class_from_margin"] = np.where(df[TARGET_RAW] < 0, "FALLO", "ESTABLE")

    status = df.get("status", pd.Series([""] * len(df), index=df.index)).astype(str)
    df["is_partial_or_diagnostic"] = status.str.contains(
        "PARTIAL|RECOVERED|NOT_SQLITE", case=False, na=False
    )
    df["is_official"] = ~df["is_partial_or_diagnostic"]

    reasons: list[str] = []
    for _, row in df.iterrows():
        reason = []
        if not bool(row.get("is_official", False)):
            reason.append("not_official_or_partial")
        if not math.isclose(float(row.get("dp", np.nan)), 0.003, rel_tol=0.0, abs_tol=1e-9):
            reason.append("not_dp_0.003")
        if str(row.get("classification_mode", "")) != "displacement_only":
            reason.append("not_displacement_only")
        if not math.isclose(float(row.get("slope_inv", np.nan)), 20.0, rel_tol=0.0, abs_tol=1e-9):
            reason.append("not_slope_20")
        for feat, (lo, hi) in DOMAIN_BOUNDS.items():
            val = float(row.get(feat, np.nan))
            if not (lo <= val <= hi):
                reason.append(f"{feat}_outside_domain")
        if pd.isna(row.get("disp_pct_deq_unified", np.nan)):
            reason.append("missing_displacement_pct")
        reasons.append(";".join(reason) if reason else "included")
    df["selection_reason"] = reasons
    df["used_for_gp"] = df["selection_reason"].eq("included")
    return df


def make_gp(n_features: int) -> GaussianProcessRegressor:
    kernel = (
        ConstantKernel(1.0, constant_value_bounds=(1e-2, 1e2))
        * Matern(
            length_scale=[0.4] * n_features,
            length_scale_bounds=(1e-2, 1e2),
            nu=2.5,
        )
        + WhiteKernel(noise_level=0.05, noise_level_bounds=(1e-6, 1e1))
    )
    return GaussianProcessRegressor(
        kernel=kernel,
        normalize_y=True,
        n_restarts_optimizer=20,
        random_state=SEED,
    )


def fit_pipeline(X: np.ndarray, y: np.ndarray):
    pipe = make_pipeline(MinMaxScaler(), make_gp(X.shape[1]))
    pipe.fit(X, y)
    return pipe


def loo_predictions(X: np.ndarray, y: np.ndarray, used: pd.DataFrame) -> pd.DataFrame:
    rows = []
    loo = LeaveOneOut()
    for train_idx, test_idx in loo.split(X):
        pipe = fit_pipeline(X[train_idx], y[train_idx])
        pred, std = pipe.predict(X[test_idx], return_std=True)
        i = int(test_idx[0])
        rows.append(
            {
                "case_id": used.iloc[i]["case_id"],
                "batch": used.iloc[i]["batch"],
                "dam_height": used.iloc[i]["dam_height"],
                "friction_coefficient": used.iloc[i]["friction_coefficient"],
                "boulder_mass": used.iloc[i]["boulder_mass"],
                "margin_pct_deq": used.iloc[i][TARGET_RAW],
                "margin_train_pct_deq": y[i],
                "loo_pred_margin_train_pct_deq": float(pred[0]),
                "loo_std_pct_deq": float(std[0]),
                "actual_class": "FALLO" if used.iloc[i][TARGET_RAW] < 0 else "ESTABLE",
                "pred_class": "FALLO" if pred[0] < 0 else "ESTABLE",
            }
        )
    loo = pd.DataFrame(rows)
    loo["abs_error_train_pct_deq"] = (
        loo["margin_train_pct_deq"] - loo["loo_pred_margin_train_pct_deq"]
    ).abs()
    return loo


def candidate_grid(pipe, used: pd.DataFrame) -> pd.DataFrame:
    H_vals = np.round(np.arange(0.175, 0.2251, 0.0025), 4)
    mu_vals = np.round(np.arange(0.56, 0.9001, 0.005), 4)
    m_vals = np.round(np.arange(0.85, 1.2501, 0.025), 4)
    grid = np.array([[H, mu, m] for H in H_vals for mu in mu_vals for m in m_vals])
    pred, std = pipe.predict(grid, return_std=True)
    out = pd.DataFrame(grid, columns=FEATURES)
    out["pred_margin_train_pct_deq"] = pred
    out["pred_std_pct_deq"] = std
    out["u_value"] = np.abs(out["pred_margin_train_pct_deq"]) / (
        out["pred_std_pct_deq"] + 1e-12
    )

    scaler = MinMaxScaler()
    scaler.fit(np.vstack([grid, used[FEATURES].to_numpy()]))
    grid_scaled = scaler.transform(grid)
    used_scaled = scaler.transform(used[FEATURES].to_numpy())
    distances = np.sqrt(((grid_scaled[:, None, :] - used_scaled[None, :, :]) ** 2).sum(axis=2))
    out["min_scaled_distance_to_existing"] = distances.min(axis=1)
    out["pred_class"] = np.where(out["pred_margin_train_pct_deq"] < 0, "FALLO", "ESTABLE")
    return out.sort_values(["u_value", "min_scaled_distance_to_existing"], ascending=[True, False])


def bracket_table(used: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for (H, m), grp in used.groupby(["dam_height", "boulder_mass"]):
        fail = grp[grp[TARGET_RAW] < 0].sort_values("friction_coefficient")
        stable = grp[grp[TARGET_RAW] >= 0].sort_values("friction_coefficient")
        max_fail = fail["friction_coefficient"].max() if len(fail) else np.nan
        min_stable = stable["friction_coefficient"].min() if len(stable) else np.nan
        width = min_stable - max_fail if not (pd.isna(max_fail) or pd.isna(min_stable)) else np.nan
        rows.append(
            {
                "dam_height": H,
                "boulder_mass": m,
                "n": len(grp),
                "fail_mu_values": ",".join(f"{v:.4f}" for v in fail["friction_coefficient"]),
                "stable_mu_values": ",".join(f"{v:.4f}" for v in stable["friction_coefficient"]),
                "max_fail_mu": max_fail,
                "min_stable_mu": min_stable,
                "bracket_width_mu": width,
            }
        )
    return pd.DataFrame(rows).sort_values(["dam_height", "boulder_mass"])


def recommended_al4(pipe) -> pd.DataFrame:
    rows = [
        ("al4_lowH_m085_mu0566", 0.175, 0.566, 0.85, "close low-H bracket between 0.560 F and 0.572 E"),
        ("al4_base_m085_mu0790", 0.200, 0.790, 0.85, "close base low-mass bracket between 0.780 F and 0.800 E"),
        ("al4_midH_m085_mu0890", 0.210, 0.890, 0.85, "close mid-H low-mass bracket between 0.880 F and 0.900 E"),
        ("al4_midH_m100_mu0748", 0.210, 0.748, 1.00, "close mid-H reference-mass bracket between 0.740 F and 0.755 E"),
        ("al4_highH_m100_mu0865", 0.225, 0.865, 1.00, "close high-H reference-mass bracket between 0.860 F and 0.870 E"),
        ("al4_highH_m115_mu0750", 0.225, 0.750, 1.15, "close high-H m*=1.15 bracket between 0.740 F and 0.760 E"),
        ("al4_highH_m125_mu0680", 0.225, 0.680, 1.25, "close high-H m*=1.25 bracket between 0.660 F and 0.700 E"),
        ("al4_base_m100_mu06808", 0.200, 0.6808, 1.00, "repeat-like fine check near legacy base transition 0.6806 F and 0.6810 E"),
    ]
    df = pd.DataFrame(
        rows,
        columns=[
            "case_id",
            "dam_height",
            "friction_coefficient",
            "boulder_mass",
            "rationale",
        ],
    )
    pred, std = pipe.predict(df[FEATURES].to_numpy(), return_std=True)
    df["pred_margin_train_pct_deq"] = pred
    df["pred_std_pct_deq"] = std
    df["u_value"] = np.abs(pred) / (std + 1e-12)
    df["boulder_rot_z"] = 0
    df["slope_inv"] = 20
    return df[
        [
            "case_id",
            "dam_height",
            "boulder_mass",
            "boulder_rot_z",
            "friction_coefficient",
            "slope_inv",
            "pred_margin_train_pct_deq",
            "pred_std_pct_deq",
            "u_value",
            "rationale",
        ]
    ]


def save_figures(used: pd.DataFrame, loo: pd.DataFrame, grid: pd.DataFrame, al4: pd.DataFrame) -> None:
    plt.rcParams.update(
        {
            "font.size": 10,
            "axes.grid": True,
            "grid.alpha": 0.22,
            "axes.spines.top": False,
            "axes.spines.right": False,
        }
    )

    # LOO validation.
    fig, ax = plt.subplots(figsize=(7, 5))
    colors = np.where(loo["actual_class"].eq("FALLO"), "#b33a3a", "#2e8b57")
    ax.scatter(loo["margin_train_pct_deq"], loo["loo_pred_margin_train_pct_deq"], c=colors, s=42, alpha=0.9)
    lo = min(loo["margin_train_pct_deq"].min(), loo["loo_pred_margin_train_pct_deq"].min()) - 1
    hi = max(loo["margin_train_pct_deq"].max(), loo["loo_pred_margin_train_pct_deq"].max()) + 1
    ax.plot([lo, hi], [lo, hi], color="#222", lw=1)
    ax.axhline(0, color="#b33a3a", ls="--", lw=1)
    ax.axvline(0, color="#b33a3a", ls="--", lw=1)
    ax.set_xlabel("g usado en entrenamiento (% d_eq, clipped)")
    ax.set_ylabel("prediccion LOO de g (% d_eq)")
    ax.set_title("Validacion leave-one-out del GP after-AL3")
    fig.savefig(FIG_DIR / "01_loo_validation.png", dpi=220, bbox_inches="tight")
    fig.savefig(FIG_DIR / "01_loo_validation.svg", bbox_inches="tight")
    plt.close(fig)

    # Actual case map and GP frontier by mass slices.
    mass_slices = [0.85, 1.00, 1.15, 1.25]
    fig, axes = plt.subplots(2, 2, figsize=(12, 9), sharex=True, sharey=True)
    for ax, m in zip(axes.ravel(), mass_slices):
        sub_grid = grid[np.isclose(grid["boulder_mass"], m)]
        pivot = sub_grid.pivot_table(
            index="dam_height",
            columns="friction_coefficient",
            values="pred_margin_train_pct_deq",
        ).sort_index()
        H = pivot.index.to_numpy()
        MU = pivot.columns.to_numpy()
        Z = pivot.to_numpy()
        cf = ax.contourf(MU, H, Z, levels=np.linspace(-10, 4, 15), cmap="RdYlGn", alpha=0.82)
        ax.contour(MU, H, Z, levels=[0], colors="black", linewidths=1.5)
        sub = used[np.isclose(used["boulder_mass"], m)]
        c = np.where(sub[TARGET_RAW] < 0, "#b33a3a", "#2e8b57")
        ax.scatter(sub["friction_coefficient"], sub["dam_height"], c=c, edgecolor="white", s=55, zorder=3)
        cand = al4[np.isclose(al4["boulder_mass"], m)]
        ax.scatter(cand["friction_coefficient"], cand["dam_height"], marker="*", s=130, c="#1f5aa6", edgecolor="white", zorder=4)
        ax.set_title(f"m* = {m:.2f}")
        ax.set_xlabel("mu")
        ax.set_ylabel("H (m)")
        ax.set_xlim(0.56, 0.90)
        ax.set_ylim(0.174, 0.226)
    fig.colorbar(cf, ax=axes.ravel().tolist(), shrink=0.88, label="g predicho = 5 - Dmax% (clipped)")
    fig.suptitle("Frontera GP after-AL3 y candidatos AL4", y=0.98)
    fig.savefig(FIG_DIR / "02_gp_frontier_by_mass.png", dpi=220, bbox_inches="tight")
    fig.savefig(FIG_DIR / "02_gp_frontier_by_mass.svg", bbox_inches="tight")
    plt.close(fig)

    # Uncertainty map.
    fig, axes = plt.subplots(2, 2, figsize=(12, 9), sharex=True, sharey=True)
    for ax, m in zip(axes.ravel(), mass_slices):
        sub_grid = grid[np.isclose(grid["boulder_mass"], m)]
        pivot = sub_grid.pivot_table(
            index="dam_height",
            columns="friction_coefficient",
            values="pred_std_pct_deq",
        ).sort_index()
        H = pivot.index.to_numpy()
        MU = pivot.columns.to_numpy()
        Z = pivot.to_numpy()
        cf = ax.contourf(MU, H, Z, levels=14, cmap="viridis", alpha=0.86)
        sub = used[np.isclose(used["boulder_mass"], m)]
        ax.scatter(sub["friction_coefficient"], sub["dam_height"], c="white", edgecolor="#333", s=35, zorder=3)
        cand = al4[np.isclose(al4["boulder_mass"], m)]
        ax.scatter(cand["friction_coefficient"], cand["dam_height"], marker="*", s=130, c="#e7b416", edgecolor="#222", zorder=4)
        ax.set_title(f"m* = {m:.2f}")
        ax.set_xlabel("mu")
        ax.set_ylabel("H (m)")
        ax.set_xlim(0.56, 0.90)
        ax.set_ylim(0.174, 0.226)
    fig.colorbar(cf, ax=axes.ravel().tolist(), shrink=0.88, label="sigma GP (% d_eq)")
    fig.suptitle("Incertidumbre del GP after-AL3", y=0.98)
    fig.savefig(FIG_DIR / "03_gp_uncertainty_by_mass.png", dpi=220, bbox_inches="tight")
    fig.savefig(FIG_DIR / "03_gp_uncertainty_by_mass.svg", bbox_inches="tight")
    plt.close(fig)

    # Margin strip by H/m.
    fig, ax = plt.subplots(figsize=(10, 6))
    for (H, m), grp in used.groupby(["dam_height", "boulder_mass"]):
        label = f"H={H:.3f}, m*={m:.2f}"
        ax.plot(
            grp.sort_values("friction_coefficient")["friction_coefficient"],
            grp.sort_values("friction_coefficient")[TARGET_RAW],
            marker="o",
            lw=1.2,
            label=label,
            alpha=0.85,
        )
    ax.axhline(0, color="#b33a3a", ls="--", lw=1.2, label="umbral g=0")
    ax.set_xlabel("mu")
    ax.set_ylabel("g = 5 - Dmax% d_eq")
    ax.set_title("Margen observado por cortes H-m*")
    ax.legend(fontsize=7, ncol=2, loc="best")
    fig.savefig(FIG_DIR / "04_observed_margin_cuts.png", dpi=220, bbox_inches="tight")
    fig.savefig(FIG_DIR / "04_observed_margin_cuts.svg", bbox_inches="tight")
    plt.close(fig)


def write_readme(summary: DatasetSummary, metrics: dict, al4: pd.DataFrame) -> None:
    text = f"""# GP H-mu-mstar after AL3

Fecha: 2026-05-18

## Objetivo

Entrenar de forma deliberada el surrogate actual de la tesis, sin usar el
reentrenamiento legacy automatico.

## Modelo

- Inputs: `H`, `mu`, `m*`.
- Target fisico: `g = 5 - Dmax(% d_eq)`.
- Interpretacion: `g > 0` estable; `g < 0` movimiento/fallo.
- Target de entrenamiento: `g` con clipping en [{TRAIN_CLIP[0]}, {TRAIN_CLIP[1]}] `% d_eq`.
- Kernel: `ConstantKernel * Matern(nu=2.5, ARD) + WhiteKernel`.
- Casos usados: {summary.n_used_rows}.
- Casos excluidos: {summary.n_excluded_rows}.

## Validacion LOO

- MAE train target: {metrics['loo_mae_train_pct_deq']:.3f} `% d_eq`.
- RMSE train target: {metrics['loo_rmse_train_pct_deq']:.3f} `% d_eq`.
- Accuracy clase LOO: {metrics['loo_class_accuracy']:.3f}.
- Falsos estables LOO: {metrics['loo_false_stable']}.
- Falsos fallos LOO: {metrics['loo_false_fail']}.

## Archivos

- `dataset_master.csv`: todos los casos leidos desde exports.
- `dataset_used.csv`: casos oficiales dentro del dominio usados para GP.
- `brackets_by_h_mstar.csv`: brackets observados por corte H-m*.
- `loo_predictions.csv`: validacion leave-one-out.
- `candidate_grid_ranked.csv`: grilla candidata ordenada por U-value.
- `al4_candidates.csv`: candidatos recomendados para siguiente lote.
- `validation_metrics.json`: metricas y kernel final.
- `figures/`: figuras de validacion, frontera e incertidumbre.
- Modelo: `{MODEL_PATH.relative_to(PROJECT_ROOT).as_posix()}`.

## AL4 recomendado

```csv
case_id,dam_height,boulder_mass,boulder_rot_z,friction_coefficient,slope_inv
"""
    for _, row in al4.iterrows():
        text += (
            f"{row['case_id']},{row['dam_height']:.3f},{row['boulder_mass']:.2f},0,"
            f"{row['friction_coefficient']:.3f},20\n"
        )
    text += "```\n"
    (OUT_DIR / "README.md").write_text(text, encoding="utf-8")


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    FIG_DIR.mkdir(parents=True, exist_ok=True)
    MODEL_DIR.mkdir(parents=True, exist_ok=True)

    master = build_master_dataset()
    used = master[master["used_for_gp"]].copy()
    used = used.sort_values(["dam_height", "boulder_mass", "friction_coefficient", "batch", "case_id"])

    if len(used) < 20:
        raise RuntimeError(f"Too few GP points after filtering: {len(used)}")

    X = used[FEATURES].to_numpy(dtype=float)
    y = used[TARGET_TRAIN].to_numpy(dtype=float)

    pipe = fit_pipeline(X, y)
    loo = loo_predictions(X, y, used)
    grid = candidate_grid(pipe, used)
    brackets = bracket_table(used)
    al4 = recommended_al4(pipe)

    y_true = loo["margin_train_pct_deq"].to_numpy()
    y_pred = loo["loo_pred_margin_train_pct_deq"].to_numpy()
    actual_class = loo["actual_class"].to_numpy()
    pred_class = loo["pred_class"].to_numpy()

    metrics = {
        "analysis_id": ANALYSIS_ID,
        "n_used": int(len(used)),
        "n_master": int(len(master)),
        "n_fail": int((used[TARGET_RAW] < 0).sum()),
        "n_stable": int((used[TARGET_RAW] >= 0).sum()),
        "loo_mae_train_pct_deq": float(mean_absolute_error(y_true, y_pred)),
        "loo_rmse_train_pct_deq": float(mean_squared_error(y_true, y_pred, squared=False)),
        "loo_class_accuracy": float(accuracy_score(actual_class, pred_class)),
        "loo_false_stable": int(((actual_class == "FALLO") & (pred_class == "ESTABLE")).sum()),
        "loo_false_fail": int(((actual_class == "ESTABLE") & (pred_class == "FALLO")).sum()),
        "kernel": str(pipe.named_steps["gaussianprocessregressor"].kernel_),
        "domain_bounds": DOMAIN_BOUNDS,
        "train_clip": TRAIN_CLIP,
        "features": FEATURES,
        "target_raw": TARGET_RAW,
        "target_train": TARGET_TRAIN,
    }

    summary = DatasetSummary(
        analysis_id=ANALYSIS_ID,
        n_master_rows=len(master),
        n_used_rows=len(used),
        n_excluded_rows=len(master) - len(used),
        n_fail=metrics["n_fail"],
        n_stable=metrics["n_stable"],
        domain_bounds=DOMAIN_BOUNDS,
        train_clip=TRAIN_CLIP,
        features=FEATURES,
        target_raw=TARGET_RAW,
        target_train=TARGET_TRAIN,
    )

    master.to_csv(OUT_DIR / "dataset_master.csv", index=False)
    used.to_csv(OUT_DIR / "dataset_used.csv", index=False)
    brackets.to_csv(OUT_DIR / "brackets_by_h_mstar.csv", index=False)
    loo.to_csv(OUT_DIR / "loo_predictions.csv", index=False)
    grid.to_csv(OUT_DIR / "candidate_grid_ranked.csv", index=False)
    al4.to_csv(OUT_DIR / "al4_candidates.csv", index=False)
    al4[
        [
            "case_id",
            "dam_height",
            "boulder_mass",
            "boulder_rot_z",
            "friction_coefficient",
            "slope_inv",
        ]
    ].to_csv(OUT_DIR / "al4_matrix_recommended.csv", index=False)

    (OUT_DIR / "dataset_summary.json").write_text(
        json.dumps(asdict(summary), indent=2), encoding="utf-8"
    )
    (OUT_DIR / "validation_metrics.json").write_text(
        json.dumps(metrics, indent=2), encoding="utf-8"
    )

    save_figures(used, loo, grid, al4)

    with MODEL_PATH.open("wb") as f:
        pickle.dump(
            {
                "analysis_id": ANALYSIS_ID,
                "model": pipe,
                "features": FEATURES,
                "target_raw": TARGET_RAW,
                "target_train": TARGET_TRAIN,
                "domain_bounds": DOMAIN_BOUNDS,
                "train_clip": TRAIN_CLIP,
                "metrics": metrics,
                "dataset_used": used[["case_id", "batch"] + FEATURES + [TARGET_RAW, TARGET_TRAIN]].copy(),
            },
            f,
        )

    write_readme(summary, metrics, al4)

    print(f"Analysis written to: {OUT_DIR}")
    print(f"Model written to: {MODEL_PATH}")
    print(json.dumps(metrics, indent=2))


if __name__ == "__main__":
    main()
