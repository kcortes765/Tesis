param(
    [string]$ProjectRoot = "C:\Users\Admin\Desktop\SPH-Tesis",
    [int]$PollSeconds = 600,
    [double]$MaxPrecheckDispPct = 2.0
)

$ErrorActionPreference = "Stop"
Set-Location $ProjectRoot

$LogDir = Join-Path $ProjectRoot "data\logs"
New-Item -ItemType Directory -Force -Path $LogDir | Out-Null
$RunId = Get-Date -Format "yyyyMMdd_HHmmss"
$LogPath = Join-Path $LogDir "batch4_auto_monitor_$RunId.log"

$PrecheckMatrix = Join-Path $ProjectRoot "config\batch4_precheck_mass_sanity_20260510.csv"
$Batch4Matrix = Join-Path $ProjectRoot "config\batch4_mass_probe_20260510.csv"
$StatusPath = Join-Path $ProjectRoot "data\production_status.json"

function Write-MonitorLog {
    param([string]$Message)
    $stamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $line = "$stamp $Message"
    Add-Content -LiteralPath $LogPath -Value $line
    Write-Host $line
}

function Get-ProductionProcesses {
    Get-CimInstance Win32_Process |
        Where-Object {
            $_.Name -match "DualSPHysics|GenCase" -or
            ($_.Name -eq "python.exe" -and $_.CommandLine -match "run_production.py")
        }
}

function Invoke-PrecheckEvaluation {
    $env:SPH_PROJECT_ROOT = $ProjectRoot
    $env:SPH_MAX_PRECHECK_DISP_PCT = [string]$MaxPrecheckDispPct
    $py = @'
import json
import os
import sqlite3
from pathlib import Path

root = Path(os.environ["SPH_PROJECT_ROOT"])
limit = float(os.environ["SPH_MAX_PRECHECK_DISP_PCT"])
cases = ["batch4_precheck_contact_m085", "batch4_precheck_contact_m125"]
db = root / "data" / "results.sqlite"
result = {
    "ok": False,
    "reason": "",
    "rows": [],
}

if not db.exists():
    result["reason"] = f"missing sqlite: {db}"
    print(json.dumps(result))
    raise SystemExit(0)

con = sqlite3.connect(db)
con.row_factory = sqlite3.Row
rows = []
for case in cases:
    row = con.execute("select * from results where case_name=?", (case,)).fetchone()
    if row is None:
        result["reason"] = f"missing result for {case}"
        print(json.dumps(result))
        raise SystemExit(0)
    rows.append(dict(row))
con.close()

result["rows"] = [
    {
        "case_name": r["case_name"],
        "dp": r["dp"],
        "classification_mode": r["classification_mode"],
        "reference_time_s": r["reference_time_s"],
        "max_displacement_rel": r["max_displacement_rel"],
        "max_displacement": r["max_displacement"],
        "max_rotation": r["max_rotation"],
        "moved": bool(r["moved"]),
        "rotated": bool(r["rotated"]),
        "failed": bool(r["failed"]),
        "sim_time_reached": r["sim_time_reached"],
        "max_flow_velocity": r["max_flow_velocity"],
        "max_sph_force": r["max_sph_force"],
        "max_contact_force": r["max_contact_force"],
    }
    for r in rows
]

for r in rows:
    if abs(float(r["dp"]) - 0.003) > 1e-9:
        result["reason"] = f"{r['case_name']} dp is {r['dp']}, expected 0.003"
        print(json.dumps(result))
        raise SystemExit(0)
    if r["classification_mode"] != "displacement_only":
        result["reason"] = f"{r['case_name']} classification_mode is {r['classification_mode']}"
        print(json.dumps(result))
        raise SystemExit(0)
    if float(r["sim_time_reached"] or 0.0) < 9.9:
        result["reason"] = f"{r['case_name']} incomplete sim_time_reached={r['sim_time_reached']}"
        print(json.dumps(result))
        raise SystemExit(0)
    if bool(r["failed"]) or bool(r["moved"]):
        result["reason"] = f"{r['case_name']} moved/failed in precheck"
        print(json.dumps(result))
        raise SystemExit(0)
    if float(r["max_displacement_rel"]) >= limit:
        result["reason"] = f"{r['case_name']} disp_pct={r['max_displacement_rel']:.3f} >= {limit:.3f}"
        print(json.dumps(result))
        raise SystemExit(0)

result["ok"] = True
result["reason"] = f"all precheck cases below {limit:.3f}% d_eq"
print(json.dumps(result))
'@
    $raw = $py | python -
    return $raw | ConvertFrom-Json
}

