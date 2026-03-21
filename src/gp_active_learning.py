"""
gp_active_learning.py — GP Surrogate + Active Learning para umbral de movimiento incipiente

Entrena un GP (Matern 5/2 + ARD) en espacio 2D (dam_height, boulder_mass) y usa
U-function (Echard 2011) para Active Learning secuencial del contorno umbral.

Metodologia:
    - Kernel: ConstantKernel * Matern(nu=2.5, ARD) + WhiteKernel
    - Acquisition: U(x) = |mu(x) - T| / sigma(x)  [Echard 2011]
    - Parada: min(U) >= 2.0 (97.7% confianza) O budget agotado
    - LOO-CV: formula analitica O(n^3)

Referencias:
    - Echard et al. (2011) Structural Safety 33(2), 145-154
    - Bryan et al. (2005) NIPS - straddle heuristic
    - Loeppky et al. (2009) Technometrics 51(4), 366-376

Ejecutar:
    python src/gp_active_learning.py --test       # test con datos sinteticos
    python src/gp_active_learning.py --from-db    # entrenar con datos de SQLite

Autor: Kevin Cortes (UCN 2026)
"""

from __future__ import annotations

import argparse
import json
import logging
import pickle
import sqlite3
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from sklearn.gaussian_process import GaussianProcessRegressor
from sklearn.gaussian_process.kernels import ConstantKernel, Matern, WhiteKernel

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Constantes
# ---------------------------------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DB_PATH = PROJECT_ROOT / "data" / "results.sqlite"
FIGURES_DIR = PROJECT_ROOT / "data" / "figures" / "gp"
MODEL_PATH = PROJECT_ROOT / "data" / "gp_surrogate.pkl"
PARAM_RANGES_PATH = PROJECT_ROOT / "config" / "param_ranges.json"

# Defaults del estudio 2D
DEFAULT_THRESHOLD = 0.10   # d_eq del boulder BLIR3@scale=0.04 [m]
DEFAULT_U_STOP = 2.0       # Criterio parada Echard 2011
DEFAULT_MAX_BUDGET = 30    # Maximo total de simulaciones
DEFAULT_GRID_SIZE = 50     # Grilla candidata 50x50
SEED = 42

FEATURES = ['dam_height', 'boulder_mass']
TARGET = 'max_displacement'

FEATURE_LABELS = {
    'dam_height': 'Altura columna $h$ [m]',
    'boulder_mass': 'Masa boulder [kg]',
}

PLT_STYLE = {
    'font.family': 'serif',
    'font.size': 10,
    'axes.labelsize': 11,
    'axes.titlesize': 12,
    'figure.dpi': 150,
    'savefig.dpi': 300,
    'savefig.bbox': 'tight',
    'axes.grid': True,
    'grid.alpha': 0.2,
    'axes.spines.top': False,
    'axes.spines.right': False,
}


# ---------------------------------------------------------------------------
# Utilidades
# ---------------------------------------------------------------------------

def load_param_ranges(path=None):
    # type: (Optional[Path]) -> np.ndarray
    """Carga rangos de param_ranges.json. Retorna array (2, 2): [[h_min, h_max], [m_min, m_max]]."""
    path = path or PARAM_RANGES_PATH
    defaults = np.array([[0.10, 0.50], [0.80, 1.60]])
    if not path.exists():
        logger.warning("param_ranges.json no encontrado, usando defaults")
        return defaults
    with open(path) as f:
        cfg = json.load(f)
    params = cfg.get('parameters', {})
    bounds = []
    for feat in FEATURES:
        if feat in params:
            bounds.append([params[feat]['min'], params[feat]['max']])
        else:
            idx = FEATURES.index(feat)
            bounds.append(list(defaults[idx]))
    return np.array(bounds)


def load_data_from_sqlite(db_path=None):
    # type: (Optional[Path]) -> Tuple[np.ndarray, np.ndarray, pd.DataFrame]
    """Lee datos de SQLite. Retorna (X, y, df)."""
    db_path = db_path or DB_PATH
    if not db_path.exists():
        raise FileNotFoundError("SQLite no encontrada: %s" % db_path)

    conn = sqlite3.connect(str(db_path))
    df = pd.read_sql("""
        SELECT case_name, dam_height, boulder_mass, max_displacement
        FROM results
        WHERE dam_height > 0 AND boulder_mass > 0
              AND max_displacement IS NOT NULL
    """, conn)
    conn.close()

    if len(df) == 0:
        raise ValueError("No hay datos validos en SQLite")

    X = df[FEATURES].values
    y = df[TARGET].values
    logger.info("Cargados %d puntos de %s", len(df), db_path.name)
    return X, y, df


