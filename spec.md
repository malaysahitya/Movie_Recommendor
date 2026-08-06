# Movie Recommender Agent — System Specification (`spec.md`)

## 1. Project Overview
The **Movie Recommender Agent** is an end-to-end intelligent research and recommendation system designed to help users discover top-rated and critically acclaimed movies tailored precisely to their preference filters:
- **Genre**
- **Industry** (Hollywood, Bollywood, Anime)
- **Release Year Range** (e.g., 2010 to 2020)

The agent conducts deep, year-by-year movie research across international databases (e.g., TMDB, OMDb, Google Search) to synthesize a curated list of top movies for **each individual year** within the specified range, ranked by standard ratings (IMDb, TMDB, Rotten Tomatoes) and popularity metrics.

---

## 2. User Input Specification

The system accepts three mandatory inputs and optional fine-tuning controls:

### 2.1 Mandatory Inputs
1. **Genre (Dropdown Selection)**:
   - Available options: `Action`, `Comedy`, `Drama`, `Sci-Fi`, `Romance`, `Thriller`, `Horror`, `Animation / Anime`, `Mystery`, `Fantasy`, `Crime`, `Adventure`, `Documentary`, `Family`, `Historical / Period`.
   - Supports both single genre selection and multi-genre filtering.

2. **Industry / Category (Select Option)**:
   - Options:
     - `Hollywood` (Western cinema, global releases)
     - `Bollywood` (Indian Hindi cinema & major South Asian releases)
     - `Anime` (Japanese animation movies & films)

3. **Release Year Range (Range / Dual Input)**:
   - **Start Year**: e.g., `2010` (Minimum year allowed: 1950)
   - **End Year**: e.g., `2020` (Maximum year allowed: Current Year)
   - Validation Rule: `Start Year <= End Year`. If equal, agent researches that single specific year.

### 2.2 Selection & Execution Rules
- **Result Count**: Absolute **top 10 highest-rated movies overall** across the selected year range.
- **API Setup**: Uses **TMDB API Key** (for live movie metadata, ratings, and streaming providers) + **Gemini API Key** (for ADK agent reasoning and explanations). No Google Custom Search API keys required.
- **Industry Scope**:
  - `Hollywood`: English & global Western releases.
  - `Bollywood`: Hindi cinema & major Indian cross-regional blockbusters (e.g. *RRR*, *KGF*, *Baahubali*).
  - `Anime`: Japanese animation feature films.

---

## 3. Multi-Agent Architecture & Research Workflow (Google ADK)

The system is powered by a **4-Agent Pipeline** built on **Google Agent Development Kit (ADK)**:

```
┌────────────────────────────────────────────────────────────────────────┐
│                        User Interface Layer                            │
│  Web UI (Dropdowns + Industry Toggle + Year Range) & Terminal CLI      │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │ Inputs: Genre, Industry, Year Range
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│               1. Planner / Orchestrator Agent                          │
│   - Validates user inputs & enforces default 10-movie target           │
│   - Breaks year range into structured execution plan per year          │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │ Year-by-Year Research Directives
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│               2. Researcher Agent                                      │
│   - Executes live searches via TMDB Tool, OMDb Tool & Google Search    │
│   - Fetches raw candidate movies, posters, ratings & watch providers   │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │ Raw Candidate Datasets per Year
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│               3. Analysis Agent                                        │
│   - Computes Composite Quality Score (IMDb + TMDB + Popularity)        │
│   - Deduplicates & filters top 10 movies across the year range         │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │ Top 10 Ranked Movies Dataset
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│               4. Explainer Agent                                       │
│   - Synthesizes "Why this movie stands out for {Year}" reasoning       │
│   - Formats rich output cards with streaming badges & trailers         │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│                       Context & Memory DB (SQLite)                     │
│   Saves user queries, session state & past recommendations             │
└────────────────────────────────────────────────────────────────────────┘
```

---

## 4. Agent Tools & Schema Specifications

The agent utilizes dedicated, strongly-typed tools to interact with external movie databases and calculate rankings:

