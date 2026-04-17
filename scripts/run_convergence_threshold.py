"""
run_convergence_threshold.py - Wrapper corto para convergencia cerca de la frontera.

Reutiliza la infraestructura de run_convergence_v2.py, pero:
- corre solo los dp finos (por defecto 0.004, 0.003, 0.002)
- permite fijar un caso candidato de frontera via CLI
- escribe resultados, logs, temporales y GCI en archivos separados

Uso recomendado:
    python scripts/run_convergence_threshold.py
    python scripts/run_convergence_threshold.py --friction 0.6 --prefix conv3_f06
    python scripts/run_convergence_threshold.py --solo-analisis --prefix conv3_f05
"""

from __future__ import annotations

import argparse
import json
import logging
import shutil
import sys
import time
from pathlib import Path

import pandas as pd

import run_convergence_v2 as base


def _sanitize_token(text: str) -> str:
    cleaned = []
    for char in text:
        if char.isalnum() or char == "_":
            cleaned.append(char)
        elif char in ".-":
            cleaned.append("_")
    return "".join(cleaned).strip("_")


def _fmt_token(value: float) -> str:
    return str(value).replace(".", "p")


def _default_prefix(args: argparse.Namespace) -> str:
    return (
        f"conv3_dh{_fmt_token(args.dam_height)}"
        f"_m{_fmt_token(args.mass)}"
        f"_fr{_fmt_token(args.friction)}"
        f"_s{int(args.slope_inv)}"
    )


def _parse_dps(raw: str) -> list[float]:
    try:
        dps = [float(piece.strip()) for piece in raw.split(",") if piece.strip()]
    except ValueError as exc:
        raise argparse.ArgumentTypeError(f"dps invalidos: {raw}") from exc
    if not dps:
        raise argparse.ArgumentTypeError("Debes indicar al menos un dp")
    return dps


def _configure_outputs(prefix: str) -> dict[str, Path]:
    paths = {
        "status": base.PROJECT_ROOT / "data" / "logs" / f"{prefix}_status.json",
        "csv": base.PROJECT_ROOT / "data" / "results" / f"{prefix}.csv",
        "log": base.PROJECT_ROOT / "data" / "logs" / f"{prefix}.log",
        "temporal": base.PROJECT_ROOT / "data" / "results" / f"{prefix}_temporal",
        "gci": base.PROJECT_ROOT / "data" / "results" / f"{prefix}_gci.json",
    }
    return paths


def _patch_temporal_writer(out_dir: Path) -> None:
    def save_temporal_data(processed_dir: Path, case_name: str, dp: float) -> None:
        del dp
        out_dir.mkdir(parents=True, exist_ok=True)

        for src in processed_dir.rglob("ChronoExchange_mkbound_*.csv"):
            shutil.copy2(str(src), str(out_dir / f"{case_name}_exchange.csv"))
            break

        for src in processed_dir.rglob("ChronoBody_forces.csv"):
            shutil.copy2(str(src), str(out_dir / f"{case_name}_forces.csv"))
            break

    base._save_temporal_data = save_temporal_data


