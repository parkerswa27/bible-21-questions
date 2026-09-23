"""In-memory round store. The secret character lives here, server-side, only —
it is never serialized into any response sent to the browser (see app.py's
`public_round_view` / `public_reveal` for exactly what crosses the wire).

CAVEAT (documented for deployment): this is a single-process in-memory dict. It
works correctly on a single dyno/instance. If you ever scale to multiple worker
processes or instances, round state will NOT be shared between them — move this
to Redis or a small database first. For the free/low-cost single-instance
deployment this project targets, that's not a concern.
"""

import random
import threading
import time
import uuid

from data_loader import get_characters_for_difficulty

MAX_QUESTIONS = 21
ROUND_TTL_SECONDS = 2 * 60 * 60  # stale rounds are garbage-collected after 2 hours

_rounds = {}
_lock = threading.Lock()


def start_round(difficulty, mode="classic"):
    pool = get_characters_for_difficulty(difficulty)
    if not pool:
        raise ValueError(f'No characters available for difficulty "{difficulty}"')
    character = random.choice(pool)
    round_id = uuid.uuid4().hex
    round_obj = {
        "id": round_id,
        "character": character,
        "difficulty": difficulty,
        "mode": mode,
        "max_questions": MAX_QUESTIONS,
        "questions_used": 0,
        "history": [],
        "status": "playing",  # 'playing' | 'won' | 'lost'
        "created_at": time.time(),
    }
    with _lock:
        _cleanup_locked()
        _rounds[round_id] = round_obj
    return round_obj


def get_round(round_id):
    with _lock:
        return _rounds.get(round_id)


def _cleanup_locked():
    cutoff = time.time() - ROUND_TTL_SECONDS
    stale = [rid for rid, r in _rounds.items() if r["created_at"] < cutoff]
    for rid in stale:
        del _rounds[rid]


def record_question(round_obj, question_text, answer, source):
    round_obj["questions_used"] += 1
    entry = {
        "kind": "question",
        "text": question_text,
        "answer": answer,
        "question_number": round_obj["questions_used"],
        "source": source,  # 'rule' | 'ai'
    }
    round_obj["history"].append(entry)
    if round_obj["questions_used"] >= round_obj["max_questions"] and round_obj["status"] == "playing":
        round_obj["status"] = "lost"
    return entry


def record_unrecognized(round_obj, question_text):
    entry = {"kind": "unrecognized", "text": question_text}
    round_obj["history"].append(entry)
    return entry


def record_guess(round_obj, guess_text, correct):
    entry = {"kind": "guess", "text": guess_text, "correct": correct}
    round_obj["history"].append(entry)
    if correct:
        round_obj["status"] = "won"
    return entry
