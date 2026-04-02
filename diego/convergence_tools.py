from __future__ import annotations

import argparse
import json
import logging
import os
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Sequence, Tuple

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

SENTINEL_THRESHOLD = -3.0e38
EXCEL_MAX_ROWS = 1_048_576

LEGACY_DIEGO_BASE_DIR = Path(
    "C:/Users/diego/OneDrive/Escritorio/An\u00e1lisis de convergencia/Lime-Stone 2"
)
DEFAULT_METADATA_FILE = Path(__file__).resolve().with_name("default_limestone_metadata.csv")


@dataclass(frozen=True)
class CaseMetadata:
    case_id: str
    dp: Optional[float] = None
    material: str = "limestone"
    observations: str = ""


def resolve_base_dir(base_dir_arg: Optional[str]) -> Path:
    if base_dir_arg:
        return Path(base_dir_arg).expanduser().resolve()

    env_dir = os.environ.get("DIEGO_BASE_DIR")
    if env_dir:
        return Path(env_dir).expanduser().resolve()

    if LEGACY_DIEGO_BASE_DIR.exists():
        return LEGACY_DIEGO_BASE_DIR.resolve()

    return Path.cwd().resolve()


def ensure_dir(path: Path) -> Path:
    path.mkdir(parents=True, exist_ok=True)
    return path


def configure_logger(name: str, log_path: Path) -> logging.Logger:
    ensure_dir(log_path.parent)

    logger = logging.getLogger(f"{name}:{log_path}")
    logger.setLevel(logging.INFO)
    logger.propagate = False

    for handler in list(logger.handlers):
        logger.removeHandler(handler)

    formatter = logging.Formatter("%(asctime)s %(levelname)s: %(message)s")

    file_handler = logging.FileHandler(log_path, mode="w", encoding="utf-8")
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(logging.Formatter("%(levelname)s: %(message)s"))
    logger.addHandler(stream_handler)

    return logger


def normalize_case_id(case_id: object) -> str:
    return str(case_id).strip()


def make_material_token(metadata_map: Dict[str, CaseMetadata], fallback: str = "limestone") -> str:
    materials = [meta.material for meta in metadata_map.values() if meta.material]
    raw = materials[0] if materials else fallback
    token = re.sub(r"[^A-Za-z0-9]+", "_", str(raw).strip().title()).strip("_")
    return token or "Resultados"


def dominant_material_label(metadata_map: Dict[str, CaseMetadata], fallback: str = "limestone") -> str:
    materials = [meta.material for meta in metadata_map.values() if meta.material]
    return materials[0] if materials else fallback


def maybe_float(value: object) -> Optional[float]:
    if value is None:
        return None
    if isinstance(value, float) and np.isnan(value):
        return None

    text = str(value).strip()
    if not text:
        return None

    try:
        return float(text)
    except ValueError:
        return None


def discover_case_ids(base_dir: Path, requested_cases: Optional[Sequence[str]] = None) -> List[str]:
    if requested_cases:
        return [normalize_case_id(case_id) for case_id in requested_cases]

    discovered = []
    patterns = (
        "ChronoExchange_mkbound_*.csv",
        "GaugesVel_V*.csv",
        "GaugesMaxZ_hmax*.csv",
    )
    for child in sorted(base_dir.iterdir()):
        if not child.is_dir():
            continue
        if any(child.glob(pattern) for pattern in patterns):
            discovered.append(child.name)
    return discovered


def _metadata_records_from_dataframe(df: pd.DataFrame) -> Dict[str, CaseMetadata]:
    lower_map = {column.lower().strip(): column for column in df.columns}

    case_column = None
    for candidate in ("caso", "case_id", "case"):
        if candidate in lower_map:
            case_column = lower_map[candidate]
            break
    if case_column is None:
        raise ValueError("El archivo de metadatos debe incluir una columna 'caso' o 'case_id'.")

    dp_column = None
    for candidate in ("dp", "dp [m]", "dp_m"):
        if candidate in lower_map:
            dp_column = lower_map[candidate]
            break

    material_column = lower_map.get("material")

    obs_column = None
    for candidate in ("observaciones", "observation", "observations", "notes", "obs"):
        if candidate in lower_map:
            obs_column = lower_map[candidate]
            break

    metadata = {}
    for _, row in df.iterrows():
        case_id = normalize_case_id(row[case_column])
        if not case_id:
            continue
        metadata[case_id] = CaseMetadata(
            case_id=case_id,
            dp=maybe_float(row[dp_column]) if dp_column else None,
            material=str(row[material_column]).strip() if material_column and pd.notna(row[material_column]) else "limestone",
            observations=str(row[obs_column]).strip() if obs_column and pd.notna(row[obs_column]) else "",
        )
    return metadata


def load_case_metadata(
    case_ids: Sequence[str],
    metadata_file: Optional[str] = None,
    default_material: str = "limestone",
) -> Dict[str, CaseMetadata]:
    metadata_path = Path(metadata_file).expanduser().resolve() if metadata_file else None
    if metadata_path is None and DEFAULT_METADATA_FILE.exists():
        metadata_path = DEFAULT_METADATA_FILE

    metadata: Dict[str, CaseMetadata] = {}

    if metadata_path is not None and metadata_path.exists():
        if metadata_path.suffix.lower() == ".json":
            with open(metadata_path, "r", encoding="utf-8") as handle:
                raw = json.load(handle)
            if isinstance(raw, dict):
                raw = raw.get("cases", raw)
            if isinstance(raw, dict):
                rows = []
                for key, value in raw.items():
                    value = value or {}
                    rows.append(
                        {
                            "caso": key,
                            "dp": value.get("dp"),
                            "material": value.get("material"),
                            "observaciones": value.get("observaciones"),
                        }
                    )
                frame = pd.DataFrame(rows)
            else:
                frame = pd.DataFrame(raw)
        else:
            frame = pd.read_csv(metadata_path)
        metadata = _metadata_records_from_dataframe(frame)

    for case_id in case_ids:
        if case_id not in metadata:
            metadata[case_id] = CaseMetadata(case_id=case_id, material=default_material)

    return metadata


def build_metadata_frame(case_ids: Sequence[str], metadata_map: Dict[str, CaseMetadata]) -> pd.DataFrame:
    rows = []
    for case_id in case_ids:
        meta = metadata_map.get(case_id, CaseMetadata(case_id=case_id))
        rows.append(
            {
                "caso": case_id,
                "dp [m]": meta.dp,
                "material": meta.material,
                "observaciones": meta.observations,
            }
        )

    frame = pd.DataFrame(rows)
    if not frame.empty and "dp [m]" in frame.columns:
        frame = frame.sort_values(["dp [m]", "caso"], ascending=[False, True], na_position="last")
    return frame.reset_index(drop=True)


def extract_gauge_number(filename: str, pattern: str) -> int:
    match = re.search(pattern, filename, flags=re.IGNORECASE)
    if not match:
        raise ValueError(f"No se pudo extraer el gauge desde '{filename}'.")
    return int(match.group(1))


def read_velocity_csv(path_csv: Path, case_id: str) -> Tuple[pd.DataFrame, Dict[str, object]]:
    df = pd.read_csv(path_csv, sep=";", engine="python")
    df.columns = [column.strip() for column in df.columns]

    required = ["time [s]", "velx [m/s]", "vely [m/s]", "velz [m/s]"]
    missing = [column for column in required if column not in df.columns]
    if missing:
        raise ValueError(f"[{case_id}] Faltan columnas en {path_csv.name}: {missing}")

    out = df[required].copy().apply(pd.to_numeric, errors="coerce")
    sentinel_mask = out[["velx [m/s]", "vely [m/s]", "velz [m/s]"]] < SENTINEL_THRESHOLD
    sentinel_rows = int(sentinel_mask.any(axis=1).sum())

    for column in ["velx [m/s]", "vely [m/s]", "velz [m/s]"]:
        out.loc[out[column] < SENTINEL_THRESHOLD, column] = np.nan

    out = out.dropna(subset=["time [s]"]).reset_index(drop=True)
    if out.empty:
        raise ValueError(f"[{case_id}] Archivo vacio tras limpieza: {path_csv.name}")

    gauge = extract_gauge_number(path_csv.name, r"V(\d+)\.csv$")
    out["caso"] = case_id
    out["gauge"] = gauge
    out["archivo_origen"] = path_csv.name
    out["vel_horizontal [m/s]"] = np.sqrt(out["velx [m/s]"] ** 2 + out["vely [m/s]"] ** 2)
    out["vel_resultante [m/s]"] = np.sqrt(
        out["velx [m/s]"] ** 2 + out["vely [m/s]"] ** 2 + out["velz [m/s]"] ** 2
    )

    diagnostics = {
        "caso": case_id,
        "gauge": gauge,
        "archivo_origen": path_csv.name,
        "n_filas": len(out),
        "n_filas_con_sentinel": sentinel_rows,
        "n_filas_con_nan": int(out[["velx [m/s]", "vely [m/s]", "velz [m/s]"]].isna().any(axis=1).sum()),
    }

    return (
        out[
            [
                "caso",
                "gauge",
                "archivo_origen",
                "time [s]",
                "velx [m/s]",
                "vely [m/s]",
                "velz [m/s]",
                "vel_horizontal [m/s]",
                "vel_resultante [m/s]",
            ]
        ],
        diagnostics,
    )


