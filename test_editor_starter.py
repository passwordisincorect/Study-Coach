"""Regression checks for the Study Coach C++ starter displayed in the editor."""
from pathlib import Path
import unittest

from problems import CPP_STARTER, get_problem

EXPECTED_STARTER = """#include <iostream>
#include <cmath>
#include <string>
#include <vector>

using namespace std;

int main() {
    // Viết code của bạn ở đây

    return 0;
}
"""


class EditorStarterTests(unittest.TestCase):
    def test_no_extra_blank_lines(self):
        self.assertEqual(CPP_STARTER, EXPECTED_STARTER)
        self.assertNotIn("\r", CPP_STARTER)
        self.assertNotIn("\n\n\n", CPP_STARTER)

    def test_all_300_problems_share_clean_starter(self):
        for number in range(1, 301):
            with self.subTest(number=number):
                self.assertEqual(get_problem(number)["starter"], EXPECTED_STARTER)

    def test_starter_source_uses_normal_line_endings(self):
        source = (Path(__file__).resolve().parent / "problems.py").read_bytes()
        self.assertNotIn(b"\r", source)


if __name__ == "__main__":
    unittest.main()
