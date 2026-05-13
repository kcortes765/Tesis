"""
watch_production_ntfy.py - watcher externo para ntfy en corridas SPH.

Lee data/production_status.json y el log production_*.log mas reciente.
Sirve cuando run_production.py fue lanzado con --no-notify o para tener
notificaciones de inicio de caso ademas de las nativas.

No modifica ni interrumpe simulaciones.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import time
from datetime import datetime
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "scripts"))

from notifier import notify  # noqa: E402


STATUS_PATH = PROJECT_ROOT / "data" / "production_status.json"
LOG_DIR = PROJECT_ROOT / "data" / "logs"

CASE_DONE_RE = re.compile(r">>>\s+(?P<case>\S+):\s+(?P<state>.+?)\s+en\s+(?P<duration>.+)$")
ERROR_RE = re.compile(r"\b(ERROR|EXCEPCION|ABORT)\b", re.IGNORECASE)


def read_json(path: Path) -> dict:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}


def latest_production_log() -> Path | None:
    logs = sorted((PROJECT_ROOT / "data").glob("production_*.log"), key=lambda p: p.stat().st_mtime, reverse=True)
    return logs[0] if logs else None


def load_state(path: Path) -> dict:
    if path.exists():
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            return {}
    return {}


def save_state(path: Path, state: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(state, indent=2, ensure_ascii=False), encoding="utf-8")


def append_log(path: Path, message: str) -> None:
    stamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.open("a", encoding="utf-8").write(f"{stamp} {message}\n")
    print(f"{stamp} {message}", flush=True)


def send(project: str, title: str, body: str, priority: str = "default", tags: str = "") -> None:
    notify(
        source="sph_production_watch",
        event_type="production_watch",
        priority=priority,
        title=title,
        body=body,
        tags=tags,
        project=project,
    )


def read_new_lines(log_path: Path, state: dict) -> list[str]:
    key = str(log_path)
    last = int(state.get("log_offsets", {}).get(key, log_path.stat().st_size))
    size = log_path.stat().st_size
    if size < last:
        last = 0
    with log_path.open("r", encoding="utf-8", errors="replace") as f:
        f.seek(last)
        lines = f.readlines()
        new_offset = f.tell()
    state.setdefault("log_offsets", {})[key] = new_offset
    return lines


def main() -> int:
    parser = argparse.ArgumentParser(description="Watcher ntfy para produccion SPH")
    parser.add_argument("--project-root", default=str(PROJECT_ROOT))
    parser.add_argument("--project", default="tesis")
    parser.add_argument("--poll-seconds", type=int, default=60)
    parser.add_argument("--heartbeat-minutes", type=int, default=0)
    parser.add_argument("--state", default=str(LOG_DIR / "production_ntfy_watch_state.json"))
    parser.add_argument("--log", default=None)
    parser.add_argument("--no-startup-notify", action="store_true")
    parser.add_argument("--exit-on-complete", action="store_true", default=True)
    args = parser.parse_args()

    state_path = Path(args.state)
    run_id = datetime.now().strftime("%Y%m%d_%H%M%S")
    monitor_log = Path(args.log) if args.log else LOG_DIR / f"production_ntfy_watch_{run_id}.log"
    state = load_state(state_path)
    state.setdefault("seen_cases_done", [])
    state.setdefault("seen_errors", [])

    status = read_json(STATUS_PATH)
    current = status.get("current_case", "")
    phase = status.get("phase", "unknown")
    progress = status.get("progress", "")
    append_log(monitor_log, f"watcher started phase={phase} current_case={current} progress={progress}")

    if not args.no_startup_notify:
        send(
            args.project,
            "SPH monitor ntfy activo",
            f"phase={phase}\ncase={current}\nprogress={progress}",
            priority="default",
            tags="satellite",
        )

    last_heartbeat = time.time()

    while True:
        status = read_json(STATUS_PATH)
        phase = status.get("phase", "unknown")
        current = status.get("current_case", "")
        progress = status.get("progress", "")
        completed = status.get("completed", 0)
        total = status.get("total_cases", "?")
        failed = status.get("failed", 0)

        if current and current != state.get("last_current_case"):
            state["last_current_case"] = current
            append_log(monitor_log, f"case start detected current_case={current} progress={progress}")
            send(
                args.project,
                f"SPH inicia caso: {current}",
                f"progress={progress}\ncompleted={completed}/{total}\nfailed={failed}",
                priority="default",
                tags="arrow_forward",
            )

        log_path = latest_production_log()
        if log_path and log_path.exists():
            for raw in read_new_lines(log_path, state):
                line = raw.strip()
                match = CASE_DONE_RE.search(line)
                if match:
                    case = match.group("case")
                    if case not in state["seen_cases_done"]:
                        state["seen_cases_done"].append(case)
                        title = f"SPH caso listo: {case}"
                        body = f"{match.group('state')} en {match.group('duration')}\ncompleted={completed}/{total}\nfailed={failed}"
                        append_log(monitor_log, f"case done detected {case}: {match.group('state')}")
                        send(args.project, title, body, priority="default", tags="white_check_mark")
                elif ERROR_RE.search(line) and "FALLO (" not in line and "Criterio" not in line:
                    key = line[:220]
                    if key not in state["seen_errors"]:
                        state["seen_errors"].append(key)
                        state["seen_errors"] = state["seen_errors"][-50:]
                        append_log(monitor_log, f"error detected: {line}")
                        send(args.project, "SPH alerta en corrida", line[:1000], priority="high", tags="warning")

        if phase in {"completed", "aborted"} and state.get("notified_final_phase") != phase:
            state["notified_final_phase"] = phase
            elapsed = status.get("total_elapsed_hours", "?")
            append_log(monitor_log, f"final phase detected phase={phase} completed={completed}/{total} failed={failed}")
            priority = "high" if phase == "completed" and int(failed or 0) == 0 else "urgent"
            tags = "trophy" if phase == "completed" else "octagonal_sign"
            send(
                args.project,
                f"SPH lote {phase}: {completed}/{total}",
                f"failed={failed}\nelapsed_h={elapsed}\nlast_case={current}",
                priority=priority,
                tags=tags,
            )
            save_state(state_path, state)
            if args.exit_on_complete:
                return 0

        if args.heartbeat_minutes > 0 and time.time() - last_heartbeat > args.heartbeat_minutes * 60:
            last_heartbeat = time.time()
            send(
                args.project,
                f"SPH heartbeat: {progress}",
                f"phase={phase}\ncase={current}\ncompleted={completed}/{total}\nfailed={failed}",
                priority="low",
                tags="hourglass",
            )

        save_state(state_path, state)
        time.sleep(args.poll_seconds)


if __name__ == "__main__":
    raise SystemExit(main())