def read_hmax_csv(path_csv: Path, case_id: str) -> Tuple[pd.DataFrame, Dict[str, object]]:
    df = pd.read_csv(path_csv, sep=";", engine="python")
    df.columns = [column.strip() for column in df.columns]

    required = ["time [s]", "zmax [m]"]
    missing = [column for column in required if column not in df.columns]
    if missing:
        raise ValueError(f"[{case_id}] Faltan columnas en {path_csv.name}: {missing}")

    out = df[required].copy().apply(pd.to_numeric, errors="coerce")
    sentinel_rows = int((out["zmax [m]"] < SENTINEL_THRESHOLD).sum())
    out.loc[out["zmax [m]"] < SENTINEL_THRESHOLD, "zmax [m]"] = np.nan
    out = out.dropna(subset=["time [s]"]).reset_index(drop=True)

    if out.empty:
        raise ValueError(f"[{case_id}] Archivo vacio tras limpieza: {path_csv.name}")

    gauge = extract_gauge_number(path_csv.name, r"hmax(\d+)\.csv$")
    out["caso"] = case_id
    out["gauge"] = gauge
    out["archivo_origen"] = path_csv.name

    diagnostics = {
        "caso": case_id,
        "gauge": gauge,
        "archivo_origen": path_csv.name,
        "n_filas": len(out),
        "n_filas_con_sentinel": sentinel_rows,
        "n_filas_con_nan": int(out["zmax [m]"].isna().sum()),
    }

    return out[["caso", "gauge", "archivo_origen", "time [s]", "zmax [m]"]], diagnostics


def read_exchange_csv(path_csv: Path, case_id: str) -> Tuple[pd.DataFrame, Dict[str, object]]:
    df = pd.read_csv(path_csv, sep=";", engine="python")
    df.columns = [column.strip() for column in df.columns]

    predictor_filtered = 0
    if "predictor" in df.columns:
        predictor_mask = df["predictor"].astype(str).str.strip().str.lower() == "true"
        predictor_filtered = int(predictor_mask.sum())
        df = df.loc[~predictor_mask].copy()

    required = [
        "time [s]",
        "fcenter.x [m]",
        "fcenter.y [m]",
        "fcenter.z [m]",
        "fvel.x [m/s]",
        "fvel.y [m/s]",
        "fvel.z [m/s]",
        "face.x [m/s^2]",
        "face.y [m/s^2]",
        "face.z [m/s^2]",
    ]
    missing = [column for column in required if column not in df.columns]
    if missing:
        raise ValueError(f"[{case_id}] Faltan columnas en Exchange: {missing}")

    out = df[required].copy().apply(pd.to_numeric, errors="coerce")
    out = out.dropna(subset=["time [s]"]).reset_index(drop=True)

    if out.empty:
        raise ValueError(f"[{case_id}] Exchange quedo vacio tras limpieza.")

    x0 = out.loc[0, "fcenter.x [m]"]
    y0 = out.loc[0, "fcenter.y [m]"]
    z0 = out.loc[0, "fcenter.z [m]"]

    out["caso"] = case_id
    out["dx [m]"] = out["fcenter.x [m]"] - x0
    out["dy [m]"] = out["fcenter.y [m]"] - y0
    out["dz [m]"] = out["fcenter.z [m]"] - z0
    out["dxy [m]"] = np.sqrt(out["dx [m]"] ** 2 + out["dy [m]"] ** 2)
    out["dxyz [m]"] = np.sqrt(out["dx [m]"] ** 2 + out["dy [m]"] ** 2 + out["dz [m]"] ** 2)
    out["vxy [m/s]"] = np.sqrt(out["fvel.x [m/s]"] ** 2 + out["fvel.y [m/s]"] ** 2)
    out["vxyz [m/s]"] = np.sqrt(
        out["fvel.x [m/s]"] ** 2 + out["fvel.y [m/s]"] ** 2 + out["fvel.z [m/s]"] ** 2
    )
    out["axy [m/s^2]"] = np.sqrt(out["face.x [m/s^2]"] ** 2 + out["face.y [m/s^2]"] ** 2)

    diagnostics = {
        "caso": case_id,
        "archivo_exchange": path_csv.name,
        "n_filas": len(out),
        "n_predictor_filtradas": predictor_filtered,
    }

    ordered_columns = [
        "caso",
        "time [s]",
        "fcenter.x [m]",
        "fcenter.y [m]",
        "fcenter.z [m]",
        "dx [m]",
        "dy [m]",
        "dz [m]",
        "dxy [m]",
        "dxyz [m]",
        "fvel.x [m/s]",
        "fvel.y [m/s]",
        "fvel.z [m/s]",
        "vxy [m/s]",
        "vxyz [m/s]",
        "face.x [m/s^2]",
        "face.y [m/s^2]",
        "face.z [m/s^2]",
        "axy [m/s^2]",
    ]
    return out[ordered_columns], diagnostics


def _normalize_force_columns(raw_columns: Sequence[str]) -> List[str]:
    clean_columns: List[str] = []
    current_body = ""

    for column in raw_columns:
        column = column.strip()
        if not column:
            continue
        if column.lower() == "time":
            clean_columns.append("time [s]")
            continue
        if column.startswith("Body_"):
            parts = column.split("_", 2)
            current_body = parts[1].lower()
            suffix = parts[2].lower() if len(parts) > 2 else "fx"
            clean_columns.append(f"{current_body}_{suffix}")
            continue
        if current_body:
            clean_columns.append(f"{current_body}_{column.lower()}")
        else:
            clean_columns.append(column.lower())

    return clean_columns


def _choose_force_body(clean_columns: Sequence[str], body_hint: str = "blir") -> str:
    bodies = sorted(
        {
            column.split("_", 1)[0]
            for column in clean_columns
            if "_" in column and column != "time [s]"
        }
    )
    if not bodies:
        raise ValueError("No se detectaron cuerpos en ChronoBody_forces.csv.")

    lowered_hint = body_hint.lower()
    for body in bodies:
        if body == lowered_hint or body.startswith(lowered_hint) or lowered_hint in body:
            return body
    return bodies[0]


def read_forces_csv(path_csv: Path, case_id: str, body_hint: str = "blir") -> Tuple[pd.DataFrame, Dict[str, object]]:
    with open(path_csv, "r", encoding="utf-8") as handle:
        header_line = handle.readline().strip().rstrip(";")

    raw_columns = [column for column in header_line.split(";") if column.strip()]
    clean_columns = _normalize_force_columns(raw_columns)

    df = pd.read_csv(path_csv, sep=";", header=0, usecols=range(len(clean_columns)))
    df.columns = clean_columns

    body_name = _choose_force_body(clean_columns, body_hint=body_hint)
    rename_map = {
        "time [s]": "time [s]",
        f"{body_name}_fx": "fx",
        f"{body_name}_fy": "fy",
        f"{body_name}_fz": "fz",
        f"{body_name}_mx": "mx",
        f"{body_name}_my": "my",
        f"{body_name}_mz": "mz",
        f"{body_name}_cfx": "cfx",
        f"{body_name}_cfy": "cfy",
        f"{body_name}_cfz": "cfz",
        f"{body_name}_cmx": "cmx",
        f"{body_name}_cmy": "cmy",
        f"{body_name}_cmz": "cmz",
    }
    missing = [column for column in rename_map if column not in df.columns]
    if missing:
        raise ValueError(f"[{case_id}] Fuerzas sin columnas esperadas para body '{body_name}': {missing}")

    out = df[list(rename_map.keys())].rename(columns=rename_map).copy()
    out = out.apply(pd.to_numeric, errors="coerce")
    out = out.dropna(subset=["time [s]"]).reset_index(drop=True)

    if out.empty:
        raise ValueError(f"[{case_id}] Forces quedo vacio tras limpieza.")

    out["caso"] = case_id
    out["body"] = body_name
    out["fxy"] = np.sqrt(out["fx"] ** 2 + out["fy"] ** 2)
    out["fxyz"] = np.sqrt(out["fx"] ** 2 + out["fy"] ** 2 + out["fz"] ** 2)

    diagnostics = {
        "caso": case_id,
        "archivo_forces": path_csv.name,
        "body": body_name,
        "n_filas": len(out),
    }

    ordered_columns = [
        "caso",
        "body",
        "time [s]",
        "fx",
        "fy",
        "fz",
        "mx",
        "my",
        "mz",
        "cfx",
        "cfy",
        "cfz",
        "cmx",
        "cmy",
        "cmz",
        "fxy",
        "fxyz",
    ]
    return out[ordered_columns], diagnostics


