import unittest
from app.tools.scoring_tool import calculate_composite_score

class TestScoringTool(unittest.TestCase):
    def test_calculate_composite_score(self):
        score = calculate_composite_score(rating=8.5, vote_count=50000, popularity=150.0)
        self.assertTrue(0.0 <= score <= 100.0)
        self.assertTrue(score > 50.0)

    def test_calculate_composite_score_zero(self):
        score = calculate_composite_score(rating=0.0, vote_count=0, popularity=0.0)
        self.assertEqual(score, 0.0)

if __name__ == "__main__":
    unittest.main()