function Invoke-Batch4DryRun {
    $args = @(
        "scripts\run_production.py",
        "--prod",
        "--matrix", "config\batch4_mass_probe_20260510.csv",
        "--max-cases", "12",
        "--dry-run",
        "--no-notify"
    )
    $previous = $ErrorActionPreference
    $ErrorActionPreference = "Continue"
    try {
        $output = & python @args 2>&1
        $exitCode = $LASTEXITCODE
    }
    finally {
        $ErrorActionPreference = $previous
    }
    $text = ($output | ForEach-Object { $_.ToString() }) -join "`n"
    Add-Content -LiteralPath $LogPath -Value $text
    if ($exitCode -ne 0) {
        throw "Dry-run batch4 termino con exit code $exitCode"
    }

    $required = @(
        "# Casos: 12",
        "# dp: 0.003",
        "# modo: prod",
        "# classification_mode: displacement_only",
        "# reference_time_s: 0.500",
        "DRY RUN completado"
    )
    foreach ($needle in $required) {
        if ($text -notmatch [regex]::Escape($needle)) {
            throw "Dry-run batch4 no contiene: $needle"
        }
    }
}

function Start-Batch4Real {
    $stdout = Join-Path $LogDir "batch4_mass_probe_20260510_${RunId}_stdout.log"
    $stderr = Join-Path $LogDir "batch4_mass_probe_20260510_${RunId}_stderr.log"
    $args = @(
        "scripts\run_production.py",
        "--prod",
        "--matrix", "config\batch4_mass_probe_20260510.csv",
        "--max-cases", "12",
        "--no-notify"
    )
    $p = Start-Process -FilePath "python" `
        -ArgumentList $args `
        -WorkingDirectory $ProjectRoot `
        -RedirectStandardOutput $stdout `
        -RedirectStandardError $stderr `
        -WindowStyle Hidden `
        -PassThru
    Write-MonitorLog "Batch4 real lanzado. pid=$($p.Id) stdout=$stdout stderr=$stderr"
}

Write-MonitorLog "Monitor batch4 iniciado. ProjectRoot=$ProjectRoot PollSeconds=$PollSeconds MaxPrecheckDispPct=$MaxPrecheckDispPct"

foreach ($path in @($PrecheckMatrix, $Batch4Matrix)) {
    if (-not (Test-Path -LiteralPath $path)) {
        Write-MonitorLog "ERROR: falta matriz $path"
        exit 2
    }
}

while ($true) {
    $procs = @(Get-ProductionProcesses)
    $status = $null
    if (Test-Path -LiteralPath $StatusPath) {
        $status = Get-Content -LiteralPath $StatusPath -Raw | ConvertFrom-Json
    }

    if ($status -and $status.phase -eq "production") {
        Write-MonitorLog "Produccion activa: current_case=$($status.current_case) completed=$($status.completed)/$($status.total_cases) failed=$($status.failed). Esperando..."
        Start-Sleep -Seconds $PollSeconds
        continue
    }

    if ($procs.Count -gt 0) {
        $desc = ($procs | ForEach-Object { "$($_.Name):$($_.ProcessId)" }) -join ", "
        Write-MonitorLog "Procesos productivos activos sin status production claro: $desc. Esperando..."
        Start-Sleep -Seconds $PollSeconds
        continue
    }

    $eval = Invoke-PrecheckEvaluation
    Write-MonitorLog "Evaluacion precheck: ok=$($eval.ok) reason=$($eval.reason)"
    foreach ($r in $eval.rows) {
        Write-MonitorLog ("  {0}: disp_pct={1:N3} moved={2} rotated={3} rot={4:N2} flow={5:N4} Fsph={6:N4}" -f `
            $r.case_name, [double]$r.max_displacement_rel, $r.moved, $r.rotated, [double]$r.max_rotation, [double]$r.max_flow_velocity, [double]$r.max_sph_force)
    }

    if (-not $eval.ok) {
        Write-MonitorLog "NO se lanza batch4. Requiere diagnostico humano."
        exit 1
    }

    Write-MonitorLog "Precheck aprobado. Ejecutando dry-run batch4."
    Invoke-Batch4DryRun
    Write-MonitorLog "Dry-run batch4 aprobado. Lanzando batch4 real."
    Start-Batch4Real
    exit 0
}
