"""
import_round2.py — Importa resultados del WS y ejecuta analisis completo.

Descomprime el ZIP generado por collect_ws_results.py, copia los datos
a data/processed/sc2_*, procesa con data_cleaner, actualiza SQLite,
y genera reporte de analisis comparable al round 1.

Uso:
  python scripts/import_round2.py --zip round2_results_20260407.zip
  python scripts/import_round2.py --zip round2.zip --skip-analysis
  python scripts/import_round2.py --zip round2.zip --only-analysis

Autor: Kevin Cortes (UCN 2026)
"""

from __future__ import annotations

import argparse
import json
import logging
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

ROUND2_CSV = PROJECT_ROOT / "config" / "screening_round2.csv"
PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"
RESULTS_DIR = PROJECT_ROOT / "data" / "results"
FIGURES_DIR = PROJECT_ROOT / "data" / "figures"
DB_PATH = PROJECT_ROOT / "data" / "results.sqlite"

# Boulder properties (BLIR3 a escala 0.04)
D_EQ = 0.1004  # diametro equivalente esferico [m]

# Umbrales de clasificacion (mismos que round 1)
DISP_THRESHOLD_MM = 5.0    # < 5mm = ESTABLE (ruido numerico + settling)
DISP_UMBRAL_MM = 10.0      # 5-10mm = UMBRAL, >10mm = FALLO


# ---------------------------------------------------------------------------
# Paso 1: Descomprimir ZIP → data/processed/
# ---------------------------------------------------------------------------

def extract_zip(zip_path: Path) -> list[str]:
    """Extrae ZIP a data/processed/ preservando estructura de carpetas."""
    logger.info(f"Extrayendo {zip_path.name}...")

    with zipfile.ZipFile(str(zip_path), "r") as zf:
        # Leer manifiesto
        manifest = {}
        if "manifest.json" in zf.namelist():
            manifest = json.loads(zf.read("manifest.json"))
            cases_info = manifest.get("cases", [])
            logger.info(f"Manifiesto: {len(cases_info)} casos, "
                        f"fuente: {manifest.get('source_dir', '?')}")

        # Identificar casos (carpetas de primer nivel)
        case_ids = sorted({
            name.split("/")[0]
            for name in zf.namelist()
            if "/" in name and not name.startswith("manifest")
        })

        logger.info(f"Casos encontrados en ZIP: {case_ids}")

        for case_id in case_ids:
            dest_dir = PROCESSED_DIR / case_id
            if dest_dir.exists():
                logger.warning(f"  {case_id}: ya existe en processed/, sobreescribiendo")
                shutil.rmtree(str(dest_dir))

        # Extraer todo excepto manifest
        for member in zf.namelist():
            if member == "manifest.json" or member.endswith("/"):
                continue
            # member es "sc2_001/ChronoExchange_mkbound_51.csv" etc
            parts = member.split("/", 1)
            if len(parts) < 2:
                continue
            case_id = parts[0]
            rel_path = parts[1]

            dest_file = PROCESSED_DIR / case_id / rel_path
            dest_file.parent.mkdir(parents=True, exist_ok=True)
            with zf.open(member) as src, open(dest_file, "wb") as dst:
                dst.write(src.read())

    logger.info(f"Extraidos {len(case_ids)} casos a {PROCESSED_DIR}")
    return case_ids


# ---------------------------------------------------------------------------
# Paso 2: Procesar cada caso con data_cleaner
# ---------------------------------------------------------------------------

def load_round2_params() -> dict:
    """Carga parametros del screening round 2 como dict {case_id: row}."""
    if not ROUND2_CSV.exists():
        logger.warning(f"No se encontro {ROUND2_CSV}, parametros no se inyectaran")
        return {}
    df = pd.read_csv(ROUND2_CSV)
    return {row["case_id"]: row.to_dict() for _, row in df.iterrows()}


