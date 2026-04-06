"""
run_convergence_v2.py — Estudio de Convergencia dp (configuracion nueva)

Caso fijo (Moris): dam_h=0.30, dam_length=1.5, mass=1.0, friction=0.3,
rot_z=0, slope=1:20, canal 15m, altura 1.5m, BLIR3 @ 0.04.

dp obligatorios: 0.010, 0.008, 0.006, 0.005, 0.004, 0.003, 0.002
dp exploratorios: 0.0015, 0.001 (limite hardware, correr solo si los
anteriores completan)

Metricas primarias (decision dp): displacement, velocity, SPH force
Metricas diagnostico: rotation (solo promueve a primaria si monotonica)
No criterio: contact_force, water_h, flow_vel

Post-analisis: Richardson extrapolation + GCI (Celik 2008) + razon asintotica

Uso:
    python scripts/run_convergence_v2.py                  # Todos los dp
    python scripts/run_convergence_v2.py --desde 0.005    # Retomar
    python scripts/run_convergence_v2.py --solo-analisis  # Solo GCI con datos existentes

Autor: Kevin Cortes (UCN 2026)
"""

import sys
import json
import logging
import time
from datetime import datetime
from pathlib import Path

import numpy as np
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from geometry_builder import CaseParams, build_case, compute_boulder_properties
from canal_generator import get_boulder_position
from batch_runner import load_config, run_case
from data_cleaner import process_case, save_to_sqlite

logger = logging.getLogger(__name__)

# ═══════════════════════════════════════════════════════════════════════════
# CONFIGURACION (NO MODIFICAR ENTRE CORRIDAS)
# ═══════════════════════════════════════════════════════════════════════════

# dp obligatorios + exploratorios
DP_CORE = [0.010, 0.008, 0.006, 0.005, 0.004, 0.003, 0.002]
DP_EXPLORATORY = [0.0015, 0.001]
DP_ALL = DP_CORE + DP_EXPLORATORY

# Caso fijo — Moris + centro del rango parametrico
SLOPE_INV = 20.0
BOULDER_POS = get_boulder_position(slope_inv=SLOPE_INV)

BASE_PARAMS = {
    "dam_height": 0.30,
    "dam_length": 1.5,
    "boulder_mass": 1.0,
    "boulder_scale": 0.04,
    "boulder_pos": BOULDER_POS,
    "boulder_rot": (0.0, 0.0, 0.0),
    "material": "pvc",
    "friction_coefficient": 0.3,
    "slope_inv": SLOPE_INV,
    "time_max": 10.0,
    "ft_pause": 0.5,
    "chrono_savedata": 0.001,
}

STATUS_FILE = PROJECT_ROOT / "data" / "logs" / "convergencia_v2_status.json"
RESULTS_CSV = PROJECT_ROOT / "data" / "results" / "convergencia_v2.csv"
LOG_FILE = PROJECT_ROOT / "data" / "logs" / "convergencia_v2.log"


# ═══════════════════════════════════════════════════════════════════════════
# GCI ENGINE (Celik 2008) — reutilizado de convergencia_formal.py
# ═══════════════════════════════════════════════════════════════════════════

def celik_apparent_order(phi1, phi2, phi3, r21, r32, p_formal=2.0,
                         max_iter=200, tol=1e-8):
    eps21 = phi2 - phi1
    eps32 = phi3 - phi2
    if abs(eps21) < 1e-15 or abs(eps32) < 1e-15:
        return np.nan, "degenerate"
    s = np.sign(eps32 / eps21)
    if s > 0 and abs(eps32 / eps21) < 1:
        conv_type = "monotonic"
    elif s > 0:
        conv_type = "divergent"
    else:
        conv_type = "oscillatory"
    p = p_formal
    for _ in range(max_iter):
        try:
            num = r21**p - s
            den = r32**p - s
            if num <= 0 or den <= 0:
                break
            q = np.log(num / den)
            p_new = (1.0 / np.log(r21)) * abs(np.log(abs(eps32 / eps21)) + q)
        except (ValueError, ZeroDivisionError):
            break
        if abs(p_new - p) < tol:
            p = p_new
            break
        p = p_new
    p = np.clip(p, 0.5, max(p_formal, 4.0))
    return p, conv_type


