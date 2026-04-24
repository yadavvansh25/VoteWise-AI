"""
VoteWise AI — Static Election Knowledge Base
Pre-loaded election education content used to enrich Gemini prompts.
"""

ELECTION_KNOWLEDGE = {
    "registration": {
        "eligibility": {
            "en": {
                "title": "Voter Eligibility Criteria",
                "content": """
To register as a voter in India, you must meet ALL of the following criteria:

1. **Citizenship**: You must be an Indian citizen
2. **Age**: You must be at least 18 years old on the qualifying date (January 1, April 1, July 1, or October 1 of the year)
3. **Residency**: You must be an ordinary resident of the constituency where you wish to enroll
4. **Sound Mind**: You must not have been declared of unsound mind by a competent court
5. **No Disqualification**: You must not be disqualified under any law relating to corrupt practices or election offences

NRI citizens can also register using Form 6A.
"""
            }
        },
        "forms": {
            "en": {
                "title": "Registration Forms Guide",
                "content": """
**Form 6** — New Voter Registration
- For first-time voters or those not on any electoral roll
- Required documents: Age proof, address proof, passport-size photo
- Submit online at voters.eci.gov.in or via the Voter Helpline App

**Form 6A** — Overseas (NRI) Voter Registration
- For Indian citizens living abroad
- Requires valid Indian passport
- Register at the constituency of your Indian passport address

**Form 8** — Corrections & Updates
- For shifting of residence between constituencies
- For correction of entries in voter ID
- For replacement of damaged/lost EPIC card
- For marking as a Person with Disability (PwD)

**Form 7** — Objection to Inclusion
- To object to someone's name being on the electoral roll
"""
            }
        },
        "portal_steps": {
            "en": {
                "title": "Online Registration Steps",
                "content": """
Step-by-step guide to register online:

1. Visit **voters.eci.gov.in** (National Voters' Service Portal)
2. Click on **"Register as a New Voter"**
3. Select **Form 6** for new registration
4. Fill in personal details:
   - Full name, Date of birth, Gender
   - Father's/Mother's/Husband's name
   - Current address with PIN code
5. Upload documents:
   - Passport-size photograph
   - Age proof (birth certificate, Class 10 marksheet, passport)
   - Address proof (Aadhaar, utility bill, bank passbook)
6. Choose your **Assembly Constituency** (auto-detected from address)
7. Submit and note your **Reference ID**
8. Track status using the Reference ID on the same portal
9. Your BLO (Booth Level Officer) may visit for verification
10. Once approved, your EPIC card will be generated
"""
            }
        }
    },
    "evm_process": {
        "en": {
            "title": "How to Use the EVM (Electronic Voting Machine)",
            "content": """
The EVM consists of two units:

**Ballot Unit (BU)** — Placed inside the voting compartment
- Contains a list of candidates with their names, party symbols, and blue voting buttons
- The voter presses the button next to their chosen candidate

**Control Unit (CU)** — Operated by the Presiding Officer
- Records and stores votes
- Has a "Ballot" button that the officer presses to allow each voter to cast their vote
- Ensures only ONE vote can be cast per ballot activation

**Step-by-step voting process:**
1. Go to your assigned polling booth on election day
2. Present your Voter ID (EPIC) or any approved ID at the verification desk
3. Your name is checked against the electoral roll
4. Indelible ink is applied to your left index finger
5. The Presiding Officer activates the ballot on the Control Unit
6. Enter the voting compartment (fully private)
7. Find your chosen candidate on the Ballot Unit
8. Press the **blue button** next to their name and symbol
9. A beep sound confirms your vote has been recorded
10. The VVPAT slip is printed (see below)
11. Exit the voting compartment
"""
        }
    },
    "vvpat": {
        "en": {
            "title": "VVPAT (Voter Verifiable Paper Audit Trail)",
            "content": """
The VVPAT machine is attached to the EVM to provide an independent verification system:

**How it works:**
1. After you press the button on the Ballot Unit, the VVPAT generates a paper slip
2. The slip shows the **candidate's name** and **party symbol** you voted for
3. The slip is visible through a **transparent window** for **7 seconds**
4. You can verify that your vote was correctly recorded
5. After 7 seconds, the slip is automatically **cut and dropped** into a sealed box
6. You CANNOT touch or take the slip

**Important:**
- If the printed slip does not match your intended vote, you can file a complaint with the Presiding Officer
- VVPAT slips from randomly selected booths are matched with EVM results during counting
- This provides an additional layer of transparency and trust in the voting process
"""
        }
    },
    "polling_booth": {
        "en": {
            "title": "Finding Your Polling Booth",
            "content": """
**Online Methods:**
1. Visit **electoralsearch.eci.gov.in** and search by:
   - Name, or
   - EPIC number
2. Download the **Voter Helpline App** (available on Android & iOS)
3. Send an SMS: Type `EPIC <your EPIC number>` and send to **1950**
4. Call the toll-free helpline: **1950**

**On Election Day:**
- Carry your **Voter ID (EPIC card)** or any of the 12 approved alternative IDs
- Approved alternatives include: Aadhaar, Passport, Driving License, PAN card,
  Service ID (government employees), Bank passbook with photo, MNREGA job card, etc.
- Polling booths are usually open from **7:00 AM to 6:00 PM**
- Arrive early to avoid long queues
"""
        }
    }
}


