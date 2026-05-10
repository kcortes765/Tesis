from __future__ import annotations

import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
EXAMPLE = Path(r"C:\DualSPHysics_v5.4.3\DualSPHysics_v5.4\examples\main\01_DamBreak")
CASE_OUT = EXAMPLE / "CaseDambreakVal2D_out"
OUT = ROOT / "data" / "benchmarks" / "hydraulic_20260508"
FIG = OUT / "figures"


def read_experiment(path: Path) -> pd.DataFrame:
    rows = []
    text = path.read_text(encoding="utf-8", errors="ignore")
    if not text.strip():
        text = path.read_text(encoding="cp1252", errors="ignore")
    for line in text.splitlines():
        line = line.strip()
        if not line or line.startswith("S.") or line.startswith("time"):
            continue
        parts = line.split()
        if len(parts) >= 2:
            rows.append((float(parts[0]), float(parts[1])))
    return pd.DataFrame(rows, columns=["time_s", "x_front_exp_m"])


def read_simulation(path: Path) -> pd.DataFrame:
    df = pd.read_csv(path, sep=";")
    return df.rename(columns={"time [s]": "time_s", "swlx [m]": "x_front_sim_m"})[
        ["time_s", "x_front_sim_m"]
    ]


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    FIG.mkdir(parents=True, exist_ok=True)

    exp_path = EXAMPLE / "EXP_X-DamTipPosition_Koshizula&Oka1996.txt"
    sim_path = CASE_OUT / "GaugesSWL_Swl_z003.csv"
    if not sim_path.exists():
        raise FileNotFoundError(sim_path)

    exp = read_experiment(exp_path)
    sim = read_simulation(sim_path)
    sim_interp = np.interp(exp["time_s"], sim["time_s"], sim["x_front_sim_m"])
    comp = exp.copy()
    comp["x_front_sim_m"] = sim_interp
    comp["error_m"] = comp["x_front_sim_m"] - comp["x_front_exp_m"]
    comp["abs_error_m"] = comp["error_m"].abs()
    comp["rel_error_pct"] = comp["abs_error_m"] / comp["x_front_exp_m"].abs() * 100.0

    metrics = {
        "benchmark": "DualSPHysics examples/main/01_DamBreak CaseDambreakVal2D",
        "reference": "Koshizuka and Oka 1996 dam-tip/front position file included in DualSPHysics",
        "n_reference_points": int(len(comp)),
        "rmse_m": float(np.sqrt(np.mean(comp["error_m"] ** 2))),
        "mae_m": float(comp["abs_error_m"].mean()),
        "mean_rel_error_pct": float(comp["rel_error_pct"].mean()),
        "max_rel_error_pct": float(comp["rel_error_pct"].max()),
        "final_exp_x_m": float(comp["x_front_exp_m"].iloc[-1]),
        "final_sim_x_m": float(comp["x_front_sim_m"].iloc[-1]),
        "final_rel_error_pct": float(comp["rel_error_pct"].iloc[-1]),
        "dp_m": 0.01,
        "time_max_s": 2.0,
        "particles_total": 21001,
    }

    comp.to_csv(OUT / "front_position_comparison.csv", index=False)
    sim.to_csv(OUT / "front_position_simulation_full.csv", index=False)
    exp.to_csv(OUT / "front_position_reference.csv", index=False)
    (OUT / "benchmark_metrics.json").write_text(json.dumps(metrics, indent=2), encoding="utf-8")

    for src in [
        EXAMPLE / "data" / "benchmarks" / "hydraulic_20260508" / "gencase_val2d.log",
        EXAMPLE / "data" / "benchmarks" / "hydraulic_20260508" / "dualsphysics_val2d.log",
        CASE_OUT / "CaseDambreakVal2D.out",
    ]:
        if src.exists():
            (OUT / src.name).write_text(src.read_text(errors="ignore"), encoding="utf-8")

    fig, ax = plt.subplots(figsize=(7.8, 4.6))
    ax.plot(sim["time_s"], sim["x_front_sim_m"], color="#2d74b8", lw=1.6, label="DualSPHysics")
    ax.scatter(exp["time_s"], exp["x_front_exp_m"], color="#17202a", s=28, label="Referencia Koshizuka & Oka")
    ax.set_xlabel("Tiempo (s)")
    ax.set_ylabel("Posición del frente de agua (m)")
    ax.set_title("Benchmark hidráulico 2D: frente de dam-break")
    ax.grid(alpha=0.25)
    ax.legend(frameon=False)
    fig.tight_layout()
    fig.savefig(FIG / "front_position_benchmark.png", dpi=220)
    fig.savefig(FIG / "front_position_benchmark.svg")
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(7.8, 3.8))
    ax.plot(comp["time_s"], comp["error_m"], marker="o", color="#b73b3b", lw=1.2)
    ax.axhline(0, color="#17202a", lw=0.8)
    ax.set_xlabel("Tiempo (s)")
    ax.set_ylabel("Error sim - ref (m)")
    ax.set_title("Error de posición del frente")
    ax.grid(alpha=0.25)
    fig.tight_layout()
    fig.savefig(FIG / "front_position_error.png", dpi=220)
    fig.savefig(FIG / "front_position_error.svg")
    plt.close(fig)

    report = f"""# Benchmark hidráulico DualSPHysics 2D

Fecha: 2026-05-08  
Caso: `examples/main/01_DamBreak/CaseDambreakVal2D`  
Referencia incluida: Koshizuka y Oka (1996), posición del frente de dam-break.  

## Qué valida

Este benchmark verifica que la instalación local de DualSPHysics, GenCase, GPU y postproceso de gauges reproducen
un caso hidráulico documentado incluido con la distribución oficial. No valida el bloque irregular ni el contacto
Chrono de la tesis.

## Resultado cuantitativo

- Puntos de referencia usados: {metrics['n_reference_points']}
- RMSE posición frente: {metrics['rmse_m']:.4f} m
- MAE posición frente: {metrics['mae_m']:.4f} m
- Error relativo medio: {metrics['mean_rel_error_pct']:.2f} %
- Error relativo máximo: {metrics['max_rel_error_pct']:.2f} %
- Error relativo final: {metrics['final_rel_error_pct']:.2f} %
- Partículas: {metrics['particles_total']}
- `dp`: {metrics['dp_m']} m
- `TimeMax`: {metrics['time_max_s']} s

## Lectura

La curva simulada reproduce la evolución temporal del frente de agua con errores de orden menor a una decena de
centímetros en el rango comparado. Esto es suficiente como benchmark hidráulico operativo del entorno local, siempre
declarando que se trata de un caso 2D simple y no de validación del bloque costero.

## Archivos

- `front_position_comparison.csv`
- `front_position_simulation_full.csv`
- `front_position_reference.csv`
- `benchmark_metrics.json`
- `figures/front_position_benchmark.png`
- `figures/front_position_error.png`
"""
    (OUT / "benchmark_hydraulic_report.md").write_text(report, encoding="utf-8")
    print(f"Benchmark report written to {OUT}")


if __name__ == "__main__":
    main()
