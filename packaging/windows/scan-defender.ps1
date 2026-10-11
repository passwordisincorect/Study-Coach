<#
Scan final artifacts with Microsoft Defender before release.
PR builds may warn if Defender is unavailable. Tagged releases fail closed.
Scan failures and new threat detections always fail.
#>
param(
    [Parameter(Mandatory = $true)][string]$ScanPath,
    [switch]$RequireDefender
)
$ErrorActionPreference = 'Stop'
$resolved = (Resolve-Path -LiteralPath $ScanPath -ErrorAction Stop).Path
if (-not (Get-Command Get-MpComputerStatus -ErrorAction SilentlyContinue)) {
    if ($RequireDefender) { throw 'Microsoft Defender is unavailable; refusing to release unscanned binaries' }
    Write-Warning 'DEFENDER_SCAN_SKIPPED=Get-MpComputerStatus is unavailable'
    return
}
try { $status = Get-MpComputerStatus -ErrorAction Stop }
catch {
    if ($RequireDefender) { throw 'Microsoft Defender status cannot be read; refusing to release' }
    Write-Warning 'DEFENDER_SCAN_SKIPPED=Cannot read Defender status'
    return
}
if (-not $status.AMServiceEnabled -or -not $status.AntivirusEnabled) {
    if ($RequireDefender) { throw 'Microsoft Defender antivirus engine is disabled; refusing to release' }
    Write-Warning 'DEFENDER_SCAN_SKIPPED=Antivirus engine is disabled'
    return
}
if (-not $status.AntivirusSignatureLastUpdated -or
    ((Get-Date) - [datetime]$status.AntivirusSignatureLastUpdated).TotalDays -gt 7) {
    if ($RequireDefender) { throw 'Defender signatures are missing or over 7 days old; refusing to release' }
    Write-Warning 'DEFENDER_SCAN_SKIPPED=Antivirus signatures are missing or too old'
    return
}
$started = Get-Date
Start-MpScan -ScanType CustomScan -ScanPath $resolved -ErrorAction Stop
$newDetections = @(Get-MpThreatDetection -ErrorAction Stop | Where-Object {
    $_.InitialDetectionTime -ge $started.AddSeconds(-3)
})
if ($newDetections.Count -gt 0) {
    throw "Defender reported $($newDetections.Count) new threat detection(s) during release scan"
}
Write-Output "DEFENDER_SCAN_OK=$resolved;DEFINITIONS=$($status.AntivirusSignatureVersion)"
