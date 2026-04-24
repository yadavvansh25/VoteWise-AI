import pytest
from app.core.bias_filter import check_partisan_request, check_partisan_response, filter_response

def test_reject_partisan_request():
    assert check_partisan_request("Who should I vote for in the upcoming election?") == True
    assert check_partisan_request("Which party is better, BJP or Congress?") == True
    assert check_partisan_request("Suggest a candidate to vote for") == True

def test_allow_neutral_request():
    assert check_partisan_request("What are the registered parties in India?") == False
    assert check_partisan_request("How do I vote using EVM?") == False
    assert check_partisan_request("Where is my polling booth?") == False

def test_detect_partisan_response():
    assert check_partisan_response("I recommend voting for this party.") == True
    assert check_partisan_response("You should vote for them.") == True

def test_allow_neutral_response():
    assert check_partisan_response("The voting process is simple. First, register...") == False

def test_filter_response_partisan_request():
    # Should catch partisan user requests
    response, was_filtered = filter_response("Who should I vote for?", "I can't say.")
    assert was_filtered == True
    assert "neutral election education assistant" in response

def test_filter_response_partisan_system():
    # Should catch partisan AI responses even if request was neutral
    response, was_filtered = filter_response("Who are the candidates?", "You should vote for X.")
    assert was_filtered == True
    assert "neutral election education assistant" in response

def test_filter_response_neutral_all():
    # Should leave everything alone if neutral
    response, was_filtered = filter_response("How to register?", "Go to voters.eci.gov.in")
    assert was_filtered == False
    assert response == "Go to voters.eci.gov.in"

