"""
collect_ws_results.py — Recolecta resultados completos desde la WS.

Copia TODA la data util de cada caso en un ZIP compacto para analisis
profundo en la laptop. Solo excluye archivos binarios pesados que son
regenerables (.bi4, .ibi4, .obi4) y VTKs grandes.

Incluye:
  - Todos los CSVs (Chrono, Gauges, Run, RunPARTs)
  - XMLs de definicion y generados (parametros exactos de la sim)
  - Logs (.out) del solver y GenCase
  - Propiedades del boulder (boulder_properties.txt)
  - Geometria de colision Chrono (chrono_objs/*.obj)
  - ChronoGeo (.cbi4, pequeno)
  - VTKs de configuracion (CfgChrono, CfgGauge, CfgInit — pequenos)

Excluye (pesados, regenerables):
  - data/Part_*.bi4 (snapshots de particulas, GB cada uno)
  - data/*.ibi4, data/*.obi4 (indices y out-particles)
  - *.bi4 en raiz de _out (geometria GenCase, ~100MB+)
  - VTKs grandes de GenCase (*_All, *_Bound, *_Fluid, *_FreePt, *_MkCells, *_beach_*, *_dbg-*)
  - Copias de STL en _out (ya estan en models/)

Uso en la WS:
  python collect_ws_results.py
  python collect_ws_results.py --cases-dir D:\\SPH-Prod\\cases
  python collect_ws_results.py --prefix sc2_ --output round2.zip
  python collect_ws_results.py --all  # todos los casos, no solo sc2_

Autor: Kevin Cortes (UCN 2026)
"""

from __future__ import annotations

import argparse
import json
import sys
import zipfile
from datetime import datetime
from pathlib import Path

# Extensiones binarias pesadas a excluir
HEAVY_EXTENSIONS = {".bi4", ".ibi4", ".obi4"}

# Patrones de VTK grandes de GenCase (regenerables)
HEAVY_VTK_SUFFIXES = [
    "_All.vtk",
    "_Bound.vtk",
    "_Fluid.vtk",
    "_FreePt.vtk",
    "_MkCells.vtk",
]
HEAVY_VTK_CONTAINS = ["_beach_", "_dbg-"]

# STLs duplicados en _out (ya estan en models/)
SKIP_EXTENSIONS_IN_OUT = {".stl"}


def is_heavy_file(filepath: Path, case_name: str) -> bool:
    """Determina si un archivo es pesado y descartable."""
    name = filepath.name
    suffix = filepath.suffix.lower()

    # Binarios de particulas
    if suffix in HEAVY_EXTENSIONS:
        return True

    # VTKs grandes de GenCase
    if suffix == ".vtk":
        for s in HEAVY_VTK_SUFFIXES:
            if name.endswith(s):
                return True
        for c in HEAVY_VTK_CONTAINS:
            if c in name:
                return True

    # STLs duplicados dentro de _out
    if suffix in SKIP_EXTENSIONS_IN_OUT and "_out" in str(filepath):
        return True

    # Floating_Materials.xml duplicado en _out
    if name == "Floating_Materials.xml" and "_out" in str(filepath):
        return True

    return False


