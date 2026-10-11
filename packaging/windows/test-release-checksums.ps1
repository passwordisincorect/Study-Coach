# Test checksum creation, verification and rejection of tampered bytes.
$ErrorActionPreference = 'Stop'
$dir = Join-Path ([IO.Path]::GetTempPath()) "studycoach-checksums-$PID"
New-Item -ItemType Directory -Path $dir -Force | Out-Null
$script = Join-Path $PSScriptRoot 'release-checksums.ps1'
try {
    'portable test payload' | Set-Content -LiteralPath (Join-Path $dir 'StudyCoach-Windows-Portable.zip')
    'installer test payload' | Set-Content -LiteralPath (Join-Path $dir 'StudyCoach-Windows-Setup.exe')
    & $script -Mode Create -DistDir $dir
    & $script -Mode Verify -DistDir $dir
    'tampered payload' | Add-Content -LiteralPath (Join-Path $dir 'StudyCoach-Windows-Setup.exe')
    $failedAsExpected = $false
    try { & $script -Mode Verify -DistDir $dir }
    catch { $failedAsExpected = $_.Exception.Message -like '*SHA-256 mismatch*' }
    if (-not $failedAsExpected) { throw 'Tampered release asset was not rejected' }
    Write-Output 'RELEASE_CHECKSUM_TESTS_OK=3'
}
finally { Remove-Item -LiteralPath $dir -Recurse -Force -ErrorAction SilentlyContinue }
