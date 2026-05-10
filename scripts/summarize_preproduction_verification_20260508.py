from __future__ import annotations

import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
D_EQ = 0.100421

BENCH = ROOT / "data" / "benchmarks" / "hydraulic_20260508"
ANALYTIC = ROOT / "data" / "analytic_comparison" / "20260508_preproduction"
CONTACT_CSV = ROOT / "data" / "results" / "contact_sanity_lowwater_20260508.csv"
CONTACT_FAIL_CSV = ROOT / "data" / "results" / "contact_sanity_noflow_20260508.csv"
CONTACT_TEMP = ROOT / "data" / "results" / "contact_sanity_lowwater_20260508_temporal"
OUT = ROOT / "data" / "verification_preproduction_20260508"
FIG = OUT / "figures"
DOCS = ROOT / "docs"


def read_semicolon(path: Path) -> pd.DataFrame:
    return pd.read_csv(path, sep=";")


def contact_figures() -> dict:
    OUT.mkdir(parents=True, exist_ok=True)
    FIG.mkdir(parents=True, exist_ok=True)

    summary = read_semicolon(CONTACT_CSV).iloc[0].to_dict()
    exchange_path = next(CONTACT_TEMP.glob("*_exchange.csv"))
    forces_path = next(CONTACT_TEMP.glob("*_forces.csv"))
    exchange = read_semicolon(exchange_path)
    forces = read_semicolon(forces_path)

    x0 = float(exchange["fcenter.x [m]"].iloc[0])
    y0 = float(exchange["fcenter.y [m]"].iloc[0])
    z0 = float(exchange["fcenter.z [m]"].iloc[0])
    displacement = np.sqrt(
        (exchange["fcenter.x [m]"] - x0) ** 2
        + (exchange["fcenter.y [m]"] - y0) ** 2
        + (exchange["fcenter.z [m]"] - z0) ** 2
    )
    displacement_pct = displacement / D_EQ * 100.0
    speed = np.sqrt(
        exchange["fvel.x [m/s]"] ** 2
        + exchange["fvel.y [m/s]"] ** 2
        + exchange["fvel.z [m/s]"] ** 2
    )
    contact_force = np.sqrt(forces["cfx"] ** 2 + forces["cfy"] ** 2 + forces["cfz"] ** 2)
    transient_end = 0.56
    post_mask = exchange["time [s]"] >= transient_end
    post_force_mask = forces["Time"] >= transient_end
    post_disp_max = float(displacement_pct[post_mask].max())
    post_speed_max = float(speed[post_mask].max())
    post_force_max = float(contact_force[post_force_mask].max())

    fig, axes = plt.subplots(3, 1, figsize=(9.2, 7.4), sharex=True)
    for axis in axes:
        axis.axvspan(0.5, transient_end, color="#f1c27d", alpha=0.18, lw=0)
        axis.grid(alpha=0.22)

    axes[0].plot(exchange["time [s]"], displacement_pct, color="#2d74b8", lw=1.5)
    axes[0].axhline(5, color="#b73b3b", ls="--", lw=1.0, label="umbral 5% d_eq")
    axes[0].set_ylabel("Desplazamiento (% d_eq)")
    axes[0].legend(frameon=False, loc="upper right")
    axes[0].text(
        0.985,
        0.18,
        f"max. post-transiente: {post_disp_max:.2f}% d_eq",
        transform=axes[0].transAxes,
        ha="right",
        va="bottom",
        fontsize=8,
        color="#536171",
    )

    axes[1].plot(exchange["time [s]"], speed, color="#2f8f5b", lw=1.2)
    axes[1].set_ylabel("Velocidad bloque (m/s)")
    axes[1].text(
        0.985,
        0.82,
        f"después de 0.56 s: max {post_speed_max:.4f} m/s",
        transform=axes[1].transAxes,
        ha="right",
        va="top",
        fontsize=8,
        color="#536171",
    )

    axes[2].plot(forces["Time"], contact_force, color="#9a6a1f", lw=1.0)
    axes[2].set_yscale("symlog", linthresh=1.0)
    axes[2].set_ylabel("Fuerza contacto (N)")
    axes[2].set_xlabel("Tiempo (s)")
    axes[2].text(
        0.985,
        0.82,
        f"pico inicial = acomodo; post-transiente max {post_force_max:.1f} N",
        transform=axes[2].transAxes,
        ha="right",
        va="top",
        fontsize=8,
        color="#536171",
    )
    axes[2].text(0.505, 0.08, "acomodo inicial", transform=axes[2].get_xaxis_transform(), fontsize=8, color="#8a5a1f")
    axes[2].set_xlim(0.5, 2.0)

    fig.suptitle("Sanity de contacto: separar acomodo inicial de movimiento sostenido", y=0.985)
    fig.tight_layout(rect=[0, 0, 1, 0.97])
    fig.savefig(FIG / "contact_sanity_timeseries.png", dpi=220)
    fig.savefig(FIG / "contact_sanity_timeseries.svg")
    plt.close(fig)

    noflow_note = ""
    if CONTACT_FAIL_CSV.exists():
        fail = read_semicolon(CONTACT_FAIL_CSV).iloc[0].to_dict()
        noflow_note = str(fail.get("error", "")).strip()

    contact_report = f"""# Sanity de contacto bloque-suelo

Fecha: 2026-05-08  
Caso aceptado: `contact_sanity_lowwater_20260508_dp0003`  
Intento sin agua: `contact_sanity_noflow_20260508_dp0003`

## Objetivo

Verificar que el bloque no inicia un movimiento relevante por una condicion inicial defectuosa,
interpenetracion, apoyo incorrecto o contacto bloque-suelo inestable. Esta prueba no busca representar
un tsunami; busca aislar el contacto.

## Diseno

- `dp = 0.003 m`
- `time_max = 2 s`
- `dam_height = 0.01 m`
- bloque en posicion oficial sobre playa 1:20
- `friction = 0.68`
- `reference_time_s = 0.5`

Primero se intento `dam_height = 0`, pero DualSPHysics no acepta un caso sin particulas de fluido:

```text
{noflow_note}
```

Por eso se uso una columna minima de 1 cm, lejos del bloque y con corrida corta. Los gauges del bloque
reportaron velocidad de flujo y altura de agua maximas iguales a cero en el entorno del bloque.

## Resultado

- Estado: {summary.get('status')}
- Desplazamiento maximo: {float(summary['max_displacement_m']):.6f} m
- Desplazamiento relativo: {float(summary['max_displacement_m']) / D_EQ * 100:.2f} % de `d_eq`
- Umbral de movimiento usado en tesis: 5.00 % de `d_eq`
- Rotacion maxima: {float(summary['max_rotation_deg']):.2f} deg
- Velocidad maxima del bloque: {float(summary['max_velocity_ms']):.4f} m/s
- Fuerza SPH maxima: {float(summary['max_sph_force_N']):.4f} N
- Fuerza de contacto maxima: {float(summary['max_contact_force_N']):.2f} N
- Velocidad de flujo en gauge representativo: {float(summary['max_flow_velocity_ms']):.4f} m/s
- Altura/cota de agua en gauge representativo: {float(summary['max_water_height_m']):.4f} m
- Particulas: {int(summary['n_particles'])}
- Tiempo de corrida: {float(summary['tiempo_min']):.1f} min

## Lectura

El bloque no supera el umbral de desplazamiento y no recibe forzante SPH en el entorno del bloque. El pequeno
desplazamiento observado queda como acomodacion/contacto inicial bajo Chrono y permanece muy por debajo del
criterio de movimiento. Esto valida el setup inicial bloque-suelo para continuar con casos hidraulicos.

## Limite

No valida el movimiento bajo impacto ni el acoplamiento fluido-bloque durante eventos fuertes. Solo prueba que
la condicion inicial y el contacto no generan una falla espuria por si solos.
"""
    (OUT / "contact_sanity_report.md").write_text(contact_report, encoding="utf-8")
    return summary