def load_data_from_csv(csv_path):
    # type: (Path) -> Tuple[np.ndarray, np.ndarray, pd.DataFrame]
    """Lee datos de CSV con columnas dam_height, boulder_mass, max_displacement."""
    df = pd.read_csv(csv_path)
    for col in FEATURES + [TARGET]:
        if col not in df.columns:
            raise ValueError("Columna faltante en CSV: %s" % col)
    X = df[FEATURES].values
    y = df[TARGET].values
    logger.info("Cargados %d puntos de %s", len(df), csv_path.name)
    return X, y, df


def make_candidate_grid(bounds, grid_size=DEFAULT_GRID_SIZE):
    # type: (np.ndarray, int) -> np.ndarray
    """Crea grilla regular 2D de candidatos. bounds: (2, 2)."""
    x1 = np.linspace(bounds[0, 0], bounds[0, 1], grid_size)
    x2 = np.linspace(bounds[1, 0], bounds[1, 1], grid_size)
    X1, X2 = np.meshgrid(x1, x2)
    return np.column_stack([X1.ravel(), X2.ravel()])


def _normalize(X, bounds):
    # type: (np.ndarray, np.ndarray) -> np.ndarray
    """Normaliza X a [0, 1] usando bounds."""
    return (X - bounds[:, 0]) / (bounds[:, 1] - bounds[:, 0])


def _denormalize(X_norm, bounds):
    # type: (np.ndarray, np.ndarray) -> np.ndarray
    """Desnormaliza de [0, 1] a espacio original."""
    return X_norm * (bounds[:, 1] - bounds[:, 0]) + bounds[:, 0]


# ---------------------------------------------------------------------------
# GPSurrogate
# ---------------------------------------------------------------------------

class GPSurrogate:
    """Gaussian Process surrogate con Matern 5/2 + ARD para estudio 2D.

    Normaliza inputs a [0, 1] internamente. Usa normalize_y=True de sklearn
    para outputs.
    """

    def __init__(self, bounds=None, noise_level=1e-5, n_restarts=20, seed=SEED):
        # type: (Optional[np.ndarray], float, int, int) -> None
        self.bounds = bounds if bounds is not None else load_param_ranges()
        self.seed = seed

        self.kernel = (
            ConstantKernel(1.0, constant_value_bounds=(1e-3, 1e3))
            * Matern(
                length_scale=[1.0, 1.0],
                length_scale_bounds=(1e-2, 1e2),
                nu=2.5,
            )
            + WhiteKernel(
                noise_level=noise_level,
                noise_level_bounds=(1e-10, 1e-1),
            )
        )

        self.gp = GaussianProcessRegressor(
            kernel=self.kernel,
            n_restarts_optimizer=n_restarts,
            normalize_y=True,
            alpha=1e-6,
            random_state=seed,
        )

        self.X_train = None   # type: Optional[np.ndarray]
        self.y_train = None   # type: Optional[np.ndarray]
        self.X_train_norm = None  # type: Optional[np.ndarray]
        self._fitted = False

    def fit(self, X, y):
        # type: (np.ndarray, np.ndarray) -> GPSurrogate
        """Entrena el GP. X: (n, 2), y: (n,)."""
        self.X_train = np.asarray(X, dtype=np.float64)
        self.y_train = np.asarray(y, dtype=np.float64)
        self.X_train_norm = _normalize(self.X_train, self.bounds)

        self.gp.fit(self.X_train_norm, self.y_train)
        self._fitted = True

        logger.info("GP entrenado con %d puntos. Kernel: %s", len(y), self.gp.kernel_)
        logger.info("  LML: %.3f", self.gp.log_marginal_likelihood_value_)
        return self

    def predict(self, X):
        # type: (np.ndarray) -> np.ndarray
        """Prediccion media. X en espacio original."""
        X_norm = _normalize(np.asarray(X, dtype=np.float64), self.bounds)
        return self.gp.predict(X_norm)

    def predict_with_std(self, X):
        # type: (np.ndarray) -> Tuple[np.ndarray, np.ndarray]
        """Prediccion media + desviacion estandar. X en espacio original."""
        X_norm = _normalize(np.asarray(X, dtype=np.float64), self.bounds)
        mu, std = self.gp.predict(X_norm, return_std=True)
        return mu, std

    def loo_cv(self):
        # type: () -> Dict[str, object]
        """Leave-One-Out via formula analitica para GP exacto.

        Returns:
            dict con keys: y_pred, y_std, rmse, q2, residuals_std
        """
        if not self._fitted:
            raise RuntimeError("GP no entrenado. Llamar fit() primero.")

        X_n = self.X_train_norm
        y = self.y_train
        n = len(y)

        # Matriz de covarianza con kernel optimizado
        K = self.gp.kernel_(X_n)
        K += self.gp.alpha * np.eye(n)

        # Inversion (n<=30, es instantaneo)
        K_inv = np.linalg.inv(K)
        alpha_vec = K_inv.dot(y - self.gp._y_train_mean)

        # Formula LOO analitica: Rasmussen & Williams eq. 5.12
        K_inv_diag = np.diag(K_inv)
        loo_mean = y - alpha_vec / K_inv_diag
        loo_var = 1.0 / K_inv_diag

        residuals = y - loo_mean
        rmse = np.sqrt(np.mean(residuals ** 2))
        ss_res = np.sum(residuals ** 2)
        ss_tot = np.sum((y - y.mean()) ** 2)
        q2 = 1.0 - ss_res / ss_tot if ss_tot > 0 else 0.0

        # Residuos estandarizados
        loo_std = np.sqrt(np.maximum(loo_var, 1e-10))
        residuals_std = residuals / loo_std

        logger.info("LOO-CV: Q2=%.4f, RMSE=%.4f m", q2, rmse)
        return {
            'y_pred': loo_mean,
            'y_std': loo_std,
            'rmse': rmse,
            'q2': q2,
            'residuals_std': residuals_std,
        }

    def save(self, path=None):
        # type: (Optional[Path]) -> None
        """Exporta modelo a pickle."""
        path = path or MODEL_PATH
        path.parent.mkdir(parents=True, exist_ok=True)
        package = {
            'gp': self.gp,
            'bounds': self.bounds,
            'X_train': self.X_train,
            'y_train': self.y_train,
            'features': FEATURES,
            'target': TARGET,
            'kernel_str': str(self.gp.kernel_),
            'lml': self.gp.log_marginal_likelihood_value_,
        }
        with open(path, 'wb') as f:
            pickle.dump(package, f)
        logger.info("Modelo guardado: %s", path)

    @classmethod
    def load(cls, path=None):
        # type: (Optional[Path]) -> GPSurrogate
        """Carga modelo desde pickle."""
        path = path or MODEL_PATH
        with open(path, 'rb') as f:
            pkg = pickle.load(f)
        obj = cls(bounds=pkg['bounds'])
        obj.gp = pkg['gp']
        obj.X_train = pkg['X_train']
        obj.y_train = pkg['y_train']
        obj.X_train_norm = _normalize(obj.X_train, obj.bounds)
        obj._fitted = True
        logger.info("Modelo cargado: %s", path)
        return obj


