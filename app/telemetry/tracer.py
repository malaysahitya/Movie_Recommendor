import time
import json
import re
from datetime import datetime
from typing import List, Dict, Any, Optional, Generator
from contextlib import contextmanager

import structlog
from opentelemetry import trace
from app.models.movie import TraceStep, TracePayload

# Initialize structlog JSON logger
structlog.configure(
    processors=[
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.JSONRenderer()
    ]
)
logger = structlog.get_logger()

# Initialize OpenTelemetry Tracer
otel_tracer = trace.get_tracer("movie_recommender_agent", "1.0.0")

# PII Redaction regex patterns
PII_PATTERNS = [
    (re.compile(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'), "[REDACTED_EMAIL]"),
    (re.compile(r'\b(?:\d{1,3}\.){3}\d{1,3}\b'), "[REDACTED_IP]"),
    (re.compile(r'(api_key|token|password|secret)=["\']?[a-zA-Z0-9_-]+["\']?', re.IGNORECASE), r'\1=[REDACTED_SECRET]'),
]

def redact_pii(data: Any) -> Any:
    """PII Redaction Mechanism: Scrubs sensitive personal identifiable information and API keys from telemetry logs."""
    if isinstance(data, str):
        cleaned = data
        for pattern, replacement in PII_PATTERNS:
            cleaned = pattern.sub(replacement, cleaned)
        return cleaned
    elif isinstance(data, dict):
        return {k: redact_pii(v) for k, v in data.items()}
    elif isinstance(data, list):
        return [redact_pii(v) for v in data]
    return data

class Tracer:
    """
    Observability & OpenTelemetry Tracer:
    Captures pre-execution INTENT before execution and post-execution OUTCOME after execution wrapping blocks in OpenTelemetry parent spans.
    """
    def __init__(self, session_id: str):
        self.session_id = redact_pii(session_id)
        self.steps: List[TraceStep] = []
        self._step_counter = 0

    @contextmanager
    def span(self, agent_name: str, action: str, inputs: Dict[str, Any]) -> Generator[None, None, None]:
        """
        OpenTelemetry Context Manager:
        1. Logs PRE_EXECUTION_INTENT before execution block
        2. Wraps block in an active OpenTelemetry trace span
        3. Logs POST_EXECUTION_OUTCOME after execution block
        """
        clean_inputs = redact_pii(inputs)
        logger.info(
            "PRE_EXECUTION_INTENT",
            session_id=self.session_id,
            agent=agent_name,
            action=action,
            inputs=clean_inputs
        )
        
        start_time = time.time()
        
        with otel_tracer.start_as_current_span(f"{agent_name}.{action}") as otel_span:
            otel_span.set_attribute("session.id", self.session_id)
            otel_span.set_attribute("agent.name", agent_name)
            otel_span.set_attribute("action.name", action)
            try:
                yield
            finally:
                latency_ms = (time.time() - start_time) * 1000
                otel_span.set_attribute("latency.ms", round(latency_ms, 2))

    def log_intent(self, agent_name: str, action: str, inputs: Dict[str, Any]):
        clean_inputs = redact_pii(inputs)
        logger.info(
            "PRE_EXECUTION_INTENT",
            session_id=self.session_id,
            agent=agent_name,
            action=action,
            inputs=clean_inputs
        )

    def log_outcome(
        self,
        agent_name: str,
        action: str,
        inputs: Dict[str, Any],
        outputs: Dict[str, Any],
        latency_ms: float
    ):
        self._step_counter += 1
        clean_inputs = redact_pii(inputs)
        clean_outputs = redact_pii(outputs)

        logger.info(
            "POST_EXECUTION_OUTCOME",
            session_id=self.session_id,
            step=self._step_counter,
            agent=agent_name,
            action=action,
            latency_ms=round(latency_ms, 2),
            outputs=clean_outputs
        )

        step = TraceStep(
            step_number=self._step_counter,
            agent_name=agent_name,
            action=action,
            inputs=clean_inputs,
            outputs=clean_outputs,
            latency_ms=round(latency_ms, 2),
            timestamp=datetime.utcnow().isoformat()
        )
        self.steps.append(step)

    def add_step(self, agent_name: str, action: str, inputs: Dict[str, Any], outputs: Dict[str, Any], latency_ms: float):
        self.log_outcome(agent_name, action, inputs, outputs, latency_ms)

    def get_payload(self) -> TracePayload:
        return TracePayload(
            session_id=self.session_id,
            total_steps=len(self.steps),
            steps=self.steps
        )

_GLOBAL_TRACERS: Dict[str, Tracer] = {}

def get_tracer(session_id: str) -> Tracer:
    if session_id not in _GLOBAL_TRACERS:
        _GLOBAL_TRACERS[session_id] = Tracer(session_id)
    return _GLOBAL_TRACERS[session_id]
