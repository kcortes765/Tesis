from __future__ import annotations

import json
import math
from dataclasses import dataclass
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "data" / "analytic_comparison" / "20260508_preproduction"
FIG = OUT / "figures"

PILOT = ROOT / "exports" / "pilot_productivo_20260501" / "pilot_summary.csv"
ROUND2 = ROOT / "data" / "results" / "results_round2.csv"

G = 9.81
RHO_W = 1000.0

# Geometry constants from the corrected thesis setup. These remain approximate
# because the analytical model is only a low-order physical consistency check.
D_EQ = 0.100421
BLOCK_VOLUME_M3 = 5.30e-4
BLOCK_HEIGHT_M = 0.0429
BLOCK_WIDTH_M = 0.2100
BLOCK_LENGTH_M = 0.1706


@dataclass(frozen=True)
class MobilityScenario:
    name: str
    cd: float
    cl: float
    area_drag_factor: float
    area_lift_factor: float
    slope_assist: bool


SCENARIOS = [
    MobilityScenario("lower", cd=1.0, cl=0.0, area_drag_factor=0.75, area_lift_factor=0.0, slope_assist=False),
    MobilityScenario("central", cd=1.5, cl=0.2, area_drag_factor=1.0, area_lift_factor=0.5, slope_assist=False),
    MobilityScenario("upper", cd=2.0, cl=0.6, area_drag_factor=1.25, area_lift_factor=1.0, slope_assist=True),
]


def read_optional_csv(path: Path) -> pd.DataFrame:
    if not path.exists():
        return pd.DataFrame()
    return pd.read_csv(path)