def richardson_extrapolate(phi1, phi2, r21, p):
    return phi1 + (phi1 - phi2) / (r21**p - 1)


def compute_gci(phi1, phi2, phi3, r21, r32, p, Fs=1.25):
    eps21 = phi2 - phi1
    eps32 = phi3 - phi2
    e_a21 = abs(eps21 / phi1) if abs(phi1) > 1e-15 else np.nan
    e_a32 = abs(eps32 / phi2) if abs(phi2) > 1e-15 else np.nan
    phi_ext = richardson_extrapolate(phi1, phi2, r21, p)
    e_ext = abs(phi_ext - phi1) / abs(phi_ext) if abs(phi_ext) > 1e-15 else np.nan
    gci_fine = Fs * e_a21 / (r21**p - 1)
    gci_med = Fs * e_a32 / (r32**p - 1)
    ar = gci_med / (r21**p * gci_fine) if abs(gci_fine) > 1e-15 else np.nan
    return {
        "phi_ext": phi_ext, "e_a21": e_a21, "e_a32": e_a32,
        "e_ext": e_ext, "GCI_fine": gci_fine, "GCI_med": gci_med,
        "AR": ar, "in_asymptotic": (0.9 < ar < 1.1) if not np.isnan(ar) else False,
    }


# ═══════════════════════════════════════════════════════════════════════════
# STATUS (monitoreo remoto)
# ═══════════════════════════════════════════════════════════════════════════

def update_status(dp, idx, total, estado, resultados, t0):
    elapsed = (time.time() - t0) / 60
    ok = [r for r in resultados if r.get("status") == "OK"]
    status = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "dp_actual": dp, "estado": estado,
        "progreso": f"{idx}/{total}",
        "completados_ok": len(ok),
        "tiempo_min": round(elapsed, 1),
        "dp_pendientes": [d for d in DP_ALL[idx:]],
    }
    STATUS_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(STATUS_FILE, "w") as f:
        json.dump(status, f, indent=2, default=str)


# ═══════════════════════════════════════════════════════════════════════════
# PIPELINE POR DP
# ═══════════════════════════════════════════════════════════════════════════

