from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import re
from typing import Dict, Iterable, List, Optional, Union

import numpy as np
import pandas as pd

PathLike = Union[str, Path]

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_IMPORT_ROOT = PROJECT_ROOT / "imports" / "ws_prelim_20260421_144616"
DEFAULT_D_EQ_M = 0.1004

GAUGE_SENTINEL = -3.40282e38
GAUGE_SENTINEL_THRESHOLD = -3.0e38

_MU_RE = re.compile(r"(?:^|_)f(?P<token>\d+)(?:[a-z]+)?(?:_|$)", re.IGNORECASE)
_DP_RE = re.compile(r"(?:^|_)dp(?P<token>\d+)(?:_|$)", re.IGNORECASE)

_SUMMARY_ALIASES = {
    "case_name": ["case_name", "case_id"],
    "dp": ["dp"],
    "max_displacement_m": ["max_displacement_m", "max_displacement", "displacement_m"],
    "max_displacement_rel_pct": ["max_displacement_rel", "disp_pct_deq"],
    "max_rotation_deg": ["max_rotation_deg", "max_rotation", "rotation_deg"],
    "max_velocity_ms": ["max_velocity_ms", "max_velocity", "velocity_ms"],
    "max_sph_force_N": ["max_sph_force_N", "max_sph_force", "sph_force_N"],
    "max_contact_force_N": ["max_contact_force_N", "max_contact_force", "contact_force_N"],
    "max_flow_velocity_ms": ["max_flow_velocity_ms", "max_flow_velocity", "flow_velocity_ms"],
    "max_water_height_m": ["max_water_height_m", "max_water_height", "water_height_m"],
    "sim_time_s": ["sim_time_s", "sim_time_reached", "duration_s"],
    "n_timesteps": ["n_timesteps", "Steps"],
    "status": ["status"],
    "criterion_mode": ["criterion_mode", "classification_mode"],
    "criterion_class": ["criterion_class"],
    "criterion_reference_time_s": ["criterion_reference_time_s", "reference_time_s"],
    "moved": ["moved"],
    "rotated": ["rotated"],
    "failed": ["failed"],
    "flow_gauge_id": ["flow_gauge_id"],
    "water_gauge_id": ["water_gauge_id"],
    "tiempo_min": ["tiempo_min"],
    "dam_height": ["dam_height"],
    "boulder_mass": ["boulder_mass"],
    "boulder_rot_z": ["boulder_rot_z"],
    "stl_file": ["stl_file"],
    "source": ["source"],
}

_NUMERIC_SUMMARY_COLUMNS = [
    "dp",
    "mu",
    "d_eq_m",
    "max_displacement_m",
    "max_displacement_rel_pct",
    "max_rotation_deg",
    "max_velocity_ms",
    "max_sph_force_N",
    "max_contact_force_N",
    "max_flow_velocity_ms",
    "max_water_height_m",
    "sim_time_s",
    "n_timesteps",
    "criterion_reference_time_s",
    "tiempo_min",
    "dam_height",
    "boulder_mass",
    "boulder_rot_z",
    "disp_mm",
    "disp_pct_deq",
    "disp_over_deq",
    "dp_mm",
]


@dataclass(frozen=True)
class WSPrelimPaths:
    import_root: Path
    meta_dir: Path
    results_dir: Path
    cases_complete_dir: Path


def resolve_import_paths(import_root: Optional[PathLike] = None) -> WSPrelimPaths:
    root = Path(import_root) if import_root is not None else DEFAULT_IMPORT_ROOT
    root = root.expanduser().resolve()

    meta_dir = root / "meta"
    results_dir = meta_dir / "results"
    cases_complete_dir = root / "cases_complete"

    for required_dir in (root, meta_dir, results_dir, cases_complete_dir):
        if not required_dir.exists():
            raise FileNotFoundError("Missing required import path: {}".format(required_dir))

    return WSPrelimPaths(
        import_root=root,
        meta_dir=meta_dir,
        results_dir=results_dir,
        cases_complete_dir=cases_complete_dir,
    )