def find_csv_dir(case_dir: Path) -> Path:
    """Encuentra el directorio que contiene los CSVs de datos."""
    # Buscar en subdirectorio _out primero
    for child in sorted(case_dir.iterdir()):
        if child.is_dir() and child.name.endswith("_out"):
            if any(child.glob("ChronoExchange_mkbound_*.csv")):
                return child
    # Fallback: CSVs directamente en el case_dir
    if any(case_dir.glob("ChronoExchange_mkbound_*.csv")):
        return case_dir
    return case_dir


def process_all_cases(case_ids: list[str]) -> list[CaseResult]:
    """Procesa todos los casos y retorna resultados."""
    params = load_round2_params()
    results = []
    errors = []

    for case_id in case_ids:
        case_dir = PROCESSED_DIR / case_id
        csv_dir = find_csv_dir(case_dir)

        logger.info(f"\n{'='*50}")
        logger.info(f"Procesando: {case_id}")
        logger.info(f"{'='*50}")

        try:
            # Obtener masa del boulder para correccion de fuerzas
            case_params = params.get(case_id, {})
            boulder_mass = float(case_params.get("boulder_mass", 1.0))

            result = process_case(
                csv_dir,
                d_eq=D_EQ,
                boulder_mass=boulder_mass,
                disp_threshold_pct=5.0,
                rot_threshold_deg=5.0,
            )

            # Inyectar parametros de entrada
            result.dam_height = float(case_params.get("dam_height", 0.0))
            result.boulder_mass = boulder_mass
            result.boulder_rot_z = float(case_params.get("boulder_rot_z", 0.0))
            result.friction_coefficient = float(case_params.get("friction_coefficient", 0.0))
            result.slope_inv = float(case_params.get("slope_inv", 20.0))
            result.dp = 0.004  # Round 2 es todo a dp=0.004
            result.stl_file = "BLIR3.stl"

            # Renombrar case_name si data_cleaner uso el nombre del csv_dir
            result.case_name = case_id

            results.append(result)
            status = "FALLO" if result.failed else "ESTABLE"
            logger.info(f"  -> {status}: disp={result.max_displacement*1000:.1f}mm, "
                        f"rot={result.max_rotation:.1f}deg")

        except Exception as e:
            logger.error(f"  ERROR procesando {case_id}: {e}")
            errors.append((case_id, str(e)))

    logger.info(f"\nProcesados: {len(results)} OK, {len(errors)} errores")
    if errors:
        for cid, err in errors:
            logger.error(f"  {cid}: {err}")

    return results


# ---------------------------------------------------------------------------
# Paso 3: Guardar en SQLite
# ---------------------------------------------------------------------------

def save_results(results: list[CaseResult]):
    """Guarda resultados en SQLite."""
    if not results:
        logger.warning("No hay resultados para guardar")
        return
    save_to_sqlite(results, DB_PATH)
    logger.info(f"Guardados {len(results)} resultados en {DB_PATH}")


# ---------------------------------------------------------------------------
# Paso 4: Analisis y reporte
# ---------------------------------------------------------------------------

def classify_case(disp_mm: float) -> str:
    """Clasifica un caso segun desplazamiento."""
    if disp_mm <= DISP_THRESHOLD_MM:
        return "ESTABLE"
    elif disp_mm <= DISP_UMBRAL_MM:
        return "UMBRAL"
    else:
        return "FALLO"


