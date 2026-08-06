import time
from datetime import datetime
from typing import List, Dict, Any, Optional
from app.models.movie import TraceStep, TracePayload

class Tracer:
    """
    In-memory tracer recording step-by-step ADK agent actions, inputs, outputs, and latency.
    """
    def __init__(self, session_id: str):
        self.session_id = session_id
        self.steps: List[TraceStep] = []
        self._step_counter = 0

    def add_step(
        self,
        agent_name: str,
        action: str,
        inputs: Dict[str, Any],
        outputs: Dict[str, Any],
        latency_ms: float
    ):
        self._step_counter += 1
        step = TraceStep(
            step_number=self._step_counter,
            agent_name=agent_name,
            action=action,
            inputs=inputs,
            outputs=outputs,
            latency_ms=round(latency_ms, 2),
            timestamp=datetime.utcnow().isoformat()
        )
        self.steps.append(step)

    def get_payload(self) -> TracePayload:
        return TracePayload(
            session_id=self.session_id,
            total_steps=len(self.steps),
            steps=self.steps
        )

# Global tracer storage mapping session_id -> Tracer
_GLOBAL_TRACERS: Dict[str, Tracer] = {}

def get_tracer(session_id: str) -> Tracer:
    if session_id not in _GLOBAL_TRACERS:
        _GLOBAL_TRACERS[session_id] = Tracer(session_id)
    return _GLOBAL_TRACERS[session_id]