# System prompts for Gemini, tailored by intent
SYSTEM_PROMPTS = {
    "base": """You are VoteWise AI, an official-sounding but friendly Election Process Education Assistant for Indian elections. Your role is to educate citizens about voter registration, the electoral process, EVM/VVPAT usage, and help them find factual candidate information.

CRITICAL RULES:
1. NEVER recommend or suggest any political party or candidate
2. NEVER express political opinions or preferences
3. ALWAYS maintain strict political neutrality
4. Provide ONLY factual, verifiable information
5. When discussing candidates/parties, present information equally and neutrally
6. If asked who to vote for, politely decline and explain that voting is a personal choice
7. Always encourage citizens to exercise their democratic right to vote
8. Be helpful, patient, and explain concepts clearly
9. Use official sources: Election Commission of India (eci.gov.in), Voter Portal (voters.eci.gov.in)
10. If you don't know something, say so clearly rather than guessing""",

    "registration": """
CONTEXT: The user is asking about voter registration or eligibility.
Focus on:
- Eligibility criteria (age, citizenship, residency)
- Registration process (Form 6, 6A, 8)
- Online portal steps (voters.eci.gov.in)
- Required documents
- Status tracking
- EPIC card information
Provide step-by-step guidance where applicable.""",

    "candidate_info": """
CONTEXT: The user is asking about candidates, parties, or election results.
Focus on:
- Provide factual, neutral information only
- Use Google Search Grounding for real-time data
- Present ALL parties/candidates discussed equally
- Include official sources and citations
- NEVER compare candidates in a way that favors one over another
- If asked for opinions, redirect to factual information""",

    "process_education": """
CONTEXT: The user is asking about the voting process, EVMs, or VVPATs.
Focus on:
- Step-by-step EVM usage instructions
- VVPAT verification process
- Polling booth procedures
- Election day logistics
- Booth finder resources
- Rights and responsibilities of voters""",

    "general": """
CONTEXT: The user has a general question about Indian elections.
Provide helpful, factual information and guide them toward the three main areas:
1. Registration & Eligibility
2. Candidate Information
3. Voting Process Education""",

    "greeting": """
CONTEXT: The user is greeting or starting a conversation.
Respond warmly and briefly introduce yourself as VoteWise AI, an election education assistant.
Mention the three main areas you can help with:
1. Voter Registration & Eligibility
2. Candidate & Party Information
3. Voting Process (EVM, VVPAT, Booth Finding)"""
}

LANGUAGE_INSTRUCTIONS = {
    "en": "Respond in English.",
    "hi": "Respond entirely in Hindi (हिन्दी). Use Devanagari script.",
    "ta": "Respond entirely in Tamil (தமிழ்). Use Tamil script."
}


def get_system_prompt(intent: str, language: str = "en") -> str:
    """
    Build a complete system prompt for Gemini based on intent and language.

    Args:
        intent: The classified intent category.
        language: Target language code.

    Returns:
        Complete system prompt string.
    """
    base = SYSTEM_PROMPTS["base"]
    intent_context = SYSTEM_PROMPTS.get(intent, SYSTEM_PROMPTS["general"])
    lang_instruction = LANGUAGE_INSTRUCTIONS.get(language, LANGUAGE_INSTRUCTIONS["en"])

    return f"{base}\n\n{intent_context}\n\n{lang_instruction}"


def get_knowledge_context(intent: str) -> str:
    """
    Get relevant election knowledge to include in the prompt.

    Args:
        intent: The classified intent category.

    Returns:
        Formatted knowledge context string.
    """
    context_parts = []

    if intent == "registration":
        for key in ["eligibility", "forms", "portal_steps"]:
            data = ELECTION_KNOWLEDGE.get("registration", {}).get(key, {}).get("en", {})
            if data:
                context_parts.append(f"### {data.get('title', '')}\n{data.get('content', '')}")

    elif intent == "process_education":
        for key in ["evm_process", "vvpat", "polling_booth"]:
            data = ELECTION_KNOWLEDGE.get(key, {}).get("en", {})
            if data:
                context_parts.append(f"### {data.get('title', '')}\n{data.get('content', '')}")

    if context_parts:
        return "\n\nREFERENCE KNOWLEDGE:\n" + "\n---\n".join(context_parts)

    return ""