# ---------------------------------------------------------------------------
# Acquisition functions
# ---------------------------------------------------------------------------

def u_function(mu, sigma, threshold):
    # type: (np.ndarray, np.ndarray, float) -> np.ndarray
    """U-function de Echard et al. (2011).

    U(x) = |mu(x) - T| / sigma(x)

    U >= 2 => 97.7% confianza en clasificacion respecto al umbral.
    """
    return np.abs(mu - threshold) / np.maximum(sigma, 1e-10)


def straddle(mu, sigma, threshold, alpha=1.96):
    # type: (np.ndarray, np.ndarray, float, float) -> np.ndarray
    """Straddle heuristic de Bryan et al. (2005).

    a(x) = alpha * sigma(x) - |mu(x) - T|

    Valores altos => punto en la frontera con alta incertidumbre.
    """
    return alpha * sigma - np.abs(mu - threshold)


# ---------------------------------------------------------------------------
# Active Learning functions
# ---------------------------------------------------------------------------

def propose_next_point(gp_model, threshold=DEFAULT_THRESHOLD,
                       grid_size=DEFAULT_GRID_SIZE, exclude_X=None,
                       min_dist=0.01):
    # type: (GPSurrogate, float, int, Optional[np.ndarray], float) -> Tuple[np.ndarray, float, np.ndarray]
    """Propone siguiente punto via argmin U(x) sobre grilla candidata.

    Args:
        gp_model: GPSurrogate entrenado
        threshold: umbral de movimiento T [m]
        grid_size: tamano de la grilla por dimension
        exclude_X: puntos ya simulados (espacio original) para excluir
        min_dist: distancia minima normalizada para excluir vecinos

    Returns:
        (x_next, u_min, U_grid): siguiente punto (espacio original),
        U minimo global, U evaluada en toda la grilla
    """
    X_cand = make_candidate_grid(gp_model.bounds, grid_size)
    mu, sigma = gp_model.predict_with_std(X_cand)
    U = u_function(mu, sigma, threshold)

    # Excluir puntos demasiado cercanos a los ya simulados
    if exclude_X is not None and len(exclude_X) > 0:
        X_cand_norm = _normalize(X_cand, gp_model.bounds)
        X_excl_norm = _normalize(exclude_X, gp_model.bounds)
        for xe in X_excl_norm:
            dists = np.linalg.norm(X_cand_norm - xe, axis=1)
            U[dists < min_dist] = np.inf

    u_min = np.min(U)
    next_idx = np.argmin(U)
    x_next = X_cand[next_idx]

    logger.info("Propuesto: dam_h=%.4f, mass=%.4f (U_min=%.3f)",
                x_next[0], x_next[1], u_min)
    return x_next, u_min, U