def case_label(case_id: str, metadata_map: Dict[str, CaseMetadata]) -> str:
    meta = metadata_map.get(case_id)
    if meta and meta.dp is not None:
        return f"Caso {case_id} (dp={meta.dp:.4f} m)"
    return f"Caso {case_id}"


def case_order(case_ids: Iterable[str], metadata_map: Dict[str, CaseMetadata]) -> List[str]:
    def sort_key(case_id: str) -> Tuple[float, str]:
        meta = metadata_map.get(case_id, CaseMetadata(case_id=case_id))
        dp_sort = meta.dp if meta.dp is not None else -np.inf
        return (dp_sort, case_id)

    return [case_id for case_id in sorted(set(case_ids), key=sort_key, reverse=True)]


def calculate_relative_error(df: pd.DataFrame, value_column: str) -> pd.DataFrame:
    out = df.copy().reset_index(drop=True)
    errors = [np.nan]

    for index in range(1, len(out)):
        previous = out.loc[index - 1, value_column]
        current = out.loc[index, value_column]
        if pd.isna(previous) or pd.isna(current) or abs(previous) < 1e-12:
            errors.append(np.nan)
        else:
            errors.append(abs(current - previous) / abs(previous) * 100.0)

    out[f"error_rel_{value_column} [%]"] = errors
    return out


def summarize_pangea_velocity_case(df_velocity: pd.DataFrame, case_id: str, metadata_map: Dict[str, CaseMetadata]) -> Dict[str, object]:
    meta = metadata_map.get(case_id, CaseMetadata(case_id=case_id))
    grouped = df_velocity.groupby("gauge", as_index=False).agg(
        {
            "velx [m/s]": lambda series: series.abs().max(),
            "vely [m/s]": lambda series: series.abs().max(),
            "velz [m/s]": lambda series: series.abs().max(),
            "vel_horizontal [m/s]": "max",
            "vel_resultante [m/s]": "max",
        }
    )

    return {
        "caso": case_id,
        "dp [m]": meta.dp,
        "material": meta.material,
        "n_gauges_vel": int(df_velocity["gauge"].nunique()),
        "velx_max_abs_global [m/s]": grouped["velx [m/s]"].max(),
        "vely_max_abs_global [m/s]": grouped["vely [m/s]"].max(),
        "velz_max_abs_global [m/s]": grouped["velz [m/s]"].max(),
        "vel_horizontal_max_global [m/s]": grouped["vel_horizontal [m/s]"].max(),
        "vel_resultante_max_global [m/s]": grouped["vel_resultante [m/s]"].max(),
        "promedio_max_vel_horizontal [m/s]": grouped["vel_horizontal [m/s]"].mean(),
        "promedio_max_vel_resultante [m/s]": grouped["vel_resultante [m/s]"].mean(),
    }


def summarize_pangea_hmax_case(df_hmax: pd.DataFrame, case_id: str, metadata_map: Dict[str, CaseMetadata]) -> Dict[str, object]:
    meta = metadata_map.get(case_id, CaseMetadata(case_id=case_id))
    grouped = df_hmax.groupby("gauge", as_index=False).agg({"zmax [m]": "max"})
    return {
        "caso": case_id,
        "dp [m]": meta.dp,
        "material": meta.material,
        "n_gauges_hmax": int(df_hmax["gauge"].nunique()),
        "zmax_max_global [m]": grouped["zmax [m]"].max(),
        "promedio_max_zmax [m]": grouped["zmax [m]"].mean(),
    }


def summarize_pangea_velocity_gauge(df_velocity: pd.DataFrame, case_id: str, metadata_map: Dict[str, CaseMetadata]) -> pd.DataFrame:
    meta = metadata_map.get(case_id, CaseMetadata(case_id=case_id))
    summary = df_velocity.groupby("gauge", as_index=False).agg(
        {
            "velx [m/s]": lambda series: series.abs().max(),
            "vely [m/s]": lambda series: series.abs().max(),
            "velz [m/s]": lambda series: series.abs().max(),
            "vel_horizontal [m/s]": "max",
            "vel_resultante [m/s]": "max",
        }
    )
    summary["caso"] = case_id
    summary["dp [m]"] = meta.dp
    summary["material"] = meta.material
    summary = summary.rename(
        columns={
            "velx [m/s]": "velx_max_abs [m/s]",
            "vely [m/s]": "vely_max_abs [m/s]",
            "velz [m/s]": "velz_max_abs [m/s]",
            "vel_horizontal [m/s]": "vel_horizontal_max [m/s]",
            "vel_resultante [m/s]": "vel_resultante_max [m/s]",
        }
    )
    return summary[
        [
            "caso",
            "dp [m]",
            "material",
            "gauge",
            "velx_max_abs [m/s]",
            "vely_max_abs [m/s]",
            "velz_max_abs [m/s]",
            "vel_horizontal_max [m/s]",
            "vel_resultante_max [m/s]",
        ]
    ]


def summarize_pangea_hmax_gauge(df_hmax: pd.DataFrame, case_id: str, metadata_map: Dict[str, CaseMetadata]) -> pd.DataFrame:
    meta = metadata_map.get(case_id, CaseMetadata(case_id=case_id))
    summary = df_hmax.groupby("gauge", as_index=False).agg({"zmax [m]": "max"})
    summary["caso"] = case_id
    summary["dp [m]"] = meta.dp
    summary["material"] = meta.material
    summary = summary.rename(columns={"zmax [m]": "zmax_max [m]"})
    return summary[["caso", "dp [m]", "material", "gauge", "zmax_max [m]"]]