def generate_analysis(results: list[CaseResult]):
    """Genera reporte de analisis del round 2 + comparacion con round 1."""
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    FIGURES_DIR.mkdir(parents=True, exist_ok=True)

    # --- CSV consolidado ---
    rows = []
    for r in results:
        disp_mm = r.max_displacement * 1000
        rows.append({
            "case_id": r.case_name,
            "dam_h": r.dam_height,
            "mass": r.boulder_mass,
            "rot_z": r.boulder_rot_z,
            "friction": r.friction_coefficient,
            "slope_inv": r.slope_inv,
            "dp": r.dp,
            "max_disp_mm": round(disp_mm, 2),
            "max_rot_deg": round(r.max_rotation, 1),
            "max_vel_mps": round(r.max_velocity, 4),
            "flow_vel_mps": round(r.max_flow_velocity, 4),
            "water_h_m": round(r.max_water_height, 4),
            "sph_force_N": round(r.max_sph_force, 2),
            "contact_force_N": round(r.max_contact_force, 2),
            "sim_time_s": round(r.sim_time_reached, 2),
            "n_timesteps": r.n_timesteps,
            "estado": classify_case(disp_mm),
        })

    df = pd.DataFrame(rows).sort_values("max_disp_mm")
    csv_path = RESULTS_DIR / "results_round2.csv"
    df.to_csv(csv_path, index=False)
    logger.info(f"CSV consolidado: {csv_path}")

    # --- Reporte markdown ---
    report = generate_report_md(df, results)
    report_path = FIGURES_DIR / "screening_round2_report.md"
    report_path.write_text(report, encoding="utf-8")
    logger.info(f"Reporte: {report_path}")

    # --- Figuras ---
    try:
        generate_figures(df)
    except Exception as e:
        logger.warning(f"No se pudieron generar figuras: {e}")

    # --- Comparacion con round 1 ---
    try:
        generate_comparison(df)
    except Exception as e:
        logger.warning(f"No se pudo generar comparacion: {e}")


def generate_report_md(df: pd.DataFrame, results: list[CaseResult]) -> str:
    """Genera reporte markdown del round 2."""
    n_total = len(df)
    n_estable = len(df[df["estado"] == "ESTABLE"])
    n_umbral = len(df[df["estado"] == "UMBRAL"])
    n_fallo = len(df[df["estado"] == "FALLO"])

    lines = [
        "# Analisis: Screening Round 2 (dp=0.004)",
        "",
        f"**Fecha:** {pd.Timestamp.now().strftime('%Y-%m-%d')}",
        f"**Casos:** {n_total} procesados",
        f"**Resolucion:** dp = 0.004 m",
        f"**TimeMax:** 10 s (FtPause = 0.5 s)",
        f"**Motor:** DualSPHysics v5.4 + Chrono (RigidAlgorithm=3)",
        "",
        "---",
        "",
        "## 1. Resumen de Clasificacion",
        "",
        f"- **ESTABLE** (< {DISP_THRESHOLD_MM}mm): {n_estable} casos",
        f"- **UMBRAL** ({DISP_THRESHOLD_MM}-{DISP_UMBRAL_MM}mm): {n_umbral} casos",
        f"- **FALLO** (> {DISP_UMBRAL_MM}mm): {n_fallo} casos",
        "",
        "---",
        "",
        "## 2. Tabla Resumen",
        "",
        "| Caso | dam_h [m] | masa [kg] | rot_z [deg] | friccion | pendiente (1/s) "
        "| max_disp [mm] | max_rot [deg] | max_vel [m/s] | flow_vel [m/s] | water_h [m] | Estado |",
        "|------|-----------|-----------|-------------|----------|-----------------|"
        "---------------|---------------|---------------|----------------|-------------|--------|",
    ]

    for _, row in df.iterrows():
        lines.append(
            f"| {row['case_id']} | {row['dam_h']:.3f} | {row['mass']:.3f} "
            f"| {row['rot_z']:.1f} | {row['friction']:.3f} | {row['slope_inv']:.0f} "
            f"| {row['max_disp_mm']:.2f} | {row['max_rot_deg']:.1f} "
            f"| {row['max_vel_mps']:.2f} | {row['flow_vel_mps']:.2f} "
            f"| {row['water_h_m']:.3f} | {row['estado']} |"
        )

    # Correlaciones
    lines.extend([
        "",
        "---",
        "",
        "## 3. Correlaciones con desplazamiento",
        "",
    ])

    numeric_cols = ["dam_h", "mass", "rot_z", "friction", "slope_inv"]
    for col in numeric_cols:
        if df[col].std() > 0:
            corr = df["max_disp_mm"].corr(df[col])
            lines.append(f"- **{col}**: rho = {corr:+.3f}")

    # Hallazgos clave
    lines.extend([
        "",
        "---",
        "",
        "## 4. Hallazgos clave",
        "",
        "*(Completar despues de revisar los datos)*",
        "",
        "### Preguntas a responder:",
        "1. La frontera dam_h~0.20m se define mejor a dp=0.004?",
        "2. Variables secundarias (rot_z, friction, slope) muestran efecto a dp fino?",
        f"3. sc2_015 (replica de sc_008 del round 1) da resultado consistente?",
        "4. Casos de no-movimiento (sc2_007, sc2_008) confirman estabilidad?",
        "5. Casos de aislamiento de variables (sc2_010-014) revelan dependencias?",
        "",
        "---",
        "",
        "## 5. Comparacion Round 1 vs Round 2",
        "",
        "Ver seccion de comparacion al final del analisis.",
        "",
    ])

    return "\n".join(lines)