def check_stopping(gp_model, threshold=DEFAULT_THRESHOLD,
                    grid_size=DEFAULT_GRID_SIZE):
    # type: (GPSurrogate, float, int) -> Tuple[bool, float]
    """Verifica criterio de parada: min(U) >= 2.0 en toda la grilla.

    Returns:
        (converged, u_min)
    """
    X_cand = make_candidate_grid(gp_model.bounds, grid_size)
    mu, sigma = gp_model.predict_with_std(X_cand)
    U = u_function(mu, sigma, threshold)
    u_min = float(np.min(U))
    converged = u_min >= DEFAULT_U_STOP
    logger.info("Stopping check: U_min=%.3f, converged=%s", u_min, converged)
    return converged, u_min


def al_loop(initial_X, initial_y, param_bounds, threshold=DEFAULT_THRESHOLD,
            max_budget=DEFAULT_MAX_BUDGET, grid_size=DEFAULT_GRID_SIZE,
            simulator=None):
    # type: (np.ndarray, np.ndarray, np.ndarray, float, int, int, object) -> Dict
    """Loop completo de Active Learning.

    Si `simulator` es None, el loop para despues de proponer el siguiente punto
    y retorna la propuesta (modo offline — el usuario corre la sim manualmente).

    Si `simulator` es un callable f(x) -> y, lo usa para evaluar puntos
    automaticamente (modo test con funcion sintetica).

    Args:
        initial_X: datos iniciales (n, 2)
        initial_y: respuestas iniciales (n,)
        param_bounds: rangos (2, 2)
        threshold: umbral T [m]
        max_budget: maximo de evaluaciones totales
        grid_size: tamano grilla candidata
        simulator: callable(x) -> float, o None para modo offline

    Returns:
        dict con keys: gp, X_train, y_train, history, converged, reason
    """
    X = np.array(initial_X, dtype=np.float64)
    y = np.array(initial_y, dtype=np.float64)

    gp_model = GPSurrogate(bounds=param_bounds)
    history = []  # type: List[Dict]

    for iteration in range(max_budget - len(X)):
        # Entrenar GP
        gp_model.fit(X, y)
        loo = gp_model.loo_cv()

        # Proponer siguiente punto
        x_next, u_min, U_grid = propose_next_point(
            gp_model, threshold, grid_size, exclude_X=X
        )

        history.append({
            'iteration': iteration,
            'n_train': len(X),
            'u_min': u_min,
            'loo_q2': loo['q2'],
            'loo_rmse': loo['rmse'],
            'x_proposed': x_next.tolist(),
        })

        # Criterio de parada
        if u_min >= DEFAULT_U_STOP:
            logger.info("CONVERGENCIA en iteracion %d: U_min=%.3f >= %.1f",
                        iteration, u_min, DEFAULT_U_STOP)
            return {
                'gp': gp_model, 'X_train': X, 'y_train': y,
                'history': history, 'converged': True,
                'reason': 'U_min >= %.1f' % DEFAULT_U_STOP,
            }

        # Evaluar punto (si hay simulador)
        if simulator is None:
            logger.info("Modo offline: propuesto x_next=%s. "
                        "Simular manualmente y re-ejecutar.", x_next)
            return {
                'gp': gp_model, 'X_train': X, 'y_train': y,
                'history': history, 'converged': False,
                'reason': 'offline',
                'x_next': x_next,
            }

        y_new = float(simulator(x_next))
        logger.info("  Evaluado: y=%.4f", y_new)
        X = np.vstack([X, x_next])
        y = np.append(y, y_new)

    # Budget agotado
    gp_model.fit(X, y)
    logger.info("BUDGET AGOTADO: %d simulaciones", len(X))
    return {
        'gp': gp_model, 'X_train': X, 'y_train': y,
        'history': history, 'converged': False,
        'reason': 'budget_exhausted',
    }


