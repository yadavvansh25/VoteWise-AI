"""
VoteWise AI — SQLite FAQ Cache
Caches common election FAQ responses to reduce Gemini API calls.
"""

import hashlib
import logging
from datetime import datetime, timedelta
from typing import Optional

import aiosqlite

from app.models.database import get_database
from app.config import get_settings

logger = logging.getLogger("votewise.cache")


def _normalize_question(question: str) -> str:
    """Normalize a question for consistent hashing."""
    normalized = question.lower().strip()
    # Remove extra whitespace
    normalized = " ".join(normalized.split())
    # Remove common punctuation
    for char in "?!.,;:'\"":
        normalized = normalized.replace(char, "")
    return normalized


def _hash_question(question: str) -> str:
    """Create a consistent hash for a question."""
    normalized = _normalize_question(question)
    return hashlib.sha256(normalized.encode("utf-8")).hexdigest()[:16]


async def get_cached_answer(
    question: str, language: str = "en", db_path: str = None
) -> Optional[str]:
    """
    Look up a cached answer for the given question.

    Args:
        question: The user's question.
        language: Language code.
        db_path: Optional database path override.

    Returns:
        Cached answer string if found and not expired, None otherwise.
    """
    question_hash = _hash_question(question)

    try:
        db = await get_database(db_path or get_settings().DATABASE_PATH)
        cursor = await db.execute(
            """
            SELECT answer, expires_at FROM faq_cache
            WHERE question_hash = ? AND language = ?
            ORDER BY created_at DESC
            LIMIT 1
            """,
            (question_hash, language),
        )
        row = await cursor.fetchone()

        if row is None:
            return None

        # Check if expired
        expires_at = datetime.fromisoformat(row[1])
        if datetime.now() > expires_at:
            # Clean up expired entry
            await db.execute(
                "DELETE FROM faq_cache WHERE question_hash = ? AND language = ?",
                (question_hash, language),
            )
            await db.commit()
            logger.info("Cache expired for question hash: %s", question_hash)
            return None

        # Increment hit count
        await db.execute(
            """
            UPDATE faq_cache SET hits = hits + 1
            WHERE question_hash = ? AND language = ?
            """,
            (question_hash, language),
        )
        await db.commit()

        logger.info("Cache hit for question hash: %s", question_hash)
        return row[0]

    except Exception as e:
        logger.error("Cache lookup failed: %s", str(e))
        return None


async def cache_answer(
    question: str,
    answer: str,
    language: str = "en",
    intent: str = "general",
    ttl_seconds: int = None,
    db_path: str = None,
) -> bool:
    """
    Store an answer in the cache.

    Args:
        question: The original question.
        answer: The answer to cache.
        language: Language code.
        intent: Detected intent category.
        ttl_seconds: Time-to-live in seconds (default from settings).
        db_path: Optional database path override.

    Returns:
        True if cached successfully, False otherwise.
    """
    settings = get_settings()
    ttl = ttl_seconds or settings.CACHE_TTL_SECONDS
    question_hash = _hash_question(question)
    expires_at = (datetime.now() + timedelta(seconds=ttl)).isoformat()

    try:
        db = await get_database(db_path or settings.DATABASE_PATH)
        await db.execute(
            """
            INSERT OR REPLACE INTO faq_cache
                (question_hash, question, answer, language, intent, hits, expires_at)
            VALUES (?, ?, ?, ?, ?, 0, ?)
            """,
            (question_hash, question, answer, language, intent, expires_at),
        )
        await db.commit()
        logger.info("Cached answer for question hash: %s", question_hash)
        return True

    except Exception as e:
        logger.error("Cache store failed: %s", str(e))
        return False


async def seed_faqs(faqs: list, db_path: str = None) -> int:
    """
    Seed the cache with pre-loaded FAQ entries.

    Args:
        faqs: List of dicts with 'question', 'answer', 'language', 'intent' keys.
        db_path: Optional database path override.

    Returns:
        Number of entries seeded.
    """
    count = 0
    for faq in faqs:
        # Validate required keys
        if not all(k in faq for k in ["question", "answer"]):
            logger.warning("Skipping invalid FAQ entry: %s", faq)
            continue

        success = await cache_answer(
            question=faq["question"],
            answer=faq["answer"],
            language=faq.get("language", "en"),
            intent=faq.get("intent", "general"),
            ttl_seconds=faq.get("ttl", 604800),  # 7 days default for seed data
            db_path=db_path,
        )
        if success:
            count += 1
    logger.info("Seeded %d FAQ entries", count)
    return count


async def clear_expired(db_path: str = None) -> int:
    """Remove all expired cache entries."""
    try:
        db = await get_database(db_path or get_settings().DATABASE_PATH)
        cursor = await db.execute(
            "DELETE FROM faq_cache WHERE expires_at < ?",
            (datetime.now().isoformat(),),
        )
        await db.commit()
        deleted = cursor.rowcount
        if deleted:
            logger.info("Cleared %d expired cache entries", deleted)
        return deleted
    except Exception as e:
        logger.error("Cache cleanup failed: %s", str(e))
        return 0
