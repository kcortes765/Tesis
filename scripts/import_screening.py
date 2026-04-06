"""
import_screening.py — Importa resultados de screening desde la WS.

Generalizado para cualquier round de screening (R1, R2, R3, etc.).
Descomprime ZIP, procesa con data_cleaner, actualiza SQLite, genera reporte.

Criterio de clasificacion unificado con data_cleaner.py:
  ESTABLE: displacement < 5mm AND rotation < 5 deg
  UMBRAL:  displacement 5-10mm OR rotation 5-15 deg (sin exceder FALLO)
  FALLO:   displacement > 10mm OR rotation > 15 deg

Uso:
  python scripts/import_screening.py --zip round3_results.zip --config config/screening_round3.csv --prefix sc3_ --label R3
  python scripts/import_screening.py --zip round2.zip --config config/screening_round2.csv --prefix sc2_ --label R2
  python scripts/import_screening.py --only-analysis --prefix sc3_ --config config/screening_round3.csv --label R3

Autor: Kevin Cortes (UCN 2026)
"""

from __future__ import annotations

import argparse
import json
import logging
import re
import shutil
import sys
import zipfile
from pathlib import Path

import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from data_cleaner import process_case, save_to_sqlite, CaseResult


# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------

PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"
RESULTS_DIR = PROJECT_ROOT / "data" / "results"
FIGURES_DIR = PROJECT_ROOT / "data" / "figures"
DB_PATH = PROJECT_ROOT / "data" / "results.sqlite"

D_EQ = 0.1004  # BLIR3 @ scale=0.04

# Umbrales unificados (coherentes con data_cleaner.py disp_threshold + rot_threshold)
DISP_STABLE_MM = 5.0     # < 5mm displacement
ROT_STABLE_DEG = 5.0     # < 5 deg rotation
DISP_FALLO_MM = 10.0     # > 10mm displacement
ROT_FALLO_DEG = 15.0     # > 15 deg rotation


def classify_case(disp_mm: float, rot_deg: float) -> str:
    """Clasificacion unificada: displacement OR rotation."""
    if disp_mm > DISP_FALLO_MM or rot_deg > ROT_FALLO_DEG:
        return "FALLO"
    if disp_mm > DISP_STABLE_MM or rot_deg > ROT_STABLE_DEG:
        return "UMBRAL"
    return "ESTABLE"


# ---------------------------------------------------------------------------
# Paso 1: Extraer ZIP
# ---------------------------------------------------------------------------

def extract_zip(zip_path: Path) -> list:
    logger.info(f"Extrayendo {zip_path.name}...")
    with zipfile.ZipFile(str(zip_path), "r") as zf:
        manifest = {}
        if "manifest.json" in zf.namelist():
            manifest = json.loads(zf.read("manifest.json"))
            logger.info(f"Manifiesto: {len(manifest.get('cases', []))} casos")

        case_ids = sorted({
            name.split("/")[0]
            for name in zf.namelist()
            if "/" in name and not name.startswith("manifest")
        })
        logger.info(f"Casos en ZIP: {case_ids}")

        for cid in case_ids:
            dest = PROCESSED_DIR / cid
            if dest.exists():
                logger.warning(f"  {cid}: sobreescribiendo")
                shutil.rmtree(str(dest))

        for member in zf.namelist():
            if member == "manifest.json" or member.endswith("/"):
                continue
            parts = member.split("/", 1)
            if len(parts) < 2:
                continue
            dest_file = PROCESSED_DIR / parts[0] / parts[1]
            dest_file.parent.mkdir(parents=True, exist_ok=True)
            with zf.open(member) as src, open(dest_file, "wb") as dst:
                dst.write(src.read())

    logger.info(f"Extraidos {len(case_ids)} casos")
    return case_ids


# ---------------------------------------------------------------------------
# Paso 2: Procesar
# ---------------------------------------------------------------------------

def load_params(config_csv: Path) -> dict:
    if not config_csv.exists():
        logger.warning(f"Config CSV no encontrado: {config_csv}")
        return {}
    df = pd.read_csv(config_csv)
    return {row["case_id"]: row.to_dict() for _, row in df.iterrows()}


def find_csv_dir(case_dir: Path) -> Path:
    for child in sorted(case_dir.iterdir()):
        if child.is_dir() and child.name.endswith("_out"):
            if any(child.glob("ChronoExchange_mkbound_*.csv")):
                return child
    if any(case_dir.glob("ChronoExchange_mkbound_*.csv")):
        return case_dir
    return case_dir


