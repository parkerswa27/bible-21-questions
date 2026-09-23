"""Canonical book lists and enum reference for character data — Python port of
js/data/schema.js. See data/new/AUTHORING_SPEC.md for the full field reference used
when authoring character entries.
"""

OT_BOOKS = [
    "Genesis", "Exodus", "Leviticus", "Numbers", "Deuteronomy", "Joshua", "Judges", "Ruth",
    "1 Samuel", "2 Samuel", "1 Kings", "2 Kings", "1 Chronicles", "2 Chronicles", "Ezra",
    "Nehemiah", "Esther", "Job", "Psalms", "Proverbs", "Ecclesiastes", "Song of Songs",
    "Isaiah", "Jeremiah", "Lamentations", "Ezekiel", "Daniel", "Hosea", "Joel", "Amos",
    "Obadiah", "Jonah", "Micah", "Nahum", "Habakkuk", "Zephaniah", "Haggai", "Zechariah", "Malachi",
]

NT_BOOKS = [
    "Matthew", "Mark", "Luke", "John", "Acts", "Romans", "1 Corinthians", "2 Corinthians",
    "Galatians", "Ephesians", "Philippians", "Colossians", "1 Thessalonians", "2 Thessalonians",
    "1 Timothy", "2 Timothy", "Titus", "Philemon", "Hebrews", "James", "1 Peter", "2 Peter",
    "1 John", "2 John", "3 John", "Jude", "Revelation",
]

DIFFICULTIES = ["easy", "medium", "hard", "expert"]

REQUIRED_FIELDS = [
    "id", "name", "alternate_names", "testament", "gender", "era", "approximate_period",
    "timeline_order", "before_or_after_flood", "before_or_after_first_temple",
    "before_or_after_babylonian_exile", "occupation", "roles", "king", "judge", "prophet",
    "priest", "disciple", "apostle", "wrote_biblical_book", "genealogy_recorded",
    "family_members", "associated_people", "associated_events", "books_mentioned_in",
    "good_bad_neutral", "married", "had_children", "violent_death", "difficulty",
    "scripture_references", "short_description",
]

ENUM_FIELDS = {
    "testament": {"OT", "NT"},
    "gender": {"M", "F"},
    "before_or_after_flood": {"before", "after", "spans", "during"},
    "before_or_after_first_temple": {"before", "during", "after"},
    "before_or_after_babylonian_exile": {"before", "during", "after"},
    "king": {"yes", "no", "debated"},
    "judge": {"yes", "no", "debated"},
    "prophet": {"yes", "no", "debated"},
    "priest": {"yes", "no", "debated"},
    "disciple": {"yes", "no", "debated"},
    "apostle": {"yes", "no", "debated"},
    "wrote_biblical_book": {"yes", "no", "debated"},
    "good_bad_neutral": {"good", "bad", "mixed", "neutral"},
    "married": {"yes", "no", "unknown"},
    "had_children": {"yes", "no", "unknown"},
    "violent_death": {"yes", "no", "unknown"},
    "difficulty": {"easy", "medium", "hard", "expert"},
}