def run_single_dp(dp, config, d_eq):
    case_name = f"conv2_dp{str(dp).replace('.', '')}"
    start = time.time()
    entry = {"dp": dp, "case_name": case_name, "status": "ERROR"}

    template_xml = PROJECT_ROOT / config["paths"]["template_xml"]
    boulder_stl = PROJECT_ROOT / config["paths"]["boulder_stl"]
    beach_stl = PROJECT_ROOT / config["paths"]["beach_stl"]
    materials_xml = PROJECT_ROOT / config["paths"]["materials_xml"]
    cases_dir = PROJECT_ROOT / config["paths"]["cases_dir"]
    processed_dir = PROJECT_ROOT / config["paths"]["processed_dir"] / case_name

    params = CaseParams(
        case_name=case_name,
        dp=dp,
        dam_height=BASE_PARAMS["dam_height"],
        dam_length=BASE_PARAMS["dam_length"],
        boulder_mass=BASE_PARAMS["boulder_mass"],
        boulder_scale=BASE_PARAMS["boulder_scale"],
        boulder_pos=BASE_PARAMS["boulder_pos"],
        boulder_rot=BASE_PARAMS["boulder_rot"],
        material=BASE_PARAMS["material"],
        friction_coefficient=BASE_PARAMS["friction_coefficient"],
        slope_inv=BASE_PARAMS["slope_inv"],
        time_max=BASE_PARAMS["time_max"],
        time_out=BASE_PARAMS["time_max"],
        ft_pause=BASE_PARAMS["ft_pause"],
        chrono_savedata=BASE_PARAMS["chrono_savedata"],
    )

    # 1. Geometry
    try:
        xml_path = build_case(
            template_xml=template_xml, boulder_stl=boulder_stl,
            beach_stl=beach_stl, materials_xml=materials_xml,
            output_dir=cases_dir, params=params,
        )
    except Exception as e:
        entry["error"] = f"GenCase prep: {e}"
        entry["tiempo_min"] = (time.time() - start) / 60
        return entry

    case_dir = xml_path.parent
    logger.info("  [1/3] Geometry OK")

    # 2. Simulacion
    try:
        run_result = run_case(case_dir, config, processed_dir)
    except Exception as e:
        entry["error"] = f"Sim exception: {e}"
        entry["tiempo_min"] = (time.time() - start) / 60
        return entry

    if not run_result["success"]:
        entry["status"] = "FALLO_SIM"
        entry["error"] = run_result.get("error_message", "unknown")
        entry["tiempo_min"] = (time.time() - start) / 60
        logger.error(f"  [2/3] Sim FALLO: {entry['error']}")
        return entry

    logger.info(f"  [2/3] Sim OK ({run_result['duration_s']:.0f}s)")

    # 3. Analisis — extraer TODA la info
    try:
        cr = process_case(processed_dir, d_eq=d_eq,
                          boulder_mass=BASE_PARAMS["boulder_mass"])
    except Exception as e:
        entry["status"] = "FALLO_ANALISIS"
        entry["error"] = f"Analisis: {e}"
        entry["tiempo_min"] = (time.time() - start) / 60
        return entry

    elapsed = (time.time() - start) / 60
    logger.info(f"  [3/3] Analisis OK — {elapsed:.1f} min total")

    # Contar particulas desde Run.csv
    n_particles = _read_particle_count(processed_dir)

    # Leer series temporales para archivo detallado
    _save_temporal_data(processed_dir, case_name, dp)

    entry.update({
        "status": "OK",
        "max_displacement_m": cr.max_displacement,
        "max_rotation_deg": cr.max_rotation,
        "max_velocity_ms": cr.max_velocity,
        "max_sph_force_N": cr.max_sph_force,
        "max_contact_force_N": cr.max_contact_force,
        "max_flow_velocity_ms": cr.max_flow_velocity,
        "max_water_height_m": cr.max_water_height,
        "sim_time_s": cr.sim_time_reached,
        "n_timesteps": cr.n_timesteps,
        "n_particles": n_particles,
        "tiempo_min": elapsed,
        "vram_estimated_gb": n_particles * 120 / 1e9 if n_particles else None,
        "_case_result": cr,
    })
    return entry


def _read_particle_count(processed_dir):
    run_csv = processed_dir / "Run.csv"
    if not run_csv.exists():
        for f in processed_dir.rglob("Run.csv"):
            run_csv = f
            break
    if not run_csv.exists():
        return None
    try:
        df = pd.read_csv(run_csv, sep=";", nrows=1)
        for col in df.columns:
            if "np" in col.lower().strip():
                return int(float(df[col].iloc[0]))
    except Exception:
        pass
    return None


def _save_temporal_data(processed_dir, case_name, dp):
    """Guarda series temporales completas para analisis post."""
    out_dir = PROJECT_ROOT / "data" / "results" / "convergencia_v2_temporal"
    out_dir.mkdir(parents=True, exist_ok=True)

    # ChronoExchange
    for f in processed_dir.rglob("ChronoExchange_mkbound_*.csv"):
        dest = out_dir / f"{case_name}_exchange.csv"
        import shutil
        shutil.copy2(str(f), str(dest))
        break

    # ChronoBody_forces
    for f in processed_dir.rglob("ChronoBody_forces.csv"):
        dest = out_dir / f"{case_name}_forces.csv"
        import shutil
        shutil.copy2(str(f), str(dest))
        break


# ═══════════════════════════════════════════════════════════════════════════
# ANALISIS GCI POST-ESTUDIO
# ═══════════════════════════════════════════════════════════════════════════

