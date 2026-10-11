<#
Create or verify SHA256SUMS.txt for exactly the two Windows release assets.
#>
param(
    [ValidateSet('Create','Verify')][string]$Mode = 'Create',
    [Parameter(Mandatory = $true)][string]$DistDir
)
$ErrorActionPreference = 'Stop'
$dir = (Resolve-Path -LiteralPath $DistDir -ErrorAction Stop).Path
$names = @('StudyCoach-Windows-Portable.zip', 'StudyCoach-Windows-Setup.exe')
$manifest = Join-Path $dir 'SHA256SUMS.txt'
if ($Mode -eq 'Create') {
    $lines = foreach ($name in $names) {
        $file = Join-Path $dir $name
        if (-not (Test-Path -LiteralPath $file -PathType Leaf)) { throw "Missing release asset: $name" }
        '{0}  {1}' -f (Get-FileHash -LiteralPath $file -Algorithm SHA256).Hash.ToLowerInvariant(), $name
    }
    [IO.File]::WriteAllText($manifest, (($lines -join [Environment]::NewLine) + [Environment]::NewLine), [Text.Encoding]::ASCII)
    Write-Output "CHECKSUMS_CREATED=$manifest"
    return
}
if (-not (Test-Path -LiteralPath $manifest -PathType Leaf)) { throw 'SHA256SUMS.txt missing' }
$actualLines = @([IO.File]::ReadAllLines($manifest) | Where-Object { $_ -ne '' })
if ($actualLines.Count -ne $names.Count) { throw 'Unexpected number of checksum entries' }
for ($i = 0; $i -lt $names.Count; $i++) {
    $name = $names[$i]
    if (-not ($actualLines[$i] -cmatch '^([a-f0-9]{64})  (.+)$')) {
        throw "Malformed SHA256SUMS entry at position $i"
    }
    if ($Matches[2] -cne $name) { throw "Unexpected SHA256SUMS entry at position $i" }
    $expected = $Matches[1]
    $file = Join-Path $dir $name
    if (-not (Test-Path -LiteralPath $file -PathType Leaf)) { throw "Missing release asset: $name" }
    $actual = (Get-FileHash -LiteralPath $file -Algorithm SHA256).Hash.ToLowerInvariant()
    if ($actual -cne $expected) { throw "SHA-256 mismatch: $name" }
}
Write-Output 'CHECKSUMS_VERIFIED=2'
