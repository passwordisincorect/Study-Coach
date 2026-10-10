"""Verified, reference-tested local C++ judge packs.

Packs are *not* activated by merely copying a file. The approval manifest
pins its SHA-256, and the CLI checks the reference C++ program first.
"""
from __future__ import annotations

import hashlib
import json
from functools import lru_cache
from pathlib import Path

from source_catalog import SOURCE_TITLES, source_problem_url

ROOT = Path(__file__).resolve().parent
PACK_DIR = ROOT / "verified-judge-packs"
MANIFEST = PACK_DIR / "approved.json"
MIN_TESTS = 8
MAX_TESTS = 250
MAX_PACK_BYTES = 512_000


class PackError(ValueError):
    pass


def pack_path(exercise_id: int, base: Path = PACK_DIR) -> Path:
    if type(exercise_id) is not int or not 31 <= exercise_id <= 300:
        raise PackError("Chỉ chấp nhận mã bài 31–300.")
    return base / f"{exercise_id:03d}.json"


def read_pack(exercise_id: int, base: Path = PACK_DIR) -> tuple[dict, str]:
    path = pack_path(exercise_id, base)
    blob = path.read_bytes()
    if not blob or len(blob) > MAX_PACK_BYTES:
        raise PackError("Dung lượng bộ test không hợp lệ.")
    try:
        pack = json.loads(blob.decode("utf-8"))
    except (UnicodeError, json.JSONDecodeError) as exc:
        raise PackError("File bộ test không phải JSON UTF-8 hợp lệ.") from exc
    validate_structure(pack, exercise_id)
    return pack, hashlib.sha256(blob).hexdigest()