def list_summary_csvs(
    import_root: Optional[PathLike] = None,
    include_backups: bool = False,
) -> List[Path]:
    paths = resolve_import_paths(import_root)
    csv_paths = sorted(paths.results_dir.glob("*.csv"))
    if include_backups:
        return csv_paths
    return [csv_path for csv_path in csv_paths if "_backup_" not in csv_path.stem]


def parse_mu_from_name(name: str) -> Optional[float]:
    match = _MU_RE.search(name)
    if not match:
        return None
    return _parse_compact_decimal(match.group("token"))


def parse_dp_from_name(name: str) -> Optional[float]:
    match = _DP_RE.search(name)
    if not match:
        return None
    return _parse_compact_decimal(match.group("token"))


def derive_case_family(name: str) -> str:
    family = re.sub(r"_dp\d+(?=_|$)", "", name)
    family = re.sub(r"_backup.*$", "", family)
    family = re.sub(r"__+", "_", family)
    return family.strip("_")


def derive_campaign(name: str) -> str:
    base = derive_case_family(name)
    tokens = [token for token in base.split("_") if token]
    campaign_tokens: List[str] = []

    for token in tokens:
        if _MU_RE.fullmatch("_" + token):
            break
        if _DP_RE.fullmatch("_" + token):
            break
        if token == "full":
            break
        campaign_tokens.append(token)

    if campaign_tokens:
        return "_".join(campaign_tokens)
    return base


def is_gauge_sentinel(values):  # type: ignore[no-untyped-def]
    if isinstance(values, pd.DataFrame):
        return values <= GAUGE_SENTINEL_THRESHOLD
    if isinstance(values, pd.Series):
        return values <= GAUGE_SENTINEL_THRESHOLD
    if isinstance(values, np.ndarray):
        return values <= GAUGE_SENTINEL_THRESHOLD
    if values is None or pd.isna(values):
        return False
    return float(values) <= GAUGE_SENTINEL_THRESHOLD


def find_case_out_dir(
    case_name: str,
    import_root: Optional[PathLike] = None,
) -> Path:
    paths = resolve_import_paths(import_root)
    case_dir = paths.cases_complete_dir / case_name
    if not case_dir.exists():
        raise FileNotFoundError("Case directory not found: {}".format(case_dir))

    exact_out_dir = case_dir / "{}_out".format(case_name)
    if exact_out_dir.exists():
        return exact_out_dir

    out_dirs = sorted(path for path in case_dir.glob("*_out") if path.is_dir())
    if not out_dirs:
        raise FileNotFoundError("No *_out directory found inside {}".format(case_dir))
    if len(out_dirs) > 1:
        raise FileExistsError("Multiple *_out directories found inside {}".format(case_dir))
    return out_dirs[0]


def load_summary_csv(
    summary_csv: PathLike,
    import_root: Optional[PathLike] = None,
    default_d_eq_m: float = DEFAULT_D_EQ_M,
) -> pd.DataFrame:
    csv_path = Path(summary_csv)
    if not csv_path.is_absolute() and import_root is not None:
        csv_path = resolve_import_paths(import_root).results_dir / csv_path
    csv_path = csv_path.expanduser().resolve()
    if not csv_path.exists():
        raise FileNotFoundError("Summary CSV not found: {}".format(csv_path))

    paths = resolve_import_paths(import_root)
    df = _read_table(csv_path)
    return _normalize_summary_df(df=df, csv_path=csv_path, paths=paths, default_d_eq_m=default_d_eq_m)


def load_summary_master_df(
    import_root: Optional[PathLike] = None,
    include_backups: bool = False,
    default_d_eq_m: float = DEFAULT_D_EQ_M,
) -> pd.DataFrame:
    paths = resolve_import_paths(import_root)
    frames = [
        load_summary_csv(csv_path, import_root=paths.import_root, default_d_eq_m=default_d_eq_m)
        for csv_path in list_summary_csvs(paths.import_root, include_backups=include_backups)
    ]
    if not frames:
        return pd.DataFrame()

    master = pd.concat(frames, ignore_index=True, sort=False)
    sort_cols = [col for col in ("campaign", "group", "family", "case_name", "dp") if col in master.columns]
    if sort_cols:
        master = master.sort_values(sort_cols, kind="stable").reset_index(drop=True)
    return master


