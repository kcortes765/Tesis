<#
.SYNOPSIS
    Wrapper para autonomous_runner.py — lanza el runner desde PowerShell.

.EXAMPLE
    .\runner.ps1                    # Ejecutar 1 tarea
    .\runner.ps1 -All               # Todas las tareas
    .\runner.ps1 -Sessions 3        # 3 sesiones
    .\runner.ps1 -Status            # Ver estado
    .\runner.ps1 -Verify            # Verificar setup
    .\runner.ps1 -Reset             # Resetear
    .\runner.ps1 -Model opus        # Usar Opus
#>

param(
    [switch]$All,
    [switch]$Status,
    [switch]$Verify,
    [switch]$Reset,
    [int]$Sessions = 0,
    [string]$Model = "sonnet",
    [int]$Timeout = 60,
    [switch]$Verbose
)

$RunnerScript = "C:\Seba\seba_os\scripts\autonomous_runner.py"
$ProjectRoot = Get-Location

if ($Status) {
    python $RunnerScript --project $ProjectRoot status
}
elseif ($Verify) {
    python $RunnerScript --project $ProjectRoot verify
}
elseif ($Reset) {
    python $RunnerScript --project $ProjectRoot reset
}
else {
    $args_list = @("--project", $ProjectRoot, "run", "--model", $Model, "--timeout", $Timeout)

    if ($All) {
        $args_list += "--all"
    }
    elseif ($Sessions -gt 0) {
        $args_list += @("--sessions", $Sessions)
    }

    if ($Verbose) {
        $args_list += "--verbose"
    }

    python $RunnerScript @args_list
}
