from __future__ import annotations

import argparse
import json
import subprocess
from datetime import datetime
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
APOS = ROOT / ".apos"
OUT = APOS / "LAPTOP_SYNC.md"


def run_git(args: list[str]) -> str:
    git = r"C:\Program Files\Git\cmd\git.exe"
    cmd = [git, *args] if Path(git).exists() else ["git", *args]
    try:
        proc = subprocess.run(cmd, cwd=ROOT, text=True, capture_output=True, check=False)
    except Exception as exc:  # pragma: no cover - defensive local helper
        return f"[git unavailable: {exc}]"
    text = (proc.stdout or "").strip()
    err = (proc.stderr or "").strip()
    if proc.returncode != 0 and err:
        return f"{text}\n{err}".strip()
    return text


def read_text(path: Path, limit: int | None = None) -> str:
    if not path.exists():
        return "_No existe._"
    text = path.read_text(encoding="utf-8", errors="replace").strip()
    if limit is not None and len(text) > limit:
        return text[-limit:].lstrip()
    return text or "_Vacio._"


def read_json(path: Path) -> dict:
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}


def recent_exports() -> list[str]:
    exports = ROOT / "exports"
    if not exports.exists():
        return []
    dirs = sorted([p for p in exports.iterdir() if p.is_dir()], key=lambda p: p.stat().st_mtime, reverse=True)
    return [f"- `{p.relative_to(ROOT)}` ({datetime.fromtimestamp(p.stat().st_mtime).isoformat(timespec='minutes')})" for p in dirs[:8]]


def production_status_block() -> str:
    status = read_json(ROOT / "data" / "production_status.json")
    if not status:
        return "_No hay `data/production_status.json` disponible._"
    keys = [
        "phase",
        "mode",
        "dp",
        "total_cases",
        "completed",
        "failed",
        "current_case",
        "progress",
        "updated",
        "eta_human",
        "eta",
    ]
    lines = []
    for key in keys:
        if key in status:
            lines.append(f"- **{key}:** `{status[key]}`")
    return "\n".join(lines)


def dirty_files_block() -> str:
    status = run_git(["status", "--short"])
    if not status:
        return "_Worktree limpio._"
    lines = status.splitlines()
    heavyish = [line for line in lines if any(token in line for token in ["data/results.sqlite", "cases/", "_out", ".bi4", ".ibi4", ".vtk"])]
    normal = [line for line in lines if line not in heavyish]
    parts = []
    if normal:
        parts.append("**Cambios livianos o de codigo:**\n" + "\n".join(f"- `{line}`" for line in normal[:80]))
    if heavyish:
        parts.append("**Cambios runtime/pesados/no sincronizar a ciegas:**\n" + "\n".join(f"- `{line}`" for line in heavyish[:80]))
    return "\n\n".join(parts)


def build_summary() -> str:
    now = datetime.now().isoformat(timespec="seconds")
    head = run_git(["log", "-1", "--oneline"])
    branch = run_git(["branch", "--show-current"])
    remote = run_git(["status", "-sb"])
    exports = recent_exports()
    exports_text = "\n".join(exports) if exports else "_No hay exports livianos detectados._"
    return f"""# LAPTOP_SYNC

Ultima actualizacion WS: {now}
Proyecto: SPH-Tesis
Ruta WS: `{ROOT}`

Este archivo es el resumen inteligente que `/guardar` debe versionar para que la laptop reciba contexto por `git pull`.

## Git
- Rama: `{branch}`
- HEAD: `{head}`

```text
{remote}
```

## Estado productivo / simulaciones
{production_status_block()}

## Estado APOS resumido

### STATUS
{read_text(APOS / "STATUS.md", limit=6000)}

### HANDOFF
{read_text(APOS / "HANDOFF.md", limit=5000)}

### PLAN
{read_text(APOS / "PLAN.md", limit=3500)}

### Riesgos activos
{read_text(APOS / "RISKS.md", limit=3000)}

### Preguntas abiertas
{read_text(APOS / "OPEN_QUESTIONS.md", limit=2500)}

## Exports livianos recientes
{exports_text}

## Cambios locales al momento de guardar
{dirty_files_block()}

## Instrucciones para laptop
1. Ejecutar `git pull`.
2. Leer primero `.apos/LAPTOP_SYNC.md`.
3. Luego leer `.apos/HANDOFF.md` y `.apos/STATUS.md`.
4. No asumir que outputs runtime ignorados por Git estan disponibles localmente.
5. Si hay simulacion activa en WS, tratar `data/results.sqlite` como vivo hasta que exista export liviano cerrado.
"""


def main() -> None:
    parser = argparse.ArgumentParser(description="Genera resumen APOS para sincronizar a laptop por Git.")
    parser.add_argument("--print", action="store_true", help="Imprime el resumen ademas de escribirlo.")
    args = parser.parse_args()
    APOS.mkdir(exist_ok=True)
    text = build_summary()
    OUT.write_text(text, encoding="utf-8")
    if args.print:
        print(text)
    else:
        print(f"Wrote {OUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