def run_gci_analysis(df_ok):
    """Calcula GCI para las 3 mallas mas finas exitosas."""
    if len(df_ok) < 3:
        logger.warning("Menos de 3 dp exitosos — no se puede calcular GCI")
        return None

    # Ordenar de fino a grueso
    df_sorted = df_ok.sort_values("dp").reset_index(drop=True)

    # Metricas a analizar
    metrics = {
        "displacement": ("max_displacement_m", "m"),
        "velocity": ("max_velocity_ms", "m/s"),
        "sph_force": ("max_sph_force_N", "N"),
        "rotation": ("max_rotation_deg", "deg"),
    }

    primary = ["displacement", "velocity", "sph_force"]

    results = {}
    logger.info("\n" + "=" * 65)
    logger.info("ANALISIS GCI (Celik 2008)")
    logger.info("=" * 65)

    # Analizar con ventana deslizante de 3 puntos (fino → grueso)
    for name, (col, unit) in metrics.items():
        is_primary = name in primary
        tag = "PRIMARIA" if is_primary else "DIAGNOSTICO"
        logger.info(f"\n--- {name} ({tag}) ---")

        values = df_sorted[col].values
        dps = df_sorted["dp"].values

        # Usar las 3 mallas mas finas
        phi1, phi2, phi3 = values[0], values[1], values[2]
        r21 = dps[1] / dps[0]
        r32 = dps[2] / dps[1]

        p, conv_type = celik_apparent_order(phi1, phi2, phi3, r21, r32)
        gci = compute_gci(phi1, phi2, phi3, r21, r32, p)

        logger.info(f"  Mallas: dp={dps[0]}, {dps[1]}, {dps[2]}")
        logger.info(f"  Valores: {phi1:.6f}, {phi2:.6f}, {phi3:.6f} {unit}")
        logger.info(f"  Orden aparente p = {p:.2f}")
        logger.info(f"  Tipo convergencia: {conv_type}")
        logger.info(f"  Richardson extrap: {gci['phi_ext']:.6f} {unit}")
        logger.info(f"  GCI_fine = {gci['GCI_fine']*100:.2f}%")
        logger.info(f"  GCI_med  = {gci['GCI_med']*100:.2f}%")
        logger.info(f"  AR = {gci['AR']:.3f} ({'asintotico' if gci['in_asymptotic'] else 'NO asintotico'})")

        # Deltas entre niveles consecutivos
        logger.info(f"  Deltas entre niveles:")
        for i in range(len(values) - 1):
            delta = abs(values[i] - values[i+1])
            pct = delta / abs(values[i]) * 100 if abs(values[i]) > 1e-15 else 0
            logger.info(f"    dp {dps[i]:.4f} -> {dps[i+1]:.4f}: "
                        f"delta={delta:.6f} {unit} ({pct:.1f}%)")

        results[name] = {
            "col": col, "unit": unit, "is_primary": is_primary,
            "p": p, "conv_type": conv_type, **gci,
            "values": values.tolist(), "dps": dps.tolist(),
        }

    # Veredicto
    logger.info("\n" + "=" * 65)
    logger.info("VEREDICTO")
    logger.info("=" * 65)

    for name in primary:
        r = results[name]
        gci_pct = r["GCI_fine"] * 100
        verdict = "OK" if gci_pct < 5 else "ACEPTABLE" if gci_pct < 10 else "INSUFICIENTE"
        logger.info(f"  {name}: GCI={gci_pct:.2f}%, p={r['p']:.2f}, "
                    f"tipo={r['conv_type']}, AR={r['AR']:.3f} -> {verdict}")

    # Rotation diagnostico
    if "rotation" in results:
        r = results["rotation"]
        if r["conv_type"] == "monotonic":
            logger.info(f"  rotation: MONOTONICA (p={r['p']:.2f}, GCI={r['GCI_fine']*100:.2f}%) "
                        f"-> podria promoverse a primaria")
        else:
            logger.info(f"  rotation: {r['conv_type']} -> se mantiene como diagnostico")

    # Guardar JSON
    json_path = PROJECT_ROOT / "data" / "results" / "convergencia_v2_gci.json"
    with open(json_path, "w") as f:
        json.dump(results, f, indent=2, default=str)
    logger.info(f"\nGCI JSON: {json_path}")

    return results


# ═══════════════════════════════════════════════════════════════════════════
# ESTUDIO COMPLETO
# ═══════════════════════════════════════════════════════════════════════════

