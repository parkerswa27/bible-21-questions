"""AI-backed question answerer — used only when the rule-based engine
(question_engine.py) can't confidently parse a question.

Architecture (per the game's integrity rules):
  Player question -> rule engine -> (if unmatched) -> AI fallback -> normalized
  answer (YES/NO/SOMETIMES/UNKNOWN) -> frontend.

The AI is given the secret character's full structured data (it needs this to answer
accurately) but its raw output NEVER reaches the browser. Every response is parsed
and validated here: only one of YES/NO/SOMETIMES/UNKNOWN is ever returned, anything
else — including any response that leaks the character's name — is converted to
UNKNOWN before this function returns.
"""

import os
import re

from answer_types import make_answer

AI_API_KEY = os.environ.get("AI_API_KEY") or os.environ.get("ANTHROPIC_API_KEY")
AI_MODEL = os.environ.get("AI_MODEL", "claude-haiku-4-5-20251001")

SYSTEM_PROMPT = (
    "You are the question-answering engine for a Bible character guessing game. "
    "You know the secret character and its structured data. Answer the player's "
    "question using only the provided data and Scripture-supported information. "
    "Return exactly one classification: YES, NO, SOMETIMES, or UNKNOWN. "
    "Never return the character's name. Never provide explanations. Never provide "
    "clues beyond the requested classification.\n\n"
    "Guidance:\n"
    "- YES / NO: only for facts explicitly stated in Scripture or the provided data.\n"
    "- SOMETIMES: for reasonable inference, traditional interpretation, or genuinely "
    "disputed/debated theological questions.\n"
    "- UNKNOWN: whenever the provided data and Scripture do not give enough "
    "information to answer confidently. When in doubt, prefer UNKNOWN over guessing.\n"
    "- Distinguish explicitly stated Scripture from inference, tradition, and "
    "disputed interpretation — only give YES/NO for the first category.\n\n"
    "Reply with ONLY one word: YES, NO, SOMETIMES, or UNKNOWN. No punctuation, no "
    "explanation, no character name, nothing else."
)

_VALID = {"YES": "yes", "NO": "no", "SOMETIMES": "sometimes", "UNKNOWN": "unknown"}


def _character_context(character):
    """Strip a character down to the structured fields relevant for Q&A — no need to
    forward UI-only fields like `short_description` prose, which could itself echo
    the name in a way the model then repeats."""
    fields = [
        "name", "alternate_names", "testament", "gender", "era", "approximate_period",
        "before_or_after_flood", "before_or_after_first_temple", "before_or_after_babylonian_exile",
        "occupation", "roles", "king", "judge", "prophet", "priest", "disciple", "apostle",
        "wrote_biblical_book", "genealogy_recorded", "family_members", "associated_people",
        "associated_events", "books_mentioned_in", "good_bad_neutral", "married",
        "had_children", "violent_death", "scripture_references",
    ]
    return {k: character.get(k) for k in fields}


def is_configured():
    return bool(AI_API_KEY)


def _contains_character_name(text, character):
    if not text:
        return False
    lowered = text.lower()
    names = [character.get("name", "")] + character.get("alternate_names", [])
    return any(n and len(n) >= 3 and n.lower() in lowered for n in names)


def _extract_classification(raw_text):
    if not raw_text:
        return None
    token = raw_text.strip().upper()
    # tolerate minor formatting like "YES." or a leading word
    match = re.match(r"^(YES|NO|SOMETIMES|UNKNOWN)\b", token)
    return match.group(1) if match else None


def answer_question(question_text, character):
    """Returns an answer dict (see answer_types.make_answer) with NO hint text
    (per spec, AI answers show only the bare category), or None if the AI is not
    configured / the call failed — callers should treat None as "still unmatched"
    and fall back to the existing unrecognized-question flow (no question consumed)."""
    if not is_configured():
        return None

    try:
        import anthropic
    except ImportError:
        return None

    try:
        client = anthropic.Anthropic(api_key=AI_API_KEY)
        response = client.messages.create(
            model=AI_MODEL,
            max_tokens=8,
            temperature=0,
            system=SYSTEM_PROMPT,
            messages=[{
                "role": "user",
                "content": (
                    f"Secret character data (JSON): {_character_context(character)}\n\n"
                    f"Player's question: {question_text!r}\n\n"
                    "Classification:"
                ),
            }],
        )
        raw_text = "".join(block.text for block in response.content if getattr(block, "type", None) == "text")
    except Exception:
        # Network/auth/rate-limit errors etc. — fail closed to "not understood", never crash the round.
        return None

    classification = _extract_classification(raw_text)

    # Defense in depth: even a well-formed classification is discarded if the raw
    # response also leaked the character's name somewhere in the text.
    if classification is None or _contains_character_name(raw_text, character):
        classification = "UNKNOWN"

    answer_type = _VALID[classification]
    # No hint text for AI answers — the player sees only the bare category, per spec.
    return make_answer(answer_type)