def _patch_gci_writer(gci_json: Path) -> None:
    def run_gci_analysis(df_ok: pd.DataFrame):
        if len(df_ok) < 3:
            base.logger.warning("Menos de 3 dp exitosos - no se puede calcular GCI")
            return None

        df_sorted = df_ok.sort_values("dp").reset_index(drop=True)
        metrics = {
            "displacement": ("max_displacement_m", "m"),
            "velocity": ("max_velocity_ms", "m/s"),
            "sph_force": ("max_sph_force_N", "N"),
            "rotation": ("max_rotation_deg", "deg"),
        }
        primary = ["displacement", "velocity", "sph_force"]

        results = {}
        base.logger.info("\n" + "=" * 65)
        base.logger.info("ANALISIS GCI (Celik 2008)")
        base.logger.info("=" * 65)

        for name, (col, unit) in metrics.items():
            is_primary = name in primary
            tag = "PRIMARIA" if is_primary else "DIAGNOSTICO"
            base.logger.info(f"\n--- {name} ({tag}) ---")

            values = df_sorted[col].values
            dps = df_sorted["dp"].values

            phi1, phi2, phi3 = values[0], values[1], values[2]
            r21 = dps[1] / dps[0]
            r32 = dps[2] / dps[1]

            p, conv_type = base.celik_apparent_order(phi1, phi2, phi3, r21, r32)
            gci = base.compute_gci(phi1, phi2, phi3, r21, r32, p)

            base.logger.info(f"  Mallas: dp={dps[0]}, {dps[1]}, {dps[2]}")
            base.logger.info(f"  Valores: {phi1:.6f}, {phi2:.6f}, {phi3:.6f} {unit}")
            base.logger.info(f"  Tipo convergencia: {conv_type}")
            if conv_type == "monotonic":
                base.logger.info(f"  Orden aparente p = {p:.2f}")
                base.logger.info(f"  Richardson extrap: {gci['phi_ext']:.6f} {unit}")
                base.logger.info(f"  GCI_fine = {gci['GCI_fine']*100:.2f}%")
                base.logger.info(f"  GCI_med  = {gci['GCI_med']*100:.2f}%")
                base.logger.info(
                    f"  AR = {gci['AR']:.3f} "
                    f"({'asintotico' if gci['in_asymptotic'] else 'NO asintotico'})"
                )
            else:
                base.logger.info(
                    f"  GCI/Richardson NO APLICA para convergencia {conv_type} "
                    f"(Celik 2008)"
                )

            base.logger.info("  Deltas entre niveles:")
            for idx in range(len(values) - 1):
                delta = abs(values[idx] - values[idx + 1])
                pct = delta / abs(values[idx]) * 100 if abs(values[idx]) > 1e-15 else 0
                base.logger.info(
                    f"    dp {dps[idx]:.4f} -> {dps[idx+1]:.4f}: "
                    f"delta={delta:.6f} {unit} ({pct:.1f}%)"
                )

            results[name] = {
                "col": col,
                "unit": unit,
                "is_primary": is_primary,
                "p": p,
                "conv_type": conv_type,
                **gci,
                "values": values.tolist(),
                "dps": dps.tolist(),
            }

        base.logger.info("\n" + "=" * 65)
        base.logger.info("VEREDICTO")
        base.logger.info("=" * 65)

        for name in primary:
            result = results[name]
            if result["conv_type"] != "monotonic":
                base.logger.info(
                    f"  {name}: convergencia {result['conv_type']} -> GCI NO APLICA"
                )
                continue
            gci_pct = result["GCI_fine"] * 100
            verdict = "OK" if gci_pct < 5 else "ACEPTABLE" if gci_pct < 10 else "INSUFICIENTE"
            base.logger.info(
                f"  {name}: GCI={gci_pct:.2f}%, p={result['p']:.2f}, "
                f"AR={result['AR']:.3f} -> {verdict}"
            )

        gci_json.parent.mkdir(parents=True, exist_ok=True)
        with open(gci_json, "w", encoding="utf-8") as handle:
            json.dump(results, handle, indent=2, default=str)
        base.logger.info(f"\nGCI JSON: {gci_json}")
        return results

    base.run_gci_analysis = run_gci_analysis


