import aiosqlite
import json
import os
from typing import List, Dict, Any, Optional

DB_PATH = "./movie_agent.db"

async def init_memory_db():
    """
    Initializes the SQLite database tables for session memory and query history.
    """
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

async def save_user_query(
    session_id: str,
    genre: str,
    industry: str,
    start_year: int,
    end_year: int,
    movie_ids: List[str]
):
    """
    Saves a completed user query and recommended movie IDs to persistent SQLite memory.
    """
    await init_memory_db()
    movie_ids_json = json.dumps(movie_ids)
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            INSERT INTO user_queries (session_id, genre, industry, start_year, end_year, recommended_movie_ids)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (session_id, genre, industry, start_year, end_year, movie_ids_json))
        await db.commit()

async def get_query_history(session_id: str) -> List[Dict[str, Any]]:
    """
    Retrieves previous query history for a given session.
    """
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
            history = []
            for row in rows:
                history.append({
                    "session_id": row["session_id"],
                    "genre": row["genre"],
                    "industry": row["industry"],
                    "start_year": row["start_year"],
                    "end_year": row["end_year"],
                    "recommended_movie_ids": json.loads(row["recommended_movie_ids"]),
                    "timestamp": row["timestamp"]
                })
            return history

async def is_duplicate_recommendation(session_id: str, movie_id: str) -> bool:
    """
    Checks if a movie has already been recommended in a given session to avoid duplicates.
    """
    history = await get_query_history(session_id)
    for entry in history:
        if movie_id in entry.get("recommended_movie_ids", []):
            return True
    return False
