"""
VoteWise AI — Political Bias Filter
Ensures the AI maintains political neutrality and refuses to take sides.
"""

import re
import logging
from typing import Tuple

logger = logging.getLogger("votewise.bias_filter")


# Patterns that indicate a user is asking for voting recommendations
PARTISAN_REQUEST_PATTERNS = [
    r"\bwho\s+should\s+i\s+vote\s+for\b",
    r"\bwhich\s+party\s+(is|should)\s+(best|better|good)\b",
    r"\bwhich\s+candidate\s+(is|should)\s+(best|better|good)\b",
    r"\bshould\s+i\s+vote\s+(for|against)\b",
    r"\bbest\s+(party|candidate)\s+(to|for)\s+vote\b",
    r"\bvote\s+for\s+whom\b",
    r"\brecommend\s+(a|any)\s+(party|candidate)\b",
    r"\bsuggest\s+(a|any)\s+(party|candidate)\b",
    r"\b(support|oppose)\s+(bjp|congress|aap|bsp|nda|india\s+alliance)\b",
    # Hindi
    r"\bकिसे\s+वोट\s+दें\b",
    r"\bकिस\s+पार्टी\s+को\s+वोट\b",
    r"\bसबसे\s+अच्छी\s+पार्टी\b",
    # Tamil
    r"\bயாருக்கு\s+வாக்களிக்க\b",
    r"\bசிறந்த\s+கட்சி\b",
]

# Patterns that indicate partisan language in AI responses
PARTISAN_RESPONSE_PATTERNS = [
    r"\byou\s+should\s+vote\s+for\b",
    r"\bi\s+recommend\s+(voting|you\s+vote)\b",
    r"\bthe\s+best\s+(party|candidate)\s+is\b",
    r"\b(bjp|congress|aap)\s+is\s+(better|best|superior)\b",
    r"\bdon'?t\s+vote\s+for\b",
    r"\bvote\s+against\b",
    r"\b(always|never)\s+vote\s+(for|against)\b",
]

NEUTRAL_REFUSAL_MESSAGES = {
    "en": (
        "🏛️ As a neutral election education assistant, I cannot recommend "
        "any specific party or candidate. My role is to provide factual, "
        "unbiased information about the electoral process.\n\n"
        "I can help you with:\n"
        "• **Understanding candidate manifestos** and their policy positions\n"
        "• **Finding factual information** about candidates in your constituency\n"
        "• **Learning about the voting process** and how to cast your vote\n\n"
        "Your vote is your personal choice — I'm here to help you make an informed decision!"
    ),
    "hi": (
        "🏛️ एक तटस्थ चुनाव शिक्षा सहायक के रूप में, मैं किसी विशेष पार्टी "
        "या उम्मीदवार की सिफारिश नहीं कर सकता। मेरी भूमिका चुनावी प्रक्रिया "
        "के बारे में तथ्यात्मक, निष्पक्ष जानकारी प्रदान करना है।\n\n"
        "मैं आपकी मदद कर सकता हूँ:\n"
        "• **उम्मीदवारों के घोषणापत्र** और उनकी नीतिगत स्थिति को समझने में\n"
        "• **आपके निर्वाचन क्षेत्र के उम्मीदवारों** के बारे में तथ्यात्मक जानकारी खोजने में\n"
        "• **मतदान प्रक्रिया** और अपना वोट कैसे डालें, यह सीखने में\n\n"
        "आपका वोट आपका व्यक्तिगत चुनाव है — मैं आपको सूचित निर्णय लेने में मदद करने के लिए यहाँ हूँ!"
    ),
    "ta": (
        "🏛️ ஒரு நடுநிலை தேர்தல் கல்வி உதவியாளராக, நான் எந்த குறிப்பிட்ட கட்சி "
        "அல்லது வேட்பாளரையும் பரிந்துரைக்க முடியாது। தேர்தல் செயல்முறை பற்றிய "
        "உண்மையான, சார்பற்ற தகவல்களை வழங்குவதே என் பணி.\n\n"
        "நான் உங்களுக்கு உதவ முடியும்:\n"
        "• **வேட்பாளர்களின் அறிக்கைகள்** மற்றும் அவர்களின் கொள்கை நிலைப்பாடுகளை புரிந்துகொள்ள\n"
        "• **உங்கள் தொகுதியின் வேட்பாளர்கள்** பற்றிய உண்மையான தகவல்களைக் கண்டறிய\n"
        "• **வாக்களிப்பு செயல்முறை** மற்றும் உங்கள் வாக்கை எவ்வாறு செலுத்துவது என்பதை அறிய\n\n"
        "உங்கள் வாக்கு உங்கள் தனிப்பட்ட தேர்வு — நீங்கள் தகவலறிந்த முடிவை எடுக்க நான் இங்கே இருக்கிறேன்!"
    ),
}


def check_partisan_request(message: str) -> bool:
    """
    Check if the user's message is asking for a voting recommendation.

    Args:
        message: The user's message.

    Returns:
        True if the message is a partisan request.
    """
    text = message.lower()
    for pattern in PARTISAN_REQUEST_PATTERNS:
        if re.search(pattern, text, re.IGNORECASE):
            logger.info("Partisan request detected: pattern=%s", pattern)
            return True
    return False


def check_partisan_response(response: str) -> bool:
    """
    Check if the AI response contains partisan language.

    Args:
        response: The AI's response text.

    Returns:
        True if partisan language is detected.
    """
    text = response.lower()
    for pattern in PARTISAN_RESPONSE_PATTERNS:
        if re.search(pattern, text, re.IGNORECASE):
            logger.warning("Partisan language detected in response: pattern=%s", pattern)
            return True
    return False


def filter_response(
    user_message: str,
    ai_response: str,
    language: str = "en"
) -> Tuple[str, bool]:
    """
    Apply the full bias filter pipeline.

    1. Check if the user is asking for a voting recommendation
    2. Check if the AI response contains partisan language

    Args:
        user_message: The user's original message.
        ai_response: The AI-generated response.
        language: Language code for the refusal message.

    Returns:
        Tuple of (filtered_response, was_filtered).
    """
    # Check if user is asking for partisan advice
    if check_partisan_request(user_message):
        return NEUTRAL_REFUSAL_MESSAGES.get(
            language, NEUTRAL_REFUSAL_MESSAGES["en"]
        ), True

    # Check if AI response is partisan
    if check_partisan_response(ai_response):
        logger.warning("AI response failed bias check, replacing with neutral response")
        return NEUTRAL_REFUSAL_MESSAGES.get(
            language, NEUTRAL_REFUSAL_MESSAGES["en"]
        ), True

    return ai_response, False
