# Local Windows build -> release\ShadowStrike-windows.zip
# Usage (from the project folder):   .\build_windows.ps1
$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot

python -m pip install --quiet -r requirements.txt pyinstaller
python -m PyInstaller --noconfirm --clean shadow_strike.spec

New-Item -ItemType Directory -Force release | Out-Null
$zip = "release\ShadowStrike-windows.zip"
if (Test-Path $zip) { Remove-Item $zip }
Compress-Archive -Path dist\ShadowStrike -DestinationPath $zip

$mb = [math]::Round((Get-Item $zip).Length / 1MB, 1)
Write-Host "Done: $zip ($mb MB)"
