import pytest
from unittest.mock import patch
from app.core.security import detect_pii, redact_pii

@patch('app.core.security._verhoeff_checksum', return_value=True)
def test_aadhaar_detection_with_spaces(mock_verhoeff):
    text = "My aadhaar is 2345 6789 1234. Please check."
    detections = detect_pii(text)
    assert len(detections) == 1
    assert detections[0]["type"] == "aadhaar"
    assert detections[0]["match"] == "2345 6789 1234"

@patch('app.core.security._verhoeff_checksum', return_value=True)
def test_aadhaar_detection_without_spaces(mock_verhoeff):
    text = "My aadhaar is 234567891234."
    detections = detect_pii(text)
    assert len(detections) == 1
    assert detections[0]["type"] == "aadhaar"
    assert detections[0]["match"] == "234567891234"

def test_aadhaar_false_positive_rejection():
    # 12 digits starting with 1 should be rejected
    text = "My number is 1345 6789 1234."
    detections = detect_pii(text)
    assert len(detections) == 0

def test_epic_detection():
    # EPIC is 3 letters followed by 7 digits
    text = "My voter ID is ABC1234567."
    detections = detect_pii(text)
    assert len(detections) == 1
    assert detections[0]["type"] == "epic"
    assert detections[0]["match"] == "ABC1234567"

def test_pan_detection():
    # PAN is 5 letters, 4 digits, 1 letter
    text = "My PAN card is ABCDE1234F."
    detections = detect_pii(text)
    assert len(detections) == 1
    assert detections[0]["type"] == "pan"
    assert detections[0]["match"] == "ABCDE1234F"

def test_phone_detection():
    text = "Call me at +91 9876543210 or 8765432109."
    detections = detect_pii(text)
    assert len(detections) == 2
    assert detections[0]["type"] == "phone"

def test_email_detection():
    text = "Email me at test.user@example.com."
    detections = detect_pii(text)
    assert len(detections) == 1
    assert detections[0]["type"] == "email"

@patch('app.core.security._verhoeff_checksum', return_value=True)
def test_redact_pii(mock_verhoeff):
    text = "My name is John, Aadhaar 2345 6789 1234, and email john@example.com."
    redacted, types = redact_pii(text)
    assert "[AADHAAR_REDACTED]" in redacted
    assert "[EMAIL_REDACTED]" in redacted
    assert "2345 6789 1234" not in redacted
    assert "john@example.com" not in redacted
    assert set(types) == {"aadhaar", "email"}

def test_no_pii_clean_text():
    text = "How do I register to vote in Delhi?"
    redacted, types = redact_pii(text)
    assert redacted == text
    assert len(types) == 0
