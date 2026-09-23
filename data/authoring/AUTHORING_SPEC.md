# Character authoring spec — Bible 21 Questions database expansion

You are writing entries for a Bible-character guessing game's structured database.
Accuracy matters: this data drives yes/no gameplay logic, so wrong or invented facts
directly break the game. Follow this spec exactly.

## Output format

Write a **single JSON array** (valid JSON — double-quoted keys/strings, no comments,
no trailing commas, no JS syntax) to the exact file path you're given. Each element
of the array is one character object with the fields below.

## Field reference

```
id                                  string, unique snake_case slug, e.g. "jacob", "james_son_of_zebedee"
name                                string, display name
alternate_names                     string[] (can be empty [])
testament                           "OT" | "NT"
gender                              "M" | "F"
era                                 short human label, e.g. "Patriarchs", "Judges", "Early Church"
approximate_period                  human-readable string, e.g. "Traditional 19th century BC" — never overclaim precision
timeline_order                      integer — see "Timeline bands" below
before_or_after_flood               "before" | "after" | "spans" | "during"
before_or_after_first_temple        "before" | "during" | "after"
before_or_after_babylonian_exile    "before" | "during" | "after"
occupation                          string[] (can be empty [])
roles                               string[] (can be empty [])
king                                "yes" | "no" | "debated"
judge                               "yes" | "no" | "debated"
prophet                             "yes" | "no" | "debated"
priest                              "yes" | "no" | "debated"
disciple                            "yes" | "no" | "debated"   (a follower of Jesus, broader than the Twelve)
apostle                             "yes" | "no" | "debated"   (one of "the Twelve" or explicitly called an apostle)
wrote_biblical_book                 "yes" | "no" | "debated"
genealogy_recorded                  true | false  (a genealogy naming them appears in Scripture)
family_members                      string[] of "Relation: Name" strings (can be empty [])
associated_people                   string[] (can be empty [])
associated_events                   string[] (can be empty [])
books_mentioned_in                  string[] of canonical book names (see allowed list below) — include every
                                     book where they appear OR are meaningfully mentioned/quoted, including NT
                                     books that reference an OT figure (this is how the game answers
                                     "were you mentioned in the New Testament?" for OT characters, and vice versa —
                                     get this right)
good_bad_neutral                    "good" | "bad" | "mixed" | "neutral"
married                             "yes" | "no" | "unknown"
had_children                        "yes" | "no" | "unknown"
violent_death                       "yes" | "no" | "unknown"   ("yes" only for a clearly narrated murder,
                                     battle death, or execution — not vague/unrecorded deaths)
difficulty                          "easy" | "medium" | "hard" | "expert"  — USE EXACTLY the tier assigned to
                                     this name in your batch list. Do not reassign it yourself.
scripture_references                string[], REQUIRED, at least 1-2 real references (e.g. "Genesis 37",
                                     "Acts 16:14-15") that a player could look up to verify every claim you made
short_description                   1-2 plain sentences, used on the post-round reveal screen
notes                               OPTIONAL object: { "<field_name>": "one clarifying sentence" }.
                                     Used ONLY to explain a "debated"/nuanced value, a name-disambiguation,
                                     or a genuinely interesting caveat. IMPORTANT: notes are shown to the
                                     player only AFTER the round ends (win or lose) — never during play — so
                                     it is safe and encouraged for them to be as specific as needed. Still:
                                     every claim in a note must be accurate and Scripture-supported.
```

## Allowed book names (66-book Protestant canon only — no Apocrypha)

OT: Genesis, Exodus, Leviticus, Numbers, Deuteronomy, Joshua, Judges, Ruth, 1 Samuel,
2 Samuel, 1 Kings, 2 Kings, 1 Chronicles, 2 Chronicles, Ezra, Nehemiah, Esther, Job,
Psalms, Proverbs, Ecclesiastes, Song of Songs, Isaiah, Jeremiah, Lamentations, Ezekiel,
Daniel, Hosea, Joel, Amos, Obadiah, Jonah, Micah, Nahum, Habakkuk, Zephaniah, Haggai,
Zechariah, Malachi

NT: Matthew, Mark, Luke, John, Acts, Romans, 1 Corinthians, 2 Corinthians, Galatians,
Ephesians, Philippians, Colossians, 1 Thessalonians, 2 Thessalonians, 1 Timothy,
2 Timothy, Titus, Philemon, Hebrews, James, 1 Peter, 2 Peter, 1 John, 2 John, 3 John,
Jude, Revelation

## Timeline bands (for `timeline_order`)

Assign an integer within the right band below. Precision beyond "roughly right
relative order" doesn't matter — the game only uses this for fuzzy "before/after
person X" comparisons and treats close values as "too close to call." When in doubt,
use the middle of the band. Keep true contemporaries (e.g. two brothers) close together
or equal.