# ---------------------------------------------------------------------------
# Generacion de figuras
# ---------------------------------------------------------------------------

def generate_figures(gp_model, X_train, y_train, threshold=DEFAULT_THRESHOLD,
                     output_dir=None, history=None):
    # type: (GPSurrogate, np.ndarray, np.ndarray, float, Optional[Path], Optional[List[Dict]]) -> List[Path]
    """Genera todas las figuras del estudio GP + AL.

    Figuras:
        1. GP surface (media) con datos de entrenamiento
        2. GP incertidumbre (std)
        3. Contorno umbral con banda de confianza
        4. LOO predicted vs actual
        5. U-function heatmap
        6. Probabilidad de movimiento P(f > T)
        7. Evolucion de U_min (si hay history)

    Returns:
        Lista de paths de figuras creadas.
    """
    output_dir = output_dir or FIGURES_DIR
    output_dir.mkdir(parents=True, exist_ok=True)
    plt.rcParams.update(PLT_STYLE)

    bounds = gp_model.bounds
    created = []  # type: List[Path]

    # Grilla de prediccion
    grid_size = 100
    x1 = np.linspace(bounds[0, 0], bounds[0, 1], grid_size)
    x2 = np.linspace(bounds[1, 0], bounds[1, 1], grid_size)
    X1, X2 = np.meshgrid(x1, x2)
    X_grid = np.column_stack([X1.ravel(), X2.ravel()])

    mu, sigma = gp_model.predict_with_std(X_grid)
    Mu = mu.reshape(grid_size, grid_size)
    Sigma = sigma.reshape(grid_size, grid_size)

    # --- Fig 1: GP Surface (media) ---
    fig, ax = plt.subplots(figsize=(7, 5.5))
    cf = ax.contourf(X1, X2, Mu, levels=25, cmap='RdYlGn_r')
    plt.colorbar(cf, ax=ax, label='Desplazamiento [m]')
    ax.contour(X1, X2, Mu, levels=[threshold], colors='black',
               linewidths=2, linestyles='--')
    ax.scatter(X_train[:, 0], X_train[:, 1], c='black', s=40,
               edgecolors='white', linewidths=0.7, zorder=5,
               label='Datos entrenamiento')
    ax.set_xlabel(FEATURE_LABELS['dam_height'])
    ax.set_ylabel(FEATURE_LABELS['boulder_mass'])
    ax.set_title('GP Surrogate — Prediccion media')
    ax.legend(fontsize=8)
    fig.tight_layout()
    p = output_dir / 'gp_surface_mean.png'
    fig.savefig(p)
    fig.savefig(output_dir / 'gp_surface_mean.pdf')
    plt.close(fig)
    created.append(p)
    logger.info("  Fig: gp_surface_mean")

    # --- Fig 2: GP Incertidumbre (std) ---
    fig, ax = plt.subplots(figsize=(7, 5.5))
    cf = ax.contourf(X1, X2, Sigma, levels=25, cmap='YlOrRd')
    plt.colorbar(cf, ax=ax, label='$\\sigma$ [m]')
    ax.scatter(X_train[:, 0], X_train[:, 1], c='black', s=40,
               edgecolors='white', linewidths=0.7, zorder=5,
               label='Datos entrenamiento')
    ax.set_xlabel(FEATURE_LABELS['dam_height'])
    ax.set_ylabel(FEATURE_LABELS['boulder_mass'])
    ax.set_title('GP Surrogate — Incertidumbre predictiva')
    ax.legend(fontsize=8)
    fig.tight_layout()
    p = output_dir / 'gp_surface_std.png'
    fig.savefig(p)
    fig.savefig(output_dir / 'gp_surface_std.pdf')
    plt.close(fig)
    created.append(p)
    logger.info("  Fig: gp_surface_std")

    # --- Fig 3: Contorno umbral con banda de confianza ---
    fig, ax = plt.subplots(figsize=(7, 5.5))
    # Probabilidad P(f > T)
    from scipy.stats import norm as norm_dist
    Z_prob = norm_dist.cdf((Mu - threshold) / np.maximum(Sigma, 1e-10))
    cf = ax.contourf(X1, X2, Z_prob, levels=np.linspace(0, 1, 21),
                     cmap='RdBu')
    plt.colorbar(cf, ax=ax, label='$P(f > T)$')
    # Contorno medio
    ax.contour(X1, X2, Mu, levels=[threshold], colors='black',
               linewidths=2, linestyles='-')
    # Banda +-2sigma
    ax.contour(X1, X2, Mu - 2 * Sigma, levels=[threshold],
               colors='gray', linewidths=1, linestyles='--')
    ax.contour(X1, X2, Mu + 2 * Sigma, levels=[threshold],
               colors='gray', linewidths=1, linestyles='--')
    ax.scatter(X_train[:, 0], X_train[:, 1], c='black', s=40,
               edgecolors='white', linewidths=0.7, zorder=5)
    ax.set_xlabel(FEATURE_LABELS['dam_height'])
    ax.set_ylabel(FEATURE_LABELS['boulder_mass'])
    ax.set_title('Contorno umbral $T = %.2f$ m con banda 95%%' % threshold)
    fig.tight_layout()
    p = output_dir / 'gp_contour_threshold.png'
    fig.savefig(p)
    fig.savefig(output_dir / 'gp_contour_threshold.pdf')
    plt.close(fig)
    created.append(p)
    logger.info("  Fig: gp_contour_threshold")

    # --- Fig 4: LOO predicted vs actual ---
    loo = gp_model.loo_cv()
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 4.5))

    y_pred_loo = loo['y_pred']
    y_std_loo = loo['y_std']

    ax1.errorbar(y_train, y_pred_loo, yerr=2 * y_std_loo,
                 fmt='o', markersize=6, color='#2166AC',
                 ecolor='#BBDEFB', elinewidth=1, capsize=3, alpha=0.8)
    lims = [
        min(y_train.min(), y_pred_loo.min()) - 0.3,
        max(y_train.max(), y_pred_loo.max()) + 0.3,
    ]
    ax1.plot(lims, lims, 'k--', lw=1, alpha=0.5, label='Perfecto')
    ax1.set_xlabel('Desplazamiento real [m]')
    ax1.set_ylabel('Desplazamiento predicho (LOO) [m]')
    ax1.set_title('(a) LOO: $Q^2$ = %.3f, RMSE = %.3f m' % (loo['q2'], loo['rmse']))
    ax1.legend(fontsize=8)
    ax1.set_xlim(lims)
    ax1.set_ylim(lims)
    ax1.set_aspect('equal')

    # Residuos estandarizados
    res_std = loo['residuals_std']
    colors = ['#EF5350' if r > 0 else '#42A5F5' for r in res_std]
    ax2.bar(range(len(y_train)), res_std, color=colors, alpha=0.7, edgecolor='none')
    ax2.axhline(0, color='black', lw=0.8)
    ax2.axhline(2, color='red', lw=0.8, ls='--', alpha=0.5)
    ax2.axhline(-2, color='red', lw=0.8, ls='--', alpha=0.5)
    ax2.set_xlabel('Indice de simulacion')
    ax2.set_ylabel('Residuo estandarizado')
    ax2.set_title('(b) Residuos LOO estandarizados')

    fig.suptitle('Validacion Leave-One-Out', fontsize=13, fontweight='bold', y=1.02)
    fig.tight_layout()
    p = output_dir / 'gp_loo_validation.png'
    fig.savefig(p)
    fig.savefig(output_dir / 'gp_loo_validation.pdf')
    plt.close(fig)
    created.append(p)
    logger.info("  Fig: gp_loo_validation")

    # --- Fig 5: U-function heatmap ---
    U_grid = u_function(mu, sigma, threshold)
    U_map = U_grid.reshape(grid_size, grid_size)

    fig, ax = plt.subplots(figsize=(7, 5.5))
    # Clip para visualizacion
    U_vis = np.clip(U_map, 0, 10)
    cf = ax.contourf(X1, X2, U_vis, levels=25, cmap='viridis_r')
    plt.colorbar(cf, ax=ax, label='$U(x)$')
    cs_u2 = ax.contour(X1, X2, U_map, levels=[DEFAULT_U_STOP], colors='red',
                       linewidths=2, linestyles='--')
    if cs_u2.collections:
        cs_u2.collections[0].set_label('$U = 2$')
    ax.scatter(X_train[:, 0], X_train[:, 1], c='white', s=40,
               edgecolors='black', linewidths=0.7, zorder=5)
    # Marcar minimo
    idx_min = np.argmin(U_grid)
    x_min = X_grid[idx_min]
    ax.scatter([x_min[0]], [x_min[1]], c='red', s=100, marker='*',
               zorder=6, label='argmin $U$ (%.2f)' % U_grid[idx_min])
    ax.set_xlabel(FEATURE_LABELS['dam_height'])
    ax.set_ylabel(FEATURE_LABELS['boulder_mass'])
    ax.set_title('U-function (Echard 2011) — $U_{min}$ = %.2f' % np.min(U_grid))
    ax.legend(fontsize=8)
    fig.tight_layout()
    p = output_dir / 'gp_u_function.png'
    fig.savefig(p)
    fig.savefig(output_dir / 'gp_u_function.pdf')
    plt.close(fig)
    created.append(p)
    logger.info("  Fig: gp_u_function")

    # --- Fig 6: Probabilidad de movimiento ---
    fig, ax = plt.subplots(figsize=(7, 5.5))
    cf = ax.contourf(X1, X2, Z_prob, levels=np.linspace(0, 1, 21),
                     cmap='RdYlGn_r')
    plt.colorbar(cf, ax=ax, label='$P(f > %.2f)$' % threshold)
    ax.contour(X1, X2, Z_prob, levels=[0.5], colors='black',
               linewidths=2, linestyles='-')
    ax.scatter(X_train[:, 0], X_train[:, 1], c='black', s=40,
               edgecolors='white', linewidths=0.7, zorder=5)
    ax.set_xlabel(FEATURE_LABELS['dam_height'])
    ax.set_ylabel(FEATURE_LABELS['boulder_mass'])
    ax.set_title('Probabilidad de movimiento ($T = %.2f$ m)' % threshold)
    fig.tight_layout()
    p = output_dir / 'gp_probability_movement.png'
    fig.savefig(p)
    fig.savefig(output_dir / 'gp_probability_movement.pdf')
    plt.close(fig)
    created.append(p)
    logger.info("  Fig: gp_probability_movement")

    # --- Fig 7: Evolucion de U_min (si hay history) ---
    if history and len(history) > 1:
        fig, ax = plt.subplots(figsize=(7, 4))
        iters = [h['iteration'] for h in history]
        u_mins = [h['u_min'] for h in history]
        ax.plot(iters, u_mins, 'o-', color='#2166AC', lw=2, markersize=6)
        ax.axhline(DEFAULT_U_STOP, color='red', ls='--', lw=1.5,
                   label='Criterio parada ($U = %.0f$)' % DEFAULT_U_STOP)
        ax.set_xlabel('Iteracion AL')
        ax.set_ylabel('$U_{min}$')
        ax.set_title('Convergencia del Active Learning')
        ax.legend(fontsize=9)
        fig.tight_layout()
        p = output_dir / 'gp_al_convergence.png'
        fig.savefig(p)
        fig.savefig(output_dir / 'gp_al_convergence.pdf')
        plt.close(fig)
        created.append(p)
        logger.info("  Fig: gp_al_convergence")

    logger.info("Generadas %d figuras en %s", len(created), output_dir)
    return created