def load_chrono_exchange(
    case_name_or_out_dir: PathLike,
    import_root: Optional[PathLike] = None,
) -> pd.DataFrame:
    out_dir = _resolve_case_out_dir(case_name_or_out_dir, import_root)
    csv_path = _find_single(out_dir, "ChronoExchange_*.csv")
    df = _read_table(csv_path)
    rename_map = {
        "time [s]": "time",
        "dt [s]": "dt",
        "face.x [m/s^2]": "acc_x",
        "face.y [m/s^2]": "acc_y",
        "face.z [m/s^2]": "acc_z",
        "fomegaace.x [rad/s^2]": "alpha_x",
        "fomegaace.y [rad/s^2]": "alpha_y",
        "fomegaace.z [rad/s^2]": "alpha_z",
        "fvel.x [m/s]": "vel_x",
        "fvel.y [m/s]": "vel_y",
        "fvel.z [m/s]": "vel_z",
        "fcenter.x [m]": "cx",
        "fcenter.y [m]": "cy",
        "fcenter.z [m]": "cz",
        "fomega.x [rad/s]": "omega_x",
        "fomega.y [rad/s]": "omega_y",
        "fomega.z [rad/s]": "omega_z",
    }
    df = df.rename(columns=rename_map)
    if "predictor" in df.columns:
        df["predictor"] = _coerce_bool_series(df["predictor"])
    return df


def load_chrono_body_forces(
    case_name_or_out_dir: PathLike,
    import_root: Optional[PathLike] = None,
) -> pd.DataFrame:
    out_dir = _resolve_case_out_dir(case_name_or_out_dir, import_root)
    csv_path = out_dir / "ChronoBody_forces.csv"
    if not csv_path.exists():
        raise FileNotFoundError("ChronoBody_forces.csv not found in {}".format(out_dir))

    with csv_path.open("r", encoding="utf-8", errors="replace") as handle:
        header_line = handle.readline().strip().rstrip(";")

    raw_columns = header_line.split(";")
    clean_columns: List[str] = []
    current_body = ""

    for raw_column in raw_columns:
        column = raw_column.strip()
        if column == "Time":
            clean_columns.append("time")
            continue
        if column.startswith("Body_"):
            parts = column.split("_", 2)
            current_body = parts[1].lower()
            suffix = parts[2] if len(parts) > 2 else "fx"
            clean_columns.append("{}_{}".format(current_body, suffix))
            continue
        clean_columns.append("{}_{}".format(current_body, column))

    df = pd.read_csv(csv_path, sep=";", usecols=range(len(clean_columns)))
    df.columns = clean_columns
    return df


def load_gauges_vel(
    case_name_or_out_dir: PathLike,
    import_root: Optional[PathLike] = None,
    gauge_id: Optional[str] = None,
) -> Union[pd.DataFrame, Dict[str, pd.DataFrame]]:
    out_dir = _resolve_case_out_dir(case_name_or_out_dir, import_root)
    return _load_gauge_group(
        out_dir=out_dir,
        pattern="GaugesVel_*.csv",
        gauge_prefix="GaugesVel_",
        gauge_id=gauge_id,
        rename_map={
            "time [s]": "time",
            "velx [m/s]": "velx",
            "vely [m/s]": "vely",
            "velz [m/s]": "velz",
            "posx [m]": "posx",
            "posy [m]": "posy",
            "posz [m]": "posz",
        },
        value_columns=["velx", "vely", "velz"],
    )


