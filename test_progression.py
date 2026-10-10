"""Regression tests for adaptive route decisions (no live database writes)."""
import sqlite3
import unittest

from progression import choose_next

TOPICS = [(1, 30, "Cơ bản"), (31, 60, "Điều kiện"), (61, 300, "Khác")]


class RouteTests(unittest.TestCase):
    def setUp(self):
        self.conn = sqlite3.connect(":memory:")
        self.conn.row_factory = sqlite3.Row
        self.conn.execute(
            "CREATE TABLE attempts (id INTEGER PRIMARY KEY AUTOINCREMENT, "
            "exercise_id INTEGER, outcome TEXT, duration_sec INTEGER, compile_errors INTEGER)"
        )

    def tearDown(self):
        self.conn.close()

    def record(self, ex, outcome="independent", seconds=100, errors=0):
        self.conn.execute(
            "INSERT INTO attempts(exercise_id,outcome,duration_sec,compile_errors) VALUES(?,?,?,?)",
            (ex, outcome, seconds, errors),
        )

    def next(self, judge=lambda x: 1 <= x <= 30):
        return choose_next(self.conn, TOPICS, judge)

    def test_start(self):
        self.assertEqual(self.next()["exercise_id"], 1)

    def test_failure_retries_current(self):
        self.record(25, "failed")
        self.assertEqual(self.next()["action"], "SỬA BÀI")
        self.assertEqual(self.next()["exercise_id"], 25)

    def test_hint_does_not_accelerate(self):
        for ex in (22, 23, 24):
            self.record(ex)
        self.record(25, "hint")
        self.assertEqual(self.next()["exercise_id"], 26)

    def test_four_distinct_clean_passes_jump_only_one(self):
        for ex in (22, 23, 24, 25):
            self.record(ex)
        got = self.next()
        self.assertEqual((got["action"], got["exercise_id"]), ("KIỂM TRA NHANH", 27))
        self.assertIn("chưa tính", got["reason"])

    def test_jumps_continue_conservatively(self):
        for ex in (22, 23, 24, 25, 27):
            self.record(ex)
        self.assertEqual(self.next()["exercise_id"], 29)

    def test_repeated_same_exercise_is_not_evidence(self):
        for _ in range(4):
            self.record(25)
        self.assertEqual(self.next()["exercise_id"], 26)

    def test_long_duration_disables_skip(self):
        for ex in (22, 23, 24):
            self.record(ex)
        self.record(25, seconds=620)
        self.assertEqual(self.next()["exercise_id"], 26)

    def test_compile_error_disables_skip(self):
        for ex in (22, 23, 24):
            self.record(ex)
        self.record(25, errors=1)
        self.assertEqual(self.next()["exercise_id"], 26)

    def test_absent_judge_disables_skip(self):
        for ex in (22, 23, 24, 25):
            self.record(ex)
        self.assertEqual(self.next(judge=lambda x: x == 26)["exercise_id"], 26)

    def test_never_skip_attempted_exercise(self):
        self.record(26, "failed")
        for ex in (22, 23, 24, 25):
            self.record(ex)
        self.assertEqual(self.next()["exercise_id"], 26)

    def test_topic_boundary_does_not_skip(self):
        for ex in (27, 28, 29, 30):
            self.record(ex)
        self.assertEqual(self.next()["exercise_id"], 31)

    def test_reviewing_older_pass_does_not_rewind(self):
        for ex in (22, 23, 24, 25):
            self.record(ex)
        self.record(7)
        self.assertEqual(self.next()["exercise_id"], 26)

    def test_latest_failure_even_if_previously_passed(self):
        self.record(25)
        self.record(25, "failed")
        self.assertEqual(self.next()["exercise_id"], 25)

    def test_end_with_skipped_exercises_is_not_false_completion(self):
        self.record(300)
        got = self.next()
        self.assertEqual(got["action"], "ÔN BÀI BỎ QUA")
        self.assertEqual(got["exercise_id"], 1)

    def test_all_passed(self):
        for ex in range(1, 301):
            self.record(ex)
        self.assertEqual(self.next()["action"], "HOÀN THÀNH")


if __name__ == "__main__":
    unittest.main()
