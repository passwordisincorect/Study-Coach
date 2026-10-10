"""Conservative adaptive exercise routing for C++ Study Coach.

A skipped exercise is never treated as passed. Progress comes only from attempts.
"""
from __future__ import annotations

from typing import Callable

PASS = {"independent", "hint", "external_pass"}
RETRY = {"failed", "solution"}
QUICK_CHECK_COUNT = 4
MAX_CLEAN_SECONDS = 600


def choose_next(conn, levels: list | tuple, has_judge: Callable[[int], bool]) -> dict:
    attempts = [
        dict(row)
        for row in conn.execute(
            "SELECT exercise_id,outcome,duration_sec,compile_errors FROM attempts ORDER BY id DESC"
        )
    ]
    if not attempts:
        return {
            "action": "BẮT ĐẦU",
            "exercise_id": 1,
            "tone": "start",
            "reason": "Bắt đầu ở bài 1. Hệ thống sẽ chỉ đề nghị kiểm tra nhảy bài khi đã có bằng chứng làm bài độc lập.",
        }

    latest = attempts[0]
    latest_id = int(latest["exercise_id"])
    if latest["outcome"] in RETRY:
        return {
            "action": "SỬA BÀI",
            "exercise_id": latest_id,
            "tone": "practice",
            "reason": "Bài vừa nộp chưa đạt. Sửa và thử lại trước khi chuyển bài.",
        }

    # Only the most recent result of each exercise determines its current state.
    by_id = {}
    for attempt in attempts:
        by_id.setdefault(int(attempt["exercise_id"]), attempt)
    passed = {i for i, attempt in by_id.items() if attempt["outcome"] in PASS}
    if len(passed) == 300:
        return {
            "action": "HOÀN THÀNH",
            "exercise_id": 300,
            "tone": "move",
            "reason": "Bạn đã đạt cả 300 bài.",
        }

    frontier = max(passed, default=latest_id)
    topic = next(
        ((lo, hi, name) for lo, hi, name in levels if lo <= frontier <= hi),
        None,
    )
    # Re-attempting an earlier mastered problem must not rewind the learning path.
    if topic is not None:
        lo, hi, name = topic
        pending = [
            i for i, attempt in by_id.items()
            if lo <= i < frontier and attempt["outcome"] in RETRY
        ]
        if pending:
            exercise_id = min(pending)
            return {
                "action": "ÔN BÀI CHƯA ĐẠT",
                "exercise_id": exercise_id,
                "tone": "practice",
                "reason": f"Bài {exercise_id} trong nhóm {name} đã từng nộp nhưng chưa đạt; cần củng cố trước khi tiến xa hơn.",
            }

    if frontier >= 300:
        undone = [i for i in range(1, 301) if i not in passed]
        return {
            "action": "ÔN BÀI BỎ QUA",
            "exercise_id": undone[0],
            "tone": "practice",
            "reason": f"Đã tới cuối lộ trình; còn {len(undone)} bài chưa đạt. Các bài nhảy qua không được tính là hoàn thành.",
        }

    next_id = frontier + 1
    while next_id <= 300 and next_id in passed:
        next_id += 1
    if next_id > 300:
        next_id = next(i for i in range(1, 301) if i not in passed)

    # Jump over AT MOST one fresh exercise, inside the current topic, only
    # after four *distinct*, recent, unassisted, clean and reasonably quick passes.
    # Local judge support is required for the checkpoint and the skipped task.
    if (
        topic is not None
        and latest["outcome"] == "independent"
        and latest_id == frontier
        and next_id == frontier + 1
        and frontier + 2 <= topic[1]
        and (frontier + 1) not in by_id
        and (frontier + 2) not in by_id
        and has_judge(frontier + 1)
        and has_judge(frontier + 2)
    ):
        unique = []
        seen = set()
        for row in attempts:
            idx = int(row["exercise_id"])
            if idx in seen or not topic[0] <= idx <= topic[1]:
                continue
            seen.add(idx)
            unique.append(row)
            if len(unique) == QUICK_CHECK_COUNT:
                break
        ids = [int(row["exercise_id"]) for row in unique]
        near = len(ids) == QUICK_CHECK_COUNT and all(
            0 < ids[j] - ids[j + 1] <= 2 for j in range(QUICK_CHECK_COUNT - 1)
        )
        clean = near and all(
            row["outcome"] == "independent"
            and int(row["compile_errors"]) == 0
            and 0 < int(row["duration_sec"]) <= MAX_CLEAN_SECONDS
            for row in unique
        )
        if clean:
            return {
                "action": "KIỂM TRA NHANH",
                "exercise_id": frontier + 2,
                "tone": "move",
                "reason": (
                    f"Bạn tự giải tốt {QUICK_CHECK_COUNT} bài gần đây. "
                    f"Thử bài {frontier + 2} để kiểm tra khả năng tiến nhanh; "
                    f"bài {frontier + 1} chỉ được tạm bỏ qua, chưa tính là đã đạt."
                ),
            }

    next_topic = next((name for lo, hi, name in levels if lo <= next_id <= hi), "")
    return {
        "action": "BÀI TIẾP THEO",
        "exercise_id": next_id,
        "tone": "move",
        "reason": f"Tiếp tục bài {next_id} trong nhóm {next_topic}. Chỉ nhảy bài khi có đủ lượt tự giải tốt và bài kiểm tra phù hợp.",
    }
