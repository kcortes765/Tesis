$paths = @(
  "$HOME\.agents\skills",
  "$HOME\.codex\skills",
  ".agents\skills",
  "C:\Seba\.agente-global\skills"
)

foreach ($p in $paths) {
  if (Test-Path $p) {
    $count = (Get-ChildItem -LiteralPath $p -Force -ErrorAction SilentlyContinue | Measure-Object).Count
    "EXISTS`t$count`t$p"
  } else {
    "MISSING`t0`t$p"
  }
}
