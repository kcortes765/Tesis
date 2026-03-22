<#
.SYNOPSIS
    Setup script para la Workstation UCN. Ejecutar UNA vez despues de git clone.
.EXAMPLE
    cd C:\Users\Admin\Desktop\SPH-Tesis
    .\scripts\setup_ws.ps1
#>

Write-Host "=== Setup WS UCN ===" -ForegroundColor Cyan

# 1. Verificar Python
Write-Host "`n[1/5] Python..." -ForegroundColor Yellow
$pyVersion = python --version 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "[X] Python no encontrado. Instalar con: winget install Python.Python.3.10" -ForegroundColor Red
    exit 1
}
Write-Host "[OK] $pyVersion" -ForegroundColor Green

# 2. Instalar dependencias Python
Write-Host "`n[2/5] Dependencias Python..." -ForegroundColor Yellow
pip install numpy pandas trimesh lxml scipy sqlalchemy scikit-learn matplotlib 2>&1 | Select-Object -Last 3
Write-Host "[OK] Dependencias instaladas" -ForegroundColor Green

# 3. Verificar DualSPHysics
Write-Host "`n[3/5] DualSPHysics..." -ForegroundColor Yellow
$found = $false
$candidates = @(
    "C:\DualSPHysics_v5.4.3\DualSPHysics_v5.4\bin\windows",
    "C:\Users\Admin\Desktop\CarpetaTesis\ejecutablesWindows",
    "C:\Users\ProyBloq_Cortes\Desktop\CarpetaTesis\ejecutablesWindows"
)
foreach ($path in $candidates) {
    $gencase = Join-Path $path "GenCase_win64.exe"
    if (Test-Path $gencase) {
        Write-Host "[OK] DualSPHysics en: $path" -ForegroundColor Green
        $found = $true
        break
    }
}
if (-not $found) {
    Write-Host "[X] DualSPHysics no encontrado en rutas conocidas" -ForegroundColor Red
    Write-Host "    Buscar GenCase_win64.exe y agregar la ruta a config/dsph_config.json" -ForegroundColor Yellow
}

# 4. Verificar GPU
Write-Host "`n[4/5] GPU..." -ForegroundColor Yellow
nvidia-smi --query-gpu=name,memory.total --format=csv,noheader 2>&1
if ($LASTEXITCODE -eq 0) {
    Write-Host "[OK] GPU disponible" -ForegroundColor Green
} else {
    Write-Host "[!] nvidia-smi fallo" -ForegroundColor Yellow
}

# 5. Test rapido del pipeline
Write-Host "`n[5/5] Test pipeline (import modules)..." -ForegroundColor Yellow
python -c "
import sys; sys.path.insert(0, 'src')
from batch_runner import load_config
from pathlib import Path
config = load_config(Path('config/dsph_config.json'))
print(f'  dsph_bin: {config[`dsph_bin`]}')
from geometry_builder import CaseParams
print('  geometry_builder: OK')
from data_cleaner import CaseResult
print('  data_cleaner: OK')
from gp_active_learning import GPSurrogate
print('  gp_active_learning: OK')
print('  Pipeline: LISTO')
" 2>&1

Write-Host "`n=== Setup completo ===" -ForegroundColor Cyan
Write-Host "Para correr 20 sims dev:" -ForegroundColor Yellow
Write-Host "  cd src" -ForegroundColor White
Write-Host "  python main_orchestrator.py --matrix config/gp_initial_batch.csv" -ForegroundColor White
Write-Host "`nPara correr 20 sims produccion:" -ForegroundColor Yellow
Write-Host "  python main_orchestrator.py --matrix config/gp_initial_batch.csv --prod" -ForegroundColor White
