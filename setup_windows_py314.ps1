$ErrorActionPreference = 'Stop'
Set-Location $PSScriptRoot

Write-Host '=== ThermalGuard - Windows / Python 3.14 setup ===' -ForegroundColor Cyan

$py = Get-Command python -ErrorAction SilentlyContinue
if (-not $py) {
  throw 'Python was not found on PATH. Install Python 3.14.x from python.org and enable Add Python to PATH.'
}

$version = python --version
Write-Host "Detected: $version"
if ($version -notmatch '^Python 3\.14\.') {
  throw "ThermalGuard v3.14 requires Python 3.14.x. Detected $version"
}

Set-Location (Join-Path $PSScriptRoot 'backend')
if (Test-Path 'venv') {
  Write-Host 'Existing venv found. Reusing it.' -ForegroundColor Yellow
} else {
  python -m venv venv
}

& .\venv\Scripts\python.exe -m pip install --upgrade pip
& .\venv\Scripts\python.exe -m pip install --only-binary=:all: -r requirements.txt

if (-not (Test-Path '.env')) { Copy-Item '.env.example' '.env' }

Write-Host ''
Write-Host 'Dependency installation complete.' -ForegroundColor Green
& .\venv\Scripts\python.exe -c "import sys,pandas,numpy,sklearn,xgboost; print('Python:',sys.version.split()[0]); print('pandas:',pandas.__version__); print('numpy:',numpy.__version__); print('scikit-learn:',sklearn.__version__); print('xgboost:',xgboost.__version__)"
Write-Host ''
Write-Host 'Start backend with:' -ForegroundColor Cyan
Write-Host '  .\venv\Scripts\python.exe -m uvicorn app.main:app --reload'
