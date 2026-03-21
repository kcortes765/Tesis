"""
deploy_ws.py — Empaqueta el proyecto para deploy en la Workstation UCN (RTX 5090).

La WS no tiene git instalado. El deploy es via ZIP + Copy-Item en PowerShell.
Este script:
  1. Copia src/*.py, config/, models/*.stl a un directorio temporal
  2. Genera XMLs de produccion (dp=0.004) para los 20 casos de gp_initial_batch.csv
  3. Crea run_batch.ps1 wrapper para la WS
  4. Comprime todo en deploy_ws_FECHA.zip

Uso:
  python scripts/deploy_ws.py
  python scripts/deploy_ws.py --matrix config/gp_initial_batch.csv
  python scripts/deploy_ws.py --dp 0.004

Autor: Kevin Cortes (UCN 2026)
"""

from __future__ import annotations

import json
import logging
import shutil
import sys
import zipfile
from datetime import datetime
from pathlib import Path

logger = logging.getLogger(__name__)

# Project root (two levels up from scripts/)
PROJECT_ROOT = Path(__file__).resolve().parent.parent

# Default production dp
DP_PROD = 0.004


def load_matrix(csv_path):
    """Carga la matriz de casos desde CSV."""
    import pandas as pd
    df = pd.read_csv(csv_path)
    logger.info(f"Matriz cargada: {len(df)} casos de {csv_path.name}")
    return df


def create_deploy_dir(base_dir):
    """Crea la estructura del directorio de deploy."""
    deploy_dir = base_dir / "deploy_ws"
    if deploy_dir.exists():
        shutil.rmtree(str(deploy_dir))

    # Subdirectorios
    (deploy_dir / "src").mkdir(parents=True)
    (deploy_dir / "config").mkdir(parents=True)
    (deploy_dir / "models").mkdir(parents=True)
    (deploy_dir / "cases").mkdir(parents=True)
    (deploy_dir / "data" / "processed").mkdir(parents=True)
    (deploy_dir / "data" / "figures").mkdir(parents=True)

    logger.info(f"Directorio de deploy creado: {deploy_dir}")
    return deploy_dir


def copy_source_files(deploy_dir):
    """Copia archivos fuente del pipeline."""
    # src/*.py
    src_dir = PROJECT_ROOT / "src"
    copied_src = 0
    for py_file in src_dir.glob("*.py"):
        shutil.copy2(str(py_file), str(deploy_dir / "src" / py_file.name))
        copied_src += 1
    logger.info(f"  src/*.py: {copied_src} archivos copiados")

    # config/ (json, csv, xml)
    config_dir = PROJECT_ROOT / "config"
    copied_cfg = 0
    for ext in ("*.json", "*.csv", "*.xml"):
        for f in config_dir.glob(ext):
            shutil.copy2(str(f), str(deploy_dir / "config" / f.name))
            copied_cfg += 1
    logger.info(f"  config/: {copied_cfg} archivos copiados")

    # models/*.stl (solo BLIR3 y Canal_Playa activo, no el ORIGINAL_15m)
    models_dir = PROJECT_ROOT / "models"
    copied_models = 0
    for stl_file in models_dir.glob("*.stl"):
        if "ORIGINAL" in stl_file.name:
            continue  # Skip backup del canal viejo
        shutil.copy2(str(stl_file), str(deploy_dir / "models" / stl_file.name))
        copied_models += 1
    logger.info(f"  models/*.stl: {copied_models} archivos copiados")

    return copied_src + copied_cfg + copied_models