def load_gauges_maxz(
    case_name_or_out_dir: PathLike,
    import_root: Optional[PathLike] = None,
    gauge_id: Optional[str] = None,
) -> Union[pd.DataFrame, Dict[str, pd.DataFrame]]:
    out_dir = _resolve_case_out_dir(case_name_or_out_dir, import_root)
    return _load_gauge_group(
        out_dir=out_dir,
        pattern="GaugesMaxZ_*.csv",
        gauge_prefix="GaugesMaxZ_",
        gauge_id=gauge_id,
        rename_map={
            "time [s]": "time",
            "zmax [m]": "zmax",
            "posx [m]": "posx",
            "posy [m]": "posy",
            "posz [m]": "posz",
        },
        value_columns=["zmax"],
    )


def load_run_csv(
    case_name_or_out_dir: PathLike,
    import_root: Optional[PathLike] = None,
) -> pd.DataFrame:
    out_dir = _resolve_case_out_dir(case_name_or_out_dir, import_root)
    csv_path = out_dir / "Run.csv"
    if not csv_path.exists():
        raise FileNotFoundError("Run.csv not found in {}".format(out_dir))

    df = _read_table(csv_path)
    if "#RunName" in df.columns:
        df = df.rename(columns={"#RunName": "run_name"})

    for column in df.columns:
        if df[column].dtype == object:
            cleaned = df[column].astype(str).str.replace(",", "", regex=False)
            numeric = pd.to_numeric(cleaned, errors="coerce")
            if numeric.notna().all():
                df[column] = numeric

    return df


def load_run(
    case_name_or_out_dir: PathLike,
    import_root: Optional[PathLike] = None,
) -> pd.DataFrame:
    return load_run_csv(case_name_or_out_dir, import_root=import_root)


def _read_table(csv_path: Path) -> pd.DataFrame:
    sep = _detect_separator(csv_path)
    return pd.read_csv(csv_path, sep=sep)


def _detect_separator(csv_path: Path) -> str:
    with csv_path.open("r", encoding="utf-8", errors="replace") as handle:
        header = handle.readline()
    if header.count(";") >= header.count(","):
        return ";"
    return ","


