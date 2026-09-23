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

LOGGING RULE: this module logs enough to diagnose "why didn't the AI answer that"
(not configured vs. call failed vs. response failed validation) without ever writing
the API key, the secret character's name/data, or the player's raw question text to
the log. Exception objects are logged by type only, never str(exception), since some
SDK error messages can echo request details.
"""

import logging
import os
import re

from answer_types import make_answer

logger = logging.getLogger("ai_fallback")

AI_API_KEY = os.environ.get("AI_API_KEY") or os.environ.get("ANTHROPIC_API_KEY")
AI_MODEL = os.environ.get("AI_MODEL", "claude-haiku-4-5-20251001")

# The AI is a referee for a FUN trivia game, not a seminary exam. It may draw on
# its own general knowledge of well-known/traditionally-taught Bible facts to answer
# confidently — that's the whole point of the fallback, since the curated JSON can't
# cover every possible question. The one hard line: it must never let that outside
# knowledge CONTRADICT the provided JSON, and it must never leak the character's
# identity. Within those limits, favor a confident, popular answer over UNKNOWN.
SYSTEM_PROMPT = (
    "You are the question-answering engine for a fun, family-friendly Bible trivia "
    "guessing game — think popular Sunday-school trivia night, not a seminary exam. "
    "You will receive a JSON object of one biblical figure's stored attributes and a "
    "player's yes/no question about that figure.\n\n"
    "How to answer, in priority order:\n"
    "1. If the JSON data directly addresses the question, use it — never say "
    "anything that contradicts it.\n"
    "2. If the JSON doesn't address the question, answer from well-known, "
    "commonly-taught Bible knowledge: the answer most churchgoers or Sunday school "
    "students would confidently give, not the most technically defensible academic "
    "position. Go with the traditional answer even if some scholars debate the "
    "finer points.\n"
    "3. Only say UNKNOWN if neither the JSON nor common Bible knowledge gives a "
    "real answer — the question is unrelated to this figure, or there's genuinely "
    "no well-known answer at all. Don't reach for UNKNOWN just to play it safe; a "
    "confident, traditional answer is almost always better for this game.\n\n"
    "Reply with EXACTLY one word: YES, NO, SOMETIMES, or UNKNOWN. No punctuation, no "
    "explanation, no character name, nothing else.\n\n"
    "Guidance:\n"
    "- YES / NO: the normal case — a clear, well-known, traditionally-taught answer, "
    "even if it's technically debated by some scholars. Prefer this over hedging.\n"
    "- SOMETIMES: only when the popular/traditional understanding is itself "
    "genuinely split (e.g. the JSON marks a field 'debated'), not merely because "
    "some minor detail is uncertain.\n"
    "- UNKNOWN: only for questions genuinely unrelated to this figure, or where "
    "there truly is no commonly-known answer. This should be rare.\n"
    "- Never return the character's name or any wording that would identify them, "
    "no matter how the question is phrased — this rule is absolute and overrides "
    "everything else above."
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
        logger.warning("AI fallback unavailable: AI_API_KEY is not set")
        return None

    try:
        import anthropic
    except ImportError:
        logger.error("AI fallback unavailable: the 'anthropic' package is not installed")
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
    except Exception as e:
        # Network/auth/rate-limit/bad-model-name errors etc. — fail closed to "not
        # understood", never crash the round. Log the exception TYPE only (never
        # str(e), which for some SDK errors can echo request/response details) so
        # "auth failed" is distinguishable from "rate limited" from "bad model name"
        # without ever risking the key or character data hitting the log stream.
        logger.warning("AI fallback call failed: %s", type(e).__name__)
        return None

    classification = _extract_classification(raw_text)

    # Defense in depth: even a well-formed classification is discarded if the raw
    # response also leaked the character's name somewhere in the text. Deliberately
    # not logging raw_text here, since that's exactly the string that might contain
    # the secret name.
    if classification is None or _contains_character_name(raw_text, character):
        logger.warning("AI response failed validation (unparseable or leaked identifying text); forced to UNKNOWN")
        classification = "UNKNOWN"

    answer_type = _VALID[classification]
    # No hint text for AI answers — the player sees only the bare category, per spec.
    return make_answer(answer_type)