def generate_case_xmls(deploy_dir, matrix_df, dp):
    """Genera XMLs de produccion para cada caso de la matriz."""
    # Import geometry_builder desde el proyecto
    sys.path.insert(0, str(PROJECT_ROOT / "src"))
    from geometry_builder import CaseParams, build_case

    config_path = PROJECT_ROOT / "config" / "dsph_config.json"
    with open(config_path) as f:
        config = json.load(f)

    template_xml = PROJECT_ROOT / config["paths"]["template_xml"]
    boulder_stl = PROJECT_ROOT / config["paths"]["boulder_stl"]
    beach_stl = PROJECT_ROOT / config["paths"]["beach_stl"]
    materials_xml = PROJECT_ROOT / config["paths"]["materials_xml"]
    cases_dir = deploy_dir / "cases"

    generated = 0
    for _, row in matrix_df.iterrows():
        case_id = row["case_id"]
        rot_z = float(row.get("boulder_rot_z", 0.0))

        params = CaseParams(
            case_name=case_id,
            dp=dp,
            dam_height=row["dam_height"],
            boulder_mass=row["boulder_mass"],
            boulder_scale=0.04,
            boulder_pos=(8.5, 0.5, 0.1),
            boulder_rot=(0.0, 0.0, rot_z),
            material="pvc",
            time_max=config["defaults"]["time_max"],
            time_out=config["defaults"]["time_out"],
            ft_pause=config["defaults"]["ft_pause"],
        )

        build_case(
            template_xml=template_xml,
            boulder_stl=boulder_stl,
            beach_stl=beach_stl,
            materials_xml=materials_xml,
            output_dir=cases_dir,
            params=params,
        )
        generated += 1
        logger.info(f"  [{generated}/{len(matrix_df)}] {case_id}: "
                     f"dam_h={row['dam_height']:.3f}, mass={row['boulder_mass']:.3f}, dp={dp}")

    logger.info(f"XMLs generados: {generated} casos con dp={dp}")
    return generated


def write_run_batch_ps1(deploy_dir):
    """Genera run_batch.ps1 para ejecutar en la WS."""
    ps1_content = r"""# run_batch.ps1 — Ejecutar batch de produccion en la WS UCN
# Generado automaticamente por deploy_ws.py
#
# Uso:
#   .\run_batch.ps1                    # Correr todos los casos
#   .\run_batch.ps1 -CaseId gp_001    # Correr un caso especifico
#
# Prerequisitos:
#   - Python 3.8+ con: numpy, pandas, trimesh, lxml, scipy, sqlalchemy, scikit-learn, matplotlib
#   - DualSPHysics v5.4 en C:\Users\ProyBloq_Cortes\Desktop\CarpetaTesis\ejecutablesWindows
#
# El config/dsph_config.json tiene dsph_bin='auto' y detecta la ruta automaticamente.

param(
    [string]$CaseId = "",
    [switch]$DryRun
)

$ErrorActionPreference = "Stop"
$ProjectRoot = $PSScriptRoot

Write-Host "============================================" -ForegroundColor Cyan
Write-Host " SPH-IncipientMotion — Batch de Produccion" -ForegroundColor Cyan
Write-Host " WS UCN (RTX 5090)" -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Directorio: $ProjectRoot"
Write-Host "Fecha: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')"
Write-Host ""

# Verificar Python
try {
    $pyVersion = python --version 2>&1
    Write-Host "Python: $pyVersion" -ForegroundColor Green
} catch {
    Write-Host "ERROR: Python no encontrado en PATH" -ForegroundColor Red
    exit 1
}

# Verificar que dsph_bin se resuelve
$configPath = Join-Path $ProjectRoot "config\dsph_config.json"
$config = Get-Content $configPath | ConvertFrom-Json
if ($config.dsph_bin -eq "auto") {
    $found = $false
    foreach ($path in $config.dsph_bin_paths) {
        if (Test-Path $path) {
            Write-Host "DualSPHysics: $path" -ForegroundColor Green
            $found = $true
            break
        }
    }
    if (-not $found) {
        Write-Host "ERROR: No se encontro DualSPHysics en ninguna ruta conocida" -ForegroundColor Red
        Write-Host "Rutas buscadas:" -ForegroundColor Yellow
        foreach ($path in $config.dsph_bin_paths) {
            Write-Host "  - $path" -ForegroundColor Yellow
        }
        exit 1
    }
}

# Verificar casos
$casesDir = Join-Path $ProjectRoot "cases"
if ($CaseId) {
    $caseDir = Join-Path $casesDir $CaseId
    if (-not (Test-Path $caseDir)) {
        Write-Host "ERROR: Caso '$CaseId' no encontrado en $casesDir" -ForegroundColor Red
        exit 1
    }
    $caseDirs = @($caseDir)
    Write-Host "Caso seleccionado: $CaseId" -ForegroundColor Yellow
} else {
    $caseDirs = Get-ChildItem $casesDir -Directory | Sort-Object Name
    Write-Host "Casos encontrados: $($caseDirs.Count)" -ForegroundColor Yellow
}

Write-Host ""

if ($DryRun) {
    Write-Host "[DRY RUN] Se ejecutarian $($caseDirs.Count) caso(s):" -ForegroundColor Magenta
    foreach ($d in $caseDirs) {
        $name = if ($d -is [string]) { Split-Path $d -Leaf } else { $d.Name }
        Write-Host "  - $name" -ForegroundColor Magenta
    }
    exit 0
}

# Ejecutar main_orchestrator con la matriz
$srcDir = Join-Path $ProjectRoot "src"
$matrixCsv = Join-Path $ProjectRoot "config\gp_initial_batch.csv"

Write-Host "Iniciando campana de produccion..." -ForegroundColor Cyan
Write-Host "Matriz: $matrixCsv" -ForegroundColor Cyan
Write-Host "dp: 0.004 (produccion)" -ForegroundColor Cyan
Write-Host ""

$env:PYTHONPATH = $srcDir
$startTime = Get-Date

if ($CaseId) {
    # Caso individual via batch_runner
    python -c @"
import sys, logging
sys.path.insert(0, r'$srcDir')
logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s: %(message)s', datefmt='%H:%M:%S')
from pathlib import Path
from batch_runner import load_config, run_case
config = load_config(Path(r'$ProjectRoot') / 'config' / 'dsph_config.json')
result = run_case(Path(r'$casesDir') / '$CaseId', config, dp=0.004)
sys.exit(0 if result['success'] else 1)
"@
} else {
    # Campana completa via main_orchestrator
    Push-Location $srcDir
    python -c @"
import sys, logging
sys.path.insert(0, r'$srcDir')
logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s: %(message)s', datefmt='%H:%M:%S')
from pathlib import Path
from batch_runner import load_config
from main_orchestrator import run_campaign
project_root = Path(r'$ProjectRoot')
config = load_config(project_root / 'config' / 'dsph_config.json')
matrix_csv = project_root / 'config' / 'gp_initial_batch.csv'
results = run_campaign(matrix_csv, project_root, config, dp=0.004)
ok = sum(1 for r in results if r['success'])
print(f'\nResultado final: {ok}/{len(results)} exitosos')
sys.exit(0 if all(r['success'] for r in results) else 1)
"@
    Pop-Location
}

$exitCode = $LASTEXITCODE
$elapsed = (Get-Date) - $startTime

Write-Host ""
Write-Host "============================================" -ForegroundColor Cyan
Write-Host " Tiempo total: $($elapsed.ToString('hh\:mm\:ss'))" -ForegroundColor Cyan
if ($exitCode -eq 0) {
    Write-Host " Estado: COMPLETADO" -ForegroundColor Green
} else {
    Write-Host " Estado: CON ERRORES (ver log arriba)" -ForegroundColor Red
}
Write-Host "============================================" -ForegroundColor Cyan

exit $exitCode
"""
    ps1_path = deploy_dir / "run_batch.ps1"
    with open(ps1_path, "w", encoding="utf-8") as f:
        f.write(ps1_content)
    logger.info(f"run_batch.ps1 generado: {ps1_path}")
    return ps1_path


