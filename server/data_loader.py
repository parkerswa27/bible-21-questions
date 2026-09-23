"""Loads the character database once at process start. The frontend never receives
this file — only server/app.py's API handlers do, and even they only ever send the
client small derived fields (see app.py for exactly what crosses the wire).
"""

import json
import os

_DATA_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "characters.json")

_all_characters = None
_by_difficulty = None
_by_id = None


def _load():
    global _all_characters, _by_difficulty, _by_id
    with open(_DATA_PATH, "r", encoding="utf-8") as f:
        _all_characters = json.load(f)

    _by_difficulty = {"easy": [], "medium": [], "hard": [], "expert": []}
    _by_id = {}
    for c in _all_characters:
        _by_difficulty.setdefault(c["difficulty"], []).append(c)
        _by_id[c["id"]] = c


def get_all_characters():
    if _all_characters is None:
        _load()
    return _all_characters


def get_characters_for_difficulty(difficulty):
    if _by_difficulty is None:
        _load()
    return _by_difficulty.get(difficulty, [])


def get_character_by_id(character_id):
    if _by_id is None:
        _load()
    return _by_id.get(character_id)


def reload():
    """Used by the validation script / tests to pick up a freshly written characters.json."""
    _load()