def assemble_pangea(base_dir: Path, case_ids: Sequence[str], metadata_map: Dict[str, CaseMetadata], logger: logging.Logger) -> Dict[str, pd.DataFrame]:
    velocity_frames = []
    hmax_frames = []
    velocity_case_summaries = []
    hmax_case_summaries = []
    velocity_gauge_summaries = []
    hmax_gauge_summaries = []
    control_rows = []
    velocity_diagnostics = []
    hmax_diagnostics = []

    for case_id in case_ids:
        case_dir = base_dir / case_id
        meta = metadata_map.get(case_id, CaseMetadata(case_id=case_id))
        velocity_files = []
        hmax_files = []

        try:
            if not case_dir.exists():
                raise FileNotFoundError(f"No existe la carpeta {case_dir}")

            velocity_files = sorted(case_dir.glob("GaugesVel_V*.csv"))
            hmax_files = sorted(case_dir.glob("GaugesMaxZ_hmax*.csv"))
            logger.info("%s: Vel=%s, Hmax=%s", case_id, len(velocity_files), len(hmax_files))

            current_velocity_frames = []
            for velocity_path in velocity_files:
                frame, diagnostics = read_velocity_csv(velocity_path, case_id)
                current_velocity_frames.append(frame)
                velocity_diagnostics.append(diagnostics)

            current_hmax_frames = []
            for hmax_path in hmax_files:
                frame, diagnostics = read_hmax_csv(hmax_path, case_id)
                current_hmax_frames.append(frame)
                hmax_diagnostics.append(diagnostics)

            velocity_case = pd.concat(current_velocity_frames, ignore_index=True) if current_velocity_frames else pd.DataFrame()
            hmax_case = pd.concat(current_hmax_frames, ignore_index=True) if current_hmax_frames else pd.DataFrame()

            if not velocity_case.empty:
                velocity_frames.append(velocity_case)
                velocity_case_summaries.append(summarize_pangea_velocity_case(velocity_case, case_id, metadata_map))
                velocity_gauge_summaries.append(summarize_pangea_velocity_gauge(velocity_case, case_id, metadata_map))

            if not hmax_case.empty:
                hmax_frames.append(hmax_case)
                hmax_case_summaries.append(summarize_pangea_hmax_case(hmax_case, case_id, metadata_map))
                hmax_gauge_summaries.append(summarize_pangea_hmax_gauge(hmax_case, case_id, metadata_map))

            state = "OK"
            if len(velocity_files) != 12 or len(hmax_files) != 8:
                state = "OK (REVISAR CANTIDAD)"

            velocity_case_diag = [row for row in velocity_diagnostics if row["caso"] == case_id]
            hmax_case_diag = [row for row in hmax_diagnostics if row["caso"] == case_id]

            control_rows.append(
                {
                    "caso": case_id,
                    "dp [m]": meta.dp,
                    "n_archivos_vel": len(velocity_files),
                    "n_archivos_hmax": len(hmax_files),
                    "n_filas_vel": int(sum(row["n_filas"] for row in velocity_case_diag)),
                    "n_filas_hmax": int(sum(row["n_filas"] for row in hmax_case_diag)),
                    "n_filas_vel_con_sentinel": int(sum(row["n_filas_con_sentinel"] for row in velocity_case_diag)),
                    "n_filas_hmax_con_sentinel": int(sum(row["n_filas_con_sentinel"] for row in hmax_case_diag)),
                    "estado": state,
                    "observaciones": meta.observations,
                }
            )
        except Exception as exc:
            logger.exception("Error procesando Pangea para %s", case_id)
            control_rows.append(
                {
                    "caso": case_id,
                    "dp [m]": meta.dp,
                    "n_archivos_vel": len(velocity_files),
                    "n_archivos_hmax": len(hmax_files),
                    "n_filas_vel": 0,
                    "n_filas_hmax": 0,
                    "n_filas_vel_con_sentinel": 0,
                    "n_filas_hmax_con_sentinel": 0,
                    "estado": f"ERROR: {exc}",
                    "observaciones": meta.observations,
                }
            )

    df_metadata = build_metadata_frame(case_ids, metadata_map)
    df_control = pd.DataFrame(control_rows)
    df_velocity = pd.concat(velocity_frames, ignore_index=True) if velocity_frames else pd.DataFrame()
    df_hmax = pd.concat(hmax_frames, ignore_index=True) if hmax_frames else pd.DataFrame()
    df_velocity_case = pd.DataFrame(velocity_case_summaries)
    df_hmax_case = pd.DataFrame(hmax_case_summaries)
    df_velocity_gauge = pd.concat(velocity_gauge_summaries, ignore_index=True) if velocity_gauge_summaries else pd.DataFrame()
    df_hmax_gauge = pd.concat(hmax_gauge_summaries, ignore_index=True) if hmax_gauge_summaries else pd.DataFrame()
    df_velocity_diag = pd.DataFrame(velocity_diagnostics)
    df_hmax_diag = pd.DataFrame(hmax_diagnostics)

    if not df_velocity_case.empty and not df_hmax_case.empty:
        df_global = pd.merge(
            df_velocity_case,
            df_hmax_case,
            on=["caso", "dp [m]", "material"],
            how="outer",
        )
    elif not df_velocity_case.empty:
        df_global = df_velocity_case.copy()
    else:
        df_global = df_hmax_case.copy()

    return {
        "Metadatos": df_metadata,
        "Control_archivos": df_control,
        "Control_vel_gauges": df_velocity_diag,
        "Control_hmax_gauges": df_hmax_diag,
        "Velocidades_completo": df_velocity,
        "Hmax_completo": df_hmax,
        "Resumen_vel_global": df_velocity_case,
        "Resumen_hmax_global": df_hmax_case,
        "Resumen_vel_por_gauge": df_velocity_gauge,
        "Resumen_hmax_por_gauge": df_hmax_gauge,
        "Resumen_global": df_global,
    }


def summarize_columbia_case(
    df_exchange: pd.DataFrame,
    df_forces: Optional[pd.DataFrame],
    case_id: str,
    metadata_map: Dict[str, CaseMetadata],
) -> Dict[str, object]:
    meta = metadata_map.get(case_id, CaseMetadata(case_id=case_id))
    summary = {
        "caso": case_id,
        "dp [m]": meta.dp,
        "material": meta.material,
        "observaciones": meta.observations,
        "tiempo_final [s]": df_exchange["time [s]"].iloc[-1],
        "x_final [m]": df_exchange["fcenter.x [m]"].iloc[-1],
        "y_final [m]": df_exchange["fcenter.y [m]"].iloc[-1],
        "z_final [m]": df_exchange["fcenter.z [m]"].iloc[-1],
        "dx_final [m]": df_exchange["dx [m]"].iloc[-1],
        "dy_final [m]": df_exchange["dy [m]"].iloc[-1],
        "dz_final [m]": df_exchange["dz [m]"].iloc[-1],
        "dxy_final [m]": df_exchange["dxy [m]"].iloc[-1],
        "dxyz_final [m]": df_exchange["dxyz [m]"].iloc[-1],
        "vxy_max [m/s]": df_exchange["vxy [m/s]"].max(),
        "vxyz_max [m/s]": df_exchange["vxyz [m/s]"].max(),
        "az_max_abs [m/s^2]": df_exchange["face.z [m/s^2]"].abs().max(),
    }

    if df_forces is not None and not df_forces.empty:
        summary["body_forces"] = df_forces["body"].iloc[0]
        summary["fx_max_abs"] = df_forces["fx"].abs().max()
        summary["fy_max_abs"] = df_forces["fy"].abs().max()
        summary["fz_max_abs"] = df_forces["fz"].abs().max()
        summary["fxy_max"] = df_forces["fxy"].max()
        summary["fxyz_max"] = df_forces["fxyz"].max()
    else:
        summary["body_forces"] = None
        summary["fx_max_abs"] = None
        summary["fy_max_abs"] = None
        summary["fz_max_abs"] = None
        summary["fxy_max"] = None
        summary["fxyz_max"] = None

    return summary


def assemble_columbia(
    base_dir: Path,
    case_ids: Sequence[str],
    metadata_map: Dict[str, CaseMetadata],
    logger: logging.Logger,
    body_hint: str = "blir",
) -> Dict[str, pd.DataFrame]:
    exchange_frames = []
    force_frames = []
    summaries = []
    control_rows = []

    for case_id in case_ids:
        case_dir = base_dir / case_id
        meta = metadata_map.get(case_id, CaseMetadata(case_id=case_id))

        if not case_dir.exists():
            control_rows.append(
                {
                    "caso": case_id,
                    "dp [m]": meta.dp,
                    "archivo_exchange": None,
                    "archivo_forces": None,
                    "n_datos_exchange": 0,
                    "n_datos_forces": 0,
                    "n_predictor_filtradas": 0,
                    "body_forces": None,
                    "estado": "CARPETA NO EXISTE",
                    "observaciones": meta.observations,
                }
            )
            logger.warning("No existe carpeta para el caso %s", case_id)
            continue

        exchange_candidates = sorted(case_dir.glob("ChronoExchange_mkbound_*.csv"))
        force_path = case_dir / "ChronoBody_forces.csv"
        exchange_path = exchange_candidates[0] if exchange_candidates else None

        if exchange_path is None:
            control_rows.append(
                {
                    "caso": case_id,
                    "dp [m]": meta.dp,
                    "archivo_exchange": None,
                    "archivo_forces": str(force_path) if force_path.exists() else None,
                    "n_datos_exchange": 0,
                    "n_datos_forces": 0,
                    "n_predictor_filtradas": 0,
                    "body_forces": None,
                    "estado": "SIN CHRONOEXCHANGE",
                    "observaciones": meta.observations,
                }
            )
            logger.warning("Caso %s sin ChronoExchange_mkbound_*.csv", case_id)
            continue

        try:
            exchange_frame, exchange_diag = read_exchange_csv(exchange_path, case_id)
            exchange_frames.append(exchange_frame)

            force_frame = None
            force_diag = {"body": None, "n_filas": 0}
            if force_path.exists():
                force_frame, force_diag = read_forces_csv(force_path, case_id, body_hint=body_hint)
                force_frames.append(force_frame)

            summaries.append(summarize_columbia_case(exchange_frame, force_frame, case_id, metadata_map))
            control_rows.append(
                {
                    "caso": case_id,
                    "dp [m]": meta.dp,
                    "archivo_exchange": str(exchange_path),
                    "archivo_forces": str(force_path) if force_path.exists() else None,
                    "n_datos_exchange": len(exchange_frame),
                    "n_datos_forces": force_diag["n_filas"],
                    "n_predictor_filtradas": exchange_diag["n_predictor_filtradas"],
                    "body_forces": force_diag["body"],
                    "estado": "OK",
                    "observaciones": meta.observations,
                }
            )
            logger.info("Caso %s procesado en Columbia", case_id)
        except Exception as exc:
            logger.exception("Error procesando Columbia para %s", case_id)
            control_rows.append(
                {
                    "caso": case_id,
                    "dp [m]": meta.dp,
                    "archivo_exchange": str(exchange_path),
                    "archivo_forces": str(force_path) if force_path.exists() else None,
                    "n_datos_exchange": 0,
                    "n_datos_forces": 0,
                    "n_predictor_filtradas": 0,
                    "body_forces": None,
                    "estado": f"ERROR: {exc}",
                    "observaciones": meta.observations,
                }
            )

    if not exchange_frames:
        raise ValueError("No se pudo procesar ningun caso correctamente para Columbia.")

    df_metadata = build_metadata_frame(case_ids, metadata_map)
    df_control = pd.DataFrame(control_rows)
    df_exchange = pd.concat(exchange_frames, ignore_index=True)
    df_forces = pd.concat(force_frames, ignore_index=True) if force_frames else pd.DataFrame()
    df_summary = pd.DataFrame(summaries)

    df_trajectory = df_exchange[
        [
            "caso",
            "time [s]",
            "fcenter.x [m]",
            "fcenter.y [m]",
            "fcenter.z [m]",
            "dx [m]",
            "dy [m]",
            "dz [m]",
            "dxy [m]",
            "dxyz [m]",
        ]
    ].copy()
    df_velocity = df_exchange[
        [
            "caso",
            "time [s]",
            "fvel.x [m/s]",
            "fvel.y [m/s]",
            "fvel.z [m/s]",
            "vxy [m/s]",
            "vxyz [m/s]",
        ]
    ].copy()

    return {
        "Metadatos": df_metadata,
        "Control_archivos": df_control,
        "Resumen": df_summary,
        "Trayectoria": df_trajectory,
        "Velocidad": df_velocity,
        "Exchange_completo": df_exchange,
        "Fuerzas": df_forces,
    }