def run_convergence_study(desde_dp=None, solo_analisis=False):

    if solo_analisis:
        logger.info("Modo solo-analisis: leyendo CSV existente")
        if not RESULTS_CSV.exists():
            logger.error(f"No existe {RESULTS_CSV}")
            return
        df = pd.read_csv(RESULTS_CSV, sep=";")
        df_ok = df[df["status"] == "OK"].sort_values("dp", ascending=True)
        run_gci_analysis(df_ok)
        return

    dp_to_run = DP_ALL
    if desde_dp is not None:
        dp_to_run = [dp for dp in DP_ALL if dp <= desde_dp]
        logger.info(f"Retomando desde dp={desde_dp}")

    logger.info("=" * 65)
    logger.info("ESTUDIO DE CONVERGENCIA v2 — Config nueva (Moris)")
    logger.info("=" * 65)
    logger.info(f"dp a probar: {dp_to_run}")
    logger.info(f"Caso fijo: dam_h={BASE_PARAMS['dam_height']}m, "
                f"mass={BASE_PARAMS['boulder_mass']}kg, "
                f"fric={BASE_PARAMS['friction_coefficient']}, "
                f"slope=1:{int(BASE_PARAMS['slope_inv'])}")
    logger.info(f"Boulder pos: {BOULDER_POS}")
    logger.info(f"Metricas primarias: displacement, velocity, SPH force")
    logger.info(f"Diagnostico: rotation")
    logger.info("=" * 65)

    config = load_config(PROJECT_ROOT / "config" / "dsph_config.json")

    boulder_props = compute_boulder_properties(
        stl_path=PROJECT_ROOT / config["paths"]["boulder_stl"],
        scale=BASE_PARAMS["boulder_scale"],
        rotation_deg=BASE_PARAMS["boulder_rot"],
        mass_kg=BASE_PARAMS["boulder_mass"],
    )
    d_eq = boulder_props["d_eq"]
    logger.info(f"d_eq = {d_eq:.6f} m")

    # Cargar resultados previos si existen (para retomar)
    resultados = []
    if desde_dp and RESULTS_CSV.exists():
        prev = pd.read_csv(RESULTS_CSV, sep=";")
        for _, row in prev.iterrows():
            if row["dp"] not in [d for d in dp_to_run]:
                resultados.append(row.to_dict())
        logger.info(f"Cargados {len(resultados)} resultados previos")

    t0 = time.time()

    for i, dp in enumerate(dp_to_run, 1):
        # Saltar si ya existe resultado OK
        existing = [r for r in resultados if abs(r.get("dp", 0) - dp) < 1e-8
                     and r.get("status") == "OK"]
        if existing:
            logger.info(f"\n[{i}/{len(dp_to_run)}] dp={dp} — ya completado, saltando")
            continue

        is_exploratory = dp in DP_EXPLORATORY
        tag = " [EXPLORATORIO]" if is_exploratory else ""

        logger.info(f"\n{'='*65}")
        logger.info(f"[{i}/{len(dp_to_run)}] dp = {dp}{tag}")
        logger.info(f"{'='*65}")

        update_status(dp, i - 1, len(dp_to_run), f"CORRIENDO dp={dp}", resultados, t0)

        try:
            entry = run_single_dp(dp, config, d_eq)
        except Exception as e:
            logger.error(f"Excepcion: {e}", exc_info=True)
            entry = {"dp": dp, "case_name": f"conv2_dp{str(dp).replace('.','')}",
                     "status": "ERROR", "error": str(e), "tiempo_min": 0}

        # Limpiar _case_result antes de guardar
        cr = entry.pop("_case_result", None)
        resultados.append(entry)

        # Guardar CSV incremental (por si crashea entre dp)
        _save_results_csv(resultados)

        # Guardar en SQLite
        if cr:
            try:
                save_to_sqlite([cr], PROJECT_ROOT / "data" / "results.sqlite",
                               table="convergence_v2")
            except Exception:
                pass

        update_status(dp, i, len(dp_to_run), f"TERMINADO dp={dp}", resultados, t0)

        # Si es exploratorio y fallo, parar
        if is_exploratory and entry["status"] != "OK":
            logger.warning(f"dp={dp} exploratorio fallo — deteniendo estudio")
            logger.warning(f"Error: {entry.get('error', '?')}")
            break

    total_min = (time.time() - t0) / 60

    # Tabla resumen
    _print_summary(resultados, total_min)

    # GCI
    df = pd.DataFrame(resultados)
    df_ok = df[df["status"] == "OK"].sort_values("dp", ascending=True)
    if len(df_ok) >= 3:
        run_gci_analysis(df_ok)

    update_status(0, len(dp_to_run), len(dp_to_run), "COMPLETADO", resultados, t0)


