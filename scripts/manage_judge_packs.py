"""Create, validate and explicitly approve local C++ judge packs for lessons 31–300.

Usage:
    py -3 scripts/manage_judge_packs.py draft 31
    py -3 scripts/manage_judge_packs.py check 31
    py -3 scripts/manage_judge_packs.py approve 31
    py -3 scripts/manage_judge_packs.py status

The tool never invents official Input/Output or asserts source verification.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import shutil
import sys
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from judge import judge_cpp, GPP
from judge_packs import (MANIFEST, PACK_DIR, PackError, read_pack, pack_path,
                         clear_cache, approvals)
from source_catalog import SOURCE_TITLES, source_problem_url


def make_draft(problem_id: int):
    path = pack_path(problem_id)
    PACK_DIR.mkdir(parents=True, exist_ok=True)
    if path.exists():
        raise PackError("Đã có file bài này; không được ghi đè.")
    url = source_problem_url(problem_id)
    obj = {
        "id": problem_id,
        "title": SOURCE_TITLES[problem_id - 1],
        "source_url": url,
        "statement": "",
        "input": "",
        "output": "",
        "hint": "",
        "official_samples_count": 2,
        "source_evidence": {
            "url": url,
            "captured_at": "",
            "reviewed_by": "",
            "input_output_checked": "no",
        },
        "reference_cpp": "",
        "tests": [],
    }
    path.write_text(json.dumps(obj, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("DRAFT", path)
    print("Cần đọc đề gốc và nhập ít nhất 2 test mẫu + 6 test ẩn. Draft KHÔNG được kích hoạt.")


def verify(problem_id: int) -> str:
    pack, digest = read_pack(problem_id)
    if not Path(GPP).is_file():
        raise PackError(f"Không tìm thấy g++: {GPP}")
    problem = {"tests": pack["tests"]}
    result = judge_cpp(pack["reference_cpp"], problem)
    if not result.get("ok") or not result.get("passed"):
        failed = [
            {
                "index": x.get("index"),
                "expected": x.get("expected") if x.get("index", 0) <= 2 else "(hidden)",
                "actual": x.get("actual"),
                "runtime_error": x.get("runtime_error"),
            }
            for x in result.get("results", []) if not x.get("passed")
        ]
        raise PackError("Reference C++ không qua toàn bộ test: " +
                        json.dumps({"stage": result.get("stage"),
                                    "error": result.get("compile_error") or result.get("error"),
                                    "failures": failed[:5]}, ensure_ascii=False))
    # Wrong reference (no output) must NOT pass. This only detects vacuous packs.
    wrong = judge_cpp("int main(){return 0;}", problem)
    if wrong.get("passed"):
        raise PackError("Test quá yếu: chương trình in rỗng vẫn đạt.")
    print(f"CHECK PASS: exercise={problem_id} tests={len(pack['tests'])} sha256={digest}")
    return digest


def approve(problem_id: int):
    digest = verify(problem_id)
    PACK_DIR.mkdir(parents=True, exist_ok=True)
    if MANIFEST.exists():
        data = json.loads(MANIFEST.read_text(encoding="utf-8"))
    else:
        data = {"schema_version": 1, "approved": {}}
    if data.get("schema_version") != 1 or not isinstance(data.get("approved"), dict):
        raise PackError("Manifest không hợp lệ; dừng để tránh mất trạng thái.")
    data["approved"][str(problem_id)] = digest
    data["updated_at"] = datetime.now(timezone.utc).isoformat()
    if MANIFEST.exists():
        back = MANIFEST.with_name("approved.backup-" +
                                  datetime.now().strftime("%Y%m%d-%H%M%S") + ".json")
        shutil.copy2(MANIFEST, back)
    tmp = MANIFEST.with_name("approved.tmp")
    tmp.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    tmp.replace(MANIFEST)
    clear_cache()
    print("APPROVED", problem_id)
    print("Khởi động lại riêng Study Coach để server nhận bộ chấm mới.")


def status():
    active = approvals()
    ready = []
    bad = []
    for id_text, sha in sorted(active.items(), key=lambda item: int(item[0])):
        try:
            pack, actual = read_pack(int(id_text))
            if actual == sha:
                ready.append(int(id_text))
            else:
                bad.append(id_text)
        except (ValueError, OSError, PackError):
            bad.append(id_text)
    print("APPROVED", len(ready), ready)
    print("INVALID_OR_CHANGED", len(bad), bad)
    print("PENDING_DRAFTS", len([p for p in PACK_DIR.glob("[0-9][0-9][0-9].json")
                                if str(int(p.stem)) not in active]) if PACK_DIR.exists() else 0)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("action", choices=("draft", "check", "approve", "status"))
    parser.add_argument("id", nargs="?", type=int)
    args = parser.parse_args()
    if args.action != "status" and args.id is None:
        parser.error("Thiếu mã bài.")
    try:
        if args.action == "draft":
            make_draft(args.id)
        elif args.action == "check":
            verify(args.id)
        elif args.action == "approve":
            approve(args.id)
        else:
            status()
    except (PackError, ValueError, OSError) as exc:
        print("ERROR", exc, file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
