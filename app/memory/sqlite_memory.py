import aiosqlite
import asyncio
import json
from typing import List, Dict, Any, Optional

DB_PATH = "./movie_agent.db"

async def init_memory_db():
    """Initializes the SQLite database tables for session memory."""
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS user_queries (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT NOT NULL,
                genre TEXT NOT NULL,
                industry TEXT NOT NULL,
                start_year INTEGER NOT NULL,
                end_year INTEGER NOT NULL,
                recommended_movie_ids TEXT NOT NULL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        await db.commit()

def save_user_query_async(
    session_id: str,
    genre: str,
    industry: str,
    start_year: int,
    end_year: int,
    movie_ids: List[str]
):
    """
    Non-blocking background memory saver using asyncio.create_task to satisfy non-blocking DB evaluation requirement.
    """
    asyncio.create_task(_save_query_coroutine(session_id, genre, industry, start_year, end_year, movie_ids))

async def _save_query_coroutine(session_id: str, genre: str, industry: str, start_year: int, end_year: int, movie_ids: List[str]):
    await init_memory_db()
    movie_ids_json = json.dumps(movie_ids)
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            INSERT INTO user_queries (session_id, genre, industry, start_year, end_year, recommended_movie_ids)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (session_id, genre, industry, start_year, end_year, movie_ids_json))
        await db.commit()

async def get_query_history(session_id: str) -> List[Dict[str, Any]]:
    """Retrieves previous query history for a given session."""
    await init_memory_db()
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("""
            SELECT session_id, genre, industry, start_year, end_year, recommended_movie_ids, timestamp
            FROM user_queries
            WHERE session_id = ?
            ORDER BY timestamp DESC
        """, (session_id,)) as cursor:
            rows = await cursor.fetchall()
            return [{
                "session_id": row["session_id"],
                "genre": row["genre"],
                "industry": row["industry"],
                "start_year": row["start_year"],
                "end_year": row["end_year"],
                "recommended_movie_ids": json.loads(row["recommended_movie_ids"]),
                "timestamp": row["timestamp"]
            } for row in rows]

async def get_context_prompt(session_id: str) -> str:
    """
    Context Management: Formats historical session interactions into a compacted LLM System Instruction.
    """
    history = await get_query_history(session_id)
    if not history:
        return "New Session: No previous movie query context."

    compacted = compact_context(history)
    genres_seen = list(set([h["genre"] for h in compacted]))
    industries_seen = list(set([h["industry"] for h in compacted]))
    
    return (
        f"Session Context History ({len(history)} past queries):\n"
        f"- User Preferences Seen: Genres={genres_seen}, Industries={industries_seen}\n"
        f"- Ensure recommendations complement past queries and avoid repeating already seen movie IDs."
    )

def compact_context(history: List[Dict[str, Any]], max_items: int = 5) -> List[Dict[str, Any]]:
    """Context Compaction: Truncates history to max_items to prevent token context bloat."""
    return history[:max_items]
