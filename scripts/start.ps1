param([int]$Port = 8780)
$ErrorActionPreference = 'Stop'
$Root = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
$env:STUDY_COACH_PORT = "$Port"
$python = $null
foreach ($n in @('py','python','python3')) {
    $cmd = Get-Command $n -ErrorAction SilentlyContinue
    if ($cmd) { $python = $cmd.Source; break }
}
if (-not $python) { throw 'Python 3.10+ is required.' }
if (-not $env:STUDY_COACH_GPP -and -not (Get-Command g++ -ErrorAction SilentlyContinue)) {
    $candidate = 'C:\msys64\ucrt64\bin\g++.exe'
    if (Test-Path $candidate) { $env:STUDY_COACH_GPP = $candidate }
}
$check = Get-NetTCPConnection -LocalPort $Port -State Listen -ErrorAction SilentlyContinue
if ($check) { throw "Port $Port is in use. Choose -Port 8781 or another free port." }
New-Item -Path (Join-Path $Root 'data') -ItemType Directory -Force | Out-Null
$args = @()
if ([IO.Path]::GetFileName($python) -ieq 'py.exe') { $args += '-3' }
$args += (Join-Path $Root 'server.py')
$proc = Start-Process -FilePath $python -ArgumentList $args -WorkingDirectory $Root -WindowStyle Hidden -PassThru
for ($i = 0; $i -lt 50; $i++) {
    Start-Sleep -Milliseconds 200
    try {
        $health = Invoke-RestMethod "http://127.0.0.1:$Port/api/health" -TimeoutSec 1
        if ($health.ok) {
            Write-Output "Study Coach started: http://127.0.0.1:$Port (PID $($proc.Id))"
            exit 0
        }
    } catch {}
    if ($proc.HasExited) { break }
}
throw 'Server startup failed. Run python server.py in a terminal for details.'
