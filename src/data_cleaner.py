from __future__ import annotations

"""
data_cleaner.py — Modulo 3 del Pipeline SPH-IncipientMotion

ETL (Extract, Transform, Load) para CSVs generados por DualSPHysics + Chrono.

Fuentes de datos:
  - ChronoExchange_mkbound_51.csv — cinematica del boulder (pos, vel, omega, accel)
  - ChronoBody_forces.csv — fuerzas SPH + contacto por cuerpo
  - GaugesVel_V**.csv — velocidad del flujo en puntos fijos
  - GaugesMaxZ_hmax**.csv — altura maxima del agua en puntos fijos
  - Run.csv / RunPARTs.csv — metadata de la simulacion

Formato CSV (DualSPHysics):
  - Separador: punto y coma (;)
  - Decimal: punto (.)
  - Sentinel: -3.40282e+38 (float min) en Gauges = sin dato -> NaN

Criterio de falla (incipient motion):
  - Desplazamiento del centro de masa > umbral (% de d_eq)
  - Rotacion acumulada > umbral (grados)
  - El modo de clasificacion puede ser combinado o privilegiar solo displacement
  - Se puede usar una referencia temporal posterior al release para evitar
    contaminar displacement con un transitorio inicial de soltado

Autor: Kevin Cortes (UCN 2026)
"""

import logging
from pathlib import Path
from dataclasses import dataclass
from typing import Optional

import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)

# Sentinel value de DualSPHysics (float min) — indica "sin dato"
SENTINEL = -3.40282e+38
SENTINEL_THRESHOLD = -3.0e+38  # Cualquier valor menor a esto es sentinel


# ---------------------------------------------------------------------------
# Dataclass de resultado
# ---------------------------------------------------------------------------

@dataclass
class CaseResult:
    """Resultado procesado de un caso de simulacion."""
    case_name: str

    # Cinematica del boulder
    max_displacement: float      # Desplazamiento maximo del CM (m)
    max_displacement_rel: float  # Desplazamiento relativo (% de d_eq)
    max_rotation: float          # Rotacion acumulada maxima (grados)
    max_velocity: float          # Velocidad maxima del boulder (m/s)

    # Fuerzas sobre el boulder
    max_sph_force: float         # Fuerza SPH maxima (N)
    max_contact_force: float     # Fuerza de contacto maxima (N)

    # Flujo (en gauge representativo externo al boulder)
    max_flow_velocity: float     # Velocidad maxima del flujo (m/s)
    max_water_height: float      # Altura maxima del agua (m)

    # Criterio de falla
    moved: bool                  # True si supero umbral de desplazamiento
    rotated: bool                # True si supero umbral de rotacion
    failed: bool                 # True si moved OR rotated

    # Metadata
    sim_time_reached: float      # Tiempo simulado alcanzado (s)
    n_timesteps: int             # Numero de filas en ChronoExchange
    reference_time_s: float = 0.0
    classification_mode: str = "combined"
    flow_gauge_id: str = ""
    flow_gauge_distance: float = float("nan")
    water_gauge_id: str = ""
    water_gauge_distance: float = float("nan")

    # Parametros de entrada (para ML surrogate)
    dam_height: float = 0.0      # Altura columna de agua (m)
    boulder_mass: float = 0.0    # Masa del boulder (kg)
    boulder_rot_z: float = 0.0   # Angulo de orientacion Z (grados)
    friction_coefficient: float = 0.0  # Coef. friccion (Kfric Chrono)
    slope_inv: float = 20.0     # Inverso de pendiente (20 = 1:20)
    dp: float = 0.0              # Distancia entre particulas (m)
    stl_file: str = ""           # Nombre del STL usado


# ---------------------------------------------------------------------------
# Parseo de CSVs
# ---------------------------------------------------------------------------

