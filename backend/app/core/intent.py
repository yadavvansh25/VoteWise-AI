"""
VoteWise AI — Intent Classification
Classifies user messages into election-related intent categories.
"""

import re
from typing import Tuple
from app.models.schemas import Intent


# Intent keyword mappings with weights
INTENT_KEYWORDS: dict[Intent, list[dict]] = {
    Intent.REGISTRATION: [
        {"pattern": r"\b(register|registration|enroll|enrol)\b", "weight": 3},
        {"pattern": r"\b(voter\s*id|voter\s*card|epic)\b", "weight": 3},
        {"pattern": r"\b(form\s*6|form\s*6a|form\s*8)\b", "weight": 4},
        {"pattern": r"\b(eligib|eligible|eligibility)\b", "weight": 3},
        {"pattern": r"\b(apply|application)\b", "weight": 1},
        {"pattern": r"\b(age|18\s*years|citizen|residency)\b", "weight": 2},
        {"pattern": r"\b(electoral\s*roll|voter\s*list)\b", "weight": 3},
        {"pattern": r"\b(voter\s*portal|voter\s*helpline)\b", "weight": 3},
        {"pattern": r"\b(blo|booth\s*level\s*officer)\b", "weight": 2},
        {"pattern": r"\b(ero|electoral\s*registration)\b", "weight": 3},
        # Hindi
        {"pattern": r"\b(पंजीकरण|मतदाता|पहचान\s*पत्र)\b", "weight": 3},
        {"pattern": r"\b(पात्रता|योग्यता|आवेदन)\b", "weight": 2},
        # Tamil
        {"pattern": r"\b(பதிவு|வாக்காளர்|அடையாள\s*அட்டை)\b", "weight": 3},
    ],
    Intent.CANDIDATE_INFO: [
        {"pattern": r"\b(candidate|candidates|party|parties)\b", "weight": 3},
        {"pattern": r"\b(bjp|congress|aap|inc|nda|india\s*alliance)\b", "weight": 3},
        {"pattern": r"\b(manifesto|promise|agenda|policy|policies)\b", "weight": 2},
        {"pattern": r"\b(leader|minister|mp|mla|mps|mlas)\b", "weight": 2},
        {"pattern": r"\b(constituency|seat|election\s*result)\b", "weight": 2},
        {"pattern": r"\b(lok\s*sabha|rajya\s*sabha|vidhan\s*sabha)\b", "weight": 3},
        {"pattern": r"\b(who\s*is\s*running|who\s*is\s*contesting)\b", "weight": 4},
        # Hindi
        {"pattern": r"\b(उम्मीदवार|पार्टी|दल|नेता)\b", "weight": 3},
        {"pattern": r"\b(चुनाव\s*परिणाम|घोषणापत्र)\b", "weight": 3},
        # Tamil
        {"pattern": r"\b(வேட்பாளர்|கட்சி|தேர்தல்\s*முடிவு)\b", "weight": 3},
    ],
    Intent.PROCESS_EDUCATION: [
        {"pattern": r"\b(evm|electronic\s*voting\s*machine)\b", "weight": 4},
        {"pattern": r"\b(vvpat|paper\s*audit\s*trail)\b", "weight": 4},
        {"pattern": r"\b(polling\s*booth|polling\s*station)\b", "weight": 3},
        {"pattern": r"\b(how\s*to\s*vote|voting\s*process|cast\s*vote)\b", "weight": 4},
        {"pattern": r"\b(ballot|button|press)\b", "weight": 1},
        {"pattern": r"\b(election\s*day|voting\s*day)\b", "weight": 2},
        {"pattern": r"\b(booth\s*finder|find\s*my\s*booth)\b", "weight": 4},
        {"pattern": r"\b(control\s*unit|ballot\s*unit)\b", "weight": 3},
        {"pattern": r"\b(ink|indelible\s*ink)\b", "weight": 2},
        {"pattern": r"\b(counting|result|results)\b", "weight": 1},
        {"pattern": r"\b(step\s*by\s*step|procedure|process)\b", "weight": 1},
        # Hindi
        {"pattern": r"\b(मतदान|ईवीएम|वीवीपैट|मतदान\s*केंद्र)\b", "weight": 3},
        {"pattern": r"\b(कैसे\s*वोट\s*करें|मतदान\s*प्रक्रिया)\b", "weight": 4},
        # Tamil
        {"pattern": r"\b(வாக்களிப்பு|வாக்குச்சாவடி)\b", "weight": 3},
    ],
    Intent.GREETING: [
        {"pattern": r"\b(hi|hello|hey|namaste|vanakkam)\b", "weight": 3},
        {"pattern": r"\b(good\s*(morning|afternoon|evening))\b", "weight": 3},
        {"pattern": r"\b(thank|thanks|dhanyavaad|nandri)\b", "weight": 2},
        {"pattern": r"\b(नमस्ते|नमस्कार|धन्यवाद)\b", "weight": 3},
        {"pattern": r"\b(வணக்கம்|நன்றி)\b", "weight": 3},
    ],
}


def classify_intent(message: str) -> Tuple[Intent, float]:
    """
    Classify a user message into an intent category.

    Uses weighted keyword matching to determine the most likely intent.

    Args:
        message: The user's message text.

    Returns:
        Tuple of (Intent, confidence_score).
        Confidence is normalized between 0.0 and 1.0.
    """
    scores: dict[Intent, int] = {intent: 0 for intent in Intent}
    text = message.lower()

    for intent, patterns in INTENT_KEYWORDS.items():
        for entry in patterns:
            matches = re.findall(entry["pattern"], text, re.IGNORECASE)
            if matches:
                scores[intent] += len(matches) * entry["weight"]

    total_score = sum(scores.values())
    if total_score == 0:
        return Intent.GENERAL, 0.0

    best_intent = max(scores, key=scores.get)
    best_score = scores[best_intent]

    # Normalize confidence: ratio of best score to total
    confidence = min(best_score / max(total_score, 1), 1.0)

    # If confidence is too low, default to general
    if confidence < 0.2:
        return Intent.GENERAL, confidence

    return best_intent, round(confidence, 2)
