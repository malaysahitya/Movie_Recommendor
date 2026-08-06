import unittest
from app.models.request import RecommendationRequest
from app.agent.planner_agent import PlannerAgent
from app.agent.analysis_agent import AnalysisAgent

class TestAgents(unittest.TestCase):
    def test_planner_agent(self):
        planner = PlannerAgent()
        req = RecommendationRequest(
            genre="Action",
            industry="Hollywood",
            start_year=2015,
            end_year=2020,
            limit=10
        )
        plan = planner.plan_execution(req)
        self.assertEqual(plan["start_year"], 2015)
        self.assertEqual(plan["end_year"], 2020)
        self.assertEqual(len(plan["target_years"]), 6)

    def test_analysis_agent_top_10(self):
        analysis = AnalysisAgent()
        raw_candidates = [
            {"id": str(i), "title": f"Movie {i}", "rating": 7.0 + (i % 3), "vote_count": 1000 * i, "popularity_score": 10.0 * i}
            for i in range(1, 25)
        ]
        top_10 = analysis.rank_and_select_top_movies(raw_candidates, limit=10)
        self.assertEqual(len(top_10), 10)
        self.assertGreaterEqual(top_10[0]["composite_score"], top_10[1]["composite_score"])

if __name__ == "__main__":
    unittest.main()