def process_all_cases(case_ids: list, config_csv: Path, dp: float) -> list:
    params = load_params(config_csv)
    results = []
    errors = []

    for cid in case_ids:
        case_dir = PROCESSED_DIR / cid
        csv_dir = find_csv_dir(case_dir)
        logger.info(f"Procesando: {cid}")

        try:
            cp = params.get(cid, {})
            mass = float(cp.get("boulder_mass", 1.0))

            result = process_case(csv_dir, d_eq=D_EQ, boulder_mass=mass,
                                  disp_threshold_pct=5.0, rot_threshold_deg=5.0)

            result.dam_height = float(cp.get("dam_height", 0.0))
            result.boulder_mass = mass
            result.boulder_rot_z = float(cp.get("boulder_rot_z", 0.0))
            result.friction_coefficient = float(cp.get("friction_coefficient", 0.0))
            result.slope_inv = float(cp.get("slope_inv", 20.0))
            result.dp = dp
            result.stl_file = "BLIR3.stl"
            result.case_name = cid

            results.append(result)
            disp_mm = result.max_displacement * 1000
            rot_deg = result.max_rotation
            estado = classify_case(disp_mm, rot_deg)
            logger.info(f"  -> {estado}: disp={disp_mm:.1f}mm, rot={rot_deg:.1f}deg")

        except Exception as e:
            logger.error(f"  ERROR {cid}: {e}")
            errors.append((cid, str(e)))

    logger.info(f"Procesados: {len(results)} OK, {len(errors)} errores")
    return results


# ---------------------------------------------------------------------------
# Paso 3: Analisis
# ---------------------------------------------------------------------------

def generate_analysis(results: list, config_csv: Path, label: str, dp: float):
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    FIGURES_DIR.mkdir(parents=True, exist_ok=True)

    params_df = pd.read_csv(config_csv) if config_csv.exists() else pd.DataFrame()

    rows = []
    for r in results:
        disp_mm = r.max_displacement * 1000
        rot_deg = r.max_rotation
        rows.append({
            "case_id": r.case_name,
            "dam_h": r.dam_height,
            "mass": r.boulder_mass,
            "rot_z": r.boulder_rot_z,
            "friction": r.friction_coefficient,
            "slope_inv": r.slope_inv,
            "dp": r.dp,
            "max_disp_mm": round(disp_mm, 2),
            "max_rot_deg": round(rot_deg, 1),
            "max_vel_mps": round(r.max_velocity, 4),
            "flow_vel_mps": round(r.max_flow_velocity, 4),
            "water_h_m": round(r.max_water_height, 4),
            "sph_force_N": round(r.max_sph_force, 2),
            "contact_force_N": round(r.max_contact_force, 2),
            "sim_time_s": round(r.sim_time_reached, 2),
            "n_timesteps": r.n_timesteps,
            "estado": classify_case(disp_mm, rot_deg),
        })

    df = pd.DataFrame(rows).sort_values("max_disp_mm")
    csv_name = f"results_{label.lower()}.csv"
    csv_path = RESULTS_DIR / csv_name
    df.to_csv(csv_path, index=False)
    logger.info(f"CSV: {csv_path}")

    # Objetivo de cada caso (si existe en config)
    obj_map = {}
    if "objetivo" in params_df.columns:
        obj_map = dict(zip(params_df["case_id"], params_df["objetivo"]))

    # Reporte markdown
    report = _build_report(df, label, dp, obj_map)
    report_path = FIGURES_DIR / f"screening_{label.lower()}_report.md"
    report_path.write_text(report, encoding="utf-8")
    logger.info(f"Reporte: {report_path}")

    return df


def _build_report(df, label, dp, obj_map):
    n = len(df)
    n_est = len(df[df["estado"] == "ESTABLE"])
    n_umb = len(df[df["estado"] == "UMBRAL"])
    n_fal = len(df[df["estado"] == "FALLO"])

    lines = [
        f"# Screening {label} (dp={dp})",
        "",
        f"**Fecha:** {pd.Timestamp.now().strftime('%Y-%m-%d')}",
        f"**Casos:** {n}",
        f"**Criterio:** ESTABLE = disp<{DISP_STABLE_MM}mm AND rot<{ROT_STABLE_DEG}deg | "
        f"FALLO = disp>{DISP_FALLO_MM}mm OR rot>{ROT_FALLO_DEG}deg | UMBRAL = resto",
        "",
        "---",
        "",
        f"## Clasificacion: {n_est} ESTABLE, {n_umb} UMBRAL, {n_fal} FALLO",
        "",
        "## Tabla Resumen",
        "",
        "| Caso | dam_h | mass | rot_z | fric | slope | disp [mm] | rot [deg] | vel [m/s] | Estado | Objetivo |",
        "|------|-------|------|-------|------|-------|-----------|-----------|-----------|--------|----------|",
    ]

    for _, r in df.iterrows():
        obj = obj_map.get(r["case_id"], "")
        lines.append(
            f"| {r['case_id']} | {r['dam_h']:.3f} | {r['mass']:.2f} | {r['rot_z']:.0f} "
            f"| {r['friction']:.2f} | {r['slope_inv']:.0f} "
            f"| {r['max_disp_mm']:.2f} | {r['max_rot_deg']:.1f} "
            f"| {r['max_vel_mps']:.3f} | {r['estado']} | {obj} |"
        )

    # Correlaciones Spearman
    from scipy.stats import spearmanr
    lines.extend(["", "---", "", "## Correlaciones Spearman vs desplazamiento", ""])
    for col, label_c in [("dam_h", "dam_h"), ("mass", "mass"), ("rot_z", "rot_z"),
                          ("friction", "friction"), ("slope_inv", "slope")]:
        if col in df.columns and df[col].std() > 0:
            rho, p = spearmanr(df[col], df["max_disp_mm"])
            sig = "***" if p < 0.001 else "**" if p < 0.01 else "*" if p < 0.05 else "n.s."
            lines.append(f"- **{label_c}**: rho={rho:+.3f}, p={p:.4f} {sig}")

    lines.extend(["", "---", ""])
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Diagnostico XML
# ---------------------------------------------------------------------------

