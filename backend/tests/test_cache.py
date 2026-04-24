import pytest
import pytest_asyncio
import os
import sqlite3
from app.core.cache import get_cached_answer, cache_answer, seed_faqs, clear_expired
from app.models.database import get_database, close_database, reset_database

TEST_DB_PATH = "./test_votewise.db"

@pytest_asyncio.fixture(autouse=True)
async def setup_teardown():
    # Setup
    await reset_database()
    db = await get_database(TEST_DB_PATH)
    yield
    # Teardown
    await close_database()
    if os.path.exists(TEST_DB_PATH):
        os.remove(TEST_DB_PATH)

@pytest.mark.asyncio
async def test_cache_miss():
    answer = await get_cached_answer("Unknown question?", "en", TEST_DB_PATH)
    assert answer is None

@pytest.mark.asyncio
async def test_cache_hit():
    await cache_answer("What is EVM?", "Electronic Voting Machine", "en", "general", 60, TEST_DB_PATH)
    
    # Exact hit
    answer1 = await get_cached_answer("What is EVM?", "en", TEST_DB_PATH)
    assert answer1 == "Electronic Voting Machine"
    
    # Fuzzy hit (different casing, punctuation)
    answer2 = await get_cached_answer("WHAT IS EVM", "en", TEST_DB_PATH)
    assert answer2 == "Electronic Voting Machine"

@pytest.mark.asyncio
async def test_cache_language_isolation():
    await cache_answer("How to vote?", "Press button", "en", "general", 60, TEST_DB_PATH)
    await cache_answer("How to vote?", "बटन दबाएं", "hi", "general", 60, TEST_DB_PATH)
    
    answer_en = await get_cached_answer("How to vote?", "en", TEST_DB_PATH)
    answer_hi = await get_cached_answer("How to vote?", "hi", TEST_DB_PATH)
    
    assert answer_en == "Press button"
    assert answer_hi == "बटन दबाएं"

@pytest.mark.asyncio
async def test_cache_expiry():
    # Cache with 0 seconds TTL
    await cache_answer("Expired?", "Yes", "en", "general", -1, TEST_DB_PATH)
    
    answer = await get_cached_answer("Expired?", "en", TEST_DB_PATH)
    assert answer is None

@pytest.mark.asyncio
async def test_seed_faqs():
    faqs = [
        {"question": "Seed Q1", "answer": "Seed A1", "language": "en", "intent": "general"},
        {"question": "Seed Q2", "answer": "Seed A2", "language": "hi", "intent": "general"}
    ]
    count = await seed_faqs(faqs, TEST_DB_PATH)
    assert count == 2
    
    ans1 = await get_cached_answer("Seed Q1", "en", TEST_DB_PATH)
    assert ans1 == "Seed A1"
