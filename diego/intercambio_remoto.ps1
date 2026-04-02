param(
    [Parameter(Mandatory = $true)]
    [string]$RootPath,

    [ValidateSet("inventory", "export")]
    [string]$Mode = "inventory",

    [string]$OutDir = "",

    [string]$SelectionFile = "",

    [string[]]$IncludePatterns = @(),

    [string[]]$ExcludePatterns = @("*.bi4", "*.vtk", "*.ply", "*.zip", "*.7z", "*.rar", "*.tmp"),

    [switch]$ComputeHash
)

Set-StrictMode -Version 2.0
$ErrorActionPreference = "Stop"

function Resolve-FullPath {
    param([string]$PathValue)

    $item = Get-Item -LiteralPath $PathValue
    return $item.FullName
}

function Get-RelativePathSafe {
    param(
        [string]$BasePath,
        [string]$TargetPath
    )

    $baseResolved = (Resolve-FullPath $BasePath).TrimEnd('\') + '\'
    $targetResolved = Resolve-FullPath $TargetPath

    $baseUri = New-Object System.Uri($baseResolved)
    $targetUri = New-Object System.Uri($targetResolved)
    $relativeUri = $baseUri.MakeRelativeUri($targetUri)
    return [System.Uri]::UnescapeDataString($relativeUri.ToString()).Replace('/', '\')
}

function Ensure-Directory {
    param([string]$PathValue)

    if (-not (Test-Path -LiteralPath $PathValue)) {
        New-Item -ItemType Directory -Path $PathValue | Out-Null
    }
}

function Format-SizeMB {
    param([double]$Bytes)
    return [math]::Round($Bytes / 1MB, 3)
}

function Parse-SelectionFile {
    param([string]$PathValue)

    $result = @{
        Include = @()
        Exclude = @()
    }

    if (-not $PathValue) {
        return $result
    }

    if (-not (Test-Path -LiteralPath $PathValue)) {
        throw "No existe el archivo de seleccion: $PathValue"
    }

    $lines = Get-Content -LiteralPath $PathValue
    foreach ($rawLine in $lines) {
        $line = $rawLine.Trim()
        if (-not $line) { continue }
        if ($line.StartsWith("#")) { continue }

        if ($line.StartsWith("include:", [System.StringComparison]::OrdinalIgnoreCase)) {
            $result.Include += $line.Substring(8).Trim()
            continue
        }
        if ($line.StartsWith("exclude:", [System.StringComparison]::OrdinalIgnoreCase)) {
            $result.Exclude += $line.Substring(8).Trim()
            continue
        }
        if ($line.StartsWith("+")) {
            $result.Include += $line.Substring(1).Trim()
            continue
        }
        if ($line.StartsWith("-")) {
            $result.Exclude += $line.Substring(1).Trim()
            continue
        }

        $result.Include += $line
    }

    return $result
}

function Test-MatchPattern {
    param(
        [string]$RelativePath,
        [string]$Name,
        [string[]]$Patterns
    )

    if (-not $Patterns -or $Patterns.Count -eq 0) {
        return $false
    }

    foreach ($pattern in $Patterns) {
        if (-not $pattern) { continue }
        if ($RelativePath -like $pattern -or $Name -like $pattern) {
            return $true
        }
    }

    return $false
}

function New-InventoryRecord {
    param(
        [string]$BasePath,
        $FileItem,
        [bool]$UseHash
    )

    $relativePath = Get-RelativePathSafe -BasePath $BasePath -TargetPath $FileItem.FullName
    $topLevel = $relativePath.Split('\')[0]
    $directoryName = Split-Path -Path $relativePath -Parent
    $hashValue = ""

    if ($UseHash) {
        try {
            $hashValue = (Get-FileHash -Algorithm SHA256 -LiteralPath $FileItem.FullName).Hash
        } catch {
            $hashValue = "HASH_ERROR"
        }
    }

    return [PSCustomObject]@{
        relative_path    = $relativePath
        top_level        = $topLevel
        file_name        = $FileItem.Name
        directory        = $directoryName
        extension        = $FileItem.Extension
        size_bytes       = [int64]$FileItem.Length
        size_mb          = (Format-SizeMB -Bytes $FileItem.Length)
        last_write_time  = $FileItem.LastWriteTime.ToString("yyyy-MM-dd HH:mm:ss")
        full_path        = $FileItem.FullName
        sha256           = $hashValue
    }
}

function Write-InventoryArtifacts {
    param(
        [string]$DestinationRoot,
        [string]$RootResolved,
        [object[]]$InventoryRows,
        [string]$ModeValue,
        [string[]]$EffectiveInclude,
        [string[]]$EffectiveExclude
    )

    Ensure-Directory $DestinationRoot

    $manifestCsv = Join-Path $DestinationRoot "inventory_manifest.csv"
    $manifestJson = Join-Path $DestinationRoot "inventory_manifest.json"
    $extensionsCsv = Join-Path $DestinationRoot "inventory_by_extension.csv"
    $foldersCsv = Join-Path $DestinationRoot "inventory_by_top_level.csv"
    $treeTxt = Join-Path $DestinationRoot "inventory_tree.txt"
    $sessionJson = Join-Path $DestinationRoot "session_info.json"
    $readmeTxt = Join-Path $DestinationRoot "LEEME_INTERCAMBIO.txt"

    $InventoryRows | Sort-Object relative_path | Export-Csv -NoTypeInformation -Encoding UTF8 -Path $manifestCsv
    $InventoryRows | Sort-Object relative_path | ConvertTo-Json -Depth 4 | Set-Content -Encoding UTF8 -Path $manifestJson
    ($InventoryRows | Sort-Object relative_path | Select-Object -ExpandProperty relative_path) | Set-Content -Encoding UTF8 -Path $treeTxt

    $InventoryRows |
        Group-Object extension |
        Sort-Object Count -Descending |
        ForEach-Object {
            [PSCustomObject]@{
                extension  = if ($_.Name) { $_.Name } else { "[sin_extension]" }
                file_count = $_.Count
                total_mb   = [math]::Round((($_.Group | Measure-Object -Property size_bytes -Sum).Sum / 1MB), 3)
            }
        } | Export-Csv -NoTypeInformation -Encoding UTF8 -Path $extensionsCsv

    $InventoryRows |
        Group-Object top_level |
        Sort-Object Count -Descending |
        ForEach-Object {
            [PSCustomObject]@{
                top_level  = $_.Name
                file_count = $_.Count
                total_mb   = [math]::Round((($_.Group | Measure-Object -Property size_bytes -Sum).Sum / 1MB), 3)
            }
        } | Export-Csv -NoTypeInformation -Encoding UTF8 -Path $foldersCsv

    $session = [PSCustomObject]@{
        generated_at      = (Get-Date).ToString("yyyy-MM-dd HH:mm:ss")
        mode              = $ModeValue
        root_path         = $RootResolved
        file_count        = $InventoryRows.Count
        total_mb          = [math]::Round((($InventoryRows | Measure-Object -Property size_bytes -Sum).Sum / 1MB), 3)
        include_patterns  = $EffectiveInclude
        exclude_patterns  = $EffectiveExclude
        hostname          = $env:COMPUTERNAME
        username          = $env:USERNAME
    }
    $session | ConvertTo-Json -Depth 4 | Set-Content -Encoding UTF8 -Path $sessionJson

    @"
INTERCAMBIO REMOTO
==================

Raiz inventariada:
$RootResolved

Archivos generados:
- inventory_manifest.csv
- inventory_manifest.json
- inventory_tree.txt
- inventory_by_extension.csv
- inventory_by_top_level.csv
- session_info.json

Flujo sugerido:
1. Trae esta carpeta al otro PC.
2. Alli se revisa inventory_manifest.csv o inventory_tree.txt.
3. Se prepara un archivo de seleccion con lineas include:/exclude:.
4. Vuelves a correr este script en modo export usando ese archivo.
5. Traes la carpeta exportada con payload\ y sus manifiestos.
"@ | Set-Content -Encoding UTF8 -Path $readmeTxt
}

function Copy-SelectedFiles {
    param(
        [string]$DestinationRoot,
        [string]$BasePath,
        [object[]]$RowsToCopy
    )

    $payloadRoot = Join-Path $DestinationRoot "payload"
    Ensure-Directory $payloadRoot

    foreach ($row in $RowsToCopy) {
        $sourcePath = $row.full_path
        $targetPath = Join-Path $payloadRoot $row.relative_path
        $targetDir = Split-Path -Path $targetPath -Parent
        Ensure-Directory $targetDir
        Copy-Item -LiteralPath $sourcePath -Destination $targetPath -Force
    }
}

if (-not (Test-Path -LiteralPath $RootPath)) {
    throw "No existe RootPath: $RootPath"
}

$rootResolved = Resolve-FullPath $RootPath
$timestamp = Get-Date -Format "yyyyMMdd_HHmmss"

if (-not $OutDir) {
    $OutDir = Join-Path (Get-Location).Path ("diego_exchange_" + $timestamp)
}

$outResolved = [System.IO.Path]::GetFullPath($OutDir)
Ensure-Directory $outResolved

$selection = Parse-SelectionFile -PathValue $SelectionFile
$effectiveInclude = @()
if ($selection.Include.Count -gt 0) {
    $effectiveInclude += $selection.Include
}
if ($IncludePatterns.Count -gt 0) {
    $effectiveInclude += $IncludePatterns
}
$effectiveExclude = @()
if ($selection.Exclude.Count -gt 0) {
    $effectiveExclude += $selection.Exclude
}
if ($ExcludePatterns.Count -gt 0) {
    $effectiveExclude += $ExcludePatterns
}

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "INTERCAMBIO REMOTO DIEGO" -ForegroundColor Cyan
Write-Host "Modo: $Mode" -ForegroundColor Cyan
Write-Host "Raiz: $rootResolved" -ForegroundColor Cyan
Write-Host "Salida: $outResolved" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan

$allFiles = Get-ChildItem -LiteralPath $rootResolved -Recurse -Force -ErrorAction SilentlyContinue |
    Where-Object { -not $_.PSIsContainer }

$inventoryRows = @()
foreach ($file in $allFiles) {
    $inventoryRows += New-InventoryRecord -BasePath $rootResolved -FileItem $file -UseHash:$ComputeHash.IsPresent
}

Write-InventoryArtifacts `
    -DestinationRoot $outResolved `
    -RootResolved $rootResolved `
    -InventoryRows $inventoryRows `
    -ModeValue $Mode `
    -EffectiveInclude $effectiveInclude `
    -EffectiveExclude $effectiveExclude

Write-Host ("Inventario: {0} archivos, {1:N2} MB" -f $inventoryRows.Count, (($inventoryRows | Measure-Object -Property size_bytes -Sum).Sum / 1MB))

if ($Mode -eq "export") {
    if ($effectiveInclude.Count -eq 0) {
        throw "En modo export debes pasar -SelectionFile y/o -IncludePatterns."
    }

    $selectedRows = @()
    foreach ($row in $inventoryRows) {
        $isIncluded = Test-MatchPattern -RelativePath $row.relative_path -Name $row.file_name -Patterns $effectiveInclude
        if (-not $isIncluded) { continue }

        $isExcluded = Test-MatchPattern -RelativePath $row.relative_path -Name $row.file_name -Patterns $effectiveExclude
        if ($isExcluded) { continue }

        $selectedRows += $row
    }

    $selectedCsv = Join-Path $outResolved "selected_manifest.csv"
    $selectedTxt = Join-Path $outResolved "selected_tree.txt"

    $selectedRows | Sort-Object relative_path | Export-Csv -NoTypeInformation -Encoding UTF8 -Path $selectedCsv
    ($selectedRows | Sort-Object relative_path | Select-Object -ExpandProperty relative_path) | Set-Content -Encoding UTF8 -Path $selectedTxt

    if ($SelectionFile -and (Test-Path -LiteralPath $SelectionFile)) {
        Copy-Item -LiteralPath $SelectionFile -Destination (Join-Path $outResolved "selection_used.txt") -Force
    }

    Copy-SelectedFiles -DestinationRoot $outResolved -BasePath $rootResolved -RowsToCopy $selectedRows

    Write-Host ("Exportados: {0} archivos, {1:N2} MB" -f $selectedRows.Count, (($selectedRows | Measure-Object -Property size_bytes -Sum).Sum / 1MB)) -ForegroundColor Green
    Write-Host ("Payload: {0}" -f (Join-Path $outResolved "payload")) -ForegroundColor Green
} else {
    Write-Host "Inventario listo. Lleva esta carpeta al otro PC para revisar el manifest." -ForegroundColor Green
}

