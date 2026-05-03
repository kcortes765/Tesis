# Safe Harness

Use `apos-run` for commands that are:
- productive
- costly
- GPU/batch
- destructive
- ambiguous

Examples:
```powershell
python apos-system\harness\apos-run.py preflight --cmd "python scripts\run_production.py --prod --matrix config\pilot.csv --max-cases 5 --dry-run"
python apos-system\harness\apos-run.py dry-run --matrix config\pilot.csv --max-cases 5
```
