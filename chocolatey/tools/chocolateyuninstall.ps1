$ErrorActionPreference = 'Stop'

$packageName = 'winterm2'
$toolsDir = Split-Path -Parent $MyInvocation.MyCommand.Definition
$installDir = Join-Path $toolsDir '..\..'

# Remove virtual environment
$venvDir = Join-Path $installDir "venv"
if (Test-Path $venvDir) {
    Remove-Item -Path $venvDir -Recurse -Force
    Write-Host "Removed winterm2 virtual environment"
}

# Remove user data directory
$userDataDir = Join-Path $env:APPDATA "winterm2"
if (Test-Path $userDataDir) {
    Remove-Item -Path $userDataDir -Recurse -Force
    Write-Host "Removed winterm2 configuration"
}

Write-Host "winterm2 uninstalled successfully"
