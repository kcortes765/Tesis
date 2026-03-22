"""
notifier.py — Engine central de notificaciones para Seba OS

Despacha notificaciones push via ntfy.sh. Integrado con APOS:
- Lee config de shared/notifier_config.json
- Lee NOTIFICATIONS.md del proyecto para decidir si notificar
- Respeta quiet hours
- Log de ultimas 100 entregas
- Fire-and-forget (nunca lanza excepciones al caller)

Uso directo:
    python notifier.py --test                    # Notificacion de prueba
    python notifier.py --notify "titulo" "cuerpo" --project tesis --priority high
    python notifier.py --task-change TASK-0042 doing done

Uso como modulo:
    from notifier import notify, notify_task_change, notify_session_close
"""

import argparse
import json
import logging
import sys
import urllib.request
import urllib.error
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------

SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent

# Buscar config: primero en el repo, luego en seba_os
_candidates = [
    PROJECT_ROOT / "config" / "notifier_config.json",  # En el repo Tesis
    SCRIPT_DIR.parent.parent / "seba_os" / "shared" / "notifier_config.json",  # seba_os local
]
CONFIG_PATH = next((p for p in _candidates if p.exists()), _candidates[0])


# ---------------------------------------------------------------------------
# Config loading
# ---------------------------------------------------------------------------

def load_config() -> dict:
    """Load notifier config. Returns empty dict on failure."""
    try:
        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        logger.warning(f"[notifier] No se pudo leer config: {e}")
        return {}


def _get_project_config(config: dict, project: str) -> dict:
    """Get project-specific config, falling back to defaults."""
    projects = config.get("projects", {})
    return projects.get(project, {})


# ---------------------------------------------------------------------------
# Quiet hours
# ---------------------------------------------------------------------------

def _in_quiet_hours(config: dict, priority: str = "default") -> bool:
    """Check if current time is in quiet hours."""
    qh = config.get("quiet_hours", {})
    if not qh.get("enabled", False):
        return False

    # Urgent always gets through
    if priority == "urgent" and qh.get("override_on_urgent", True):
        return False

    tz_name = qh.get("timezone", "America/Santiago")
    # Chile is UTC-3 (CLT) or UTC-4 (CLST) — use -3 as default
    # Simple offset since we don't want to require pytz
    try:
        offset_hours = -3 if "Santiago" in tz_name else 0
        tz = timezone(timedelta(hours=offset_hours))
        now = datetime.now(tz)
    except Exception:
        now = datetime.now()

    try:
        start_h, start_m = map(int, qh.get("start", "23:00").split(":"))
        end_h, end_m = map(int, qh.get("end", "07:00").split(":"))
    except (ValueError, AttributeError):
        return False

    current_minutes = now.hour * 60 + now.minute
    start_minutes = start_h * 60 + start_m
    end_minutes = end_h * 60 + end_m

    if start_minutes > end_minutes:
        # Crosses midnight: e.g. 23:00 - 07:00
        return current_minutes >= start_minutes or current_minutes < end_minutes
    else:
        return start_minutes <= current_minutes < end_minutes


# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------

def _log_notification(config: dict, entry: dict):
    """Append to notification log, keeping max_entries."""
    log_cfg = config.get("log", {})
    if not log_cfg.get("enabled", True):
        return

    log_path = Path(log_cfg.get("path", PROJECT_ROOT / "data" / "logs" / "notification_log.json"))
    max_entries = log_cfg.get("max_entries", 100)

    try:
        if log_path.exists():
            with open(log_path, "r", encoding="utf-8") as f:
                log_data = json.load(f)
        else:
            log_data = []
    except Exception:
        log_data = []

    log_data.append(entry)

    # Trim to max_entries
    if len(log_data) > max_entries:
        log_data = log_data[-max_entries:]

    try:
        log_path.parent.mkdir(parents=True, exist_ok=True)
        with open(log_path, "w", encoding="utf-8") as f:
            json.dump(log_data, f, indent=2, ensure_ascii=False)
    except Exception as e:
        logger.warning(f"[notifier] No se pudo escribir log: {e}")