def build_columbia_error_table(df_summary: pd.DataFrame) -> pd.DataFrame:
    if df_summary.empty:
        return pd.DataFrame()

    ordered = df_summary.copy()
    if "dp [m]" in ordered.columns:
        ordered = ordered.sort_values("dp [m]", ascending=False, na_position="last")

    error_table = ordered[["caso", "dp [m]"]].copy()
    for column in ("dxy_final [m]", "vxy_max [m/s]", "fxyz_max"):
        if column in ordered.columns:
            with_error = calculate_relative_error(ordered[["caso", "dp [m]", column]], column)
            error_table[column] = with_error[column]
            error_table[f"error_rel_{column} [%]"] = with_error[f"error_rel_{column} [%]"]
    return error_table


def save_figure(fig: plt.Figure, output_path: Path, dpi: int) -> None:
    ensure_dir(output_path.parent)
    fig.tight_layout()
    fig.savefig(output_path, dpi=dpi, bbox_inches="tight")
    plt.close(fig)


def plot_convergence_series(
    df: pd.DataFrame,
    x_column: str,
    y_column: str,
    title: str,
    y_label: str,
    output_path: Path,
    dpi: int,
    annotate_column: str = "caso",
) -> None:
    subset = df.dropna(subset=[x_column, y_column]).sort_values(x_column, ascending=False)
    if subset.empty:
        return

    fig, ax = plt.subplots(figsize=(8, 5))
    ax.plot(subset[x_column], subset[y_column], marker="o", linewidth=1.8)
    ax.set_title(title)
    ax.set_xlabel(x_column)
    ax.set_ylabel(y_label)
    ax.grid(True, alpha=0.35)

    for _, row in subset.iterrows():
        ax.annotate(str(row[annotate_column]), (row[x_column], row[y_column]), fontsize=8)

    save_figure(fig, output_path, dpi=dpi)

    with_error = calculate_relative_error(subset[[annotate_column, x_column, y_column]], y_column)
    error_column = f"error_rel_{y_column} [%]"

    fig, ax = plt.subplots(figsize=(8, 5))
    ax.plot(with_error[x_column], with_error[error_column], marker="o", linewidth=1.8)
    ax.set_title(f"Error relativo - {title}")
    ax.set_xlabel(x_column)
    ax.set_ylabel("Error relativo [%]")
    ax.grid(True, alpha=0.35)

    for _, row in with_error.iterrows():
        if pd.notna(row[error_column]):
            ax.annotate(str(row[annotate_column]), (row[x_column], row[error_column]), fontsize=8)

    save_figure(fig, output_path.with_name(output_path.stem + "_error.png"), dpi=dpi)


def plot_pangea(
    tables: Dict[str, pd.DataFrame],
    metadata_map: Dict[str, CaseMetadata],
    output_dir: Path,
    dpi: int,
    logger: logging.Logger,
) -> None:
    velocity = tables["Velocidades_completo"]
    hmax = tables["Hmax_completo"]
    velocity_gauge = tables["Resumen_vel_por_gauge"]
    hmax_gauge = tables["Resumen_hmax_por_gauge"]
    velocity_global = tables["Resumen_vel_global"]
    hmax_global = tables["Resumen_hmax_global"]
    control = tables["Control_archivos"]

    time_velocity_dir = ensure_dir(output_dir / "01_velocidades_tiempo")
    velocity_conv_dir = ensure_dir(output_dir / "02_velocidades_convergencia")
    time_hmax_dir = ensure_dir(output_dir / "03_hmax_tiempo")
    hmax_conv_dir = ensure_dir(output_dir / "04_hmax_convergencia")
    summary_dir = ensure_dir(output_dir / "05_resumenes_csv")

    ordered_cases = case_order(velocity["caso"].tolist() if not velocity.empty else hmax["caso"].tolist(), metadata_map)

    if not velocity.empty:
        gauges = sorted(velocity["gauge"].dropna().unique())
        for gauge in gauges:
            subset = velocity[velocity["gauge"] == gauge].copy()
            if subset.empty:
                continue
            for variable, title, ylabel, folder_name in (
                ("vel_horizontal [m/s]", "Velocidad horizontal vs tiempo", "Velocidad horizontal [m/s]", "vel_horizontal_tiempo"),
                ("vel_resultante [m/s]", "Velocidad resultante vs tiempo", "Velocidad resultante [m/s]", "vel_resultante_tiempo"),
            ):
                figure_dir = ensure_dir(time_velocity_dir / folder_name)
                fig, ax = plt.subplots(figsize=(10, 6))
                for case_id in ordered_cases:
                    current = subset[subset["caso"] == case_id].sort_values("time [s]")
                    if current.empty:
                        continue
                    ax.plot(current["time [s]"], current[variable], linewidth=1.6, label=case_label(case_id, metadata_map))

                ax.set_title(f"{title} - Gauge {int(gauge):02d}")
                ax.set_xlabel("Tiempo [s]")
                ax.set_ylabel(ylabel)
                ax.grid(True, alpha=0.35)
                ax.legend(fontsize=8, loc="best")
                save_figure(fig, figure_dir / f"Gauge_{int(gauge):02d}_{folder_name}.png", dpi=dpi)

    if not velocity_gauge.empty:
        for gauge in sorted(velocity_gauge["gauge"].dropna().unique()):
            subset = velocity_gauge[velocity_gauge["gauge"] == gauge].copy()
            if subset.empty:
                continue
            for column, title, ylabel, folder_name, filename in (
                ("vel_horizontal_max [m/s]", "Velocidad horizontal maxima vs dp", "Velocidad horizontal maxima [m/s]", "vel_horizontal_por_gauge", "vel_horizontal_max_vs_dp.png"),
                ("vel_resultante_max [m/s]", "Velocidad resultante maxima vs dp", "Velocidad resultante maxima [m/s]", "vel_resultante_por_gauge", "vel_resultante_max_vs_dp.png"),
            ):
                plot_convergence_series(
                    subset,
                    "dp [m]",
                    column,
                    f"{title} - Gauge {int(gauge):02d}",
                    ylabel,
                    velocity_conv_dir / folder_name / f"Gauge_{int(gauge):02d}_{filename}",
                    dpi=dpi,
                )

    if not velocity_global.empty:
        for column, title, ylabel, filename in (
            ("vel_horizontal_max_global [m/s]", "Maximo global de velocidad horizontal", "Velocidad [m/s]", "vel_horizontal_max_global.png"),
            ("promedio_max_vel_horizontal [m/s]", "Promedio de maximos de velocidad horizontal", "Velocidad [m/s]", "promedio_max_vel_horizontal.png"),
            ("vel_resultante_max_global [m/s]", "Maximo global de velocidad resultante", "Velocidad [m/s]", "vel_resultante_max_global.png"),
            ("promedio_max_vel_resultante [m/s]", "Promedio de maximos de velocidad resultante", "Velocidad [m/s]", "promedio_max_vel_resultante.png"),
        ):
            if column in velocity_global.columns:
                plot_convergence_series(
                    velocity_global,
                    "dp [m]",
                    column,
                    title,
                    ylabel,
                    velocity_conv_dir / "global" / filename,
                    dpi=dpi,
                )

    if not hmax.empty:
        for gauge in sorted(hmax["gauge"].dropna().unique()):
            subset = hmax[hmax["gauge"] == gauge].copy()
            if subset.empty:
                continue

            fig, ax = plt.subplots(figsize=(10, 6))
            for case_id in ordered_cases:
                current = subset[subset["caso"] == case_id].sort_values("time [s]")
                if current.empty:
                    continue
                ax.plot(current["time [s]"], current["zmax [m]"], linewidth=1.6, label=case_label(case_id, metadata_map))

            ax.set_title(f"Hmax vs tiempo - Gauge {int(gauge):02d}")
            ax.set_xlabel("Tiempo [s]")
            ax.set_ylabel("zmax [m]")
            ax.grid(True, alpha=0.35)
            ax.legend(fontsize=8, loc="best")
            save_figure(fig, time_hmax_dir / f"Gauge_{int(gauge):02d}_zmax_vs_tiempo.png", dpi=dpi)

    if not hmax_gauge.empty:
        for gauge in sorted(hmax_gauge["gauge"].dropna().unique()):
            subset = hmax_gauge[hmax_gauge["gauge"] == gauge].copy()
            if subset.empty:
                continue
            plot_convergence_series(
                subset,
                "dp [m]",
                "zmax_max [m]",
                f"Hmax maxima vs dp - Gauge {int(gauge):02d}",
                "zmax maxima [m]",
                hmax_conv_dir / "por_gauge" / f"Gauge_{int(gauge):02d}_zmax_max_vs_dp.png",
                dpi=dpi,
            )

    if not hmax_global.empty:
        for column, title, ylabel, filename in (
            ("zmax_max_global [m]", "Hmax maxima global", "zmax [m]", "zmax_max_global.png"),
            ("promedio_max_zmax [m]", "Promedio de maximos de Hmax", "zmax [m]", "promedio_max_zmax.png"),
        ):
            if column in hmax_global.columns:
                plot_convergence_series(
                    hmax_global,
                    "dp [m]",
                    column,
                    title,
                    ylabel,
                    hmax_conv_dir / "global" / filename,
                    dpi=dpi,
                )

    control.to_csv(summary_dir / "control_archivos.csv", index=False, encoding="utf-8-sig")
    tables["Control_vel_gauges"].to_csv(summary_dir / "control_vel_gauges.csv", index=False, encoding="utf-8-sig")
    tables["Control_hmax_gauges"].to_csv(summary_dir / "control_hmax_gauges.csv", index=False, encoding="utf-8-sig")
    velocity_gauge.to_csv(summary_dir / "resumen_vel_por_gauge.csv", index=False, encoding="utf-8-sig")
    hmax_gauge.to_csv(summary_dir / "resumen_hmax_por_gauge.csv", index=False, encoding="utf-8-sig")
    velocity_global.to_csv(summary_dir / "resumen_vel_global.csv", index=False, encoding="utf-8-sig")
    hmax_global.to_csv(summary_dir / "resumen_hmax_global.csv", index=False, encoding="utf-8-sig")

    logger.info("Graficos Pangea generados en %s", output_dir)


