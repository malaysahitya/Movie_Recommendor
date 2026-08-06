# Evaluation & Compliance Audit Document (`eval.md`)

## 1. Overview
This document tracks compliance against the **5 Core Evaluation Parameters** defined in the *AI in 5 Days Assessment Agent* benchmark. The goal is to ensure the **Movie Recommender Agent** meets every requirement without violations, targeting a maximum score of **95/95**.

---

## 2. Evaluation Parameters & Compliance Criteria

| # | Parameter | Target Score | Key Requirements | Verification Strategy |
|---|---|---|---|---|
| 1 | **Tool & Interface Design** | Max Points | - Clean user input interface (Genre dropdown, Industry selection, Year range slider/inputs).<br>- Strongly typed Pydantic tool schemas.<br>- Interactive Web UI + Terminal CLI.<br>- Error handling for invalid inputs or empty database results. | Unit tests for UI endpoints & Pydantic tool schemas; Manual UI inspection. |
| 2 | **Context & Memory** | Max Points | - Session state management.<br>- Persistent SQLite storage for past user queries, selected preferences, and search history.<br>- Context-aware recommendations preventing duplicate movie returns. | Integration tests for SQLite DB operations and session history retention across requests. |
| 3 | **Orchestration & Logic** | Max Points | - Built strictly with **Google Agent Development Kit (ADK)** (`adk-python`).<br>- Multi-year research planner splitting requests across individual years.<br>- Multi-criteria ranking algorithm (Rating + Popularity + Critical Acclaim).<br>- Fallback paths if external APIs fail or return sparse results. | Mock testing for API fallback branches & ADK multi-year loop execution logic. |
| 4 | **Observability & Tracing** | Max Points | - Structured step-by-step execution logs.<br>- Latency and token usage tracking.<br>- `/api/trace` endpoint exposing agent thought processes and tool execution trees to the user/evaluator. | Automated test checking tracer payload logs and trace endpoint responses. |
| 5 | **Infrastructure & CI/CD** | Max Points | - Root GitHub repository setup.<br>- Clear dependencies (`requirements.txt` / `pyproject.toml`).<br>- Docker containerization.<br>- Automated GitHub Actions CI workflow (linting + pytest).<br>- Complete `README.md` documentation. | CI pipeline execution (`pytest`, `flake8`/`ruff`, `docker build`). |

---

## 3. Active Violation Monitor & Safeguards

The development process will continuously enforce the following **Zero-Violation Safeguards**:

### 🚫 Violation Rule 1: Missing or Generic Tool Schemas
- **Requirement**: Every agent tool MUST have explicit Pydantic schemas with type annotations, parameter descriptions, and field constraints.
- **Violation Check**: Fail build if any tool lacks docstrings or schema validation.

### 🚫 Violation Rule 2: Non-Persistent Session State
- **Requirement**: User query history, preferred genres, and past recommendations must persist across sessions in SQLite.
- **Violation Check**: Test session re-hydration after server restart.

### 🚫 Violation Rule 3: Unhandled External API Failures
- **Requirement**: If external movie APIs (e.g. TMDB) hit rate limits, timeouts, or network errors, the agent MUST gracefully fall back to cached datasets or web search tools without crashing.
- **Violation Check**: Execute simulated network failure tests.

### 🚫 Violation Rule 4: Black-Box Agent Logic (Lack of Observability)
- **Requirement**: Every decision step, tool call, and research iteration must produce structured trace logs accessible via `/api/trace`.
- **Violation Check**: Verify `/api/trace` returns non-empty structured JSON execution logs for every recommendation run.

### 🚫 Violation Rule 5: Non-Standard Repository or Missing CI/CD
- **Requirement**: Project must be at the root of the Git repo, fully testable with a single command, containerized, and covered by CI actions.
- **Violation Check**: Verify local Docker build and GitHub Actions workflow file `.github/workflows/ci.yml`.

---

## 4. Continuous Compliance Audit Status Matrix

*This matrix is continuously updated during agent implementation.*

| Checklist Item | Parameter | Status | Verification Notes |
|---|---|---|---|
| User Input UI (Genre Dropdown, Industry, Year Range) | Tool & Interface | ✅ Completed | Web UI + CLI implemented |
| CLI Interface (`rich` library) | Tool & Interface | ✅ Completed | `app/cli.py` ready |
| Pydantic Tool Schemas (`tmdb_tool`, `scoring_tool`) | Tool & Interface | ✅ Completed | Pydantic v2 schemas complete |
| SQLite Session & Preference Memory | Context & Memory | ✅ Completed | `app/memory/sqlite_memory.py` |
| Multi-Year Orchestrator & Research Logic | Orchestration & Logic | ✅ Completed | Google ADK 4-Agent Pipeline |
| Scoring & Ranking Engine | Orchestration & Logic | ✅ Completed | Composite quality formula |
| Execution Telemetry & Tracing (`/api/trace`) | Observability & Tracing | ✅ Completed | `app/telemetry/tracer.py` |
| Dockerfile & `requirements.txt` | Infrastructure & CI/CD | ✅ Completed | Dockerfile ready |
| GitHub Actions CI (`ci.yml`) | Infrastructure & CI/CD | ✅ Completed | `.github/workflows/ci.yml` |
| Comprehensive `README.md` | Infrastructure & CI/CD | ✅ Completed | Setup guide & architecture docs |
