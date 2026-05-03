# APOS-X preflight

Command: `python scripts\run_production.py --pilot --prod`
Allowed: False

## Reasons
- run_production.py with --pilot and --prod is ambiguous
- production command requires prior dry-run evidence or confirm token
- production command requires --max-cases
- production command requires explicit --matrix