# ---------------------------------------------------------------------------
# Test con datos sinteticos
# ---------------------------------------------------------------------------

def _synthetic_response(X):
    # type: (np.ndarray) -> np.ndarray
    """Funcion sintetica que emula fisica de boulder transport.

    displacement ~ energy / resistance
    energy ~ rho * g * h^2 / 2
    resistance ~ mass * g * mu
    """
    X = np.atleast_2d(X)
    dam_h = X[:, 0]
    mass = X[:, 1]
    energy = 1000.0 * 9.81 * dam_h ** 2 * 0.5
    resistance = mass * 9.81 * 0.6
    displacement = 2.0 * (energy / resistance) ** 0.7
    return np.maximum(displacement, 0.0)


def run_synthetic_test(output_dir=None):
    # type: (Optional[Path]) -> Dict
    """Test completo con funcion sintetica: batch inicial + AL loop + figuras."""
    output_dir = output_dir or (FIGURES_DIR / "test_synthetic")
    output_dir.mkdir(parents=True, exist_ok=True)

    bounds = load_param_ranges()
    rng = np.random.RandomState(SEED)

    # Batch inicial: 10 puntos LHS-like
    n_initial = 10
    X_init = np.column_stack([
        rng.uniform(bounds[0, 0], bounds[0, 1], n_initial),
        rng.uniform(bounds[1, 0], bounds[1, 1], n_initial),
    ])
    y_init = _synthetic_response(X_init)

    logger.info("=== TEST SINTETICO ===")
    logger.info("Batch inicial: %d puntos", n_initial)
    logger.info("Threshold: %.2f m", DEFAULT_THRESHOLD)

    # AL loop con simulador sintetico
    result = al_loop(
        X_init, y_init, bounds,
        threshold=DEFAULT_THRESHOLD,
        max_budget=20,
        simulator=lambda x: _synthetic_response(x.reshape(1, -1))[0],
    )

    logger.info("Resultado: converged=%s, reason=%s, n_total=%d",
                result['converged'], result['reason'], len(result['y_train']))

    # Figuras
    figs = generate_figures(
        result['gp'], result['X_train'], result['y_train'],
        threshold=DEFAULT_THRESHOLD,
        output_dir=output_dir,
        history=result['history'],
    )

    # Resumen
    loo = result['gp'].loo_cv()
    summary = {
        'converged': result['converged'],
        'reason': result['reason'],
        'n_total': len(result['y_train']),
        'n_iterations': len(result['history']),
        'final_u_min': result['history'][-1]['u_min'] if result['history'] else None,
        'loo_q2': loo['q2'],
        'loo_rmse': loo['rmse'],
        'figures': [str(f) for f in figs],
    }

    print("\n" + "=" * 60)
    print("  TEST SINTETICO — RESUMEN")
    print("=" * 60)
    print("  Convergencia:     %s (%s)" % (result['converged'], result['reason']))
    print("  Total sims:       %d" % len(result['y_train']))
    print("  Iteraciones AL:   %d" % len(result['history']))
    if result['history']:
        print("  U_min final:      %.3f" % result['history'][-1]['u_min'])
    print("  LOO Q2:           %.4f" % loo['q2'])
    print("  LOO RMSE:         %.4f m" % loo['rmse'])
    print("  Figuras:          %s" % output_dir)
    print("=" * 60)

    return summary


