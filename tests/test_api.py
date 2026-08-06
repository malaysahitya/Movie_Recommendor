import unittest
from app.models.request import RecommendationRequest

class TestRequestValidation(unittest.TestCase):
    def test_valid_request(self):
        req = RecommendationRequest(
            genre="Comedy",
            industry="Bollywood",
            start_year=2010,
            end_year=2020,
            limit=10
        )
        self.assertEqual(req.genre, "Comedy")
        self.assertEqual(req.industry, "Bollywood")

    def test_invalid_year_range(self):
        with self.assertRaises(ValueError):
            RecommendationRequest(
                genre="Action",
                industry="Hollywood",
                start_year=2020,
                end_year=2010
            )

if __name__ == "__main__":
    unittest.main()
