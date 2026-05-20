param(
    [string]$Project = "tesis",
    [int]$PollSeconds = 60,
    [int]$HeartbeatMinutes = 120,
    [string]$Label = "production",
    [switch]$Force
)

$ErrorActionPreference = "Stop"

$ProjectRoot = Split-Path -Parent $PSScriptRoot
$LogDir = Join-Path $ProjectRoot "data\logs"
New-Item -ItemType Directory -Path $LogDir -Force | Out-Null

$existing = Get-CimInstance Win32_Process |
    Where-Object {
        $_.CommandLine -match "watch_production_ntfy.py" -and
        $_.CommandLine -match [regex]::Escape($ProjectRoot)
    }

if ($existing -and -not $Force) {
    Write-Host "ntfy watcher already active:"
    $existing | Select-Object ProcessId, CommandLine
    exit 0
}

$RunId = Get-Date -Format "yyyyMMdd_HHmmss"
$SafeLabel = $Label -replace "[^A-Za-z0-9_-]", "_"
$stdout = Join-Path $LogDir "production_ntfy_watch_${SafeLabel}_stdout.log"
$stderr = Join-Path $LogDir "production_ntfy_watch_${SafeLabel}_stderr.log"
$state = Join-Path $LogDir "production_ntfy_watch_${SafeLabel}_${RunId}_state.json"
$log = Join-Path $LogDir "production_ntfy_watch_${SafeLabel}_${RunId}.log"

$args = @(
    "scripts\watch_production_ntfy.py",
    "--project", $Project,
    "--poll-seconds", "$PollSeconds",
    "--heartbeat-minutes", "$HeartbeatMinutes",
    "--exit-on-complete",
    "--state", $state,
    "--log", $log
)

$proc = Start-Process -FilePath "python" `
    -ArgumentList $args `
    -WorkingDirectory $ProjectRoot `
    -RedirectStandardOutput $stdout `
    -RedirectStandardError $stderr `
    -WindowStyle Hidden `
    -PassThru

Write-Host "ntfy watcher started"
Write-Host "pid=$($proc.Id)"
Write-Host "log=$log"
Write-Host "state=$state"
