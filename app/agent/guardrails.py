from typing import Dict, Any, Tuple, Optional

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
