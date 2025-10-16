import unittest
from datetime import datetime

from burnout import (
    compute_off_hours_rate,
    compute_score_index,
    is_off_hours,
    normalize_author,
)


class TestGitAnalysis(unittest.TestCase):
    def test_normalize_author(self):
        self.assertEqual(normalize_author("Éric"), "eric")
        self.assertEqual(normalize_author("JOHN DOE"), "john doe")

    def test_is_off_hours(self):
        self.assertTrue(is_off_hours(datetime(2025, 10, 18, 7, 0)))  # samedi
        self.assertTrue(is_off_hours(datetime(2025, 10, 14, 21, 0)))  # après 20h
        self.assertFalse(is_off_hours(datetime(2025, 10, 14, 10, 0)))  # jour ouvré

    def test_compute_off_hours_rate(self):
        commits = [
            ("alice", datetime(2025, 10, 14, 21, 0)),
            ("Alice", datetime(2025, 10, 14, 10, 0)),
        ]
        total, off_hours, rate = compute_off_hours_rate(
            [(normalize_author(a), d) for a, d in commits]
        )
        self.assertEqual(total["alice"], 2)
        self.assertEqual(off_hours["alice"], 1)
        self.assertEqual(rate["alice"], 0.5)

    def test_compute_score_index(self):
        off_hours_commits = {"alice": 2, "bob": 1}
        scores = compute_score_index(off_hours_commits)
        self.assertAlmostEqual(scores["alice"], round(2 / 1.5, 2))
        self.assertAlmostEqual(scores["bob"], round(1 / 1.5, 2))


if __name__ == "__main__":
    unittest.main()