def validate_structure(pack: dict, exercise_id: int) -> None:
    if not isinstance(pack, dict):
        raise PackError("Định dạng pack không hợp lệ.")
    if type(pack.get("id")) is not int or pack["id"] != exercise_id:
        raise PackError("Mã bài trong pack không khớp tên file.")
    expected_title = SOURCE_TITLES[exercise_id - 1]
    if pack.get("title") != expected_title:
        raise PackError("Tên bài không khớp danh mục nguồn.")
    if pack.get("source_url") != source_problem_url(exercise_id):
        raise PackError("Liên kết nguồn không khớp mã bài.")
    for name in ("statement", "input", "output", "reference_cpp"):
        value = pack.get(name)
        if not isinstance(value, str) or len(value.strip()) < 10:
            raise PackError(f"Thiếu nội dung kiểm định: {name}.")
        if len(value) > (30000 if name == "reference_cpp" else 15000):
            raise PackError(f"Nội dung quá dài: {name}.")
    if pack.get("review_policy") == "public_generated_v1":
        if pack.get("official_samples_count") != 0:
            raise PackError("Public release contains no official source samples.")
        if "source_evidence" in pack or "source_conflicts" in pack:
            raise PackError("Do not distribute copied source evidence.")
        tests = pack.get("tests")
        if not isinstance(tests, list) or not 8 <= len(tests) <= MAX_TESTS:
            raise PackError("Public pack requires 8-250 independently authored tests.")
        if sum(isinstance(t, dict) and t.get("origin") == "demonstration" for t in tests) != 2:
            raise PackError("Exactly two locally authored demonstration examples required.")
        seen = set()
        for index, t in enumerate(tests, 1):
            if not isinstance(t, dict) or t.get("origin") not in ("demonstration", "generated"):
                raise PackError(f"Invalid public test label at {index}.")
            inp, out = t.get("input"), t.get("output")
            if (not isinstance(inp, str) or not isinstance(out, str)
                or not inp.strip() or not out.strip()
                or len(inp) > 20000 or len(out) > 20000 or inp in seen):
                raise PackError(f"Invalid or duplicate local test at {index}.")
            seen.add(inp)
        return

    evidence = pack.get("source_evidence")
    if not isinstance(evidence, dict):
        raise PackError("Thiếu bằng chứng đối chiếu đề gốc.")
    if evidence.get("url") != pack["source_url"]:
        raise PackError("Bằng chứng không khớp URL đề gốc.")
    for field in ("captured_at", "reviewed_by", "input_output_checked"):
        if not isinstance(evidence.get(field), str) or not evidence[field].strip():
            raise PackError(f"Thiếu bằng chứng: {field}.")
    if evidence["input_output_checked"] != "yes":
        raise PackError("Cần kiểm tra Input/Output với đề gốc trước khi duyệt.")
    tests = pack.get("tests")
    if not isinstance(tests, list) or not MIN_TESTS <= len(tests) <= MAX_TESTS:
        raise PackError(f"Cần {MIN_TESTS}–{MAX_TESTS} test, ít nhất 2 test mẫu.")
    official_count = pack.get("official_samples_count")
    if type(official_count) is not int or official_count > len(tests)-4:
        raise PackError("Số lượng test mẫu không hợp lệ.")
    policy = pack.get("review_policy")
    if policy is None:
        if official_count < 2:
            raise PackError("Cần ít nhất 2 ví dụ chính thức nếu không có chính sách duyệt bổ sung.")
    elif policy == "single_source_sample_v1":
        if official_count != 1 or len(tests) < 12:
            raise PackError("Chính sách một ví dụ: cần chính xác 1 ví dụ chính thức + ít nhất 11 test bổ sung.")
        audit = pack.get("generated_test_audit")
        if not isinstance(audit, dict) or any(not isinstance(audit.get(key), str) or len(audit[key].strip()) < 12
            for key in ("oracle_method", "edge_case_coverage", "reviewer", "limitations")):
            raise PackError("Thiếu thẩm định độc lập và giới hạn cho test tự tạo.")
        source_path = ROOT / "source-evidence" / f"{exercise_id:03d}.json"
        try:
            source = json.loads(source_path.read_text(encoding="utf-8"))
        except (OSError, ValueError) as exc:
            raise PackError("Không tìm được dữ liệu ví dụ chính thức để đối chiếu.") from exc
        samples = source.get("examples", [])
        if (source.get("source_url") != pack["source_url"] or
            source.get("title") != pack["title"] or not isinstance(samples, list)):
            raise PackError("Bộ ví dụ nguồn không khớp đề bài.")
        official_tests = [t for t in tests if t.get("origin") == "official"]
        generated_tests = [t for t in tests if t.get("origin") == "generated"]
        if len(official_tests) != 1 or len(generated_tests) != len(tests)-1:
            raise PackError("Phải đánh dấu đúng 1 test official, còn lại là generated.")
        match = [i for i, sample in enumerate(samples, 1)
                 if (sample.get("input") == official_tests[0]["input"] and
                     sample.get("output") == official_tests[0]["output"])]
        if len(match) != 1:
            raise PackError("Test được gọi là chính thức không trùng ví dụ gốc.")
        excluded = sorted(i for i in range(1, len(samples)+1) if i not in match)
        excluded_doc = pack.get("source_conflicts", [])
        if excluded:
            if not isinstance(excluded_doc, list) or sorted(x.get("sample_index") for x in excluded_doc if isinstance(x, dict)) != excluded:
                raise PackError("Ví dụ nguồn bị loại phải ghi rõ chỉ số và lý do.")
            if any(not isinstance(x.get("reason"), str) or len(x["reason"]) < 20 for x in excluded_doc):
                raise PackError("Thiếu lý do xử lý ví dụ không nhất quán.")
        elif excluded_doc:
            raise PackError("Không được khai báo xung đột không có thật.")
    else:
        raise PackError("Chính sách duyệt không được công nhận.")
    seen = set()
    for index, test in enumerate(tests, 1):
        if not isinstance(test, dict):
            raise PackError(f"Test {index} sai định dạng.")
        inp, out = test.get("input"), test.get("output")
        if not isinstance(inp, str) or not isinstance(out, str):
            raise PackError(f"Test {index} phải có input/output dạng chuỗi.")
        if not inp.strip() or not out.strip() or len(inp) > 20000 or len(out) > 20000:
            raise PackError(f"Test {index} thiếu dữ liệu hoặc quá lớn.")
        if inp in seen:
            raise PackError(f"Test trùng input: {index}.")
        seen.add(inp)


def public_judge_problem(pack: dict) -> dict:
    from problems import CPP_STARTER
    return {
        "id": pack["id"],
        "title": pack["title"],
        "statement": pack["statement"],
        "input": pack["input"],
        "output": pack["output"],
        "tests": [{**{"input": t["input"], "output": t["output"]}, **({"origin": t["origin"]} if "origin" in t else {})} for t in pack["tests"]],
        "hint": pack.get("hint", ""),
        "starter": CPP_STARTER,
        "source_url": pack["source_url"],
        "source_mode": "reviewed-reference-tested-local-pack",
    }


@lru_cache(maxsize=1)
def approvals() -> dict[str, str]:
    if not MANIFEST.is_file():
        return {}
    try:
        data = json.loads(MANIFEST.read_text(encoding="utf-8"))
        entries = data.get("approved", {})
        if not isinstance(entries, dict):
            return {}
        return {str(k): v for k, v in entries.items()
                if isinstance(v, str) and len(v) == 64}
    except (OSError, UnicodeError, json.JSONDecodeError):
        return {}


@lru_cache(maxsize=300)
def approved_problem(exercise_id: int):
    if type(exercise_id) is not int or not 31 <= exercise_id <= 300:
        return None
    sha = approvals().get(str(exercise_id))
    if not sha:
        return None
    try:
        pack, actual = read_pack(exercise_id)
        if actual != sha:
            return None
        return public_judge_problem(pack)
    except (OSError, PackError):
        return None


def clear_cache():
    approvals.cache_clear()
    approved_problem.cache_clear()