def write_readme(deploy_dir, matrix_df, dp, timestamp):
    """Genera un README.txt con instrucciones de uso."""
    readme = f"""SPH-IncipientMotion — Deploy Package para WS UCN
=================================================
Generado: {timestamp}
Casos: {len(matrix_df)}
dp: {dp} (produccion)

INSTRUCCIONES:
1. Copiar esta carpeta completa a la WS:
   Copy-Item -Recurse deploy_ws\\ C:\\Users\\ProyBloq_Cortes\\Desktop\\SPH-Prod\\

2. En la WS, abrir PowerShell y ejecutar:
   cd C:\\Users\\ProyBloq_Cortes\\Desktop\\SPH-Prod
   .\\run_batch.ps1

3. Para correr un caso especifico:
   .\\run_batch.ps1 -CaseId gp_001

4. Para verificar sin ejecutar (dry run):
   .\\run_batch.ps1 -DryRun

PREREQUISITOS WS:
- Python 3.8+ con: numpy, pandas, trimesh, lxml, scipy, sqlalchemy, scikit-learn, matplotlib
- DualSPHysics v5.4 en: C:\\Users\\ProyBloq_Cortes\\Desktop\\CarpetaTesis\\ejecutablesWindows

ESTRUCTURA:
  run_batch.ps1     — Script principal de ejecucion
  src/              — Pipeline Python (geometry_builder, batch_runner, etc.)
  config/           — Configuracion (dsph_config.json, matrices, template XML)
  models/           — STLs (BLIR3.stl, Canal_Playa)
  cases/            — Casos pre-generados con XMLs de produccion (dp={dp})
  data/processed/   — Aqui se guardan los CSVs de resultado
  data/figures/     — Figuras generadas

NOTAS:
- dsph_config.json tiene dsph_bin='auto' — detecta WS automaticamente
- Cada caso tarda ~40-90 min con dp={dp} en RTX 5090
- Los .bi4 se eliminan automaticamente despues de cada sim (~64 GB/caso)
- Si un caso falla, el pipeline continua con el siguiente
"""
    readme_path = deploy_dir / "README.txt"
    with open(readme_path, "w", encoding="utf-8") as f:
        f.write(readme)
    logger.info(f"README.txt generado")
    return readme_path


