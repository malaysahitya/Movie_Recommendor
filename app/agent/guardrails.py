from typing import Dict, Any, Tuple, Optional
import re

INAPPROPRIATE_KEYWORDS = ["explicit_nsw_flag", "malware", "hack", "illegal_substance"]

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
    Human-In-The-Loop (HITL) Confirmation Hook:
    Evaluates actions before execution and triggers explicit human approval for high-stakes or high-limit operations.
    """
    def __init__(self):
        self.pending_approvals: Dict[str, Dict[str, Any]] = {}

    def requires_approval(self, action_name: str, limit: int) -> bool:
        """Determines if an action requires explicit human confirmation (e.g., requesting > 20 recommendations)."""
        if limit > 20 or action_name in ["purge_cache", "bulk_query"]:
            return True
        return False

    def request_approval(self, session_id: str, action_name: str, details: Dict[str, Any]) -> Dict[str, Any]:
        """Registers a pending approval request for human confirmation."""
        request_data = {
            "session_id": session_id,
            "action": action_name,
            "details": details,
            "status": "pending_human_confirmation",
            "message": f"Action '{action_name}' requires human approval before proceeding."
        }
        self.pending_approvals[session_id] = request_data
        return request_data

    def confirm_approval(self, session_id: str, approved: bool) -> bool:
        """Processes human confirmation for a pending action."""
        if session_id in self.pending_approvals:
            self.pending_approvals[session_id]["status"] = "approved" if approved else "rejected"
            return approved
        return True

hitl_hook = HumanInTheLoopHook()