def run_xml_diagnostics(case_ids: list, expected_dp: float):
    logger.info("--- Diagnostico XMLs ---")
    for cid in case_ids:
        case_dir = PROCESSED_DIR / cid
        xml_defs = list(case_dir.rglob("*_Def.xml"))
        if not xml_defs:
            logger.warning(f"  {cid}: sin XML")
            continue
        text = xml_defs[0].read_text(encoding="utf-8", errors="ignore")
        dp = _extract_float(r'<definition\s+dp="([^"]+)"', text)
        mass = _extract_float(r'<massbody\s+value="([^"]+)"', text)
        tmax = _extract_float(r'key="TimeMax"\s+value="([^"]+)"', text)
        ftpause = _extract_float(r'key="FtPause"\s+value="([^"]+)"', text)

        issues = []
        if dp and abs(dp - expected_dp) > 1e-6:
            issues.append(f"dp={dp}")
        if tmax and abs(tmax - 10.0) > 0.1:
            issues.append(f"TimeMax={tmax}")
        if ftpause is not None and abs(ftpause - 0.5) > 0.01:
            issues.append(f"FtPause={ftpause}")
        status = "OK" if not issues else f"REVISAR: {', '.join(issues)}"
        logger.info(f"  {cid}: dp={dp}, mass={mass}, TimeMax={tmax} -> {status}")


def _extract_float(pattern, text):
    m = re.search(pattern, text, re.IGNORECASE)
    if m:
        try:
            return float(m.group(1))
        except ValueError:
            pass
    return None


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Importa y analiza resultados de screening desde la WS.")
    parser.add_argument("--zip", default=None, help="ZIP de collect_ws_results.py")
    parser.add_argument("--config", required=True,
                        help="CSV de configuracion (config/screening_roundN.csv)")
    parser.add_argument("--prefix", required=True,
                        help="Prefijo de casos (sc2_, sc3_, etc.)")
    parser.add_argument("--label", default="RX",
                        help="Etiqueta del round (R2, R3, etc.)")
    parser.add_argument("--dp", type=float, default=0.004,
                        help="dp de las simulaciones (default: 0.004)")
    parser.add_argument("--skip-analysis", action="store_true")
    parser.add_argument("--only-analysis", action="store_true")
    args = parser.parse_args(argv)

    config_csv = Path(args.config)
    if not config_csv.is_absolute():
        config_csv = PROJECT_ROOT / config_csv

    print(f"{'='*60}")
    print(f"  Import Screening {args.label}: WS -> Laptop")
    print(f"{'='*60}")

    # Extraer
    if not args.only_analysis:
        zip_path = Path(args.zip).resolve() if args.zip else None
        if not zip_path or not zip_path.exists():
            print(f"ERROR: ZIP no encontrado: {zip_path}")
            return 1
        case_ids = extract_zip(zip_path)
    else:
        case_ids = sorted(
            d.name for d in PROCESSED_DIR.iterdir()
            if d.is_dir() and d.name.startswith(args.prefix)
        )
        if not case_ids:
            print(f"ERROR: No se encontraron casos {args.prefix}* en data/processed/")
            return 1

    # Diagnostico
    run_xml_diagnostics(case_ids, args.dp)

    if args.skip_analysis:
        return 0

    # Procesar
    results = process_all_cases(case_ids, config_csv, args.dp)

    # SQLite
    if results:
        save_to_sqlite(results, DB_PATH)

    # Analisis
    generate_analysis(results, config_csv, args.label, args.dp)

    print(f"\n{'='*60}")
    print(f"  {len(results)} casos procesados")
    print(f"  SQLite: {DB_PATH}")
    print(f"  CSV: {RESULTS_DIR / f'results_{args.label.lower()}.csv'}")
    print(f"  Reporte: {FIGURES_DIR / f'screening_{args.label.lower()}_report.md'}")
    print(f"{'='*60}")
    return 0


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s: %(message)s",
                        datefmt="%H:%M:%S")
    sys.exit(main())
