# C++ Study Coach — Community Edition

Study Coach is a local-first C++ learning app with **300 exercises**, a **C++17 auto judge**, learning progress tracking, and optional VS Code / browser helpers. No ChatGPT account, API key, tunnel or network service is required for the judge itself.

## Source and copyright notice

The project lists short lesson titles and links to the original exercises at [300bàicode.vn](https://xn--300bicode-t1a.vn/). **The original problem statements, official examples, and browser captures are not distributed in this repository.** For exercises 31–300, open the link from the app to read the complete original problem.

The included reference C++ and **4,421 locally authored cases** are part of the Study Coach judge, not the official website judge. Exactly two cases per exercise are shown as generated demonstrations, clearly not official samples. Private website hidden tests were not available, so the local results may differ in ambiguous edge cases.

## Prerequisites

- Python 3.10+ (uses only the Python standard library)
- `g++` (GCC C++17 compiler)
- Windows or Linux

## Windows (PowerShell)

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