def parse_chrono_exchange(csv_path: Path) -> pd.DataFrame:
    """
    Parsea ChronoExchange_mkbound_*.csv (cinematica del boulder).

    Columnas: nstep; time [s]; dt [s]; predictor; face.x/y/z [m/s^2];
              fomegaace.x/y/z [rad/s^2]; fvel.x/y/z [m/s];
              fcenter.x/y/z [m]; fomega.x/y/z [rad/s]
    """
    df = pd.read_csv(csv_path, sep=';')

    # Renombrar columnas para facilitar acceso
    rename = {
        'time [s]': 'time',
        'dt [s]': 'dt',
        'face.x [m/s^2]': 'acc_x', 'face.y [m/s^2]': 'acc_y', 'face.z [m/s^2]': 'acc_z',
        'fomegaace.x [rad/s^2]': 'alpha_x', 'fomegaace.y [rad/s^2]': 'alpha_y', 'fomegaace.z [rad/s^2]': 'alpha_z',
        'fvel.x [m/s]': 'vel_x', 'fvel.y [m/s]': 'vel_y', 'fvel.z [m/s]': 'vel_z',
        'fcenter.x [m]': 'cx', 'fcenter.y [m]': 'cy', 'fcenter.z [m]': 'cz',
        'fomega.x [rad/s]': 'omega_x', 'fomega.y [rad/s]': 'omega_y', 'fomega.z [rad/s]': 'omega_z',
    }
    df = df.rename(columns=rename)

    # Convertir 'predictor' de string a bool
    if 'predictor' in df.columns:
        df['predictor'] = df['predictor'].map({'True': True, 'False': False})

    logger.info(f"  ChronoExchange: {len(df)} filas, t=[{df['time'].iloc[0]:.4f}, {df['time'].iloc[-1]:.4f}]s")
    return df


def parse_chrono_forces(csv_path: Path) -> pd.DataFrame:
    """
    Parsea ChronoBody_forces.csv (fuerzas SPH + contacto por cuerpo).

    Header problematico: columnas repetidas (fy, fz, mx...) para cada body.
    Resolvemos renombrando con prefijo del body.

    Columnas originales:
      Time; Body_BLIR_fx;fy;fz;mx;my;mz;cfx;cfy;cfz;cmx;cmy;cmz;
            Body_beach_fx;fy;fz;mx;my;mz;cfx;cfy;cfz;cmx;cmy;cmz;
    """
    # Leer header manualmente para resolver duplicados
    with open(csv_path) as f:
        header_line = f.readline().strip().rstrip(';')

    raw_cols = header_line.split(';')

    # Construir nombres unicos: detectar Body_* como inicio de bloque
    clean_cols = []
    current_body = ''
    body_suffixes = ['fx', 'fy', 'fz', 'mx', 'my', 'mz',
                     'cfx', 'cfy', 'cfz', 'cmx', 'cmy', 'cmz']
    suffix_idx = 0

    for col in raw_cols:
        col = col.strip()
        if col == 'Time':
            clean_cols.append('time')
        elif col.startswith('Body_'):
            # New body block: extract body name
            # "Body_BLIR_fx" -> body="blir", suffix="fx"
            parts = col.split('_', 2)  # ['Body', 'BLIR', 'fx']
            current_body = parts[1].lower()
            suffix = parts[2] if len(parts) > 2 else body_suffixes[0]
            clean_cols.append(f'{current_body}_{suffix}')
            suffix_idx = 1  # Next suffix
        else:
            # Continuation of current body block
            clean_cols.append(f'{current_body}_{col.strip()}')
            suffix_idx += 1

    df = pd.read_csv(csv_path, sep=';', header=0, usecols=range(len(clean_cols)))
    df.columns = clean_cols

    logger.info(f"  ChronoBody_forces: {len(df)} filas, bodies: "
                f"{set(c.split('_')[0] for c in clean_cols if '_' in c and c != 'time')}")
    return df