def collect_case(case_dir: Path, zf: zipfile.ZipFile, prefix: str) -> dict:
    """Recolecta todos los archivos utiles de un caso."""
    collected = []
    skipped = []
    total_size = 0
    skipped_size = 0

    case_name = case_dir.name

    for filepath in sorted(case_dir.rglob("*")):
        if not filepath.is_file():
            continue

        if is_heavy_file(filepath, case_name):
            skipped.append(filepath.name)
            skipped_size += filepath.stat().st_size
            continue

        rel_path = filepath.relative_to(case_dir)
        arcname = f"{prefix}/{rel_path}"
        zf.write(str(filepath), arcname)
        fsize = filepath.stat().st_size
        collected.append(str(rel_path))
        total_size += fsize

    # Diagnostico rapido
    has_exchange = any("ChronoExchange" in f for f in collected)
    has_run = any(f == "Run.csv" or f.endswith("/Run.csv") or f.endswith("\\Run.csv") for f in collected)
    has_xml_def = any(f.endswith("_Def.xml") for f in collected)
    has_xml_gen = any(f.endswith(".xml") and "_Def" not in f for f in collected)
    has_log = any(f.endswith(".out") for f in collected)
    n_gauges_vel = sum(1 for f in collected if "GaugesVel_V" in f)
    n_gauges_hmax = sum(1 for f in collected if "GaugesMaxZ_hmax" in f)

    status = "OK"
    issues = []
    if not has_exchange:
        issues.append("SIN_EXCHANGE")
    if not has_run:
        issues.append("SIN_RUN")
    if not has_xml_def:
        issues.append("SIN_XML_DEF")
    if issues:
        status = "+".join(issues)

    return {
        "case_id": prefix,
        "data_dir": str(case_dir),
        "files_collected": len(collected),
        "files_skipped": len(skipped),
        "size_collected_mb": round(total_size / (1024 * 1024), 2),
        "size_skipped_mb": round(skipped_size / (1024 * 1024), 2),
        "has_exchange": has_exchange,
        "has_run": has_run,
        "has_xml_def": has_xml_def,
        "has_xml_generated": has_xml_gen,
        "has_log": has_log,
        "n_gauges_vel": n_gauges_vel,
        "n_gauges_hmax": n_gauges_hmax,
        "status": status,
    }


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Recolecta data completa de casos SPH en un ZIP (sin binarios pesados)."
    )
    parser.add_argument(
        "--cases-dir",
        default="cases",
        help="Directorio con las carpetas de casos (default: cases/)",
    )
    parser.add_argument(
        "--prefix",
        default="sc2_",
        help="Prefijo de los casos a recolectar (default: sc2_)",
    )
    parser.add_argument(
        "--output",
        default=None,
        help="Nombre del ZIP de salida (default: round2_results_FECHA.zip)",
    )
    parser.add_argument(
        "--all",
        action="store_true",
        help="Recolectar TODOS los casos, no solo los que matchean --prefix",
    )
    args = parser.parse_args(argv)

    cases_dir = Path(args.cases_dir).resolve()
    if not cases_dir.exists():
        print(f"ERROR: Directorio de casos no encontrado: {cases_dir}")
        return 1

    # Encontrar casos
    case_dirs = sorted(
        d for d in cases_dir.iterdir()
        if d.is_dir() and (args.all or d.name.startswith(args.prefix))
    )

    if not case_dirs:
        print(f"ERROR: No se encontraron casos con prefijo '{args.prefix}' en {cases_dir}")
        dirs_found = [d.name for d in cases_dir.iterdir() if d.is_dir()][:20]
        print(f"Carpetas encontradas: {dirs_found}")
        return 1

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_path = Path(args.output) if args.output else Path(f"round2_results_{timestamp}.zip")

    print("=" * 65)
    print("  Recolectando resultados para analisis profundo")
    print("=" * 65)
    print(f"  Directorio:  {cases_dir}")
    print(f"  Casos:       {len(case_dirs)}")
    print(f"  Output:      {output_path}")
    print(f"  Excluye:     .bi4, .ibi4, .obi4, VTKs grandes, STLs duplicados")
    print()

    summaries = []
    with zipfile.ZipFile(str(output_path), "w", zipfile.ZIP_DEFLATED) as zf:
        for case_dir in case_dirs:
            case_id = case_dir.name
            print(f"  [{case_id}] ", end="", flush=True)
            try:
                summary = collect_case(case_dir, zf, case_id)
                summaries.append(summary)
                print(
                    f"{summary['status']}  "
                    f"({summary['files_collected']} files, "
                    f"{summary['size_collected_mb']:.1f} MB kept, "
                    f"{summary['size_skipped_mb']:.1f} MB skipped)"
                )
            except Exception as e:
                print(f"ERROR: {e}")
                summaries.append({"case_id": case_id, "status": f"ERROR: {e}"})

        # Manifiesto con toda la metadata
        manifest = {
            "timestamp": timestamp,
            "source_dir": str(cases_dir),
            "collection_script": "collect_ws_results.py",
            "prefix_filter": args.prefix if not args.all else "(all)",
            "exclusions": {
                "heavy_extensions": list(HEAVY_EXTENSIONS),
                "heavy_vtk_suffixes": HEAVY_VTK_SUFFIXES,
                "note": "Particle binaries and large GenCase VTKs excluded (regenerable)",
            },
            "cases": summaries,
        }
        zf.writestr("manifest.json", json.dumps(manifest, indent=2, ensure_ascii=False))

    # Resumen final
    zip_size = output_path.stat().st_size / (1024 * 1024)
    total_collected = sum(s.get("size_collected_mb", 0) for s in summaries)
    total_skipped = sum(s.get("size_skipped_mb", 0) for s in summaries)
    ok_count = sum(1 for s in summaries if s.get("status") == "OK")

    print()
    print("=" * 65)
    print(f"  ZIP creado: {output_path}")
    print(f"  Tamano ZIP: {zip_size:.1f} MB (de {total_collected:.0f} MB recolectados)")
    print(f"  Descartados: {total_skipped:.0f} MB en binarios pesados")
    print(f"  Casos OK: {ok_count}/{len(summaries)}")
    if ok_count < len(summaries):
        for s in summaries:
            if s.get("status", "") != "OK":
                print(f"    ATENCION: {s['case_id']} -> {s.get('status', '?')}")
    print("=" * 65)
    print()
    print("Siguiente paso: copiar ZIP a la laptop y ejecutar:")
    print(f"  python scripts/import_round2.py --zip {output_path.name}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
