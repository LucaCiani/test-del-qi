$ErrorActionPreference = "Stop"

$python = Join-Path (Get-Location) ".venv\Scripts\python.exe"
if (-not (Test-Path $python)) {
    $python = (Get-Command python -ErrorAction SilentlyContinue).Source
}
if (-not $python) {
    Write-Error "Python non è installato. Installalo da python.org e riapri PowerShell."
}

& $python -m PyInstaller --version
if ($LASTEXITCODE -ne 0) {
    Write-Error "PyInstaller non è installato. Esegui: python -m pip install pyinstaller"
}

& $python -m PyInstaller --noconfirm --clean --onefile --windowed --name "Test-del-QI" `
    --distpath "." --workpath "build\onefile" --specpath "build\onefile" `
    --add-data "$(Join-Path (Get-Location) 'media');media" `
    --collect-all cv2 --collect-all pygame --collect-all PIL quiz_qi.py

Write-Host "Creato: .\Test-del-QI.exe"
