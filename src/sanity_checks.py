"""
sanity_checks.py — Verificaciones fisicas automaticas para resultados SPH.

Valida que los resultados de simulacion DualSPHysics + Chrono sean fisicamente
consistentes, usando ecuaciones empiricas y heuristicas de orden de magnitud.

Checks implementados:
  1. Monotonicidad: dam_h↑ → disp↑, mass↑ → disp↓
  2. Ritter: velocidad del frente vs 2*sqrt(g*h0), tolerancia 15%
  3. Magnitudes: desplazamiento, rotacion en rangos razonables
  4. Fuerzas: fuerza SPH > 0 y < 10*peso del boulder
  5. Suavidad: curvas temporales sin oscilaciones espurias

Referencias:
  - Ritter (1892): v_front = 2*sqrt(g*h0)
  - Nandasena et al. (2011): velocidad minima para sliding
  - Cox et al. (2020): critica sistematica de ecuaciones empiricas
  - docs/RESEARCH_EMPIRICAL_SANITY.md (compilacion completa)

Autor: Kevin Cortes (UCN 2026)
"""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)

G = 9.81  # m/s^2


# ---------------------------------------------------------------------------
# Individual checks
# ---------------------------------------------------------------------------

def check_monotonicity(results_df: pd.DataFrame) -> Dict:
    """
    Verifica tendencias monotónicas esperadas:
      - dam_height sube → max_displacement sube (correlacion positiva)
      - boulder_mass sube → max_displacement baja (correlacion negativa)

    Usa correlacion de Spearman (rank-based, robusta a no-linealidad).
    Requiere al menos 3 puntos con variacion en cada parametro.
    """
    from scipy.stats import spearmanr

    result = {'name': 'monotonicity', 'passed': True, 'details': {}}

    # --- dam_h vs displacement ---
    dam_h = results_df['dam_height'].values
    disp = results_df['max_displacement'].values

    if len(np.unique(dam_h)) >= 3:
        rho, pval = spearmanr(dam_h, disp)
        dam_ok = rho > 0
        result['details']['dam_h_vs_disp'] = {
            'spearman_rho': float(rho),
            'p_value': float(pval),
            'expected': 'positive',
            'passed': bool(dam_ok),
        }
        if not dam_ok:
            result['passed'] = False
            logger.warning("MONOTONICITY FAIL: dam_h vs displacement rho=%.3f (expected >0)", rho)
    else:
        result['details']['dam_h_vs_disp'] = {
            'skipped': True,
            'reason': 'Need >=3 unique dam_height values',
        }

    # --- mass vs displacement ---
    mass = results_df['boulder_mass'].values

    if len(np.unique(mass)) >= 3:
        rho, pval = spearmanr(mass, disp)
        mass_ok = rho < 0
        result['details']['mass_vs_disp'] = {
            'spearman_rho': float(rho),
            'p_value': float(pval),
            'expected': 'negative',
            'passed': bool(mass_ok),
        }
        if not mass_ok:
            result['passed'] = False
            logger.warning("MONOTONICITY FAIL: mass vs displacement rho=%.3f (expected <0)", rho)
    else:
        result['details']['mass_vs_disp'] = {
            'skipped': True,
            'reason': 'Need >=3 unique boulder_mass values',
        }

    logger.info("Monotonicity check: %s", 'PASS' if result['passed'] else 'FAIL')
    return result