def generate_figures(df: pd.DataFrame):
    """Genera figuras de analisis."""
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    colors = {"ESTABLE": "#2ecc71", "UMBRAL": "#f39c12", "FALLO": "#e74c3c"}

    # --- Fig 1: dam_h vs desplazamiento ---
    fig, ax = plt.subplots(figsize=(10, 6))
    for estado, color in colors.items():
        mask = df["estado"] == estado
        ax.scatter(df.loc[mask, "dam_h"], df.loc[mask, "max_disp_mm"],
                   c=color, label=estado, s=80, edgecolors="k", zorder=3)
    ax.axhline(DISP_THRESHOLD_MM, color="gray", ls="--", alpha=0.5, label=f"Umbral {DISP_THRESHOLD_MM}mm")
    ax.axhline(DISP_UMBRAL_MM, color="gray", ls=":", alpha=0.5, label=f"Umbral {DISP_UMBRAL_MM}mm")
    ax.set_xlabel("dam_height [m]")
    ax.set_ylabel("max displacement [mm]")
    ax.set_title("Round 2 (dp=0.004): dam_h vs Desplazamiento")
    ax.legend()
    ax.grid(True, alpha=0.3)
    fig.tight_layout()
    fig.savefig(str(FIGURES_DIR / "round2_scatter_damh_vs_disp.png"), dpi=150)
    plt.close(fig)
    logger.info("  Figura: round2_scatter_damh_vs_disp.png")

    # --- Fig 2: masa vs desplazamiento ---
    fig, ax = plt.subplots(figsize=(10, 6))
    for estado, color in colors.items():
        mask = df["estado"] == estado
        ax.scatter(df.loc[mask, "mass"], df.loc[mask, "max_disp_mm"],
                   c=color, label=estado, s=80, edgecolors="k", zorder=3)
    ax.set_xlabel("boulder_mass [kg]")
    ax.set_ylabel("max displacement [mm]")
    ax.set_title("Round 2 (dp=0.004): Masa vs Desplazamiento")
    ax.legend()
    ax.grid(True, alpha=0.3)
    fig.tight_layout()
    fig.savefig(str(FIGURES_DIR / "round2_scatter_mass_vs_disp.png"), dpi=150)
    plt.close(fig)
    logger.info("  Figura: round2_scatter_mass_vs_disp.png")

    # --- Fig 3: Heatmap de correlaciones ---
    fig, ax = plt.subplots(figsize=(8, 6))
    corr_cols = ["dam_h", "mass", "rot_z", "friction", "slope_inv", "max_disp_mm",
                 "max_rot_deg", "max_vel_mps", "flow_vel_mps", "water_h_m"]
    corr_cols = [c for c in corr_cols if c in df.columns]
    corr_matrix = df[corr_cols].corr()
    im = ax.imshow(corr_matrix, cmap="RdBu_r", vmin=-1, vmax=1, aspect="auto")
    ax.set_xticks(range(len(corr_cols)))
    ax.set_yticks(range(len(corr_cols)))
    ax.set_xticklabels(corr_cols, rotation=45, ha="right", fontsize=8)
    ax.set_yticklabels(corr_cols, fontsize=8)
    for i in range(len(corr_cols)):
        for j in range(len(corr_cols)):
            ax.text(j, i, f"{corr_matrix.iloc[i, j]:.2f}", ha="center", va="center", fontsize=7)
    fig.colorbar(im, ax=ax)
    ax.set_title("Round 2 (dp=0.004): Correlaciones")
    fig.tight_layout()
    fig.savefig(str(FIGURES_DIR / "round2_correlation_heatmap.png"), dpi=150)
    plt.close(fig)
    logger.info("  Figura: round2_correlation_heatmap.png")

    # --- Fig 4: Variables aisladas (sc2_010 a sc2_014) ---
    isolated = df[df["case_id"].isin(["sc2_010", "sc2_011", "sc2_012", "sc2_013", "sc2_014"])]
    if len(isolated) >= 3:
        fig, axes = plt.subplots(1, 3, figsize=(15, 5))

        # slope
        slope_cases = isolated[isolated["case_id"].isin(["sc2_010", "sc2_011"])]
        if len(slope_cases) > 0:
            axes[0].bar(slope_cases["case_id"], slope_cases["max_disp_mm"], color="#3498db")
            for _, row in slope_cases.iterrows():
                axes[0].annotate(f"slope=1:{row['slope_inv']:.0f}",
                                 (row["case_id"], row["max_disp_mm"]),
                                 textcoords="offset points", xytext=(0, 10), ha="center", fontsize=9)
            axes[0].set_ylabel("max displacement [mm]")
            axes[0].set_title("Efecto slope (dam_h=0.20, fric=0.3)")

        # friction
        fric_cases = isolated[isolated["case_id"].isin(["sc2_012", "sc2_013"])]
        if len(fric_cases) > 0:
            axes[1].bar(fric_cases["case_id"], fric_cases["max_disp_mm"], color="#e67e22")
            for _, row in fric_cases.iterrows():
                axes[1].annotate(f"fric={row['friction']:.2f}",
                                 (row["case_id"], row["max_disp_mm"]),
                                 textcoords="offset points", xytext=(0, 10), ha="center", fontsize=9)
            axes[1].set_ylabel("max displacement [mm]")
            axes[1].set_title("Efecto friccion (dam_h=0.20, slope=1:20)")

        # rot_z
        rot_cases = isolated[isolated["case_id"].isin(["sc2_014"])]
        # include sc2_003 as baseline (dam_h=0.20, rot_z=60) if available
        baseline = df[df["case_id"] == "sc2_003"]
        rot_all = pd.concat([baseline, rot_cases]) if len(baseline) > 0 else rot_cases
        if len(rot_all) > 0:
            axes[2].bar(rot_all["case_id"], rot_all["max_disp_mm"], color="#9b59b6")
            for _, row in rot_all.iterrows():
                axes[2].annotate(f"rot_z={row['rot_z']:.0f}°",
                                 (row["case_id"], row["max_disp_mm"]),
                                 textcoords="offset points", xytext=(0, 10), ha="center", fontsize=9)
            axes[2].set_ylabel("max displacement [mm]")
            axes[2].set_title("Efecto rotacion (dam_h=0.20)")

        fig.suptitle("Round 2: Aislamiento de variables secundarias", fontsize=14)
        fig.tight_layout()
        fig.savefig(str(FIGURES_DIR / "round2_isolated_variables.png"), dpi=150)
        plt.close(fig)
        logger.info("  Figura: round2_isolated_variables.png")


