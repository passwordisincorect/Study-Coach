"""Regression tests for source-site AC reporting and adaptive routing."""
import sqlite3
import unittest

from source_progress import SourceProgressError, record_source_ac
from progression import choose_next


class SourceProgressTests(unittest.TestCase):
    def setUp(self):
        self.conn = sqlite3.connect(":memory:")
        self.conn.row_factory = sqlite3.Row
        self.conn.executescript(
            "CREATE TABLE attempts (id INTEGER PRIMARY KEY AUTOINCREMENT, "
            "exercise_id INTEGER,outcome TEXT,duration_sec INTEGER,"
            "compile_errors INTEGER,notes TEXT,created_at TEXT);"
            "CREATE TABLE meta (key TEXT PRIMARY KEY,value TEXT);"
        )

    def tearDown(self):
        self.conn.close()

    def record(self, ex=31, confirmed=True, local=False):
        return record_source_ac(
            self.conn, ex, confirmed, lambda i: local, lambda: "2026-10-10T00:00:00Z"
        )

    def count(self):
        return self.conn.execute("SELECT COUNT(*) FROM attempts").fetchone()[0]

    def test_verified_user_attestation_recorded(self):
        self.assertTrue(self.record())
        row = self.conn.execute("SELECT * FROM attempts").fetchone()
        self.assertEqual(row["outcome"], "external_pass")
        self.assertIn("tự xác nhận", row["notes"])
        self.assertEqual(self.conn.execute(
            "SELECT value FROM meta WHERE key='active_exercise_id'"
        ).fetchone()[0], "31")

    def test_no_confirmation_no_changes(self):
        for confirmed in (False, "true", None, 1):
            with self.assertRaises(SourceProgressError):
                self.record(confirmed=confirmed)
        self.assertEqual(self.count(), 0)

    def test_invalid_id_and_local_judge_rejected(self):
        for number in (0, 301, -1, True, "31"):
            with self.assertRaises(SourceProgressError):
                self.record(ex=number)
        with self.assertRaises(SourceProgressError):
            self.record(ex=30, local=True)
        self.assertEqual(self.count(), 0)

    def test_duplicate_click_idempotent(self):
        self.assertTrue(self.record())
        self.assertFalse(self.record())
        self.assertEqual(self.count(), 1)

    def test_failure_then_source_ac(self):
        self.conn.execute(
            "INSERT INTO attempts(exercise_id,outcome,duration_sec,compile_errors,notes,created_at)"
            " VALUES(31,'failed',12,0,'','')"
        )
        self.assertTrue(self.record())
        self.assertEqual(self.count(), 2)

    def test_external_ac_moves_forward_but_no_skip(self):
        for ex in (31, 32, 33, 34):
            self.record(ex=ex)
        rec = choose_next(
            self.conn, [(31, 60, "Điều kiện")], lambda i: True
        )
        self.assertEqual(rec["exercise_id"], 35)
        self.assertEqual(rec["action"], "BÀI TIẾP THEO")


if __name__ == "__main__":
    unittest.main()
