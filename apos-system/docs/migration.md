# APOS-X Migration

Order:
1. Audit.
2. Backup.
3. Prepare `.apos/`.
4. Add local `apos-system/`.
5. Validate in dry-run.
6. Install repo-local skills only after validation.
7. Global/user scope only with explicit confirmation.

Rollback:
- Restore `.apos/snapshots/<snapshot>`.
- Remove local `apos-system/` if needed.
- Do not touch global unless separately approved.
