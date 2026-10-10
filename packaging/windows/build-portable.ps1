param([string]$Output = '')
$ErrorActionPreference = 'Stop'
$Repo = Split-Path -Parent (Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path))
if (-not $Output) { $Output = Join-Path $Repo 'dist\StudyCoach-Windows-Portable' }
$Root = [IO.Path]::GetFullPath($Output)
$Toolchain = if ($env:STUDY_COACH_MSYS2) { Join-Path $env:STUDY_COACH_MSYS2 'ucrt64' } else { 'C:\msys64\ucrt64' }
if (-not (Test-Path (Join-Path $Toolchain 'bin\g++.exe'))) { throw 'MSYS2 UCRT64 GCC not found' }
if (Test-Path $Root) { throw 'Refusing to overwrite existing output directory' }
New-Item -ItemType Directory -Path $Root -Force | Out-Null
$assets = @('server.py','judge.py','judge_packs.py','problems.py','progression.py','source_catalog.py','source_progress.py')
foreach($f in $assets) { Copy-Item (Join-Path $Repo $f) $Root }
foreach($d in @('static','verified-judge-packs')) { Copy-Item (Join-Path $Repo $d) $Root -Recurse }
$runtime = Join-Path $Root 'runtime'
New-Item $runtime -ItemType Directory | Out-Null
$zip = Join-Path $env:TEMP 'study-coach-python-3.12.10-embed-amd64.zip'
if (-not (Test-Path $zip)) {
    Invoke-WebRequest 'https://www.python.org/ftp/python/3.12.10/python-3.12.10-embed-amd64.zip' -OutFile $zip -TimeoutSec 120
}
Expand-Archive -LiteralPath $zip -DestinationPath $runtime
$pth = Get-ChildItem $runtime -Filter 'python*._pth' | Select-Object -First 1
if (-not $pth) { throw 'Embedded Python ._pth missing' }
Add-Content -LiteralPath $pth.FullName -Value '..'
$compilerRoot = Join-Path $Root 'toolchain'
New-Item $compilerRoot -ItemType Directory | Out-Null
foreach($dir in @('bin','include','lib','x86_64-w64-mingw32','etc')) {
    $src = Join-Path $Toolchain $dir
    if (Test-Path $src) { Copy-Item $src -Destination (Join-Path $compilerRoot $dir) -Recurse -Force }
}
$source = Join-Path $Repo 'packaging\windows\launcher.cpp'
$exe = Join-Path $Root 'StudyCoach.exe'
& (Join-Path $Toolchain 'bin\g++.exe') $source -o $exe -std=c++17 -municode -mwindows -static -lws2_32 -lshell32
if ($LASTEXITCODE -ne 0) { throw 'Launcher C++ build failed' }
$licenses = Join-Path $Root 'LICENSES'
New-Item $licenses -ItemType Directory | Out-Null
Copy-Item (Join-Path $Repo 'LICENSE') (Join-Path $licenses 'STUDY-COACH-LICENSE.txt')
$otherLicenses = Join-Path $Toolchain 'share\licenses'
if (Test-Path $otherLicenses) { Copy-Item $otherLicenses -Destination (Join-Path $licenses 'MSYS2-PACKAGE-LICENSES') -Recurse }
'Python 3.12.10 embedded distribution: https://www.python.org/downloads/release/python-31210/ (PSF License).' | Set-Content (Join-Path $licenses 'PYTHON.txt')
'GCC/MSYS2 UCRT64 runtime and toolchain: https://www.msys2.org/ . Redistributable packages are covered by the packages respective open-source licenses including GNU GPL and runtime exceptions. See https://www.gnu.org/licenses/ and https://packages.msys2.org/ for notices.' | Set-Content (Join-Path $licenses 'TOOLCHAIN.txt')
"Portable Study Coach: extract this entire folder then double-click StudyCoach.exe. Keep the window open while using the browser. Do not delete runtime or toolchain. Full exercises 31-300: open their original source links in the app." | Set-Content (Join-Path $Root 'START-HERE.txt')
Write-Output "PORTABLE_DIR=$Root"
Write-Output "LAUNCHER_BYTES=$((Get-Item $exe).Length)"