def _patch_runner(prefix: str, sqlite_table: str) -> None:
    def run_single_dp(dp: float, config: dict, d_eq: float) -> dict:
        case_name = f"{prefix}_dp{str(dp).replace('.', '')}"
        start = time.time()
        entry = {"dp": dp, "case_name": case_name, "status": "ERROR"}

        template_xml = base.PROJECT_ROOT / config["paths"]["template_xml"]
        boulder_stl = base.PROJECT_ROOT / config["paths"]["boulder_stl"]
        beach_stl = base.PROJECT_ROOT / config["paths"]["beach_stl"]
        materials_xml = base.PROJECT_ROOT / config["paths"]["materials_xml"]
        cases_dir = base.PROJECT_ROOT / config["paths"]["cases_dir"]
        processed_dir = base.PROJECT_ROOT / config["paths"]["processed_dir"] / case_name

        params = base.CaseParams(
            case_name=case_name,
            dp=dp,
            dam_height=base.BASE_PARAMS["dam_height"],
            dam_length=base.BASE_PARAMS["dam_length"],
            boulder_mass=base.BASE_PARAMS["boulder_mass"],
            boulder_scale=base.BASE_PARAMS["boulder_scale"],
            boulder_pos=base.BASE_PARAMS["boulder_pos"],
            boulder_rot=base.BASE_PARAMS["boulder_rot"],
            material=base.BASE_PARAMS["material"],
            friction_coefficient=base.BASE_PARAMS["friction_coefficient"],
            slope_inv=base.BASE_PARAMS["slope_inv"],
            time_max=base.BASE_PARAMS["time_max"],
            time_out=base.BASE_PARAMS["time_max"],
            ft_pause=base.BASE_PARAMS["ft_pause"],
            chrono_savedata=base.BASE_PARAMS["chrono_savedata"],
        )

        try:
            xml_path = base.build_case(
                template_xml=template_xml,
                boulder_stl=boulder_stl,
                beach_stl=beach_stl,
                materials_xml=materials_xml,
                output_dir=cases_dir,
                params=params,
            )
        except Exception as exc:
            entry["error"] = f"GenCase prep: {exc}"
            entry["tiempo_min"] = (time.time() - start) / 60
            return entry

        case_dir = xml_path.parent
        base.logger.info("  [1/3] Geometry OK")

        try:
            run_result = base.run_case(case_dir, config, processed_dir, dp=dp)
        except Exception as exc:
            entry["error"] = f"Sim exception: {exc}"
            entry["tiempo_min"] = (time.time() - start) / 60
            return entry

        if not run_result["success"]:
            entry["status"] = "FALLO_SIM"
            entry["error"] = run_result.get("error_message", "unknown")
            entry["tiempo_min"] = (time.time() - start) / 60
            base.logger.error(f"  [2/3] Sim FALLO: {entry['error']}")
            return entry

        base.logger.info(f"  [2/3] Sim OK ({run_result['duration_s']:.0f}s)")

        try:
            case_result = base.process_case(
                processed_dir,
                d_eq=d_eq,
                boulder_mass=base.BASE_PARAMS["boulder_mass"],
                **base.PROCESS_CASE_KWARGS,
            )
        except Exception as exc:
            entry["status"] = "FALLO_ANALISIS"
            entry["error"] = f"Analisis: {exc}"
            entry["tiempo_min"] = (time.time() - start) / 60
            return entry

        elapsed = (time.time() - start) / 60
        base.logger.info(f"  [3/3] Analisis OK - {elapsed:.1f} min total")

        run_metrics = base._read_run_metrics(processed_dir)
        base._save_temporal_data(processed_dir, case_name, dp)

        entry.update(
            {
                "status": "OK",
                "max_displacement_m": case_result.max_displacement,
                "max_rotation_deg": case_result.max_rotation,
                "max_velocity_ms": case_result.max_velocity,
                "max_sph_force_N": case_result.max_sph_force,
                "max_contact_force_N": case_result.max_contact_force,
                "max_flow_velocity_ms": case_result.max_flow_velocity,
                "max_water_height_m": case_result.max_water_height,
                "criterion_mode": case_result.classification_mode,
                "criterion_class": "FALLO" if case_result.failed else "ESTABLE",
                "criterion_reference_time_s": case_result.reference_time_s,
                "moved": case_result.moved,
                "rotated": case_result.rotated,
                "flow_gauge_id": case_result.flow_gauge_id,
                "water_gauge_id": case_result.water_gauge_id,
                "sim_time_s": case_result.sim_time_reached,
                "n_timesteps": case_result.n_timesteps,
                "n_particles": run_metrics["n_particles"],
                "mem_gpu_mb": run_metrics["mem_gpu_mb"],
                "mem_gpu_cells_mb": run_metrics["mem_gpu_cells_mb"],
                "tiempo_min": elapsed,
                "_case_result": case_result,
            }
        )
        return entry

    original_study = base.run_convergence_study

    def run_convergence_study(desde_dp=None, solo_analisis=False):
        return original_study(desde_dp=desde_dp, solo_analisis=solo_analisis)

    base.run_single_dp = run_single_dp
    base.run_convergence_study = run_convergence_study
    base.SQLITE_TABLE = sqlite_table