# ---------------------------------------------------------------------------
# Core: send notification
# ---------------------------------------------------------------------------

def notify(
    source: str = "seba_os",
    event_type: str = "generic",
    priority: str = "default",
    title: str = "",
    body: str = "",
    tags: str = "",
    project: Optional[str] = None,
    topic_override: Optional[str] = None,
) -> bool:
    """
    Despacha una notificacion via ntfy.sh.

    Args:
        source: origen de la notificacion (nombre del sistema/script)
        event_type: tipo de evento (session_close, pipeline_error, etc.)
        priority: min | low | default | high | urgent
        title: titulo de la notificacion
        body: cuerpo del mensaje
        tags: emojis ntfy separados por coma
        project: nombre del proyecto (para resolver topic)
        topic_override: topic ntfy explicito (ignora config)

    Returns:
        True si se envio exitosamente, False en caso contrario.
        Nunca lanza excepciones.
    """
    try:
        config = load_config()

        # Master switch
        if not config.get("enabled", True):
            return False

        # Quiet hours check
        if _in_quiet_hours(config, priority):
            logger.info(f"[notifier] Quiet hours — suprimida: {title}")
            _log_notification(config, {
                "timestamp": datetime.now().isoformat(),
                "source": source,
                "event": event_type,
                "title": title,
                "priority": priority,
                "status": "suppressed_quiet_hours",
            })
            return False

        # Resolve topic
        if topic_override:
            topic = topic_override
        elif project:
            proj_cfg = _get_project_config(config, project)
            if not proj_cfg.get("enabled", True):
                return False
            topic = proj_cfg.get("topic", config.get("default_topic", "seba-os-2026"))
        else:
            topic = config.get("default_topic", "seba-os-2026")

        base_url = config.get("ntfy_base_url", "https://ntfy.sh")

        # Build and send request
        # ntfy supports UTF-8 in headers but urllib uses latin-1,
        # so we ASCII-encode non-ASCII chars as a fallback
        safe_title = title.encode("ascii", errors="replace").decode("ascii")
        headers = {"Title": safe_title, "Priority": priority}
        if tags:
            headers["Tags"] = tags

        req = urllib.request.Request(
            "{}/{}".format(base_url, topic),
            data=body.encode("utf-8") if body else b"",
            headers=headers,
        )
        urllib.request.urlopen(req, timeout=10)

        logger.info(f"[notifier] Enviada: {title} -> {topic} ({priority})")

        # Log
        _log_notification(config, {
            "timestamp": datetime.now().isoformat(),
            "source": source,
            "event": event_type,
            "project": project,
            "topic": topic,
            "title": title,
            "priority": priority,
            "status": "sent",
        })
        return True

    except Exception as e:
        logger.warning(f"[notifier] Fallo: {e}")
        try:
            _log_notification(load_config(), {
                "timestamp": datetime.now().isoformat(),
                "source": source,
                "event": event_type,
                "title": title,
                "priority": priority,
                "status": f"failed: {e}",
            })
        except Exception:
            pass
        return False


# ---------------------------------------------------------------------------
# Task change notifications
# ---------------------------------------------------------------------------

def notify_task_change(
    task_id: str,
    task_title: str,
    old_status: str,
    new_status: str,
    project: Optional[str] = None,
    task_priority: str = "p2",
) -> bool:
    """
    Notifica cambios de status en tasks.json.

    Solo notifica si el cambio esta en la lista de notify_on_status_change
    de la config.
    """
    try:
        config = load_config()
        tw = config.get("task_watching", {})
        if not tw.get("enabled", True):
            return False

        # Check if this transition should notify
        transitions = tw.get("notify_on_status_change", [])
        transition = f"{old_status}->{new_status}"
        wildcard = f"*->{new_status}"

        should_notify = transition in transitions or wildcard in transitions
        if not should_notify:
            return False

        # Map task priority to ntfy priority
        priority_map = tw.get("priority_map", {})
        ntfy_priority = priority_map.get(task_priority, "default")

        # Build notification
        status_emoji = {
            "done": "white_check_mark",
            "doing": "hammer",
            "waiting": "hourglass",
            "next": "arrow_forward",
        }
        tags = status_emoji.get(new_status, "memo")

        title = f"[{task_id}] {old_status} -> {new_status}"
        body = task_title

        return notify(
            source="task_watcher",
            event_type="task_change",
            priority=ntfy_priority,
            title=title,
            body=body,
            tags=tags,
            project=project,
        )

    except Exception as e:
        logger.warning(f"[notifier] task_change fallo: {e}")
        return False