| Band | Range | Anchor characters already in the database at these values |
|---|---|---|
| Creation | 5-15 | Adam=10, Eve=10 |
| Antediluvian (pre-flood) | 12-24 | (none yet — Cain/Abel/Seth/Enoch/Methuselah/Lamech go here if in your batch) |
| The Flood | 25 | Noah=25 |
| Post-flood/Babel | 27-29 | (Nimrod goes here if in your batch) |
| Patriarchs | 30-39 | Abraham=30 |
| Egypt / Exodus / Conquest | 40-49 | Moses=40, Joshua=41, Caleb=41 |
| Judges period | 50-59 | Ehud=51, Deborah=52, Gideon=53, Samson=55, Ruth=56, Boaz=56, Hannah=57, Eli=58 |
| United Monarchy (Saul/David/Solomon) | 60-69 | Abigail=61, David=62, Nathan=63, Solomon=65 |
| Divided Monarchy, earlier (Elijah–Jonah era) | 70-77 | Elijah=70, Elisha=71, Jehu=73, Jonah=74, Hezekiah=76, Nahum=77 |
| Divided Monarchy, later (Isaiah–last kings of Judah) | 76-87 | Zephaniah=78, Josiah=79, Habakkuk=80, Jeremiah=81 |
| Babylonian Exile | 87-93 | Obadiah=88, Daniel=90 |
| Post-Exile / Persian period | 94-106 | Haggai=95, Zechariah(prophet)=95, Esther=97, Nehemiah=98, Malachi=105 |
| Gospels (Jesus's lifetime) | 108-114 | Jesus=110, Zacchaeus/Martha/Lazarus/Mary Magdalene/Nicodemus=111, Peter/Bartholomew=112 |
| Early Church / Acts / Epistles | 115-130 | Philip the Evangelist=120, Barnabas=121, Paul=122, Priscilla/Aquila=123, Onesimus=124, Timothy=125 |

## Hard rules — do not violate these

1. **Never invent a fact.** If Scripture doesn't say it, the value is `"unknown"` (for
   married/had_children/violent_death) or the field is simply left empty/minimal
   (e.g. `family_members: []`, `occupation: []`). Do not guess.
2. **Every important claim needs a scripture reference** in `scripture_references`.
3. **Disputed/traditional attributions use `"debated"`**, not a confident `"yes"`.
   Explain briefly in `notes`.
4. **No duplicate characters.** You are given the full list of names already in the
   database (existing + all other batches). Do not create an entry for any of them,
   and do not invent a new entry that's secretly the same person under a different
   name — see the disambiguation rule next.
5. **Disambiguate same-name figures deliberately.** The Bible reuses names constantly
   (multiple Marys, Jameses, Johns, Simons, Judes/Judases, Zechariahs, Ananiases...).
   For every name in your batch that could be confused with another biblical figure
   (in your batch, another batch, or the existing 53), you MUST:
   - give it a distinct, specific `id` (e.g. `james_son_of_zebedee`, not `james`)
   - list the disambiguating fact in `alternate_names` or `notes.name`
   - add a one-line `notes.name` explaining which figure this is and how they differ
     from the others sharing the name (e.g. "Distinct from James son of Zebedee and
     James son of Alphaeus, both among the Twelve.")
   Never merge two distinct biblical figures into one entry, and never split one
   figure into two entries under different names (e.g. Bartholomew/Nathanael in the
   existing data is treated as ONE entry with a note about the traditional
   identification — follow that pattern).
6. **Difficulty is pre-assigned per name in your batch — use it as given.** Don't
   second-guess it into a different tier.
7. **Keep it playable.** Every character needs enough concrete (non-"unknown") fields
   that a player asking good questions could actually identify them — don't leave
   more than a few fields as "unknown"/empty unless Scripture is genuinely that
   sparse about the person (that's fine for a few deliberately obscure entries, but
   should be the exception, not the rule).

## Worked example (existing character, follow this style exactly)

```json
{
  "id": "gideon", "name": "Gideon", "alternate_names": ["Jerubbaal"],
  "testament": "OT", "gender": "M", "era": "Judges", "approximate_period": "Traditional 12th century BC",
  "timeline_order": 53,
  "before_or_after_flood": "after", "before_or_after_first_temple": "before", "before_or_after_babylonian_exile": "before",
  "occupation": ["Farmer", "Judge / military deliverer"], "roles": ["Judge of Israel", "Military leader"],
  "king": "no", "judge": "yes", "prophet": "no", "priest": "no", "disciple": "no", "apostle": "no",
  "wrote_biblical_book": "no", "genealogy_recorded": false,
  "family_members": ["Father: Joash", "Many wives", "70 sons", "Son by concubine: Abimelech"],
  "associated_people": ["The Midianites", "Abimelech"],
  "associated_events": ["The sign of the fleece", "Reducing his army to 300 men", "Defeating the Midianites with trumpets and jars", "Making a golden ephod that became a snare"],
  "books_mentioned_in": ["Judges", "Hebrews"],
  "good_bad_neutral": "mixed", "married": "yes", "had_children": "yes", "violent_death": "no",
  "difficulty": "medium",
  "scripture_references": ["Judges 6-8", "Hebrews 11:32"],
  "short_description": "Called by an angel while threshing wheat in hiding, Gideon led Israel to victory over the Midianites with just 300 men, though he later made a golden ephod that led Israel into idolatry.",
  "notes": { "king": "Israel offered to make Gideon king after his victory, but he refused, saying \"the LORD will rule over you\" (Judges 8:22-23)." }
}
```

## Existing 53 characters already in the database — do NOT duplicate any of these

Adam, Eve, Noah, Abraham, Moses, David, Solomon, Daniel, Samson, Jonah, Jesus, Peter,
Paul, Bartholomew (= traditional Nathanael, one entry), Nathan (the prophet), Deborah,
Gideon, Joshua, Caleb, Ruth, Esther, Nehemiah, Nicodemus, Barnabas, Timothy, Elijah,
Elisha, Jehu, Hezekiah, Josiah, Jeremiah, Hannah, Eli, Abigail, Boaz, Zacchaeus, Martha,
Lazarus, Mary Magdalene, Obadiah, Nahum, Habakkuk, Zephaniah, Haggai, Zechariah (the
prophet — distinct from Zechariah father of John the Baptist, which is a NEW character
in this expansion), Malachi, Jael, Phinehas, Ehud, Onesimus, Priscilla, Aquila, Philip
the Evangelist (distinct from Philip the Apostle, which is a NEW character in this
expansion).