def _save_results_csv(resultados):
    RESULTS_CSV.parent.mkdir(parents=True, exist_ok=True)
    df = pd.DataFrame(resultados)
    df.to_csv(RESULTS_CSV, index=False, sep=";")


def _print_summary(resultados, total_min):
    ok = [r for r in resultados if r.get("status") == "OK"]
    logger.info(f"\n{'='*65}")
    logger.info("RESUMEN CONVERGENCIA")
    logger.info(f"{'='*65}")

    if ok:
        header = (f"{'dp':>8}  {'Np':>10}  {'VRAM_GB':>8}  "
                  f"{'disp(m)':>10}  {'d%':>5}  "
                  f"{'vel(m/s)':>9}  {'d%':>5}  "
                  f"{'Fsph(N)':>9}  {'d%':>5}  "
                  f"{'rot(deg)':>9}  {'t(min)':>8}")
        logger.info(header)
        logger.info("-" * len(header))

        prev = {}
        for r in sorted(ok, key=lambda x: -x["dp"]):
            dp = r["dp"]
            disp = r["max_displacement_m"]
            vel = r["max_velocity_ms"]
            fsph = r["max_sph_force_N"]
            rot = r["max_rotation_deg"]
            np_val = r.get("n_particles", 0) or 0
            vram = r.get("vram_estimated_gb", 0) or 0

            d_disp = _delta_pct(disp, prev.get("disp"))
            d_vel = _delta_pct(vel, prev.get("vel"))
            d_fsph = _delta_pct(fsph, prev.get("fsph"))

            logger.info(
                f"{dp:>8.4f}  {np_val:>10.0f}  {vram:>8.1f}  "
                f"{disp:>10.6f}  {d_disp:>5}  "
                f"{vel:>9.4f}  {d_vel:>5}  "
                f"{fsph:>9.4f}  {d_fsph:>5}  "
                f"{rot:>9.2f}  {r['tiempo_min']:>8.1f}"
            )
            prev = {"disp": disp, "vel": vel, "fsph": fsph}

    failed = [r for r in resultados if r.get("status") != "OK"]
    if failed:
        logger.warning(f"\nFallidos:")
        for r in failed:
            logger.warning(f"  dp={r['dp']}: {r.get('error', '?')}")

    logger.info(f"\n{len(ok)}/{len(resultados)} exitosos, total {total_min:.1f} min")
    logger.info(f"CSV: {RESULTS_CSV}")


def _delta_pct(current, previous):
    if previous is None or abs(previous) < 1e-15:
        return ""
    pct = abs(current - previous) / abs(previous) * 100
    return f"{pct:.1f}%"


# ═══════════════════════════════════════════════════════════════════════════
# CLI
# ═══════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s: %(message)s",
        datefmt="%H:%M:%S",
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler(LOG_FILE, encoding="utf-8"),
        ],
    )

    desde = None
    solo_analisis = False

    args = sys.argv[1:]
    i = 0
    while i < len(args):
        if args[i] == "--desde" and i + 1 < len(args):
            desde = float(args[i + 1])
            i += 2
        elif args[i] == "--solo-analisis":
            solo_analisis = True
            i += 1
        else:
            print(f"Uso: python run_convergence_v2.py [--desde DP] [--solo-analisis]")
            sys.exit(1)

    run_convergence_study(desde_dp=desde, solo_analisis=solo_analisis)
