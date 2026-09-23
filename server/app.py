"""Bible 21 Questions — Flask backend.

Serves the static frontend AND the game API from one process (simplest possible
deployment: one web service, no CORS to configure, HTTPS handled by the host).

SECRET-CHARACTER PROTECTION: the character object never leaves this process except
through the deliberately narrow `public_round_view` (mid-game) and `public_reveal`
(post-game only) helpers below. No route ever serializes a raw round or character
dict directly into a response.
"""

import logging
import os
import sys

from dotenv import load_dotenv
from flask import Flask, jsonify, request, send_from_directory
from werkzeug.middleware.proxy_fix import ProxyFix

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
load_dotenv(os.path.join(PROJECT_ROOT, ".env"))  # no-op if the file doesn't exist (e.g. in production, where the host injects env vars directly)

sys.path.insert(0, os.path.dirname(__file__))  # allow `import question_engine` etc. as top-level modules

import ai_fallback
import data_loader
import game_store
import rate_limit
from question_engine import answer_question, check_guess, looks_like_name_guess

# INFO-level so ai_fallback's diagnostic logging (not configured / call failed /
# response failed validation) actually shows up in the host's log stream — this is
# what makes "the AI fallback silently isn't working" diagnosable in production
# instead of looking identical to "the rule engine just didn't match."
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")

app = Flask(__name__, static_folder=None)
app.config["MAX_CONTENT_LENGTH"] = 4 * 1024  # a question/guess body has no business being large

# Render (like Heroku/Railway) puts one reverse proxy in front of the app; without
# this, request.remote_addr is the proxy's IP for every request, which would make
# the per-IP AI rate limit in rate_limit.py either useless (everyone shares one
# bucket) or spoofable. Trusting exactly one hop matches that single-proxy setup.
app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1)


# ---------------------------------------------------------------------------
# Static frontend
# ---------------------------------------------------------------------------

@app.route("/")
def serve_index():
    return send_from_directory(PROJECT_ROOT, "index.html")


@app.route("/css/<path:filename>")
def serve_css(filename):
    return send_from_directory(os.path.join(PROJECT_ROOT, "css"), filename)


@app.route("/js/<path:filename>")
def serve_js(filename):
    return send_from_directory(os.path.join(PROJECT_ROOT, "js"), filename)


# ---------------------------------------------------------------------------
# API — helpers that decide exactly what the client is allowed to see
# ---------------------------------------------------------------------------

DIFFICULTY_LABELS = {
    "easy": "Very recognizable Bible characters.",
    "medium": "Recognizable but less obvious characters.",
    "hard": "Less famous — you'll need sharper questions to pin them down.",
    "expert": "Minor prophets, obscure kings and priests, and other named figures.",
}


def public_round_view(round_obj):
    """Everything the client needs mid-game. No character fields at all."""
    return {
        "roundId": round_obj["id"],
        "difficulty": round_obj["difficulty"],
        "maxQuestions": round_obj["max_questions"],
        "questionsUsed": round_obj["questions_used"],
        "questionsRemaining": round_obj["max_questions"] - round_obj["questions_used"],
        "status": round_obj["status"],
    }


def public_entry_view(entry):
    if entry["kind"] == "question":
        return {
            "kind": "question",
            "text": entry["text"],
            "questionNumber": entry["question_number"],
            "answer": {"type": entry["answer"]["type"], "label": entry["answer"]["label"], "hint": entry["answer"]["hint"]},
        }
    if entry["kind"] == "guess":
        return {"kind": "guess", "text": entry["text"], "correct": entry["correct"]}
    return {"kind": "unrecognized", "text": entry["text"]}


def public_reveal(round_obj):
    """Only ever called once round status is 'won' or 'lost'."""
    c = round_obj["character"]
    return {
        "name": c["name"],
        "testament": c["testament"],
        "difficulty": round_obj["difficulty"],
        "questionsUsed": round_obj["questions_used"],
        "status": round_obj["status"],
        "shortDescription": c["short_description"],
        "scriptureReferences": c["scripture_references"],
        "notes": c.get("notes") or {},
    }


# ---------------------------------------------------------------------------
# API routes
# ---------------------------------------------------------------------------