def parse_gauge_velocity(csv_path: Path) -> pd.DataFrame:
    """
    Parsea GaugesVel_V**.csv (velocidad del flujo en un punto).

    Columnas: time [s]; velx [m/s]; vely [m/s]; velz [m/s]; posx [m]; posy [m]; posz [m]
    """
    df = pd.read_csv(csv_path, sep=';')
    rename = {
        'time [s]': 'time',
        'velx [m/s]': 'velx', 'vely [m/s]': 'vely', 'velz [m/s]': 'velz',
        'posx [m]': 'posx', 'posy [m]': 'posy', 'posz [m]': 'posz',
    }
    df = df.rename(columns=rename)

    # Reemplazar sentinels con NaN
    for col in ['velx', 'vely', 'velz']:
        df.loc[df[col] < SENTINEL_THRESHOLD, col] = np.nan

    return df


def parse_gauge_maxz(csv_path: Path) -> pd.DataFrame:
    """
    Parsea GaugesMaxZ_hmax**.csv (altura maxima del agua).

    Columnas: time [s]; zmax [m]; posx [m]; posy [m]; posz [m]
    """
    df = pd.read_csv(csv_path, sep=';')
    rename = {
        'time [s]': 'time',
        'zmax [m]': 'zmax',
        'posx [m]': 'posx', 'posy [m]': 'posy', 'posz [m]': 'posz',
    }
    df = df.rename(columns=rename)

    # Reemplazar sentinels con NaN
    df.loc[df['zmax'] < SENTINEL_THRESHOLD, 'zmax'] = np.nan

    return df


def parse_all_gauges(case_dir: Path) -> dict:
    """
    Parsea todos los Gauges de un caso.

    Returns:
        dict con claves 'velocity' y 'maxz', cada una es una lista de
        (gauge_id, DataFrame, position).
    """
    result = {'velocity': [], 'maxz': []}

    # Velocity gauges
    for csv_path in sorted(case_dir.glob('GaugesVel_V*.csv')):
        gauge_id = csv_path.stem.replace('GaugesVel_V', '')
        df = parse_gauge_velocity(csv_path)
        pos = (df['posx'].iloc[0], df['posy'].iloc[0], df['posz'].iloc[0])
        result['velocity'].append((gauge_id, df, pos))

    # MaxZ gauges
    for csv_path in sorted(case_dir.glob('GaugesMaxZ_hmax*.csv')):
        gauge_id = csv_path.stem.replace('GaugesMaxZ_hmax', '')
        df = parse_gauge_maxz(csv_path)
        pos = (df['posx'].iloc[0], df['posy'].iloc[0], df['posz'].iloc[0])
        result['maxz'].append((gauge_id, df, pos))

    logger.info(f"  Gauges: {len(result['velocity'])} velocity, {len(result['maxz'])} maxZ")
    return result


# ---------------------------------------------------------------------------
# Analisis de cinematica del boulder
# ---------------------------------------------------------------------------

def _resolve_reference_index(chrono_df: pd.DataFrame,
                             reference_time_s: Optional[float]) -> int:
    """Retorna el indice de referencia para metricas temporales."""
    if reference_time_s is None:
        return 0

    valid = chrono_df.index[chrono_df['time'] >= reference_time_s]
    if len(valid) == 0:
        logger.warning(
            "  reference_time_s=%.3f fuera de rango; se usa la ultima fila como referencia",
            reference_time_s,
        )
        return len(chrono_df) - 1
    return int(valid[0])


def compute_displacement(chrono_df: pd.DataFrame,
                         reference_time_s: Optional[float] = None) -> pd.Series:
    """Calcula desplazamiento del CM respecto a una referencia temporal dada."""
    ref_idx = _resolve_reference_index(chrono_df, reference_time_s)
    cx0 = chrono_df['cx'].iloc[ref_idx]
    cy0 = chrono_df['cy'].iloc[ref_idx]
    cz0 = chrono_df['cz'].iloc[ref_idx]

    return np.sqrt(
        (chrono_df['cx'] - cx0)**2 +
        (chrono_df['cy'] - cy0)**2 +
        (chrono_df['cz'] - cz0)**2
    )


