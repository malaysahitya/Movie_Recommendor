from typing import Dict, Any, Tuple, Optional, List

INAPPROPRIATE_KEYWORDS = ["explicit_nsw_flag", "malware", "hack", "illegal_substance"]
ADULT_GENRES = ["horror", "crime", "thriller"]

def validate_input_guardrail(genre: str, industry: str, start_year: int, end_year: int) -> Tuple[bool, str]:
    """
    Input Guardrail: Validates user input parameters against safety and boundary rules.
    """
    for kw in INAPPROPRIATE_KEYWORDS:
        if kw in genre.lower() or kw in industry.lower():
            return False, f"Inappropriate request flagged by input guardrail."

    if start_year < 1900 or end_year > 2026:
        return False, f"Year range must be between 1900 and 2026."

    if start_year > end_year:
        return False, f"Start year ({start_year}) cannot be greater than end year ({end_year})."

    return True, "Guardrail validation passed."

def model_router(task_type: str) -> str:
    """
    Model Routing: Directs tasks to the optimal Gemini LLM model based on complexity.
    """
    if task_type in ["planning", "research"]:
        return "gemini-1.5-flash"
    elif task_type in ["analysis", "explainer"]:
        return "gemini-1.5-pro"
    return "gemini-1.5-flash"

class HumanInTheLoopHook:
    """
    Human-In-The-Loop (HITL) Safety & Age Verification Hook:
    Detects 18+ adult themes (Horror, Crime, R-rated content) and halts pipeline execution
    until explicit human confirmation is received.
    """
    def __init__(self):
        self.pending_confirmations: Dict[str, Dict[str, Any]] = {}

    def check_18_plus_content(self, genre: str, movies: List[Dict[str, Any]]) -> bool:
        """Determines if the requested query or selected candidates contain 18+ adult content."""
        if genre.lower().strip() in ADULT_GENRES:
            return True
        for m in movies:
            g_ids = m.get("genre_ids", [])
            # 27 = Horror, 80 = Crime, 53 = Thriller
            if any(gid in [27, 80, 53] for gid in g_ids):
                return True
        return False

    def trigger_hitl_halt(self, session_id: str, genre: str, count_18_plus: int) -> Dict[str, Any]:
        """Halts execution and logs a pending HITL age confirmation request."""
        request_payload = {
            "session_id": session_id,
            "status": "AWAITING_18_PLUS_APPROVAL",
            "message": f"🔞 Age Verification Required: Top recommendations for '{genre}' contain 18+ adult themes ({count_18_plus} movies flagged). Explicit human confirmation required.",
            "requires_user_confirmation": True
        }
        self.pending_confirmations[session_id] = request_payload
        return request_payload

hitl_hook = HumanInTheLoopHook()