def consolidated_report(contact: dict) -> None:
    bench_metrics = json.loads((BENCH / "benchmark_metrics.json").read_text(encoding="utf-8"))
    analytic_summary = pd.read_csv(ANALYTIC / "analytic_mobility_summary.csv")
    usable = analytic_summary[analytic_summary["flow_data_flag"] == "OK"]
    failures = usable[usable["criterion_class"] == "FALLO"]
    stable = usable[usable["criterion_class"] == "ESTABLE"]
    contradictions = int(usable["strong_contradiction"].sum())

    report = f"""# Verificacion preproduccion sin experimento real

Fecha: 2026-05-08  
Objetivo: aumentar la defensibilidad antes de la campana productiva con tres controles independientes:
benchmark hidraulico, sanity de contacto y comparacion analitica preliminar.

## 1. Benchmark SPH/DualSPHysics

Se ejecuto el caso oficial `examples/main/01_DamBreak/CaseDambreakVal2D` de DualSPHysics v5.4.3 y se comparo
la posicion del frente de agua contra la referencia experimental incluida de Koshizuka y Oka (1996).

Resultado:

- puntos de referencia: {bench_metrics['n_reference_points']}
- RMSE posicion del frente: {bench_metrics['rmse_m']:.4f} m
- MAE posicion del frente: {bench_metrics['mae_m']:.4f} m
- error relativo medio: {bench_metrics['mean_rel_error_pct']:.2f} %
- error relativo maximo: {bench_metrics['max_rel_error_pct']:.2f} %
- error relativo final: {bench_metrics['final_rel_error_pct']:.2f} %
- particulas: {bench_metrics['particles_total']}
- `dp`: {bench_metrics['dp_m']} m

Lectura: valida que la instalacion local, GenCase, DualSPHysics, GPU y postproceso de gauges reproducen un caso
hidraulico conocido. No valida el bloque irregular ni Chrono.

Archivos:

- `data/benchmarks/hydraulic_20260508/benchmark_hydraulic_report.md`
- `data/benchmarks/hydraulic_20260508/figures/front_position_benchmark.png`
- `data/benchmarks/hydraulic_20260508/figures/front_position_error.png`

## 2. Chequeo de contacto bloque-suelo

Se intento un caso sin agua (`dam_height=0`), pero DualSPHysics no acepta ausencia total de particulas de fluido.
Luego se ejecuto una columna minima de 1 cm, corta y lejos del bloque, para mantener el solver activo sin impacto
hidraulico sobre el bloque.

Resultado:

- caso: `contact_sanity_lowwater_20260508_dp0003`
- `dp`: 0.003 m
- desplazamiento maximo: {float(contact['max_displacement_m']):.6f} m
- desplazamiento relativo: {float(contact['max_displacement_m']) / D_EQ * 100:.2f} % de `d_eq`
- umbral de movimiento: 5.00 % de `d_eq`
- rotacion maxima: {float(contact['max_rotation_deg']):.2f} deg
- fuerza SPH maxima: {float(contact['max_sph_force_N']):.4f} N
- flujo maximo en gauge del bloque: {float(contact['max_flow_velocity_ms']):.4f} m/s
- agua maxima en gauge del bloque: {float(contact['max_water_height_m']):.4f} m

Lectura: el bloque no se mueve por mala condicion inicial o contacto espurio. El pequeno desplazamiento queda
por debajo del umbral y ocurre sin forzante SPH local.

Archivos:

- `data/verification_preproduction_20260508/contact_sanity_report.md`
- `data/verification_preproduction_20260508/figures/contact_sanity_timeseries.png`

## 3. Comparacion analitica preliminar

Se compararon casos del piloto y batch2 contra un indice de movilidad de bajo orden:

```text
Psi = fuerza motriz aproximada / resistencia friccional efectiva
```

La comparacion usa una banda lower-central-upper de coeficientes de arrastre, sustentacion y area proyectada.
No reclasifica los casos; solo busca contradicciones de orden de magnitud.

Resultado:

- casos consolidados: {len(analytic_summary)}
- casos utiles para analitica: {len(usable)}
- contradicciones fuertes: {contradictions}/{len(usable)}
- fallos SPH con banda completamente movil: {int((failures['psi_lower'] > 1).sum())}/{len(failures)}
- estables SPH con resistencia posible en la banda: {int((stable['psi_lower'] < 1).sum())}/{len(stable)}
- mediana `Psi_central` en estables: {stable['psi_central'].median():.2g}
- mediana `Psi_central` en fallos: {failures['psi_central'].median():.2g}

Lectura: no aparecen contradicciones fuertes entre la banda analitica y la clase SPH. Esto aporta coherencia
fisica preliminar, pero no reemplaza validacion experimental ni la campana productiva.

Archivos:

- `data/analytic_comparison/20260508_preproduction/analytic_comparison_report.md`
- `data/analytic_comparison/20260508_preproduction/figures/psi_vs_displacement.png`
- `data/analytic_comparison/20260508_preproduction/figures/ordered_mobility_cases.png`

## Conclusion operativa

Estos tres controles cubren cosas distintas:

1. El benchmark valida el pipeline hidraulico basico.
2. El sanity valida que el contacto inicial no genera movimiento espurio relevante.
3. La comparacion analitica valida coherencia fisica de orden de magnitud.

Con esto la campana productiva queda mejor defendida, pero las afirmaciones deben seguir siendo conservadoras:
la frontera final sera condicionada a la resolucion `dp=0.003`, al modelo de contacto, a la geometria fija y a las
distribuciones/variables consideradas.

## Fuentes metodologicas usadas

- SPHERIC benchmark tests: https://www.spheric-sph.org/validation-tests
- SPHERIC Test 05 wet-bottom dam break: https://www.spheric-sph.org/tests/test-05
- DualSPHysics SPH formulation and Chrono coupling: https://github.com/DualSPHysics/DualSPHysics/wiki/3.-SPH-formulation
- Project Chrono introduction/contact capabilities: https://api.chrono.projectchrono.org/introduction_chrono.html
- NASA/NPARC grid convergence and GCI tutorial: https://www.grc.nasa.gov/www/wind/valid/tutorial/spatconv.html
- Bressan et al. incipient boulder motion: https://pearl.plymouth.ac.uk/secam-research/1746
- Cox et al. critique of common boulder hydrodynamic equations: https://www.frontiersin.org/articles/10.3389/fmars.2020.00004/full
"""
    DOCS.mkdir(parents=True, exist_ok=True)
    (DOCS / "VERIFICACION_PREPRODUCCION_RESULTADOS_2026-05-08.md").write_text(report, encoding="utf-8")
    (OUT / "VERIFICACION_PREPRODUCCION_RESULTADOS_2026-05-08.md").write_text(report, encoding="utf-8")


def main() -> None:
    contact = contact_figures()
    consolidated_report(contact)
    print(f"Verification report written to {DOCS / 'VERIFICACION_PREPRODUCCION_RESULTADOS_2026-05-08.md'}")
    print(f"Figures written to {FIG}")


if __name__ == "__main__":
    main()