def compute_rotation(chrono_df: pd.DataFrame,
                     reference_time_s: Optional[float] = None) -> pd.Series:
    """
    Calcula rotacion acumulada integrando velocidad angular.

    Aproximacion: integral trapezoidal de |omega| sobre el tiempo.
    Resultado en grados.
    """
    ref_idx = _resolve_reference_index(chrono_df, reference_time_s)
    segment = chrono_df.iloc[ref_idx:].copy()
    omega_mag = np.sqrt(
        segment['omega_x']**2 +
        segment['omega_y']**2 +
        segment['omega_z']**2
    )
    dt = segment['time'].diff().fillna(0)
    rotation_rad = np.cumsum(omega_mag * dt)

    rotation_deg = pd.Series(0.0, index=chrono_df.index, dtype=float)
    rotation_deg.loc[segment.index] = np.degrees(rotation_rad)
    return rotation_deg


def compute_boulder_velocity(chrono_df: pd.DataFrame) -> pd.Series:
    """Calcula magnitud de velocidad del boulder."""
    return np.sqrt(
        chrono_df['vel_x']**2 +
        chrono_df['vel_y']**2 +
        chrono_df['vel_z']**2
    )


# ---------------------------------------------------------------------------
# Analisis de fuerzas
# ---------------------------------------------------------------------------

def compute_forces(forces_df: pd.DataFrame, body: str = 'blir',
                    boulder_mass: float = 1.06) -> dict:
    """
    Extrae fuerzas maximas sobre un cuerpo.

    En ChronoBody_forces:
    - fx/fy/fz = fuerzas SPH (presion + viscosidad + gravedad)
    - cfx/cfy/cfz = fuerzas de contacto (Chrono)
    - mx/my/mz = momentos SPH
    - cmx/cmy/cmz = momentos de contacto

    NOTA: fz incluye gravedad (peso = mass * g). Se resta para obtener
    la fuerza hidrodinamica neta.
    """
    # Fuerza SPH hidrodinamica (restar peso de fz)
    weight = boulder_mass * 9.81  # N
    sph_force = np.sqrt(
        forces_df[f'{body}_fx']**2 +
        forces_df[f'{body}_fy']**2 +
        (forces_df[f'{body}_fz'] + weight)**2  # fz es negativa por gravedad
    )

    # Fuerza de contacto
    contact_force = np.sqrt(
        forces_df[f'{body}_cfx']**2 +
        forces_df[f'{body}_cfy']**2 +
        forces_df[f'{body}_cfz']**2
    )

    return {
        'max_sph_force': float(sph_force.max()),
        'max_contact_force': float(contact_force.max()),
        'sph_force_series': sph_force,
        'contact_force_series': contact_force,
    }


# ---------------------------------------------------------------------------
# Analisis de flujo
# ---------------------------------------------------------------------------

def find_nearest_gauge(gauges: list, boulder_pos: tuple) -> tuple:
    """
    Encuentra el gauge mas cercano a la posicion del boulder.

    Args:
        gauges: Lista de (gauge_id, df, position).
        boulder_pos: (x, y, z) del boulder.

    Returns:
        (gauge_id, df, distance)
    """
    if not gauges:
        return None, None, float('inf')

    bx, by, bz = boulder_pos
    best = None
    best_dist = float('inf')

    for gauge_id, df, (gx, gy, gz) in gauges:
        dist = np.sqrt((gx - bx)**2 + (gy - by)**2 + (gz - bz)**2)
        if dist < best_dist:
            best_dist = dist
            best = (gauge_id, df)

    return best[0], best[1], best_dist


def _velocity_magnitude(gauge_df: pd.DataFrame) -> pd.Series:
    return np.sqrt(gauge_df['velx']**2 + gauge_df['vely']**2 + gauge_df['velz']**2)