def check_ritter(results_df: pd.DataFrame, tolerance: float = 0.15) -> Dict:
    """
    Verifica velocidad del flujo contra solucion analitica de Ritter.

    v_ritter = 2 * sqrt(g * dam_h)
    SPH debe dar v <= v_ritter (friccion, 3D reducen velocidad).
    Tolerancia: SPH puede ser hasta `tolerance` menor que Ritter.
    Si SPH > Ritter: posible error numerico.

    Solo evalua casos con max_flow_velocity > 0 (gauge midio algo).
    """
    result = {'name': 'ritter_velocity', 'passed': True, 'details': []}

    for _, row in results_df.iterrows():
        v_sph = row['max_flow_velocity']
        dam_h = row['dam_height']
        case = row['case_name']

        if v_sph <= 0 or dam_h <= 0:
            result['details'].append({
                'case': case,
                'skipped': True,
                'reason': 'no flow velocity data or dam_h=0',
            })
            continue

        v_ritter = 2.0 * np.sqrt(G * dam_h)
        ratio = v_sph / v_ritter

        # SPH should be <= Ritter (within small margin for numerical overshoot)
        too_high = ratio > 1.05  # allow 5% overshoot for numerics
        too_low = ratio < (1.0 - tolerance - 0.10)  # more than tolerance+10% below is suspicious

        case_passed = not too_high
        detail = {
            'case': case,
            'dam_h': float(dam_h),
            'v_sph': float(v_sph),
            'v_ritter': float(v_ritter),
            'ratio_sph_ritter': float(ratio),
            'passed': bool(case_passed),
        }

        if too_low:
            detail['warning'] = 'SPH velocity unusually low vs Ritter'

        result['details'].append(detail)

        if not case_passed:
            result['passed'] = False
            logger.warning("RITTER FAIL: %s v_sph=%.3f > v_ritter=%.3f (ratio=%.3f)",
                           case, v_sph, v_ritter, ratio)

    logger.info("Ritter velocity check: %s", 'PASS' if result['passed'] else 'FAIL')
    return result


def check_magnitudes(results_df: pd.DataFrame,
                     max_disp: float = 20.0,
                     max_rot: float = 360.0) -> Dict:
    """
    Verifica que magnitudes estan en rangos fisicamente razonables.

    - Desplazamiento: [0, max_disp] m  (canal es 30m, >20m es sospechoso)
    - Rotacion: [0, max_rot] grados
    - Velocidad del boulder: >= 0 y < velocidad del flujo * 1.5
    - max_displacement >= 0 (no puede ir contra el flujo)

    Nota: boulder velocity > flow velocity puede ocurrir legitimamente si
    el gauge no captura el pico del flujo (e.g. dam_h bajo, gauge lejos).
    """
    result = {'name': 'magnitudes', 'passed': True, 'details': []}

    for _, row in results_df.iterrows():
        case = row['case_name']
        issues = []

        d = row['max_displacement']
        r = row['max_rotation']
        v = row['max_velocity']
        v_flow = row['max_flow_velocity']

        if d < 0:
            issues.append('displacement < 0 (impossible)')
        if d > max_disp:
            issues.append('displacement > %.1fm (extreme for lab scale)' % max_disp)
        if r < 0:
            issues.append('rotation < 0 (impossible)')
        if r > max_rot:
            issues.append('rotation > %.0f deg' % max_rot)
        if v < 0:
            issues.append('velocity < 0 (impossible)')
        if v_flow > 0.1 and v > v_flow * 1.5:
            issues.append('boulder velocity (%.2f) > flow velocity (%.2f) * 1.5' % (v, v_flow))

        case_passed = len(issues) == 0
        result['details'].append({
            'case': case,
            'max_displacement': float(d),
            'max_rotation': float(r),
            'max_velocity': float(v),
            'max_flow_velocity': float(v_flow),
            'passed': bool(case_passed),
            'issues': issues,
        })

        if not case_passed:
            result['passed'] = False
            logger.warning("MAGNITUDE FAIL: %s — %s", case, '; '.join(issues))

    logger.info("Magnitudes check: %s", 'PASS' if result['passed'] else 'FAIL')
    return result


