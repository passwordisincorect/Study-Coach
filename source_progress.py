"""Manual progress capture for exercises without a verified local judge.

This is a user-attested report of AC on the external site, NOT automatic
verification. It is deliberately excluded from clean-pass acceleration.
"""
from __future__ import annotations

from typing import Callable


class SourceProgressError(ValueError):
    pass


def record_source_ac(conn, exercise_id, confirmed, has_local_judge: Callable[[int], bool], now: Callable[[], str]):
    # Explicit boolean only; strings such as "true" are not adequate confirmation.
    if type(exercise_id) is not int or not (1 <= exercise_id <= 300):
        raise SourceProgressError("Mã bài phải là số nguyên từ 1 đến 300.")
    if confirmed is not True:
        raise SourceProgressError("Cần xác nhận bạn đã thấy kết quả AC trên trang nguồn.")
    if has_local_judge(exercise_id):
        raise SourceProgressError("Bài này đã có Auto Judge local; hãy nộp qua trình chấm.")
    latest = conn.execute(
        "SELECT outcome FROM attempts WHERE exercise_id=? ORDER BY id DESC LIMIT 1",
        (exercise_id,),
    ).fetchone()
    if latest is not None and latest["outcome"] == "external_pass":
        return False

    conn.execute(
        "INSERT INTO attempts(exercise_id,outcome,duration_sec,compile_errors,notes,created_at)"
        " VALUES(?,?,?,?,?,?)",
        (
            exercise_id,
            "external_pass",
            0,
            0,
            "AC trên trang nguồn, người học tự xác nhận; chưa được hệ thống xác minh.",
            now(),
        ),
    )
    conn.execute(
        "INSERT INTO meta(key,value) VALUES('active_exercise_id',?) "
        "ON CONFLICT(key) DO UPDATE SET value=excluded.value",
        (str(exercise_id),),
    )
    return True
