"""Community release regressions without copied source or private state."""
from __future__ import annotations
import hashlib
import json
from pathlib import Path
import unittest
import judge_packs
from problems import get_problem, public_problem

ROOT=Path(__file__).resolve().parent

class PublicReleaseTests(unittest.TestCase):
    def test_all_packs_sha_and_origin(self):
        approved=json.loads((ROOT/"verified-judge-packs"/"approved.json").read_text(encoding="utf-8"))["approved"]
        self.assertEqual(len(approved),270)
        for i in range(31,301):
            path=ROOT/"verified-judge-packs"/f"{i:03d}.json"
            blob=path.read_bytes()
            self.assertEqual(hashlib.sha256(blob).hexdigest(),approved[str(i)])
            pack,_=judge_packs.read_pack(i)
            self.assertEqual(pack["review_policy"],"public_generated_v1")
            self.assertEqual(pack["official_samples_count"],0)
            self.assertNotIn("source_evidence",pack)
            self.assertEqual(sum(t.get("origin")=="demonstration" for t in pack["tests"]),2)
    def test_all_300_accessible(self):
        for i in range(1,301):
            problem=get_problem(i)
            self.assertIsNotNone(problem,i)
            public=public_problem(problem)
            self.assertTrue(public["title"],i)
            self.assertGreaterEqual(len(public["samples"]),2)
    def test_no_private_source_capture(self):
        self.assertFalse((ROOT/"source-evidence").exists())
        self.assertFalse((ROOT/"data"/"study.db").exists() and (ROOT/"data"/"study.db").stat().st_size==0)
    def test_generated_demo_not_hidden(self):
        from judge import judge_cpp
        pack,_=judge_packs.read_pack(215)
        result=judge_cpp(pack["reference_cpp"],{"tests":pack["tests"]})
        self.assertTrue(result["passed"], result)
        self.assertFalse(result["results"][0]["hidden"])
        self.assertTrue(result["results"][2]["hidden"])
        self.assertIsNone(result["results"][2]["expected"])

if __name__=="__main__":
    unittest.main()