def check_forces(results_df: pd.DataFrame) -> Dict:
    """
    Verifica fuerzas SPH contra peso del boulder.

    - Fuerza SPH > 0 cuando hay movimiento
    - Fuerza SPH < 50 * W (donde W = mass * g) — dam-break con dam_h=0.5
      contra boulder ligero (0.8kg) genera fuerzas SPH grandes vs peso
    - Si hay movimiento y F_SPH < mu*W, advertencia (no falla)

    Nota: fuerza de contacto NO se valida (CV=82%, no converge — hallazgo conocido).
    """
    MU_S = 0.65  # coeficiente de friccion estatica tipico

    result = {'name': 'forces', 'passed': True, 'details': []}

    for _, row in results_df.iterrows():
        case = row['case_name']
        mass = row['boulder_mass']
        f_sph = row['max_sph_force']
        moved = bool(row.get('moved', row['max_displacement'] > 0.01))
        issues = []
        warnings = []

        if mass <= 0:
            result['details'].append({
                'case': case, 'boulder_mass': mass, 'passed': False,
                'issues': ['boulder_mass <= 0 (invalid data)'], 'warnings': [],
            })
            result['passed'] = False
            continue

        W = mass * G

        if f_sph < 0:
            issues.append('SPH force < 0 (impossible)')

        if moved and f_sph <= 0:
            issues.append('boulder moved but max SPH force = 0')

        if f_sph > 50 * W:
            issues.append('SPH force (%.1fN) > 50*W (%.1fN) — possible numerical error' % (f_sph, 50 * W))

        if moved and f_sph < MU_S * W and f_sph > 0:
            warnings.append('SPH force (%.1fN) < mu*W (%.1fN) but boulder moved — '
                            'check if contact/other forces contributed' % (f_sph, MU_S * W))

        case_passed = len(issues) == 0
        result['details'].append({
            'case': case,
            'boulder_mass': float(mass),
            'weight': float(W),
            'max_sph_force': float(f_sph),
            'ratio_fsph_weight': float(f_sph / W) if W > 0 else 0.0,
            'passed': bool(case_passed),
            'issues': issues,
            'warnings': warnings,
        })

        if not case_passed:
            result['passed'] = False
            logger.warning("FORCE FAIL: %s — %s", case, '; '.join(issues))
        for w in warnings:
            logger.info("FORCE WARNING: %s — %s", case, w)

    logger.info("Forces check: %s", 'PASS' if result['passed'] else 'FAIL')
    return result


def check_smoothness(case_dir: Path,
                     max_sign_changes_disp: int = 15,
                     max_sign_changes_vel: int = 50) -> Dict:
    """
    Verifica suavidad de curvas temporales leyendo ChronoExchange CSV.

    Checks:
    - Desplazamiento: derivada no debe cambiar signo mas de N veces
      (el boulder avanza, no oscila adelante/atras)
    - Velocidad del boulder: derivada puede oscilar mas, pero no excesivamente
      (pico + decay es normal, spikes de alta frecuencia no)

    Retorna pass/fail + conteo de sign changes.
    """
    try:
        from src.data_cleaner import parse_chrono_exchange, compute_displacement
    except ModuleNotFoundError:
        from data_cleaner import parse_chrono_exchange, compute_displacement

    result = {'name': 'smoothness', 'case': case_dir.name, 'passed': True, 'details': {}}

    chrono_csvs = sorted(case_dir.glob('ChronoExchange*.csv'))
    if not chrono_csvs:
        result['details']['error'] = 'No ChronoExchange CSV found'
        result['passed'] = False
        return result

    try:
        df = parse_chrono_exchange(chrono_csvs[0])
    except Exception as e:
        result['details']['error'] = str(e)
        result['passed'] = False
        return result

    # Displacement derivative sign changes
    disp = compute_displacement(df).values
    disp_diff = np.diff(disp)
    # Filter out near-zero diffs (noise at FtPause)
    threshold = np.max(np.abs(disp_diff)) * 0.01 if len(disp_diff) > 0 else 0
    significant = disp_diff[np.abs(disp_diff) > threshold]
    if len(significant) > 1:
        signs = np.sign(significant)
        sign_changes_disp = int(np.sum(np.abs(np.diff(signs)) > 0))
    else:
        sign_changes_disp = 0

    disp_ok = sign_changes_disp <= max_sign_changes_disp
    result['details']['displacement_sign_changes'] = sign_changes_disp
    result['details']['displacement_max_allowed'] = max_sign_changes_disp
    result['details']['displacement_smooth'] = bool(disp_ok)

    # Velocity magnitude derivative sign changes
    vel = np.sqrt(df['vel_x']**2 + df['vel_y']**2 + df['vel_z']**2).values
    vel_diff = np.diff(vel)
    threshold_v = np.max(np.abs(vel_diff)) * 0.01 if len(vel_diff) > 0 else 0
    significant_v = vel_diff[np.abs(vel_diff) > threshold_v]
    if len(significant_v) > 1:
        signs_v = np.sign(significant_v)
        sign_changes_vel = int(np.sum(np.abs(np.diff(signs_v)) > 0))
    else:
        sign_changes_vel = 0

    vel_ok = sign_changes_vel <= max_sign_changes_vel
    result['details']['velocity_sign_changes'] = sign_changes_vel
    result['details']['velocity_max_allowed'] = max_sign_changes_vel
    result['details']['velocity_smooth'] = bool(vel_ok)

    result['passed'] = disp_ok and vel_ok

    if not disp_ok:
        logger.warning("SMOOTHNESS FAIL: %s displacement has %d sign changes (max %d)",
                        case_dir.name, sign_changes_disp, max_sign_changes_disp)
    if not vel_ok:
        logger.warning("SMOOTHNESS FAIL: %s velocity has %d sign changes (max %d)",
                        case_dir.name, sign_changes_vel, max_sign_changes_vel)

    logger.info("Smoothness check (%s): %s", case_dir.name, 'PASS' if result['passed'] else 'FAIL')
    return result


