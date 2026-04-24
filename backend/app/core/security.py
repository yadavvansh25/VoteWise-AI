"""
VoteWise AI — PII Detection & Redaction Engine
Detects and redacts personally identifiable information before sending to LLM.

Supports:
- Aadhaar numbers (12 digits, with Verhoeff checksum validation)
- EPIC / Voter ID numbers (3 alpha + 7 digits)
- PAN card numbers (5 alpha + 4 digits + 1 alpha)
- Indian phone numbers (10 digits, with optional +91 prefix)
- Email addresses
"""

import re
from typing import Tuple, List, Dict


# --- Verhoeff Checksum Tables (for Aadhaar validation) ---

_VERHOEFF_TABLE_D = [
    [0, 1, 2, 3, 4, 5, 6, 7, 8, 9],
    [1, 2, 3, 4, 0, 6, 7, 8, 9, 5],
    [2, 3, 4, 0, 1, 7, 8, 9, 5, 6],
    [3, 4, 0, 1, 2, 8, 9, 5, 6, 7],
    [4, 0, 1, 2, 3, 9, 5, 6, 7, 8],
    [5, 9, 8, 7, 6, 0, 4, 3, 2, 1],
    [6, 5, 9, 8, 7, 1, 0, 4, 3, 2],
    [7, 6, 5, 9, 8, 2, 1, 0, 4, 3],
    [8, 7, 6, 5, 9, 3, 2, 1, 0, 4],
    [9, 8, 7, 6, 5, 4, 3, 2, 1, 0],
]

_VERHOEFF_TABLE_P = [
    [0, 1, 2, 3, 4, 5, 6, 7, 8, 9],
    [1, 5, 7, 6, 2, 8, 3, 0, 9, 4],
    [5, 8, 0, 3, 7, 9, 6, 1, 4, 2],
    [8, 9, 1, 6, 0, 4, 3, 5, 2, 7],
    [9, 4, 5, 3, 1, 2, 6, 8, 7, 0],
    [4, 2, 8, 6, 5, 7, 3, 9, 0, 1],
    [2, 7, 9, 3, 8, 0, 6, 4, 1, 5],
    [7, 0, 4, 6, 9, 1, 3, 2, 5, 8],
]

_VERHOEFF_TABLE_INV = [0, 4, 3, 2, 1, 5, 6, 7, 8, 9]


def _verhoeff_checksum(number: str) -> bool:
    """Validate a number string using the Verhoeff checksum algorithm."""
    c = 0
    digits = [int(d) for d in reversed(number)]
    for i, digit in enumerate(digits):
        c = _VERHOEFF_TABLE_D[c][_VERHOEFF_TABLE_P[i % 8][digit]]
    return c == 0


# --- Regex Patterns ---

PII_PATTERNS: Dict[str, re.Pattern] = {
    "aadhaar": re.compile(r'\b[2-9]\d{3}[\s-]?\d{4}[\s-]?\d{4}\b'),
    "epic": re.compile(r'\b[A-Z]{3}\d{7}\b'),
    "pan": re.compile(r'\b[A-Z]{5}\d{4}[A-Z]\b'),
    "phone": re.compile(r'(?:\+91[\s-]?)?(?:\b[6-9]\d{9}\b)'),
    "email": re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'),
}

REDACTION_LABELS: Dict[str, str] = {
    "aadhaar": "[AADHAAR_REDACTED]",
    "epic": "[EPIC_REDACTED]",
    "pan": "[PAN_REDACTED]",
    "phone": "[PHONE_REDACTED]",
    "email": "[EMAIL_REDACTED]",
}


def _validate_aadhaar_candidate(match_text: str) -> bool:
    """
    Validate if a matched string is likely a real Aadhaar number.
    Uses Verhoeff checksum to reduce false positives.
    """
    digits_only = re.sub(r'[\s-]', '', match_text)
    if len(digits_only) != 12:
        return False
    if digits_only[0] == '0' or digits_only[0] == '1':
        return False
    return _verhoeff_checksum(digits_only)


def detect_pii(text: str) -> List[Dict[str, str]]:
    """
    Detect all PII occurrences in the given text.

    Returns:
        List of dicts with 'type', 'match', 'start', 'end' keys.
    """
    detections = []

    for pii_type, pattern in PII_PATTERNS.items():
        for match in pattern.finditer(text):
            matched_text = match.group()

            # Extra validation for Aadhaar to reduce false positives
            if pii_type == "aadhaar":
                if not _validate_aadhaar_candidate(matched_text):
                    continue

            detections.append({
                "type": pii_type,
                "match": matched_text,
                "start": match.start(),
                "end": match.end(),
            })

    return detections


def redact_pii(text: str) -> Tuple[str, List[str]]:
    """
    Detect and redact all PII from the given text.

    Args:
        text: Input text potentially containing PII.

    Returns:
        Tuple of (redacted_text, list_of_pii_types_found).
    """
    detections = detect_pii(text)

    if not detections:
        return text, []

    # Sort detections by position (reverse) to replace from end to start
    # This preserves character positions during replacement
    detections.sort(key=lambda d: d["start"], reverse=True)

    redacted = text
    pii_types_found = set()

    for detection in detections:
        pii_type = detection["type"]
        label = REDACTION_LABELS[pii_type]
        redacted = redacted[:detection["start"]] + label + redacted[detection["end"]:]
        pii_types_found.add(pii_type)

    return redacted, list(pii_types_found)


def get_pii_warning_message(pii_types: List[str], language: str = "en") -> str:
    """
    Generate a user-facing warning message about detected PII.

    Args:
        pii_types: List of PII types that were detected.
        language: Language code for the message.

    Returns:
        Localized warning message string.
    """
    type_names = {
        "en": {
            "aadhaar": "Aadhaar number",
            "epic": "Voter ID (EPIC) number",
            "pan": "PAN card number",
            "phone": "phone number",
            "email": "email address",
        },
        "hi": {
            "aadhaar": "आधार नंबर",
            "epic": "मतदाता पहचान (EPIC) नंबर",
            "pan": "पैन कार्ड नंबर",
            "phone": "फ़ोन नंबर",
            "email": "ईमेल पता",
        },
        "ta": {
            "aadhaar": "ஆதார் எண்",
            "epic": "வாக்காளர் அடையாள (EPIC) எண்",
            "pan": "PAN அட்டை எண்",
            "phone": "தொலைபேசி எண்",
            "email": "மின்னஞ்சல் முகவரி",
        },
    }

    messages = {
        "en": "⚠️ For your security, I've detected and removed the following personal information from your message: {types}. Your data is never stored or sent to external services.",
        "hi": "⚠️ आपकी सुरक्षा के लिए, मैंने आपके संदेश से निम्नलिखित व्यक्तिगत जानकारी का पता लगाया और हटा दिया है: {types}। आपका डेटा कभी भी संग्रहीत या बाहरी सेवाओं को नहीं भेजा जाता है।",
        "ta": "⚠️ உங்கள் பாதுகாப்பிற்காக, உங்கள் செய்தியிலிருந்து பின்வரும் தனிப்பட்ட தகவல்களை நான் கண்டறிந்து நீக்கியுள்ளேன்: {types}। உங்கள் தரவு ஒருபோதும் சேமிக்கப்படாது அல்லது வெளி சேவைகளுக்கு அனுப்பப்படாது.",
    }

    lang = language if language in type_names else "en"
    names = type_names[lang]
    detected_names = ", ".join(names.get(t, t) for t in pii_types)
    message_template = messages.get(lang, messages["en"])

    return message_template.format(types=detected_names)