def _external_gauge_candidates(gauges: list, boulder_pos: tuple,
                               exclusion_radius_m: float) -> list[tuple]:
    bx, by, bz = boulder_pos
    candidates = []
    for gauge_id, df, (gx, gy, gz) in gauges:
        dx = gx - bx
        dy = gy - by
        dz = gz - bz
        dist = float(np.sqrt(dx**2 + dy**2 + dz**2))
        radial = float(np.sqrt(dx**2 + dz**2))
        outside = radial > exclusion_radius_m
        upstream = gx <= bx
        candidates.append((gauge_id, df, dist, outside, upstream, dx))
    return candidates


def find_representative_velocity_gauge(gauges: list, boulder_pos: tuple,
                                       d_eq: float) -> tuple:
    """
    Selecciona un gauge de velocidad representativo del flujo incidente.

    Prioriza gauges fuera del cuerpo, aguas arriba y con señal valida.
    """
    if not gauges:
        return None, None, float('inf')

    exclusion_radius = max(0.5 * d_eq, 0.05)
    ranked = []
    for gauge_id, df, dist, outside, upstream, dx in _external_gauge_candidates(
        gauges, boulder_pos, exclusion_radius
    ):
        vel_mag = _velocity_magnitude(df).dropna()
        peak = float(vel_mag.max()) if len(vel_mag) else 0.0
        score = (
            0 if outside and upstream and peak > 0 else
            1 if outside and peak > 0 else
            2 if outside and upstream else
            3 if outside else
            4,
            abs(dx),
            dist,
            -peak,
        )
        ranked.append((score, gauge_id, df, dist))

    ranked.sort(key=lambda item: item[0])
    _, gauge_id, df, dist = ranked[0]
    return gauge_id, df, dist


def find_representative_maxz_gauge(gauges: list, boulder_pos: tuple,
                                   d_eq: float) -> tuple:
    """Selecciona un gauge de maxz cercano pero fuera del cuerpo."""
    if not gauges:
        return None, None, float('inf')

    exclusion_radius = max(0.5 * d_eq, 0.05)
    ranked = []
    for gauge_id, df, dist, outside, upstream, dx in _external_gauge_candidates(
        gauges, boulder_pos, exclusion_radius
    ):
        valid = df['zmax'].dropna()
        peak = float(valid.max()) if len(valid) else 0.0
        score = (
            0 if outside and upstream and peak > 0 else
            1 if outside and peak > 0 else
            2 if outside else
            3,
            abs(dx),
            dist,
            -peak,
        )
        ranked.append((score, gauge_id, df, dist))

    ranked.sort(key=lambda item: item[0])
    _, gauge_id, df, dist = ranked[0]
    return gauge_id, df, dist


def classify_failure(max_disp: float, max_rot: float,
                     disp_threshold_m: float, rot_threshold_deg: float,
                     classification_mode: str = "combined") -> tuple[bool, bool, bool]:
    """Evalua moved/rotated y decide failed segun el modo pedido."""
    moved = max_disp > disp_threshold_m
    rotated = max_rot > rot_threshold_deg

    mode = classification_mode.lower()
    if mode == "combined":
        failed = moved or rotated
    elif mode == "displacement_only":
        failed = moved
    elif mode == "rotation_only":
        failed = rotated
    else:
        raise ValueError(
            f"classification_mode invalido: {classification_mode}. "
            "Usa combined|displacement_only|rotation_only"
        )

    return moved, rotated, failed


# ---------------------------------------------------------------------------
# Funcion principal: procesar un caso completo
# ---------------------------------------------------------------------------