def read_columbia_workbook(excel_path: Path) -> Dict[str, pd.DataFrame]:
    if not excel_path.exists():
        raise FileNotFoundError(f"No existe el archivo: {excel_path}")

    workbook = pd.ExcelFile(excel_path)
    tables = {
        "Metadatos": pd.read_excel(excel_path, sheet_name="Metadatos"),
        "Resumen": pd.read_excel(excel_path, sheet_name="Resumen"),
        "Trayectoria": pd.read_excel(excel_path, sheet_name="Trayectoria"),
        "Velocidad": pd.read_excel(excel_path, sheet_name="Velocidad"),
    }

    if "Fuerzas" in workbook.sheet_names:
        tables["Fuerzas"] = pd.read_excel(excel_path, sheet_name="Fuerzas")
    else:
        tables["Fuerzas"] = pd.DataFrame()

    for name, frame in tables.items():
        if not frame.empty and "caso" in frame.columns:
            tables[name]["caso"] = tables[name]["caso"].astype(str).str.strip()

    return tables


def plot_columbia(
    tables: Dict[str, pd.DataFrame],
    metadata_map: Dict[str, CaseMetadata],
    output_dir: Path,
    dpi: int,
    save_individual: bool,
    logger: logging.Logger,
) -> None:
    metadata_frame = tables["Metadatos"].copy()
    if not metadata_frame.empty and "caso" in metadata_frame.columns:
        metadata_frame["caso"] = metadata_frame["caso"].astype(str).str.strip()

    summary = tables["Resumen"].copy()
    trajectory = tables["Trayectoria"].copy()
    velocity = tables["Velocidad"].copy()
    forces = tables["Fuerzas"].copy()

    ordered_cases = case_order(metadata_frame["caso"].tolist(), metadata_map)

    dxy_dir = ensure_dir(output_dir / "01_dxy_vs_tiempo")
    vxy_dir = ensure_dir(output_dir / "02_vxy_vs_tiempo")
    force_dir = ensure_dir(output_dir / "03_fuerzas_vs_tiempo")
    summary_dir = ensure_dir(output_dir / "04_resumen_convergencia")
    individual_dir = ensure_dir(output_dir / "05_individuales_por_caso")

    fig, ax = plt.subplots(figsize=(10, 6))
    for case_id in ordered_cases:
        subset = trajectory[trajectory["caso"] == case_id].sort_values("time [s]")
        if subset.empty:
            continue
        ax.plot(subset["time [s]"], subset["dxy [m]"], linewidth=1.8, label=case_label(case_id, metadata_map))
    ax.set_title("Desplazamiento horizontal resultante")
    ax.set_xlabel("Tiempo [s]")
    ax.set_ylabel("Desplazamiento [m]")
    ax.grid(True, alpha=0.35)
    ax.legend(fontsize=8, loc="best")
    save_figure(fig, dxy_dir / "dxy_vs_tiempo_todos_los_casos.png", dpi=dpi)

    fig, ax = plt.subplots(figsize=(10, 6))
    for case_id in ordered_cases:
        subset = velocity[velocity["caso"] == case_id].sort_values("time [s]")
        if subset.empty:
            continue
        ax.plot(subset["time [s]"], subset["vxy [m/s]"], linewidth=1.8, label=case_label(case_id, metadata_map))
    ax.set_title("Velocidad horizontal resultante")
    ax.set_xlabel("Tiempo [s]")
    ax.set_ylabel("Velocidad [m/s]")
    ax.grid(True, alpha=0.35)
    ax.legend(fontsize=8, loc="best")
    save_figure(fig, vxy_dir / "vxy_vs_tiempo_todos_los_casos.png", dpi=dpi)

    if not forces.empty:
        for column, title in (
            ("fx", "Fuerza en X"),
            ("fy", "Fuerza en Y"),
            ("fz", "Fuerza en Z"),
            ("fxy", "Fuerza horizontal resultante"),
            ("fxyz", "Fuerza resultante total"),
        ):
            if column not in forces.columns:
                continue
            fig, ax = plt.subplots(figsize=(10, 6))
            for case_id in ordered_cases:
                subset = forces[forces["caso"] == case_id].sort_values("time [s]")
                if subset.empty:
                    continue
                ax.plot(subset["time [s]"], subset[column], linewidth=1.5, label=case_label(case_id, metadata_map))
            ax.set_title(title)
            ax.set_xlabel("Tiempo [s]")
            ax.set_ylabel(column)
            ax.grid(True, alpha=0.35)
            ax.legend(fontsize=8, loc="best")
            save_figure(fig, force_dir / f"{column}_vs_tiempo_todos_los_casos.png", dpi=dpi)

    if not summary.empty:
        for column, title, ylabel, filename in (
            ("dxy_final [m]", "Desplazamiento final vs dp", "Desplazamiento final [m]", "desplazamiento_final_vs_dp.png"),
            ("vxy_max [m/s]", "Velocidad maxima vs dp", "Velocidad maxima [m/s]", "velocidad_maxima_vs_dp.png"),
            ("fxyz_max", "Fuerza maxima resultante vs dp", "Fuerza maxima resultante", "fuerza_maxima_resultante_vs_dp.png"),
        ):
            if column in summary.columns:
                plot_convergence_series(
                    summary,
                    "dp [m]",
                    column,
                    title,
                    ylabel,
                    summary_dir / filename,
                    dpi=dpi,
                )

        error_table = build_columbia_error_table(summary)
        error_table.to_csv(summary_dir / "tabla_error_relativo.csv", index=False, encoding="utf-8-sig")

    if save_individual:
        for case_id in ordered_cases:
            case_output_dir = ensure_dir(individual_dir / f"Caso_{case_id}")
            trajectory_case = trajectory[trajectory["caso"] == case_id].sort_values("time [s]")
            velocity_case = velocity[velocity["caso"] == case_id].sort_values("time [s]")
            if trajectory_case.empty or velocity_case.empty:
                continue

            label = case_label(case_id, metadata_map)

            fig, ax = plt.subplots(figsize=(9, 5))
            ax.plot(trajectory_case["time [s]"], trajectory_case["dxy [m]"], linewidth=2.0)
            ax.set_title(f"{label} - Desplazamiento horizontal resultante")
            ax.set_xlabel("Tiempo [s]")
            ax.set_ylabel("Desplazamiento [m]")
            ax.grid(True, alpha=0.35)
            save_figure(fig, case_output_dir / f"{case_id}_dxy_vs_tiempo.png", dpi=dpi)

            fig, ax = plt.subplots(figsize=(9, 5))
            ax.plot(velocity_case["time [s]"], velocity_case["vxy [m/s]"], linewidth=2.0)
            ax.set_title(f"{label} - Velocidad horizontal resultante")
            ax.set_xlabel("Tiempo [s]")
            ax.set_ylabel("Velocidad [m/s]")
            ax.grid(True, alpha=0.35)
            save_figure(fig, case_output_dir / f"{case_id}_vxy_vs_tiempo.png", dpi=dpi)

            if not forces.empty:
                forces_case = forces[forces["caso"] == case_id].sort_values("time [s]")
                for column, title in (
                    ("fx", "Fuerza en X"),
                    ("fy", "Fuerza en Y"),
                    ("fz", "Fuerza en Z"),
                    ("fxyz", "Fuerza resultante total"),
                ):
                    if forces_case.empty or column not in forces_case.columns:
                        continue
                    fig, ax = plt.subplots(figsize=(9, 5))
                    ax.plot(forces_case["time [s]"], forces_case[column], linewidth=2.0)
                    ax.set_title(f"{label} - {title}")
                    ax.set_xlabel("Tiempo [s]")
                    ax.set_ylabel(column)
                    ax.grid(True, alpha=0.35)
                    save_figure(fig, case_output_dir / f"{case_id}_{column}_vs_tiempo.png", dpi=dpi)

    logger.info("Graficos Columbia generados en %s", output_dir)