# ---------------------------------------------------------------------------
# Session close notifications
# ---------------------------------------------------------------------------

def notify_session_close(
    project: str,
    handoff_summary: str = "",
    next_action: str = "",
) -> bool:
    """
    Notifica al cerrar sesion APOS (/guardar).

    Priority: low (informativo, no requiere accion inmediata).
    """
    body_parts = []
    if handoff_summary:
        body_parts.append(handoff_summary)
    if next_action:
        body_parts.append(f"Siguiente: {next_action}")
    body = "\n".join(body_parts) if body_parts else "Sesion cerrada correctamente."

    return notify(
        source="apos_guardar",
        event_type="session_close",
        priority="low",
        title=f"Sesion guardada: {project}",
        body=body,
        tags="floppy_disk",
        project=project,
    )


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="Seba OS Notifier")
    sub = parser.add_subparsers(dest="command")

    # --test
    test_p = sub.add_parser("test", help="Enviar notificacion de prueba")
    test_p.add_argument("--project", default=None, help="Proyecto (default: usa default_topic)")

    # --notify
    notify_p = sub.add_parser("notify", help="Enviar notificacion libre")
    notify_p.add_argument("title", help="Titulo")
    notify_p.add_argument("body", help="Cuerpo")
    notify_p.add_argument("--project", default=None)
    notify_p.add_argument("--priority", default="default")
    notify_p.add_argument("--tags", default="")

    # --task-change
    task_p = sub.add_parser("task-change", help="Notificar cambio de tarea")
    task_p.add_argument("task_id", help="ID de la tarea")
    task_p.add_argument("old_status", help="Status anterior")
    task_p.add_argument("new_status", help="Status nuevo")
    task_p.add_argument("--title", default="", help="Titulo de la tarea")
    task_p.add_argument("--project", default=None)
    task_p.add_argument("--task-priority", default="p2")

    # --session-close
    session_p = sub.add_parser("session-close", help="Notificar cierre de sesion")
    session_p.add_argument("project", help="Nombre del proyecto")
    session_p.add_argument("--summary", default="", help="Resumen del handoff")
    session_p.add_argument("--next-action", default="", help="Siguiente accion")

    args = parser.parse_args()

    # Setup logging
    logging.basicConfig(level=logging.INFO, format="%(message)s")

    if args.command == "test":
        ok = notify(
            source="cli_test",
            event_type="test",
            priority="default",
            title="Seba OS — Test de notificaciones",
            body=f"Si ves esto, ntfy funciona correctamente.\n{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            tags="white_check_mark,bell",
            project=args.project,
        )
        print(f"{'OK' if ok else 'FALLO'} — notificacion de prueba enviada")

    elif args.command == "notify":
        ok = notify(
            source="cli",
            event_type="manual",
            priority=args.priority,
            title=args.title,
            body=args.body,
            tags=args.tags,
            project=args.project,
        )
        print(f"{'OK' if ok else 'FALLO'}")

    elif args.command == "task-change":
        ok = notify_task_change(
            task_id=args.task_id,
            task_title=args.title,
            old_status=args.old_status,
            new_status=args.new_status,
            project=args.project,
            task_priority=args.task_priority,
        )
        print(f"{'OK' if ok else 'FALLO/FILTRADA'}")

    elif args.command == "session-close":
        ok = notify_session_close(
            project=args.project,
            handoff_summary=args.summary,
            next_action=args.next_action,
        )
        print(f"{'OK' if ok else 'FALLO'}")

    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
