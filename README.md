# C++ Study Coach — Community Edition

Study Coach is a local-first C++ learning app with **300 exercises**, a **C++17 auto judge**, learning progress tracking, and optional VS Code / browser helpers. No ChatGPT account, API key, tunnel or network service is required for the judge itself.

## Source and copyright notice

The project lists short lesson titles and links to the original exercises at [300bàicode.vn](https://xn--300bicode-t1a.vn/). **The original problem statements, official examples, and browser captures are not distributed in this repository.** For exercises 31–300, open the link from the app to read the complete original problem.

The included reference C++ and **4,421 locally authored cases** are part of the Study Coach judge, not the official website judge. Exactly two cases per exercise are shown as generated demonstrations, clearly not official samples. Private website hidden tests were not available, so the local results may differ in ambiguous edge cases.

## Prerequisites

- Python 3.10+ (uses only the Python standard library)
- `g++` (GCC C++17 compiler)
- Windows or Linux

## Windows — No commands required

**Download the ready-to-use build from [GitHub Releases](https://github.com/passwordisincorect/Study-Coach/releases):**

- **Install:** download `StudyCoach-Windows-Setup.exe`, double-click and follow the setup wizard, then open **Study Coach** from your desktop or Start Menu.
- **Portable:** download `StudyCoach-Windows-Portable.zip`, extract the *whole archive*, then double-click `StudyCoach.exe`.

Both packages include **Python and the C++ compiler**, so you do **not** need Python, Git, GCC, PowerShell, or installation commands. The app runs locally and opens your browser automatically. Keep the Study Coach launcher window open while studying; use **Stop Study Coach** when finished.

**Important:** GitHub's green **Code → Download ZIP** contains source code, not the ready-to-run Windows package. Use **Releases** for the installer or portable ZIP. Release files appear after the build workflow completes.

## Windows download verification and release signing

Every **new signed Windows release** publishes three assets: the installer EXE, the portable ZIP, and SHA256SUMS.txt. Download all three from the **same GitHub release tag**. To verify locally in PowerShell:

```powershell
Get-FileHash .\StudyCoach-Windows-Setup.exe -Algorithm SHA256
Get-FileHash .\StudyCoach-Windows-Portable.zip -Algorithm SHA256
Get-AuthenticodeSignature .\StudyCoach-Windows-Setup.exe | Format-List Status,SignerCertificate,TimeStamperCertificate
```

Compare the SHA-256 values to SHA256SUMS.txt **and** confirm the manifest was obtained from the intended release. Check that Authenticode shows Status = Valid and an expected verified signer. SHA-256 detects changes but does not independently authenticate the publisher. Do not bypass Windows SmartScreen if the origin or signer is uncertain.

### Maintainer: configuring a signed release

A publicly trusted **code-signing certificate with accessible signing permissions** is required. A self-signed certificate does not establish Windows publisher trust. The workflow accepts a compatible PFX for automated signing, provisioned only through GitHub Actions repository secrets:

- STUDY_COACH_SIGNING_PFX_BASE64: base64 bytes of the PFX (one line).
- STUDY_COACH_SIGNING_PFX_PASSWORD: password for the PFX.

Never commit, paste into issues, or distribute the certificate, PFX, its private key, or its password. Hardware-backed or cloud-managed code-signing keys might **not** be exportable as PFX; those require a separate signing provider integration before the workflow can use them. Prefer a dedicated restricted signing identity over a reusable personal certificate.

On pull requests and untagged manual runs, binaries may be unsigned and Defender may be unavailable, but both conditions are explicit in the job output. On version tags (v*), the pipeline fails if the signing credentials are absent, signatures/timestamps are invalid, Defender is disabled/outdated, its scan fails, or a threat is reported. Only a fully passing Windows job can upload and publish its artifacts. The publication job alone has contents:write permission.

The Defender step requires a Windows runner with working Microsoft Defender, current signature definitions and permission to perform a custom scan. If the GitHub-hosted runner does not provide a working antivirus engine, the tag build **must fail closed**; configure a trusted Windows runner instead of silently skipping the scan. Do not claim that a release has been scanned unless the scan job succeeded.

A signed package can still receive SmartScreen warnings until its reputation is established. Signing and checksums improve authenticity and integrity but are not malware guarantees.


## Developer-only Windows source setup (PowerShell)

```powershell
git clone https://github.com/passwordisincorect/Study-Coach.git
cd Study-Coach
.\scripts\start.ps1
```

Then open **http://127.0.0.1:8780**. To stop: `.\scripts\stop.ps1`.

Install GCC through MSYS2 UCRT64 if needed. The server auto-detects `g++` on PATH or at `C:\msys64\ucrt64\bin\g++.exe`. You can override it:

```powershell
$env:STUDY_COACH_GPP = "C:\msys64\ucrt64\bin\g++.exe"
.\scripts\start.ps1
```

If your PowerShell execution policy blocks scripts, run `python server.py` directly. For another port: `.\scripts\start.ps1 -Port 8781`.

## Linux

Ubuntu/Debian:

```bash
sudo apt update && sudo apt install -y python3 g++ git
git clone https://github.com/passwordisincorect/Study-Coach.git
cd Study-Coach
bash scripts/start.sh
```

Open **http://127.0.0.1:8780**. Stop with Ctrl+C. To change the port: `STUDY_COACH_PORT=8781 bash scripts/start.sh`.

## How to use

Open Study Coach, choose a problem, read its linked original statement where needed, write C++17, run sample demonstrations, then submit. Successful submissions update progress automatically. Progress is local in `data/study.db` and is excluded from GitHub.

**Security:** the judge compiles and runs arbitrary C++ code. Keep this server bound to loopback (`127.0.0.1`) on a trusted computer. **Do not expose it directly to the public internet.**

## Verify installation

```bash
python -m unittest -q test_progression test_source_progress test_public_release
python scripts/manage_judge_packs.py status
```

The approval manifest pins SHA-256 hashes for all 270 packaged exercises (31–300); exercises 1–30 use built-in local material. The public `public_generated_v1` test policy does not claim to contain any original website examples.

## Extensions

The `browser-extension/` folder provides optional YouTube progress tracking (load unpacked on Chrome, Edge or Brave). The `vscode-extension/` folder contains an optional local VS Code extension.

## License

See `LICENSE` for the project's software license. The software license **does not grant rights to the original problem statements on third-party sites**. Link attribution is provided for navigation.