def create_zip(deploy_dir, output_path):
    """Comprime el directorio de deploy en un ZIP."""
    file_count = 0
    total_size = 0

    with zipfile.ZipFile(str(output_path), "w", zipfile.ZIP_DEFLATED) as zf:
        for file_path in sorted(deploy_dir.rglob("*")):
            if file_path.is_file():
                arcname = file_path.relative_to(deploy_dir.parent)
                zf.write(str(file_path), str(arcname))
                file_count += 1
                total_size += file_path.stat().st_size

    zip_size = output_path.stat().st_size
    ratio = (1 - zip_size / total_size) * 100 if total_size > 0 else 0

    logger.info(f"ZIP creado: {output_path}")
    logger.info(f"  Archivos: {file_count}")
    logger.info(f"  Tamano original: {total_size / 1024 / 1024:.1f} MB")
    logger.info(f"  Tamano ZIP: {zip_size / 1024 / 1024:.1f} MB ({ratio:.0f}% compresion)")

    return output_path


def deploy(matrix_csv=None, dp=DP_PROD):
    """Funcion principal de deploy."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    if matrix_csv is None:
        matrix_csv = PROJECT_ROOT / "config" / "gp_initial_batch.csv"
    matrix_csv = Path(matrix_csv)

    logger.info("=" * 60)
    logger.info("SPH-IncipientMotion — Deploy para WS UCN")
    logger.info("=" * 60)
    logger.info(f"  Matriz: {matrix_csv}")
    logger.info(f"  dp: {dp}")
    logger.info(f"  Timestamp: {timestamp}")
    logger.info("")

    # 1. Cargar matriz
    matrix_df = load_matrix(matrix_csv)

    # 2. Crear directorio de deploy
    deploy_dir = create_deploy_dir(PROJECT_ROOT)

    # 3. Copiar archivos fuente
    logger.info("Copiando archivos fuente...")
    copy_source_files(deploy_dir)

    # 4. Generar XMLs de produccion
    logger.info(f"\nGenerando XMLs de produccion (dp={dp})...")
    generate_case_xmls(deploy_dir, matrix_df, dp)

    # 5. Generar run_batch.ps1
    logger.info("\nGenerando scripts de ejecucion...")
    write_run_batch_ps1(deploy_dir)

    # 6. Generar README
    write_readme(deploy_dir, matrix_df, dp, timestamp)

    # 7. Crear ZIP
    zip_name = f"deploy_ws_{timestamp}.zip"
    zip_path = PROJECT_ROOT / zip_name
    logger.info(f"\nCreando ZIP: {zip_name}")
    create_zip(deploy_dir, zip_path)

    # 8. Limpiar directorio temporal
    shutil.rmtree(str(deploy_dir))
    logger.info(f"Directorio temporal limpiado")

    logger.info("")
    logger.info("=" * 60)
    logger.info(f"DEPLOY LISTO: {zip_path}")
    logger.info(f"Copiar a la WS y ejecutar run_batch.ps1")
    logger.info("=" * 60)

    return zip_path


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s: %(message)s",
        datefmt="%H:%M:%S",
    )

    matrix_csv = None
    dp = DP_PROD

    args = sys.argv[1:]
    i = 0
    while i < len(args):
        if args[i] == "--matrix" and i + 1 < len(args):
            matrix_csv = Path(args[i + 1])
            i += 2
        elif args[i] == "--dp" and i + 1 < len(args):
            dp = float(args[i + 1])
            i += 2
        else:
            print(f"Argumento desconocido: {args[i]}")
            print("Uso: python deploy_ws.py [--matrix CSV] [--dp FLOAT]")
            sys.exit(1)

    zip_path = deploy(matrix_csv=matrix_csv, dp=dp)
    print(f"\nZIP generado: {zip_path}")