@app.route("/api/health")
def health():
    return jsonify({
        "status": "ok",
        "characters": len(data_loader.get_all_characters()),
        "aiConfigured": ai_fallback.is_configured(),
        "aiModel": ai_fallback.AI_MODEL if ai_fallback.is_configured() else None,
        "aiMaxCallsPerRound": game_store.MAX_AI_CALLS_PER_ROUND,
        "aiMaxCallsPerIpPerHour": rate_limit.MAX_AI_CALLS_PER_IP_PER_HOUR,
    })


@app.route("/api/difficulties")
def difficulties():
    out = []
    for d in ("easy", "medium", "hard", "expert"):
        out.append({"id": d, "description": DIFFICULTY_LABELS[d], "characterCount": len(data_loader.get_characters_for_difficulty(d))})
    return jsonify(out)


@app.route("/api/rounds", methods=["POST"])
def create_round():
    body = request.get_json(silent=True) or {}
    difficulty = body.get("difficulty", "easy")
    if difficulty not in ("easy", "medium", "hard", "expert"):
        return jsonify({"error": "invalid difficulty"}), 400
    try:
        round_obj = game_store.start_round(difficulty)
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    return jsonify(public_round_view(round_obj)), 201


@app.route("/api/rounds/<round_id>/questions", methods=["POST"])
def ask_question(round_id):
    round_obj = game_store.get_round(round_id)
    if not round_obj:
        return jsonify({"error": "round not found"}), 404
    if round_obj["status"] != "playing":
        return jsonify({"error": "round is already over", "round": public_round_view(round_obj)}), 409

    body = request.get_json(silent=True) or {}
    text = (body.get("question") or "").strip()
    if not text:
        return jsonify({"error": "question is required"}), 400
    if len(text) > 300:
        return jsonify({"error": "question is too long"}), 400

    all_characters = data_loader.get_all_characters()

    # A bare "David" typed into the question box isn't a question at all — treat it
    # as a guess (doesn't cost a question turn) instead of dying as unparseable or
    # burning an AI call on something that was never yes/no in the first place.
    if looks_like_name_guess(text, all_characters):
        correct = check_guess(text, round_obj["character"])
        entry = game_store.record_guess(round_obj, text, correct)
        return jsonify({"entry": public_entry_view(entry), "round": public_round_view(round_obj)})

    result = answer_question(text, round_obj["character"], all_characters)

    if result["matched"]:
        entry = game_store.record_question(round_obj, text, result["answer"], source="rule")
    else:
        ai_answer = None
        # Gate on is_configured() FIRST: neither budget counter should move for a call
        # that was never going to reach the network. Without this check, every
        # unmatched question while AI is unconfigured would still burn down both the
        # round's and the IP's AI budget for no reason, eventually reporting "AI
        # budget exhausted" even though AI was never active.
        if ai_fallback.is_configured() and game_store.can_use_ai(round_obj) and rate_limit.allow_ai_call(request.remote_addr):
            game_store.record_ai_call_attempt(round_obj)
            ai_answer = ai_fallback.answer_question(text, round_obj["character"])
        if ai_answer is not None:
            entry = game_store.record_question(round_obj, text, ai_answer, source="ai")
        else:
            entry = game_store.record_unrecognized(round_obj, text)

    return jsonify({"entry": public_entry_view(entry), "round": public_round_view(round_obj)})


@app.route("/api/rounds/<round_id>/guess", methods=["POST"])
def make_guess(round_id):
    round_obj = game_store.get_round(round_id)
    if not round_obj:
        return jsonify({"error": "round not found"}), 404
    if round_obj["status"] != "playing":
        return jsonify({"error": "round is already over", "round": public_round_view(round_obj)}), 409

    body = request.get_json(silent=True) or {}
    text = (body.get("guess") or "").strip()
    if not text:
        return jsonify({"error": "guess is required"}), 400
    if len(text) > 100:
        return jsonify({"error": "guess is too long"}), 400

    correct = check_guess(text, round_obj["character"])
    entry = game_store.record_guess(round_obj, text, correct)

    return jsonify({"entry": public_entry_view(entry), "round": public_round_view(round_obj)})


@app.route("/api/rounds/<round_id>/reveal")
def reveal(round_id):
    round_obj = game_store.get_round(round_id)
    if not round_obj:
        return jsonify({"error": "round not found"}), 404
    if round_obj["status"] == "playing":
        return jsonify({"error": "round is still in progress"}), 403
    return jsonify(public_reveal(round_obj))


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8778))
    debug = os.environ.get("FLASK_DEBUG", "0") == "1"
    app.run(host="0.0.0.0", port=port, debug=debug)