def _normalize_summary_df(
    df: pd.DataFrame,
    csv_path: Path,
    paths: WSPrelimPaths,
    default_d_eq_m: float,
) -> pd.DataFrame:
    normalized = df.copy()
    normalized.columns = [str(column).strip() for column in normalized.columns]

    for canonical_name, aliases in _SUMMARY_ALIASES.items():
        if canonical_name in normalized.columns:
            continue
        for alias in aliases:
            if alias in normalized.columns:
                normalized[canonical_name] = normalized[alias]
                break

    group_name = re.sub(r"_backup.*$", "", csv_path.stem)
    normalized["source_csv"] = csv_path.name
    normalized["source_path"] = str(csv_path)
    normalized["import_root"] = str(paths.import_root)
    normalized["group"] = csv_path.stem

    if "case_name" not in normalized.columns:
        normalized["case_name"] = [group_name] * len(normalized)

    normalized["case_name"] = normalized["case_name"].fillna("").astype(str).str.strip()

    if "dp" not in normalized.columns:
        normalized["dp"] = np.nan
    normalized["dp"] = _coerce_numeric_series(normalized["dp"])
    missing_dp = normalized["dp"].isna()
    normalized.loc[missing_dp, "dp"] = normalized.loc[missing_dp, "case_name"].map(parse_dp_from_name)
    missing_dp = normalized["dp"].isna()
    normalized.loc[missing_dp, "dp"] = parse_dp_from_name(csv_path.stem)

    normalized["mu"] = normalized["case_name"].map(parse_mu_from_name)
    missing_mu = normalized["mu"].isna()
    normalized.loc[missing_mu, "mu"] = parse_mu_from_name(csv_path.stem)

    normalized["family"] = normalized["case_name"].map(derive_case_family)
    normalized.loc[normalized["family"] == "", "family"] = group_name
    normalized["campaign"] = normalized["family"].map(derive_campaign)

    d_eq_cache: Dict[str, float] = {}
    case_out_cache: Dict[str, Optional[str]] = {}
    case_dir_cache: Dict[str, Optional[str]] = {}

    d_eq_values: List[float] = []
    case_dirs: List[Optional[str]] = []
    case_out_dirs: List[Optional[str]] = []

    for case_name in normalized["case_name"]:
        if case_name in d_eq_cache:
            d_eq_values.append(d_eq_cache[case_name])
            case_dirs.append(case_dir_cache[case_name])
            case_out_dirs.append(case_out_cache[case_name])
            continue

        case_dir = paths.cases_complete_dir / case_name
        if case_dir.exists():
            case_dir_cache[case_name] = str(case_dir)
            try:
                case_out_cache[case_name] = str(find_case_out_dir(case_name, paths.import_root))
            except FileNotFoundError:
                case_out_cache[case_name] = None
            d_eq_cache[case_name] = _load_case_d_eq(case_dir, default_d_eq_m)
        else:
            case_dir_cache[case_name] = None
            case_out_cache[case_name] = None
            d_eq_cache[case_name] = default_d_eq_m

        d_eq_values.append(d_eq_cache[case_name])
        case_dirs.append(case_dir_cache[case_name])
        case_out_dirs.append(case_out_cache[case_name])

    normalized["case_dir"] = case_dirs
    normalized["case_out_dir"] = case_out_dirs
    normalized["d_eq_m"] = d_eq_values

    normalized["dp_mm"] = normalized["dp"] * 1000.0
    normalized["disp_mm"] = _pick_numeric_series(normalized, "max_displacement_m") * 1000.0

    disp_pct = _pick_numeric_series(normalized, "max_displacement_rel_pct")
    if disp_pct.isna().all():
        disp_pct = (_pick_numeric_series(normalized, "max_displacement_m") / normalized["d_eq_m"]) * 100.0
    normalized["disp_pct_deq"] = disp_pct
    normalized["disp_over_deq"] = normalized["disp_pct_deq"] / 100.0

    if "failed" in normalized.columns:
        normalized["failed"] = _coerce_bool_series(normalized["failed"])
    elif "criterion_class" in normalized.columns:
        normalized["failed"] = normalized["criterion_class"].astype(str).str.upper().eq("FALLO")
    elif "moved" in normalized.columns or "rotated" in normalized.columns:
        moved = _coerce_bool_series(normalized.get("moved", False))
        rotated = _coerce_bool_series(normalized.get("rotated", False))
        normalized["failed"] = moved | rotated

    for bool_column in ("moved", "rotated"):
        if bool_column in normalized.columns:
            normalized[bool_column] = _coerce_bool_series(normalized[bool_column])

    for numeric_column in _NUMERIC_SUMMARY_COLUMNS:
        if numeric_column in normalized.columns:
            normalized[numeric_column] = _coerce_numeric_series(normalized[numeric_column])

    return normalized


def _pick_numeric_series(df: pd.DataFrame, column_name: str) -> pd.Series:
    if column_name not in df.columns:
        return pd.Series(np.nan, index=df.index, dtype=float)
    return _coerce_numeric_series(df[column_name])


def _coerce_numeric_series(series: pd.Series) -> pd.Series:
    if pd.api.types.is_numeric_dtype(series):
        return pd.to_numeric(series, errors="coerce")
    cleaned = series.map(lambda value: "" if pd.isna(value) else str(value).strip())
    cleaned = cleaned.replace({"": np.nan, "nan": np.nan, "None": np.nan})
    cleaned = cleaned.map(lambda value: value.replace(",", "") if isinstance(value, str) else value)
    return pd.to_numeric(cleaned, errors="coerce")


def _coerce_bool_series(values) -> pd.Series:  # type: ignore[no-untyped-def]
    if isinstance(values, pd.Series):
        series = values.copy()
    else:
        series = pd.Series(values)

    true_values = {"true", "1", "yes", "y", "si"}
    false_values = {"false", "0", "no", "n"}

    def convert(value):  # type: ignore[no-untyped-def]
        if pd.isna(value):
            return np.nan
        if isinstance(value, (bool, np.bool_)):
            return bool(value)
        text = str(value).strip().lower()
        if text in true_values:
            return True
        if text in false_values:
            return False
        return np.nan

    return series.map(convert)