def _write_sheet_or_note(
    writer: pd.ExcelWriter,
    sheet_name: str,
    frame: pd.DataFrame,
    notes: List[Dict[str, object]],
    csv_backup_path: Optional[Path] = None,
) -> None:
    if frame is None or frame.empty:
        return

    if len(frame) <= EXCEL_MAX_ROWS:
        frame.to_excel(writer, sheet_name=sheet_name[:31], index=False)
        return

    if csv_backup_path is not None:
        notes.append(
            {
                "hoja": sheet_name,
                "estado": "OMITIDA_EN_EXCEL",
                "motivo": f"Excede el limite de Excel ({EXCEL_MAX_ROWS} filas)",
                "archivo_csv": str(csv_backup_path),
            }
        )
        return

    frame.head(EXCEL_MAX_ROWS).to_excel(writer, sheet_name=sheet_name[:31], index=False)
    notes.append(
        {
            "hoja": sheet_name,
            "estado": "TRUNCADA_EN_EXCEL",
            "motivo": f"Excede el limite de Excel ({EXCEL_MAX_ROWS} filas)",
            "archivo_csv": "",
        }
    )


def write_pangea_outputs(
    tables: Dict[str, pd.DataFrame],
    output_dir: Path,
    material_token: str,
    logger: logging.Logger,
) -> Path:
    ensure_dir(output_dir)

    excel_path = output_dir / f"Pangea_{material_token}.xlsx"
    velocity_csv = output_dir / "Velocidades_completo.csv"
    hmax_csv = output_dir / "Hmax_completo.csv"
    velocity_diag_csv = output_dir / "Control_vel_gauges.csv"
    hmax_diag_csv = output_dir / "Control_hmax_gauges.csv"

    notes = [
        {
            "artefacto": "Velocidades_completo",
            "estado": "CSV",
            "detalle": str(velocity_csv),
        },
        {
            "artefacto": "Hmax_completo",
            "estado": "CSV",
            "detalle": str(hmax_csv),
        },
    ]

    if not tables["Velocidades_completo"].empty:
        tables["Velocidades_completo"].to_csv(velocity_csv, index=False, encoding="utf-8-sig")
    if not tables["Hmax_completo"].empty:
        tables["Hmax_completo"].to_csv(hmax_csv, index=False, encoding="utf-8-sig")

    tables["Control_vel_gauges"].to_csv(velocity_diag_csv, index=False, encoding="utf-8-sig")
    tables["Control_hmax_gauges"].to_csv(hmax_diag_csv, index=False, encoding="utf-8-sig")

    with pd.ExcelWriter(excel_path) as writer:
        tables["Metadatos"].to_excel(writer, sheet_name="Metadatos", index=False)
        tables["Control_archivos"].to_excel(writer, sheet_name="Control_archivos", index=False)
        tables["Resumen_vel_global"].to_excel(writer, sheet_name="Resumen_vel_global", index=False)
        tables["Resumen_hmax_global"].to_excel(writer, sheet_name="Resumen_hmax_global", index=False)
        tables["Resumen_vel_por_gauge"].to_excel(writer, sheet_name="Resumen_vel_por_gauge", index=False)
        tables["Resumen_hmax_por_gauge"].to_excel(writer, sheet_name="Resumen_hmax_por_gauge", index=False)
        tables["Resumen_global"].to_excel(writer, sheet_name="Resumen_global", index=False)
        pd.DataFrame(notes).to_excel(writer, sheet_name="Notas_exportacion", index=False)

    logger.info("Pangea exportado a %s", excel_path)
    return excel_path


def write_columbia_outputs(
    tables: Dict[str, pd.DataFrame],
    output_dir: Path,
    material_token: str,
    logger: logging.Logger,
) -> Path:
    ensure_dir(output_dir)

    excel_path = output_dir / f"Columbia_{material_token}.xlsx"
    exchange_csv = output_dir / "Exchange_completo.csv"
    forces_csv = output_dir / "Fuerzas_completo.csv"
    error_csv = output_dir / "Errores_convergencia.csv"

    tables["Exchange_completo"].to_csv(exchange_csv, index=False, encoding="utf-8-sig")
    if not tables["Fuerzas"].empty:
        tables["Fuerzas"].to_csv(forces_csv, index=False, encoding="utf-8-sig")

    error_table = build_columbia_error_table(tables["Resumen"])
    error_table.to_csv(error_csv, index=False, encoding="utf-8-sig")

    notes: List[Dict[str, object]] = [
        {
            "hoja": "Exchange_completo",
            "estado": "CSV_RESPALDO",
            "motivo": "",
            "archivo_csv": str(exchange_csv),
        },
        {
            "hoja": "Fuerzas",
            "estado": "CSV_RESPALDO",
            "motivo": "",
            "archivo_csv": str(forces_csv) if not tables["Fuerzas"].empty else "",
        },
    ]

    with pd.ExcelWriter(excel_path) as writer:
        tables["Metadatos"].to_excel(writer, sheet_name="Metadatos", index=False)
        tables["Control_archivos"].to_excel(writer, sheet_name="Control_archivos", index=False)
        tables["Resumen"].to_excel(writer, sheet_name="Resumen", index=False)
        _write_sheet_or_note(writer, "Trayectoria", tables["Trayectoria"], notes)
        _write_sheet_or_note(writer, "Velocidad", tables["Velocidad"], notes)
        _write_sheet_or_note(writer, "Exchange_completo", tables["Exchange_completo"], notes, csv_backup_path=exchange_csv)
        if not tables["Fuerzas"].empty:
            _write_sheet_or_note(writer, "Fuerzas", tables["Fuerzas"], notes, csv_backup_path=forces_csv)
        error_table.to_excel(writer, sheet_name="Errores_convergencia", index=False)
        pd.DataFrame(notes).to_excel(writer, sheet_name="Notas_exportacion", index=False)

    logger.info("Columbia exportado a %s", excel_path)
    return excel_path


