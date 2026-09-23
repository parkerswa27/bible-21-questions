"""Rule-based question-answering engine — Python port of js/engine/questionEngine.js.

This runs entirely server-side now, so the secret character it operates on is never
sent to the browser. `answer_question` is tried first; if it returns matched=False,
app.py falls through to the AI fallback (ai_fallback.py) before finally telling the
player the question wasn't understood.
"""

import re

from answer_types import make_answer
from question_bank import QUESTION_BANK
from schema import NT_BOOKS, OT_BOOKS

_PUNCT_RE = re.compile(r"[?.!,;:'\"()]")
_WS_RE = re.compile(r"\s+")

TIMELINE_CONFIDENCE_GAP = 3

# Words that mark text as an actual question rather than a bare name typed into the
# question box. If any of these lead the input (or it contains "?"), we never treat
# it as an implicit guess — see looks_like_name_guess().
_QUESTION_STARTERS = re.compile(
    r"^(did|do|does|was|were|is|are|am|will|would|should|can|could|have|has|had|"
    r"who|what|when|where|why|how)\b"
)


def normalize(text):
    t = text.lower()
    t = _PUNCT_RE.sub(" ", t)
    t = _WS_RE.sub(" ", t).strip()
    return t


def looks_like_name_guess(raw_text, all_characters):
    """True if `raw_text` isn't phrased as a question at all and exactly matches a
    known character's name or alternate name (anywhere in the full roster, not just
    the secret one — the player is guessing from their own knowledge, not ours).

    Used by app.py to redirect a bare "David" typed into the question box straight
    to the guess flow instead of letting it die as an unparseable question or
    burning an AI call on something that was never a yes/no question."""
    stripped = raw_text.strip()
    if not stripped or "?" in stripped:
        return False
    if _QUESTION_STARTERS.match(stripped.lower()):
        return False

    key = stripped.lower()
    for c in all_characters:
        if c["name"].strip().lower() == key:
            return True
        if any(a.strip().lower() == key for a in c.get("alternate_names", [])):
            return True
    return False


def _try_named_comparison(t, character, all_characters):
    direction = "before" if re.search(r"\bbefore\b", t) else ("after" if re.search(r"\bafter\b", t) else None)
    if not direction:
        return None

    candidates = []
    for c in all_characters:
        if c["id"] == character["id"]:
            continue
        names = [c["name"]] + c.get("alternate_names", [])
        if any(len(n) >= 3 and n.lower() in t for n in names):
            candidates.append(c)
    if len(candidates) != 1:
        return None  # ambiguous or no name found

    other = candidates[0]
    diff = character["timeline_order"] - other["timeline_order"]
    if abs(diff) < TIMELINE_CONFIDENCE_GAP:
        # Names the character the PLAYER typed, never the secret one — safe.
        return make_answer("sometimes", f"Our timelines are too close (or overlap) to say for certain relative to {other['name']}.")

    lived_before = diff < 0
    matches = lived_before if direction == "before" else not lived_before
    return make_answer("yes" if matches else "no")


def answer_question(raw_text, character, all_characters):
    """Returns {"matched": bool, "question_id": str|None, "category": str|None, "answer": dict|None}"""
    t = normalize(raw_text)
    if not t:
        return {"matched": False}

    comparison = _try_named_comparison(t, character, all_characters)
    if comparison:
        return {"matched": True, "question_id": "named_comparison", "category": "Time period", "answer": comparison}

    for q in QUESTION_BANK:
        if q["match"](t):
            return {"matched": True, "question_id": q["id"], "category": q["category"], "answer": q["evaluate"](character)}

    # Cross-testament mention, derived from books_mentioned_in rather than a hand-set flag.
    if re.search(r"mentioned\b.*\bnew testament\b", t) or ("new testament" in t and "mention" in t):
        mentioned = character["testament"] == "NT" or any(b in NT_BOOKS for b in character["books_mentioned_in"])
        return {"matched": True, "question_id": "mentioned_nt", "category": "Identity", "answer": make_answer("yes" if mentioned else "no")}
    if re.search(r"mentioned\b.*\bold testament\b", t) or ("old testament" in t and "mention" in t):
        mentioned = character["testament"] == "OT" or any(b in OT_BOOKS for b in character["books_mentioned_in"])
        return {"matched": True, "question_id": "mentioned_ot", "category": "Identity", "answer": make_answer("yes" if mentioned else "no")}

    # NOTE: deliberately no generic keyword/event fallback — see questionBank.js for why.
    # Anything unmatched here is handed to the AI fallback by app.py, never guessed at locally.
    return {"matched": False}


def check_guess(guess_text, character):
    g = guess_text.strip().lower()
    if not g:
        return False
    if character["name"].lower() == g:
        return True
    return any(a.lower() == g for a in character.get("alternate_names", []))