def process_case(case_dir: Path, d_eq: float,
                 boulder_mass: float = 1.06,
                 disp_threshold_pct: float = 5.0,
                 rot_threshold_deg: float = 5.0,
                 reference_time_s: Optional[float] = None,
                 classification_mode: str = "combined") -> CaseResult:
    """
    Procesa todos los CSVs de un caso y determina si hubo incipient motion.

    Args:
        case_dir: Directorio con los CSVs del caso (data/processed/case_name/).
        d_eq: Diametro equivalente esferico del boulder (m).
        disp_threshold_pct: Umbral de desplazamiento (% de d_eq).
        rot_threshold_deg: Umbral de rotacion (grados).
        reference_time_s: Referencia temporal para displacement/rotation.
        classification_mode: combined | displacement_only | rotation_only.

    Returns:
        CaseResult con metricas y criterio de falla.
    """
    case_name = case_dir.name
    logger.info(f"Procesando caso: {case_name}")

    # --- 1. ChronoExchange (cinematica) ---
    chrono_csvs = sorted(case_dir.glob('ChronoExchange*.csv'))
    if not chrono_csvs:
        raise FileNotFoundError(f"No se encontro ChronoExchange CSV en {case_dir}")
    chrono_df = parse_chrono_exchange(chrono_csvs[0])

    ref_idx = _resolve_reference_index(chrono_df, reference_time_s)
    ref_time_used = float(chrono_df['time'].iloc[ref_idx])
    if reference_time_s is not None:
        logger.info(f"  Baseline temporal: t_ref={ref_time_used:.4f}s")

    displacement = compute_displacement(chrono_df, reference_time_s=reference_time_s)
    rotation = compute_rotation(chrono_df, reference_time_s=reference_time_s)
    velocity = compute_boulder_velocity(chrono_df)

    max_disp = float(displacement.max())
    max_disp_rel = (max_disp / d_eq) * 100  # porcentaje de d_eq
    max_rot = float(rotation.max())
    max_vel = float(velocity.max())

    logger.info(f"  Desplazamiento max: {max_disp:.6f}m ({max_disp_rel:.2f}% de d_eq={d_eq:.4f}m)")
    logger.info(f"  Rotacion acumulada max: {max_rot:.2f} grados")
    logger.info(f"  Velocidad max boulder: {max_vel:.4f} m/s")

    # --- 2. ChronoBody_forces ---
    forces_csv = case_dir / 'ChronoBody_forces.csv'
    max_sph = 0.0
    max_contact = 0.0
    if forces_csv.exists():
        forces_df = parse_chrono_forces(forces_csv)
        forces = compute_forces(forces_df, body='blir', boulder_mass=boulder_mass)
        max_sph = forces['max_sph_force']
        max_contact = forces['max_contact_force']
        logger.info(f"  Fuerza SPH max: {max_sph:.4f}N, Contacto max: {max_contact:.4f}N")
    else:
        logger.warning(f"  ChronoBody_forces.csv no encontrado")

    # --- 3. Gauges ---
    gauges = parse_all_gauges(case_dir)

    # Posicion inicial del boulder
    boulder_pos = (chrono_df['cx'].iloc[0], chrono_df['cy'].iloc[0], chrono_df['cz'].iloc[0])

    # Velocidad del flujo (gauge representativo del flujo incidente)
    max_flow_vel = 0.0
    flow_gauge_id = ""
    flow_gauge_dist = float("nan")
    if gauges['velocity']:
        gid, gdf, gdist = find_representative_velocity_gauge(
            gauges['velocity'], boulder_pos, d_eq
        )
        vel_mag = _velocity_magnitude(gdf)
        max_flow_vel = float(vel_mag.max())
        flow_gauge_id = f"V{gid}"
        flow_gauge_dist = gdist
        logger.info(f"  Flujo max (gauge V{gid}, dist={gdist:.2f}m): {max_flow_vel:.4f} m/s")

    # Altura del agua (gauge representativo cercano pero fuera del cuerpo)
    max_water_h = 0.0
    water_gauge_id = ""
    water_gauge_dist = float("nan")
    if gauges['maxz']:
        gid, gdf, gdist = find_representative_maxz_gauge(
            gauges['maxz'], boulder_pos, d_eq
        )
        valid_zmax = gdf['zmax'].dropna()
        if len(valid_zmax) > 0:
            max_water_h = float(valid_zmax.max())
        water_gauge_id = f"hmax{gid}"
        water_gauge_dist = gdist
        logger.info(f"  Agua max (gauge hmax{gid}, dist={gdist:.2f}m): {max_water_h:.4f}m")

    # --- 4. Criterio de falla ---
    disp_threshold_m = d_eq * (disp_threshold_pct / 100.0)
    moved, rotated, failed = classify_failure(
        max_disp=max_disp,
        max_rot=max_rot,
        disp_threshold_m=disp_threshold_m,
        rot_threshold_deg=rot_threshold_deg,
        classification_mode=classification_mode,
    )

    status = "FALLO" if failed else "ESTABLE"
    logger.info(
        f"  Criterio ({classification_mode}): {status} "
        f"(umbral disp={disp_threshold_pct}% d_eq={disp_threshold_m:.4f}m, "
        f"rot={rot_threshold_deg} deg)"
    )
    logger.info(f"  Flags criterio: moved={moved}, rotated={rotated}")

    return CaseResult(
        case_name=case_name,
        max_displacement=max_disp,
        max_displacement_rel=max_disp_rel,
        max_rotation=max_rot,
        max_velocity=max_vel,
        max_sph_force=max_sph,
        max_contact_force=max_contact,
        max_flow_velocity=max_flow_vel,
        max_water_height=max_water_h,
        moved=moved,
        rotated=rotated,
        failed=failed,
        sim_time_reached=float(chrono_df['time'].iloc[-1]),
        n_timesteps=len(chrono_df),
        reference_time_s=ref_time_used,
        classification_mode=classification_mode,
        flow_gauge_id=flow_gauge_id,
        flow_gauge_distance=flow_gauge_dist,
        water_gauge_id=water_gauge_id,
        water_gauge_distance=water_gauge_dist,
    )


