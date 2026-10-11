<#
Sign Windows PE artifacts only when a compatible, trusted code-signing certificate
is supplied via GitHub Actions secrets. Do not print certificate or password.
#>
param(
    [Parameter(Mandatory = $true)][string[]]$Files,
    [switch]$RequireSigning
)
$ErrorActionPreference = 'Stop'
$certificateBase64 = $env:STUDY_COACH_SIGNING_PFX_BASE64
$certificatePassword = $env:STUDY_COACH_SIGNING_PFX_PASSWORD

if ([string]::IsNullOrWhiteSpace($certificateBase64) -or [string]::IsNullOrWhiteSpace($certificatePassword)) {
    if ($RequireSigning -or $certificateBase64 -or $certificatePassword) {
        throw 'Signing credentials are missing or incomplete. Release is blocked.'
    }
    Write-Output 'SIGNING_SKIPPED=No certificate configured (CI only; not a public release)'
    return
}
foreach ($file in $Files) {
    if (-not (Test-Path -LiteralPath $file -PathType Leaf)) { throw "Missing signing input: $file" }
}
$kits = Join-Path ([Environment]::GetFolderPath('ProgramFilesX86')) 'Windows Kits\10\bin'
$signTool = Get-ChildItem "$kits\*\x64\signtool.exe" -ErrorAction SilentlyContinue |
    Sort-Object { [version]$_.Directory.Parent.Name } -Descending | Select-Object -First 1
if (-not $signTool) { throw 'Windows SDK signtool.exe not found' }

$pfxPath = Join-Path $env:RUNNER_TEMP "studycoach-signing-$PID.pfx"
$certificate = $null
$removeImportedCertificate = $false
try {
    [IO.File]::WriteAllBytes($pfxPath, [Convert]::FromBase64String($certificateBase64))
    $password = ConvertTo-SecureString -String $certificatePassword -AsPlainText -Force
    $pfx = Get-PfxData -FilePath $pfxPath -Password $password
    if (-not $pfx.EndEntityCertificates -or $pfx.EndEntityCertificates.Count -ne 1) {
        throw 'Expected exactly one leaf signing certificate in the PFX'
    }
    $thumbprint = $pfx.EndEntityCertificates[0].Thumbprint
    $alreadyInstalled = Test-Path "Cert:\CurrentUser\My\$thumbprint"
    Import-PfxCertificate -FilePath $pfxPath -CertStoreLocation 'Cert:\CurrentUser\My' -Password $password -ErrorAction Stop | Out-Null
    $certificate = Get-Item "Cert:\CurrentUser\My\$thumbprint" -ErrorAction Stop
    if (-not $certificate.HasPrivateKey) { throw 'Certificate private key is not available to SignTool' }
    $removeImportedCertificate = -not $alreadyInstalled
    foreach ($file in $Files) {
        & $signTool.FullName sign /sha1 $thumbprint /s My /fd SHA256 /tr http://timestamp.digicert.com /td SHA256 "$file"
        if ($LASTEXITCODE -ne 0) { throw "Signing failed: $file" }
        & $signTool.FullName verify /pa /all "$file"
        if ($LASTEXITCODE -ne 0) { throw "Authenticode verification failed: $file" }
        $signature = Get-AuthenticodeSignature -LiteralPath $file
        if ($signature.Status -ne 'Valid' -or $signature.SignerCertificate.Thumbprint -ne $thumbprint) {
            throw "Invalid signature or signer mismatch: $file"
        }
        if (-not $signature.TimeStamperCertificate) { throw "No signing timestamp: $file" }
        Write-Output "SIGNED_AND_VERIFIED=$(Split-Path -Leaf $file)"
    }
}
finally {
    if ($removeImportedCertificate -and $certificate) {
        Remove-Item "Cert:\CurrentUser\My\$($certificate.Thumbprint)" -ErrorAction SilentlyContinue
    }
    if (Test-Path -LiteralPath $pfxPath) { Remove-Item -LiteralPath $pfxPath -Force }
}