# ---------------------------------------------------------------------------
# Aggregate runner
# ---------------------------------------------------------------------------

def run_all_checks(results_df: pd.DataFrame,
                   processed_dir: Optional[Path] = None) -> Dict:
    """
    Ejecuta todos los sanity checks y retorna diccionario consolidado.

    Args:
        results_df: DataFrame con columnas de CaseResult (de SQLite o manual).
        processed_dir: Directorio con subdirectorios por caso (para smoothness check).

    Returns:
        Dict con resultados de cada check + resumen global.
    """
    report = {
        'checks': {},
        'summary': {'total': 0, 'passed': 0, 'failed': 0, 'all_passed': True},
    }

    # 1. Monotonicity
    mono = check_monotonicity(results_df)
    report['checks']['monotonicity'] = mono

    # 2. Ritter
    ritter = check_ritter(results_df)
    report['checks']['ritter_velocity'] = ritter

    # 3. Magnitudes
    magnitudes = check_magnitudes(results_df)
    report['checks']['magnitudes'] = magnitudes

    # 4. Forces
    forces = check_forces(results_df)
    report['checks']['forces'] = forces

    # 5. Smoothness (per case, requires CSVs)
    smoothness_results = []
    if processed_dir and processed_dir.exists():
        for _, row in results_df.iterrows():
            case_name = row['case_name']
            case_path = processed_dir / case_name
            if case_path.exists():
                sm = check_smoothness(case_path)
                smoothness_results.append(sm)
            else:
                logger.info("Smoothness: skipping %s (dir not found)", case_name)

    smoothness_all_pass = all(s['passed'] for s in smoothness_results) if smoothness_results else True
    report['checks']['smoothness'] = {
        'name': 'smoothness',
        'passed': smoothness_all_pass,
        'cases': smoothness_results,
    }

    # Summary
    for name, check in report['checks'].items():
        report['summary']['total'] += 1
        if check['passed']:
            report['summary']['passed'] += 1
        else:
            report['summary']['failed'] += 1
            report['summary']['all_passed'] = False

    logger.info("=== SANITY CHECK SUMMARY: %d/%d passed ===",
                report['summary']['passed'], report['summary']['total'])
    return report


# ---------------------------------------------------------------------------
# Report generation
# ---------------------------------------------------------------------------

def generate_report(check_results: Dict, output_dir: Path) -> Tuple[Path, Path]:
    """
    Genera reporte JSON + figura resumen.

    Returns:
        (json_path, figure_path)
    """
    output_dir.mkdir(parents=True, exist_ok=True)

    # --- JSON report ---
    json_path = output_dir / 'sanity_report.json'

    # Make JSON-serializable (convert numpy types)
    def _serialize(obj):
        if isinstance(obj, (np.integer,)):
            return int(obj)
        if isinstance(obj, (np.floating,)):
            return float(obj)
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        if isinstance(obj, (np.bool_,)):
            return bool(obj)
        raise TypeError(f"Not serializable: {type(obj)}")

    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(check_results, f, indent=2, default=_serialize, ensure_ascii=False)
    logger.info("JSON report saved: %s", json_path)

    # --- Figure ---
    fig_path = _plot_summary(check_results, output_dir)

    return json_path, fig_path