def generate_comparison(df_r2: pd.DataFrame):
    """Genera comparacion Round 1 vs Round 2."""
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    # Cargar round 1 desde SQLite
    import sqlite3
    if not DB_PATH.exists():
        logger.warning("No se encontro results.sqlite para comparacion")
        return

    conn = sqlite3.connect(str(DB_PATH))
    try:
        df_all = pd.read_sql("SELECT * FROM results", conn)
    except Exception:
        logger.warning("No se pudo leer tabla results de SQLite")
        return
    finally:
        conn.close()

    # Separar por dp
    r1 = df_all[df_all["dp"] == 0.005].copy()
    if len(r1) == 0:
        # Intentar con screening round 1 que no tiene dp en SQLite
        r1 = df_all[df_all["case_name"].str.startswith("sc_")].copy()

    if len(r1) == 0:
        logger.warning("No se encontraron datos de round 1 para comparar")
        return

    r1["round"] = "R1 (dp=0.005)"
    r1["disp_mm"] = r1["max_displacement"] * 1000

    r2 = df_r2.copy()
    r2["round"] = "R2 (dp=0.004)"
    r2["disp_mm"] = r2["max_disp_mm"]
    r2 = r2.rename(columns={"dam_h": "dam_height", "mass": "boulder_mass"})

    # --- Fig: Comparacion dam_h vs disp ambos rounds ---
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.scatter(r1["dam_height"], r1["disp_mm"], c="#3498db", s=60,
               marker="o", label="Round 1 (dp=0.005)", alpha=0.7, edgecolors="k")
    ax.scatter(r2["dam_height"], r2["disp_mm"], c="#e74c3c", s=80,
               marker="^", label="Round 2 (dp=0.004)", alpha=0.9, edgecolors="k")
    ax.axhline(DISP_THRESHOLD_MM, color="gray", ls="--", alpha=0.5)
    ax.axhline(DISP_UMBRAL_MM, color="gray", ls=":", alpha=0.5)
    ax.set_xlabel("dam_height [m]")
    ax.set_ylabel("max displacement [mm]")
    ax.set_title("Comparacion Round 1 vs Round 2: dam_h vs Desplazamiento")
    ax.legend()
    ax.grid(True, alpha=0.3)
    fig.tight_layout()
    fig.savefig(str(FIGURES_DIR / "round2_vs_round1_comparison.png"), dpi=150)
    plt.close(fig)
    logger.info("  Figura: round2_vs_round1_comparison.png")

    # --- Caso replicado: sc_008 (R1) vs sc2_015 (R2) ---
    sc008 = r1[r1["case_name"] == "sc_008"]
    sc2_015 = r2[r2["case_id"] == "sc2_015"]
    if len(sc008) > 0 and len(sc2_015) > 0:
        comp_path = FIGURES_DIR / "round2_replication_check.md"
        lines = [
            "# Verificacion de Replicacion: sc_008 (R1) vs sc2_015 (R2)",
            "",
            "sc2_015 replica los parametros exactos de sc_008 del round 1,",
            "pero a dp=0.004 en vez de dp=0.005.",
            "",
            "| Metrica | sc_008 (dp=0.005) | sc2_015 (dp=0.004) | Diferencia |",
            "| --- | ---: | ---: | ---: |",
        ]
        r1_row = sc008.iloc[0]
        r2_row = sc2_015.iloc[0]
        metrics = [
            ("max_disp [mm]", r1_row["disp_mm"], r2_row["disp_mm"]),
            ("max_rot [deg]", r1_row.get("max_rotation", 0), r2_row.get("max_rot_deg", 0)),
            ("max_vel [m/s]", r1_row.get("max_velocity", 0), r2_row.get("max_vel_mps", 0)),
        ]
        for name, v1, v2 in metrics:
            diff = v2 - v1 if v1 and v2 else 0
            lines.append(f"| {name} | {v1:.2f} | {v2:.2f} | {diff:+.2f} |")

        comp_path.write_text("\n".join(lines), encoding="utf-8")
        logger.info(f"  Comparacion replicacion: {comp_path}")


