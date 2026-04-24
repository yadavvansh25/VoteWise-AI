import pytest
from app.core.intent import classify_intent
from app.models.schemas import Intent

def test_intent_registration():
    intent, score = classify_intent("How do I register for voter ID?")
    assert intent == Intent.REGISTRATION
    assert score > 0.0

def test_intent_candidate_info():
    intent, score = classify_intent("Who are the candidates running from Delhi?")
    assert intent == Intent.CANDIDATE_INFO
    assert score > 0.0

def test_intent_process_education():
    intent, score = classify_intent("How does the EVM work during polling?")
    assert intent == Intent.PROCESS_EDUCATION
    assert score > 0.0

def test_intent_greeting():
    intent, score = classify_intent("Hello VoteWise AI")
    assert intent == Intent.GREETING
    assert score > 0.0

def test_intent_general_fallback():
    intent, score = classify_intent("Tell me a random joke")
    assert intent == Intent.GENERAL
    
def test_intent_hindi_support():
    intent, score = classify_intent("मतदाता पंजीकरण कैसे करें?")
    assert intent == Intent.REGISTRATION
    assert score > 0.0
