$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
$Source = Join-Path $Root "vscode-extension"
$Target = Join-Path $env:USERPROFILE ".vscode\extensions\local.study-coach-0.1.0"

if (Test-Path $Target) {
    Remove-Item $Target -Recurse -Force
}
New-Item -ItemType Directory -Path $Target -Force | Out-Null
Copy-Item (Join-Path $Source "*") $Target -Recurse -Force
Write-Host "Installed local extension to: $Target"
Write-Host "Reload VS Code window to activate it."