# ---------------------------------------------------------------------------
# Persistencia en SQLite
# ---------------------------------------------------------------------------

def save_to_sqlite(results: list, db_path: Path, table: str = 'results'):
    """
    Guarda lista de CaseResult en SQLite.

    Crea la tabla si no existe. Inserta filas nuevas (no duplica case_name).
    """
    from dataclasses import asdict
    import sqlite3

    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(db_path))

    df = pd.DataFrame([asdict(r) for r in results])

    # Eliminar resultados previos de los mismos casos (upsert)
    cursor = conn.cursor()
    cursor.execute(f"""
        CREATE TABLE IF NOT EXISTS {table} (
            case_name TEXT PRIMARY KEY,
            max_displacement REAL,
            max_displacement_rel REAL,
            max_rotation REAL,
            max_velocity REAL,
            max_sph_force REAL,
            max_contact_force REAL,
            max_flow_velocity REAL,
            max_water_height REAL,
            moved INTEGER,
            rotated INTEGER,
            failed INTEGER,
            sim_time_reached REAL,
            n_timesteps INTEGER,
            dam_height REAL,
            boulder_mass REAL,
            boulder_rot_z REAL,
            friction_coefficient REAL,
            slope_inv REAL,
            dp REAL,
            stl_file TEXT,
            reference_time_s REAL,
            classification_mode TEXT,
            flow_gauge_id TEXT,
            flow_gauge_distance REAL,
            water_gauge_id TEXT,
            water_gauge_distance REAL
        )
    """)

    # Agregar columnas nuevas si la tabla ya existia sin ellas
    existing_cols = {row[1] for row in cursor.execute(f"PRAGMA table_info({table})").fetchall()}
    for col, coltype in [('dam_height', 'REAL'), ('boulder_mass', 'REAL'),
                         ('boulder_rot_z', 'REAL'), ('friction_coefficient', 'REAL'),
                         ('slope_inv', 'REAL'), ('dp', 'REAL'), ('stl_file', 'TEXT'),
                         ('reference_time_s', 'REAL'), ('classification_mode', 'TEXT'),
                         ('flow_gauge_id', 'TEXT'), ('flow_gauge_distance', 'REAL'),
                         ('water_gauge_id', 'TEXT'), ('water_gauge_distance', 'REAL')]:
        if col not in existing_cols:
            cursor.execute(f"ALTER TABLE {table} ADD COLUMN {col} {coltype}")
            logger.info(f"  SQLite: columna '{col}' agregada a tabla '{table}'")

    for _, row in df.iterrows():
        cursor.execute(f"""
            INSERT OR REPLACE INTO {table} (
                case_name, max_displacement, max_displacement_rel,
                max_rotation, max_velocity,
                max_sph_force, max_contact_force,
                max_flow_velocity, max_water_height,
                moved, rotated, failed,
                sim_time_reached, n_timesteps,
                dam_height, boulder_mass, boulder_rot_z,
                friction_coefficient, slope_inv, dp, stl_file,
                reference_time_s, classification_mode,
                flow_gauge_id, flow_gauge_distance,
                water_gauge_id, water_gauge_distance
            ) VALUES (
                ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?
            )
        """, (
            row['case_name'],
            row['max_displacement'], row['max_displacement_rel'],
            row['max_rotation'], row['max_velocity'],
            row['max_sph_force'], row['max_contact_force'],
            row['max_flow_velocity'], row['max_water_height'],
            int(row['moved']), int(row['rotated']), int(row['failed']),
            row['sim_time_reached'], row['n_timesteps'],
            row.get('dam_height', 0.0), row.get('boulder_mass', 0.0),
            row.get('boulder_rot_z', 0.0), row.get('friction_coefficient', 0.0),
            row.get('slope_inv', 20.0),
            row.get('dp', 0.0), row.get('stl_file', ''),
            row.get('reference_time_s', 0.0), row.get('classification_mode', 'combined'),
            row.get('flow_gauge_id', ''), row.get('flow_gauge_distance', float('nan')),
            row.get('water_gauge_id', ''), row.get('water_gauge_distance', float('nan')),
        ))

    conn.commit()
    conn.close()
    logger.info(f"SQLite: {len(results)} resultados guardados en {db_path}:{table}")


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

    # Determinar directorio de CSVs
    if len(sys.argv) > 1:
        case_dir = Path(sys.argv[1])
    else:
        # Default: usar datos de Diego como ejemplo
        case_dir = project_root / 'ENTREGA_KEVIN'

    # d_eq del boulder (de boulder_properties.txt o hardcoded)
    d_eq = 0.1004  # metros, calculado por geometry_builder

    result = process_case(case_dir, d_eq=d_eq)

    print(f"\n{'='*60}")
    print(f"Caso: {result.case_name}")
    print(f"{'='*60}")
    print(f"Desplazamiento max:  {result.max_displacement:.6f}m ({result.max_displacement_rel:.2f}% d_eq)")
    print(f"Rotacion max:        {result.max_rotation:.2f} grados")
    print(f"Velocidad max:       {result.max_velocity:.4f} m/s")
    print(f"Fuerza SPH max:      {result.max_sph_force:.4f} N")
    print(f"Fuerza contacto max: {result.max_contact_force:.4f} N")
    print(f"Flujo max:           {result.max_flow_velocity:.4f} m/s")
    print(f"Agua max:            {result.max_water_height:.4f} m")
    print(f"Tiempo simulado:     {result.sim_time_reached:.4f}s ({result.n_timesteps} steps)")
    print(f"Resultado:           {'FALLO' if result.failed else 'ESTABLE'}")

    # Guardar en SQLite
    db_path = project_root / 'data' / 'results.sqlite'
    save_to_sqlite([result], db_path)
    print(f"\nGuardado en: {db_path}")
