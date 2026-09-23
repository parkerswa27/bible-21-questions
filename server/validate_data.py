#!/usr/bin/env python3
"""Standalone validation for the character database.

Run as: /opt/anaconda3/bin/python3 server/validate_data.py [path/to/characters.json]

Checks: missing required fields, invalid enum values, duplicate ids, duplicate
name/alternate_name collisions (a real accuracy risk — see AUTHORING_SPEC.md's
disambiguation rule), missing scripture references, a handful of cross-field
contradiction checks, and difficulty-tier distribution. Exits non-zero if any
ERROR-level issue is found (warnings don't fail the build).
"""

import json
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
from schema import DIFFICULTIES, ENUM_FIELDS, NT_BOOKS, OT_BOOKS, REQUIRED_FIELDS

ALL_BOOKS = set(OT_BOOKS) | set(NT_BOOKS)


def load(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def validate(characters):
    errors = []
    warnings = []
    seen_ids = {}
    seen_names = {}  # lowercase name/alt-name -> list of (id, which)

    for idx, c in enumerate(characters):
        label = c.get("id") or c.get("name") or f"index {idx}"

        # --- required fields ---
        for field in REQUIRED_FIELDS:
            if field not in c:
                errors.append(f"[{label}] missing required field '{field}'")
            elif c[field] is None:
                errors.append(f"[{label}] field '{field}' is null")

        if "id" not in c or not c.get("id"):
            errors.append(f"[{label}] missing 'id'")
            continue

        # --- duplicate ids ---
        if c["id"] in seen_ids:
            errors.append(f"[{c['id']}] duplicate id (also used by entry at index {seen_ids[c['id']]})")
        else:
            seen_ids[c["id"]] = idx

        # --- enum values ---
        for field, allowed in ENUM_FIELDS.items():
            if field in c and c[field] is not None and c[field] not in allowed:
                errors.append(f"[{label}] field '{field}' has invalid value {c[field]!r} (allowed: {sorted(allowed)})")

        # --- genealogy_recorded must be a real boolean ---
        if "genealogy_recorded" in c and not isinstance(c["genealogy_recorded"], bool):
            errors.append(f"[{label}] 'genealogy_recorded' must be true/false, got {c['genealogy_recorded']!r}")

        # --- timeline_order must be a number ---
        if "timeline_order" in c and not isinstance(c["timeline_order"], (int, float)):
            errors.append(f"[{label}] 'timeline_order' must be a number, got {c['timeline_order']!r}")

        # --- scripture references required and non-empty ---
        refs = c.get("scripture_references")
        if not refs or not isinstance(refs, list) or len(refs) == 0:
            errors.append(f"[{label}] missing scripture_references")

        # --- books_mentioned_in must be real canon books ---
        for b in c.get("books_mentioned_in", []) or []:
            if b not in ALL_BOOKS:
                errors.append(f"[{label}] books_mentioned_in has unrecognized book '{b}'")

        # --- short_description present ---
        if not c.get("short_description"):
            errors.append(f"[{label}] missing short_description")

        # --- name/alternate_name collision tracking ---
        names_here = [c.get("name", "")] + list(c.get("alternate_names", []) or [])
        for n in names_here:
            if not n:
                continue
            key = n.strip().lower()
            seen_names.setdefault(key, []).append(c["id"])

        # --- playability: too many unknowns ---
        unknown_like = sum(
            1 for f in ("married", "had_children", "violent_death") if c.get(f) == "unknown"
        )
        empty_lists = sum(
            1 for f in ("occupation", "roles", "family_members", "associated_people", "associated_events")
            if not c.get(f)
        )
        if unknown_like == 3 and empty_lists >= 4:
            warnings.append(f"[{label}] very sparse entry ({unknown_like} unknown fields, {empty_lists} empty lists) — may be hard to identify through play")

        # --- contradiction checks ---
        if c.get("king") == "yes" and c.get("testament") == "NT" and "king" not in " ".join(c.get("roles", [])).lower():
            warnings.append(f"[{label}] king='yes' but 'king' isn't mentioned in roles — double-check this is intentional")
        if c.get("wrote_biblical_book") == "yes" and not c.get("books_mentioned_in"):
            warnings.append(f"[{label}] wrote_biblical_book='yes' but books_mentioned_in is empty")
        if c.get("difficulty") not in DIFFICULTIES:
            errors.append(f"[{label}] invalid difficulty {c.get('difficulty')!r}")

    # --- name collisions across DIFFERENT characters (the disambiguation rule) ---
    for name, ids in seen_names.items():
        unique_ids = sorted(set(ids))
        if len(unique_ids) > 1:
            warnings.append(f"Name/alternate-name '{name}' is shared by multiple characters: {unique_ids} — verify this is deliberate (e.g. distinct people) and each has a disambiguating notes.name")

    return errors, warnings


def report(characters, errors, warnings):
    print(f"Loaded {len(characters)} characters.\n")

    by_diff = {d: 0 for d in DIFFICULTIES}
    for c in characters:
        d = c.get("difficulty")
        if d in by_diff:
            by_diff[d] += 1
    print("Distribution by difficulty:")
    for d in DIFFICULTIES:
        print(f"  {d:8s} {by_diff[d]}")
    print()

    ot = sum(1 for c in characters if c.get("testament") == "OT")
    nt = sum(1 for c in characters if c.get("testament") == "NT")
    print(f"Testament split: OT={ot}  NT={nt}\n")

    if errors:
        print(f"ERRORS ({len(errors)}):")
        for e in errors:
            print(f"  ✗ {e}")
        print()
    else:
        print("No errors. ✓\n")

    if warnings:
        print(f"WARNINGS ({len(warnings)}):")
        for w in warnings:
            print(f"  ! {w}")
        print()
    else:
        print("No warnings. ✓\n")

    return len(errors) == 0


if __name__ == "__main__":
    path = sys.argv[1] if len(sys.argv) > 1 else os.path.join(os.path.dirname(__file__), "..", "data", "characters.json")
    characters = load(path)
    errors, warnings = validate(characters)
    ok = report(characters, errors, warnings)
    sys.exit(0 if ok else 1)