# ---------------------------------------------------------------------------
# Diagnostico de XMLs
# ---------------------------------------------------------------------------

def run_xml_diagnostics(case_ids: list[str]):
    """Verifica consistencia de XMLs de definicion para cada caso."""
    logger.info("\n--- Diagnostico de XMLs ---")
    import re

    for case_id in case_ids:
        case_dir = PROCESSED_DIR / case_id

        # Buscar _Def.xml
        xml_defs = list(case_dir.rglob("*_Def.xml"))
        if not xml_defs:
            logger.warning(f"  {case_id}: sin XML de definicion")
            continue

        xml_text = xml_defs[0].read_text(encoding="utf-8", errors="ignore")

        dp = None
        match = re.search(r'<definition\s+dp="([^"]+)"', xml_text)
        if match:
            dp = float(match.group(1))

        massbody = None
        match = re.search(r'<massbody\s+value="([^"]+)"', xml_text)
        if match:
            massbody = float(match.group(1))

        timemax = None
        match = re.search(r'key="TimeMax"\s+value="([^"]+)"', xml_text)
        if match:
            timemax = float(match.group(1))

        ftpause = None
        match = re.search(r'key="FtPause"\s+value="([^"]+)"', xml_text)
        if match:
            ftpause = float(match.group(1))

        issues = []
        if dp and abs(dp - 0.004) > 1e-6:
            issues.append(f"dp={dp} (esperado 0.004)")
        if timemax and abs(timemax - 10.0) > 0.1:
            issues.append(f"TimeMax={timemax} (esperado 10.0)")
        if ftpause is not None and abs(ftpause - 0.5) > 0.01:
            issues.append(f"FtPause={ftpause} (esperado 0.5)")

        status = "OK" if not issues else f"REVISAR: {', '.join(issues)}"
        logger.info(f"  {case_id}: dp={dp}, mass={massbody}, TimeMax={timemax}, "
                     f"FtPause={ftpause} -> {status}")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Importa y analiza resultados de screening round 2 desde la WS."
    )
    parser.add_argument("--zip", required=True, help="ZIP generado por collect_ws_results.py")
    parser.add_argument("--skip-analysis", action="store_true", help="Solo extraer, no analizar")
    parser.add_argument("--only-analysis", action="store_true",
                        help="Solo analisis (datos ya extraidos)")
    args = parser.parse_args(argv)

    zip_path = Path(args.zip).resolve()

    print("=" * 65)
    print("  Import Round 2: WS -> Laptop")
    print("=" * 65)

    # Paso 1: Extraer
    if not args.only_analysis:
        if not zip_path.exists():
            print(f"ERROR: ZIP no encontrado: {zip_path}")
            return 1
        case_ids = extract_zip(zip_path)
    else:
        # Detectar casos ya extraidos
        case_ids = sorted(
            d.name for d in PROCESSED_DIR.iterdir()
            if d.is_dir() and d.name.startswith("sc2_")
        )
        if not case_ids:
            print("ERROR: No se encontraron casos sc2_* en data/processed/")
            return 1
        logger.info(f"Usando {len(case_ids)} casos ya extraidos: {case_ids}")

    # Paso 2: Diagnostico XML
    run_xml_diagnostics(case_ids)

    if args.skip_analysis:
        logger.info("Skip analysis solicitado. Datos extraidos listos.")
        return 0

    # Paso 3: Procesar con data_cleaner
    results = process_all_cases(case_ids)

    # Paso 4: Guardar en SQLite
    save_results(results)

    # Paso 5: Analisis y figuras
    generate_analysis(results)

    print()
    print("=" * 65)
    print(f"  Importacion completa: {len(results)} casos procesados")
    print(f"  SQLite: {DB_PATH}")
    print(f"  CSV: {RESULTS_DIR / 'results_round2.csv'}")
    print(f"  Reporte: {FIGURES_DIR / 'screening_round2_report.md'}")
    print("=" * 65)

    return 0


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s: %(message)s",
        datefmt="%H:%M:%S",
    )
    sys.exit(main())