def run_from_db(db_path=None, output_dir=None, threshold=DEFAULT_THRESHOLD):
    # type: (Optional[Path], Optional[Path], float) -> Dict
    """Entrena GP con datos de SQLite, genera figuras, propone siguiente punto."""
    output_dir = output_dir or FIGURES_DIR
    X, y, df = load_data_from_sqlite(db_path)
    bounds = load_param_ranges()

    gp_model = GPSurrogate(bounds=bounds)
    gp_model.fit(X, y)
    loo = gp_model.loo_cv()

    converged, u_min = check_stopping(gp_model, threshold)
    x_next = None
    if not converged:
        x_next, _, _ = propose_next_point(gp_model, threshold, exclude_X=X)

    figs = generate_figures(gp_model, X, y, threshold, output_dir)
    gp_model.save()

    print("\n" + "=" * 60)
    print("  GP SURROGATE — RESULTADOS")
    print("=" * 60)
    print("  Datos:            %d puntos" % len(y))
    print("  Kernel:           %s" % gp_model.gp.kernel_)
    print("  LML:              %.3f" % gp_model.gp.log_marginal_likelihood_value_)
    print("  LOO Q2:           %.4f" % loo['q2'])
    print("  LOO RMSE:         %.4f m" % loo['rmse'])
    print("  U_min:            %.3f" % u_min)
    print("  Convergido:       %s" % converged)
    if x_next is not None:
        print("  Siguiente punto:  dam_h=%.4f, mass=%.4f" % (x_next[0], x_next[1]))
    print("  Figuras:          %s" % output_dir)
    print("  Modelo:           %s" % MODEL_PATH)
    print("=" * 60)

    return {
        'n_data': len(y),
        'loo_q2': loo['q2'],
        'loo_rmse': loo['rmse'],
        'u_min': u_min,
        'converged': converged,
        'x_next': x_next.tolist() if x_next is not None else None,
    }


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