### Tool 1: `fetch_movies_by_year_and_genre`
- **Description**: Retrieves candidate movies for a specific year, industry, and genre.
- **Parameters**:
  - `year` (integer, required): Target release year (e.g., 2015).
  - `genre` (string, required): Standardized genre identifier.
  - `industry` (string, required): `hollywood`, `bollywood`, or `anime`.
  - `limit` (integer, optional): Maximum candidate pool size (default: 20).
- **Return Value**: JSON array of candidate movies containing raw titles, release dates, TMDB/IMDb IDs, genre matches, and baseline popularity scores.

### Tool 2: `get_movie_details_and_ratings`
- **Description**: Fetches detailed ratings (IMDb, TMDB, Rotten Tomatoes), vote counts, plot summary, director, top cast, and poster links.
- **Parameters**:
  - `movie_id` or `title` (string, required).
  - `release_year` (integer, required).
- **Return Value**: Structured metadata including weighted rating scores, poster URLs, trailer links, and streaming platform availability.

### Tool 3: `calculate_composite_score`
- **Description**: Normalizes ratings and vote counts into a unified quality score (0 - 100) combining critical acclaim and audience popularity.
- **Formula**: `Score = (Weighted_Rating * 0.7) + (Popularity_Percentile * 0.3)`.

---

## 5. User Output & Presentation Format

The agent presents results organized strictly **year by year** in collapsible cards or chronological timeline sections:

### Year Header (e.g., 📅 2015)
For each top movie selected for that year:
- **Title & Native Title** (e.g., for Anime/Bollywood)
- **Visuals**: Poster Image + Trailer Button
- **Key Metrics**:
  - ⭐ IMDb Score / TMDB Score / Rotten Tomatoes %
  - 🎭 Genre Tags
  - ⏱️ Runtime & Director
- **Plot Overview**: Concise 2-sentence synopsis.
- **Agent Analysis / Recommendation Reasoning**:
  - *"Why it's a top pick for 2015"*: Highlights awards, cultural impact, or why it matches the selected genre & industry.
- **Where to Watch**: Streaming availability badges (e.g., Netflix, Prime Video, Crunchyroll).

---

## 6. Technical Stack & File Structure

### Tech Stack
- **Framework**: **Google Agent Development Kit (ADK)** (`google-adk` / `adk-python`).
- **Backend & Logic**: Python 3.11+, FastAPI, Pydantic v2, `httpx` (async API client).
- **UI / Frontend**: HTML5, Vanilla JavaScript, CSS3 (Modern dark-mode glassmorphism theme, native dropdowns, year range sliders).
- **Database / Storage**: SQLite (local session and query history memory).
- **CLI**: Python `rich` library for terminal rendering.

### Repository Layout
```
Movie_Recommendor/
├── spec.md                   # System Specification (This file)
├── eval.md                   # Evaluation & Compliance Audit Document
├── README.md                 # Project Documentation & Setup Instructions
├── requirements.txt          # Dependencies
├── Dockerfile                # Container definition
├── .github/
│   └── workflows/
│       └── ci.yml            # Automated CI build & test workflow
├── app/
│   ├── __init__.py
│   ├── main.py               # FastAPI application entrypoint
│   ├── cli.py                # Command Line Interface
│   ├── config.py             # App settings & environment variables
│   ├── models/               # Pydantic schemas & database models
│   │   ├── request.py
│   │   └── movie.py
│   ├── agent/                # Core agent logic & orchestrator
│   │   ├── orchestrator.py   # Intent router & multi-year planner
│   │   ├── research.py       # Year-by-year research logic
│   │   └── memory.py         # Context & persistent memory
│   ├── tools/                # Dedicated agent tools
│   │   ├── tmdb_tool.py
│   │   └── scoring_tool.py
│   ├── telemetry/            # Observability & tracing loggers
│   │   └── tracer.py
│   └── static/               # Web frontend UI assets
│       ├── index.html
│       ├── style.css
│       └── app.js
└── tests/                    # Comprehensive test suite
    ├── test_tools.py
    ├── test_agent.py
    └── test_api.py
```
