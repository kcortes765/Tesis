"""
train_gp.py — Entrena GP surrogate con datos reales y genera figuras.

Wrapper de re-ejecucion rapida sobre src/gp_active_learning.py.
Lee datos de SQLite, entrena GP, genera figuras en data/figures/gp/,
propone siguiente punto para Active Learning.

Uso:
    python scripts/train_gp.py                # default: threshold=0.1004 (d_eq BLIR3)
    python scripts/train_gp.py --threshold 0.15
    python scripts/train_gp.py --output-dir data/figures/gp_custom

Autor: Kevin Cortes (UCN 2026)
"""

from __future__ import annotations

import argparse
import logging
import sys
from pathlib import Path

# Asegurar que src/ esta en el path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from src.gp_active_learning import (
    GPSurrogate,
    generate_figures,
    load_data_from_sqlite,
    load_param_ranges,
    propose_next_point,
    check_stopping,
    DEFAULT_THRESHOLD,
)

logger = logging.getLogger(__name__)


def main():
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s %(levelname)s: %(message)s',
        datefmt='%H:%M:%S',
    )

    parser = argparse.ArgumentParser(
        description='Entrena GP surrogate con datos reales de SQLite'
    )
    parser.add_argument('--threshold', type=float, default=DEFAULT_THRESHOLD,
                        help='Umbral de movimiento T [m] (default: %.4f)' % DEFAULT_THRESHOLD)
    parser.add_argument('--output-dir', type=str, default=None,
                        help='Directorio de figuras (default: data/figures/gp/)')
    parser.add_argument('--db', type=str, default=None,
                        help='Path a SQLite (default: data/results.sqlite)')
    args = parser.parse_args()

    db_path = Path(args.db) if args.db else None
    output_dir = Path(args.output_dir) if args.output_dir else None

    # 1. Cargar datos
    X, y, df = load_data_from_sqlite(db_path)
    bounds = load_param_ranges()

    print("\n--- Datos cargados ---")
    print(df[['case_name', 'dam_height', 'boulder_mass', 'max_displacement']].to_string(index=False))

    # 2. Entrenar GP
    gp = GPSurrogate(bounds=bounds)
    gp.fit(X, y)

    # 3. LOO-CV
    loo = gp.loo_cv()

    # 4. Stopping check + proponer siguiente punto
    converged, u_min = check_stopping(gp, args.threshold)
    x_next = None
    if not converged:
        x_next, _, _ = propose_next_point(gp, args.threshold, exclude_X=X)

    # 5. Generar figuras
    figs = generate_figures(gp, X, y, args.threshold, output_dir)

    # 6. Guardar modelo
    gp.save()

    # 7. Resumen
    print("\n" + "=" * 60)
    print("  GP SURROGATE — RESUMEN")
    print("=" * 60)
    print("  Datos:            %d puntos" % len(y))
    print("  Kernel:           %s" % gp.gp.kernel_)
    print("  LML:              %.3f" % gp.gp.log_marginal_likelihood_value_)
    print("  LOO Q2:           %.4f" % loo['q2'])
    print("  LOO RMSE:         %.4f m" % loo['rmse'])
    print("  Threshold:        %.4f m" % args.threshold)
    print("  U_min:            %.3f" % u_min)
    print("  Convergido:       %s" % converged)
    if x_next is not None:
        print("  Siguiente punto:  dam_h=%.4f, mass=%.4f" % (x_next[0], x_next[1]))
    print("  Figuras:          %d generadas" % len(figs))
    print("=" * 60)


if __name__ == '__main__':
    main()
