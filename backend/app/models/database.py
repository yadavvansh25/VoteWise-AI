"""
VoteWise AI — Database Models & Connection
SQLite async connection management for FAQ caching.
"""

import aiosqlite
import os
from typing import Optional

_db_connection: Optional[aiosqlite.Connection] = None


SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS faq_cache (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    question_hash TEXT NOT NULL,
    question TEXT NOT NULL,
    answer TEXT NOT NULL,
    language TEXT NOT NULL DEFAULT 'en',
    intent TEXT DEFAULT 'general',
    hits INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP NOT NULL,
    UNIQUE(question_hash, language)
);

CREATE INDEX IF NOT EXISTS idx_faq_hash_lang
    ON faq_cache(question_hash, language);

CREATE INDEX IF NOT EXISTS idx_faq_expires
    ON faq_cache(expires_at);
"""


async def get_database(db_path: str = "./votewise.db") -> aiosqlite.Connection:
    """Get or create the database connection."""
    global _db_connection
    if _db_connection is None:
        _db_connection = await aiosqlite.connect(db_path)
        _db_connection.row_factory = aiosqlite.Row
        await _db_connection.executescript(SCHEMA_SQL)
        await _db_connection.commit()
    return _db_connection


async def close_database():
    """Close the database connection."""
    global _db_connection
    if _db_connection is not None:
        await _db_connection.close()
        _db_connection = None


async def reset_database():
    """Reset the database connection (for testing)."""
    global _db_connection
    _db_connection = None