def _parse_compact_decimal(token: str) -> Optional[float]:
    cleaned = re.sub(r"[^0-9.]", "", token)
    if not cleaned:
        return None
    if "." in cleaned:
        return float(cleaned)
    scale = max(len(cleaned) - 1, 0)
    if scale == 0:
        return float(cleaned)
    return float(int(cleaned)) / (10 ** scale)


def _load_case_d_eq(case_dir: Path, default_d_eq_m: float) -> float:
    properties_path = case_dir / "boulder_properties.txt"
    if not properties_path.exists():
        return default_d_eq_m

    with properties_path.open("r", encoding="utf-8", errors="replace") as handle:
        for line in handle:
            if line.lower().startswith("d_eq_m"):
                _, value = line.split(":", 1)
                try:
                    return float(value.strip())
                except ValueError:
                    return default_d_eq_m
    return default_d_eq_m


def _resolve_case_out_dir(
    case_name_or_out_dir: PathLike,
    import_root: Optional[PathLike],
) -> Path:
    candidate = Path(case_name_or_out_dir)
    if candidate.exists():
        resolved = candidate.expanduser().resolve()
        if resolved.is_dir() and resolved.name.endswith("_out"):
            return resolved
        raise FileNotFoundError("Expected an existing *_out directory, got {}".format(resolved))
    return find_case_out_dir(str(case_name_or_out_dir), import_root=import_root)


def _find_single(root_dir: Path, pattern: str) -> Path:
    matches = sorted(root_dir.glob(pattern))
    if not matches:
        raise FileNotFoundError("No file matching {} in {}".format(pattern, root_dir))
    if len(matches) > 1:
        raise FileExistsError("Multiple files matching {} in {}".format(pattern, root_dir))
    return matches[0]


def _load_gauge_group(
    out_dir: Path,
    pattern: str,
    gauge_prefix: str,
    gauge_id: Optional[str],
    rename_map: Dict[str, str],
    value_columns: Iterable[str],
) -> Union[pd.DataFrame, Dict[str, pd.DataFrame]]:
    if gauge_id is not None:
        csv_path = out_dir / "{}{}.csv".format(gauge_prefix, gauge_id)
        if not csv_path.exists():
            raise FileNotFoundError("Gauge file not found: {}".format(csv_path))
        return _load_single_gauge(csv_path, rename_map, value_columns)

    gauge_frames: Dict[str, pd.DataFrame] = {}
    for csv_path in sorted(out_dir.glob(pattern)):
        gauge_key = csv_path.stem.replace(gauge_prefix, "", 1)
        gauge_frames[gauge_key] = _load_single_gauge(csv_path, rename_map, value_columns)
    if not gauge_frames:
        raise FileNotFoundError("No gauge files matching {} in {}".format(pattern, out_dir))
    return gauge_frames


def _load_single_gauge(
    csv_path: Path,
    rename_map: Dict[str, str],
    value_columns: Iterable[str],
) -> pd.DataFrame:
    df = _read_table(csv_path).rename(columns=rename_map)
    for value_column in value_columns:
        if value_column in df.columns:
            df.loc[is_gauge_sentinel(df[value_column]), value_column] = np.nan
    return df


__all__ = [
    "DEFAULT_D_EQ_M",
    "DEFAULT_IMPORT_ROOT",
    "GAUGE_SENTINEL",
    "GAUGE_SENTINEL_THRESHOLD",
    "WSPrelimPaths",
    "derive_campaign",
    "derive_case_family",
    "find_case_out_dir",
    "is_gauge_sentinel",
    "list_summary_csvs",
    "load_chrono_body_forces",
    "load_chrono_exchange",
    "load_gauges_maxz",
    "load_gauges_vel",
    "load_run",
    "load_run_csv",
    "load_summary_csv",
    "load_summary_master_df",
    "parse_dp_from_name",
    "parse_mu_from_name",
    "resolve_import_paths",
]
