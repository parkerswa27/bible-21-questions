"""Rule-based question bank — Python port of js/engine/questionBank.js.

Keep this in sync with the JS version if either changes; they're independent
implementations of the same rules (the JS copy is no longer used at runtime once
the frontend is API-driven, but is kept in the repo as the original reference/
offline-demo implementation).

Each entry: id, category, label (used for suggested-question chips), match(t) -> bool,
evaluate(character) -> answer dict. `t` is already normalized (lowercase, punctuation
stripped). See answer_types.py for the game-integrity rule on hints.
"""

import re

from answer_types import (
    answer_from_boolean,
    answer_from_timeline,
    answer_from_tri_state,
    answer_from_yes_no_unknown,
    make_answer,
)


def _match(pattern):
    compiled = re.compile(pattern)
    return lambda t: compiled.search(t) is not None


def _morality(field_key):
    hint = "Their portrayal in Scripture includes both admirable and troubling actions."

    def evaluate(c, good_type, bad_type):
        v = c["good_bad_neutral"]
        if v == "good":
            return make_answer(good_type)
        if v == "bad":
            return make_answer(bad_type)
        if v == "mixed":
            return make_answer("sometimes", hint)
        return make_answer("unknown")

    return evaluate


QUESTION_BANK = [
    # --- Identity ---
    {
        "id": "testament_old", "category": "Identity", "label": "Are you from the Old Testament?",
        "match": _match(r"\bold testament\b"),
        "evaluate": lambda c: answer_from_boolean(c["testament"] == "OT"),
    },
    {
        "id": "testament_new", "category": "Identity", "label": "Are you from the New Testament?",
        "match": _match(r"\bnew testament\b"),
        "evaluate": lambda c: answer_from_boolean(c["testament"] == "NT"),
    },
    {
        "id": "gender_woman", "category": "Identity", "label": "Are you a woman?",
        "match": _match(r"\b(woman|female|girl|lady)\b"),
        "evaluate": lambda c: answer_from_boolean(c["gender"] == "F"),
    },
    {
        "id": "gender_man", "category": "Identity", "label": "Are you a man?",
        "match": lambda t: re.search(r"\b(man|male|guy|boy)\b", t) is not None and re.search(r"\bwoman|\bhuman", t) is None,
        "evaluate": lambda c: answer_from_boolean(c["gender"] == "M"),
    },

    # --- Roles / offices ---
    {
        "id": "role_queen", "category": "Role", "label": "Were you a queen?",
        "match": _match(r"\bqueen(s)?\b"),
        "evaluate": lambda c: answer_from_boolean(any(re.search(r"queen", r, re.I) for r in c["roles"])),
    },
    {
        "id": "role_king", "category": "Role", "label": "Were you a king?",
        "match": lambda t: re.search(r"\bking(s)?\b", t) is not None and "kingdom" not in t,
        "evaluate": lambda c: answer_from_tri_state(c["king"], "This depends on how the term 'king' is defined."),
    },
    {
        "id": "role_judge", "category": "Role", "label": "Were you a judge of Israel?",
        "match": _match(r"\bjudge(s)?\b"),
        "evaluate": lambda c: answer_from_tri_state(c["judge"], "This depends on how the term 'judge' is defined."),
    },
    {
        "id": "role_prophet", "category": "Role", "label": "Were you a prophet?",
        "match": _match(r"\bprophet(s|ess|esses)?\b"),
        "evaluate": lambda c: answer_from_tri_state(c["prophet"], "This depends on how the term 'prophet' is defined."),
    },
    {
        "id": "role_priest", "category": "Role", "label": "Were you a priest?",
        "match": _match(r"\bpriest(s|hood)?\b"),
        "evaluate": lambda c: answer_from_tri_state(c["priest"], "This depends on how the term 'priest' is defined."),
    },
    {
        "id": "role_apostle", "category": "Role", "label": "Were you an apostle?",
        "match": lambda t: re.search(r"\bapostle(s)?\b", t) is not None or re.search(r"\btwelve\b", t) is not None,
        "evaluate": lambda c: answer_from_tri_state(c["apostle"], "This depends on how the term 'apostle' is defined."),
    },
    {
        "id": "role_disciple", "category": "Role", "label": "Were you one of Jesus's disciples?",
        "match": _match(r"\bdisciple(s)?\b"),
        "evaluate": lambda c: answer_from_tri_state(c["disciple"], "Scripture does not explicitly label this either way."),
    },
    {
        "id": "wrote_book", "category": "Role", "label": "Did you write a book of the Bible?",
        "match": lambda t: re.search(r"\b(write|wrote|writer|author(ed)?)\b", t) is not None and re.search(r"\bbook(s)?\b|\bbible\b|\bscripture(s)?\b", t) is not None,
        "evaluate": lambda c: answer_from_tri_state(c["wrote_biblical_book"], "Authorship is traditionally held but debated by some scholars."),
    },

    # --- Morality ---
    {
        "id": "morality_bad", "category": "Character", "label": "Are you considered a bad or villainous character?",
        "match": _match(r"\b(bad|evil|wicked|villain(ous)?|sinful)\b"),
        "evaluate": lambda c: _morality("good_bad_neutral")(c, "no", "yes"),
    },
    {
        "id": "morality_good", "category": "Character", "label": "Are you generally considered a good character?",
        "match": _match(r"\b(good|righteous|godly|virtuous)\b"),
        "evaluate": lambda c: _morality("good_bad_neutral")(c, "yes", "no"),
    },

    # --- Family ---
    {
        "id": "was_married", "category": "Family", "label": "Were you married?",
        "match": _match(r"\bmarried\b|\bwife\b|\bhusband\b|\bspouse\b"),
        "evaluate": lambda c: answer_from_yes_no_unknown(c["married"]),
    },
    {
        "id": "had_children", "category": "Family", "label": "Did you have children?",
        "match": lambda t: re.search(r"\bchildren\b|\bkids\b|\bson(s)?\b|\bdaughter(s)?\b", t) is not None and re.search(r"\bhave\b|\bany\b|\bdid\b", t) is not None,
        "evaluate": lambda c: answer_from_yes_no_unknown(c["had_children"]),
    },
    {
        "id": "genealogy", "category": "Family", "label": "Is your genealogy recorded in the Bible?",
        "match": _match(r"\bgenealog(y|ies)\b|\bfamily tree\b"),
        "evaluate": lambda c: answer_from_boolean(c["genealogy_recorded"]),
    },

    # --- Death ---
    {
        "id": "violent_death", "category": "Life & Death", "label": "Did you die a violent death?",
        "match": _match(r"\bviolent(ly)?\b|\bkilled\b|\bmurder(ed)?\b|\bcrucif(y|ied|ixion)\b|\bexecut(ed|ion)\b|\bassassinat(ed|ion)\b|\bbehead(ed|ing)?\b|\bstab(bed)?\b|\bslain\b"),
        "evaluate": lambda c: answer_from_yes_no_unknown(c["violent_death"]),
    },

    # --- Time period (landmark-relative) ---
    {
        "id": "flood_before", "category": "Time period", "label": "Did you live before the Great Flood?",
        "match": lambda t: "flood" in t and "before" in t,
        "evaluate": lambda c: answer_from_timeline(c["before_or_after_flood"], "before", "Their life overlaps with this event."),
    },
    {
        "id": "flood_after", "category": "Time period", "label": "Did you live after the Great Flood?",
        "match": lambda t: "flood" in t and "after" in t,
        "evaluate": lambda c: answer_from_timeline(c["before_or_after_flood"], "after", "Their life overlaps with this event."),
    },
    {
        "id": "temple_before", "category": "Time period", "label": "Did you live before the First Temple was built?",
        "match": lambda t: "temple" in t and "before" in t,
        "evaluate": lambda c: answer_from_timeline(c["before_or_after_first_temple"], "before", "Their life overlaps with this period."),
    },
    {
        "id": "temple_after", "category": "Time period", "label": "Did you live after the First Temple was built?",
        "match": lambda t: "temple" in t and "after" in t,
        "evaluate": lambda c: answer_from_timeline(c["before_or_after_first_temple"], "after", "Their life overlaps with this period."),
    },
    {
        "id": "exile_before", "category": "Time period", "label": "Did you live before the Babylonian exile?",
        "match": lambda t: ("exile" in t or "captivity" in t) and "before" in t,
        "evaluate": lambda c: answer_from_timeline(c["before_or_after_babylonian_exile"], "before", "Their life overlaps with this period."),
    },
    {
        "id": "exile_after", "category": "Time period", "label": "Did you live after the Babylonian exile?",
        "match": lambda t: ("exile" in t or "captivity" in t) and "after" in t,
        "evaluate": lambda c: answer_from_timeline(c["before_or_after_babylonian_exile"], "after", "Their life overlaps with this period."),
    },
]
