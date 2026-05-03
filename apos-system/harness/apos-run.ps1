param(
  [Parameter(ValueFromRemainingArguments = $true)]
  [string[]]$Args
)

$script = Join-Path $PSScriptRoot "apos-run.py"
python $script @Args