if __name__ == '__main__':
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s %(levelname)s: %(message)s',
        datefmt='%H:%M:%S',
    )

    parser = argparse.ArgumentParser(
        description='GP Surrogate + Active Learning para umbral de movimiento'
    )
    parser.add_argument('--test', action='store_true',
                        help='Test con datos sinteticos')
    parser.add_argument('--from-db', action='store_true',
                        help='Entrenar con datos de SQLite')
    parser.add_argument('--from-csv', type=str, default=None,
                        help='Entrenar con datos de CSV')
    parser.add_argument('--threshold', type=float, default=DEFAULT_THRESHOLD,
                        help='Umbral de movimiento T [m] (default: %.2f)' % DEFAULT_THRESHOLD)
    parser.add_argument('--output-dir', type=str, default=None,
                        help='Directorio de figuras')
    args = parser.parse_args()

    out = Path(args.output_dir) if args.output_dir else None

    if args.test:
        run_synthetic_test(output_dir=out)
    elif args.from_db:
        run_from_db(threshold=args.threshold, output_dir=out)
    elif args.from_csv:
        X, y, df = load_data_from_csv(Path(args.from_csv))
        bounds = load_param_ranges()
        gp_model = GPSurrogate(bounds=bounds)
        gp_model.fit(X, y)
        loo = gp_model.loo_cv()
        generate_figures(gp_model, X, y, args.threshold, out)
        gp_model.save()
        print("Q2=%.4f, RMSE=%.4f" % (loo['q2'], loo['rmse']))
    else:
        parser.print_help()