def normalize_pilot(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty:
        return df
    out = pd.DataFrame(
        {
            "source": "pilot",
            "case_id": df["case_id"],
            "dp": df.get("dp", 0.003),
            "H_m": df["dam_height"],
            "mass_kg": df["boulder_mass"],
            "mu": df["friction_coefficient"],
            "slope_inv": df["slope_inv"],
            "max_disp_m": df["max_displacement_m"],
            "disp_pct_deq": df["disp_pct_deq"],
            "max_rotation_deg": df["max_rotation_deg"],
            "block_velocity_mps": df["max_velocity_ms"],
            "flow_velocity_mps": df["max_flow_velocity_ms"],
            "water_height_m": df["max_water_height_m"],
            "sph_force_N": df["max_sph_force_N"],
            "contact_force_N": df["max_contact_force_N"],
            "criterion_class": df["criterion_class"],
        }
    )
    return out


def normalize_round2(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty:
        return df
    max_disp_m = df["max_disp_mm"] / 1000.0
    out = pd.DataFrame(
        {
            "source": "round2",
            "case_id": df["case_id"],
            "dp": df.get("dp", 0.004),
            "H_m": df["dam_h"],
            "mass_kg": df["mass"],
            "mu": df["friction"],
            "slope_inv": df["slope_inv"],
            "max_disp_m": max_disp_m,
            "disp_pct_deq": max_disp_m / D_EQ * 100.0,
            "max_rotation_deg": df["max_rot_deg"],
            "block_velocity_mps": df["max_vel_mps"],
            "flow_velocity_mps": df["flow_vel_mps"],
            "water_height_m": df["water_h_m"],
            "sph_force_N": df["sph_force_N"],
            "contact_force_N": df["contact_force_N"],
            "criterion_class": df["estado"],
        }
    )
    return out


def analytical_terms(row: pd.Series, scenario: MobilityScenario) -> dict[str, float | str | bool]:
    u = max(float(row["flow_velocity_mps"]), 0.0)
    h = max(float(row["water_height_m"]), 0.0)
    mass = float(row["mass_kg"])
    mu = float(row["mu"])
    slope_inv = float(row["slope_inv"]) if float(row["slope_inv"]) > 0 else 20.0
    beta = math.atan(1.0 / slope_inv)

    submerged_fraction = min(max(h / BLOCK_HEIGHT_M, 0.0), 1.0)
    submerged_volume = BLOCK_VOLUME_M3 * submerged_fraction
    effective_weight = max((mass - RHO_W * submerged_volume) * G, 0.05 * mass * G)

    projected_depth = min(h, BLOCK_HEIGHT_M)
    area_drag = max(BLOCK_WIDTH_M * projected_depth * scenario.area_drag_factor, 1e-6)
    area_lift = BLOCK_WIDTH_M * BLOCK_LENGTH_M * submerged_fraction * scenario.area_lift_factor

    f_drag = 0.5 * RHO_W * scenario.cd * area_drag * u**2
    f_lift = 0.5 * RHO_W * scenario.cl * area_lift * u**2
    slope_force = effective_weight * math.sin(beta) if scenario.slope_assist else 0.0
    normal = max(effective_weight * math.cos(beta) - f_lift, 0.05 * mass * G)
    resistance = max(mu * normal, 1e-9)
    drive = f_drag + slope_force
    psi = drive / resistance

    return {
        f"psi_{scenario.name}": psi,
        f"drag_N_{scenario.name}": f_drag,
        f"lift_N_{scenario.name}": f_lift,
        f"resistance_N_{scenario.name}": resistance,
        f"effective_weight_N_{scenario.name}": effective_weight,
    }


def build_summary() -> pd.DataFrame:
    frames = [
        normalize_pilot(read_optional_csv(PILOT)),
        normalize_round2(read_optional_csv(ROUND2)),
    ]
    df = pd.concat([f for f in frames if not f.empty], ignore_index=True)
    if df.empty:
        raise FileNotFoundError("No se encontraron CSV de piloto ni round2.")

    for scenario in SCENARIOS:
        terms = df.apply(lambda row: pd.Series(analytical_terms(row, scenario)), axis=1)
        df = pd.concat([df, terms], axis=1)

    df["psi_band_min"] = df["psi_lower"]
    df["psi_band_max"] = df["psi_upper"]
    df["psi_flag"] = np.select(
        [df["psi_upper"] < 1.0, df["psi_lower"] > 1.0],
        ["analiticamente_resistente", "analiticamente_movil"],
        default="zona_intermedia",
    )
    df["flow_data_flag"] = np.select(
        [
            df["flow_velocity_mps"] <= 0.01,
            df["water_height_m"] <= 0.01,
        ],
        [
            "sin_velocidad_flujo_util",
            "sin_altura_agua_util",
        ],
        default="OK",
    )
    df["sph_fail"] = df["criterion_class"].astype(str).str.upper().eq("FALLO")
    df["analytical_central_mobile"] = df["psi_central"] > 1.0
    df["strong_contradiction"] = (
        (df["sph_fail"] & (df["psi_band_max"] < 1.0))
        | (~df["sph_fail"] & (df["psi_band_min"] > 1.0))
    )
    return df


def save_plot_psi_vs_displacement(df: pd.DataFrame) -> None:
    plot_df = df[df["flow_data_flag"].eq("OK")].copy()
    fig, ax = plt.subplots(figsize=(8.6, 5.4))
    colors = plot_df["criterion_class"].map({"FALLO": "#b73b3b", "ESTABLE": "#2f7d4f"}).fillna("#536171")
    yerr = np.vstack([
        plot_df["psi_central"] - plot_df["psi_band_min"],
        plot_df["psi_band_max"] - plot_df["psi_central"],
    ])
    ax.errorbar(
        plot_df["psi_central"],
        plot_df["disp_pct_deq"],
        xerr=yerr,
        fmt="none",
        ecolor="#aab4c0",
        alpha=0.8,
        capsize=3,
        zorder=1,
    )
    for klass, label, color in [
        ("ESTABLE", "SPH estable", "#2f7d4f"),
        ("FALLO", "SPH falla", "#b73b3b"),
    ]:
        part = plot_df[plot_df["criterion_class"].eq(klass)]
        ax.scatter(
            part["psi_central"],
            part["disp_pct_deq"],
            s=58,
            c=color,
            edgecolor="white",
            label=label,
            zorder=2,
        )
    selected = plot_df[
        (plot_df["disp_pct_deq"].between(3, 8))
        | (plot_df["disp_pct_deq"].ge(plot_df["disp_pct_deq"].quantile(0.92)))
    ]
    for idx, (_, row) in enumerate(selected.iterrows()):
        offset_y = 7 if idx % 2 == 0 else -11
        ax.annotate(
            row["case_id"],
            (row["psi_central"], row["disp_pct_deq"]),
            xytext=(5, offset_y),
            textcoords="offset points",
            fontsize=7,
            color="#17202a",
        )
    ax.axvline(1.0, color="#17202a", ls="--", lw=1.0, label="Psi=1")
    ax.axhline(5.0, color="#b73b3b", ls="--", lw=1.0, label="umbral SPH 5% d_eq")
    ax.set_xscale("log")
    ax.set_yscale("log")
    ax.set_ylim(0.8, max(20, plot_df["disp_pct_deq"].max() * 1.45))
    ax.set_xlabel("Índice de movilidad analítico Psi (central, con banda)")
    ax.set_ylabel("Desplazamiento máximo SPH (% d_eq, escala log)")
    ax.set_title("Comparación analítica preliminar: movilidad vs desplazamiento SPH")
    ax.grid(alpha=0.22)
    ax.legend(frameon=False, fontsize=8, loc="upper left")
    fig.tight_layout()
    fig.savefig(FIG / "psi_vs_displacement.png", dpi=220)
    fig.savefig(FIG / "psi_vs_displacement.svg")
    plt.close(fig)


def save_plot_ordered_cases(df: pd.DataFrame) -> None:
    plot_df = df[df["flow_data_flag"].eq("OK")].sort_values("psi_central")
    fig, ax = plt.subplots(figsize=(9.0, max(4.0, 0.32 * len(plot_df))))
    y = np.arange(len(plot_df))
    colors = plot_df["criterion_class"].map({"FALLO": "#b73b3b", "ESTABLE": "#2f7d4f"}).fillna("#536171")
    ax.barh(y, plot_df["psi_central"], color=colors, alpha=0.88)
    ax.axvline(1.0, color="#17202a", ls="--", lw=1.0)
    ax.set_yticks(y, plot_df["case_id"])
    ax.set_xscale("log")
    ax.set_xlabel("Psi central")
    ax.set_title("Casos ordenados por movilidad analítica preliminar")
    ax.grid(axis="x", alpha=0.22)
    fig.tight_layout()
    fig.savefig(FIG / "ordered_mobility_cases.png", dpi=220)
    fig.savefig(FIG / "ordered_mobility_cases.svg")
    plt.close(fig)


def write_report(df: pd.DataFrame) -> None:
    usable = df[df["flow_data_flag"].eq("OK")]
    total = len(df)
    usable_n = len(usable)
    stable = usable[usable["criterion_class"].eq("ESTABLE")]
    fail = usable[usable["criterion_class"].eq("FALLO")]
    contradictions = usable[usable["strong_contradiction"]]
    robust_mobile_fail = fail[fail["psi_band_min"] > 1.0]
    possible_resistant_stable = stable[stable["psi_band_min"] < 1.0]

    report = f"""# Comparación analítica preliminar preproducción

Fecha: 2026-05-08  
Datos usados: piloto productivo liviano y `data/results/results_round2.csv` si existe.  
Objetivo: control de coherencia física de bajo orden, no validación exacta.

## Resumen

- Casos consolidados: {total}
- Casos con velocidad de flujo útil para la comparación: {usable_n}
- Contradicciones fuertes entre banda analítica y clase SPH: {len(contradictions)}/{usable_n}
- Fallos SPH con banda completamente móvil (`Psi_lower > 1`): {len(robust_mobile_fail)}/{len(fail)}
- Estables SPH con resistencia posible en la banda (`Psi_lower < 1`): {len(possible_resistant_stable)}/{len(stable)}
- Mediana `Psi_central` en casos ESTABLE: {stable['psi_central'].median() if len(stable) else float('nan'):.3g}
- Mediana `Psi_central` en casos FALLO: {fail['psi_central'].median() if len(fail) else float('nan'):.3g}

## Lectura técnica

El índice `Psi` compara una fuerza motriz analítica aproximada contra una resistencia friccional efectiva:

```text
Psi = F_drive / F_resist
```

La lectura de referencia es:

- `Psi < 1`: resistencia mayor que forzante;
- `Psi > 1`: condición favorable al movimiento bajo los coeficientes asumidos;
- banda `lower-central-upper`: sensibilidad a coeficientes de arrastre, sustentación, área proyectada y efecto de pendiente.

La banda es más importante que el valor central. Si un caso estable tiene `Psi_central > 1`, pero `Psi_lower < 1`,
eso no se interpreta como contradicción fuerte: significa que con coeficientes conservadores todavía hay resistencia
analítica suficiente. La comparación se usa para detectar órdenes de magnitud incompatibles, no para reclasificar casos.

## Límites

Esta comparación no valida numéricamente el desplazamiento del bloque. Usa coeficientes hidráulicos no calibrados,
áreas proyectadas aproximadas y velocidades de gauge/postproceso. Su función es verificar coherencia de tendencia:
los casos con mayor movilidad analítica deberían tender a mostrar mayor desplazamiento o clase de falla.

## Advertencias de datos

Los casos con `flow_velocity_mps <= 0.01` o `water_height_m <= 0.01` se mantienen en el CSV maestro, pero no se usan
para la comparación principal, porque el índice analítico depende de una velocidad y una submergencia representativas.

## Archivos generados

- `analytic_mobility_summary.csv`
- `analytic_parameters.json`
- `figures/psi_vs_displacement.png`
- `figures/ordered_mobility_cases.png`

"""
    (OUT / "analytic_comparison_report.md").write_text(report, encoding="utf-8")


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    FIG.mkdir(parents=True, exist_ok=True)
    df = build_summary()
    df.to_csv(OUT / "analytic_mobility_summary.csv", index=False)
    params = {
        "D_EQ": D_EQ,
        "BLOCK_VOLUME_M3": BLOCK_VOLUME_M3,
        "BLOCK_HEIGHT_M": BLOCK_HEIGHT_M,
        "BLOCK_WIDTH_M": BLOCK_WIDTH_M,
        "BLOCK_LENGTH_M": BLOCK_LENGTH_M,
        "RHO_W": RHO_W,
        "G": G,
        "scenarios": [scenario.__dict__ for scenario in SCENARIOS],
    }
    (OUT / "analytic_parameters.json").write_text(json.dumps(params, indent=2), encoding="utf-8")
    save_plot_psi_vs_displacement(df)
    save_plot_ordered_cases(df)
    write_report(df)
    print(f"Analytical comparison written to {OUT}")


if __name__ == "__main__":
    main()