def _plot_summary(report: Dict, output_dir: Path) -> Path:
    """Genera figura resumen tipo semaforo con detalle por check."""
    checks = report['checks']
    names = list(checks.keys())
    passed = [checks[n]['passed'] for n in names]

    fig, axes = plt.subplots(1, 2, figsize=(14, 5), gridspec_kw={'width_ratios': [1, 2]})

    # --- Panel 1: Semaforo ---
    ax = axes[0]
    colors = ['#2ecc71' if p else '#e74c3c' for p in passed]
    labels_display = [n.replace('_', '\n') for n in names]
    y_pos = np.arange(len(names))

    bars = ax.barh(y_pos, [1] * len(names), color=colors, edgecolor='white', height=0.6)
    ax.set_yticks(y_pos)
    ax.set_yticklabels(labels_display, fontsize=10)
    ax.set_xlim(0, 1.2)
    ax.set_xticks([])
    for i, p in enumerate(passed):
        ax.text(0.5, i, 'PASS' if p else 'FAIL', ha='center', va='center',
                fontsize=12, fontweight='bold', color='white')

    total = report['summary']['total']
    n_pass = report['summary']['passed']
    ax.set_title(f'Sanity Checks: {n_pass}/{total} passed', fontsize=13, fontweight='bold')

    # --- Panel 2: Detalle por check ---
    ax2 = axes[1]
    ax2.axis('off')

    text_lines = []
    for name in names:
        check = checks[name]
        status = 'PASS' if check['passed'] else 'FAIL'
        line = f"[{status}] {name}"

        if name == 'monotonicity' and 'details' in check:
            for key, val in check['details'].items():
                if isinstance(val, dict) and 'skipped' not in val:
                    line += f"\n    {key}: rho={val.get('spearman_rho', '?'):.3f} " \
                            f"({'OK' if val.get('passed') else 'FAIL'})"

        elif name == 'ritter_velocity' and 'details' in check:
            for d in check['details']:
                if not d.get('skipped'):
                    line += f"\n    {d['case']}: SPH/Ritter={d.get('ratio_sph_ritter', 0):.2f}"

        elif name == 'forces' and 'details' in check:
            for d in check['details']:
                line += f"\n    {d['case']}: F_sph/W={d.get('ratio_fsph_weight', 0):.2f}"

        elif name == 'smoothness' and 'cases' in check:
            for c in check.get('cases', []):
                sc_d = c.get('details', {}).get('displacement_sign_changes', '?')
                line += f"\n    {c.get('case', '?')}: disp_sign_changes={sc_d}"

        text_lines.append(line)

    ax2.text(0.02, 0.95, '\n'.join(text_lines), transform=ax2.transAxes,
             fontsize=9, fontfamily='monospace', verticalalignment='top')
    ax2.set_title('Details', fontsize=13, fontweight='bold')

    plt.tight_layout()
    fig_path = output_dir / 'sanity_summary.png'
    fig.savefig(str(fig_path), dpi=150, bbox_inches='tight')
    plt.close(fig)
    logger.info("Summary figure saved: %s", fig_path)
    return fig_path


# ---------------------------------------------------------------------------
# Helpers: load data from SQLite or CSV
# ---------------------------------------------------------------------------

def load_results_from_sqlite(db_path: Path, table: str = 'results') -> pd.DataFrame:
    """Carga resultados desde SQLite."""
    import sqlite3
    conn = sqlite3.connect(str(db_path))
    df = pd.read_sql(f'SELECT * FROM {table}', conn)
    conn.close()
    logger.info("Loaded %d results from %s", len(df), db_path)
    return df


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

if __name__ == '__main__':
    import sys

    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s %(levelname)s: %(message)s',
        datefmt='%H:%M:%S',
    )

    project_root = Path(__file__).parent.parent
    db_path = project_root / 'data' / 'results.sqlite'
    processed_dir = project_root / 'data' / 'processed'
    output_dir = project_root / 'data' / 'figures' / 'sanity'

    if db_path.exists():
        df = load_results_from_sqlite(db_path)
    else:
        logger.error("No results.sqlite found at %s", db_path)
        sys.exit(1)

    if len(df) == 0:
        logger.error("No results in database")
        sys.exit(1)

    print(f"\nLoaded {len(df)} results from SQLite")
    print(f"Cases: {list(df['case_name'])}\n")

    report = run_all_checks(df, processed_dir=processed_dir)
    json_path, fig_path = generate_report(report, output_dir)

    print(f"\n{'='*60}")
    print(f"SANITY CHECK RESULTS")
    print(f"{'='*60}")
    for name, check in report['checks'].items():
        status = 'PASS' if check['passed'] else 'FAIL'
        print(f"  [{status}] {name}")
    print(f"{'='*60}")
    print(f"Overall: {report['summary']['passed']}/{report['summary']['total']} passed")
    print(f"\nReport: {json_path}")
    print(f"Figure: {fig_path}")
