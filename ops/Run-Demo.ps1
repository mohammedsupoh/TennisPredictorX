param(
  [ValidateSet("local","sheet")]
  [string]$Mode = "local",
  [string]$SheetUrl = ""
)
Write-Host "== TennisPredictorX Demo Runner ==" -ForegroundColor Cyan

# Ensure venv
if (-not (Test-Path "$PSScriptRoot\..\ .venv")) {
  python -m venv "$PSScriptRoot\..\ .venv" | Out-Null
}
& "$PSScriptRoot\..\.venv\Scripts\Activate.ps1"

python -m pip install -U pip | Out-Null
pip install -U -r "$PSScriptRoot\..\requirements.txt" | Out-Null

$env:STREAMLIT_BROWSER_GATHER_USAGE_STATS="false"

if ($Mode -eq "sheet" -and [string]::IsNullOrWhiteSpace($SheetUrl)) {
  Write-Host "Provide -SheetUrl for Google Sheet CSV" -ForegroundColor Yellow
}

streamlit run "$PSScriptRoot\..\app\streamlit_app.py"
