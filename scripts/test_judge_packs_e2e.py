"""Isolated end-to-end test of approved C++ judge pack (no production DB writes)."""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import shutil
import socket
import subprocess
import sys
import tempfile
import time
from urllib.error import URLError
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from test_judge_packs import synthetic_pack


def request(base, route, obj=None):
    blob = None if obj is None else json.dumps(obj).encode("utf-8")
    req = Request(base + route, data=blob,
                  headers={"Content-Type": "application/json"}, method="GET" if blob is None else "POST")
    with urlopen(req, timeout=12) as response:
        return json.load(response)


with tempfile.TemporaryDirectory(prefix="cpp-coach-e2e-") as temp_dir:
    tmp = Path(temp_dir)
    for filename in ("server.py", "source_catalog.py", "problems.py",
                     "judge_packs.py", "judge.py", "progression.py",
                     "source_progress.py"):
        shutil.copy2(ROOT / filename, tmp / filename)
    (tmp / "static").mkdir()
    packs = tmp / "verified-judge-packs"
    packs.mkdir()
    pack_file = packs / "034.json"
    pack = synthetic_pack()
    pack_file.write_text(json.dumps(pack, ensure_ascii=False), encoding="utf-8")
    digest = hashlib.sha256(pack_file.read_bytes()).hexdigest()
    (packs / "approved.json").write_text(
        json.dumps({"schema_version": 1, "approved": {"34": digest}}), encoding="utf-8"
    )

    with socket.socket() as sock:
        sock.bind(("127.0.0.1", 0))
        port = sock.getsockname()[1]
    env = dict(os.environ)
    env["STUDY_COACH_HOST"] = "127.0.0.1"
    env["STUDY_COACH_PORT"] = str(port)
    env["PYTHONIOENCODING"] = "utf-8"
    proc = subprocess.Popen([sys.executable, str(tmp / "server.py")],
                            cwd=tmp, env=env, stdout=subprocess.DEVNULL,
                            stderr=subprocess.DEVNULL,
                            creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))
    try:
        base = f"http://127.0.0.1:{port}"
        deadline = time.monotonic() + 12
        while True:
            try:
                assert request(base, "/api/health")["ok"]
                break
            except (URLError, ConnectionError, TimeoutError):
                if time.monotonic() > deadline:
                    raise RuntimeError("Isolated Study Coach did not start")
                time.sleep(0.1)
        board = request(base, "/api/dashboard")
        assert board["exercises"][33]["auto_judge"] is True
        assert board["exercises"][34]["auto_judge"] is False
        assert board["summary"]["attempted"] == 0
        public = request(base, "/api/exercise/34")["problem"]
        assert public["test_count"] == 8
        assert public["hidden_count"] == 6
        assert "reference_cpp" not in public
        good = request(base, "/api/judge", {"exercise_id": 34,
                                           "code": pack["reference_cpp"], "record": False})
        assert good["judge"]["passed"] is True, good
        bad = request(base, "/api/judge", {"exercise_id": 34,
                                          "code": "int main(){return 0;}", "record": False})
        assert bad["judge"]["passed"] is False
        assert request(base, "/api/dashboard")["summary"]["attempted"] == 0
        print("ISOLATED_E2E_PASS: synthetic pack loaded, real g++ test passed, incorrect code rejected, progress unchanged")
    finally:
        proc.terminate()
        try:
            proc.wait(timeout=5)
        except subprocess.TimeoutExpired:
            proc.kill()