def _build_common_parser(description: str) -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument("--base-dir", default=None, help="Directorio que contiene las carpetas de casos.")
    parser.add_argument(
        "--metadata-file",
        default=None,
        help="CSV o JSON con columnas caso, dp, material y observaciones.",
    )
    parser.add_argument("--cases", nargs="*", default=None, help="Lista explicita de casos a procesar.")
    parser.add_argument("--material", default="limestone", help="Material por defecto para casos sin metadatos.")
    parser.add_argument("--pause-on-exit", action="store_true", help="Pausa la consola al terminar.")
    return parser


def _pause_if_needed(enabled: bool) -> None:
    if enabled:
        input("\nPresiona ENTER para cerrar...")


def run_pangea_builder_from_cli(argv: Optional[Sequence[str]] = None) -> int:
    parser = _build_common_parser("Construye Pangea.xlsx a partir de GaugesVel y GaugesMaxZ.")
    parser.add_argument("--output-dir", default=None, help="Directorio de salida. Por defecto usa base-dir.")
    args = parser.parse_args(argv)

    base_dir = resolve_base_dir(args.base_dir)
    output_dir = Path(args.output_dir).expanduser().resolve() if args.output_dir else (base_dir if base_dir.exists() else Path.cwd())
    material_token = make_material_token({}, fallback=args.material)
    log_path = output_dir / f"log_pangea_{material_token.lower()}.txt"
    logger = configure_logger("pangea_builder", log_path)

    try:
        if not base_dir.exists():
            raise FileNotFoundError(f"No existe la carpeta base: {base_dir}")
        case_ids = discover_case_ids(base_dir, args.cases)
        if not case_ids:
            raise ValueError(f"No se encontraron casos en {base_dir}")
        metadata_map = load_case_metadata(case_ids, metadata_file=args.metadata_file, default_material=args.material)
        material_token = make_material_token(metadata_map, fallback=args.material)

        tables = assemble_pangea(base_dir, case_ids, metadata_map, logger)
        excel_path = write_pangea_outputs(tables, output_dir, material_token, logger)
        logger.info("Excel generado correctamente en %s", excel_path)
        return 0
    except Exception:
        logger.exception("Fallo la construccion de Pangea")
        return 1
    finally:
        _pause_if_needed(args.pause_on_exit)


def run_columbia_builder_from_cli(argv: Optional[Sequence[str]] = None) -> int:
    parser = _build_common_parser("Construye Columbia.xlsx a partir de ChronoExchange y ChronoBody_forces.")
    parser.add_argument("--output-dir", default=None, help="Directorio de salida. Por defecto usa base-dir.")
    parser.add_argument("--body-hint", default="blir", help="Nombre esperado del cuerpo del bloque en fuerzas.")
    args = parser.parse_args(argv)

    base_dir = resolve_base_dir(args.base_dir)
    output_dir = Path(args.output_dir).expanduser().resolve() if args.output_dir else (base_dir if base_dir.exists() else Path.cwd())
    material_token = make_material_token({}, fallback=args.material)
    log_path = output_dir / f"log_columbia_{material_token.lower()}.txt"
    logger = configure_logger("columbia_builder", log_path)

    try:
        if not base_dir.exists():
            raise FileNotFoundError(f"No existe la carpeta base: {base_dir}")
        case_ids = discover_case_ids(base_dir, args.cases)
        if not case_ids:
            raise ValueError(f"No se encontraron casos en {base_dir}")
        metadata_map = load_case_metadata(case_ids, metadata_file=args.metadata_file, default_material=args.material)
        material_token = make_material_token(metadata_map, fallback=args.material)

        tables = assemble_columbia(base_dir, case_ids, metadata_map, logger, body_hint=args.body_hint)
        excel_path = write_columbia_outputs(tables, output_dir, material_token, logger)
        logger.info("Excel generado correctamente en %s", excel_path)
        return 0
    except Exception:
        logger.exception("Fallo la construccion de Columbia")
        return 1
    finally:
        _pause_if_needed(args.pause_on_exit)


def run_pangea_plotter_from_cli(argv: Optional[Sequence[str]] = None) -> int:
    parser = _build_common_parser("Genera graficos Pangea desde GaugesVel y GaugesMaxZ.")
    parser.add_argument("--output-dir", default=None, help="Directorio de salida para graficos.")
    parser.add_argument("--dpi", type=int, default=300, help="Resolucion de las figuras.")
    args = parser.parse_args(argv)

    base_dir = resolve_base_dir(args.base_dir)
    material_token = make_material_token({}, fallback=args.material)
    default_output = (base_dir if base_dir.exists() else Path.cwd()) / f"Graficos_Pangea_{material_token}"
    output_dir = Path(args.output_dir).expanduser().resolve() if args.output_dir else default_output
    log_path = output_dir / f"log_graficos_pangea_{material_token.lower()}.txt"
    logger = configure_logger("pangea_plotter", log_path)

    try:
        if not base_dir.exists():
            raise FileNotFoundError(f"No existe la carpeta base: {base_dir}")
        case_ids = discover_case_ids(base_dir, args.cases)
        if not case_ids:
            raise ValueError(f"No se encontraron casos en {base_dir}")
        metadata_map = load_case_metadata(case_ids, metadata_file=args.metadata_file, default_material=args.material)
        material_token = make_material_token(metadata_map, fallback=args.material)

        tables = assemble_pangea(base_dir, case_ids, metadata_map, logger)
        if tables["Velocidades_completo"].empty and tables["Hmax_completo"].empty:
            raise ValueError("No se pudo leer ningun CSV de velocidades ni Hmax.")
        plot_pangea(tables, metadata_map, output_dir, dpi=args.dpi, logger=logger)
        return 0
    except Exception:
        logger.exception("Fallo la generacion de graficos Pangea")
        return 1
    finally:
        _pause_if_needed(args.pause_on_exit)


def run_columbia_plotter_from_cli(argv: Optional[Sequence[str]] = None) -> int:
    parser = argparse.ArgumentParser(description="Genera graficos Columbia desde el Excel armado.")
    parser.add_argument("--excel-path", default=None, help="Ruta al archivo Columbia.xlsx.")
    parser.add_argument("--metadata-file", default=None, help="CSV o JSON con columnas caso, dp, material y observaciones.")
    parser.add_argument("--output-dir", default=None, help="Directorio de salida para graficos.")
    parser.add_argument("--material", default="limestone", help="Material por defecto para casos sin metadatos.")
    parser.add_argument("--dpi", type=int, default=300, help="Resolucion de las figuras.")
    parser.add_argument("--save-individuals", dest="save_individuals", action="store_true", help="Guarda graficos individuales por caso.")
    parser.add_argument("--no-save-individuals", dest="save_individuals", action="store_false", help="No guarda graficos individuales por caso.")
    parser.set_defaults(save_individuals=True)
    parser.add_argument("--pause-on-exit", action="store_true", help="Pausa la consola al terminar.")
    args = parser.parse_args(argv)

    if args.excel_path:
        excel_path = Path(args.excel_path).expanduser().resolve()
    else:
        base_dir = resolve_base_dir(None)
        material_token = make_material_token({}, fallback=args.material)
        excel_path = base_dir / f"Columbia_{material_token}.xlsx"

    material_token = make_material_token({}, fallback=args.material)
    output_dir = Path(args.output_dir).expanduser().resolve() if args.output_dir else excel_path.parent / f"Graficos_Columbia_{material_token}"
    log_path = output_dir / f"log_graficos_columbia_{material_token.lower()}.txt"
    logger = configure_logger("columbia_plotter", log_path)

    try:
        workbook_tables = read_columbia_workbook(excel_path)
        case_ids = workbook_tables["Metadatos"]["caso"].astype(str).tolist() if not workbook_tables["Metadatos"].empty else []
        metadata_map = load_case_metadata(case_ids, metadata_file=args.metadata_file, default_material=args.material)
        plot_columbia(
            workbook_tables,
            metadata_map,
            output_dir=output_dir,
            dpi=args.dpi,
            save_individual=args.save_individuals,
            logger=logger,
        )
        return 0
    except Exception:
        logger.exception("Fallo la generacion de graficos Columbia")
        return 1
    finally:
        _pause_if_needed(args.pause_on_exit)