def _patch_sqlite_table(sqlite_table: str) -> None:
    original_save = base.save_to_sqlite

    def save_to_sqlite(results, db_path, table="results"):
        del table
        return original_save(results, db_path, table=sqlite_table)

    base.save_to_sqlite = save_to_sqlite


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Convergencia corta cerca de la frontera usando la infraestructura v2."
    )
    parser.add_argument("--dam-height", type=float, default=0.20)
    parser.add_argument("--dam-length", type=float, default=1.5)
    parser.add_argument("--mass", type=float, default=1.0)
    parser.add_argument("--friction", type=float, default=0.5)
    parser.add_argument("--slope-inv", type=float, default=20.0)
    parser.add_argument("--rot-z", type=float, default=0.0)
    parser.add_argument("--material", default="pvc")
    parser.add_argument("--time-max", type=float, default=10.0)
    parser.add_argument("--ft-pause", type=float, default=0.5)
    parser.add_argument("--chrono-savedata", type=float, default=0.001)
    parser.add_argument(
        "--classification-mode",
        choices=["combined", "displacement_only", "rotation_only"],
        default="displacement_only",
    )
    parser.add_argument(
        "--reference-time",
        type=float,
        default=None,
        help="Referencia temporal para displacement/rotation.",
    )
    parser.add_argument("--dps", type=_parse_dps, default=[0.004, 0.003, 0.002])
    parser.add_argument("--prefix")
    parser.add_argument("--desde", type=float)
    parser.add_argument("--solo-analisis", action="store_true")
    return parser


def main() -> None:
    parser = _build_parser()
    args = parser.parse_args()

    prefix = _sanitize_token(args.prefix or _default_prefix(args))
    sqlite_table = _sanitize_token(f"convergence_{prefix}")
    outputs = _configure_outputs(prefix)

    base.DP_CORE = list(args.dps)
    base.DP_EXPLORATORY = []
    base.DP_ALL = list(args.dps)
    base.SLOPE_INV = args.slope_inv
    base.BOULDER_POS = base.get_boulder_position(slope_inv=args.slope_inv)
    base.BOULDER_ROT = base.get_boulder_rotation(slope_inv=args.slope_inv, rot_z=args.rot_z)
    base.BASE_PARAMS.update(
        {
            "dam_height": args.dam_height,
            "dam_length": args.dam_length,
            "boulder_mass": args.mass,
            "boulder_scale": 0.04,
            "boulder_pos": base.BOULDER_POS,
            "boulder_rot": base.BOULDER_ROT,
            "material": args.material,
            "friction_coefficient": args.friction,
            "slope_inv": args.slope_inv,
            "time_max": args.time_max,
            "ft_pause": args.ft_pause,
            "chrono_savedata": args.chrono_savedata,
        }
    )
    base.PROCESS_CASE_KWARGS = {
        "classification_mode": args.classification_mode,
        "reference_time_s": args.reference_time,
    }

    base.STATUS_FILE = outputs["status"]
    base.RESULTS_CSV = outputs["csv"]
    base.LOG_FILE = outputs["log"]

    _patch_temporal_writer(outputs["temporal"])
    _patch_gci_writer(outputs["gci"])
    _patch_sqlite_table(sqlite_table)
    _patch_runner(prefix, sqlite_table)

    base.LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s: %(message)s",
        datefmt="%H:%M:%S",
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler(base.LOG_FILE, encoding="utf-8"),
        ],
    )

    base.logger.info("=" * 65)
    base.logger.info("CONVERGENCIA CORTA CERCA DE LA FRONTERA")
    base.logger.info("=" * 65)
    base.logger.info(f"prefix: {prefix}")
    base.logger.info(
        f"caso: dam_h={args.dam_height}, mass={args.mass}, fric={args.friction}, "
        f"slope=1:{int(args.slope_inv)}, rot_z={args.rot_z}"
    )
    base.logger.info(f"dps: {base.DP_ALL}")
    base.logger.info(f"csv: {base.RESULTS_CSV}")
    base.logger.info(f"gci: {outputs['gci']}")
    base.logger.info(f"sqlite table: {sqlite_table}")
    base.logger.info(
        f"criterion: mode={args.classification_mode}, "
        f"reference_time={args.reference_time}"
    )

    base.run_convergence_study(desde_dp=args.desde, solo_analisis=args.solo_analisis)


if __name__ == "__main__":
    main()
