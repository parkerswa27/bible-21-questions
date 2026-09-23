"""Canonical answer shape, mirroring js/engine/answerTypes.js exactly.

GAME-INTEGRITY RULE: an answer must never be able to identify or narrow down the
secret character. `hint` may ONLY be a fixed, generic, question-level sentence
(identical for every character who could produce that answer) — never anything
derived from the specific character. See question_bank.py for where hints come from.
"""

DISPLAY_LABEL = {
    "yes": "Yes",
    "no": "No",
    "sometimes": "Sometimes",
    "unknown": "Not enough information",
}


def make_answer(answer_type, hint=None):
    label = DISPLAY_LABEL.get(answer_type, DISPLAY_LABEL["unknown"])
    return {
        "type": answer_type,
        "label": label,
        "hint": hint,
        "text": f"{label}. {hint}" if hint else f"{label}.",
    }


def answer_from_tri_state(value, sometimes_hint=None):
    """value: 'yes' | 'no' | 'debated'"""
    if value == "yes":
        return make_answer("yes")
    if value == "no":
        return make_answer("no")
    if value == "debated":
        return make_answer("sometimes", sometimes_hint)
    return make_answer("unknown")


def answer_from_boolean(value):
    return make_answer("yes" if value else "no")


def answer_from_yes_no_unknown(value):
    """value: 'yes' | 'no' | 'unknown'"""
    if value == "yes":
        return make_answer("yes")
    if value == "no":
        return make_answer("no")
    return make_answer("unknown")


def answer_from_timeline(value, direction, sometimes_hint=None):
    """value: 'before' | 'during' | 'after' | 'spans' | 'na'; direction: 'before' | 'after'"""
    if value in ("spans", "during"):
        return make_answer("sometimes", sometimes_hint)
    if value == "na":
        return make_answer("unknown")
    is_before = value == "before"
    matches = is_before if direction == "before" else not is_before
    return make_answer("yes" if matches else "no")
