$ErrorActionPreference = 'Stop'

$packageName = 'winterm2'
$toolsDir = Split-Path -Parent $MyInvocation.MyCommand.Definition
$installDir = Join-Path $toolsDir '..\..'

# Install Python if not present
if (-not (Get-Command python -ErrorAction SilentlyContinue)) {
    Write-Host "Installing Python 3.11..."
    $pythonUrl = "https://www.python.org/ftp/python/3.11.8/python-3.11.8-amd64.exe"
    $pythonInstaller = Join-Path $env:TEMP "python-3.11.8-amd64.exe"

    Invoke-WebRequest -Uri $pythonUrl -OutFile $pythonInstaller -UseBasicParsing
    Start-Process -FilePath $pythonInstaller -Args "/quiet InstallAllUsers=1 PrependPath=1" -Wait

    $env:Path = [System.Environment]::GetEnvironmentVariable("Path", "Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path", "User")
}

# Create virtual environment
$venvDir = Join-Path $installDir "venv"
if (-not (Test-Path $venvDir)) {
    python -m venv $venvDir
}

# Install winterm2
$pipPath = Join-Path $venvDir "Scripts\pip.exe"
& $pipPath install --upgrade pip
& $pipPath install winterm2==0.1.0

# Verify installation
$wt2Path = Join-Path $venvDir "Scripts\wt2.exe"
if (Test-Path $wt2Path) {
    Write-Host "winterm2 installed successfully!"
    Write-Host "Run 'wt2 --help' to get started."
} else {
    throw "Installation failed - wt2.exe not found"
}
