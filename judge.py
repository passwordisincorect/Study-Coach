from __future__ import annotations

import os
import subprocess
import tempfile
from pathlib import Path

import shutil
GPP = (os.environ.get("STUDY_COACH_GPP") or shutil.which("g++") or (r"C:\msys64\ucrt64\bin\g++.exe" if os.name == "nt" else "/usr/bin/g++"))
MAX_SOURCE_CHARS = 30000
MAX_OUTPUT_CHARS = 20000
COMPILE_TIMEOUT = 12
RUN_TIMEOUT = 2.5


def _clean(text: str) -> str:
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    lines = [line.rstrip() for line in text.split("\n")]
    while lines and lines[-1] == "":
        lines.pop()
    return "\n".join(lines).strip()


def _numeric_equal(actual: str, expected: str) -> bool:
    a_tokens = _clean(actual).split()
    e_tokens = _clean(expected).split()
    if len(a_tokens) != len(e_tokens) or not a_tokens:
        return False
    for a, e in zip(a_tokens, e_tokens):
        try:
            af = float(a)
            ef = float(e)
        except ValueError:
            if a != e:
                return False
            continue
        tolerance = 1e-6 * max(1.0, abs(ef))
        if abs(af - ef) > tolerance:
            return False
    return True


def outputs_equal(actual: str, expected: str) -> bool:
    if _clean(actual) == _clean(expected):
        return True
    return _numeric_equal(actual, expected)


def judge_cpp(code: str, problem: dict) -> dict:
    if not isinstance(code, str) or not code.strip():
        return {"ok": False, "stage": "validation", "error": "Code đang trống."}
    if len(code) > MAX_SOURCE_CHARS:
        return {"ok": False, "stage": "validation", "error": "Code quá dài."}
    if not Path(GPP).is_file():
        return {"ok": False, "stage": "server", "error": "Không tìm thấy g++ trên máy."}

    with tempfile.TemporaryDirectory(prefix="study-coach-") as tmp:
        tmpdir = Path(tmp)
        src = tmpdir / "main.cpp"
        exe = tmpdir / ("main.exe" if os.name == "nt" else "main")
        src.write_text(code, encoding="utf-8")

        try:
            compiled = subprocess.run(
                [GPP, str(src), "-std=c++17", "-O2", "-Wall", "-Wextra", "-o", str(exe)],
                cwd=str(tmpdir),
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                timeout=COMPILE_TIMEOUT,
                shell=False,
            )
        except subprocess.TimeoutExpired:
            return {"ok": False, "stage": "compile", "error": "Biên dịch quá thời gian cho phép."}

        if compiled.returncode != 0:
            return {
                "ok": False,
                "stage": "compile",
                "compile_error": (compiled.stderr or compiled.stdout)[-8000:],
            }

        results = []
        all_passed = True
        tests = problem.get("tests", [])
        for index, test in enumerate(tests, start=1):
            try:
                run = subprocess.run(
                    [str(exe)],
                    cwd=str(tmpdir),
                    input=test.get("input", ""),
                    capture_output=True,
                    text=True,
                    encoding="utf-8",
                    errors="replace",
                    timeout=RUN_TIMEOUT,
                    shell=False,
                )
                actual = (run.stdout or "")[:MAX_OUTPUT_CHARS]
                runtime_error = (run.stderr or "")[:4000]
                passed = run.returncode == 0 and outputs_equal(actual, test.get("output", ""))
                if not passed:
                    all_passed = False
                results.append({
                    "index": index,
                    "passed": passed,
                    "input": test.get("input", "") if index <= 2 and test.get("origin", "official") in ("official", "demonstration") else None,
                    "expected": test.get("output", "") if index <= 2 and test.get("origin", "official") in ("official", "demonstration") else None,
                    "actual": actual if (index <= 2 and test.get("origin", "official") in ("official", "demonstration")) or not passed else None,
                    "runtime_error": runtime_error if run.returncode != 0 else "",
                    "hidden": not (index <= 2 and test.get("origin", "official") in ("official", "demonstration")),
                })
            except subprocess.TimeoutExpired:
                all_passed = False
                results.append({
                    "index": index,
                    "passed": False,
                    "input": test.get("input", "") if index <= 2 and test.get("origin", "official") in ("official", "demonstration") else None,
                    "expected": test.get("output", "") if index <= 2 and test.get("origin", "official") in ("official", "demonstration") else None,
                    "actual": None,
                    "runtime_error": "Quá thời gian chạy (timeout).",
                    "hidden": not (index <= 2 and test.get("origin", "official") in ("official", "demonstration")),
                })

        return {
            "ok": True,
            "stage": "run",
            "passed": all_passed,
            "passed_count": sum(1 for r in results if r["passed"]),
            "total_count": len(results),
            "results": results,
            "compiler_warnings": (compiled.stderr or "")[-3000:] if compiled.returncode == 0 else "",
        }
