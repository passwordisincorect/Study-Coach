$Root = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
$PidFile = Join-Path $Root 'data\server.pid'
if (-not (Test-Path $PidFile)) { Write-Output 'No server PID file'; exit 0 }
$id = (Get-Content $PidFile -Raw).Trim()
if ($id -match '^\d+$') {
    $proc = Get-CimInstance Win32_Process -Filter "ProcessId=$id" -ErrorAction SilentlyContinue
    if ($proc -and $proc.CommandLine -match 'server\.py') {
        Stop-Process -Id ([int]$id)
        Write-Output "Stopped server PID $id"
    }
}
Remove-Item $PidFile -Force -ErrorAction SilentlyContinue
