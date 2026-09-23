// Character data schema for Bible 21 Questions.
//
// Every character object in js/data/characters.*.js follows this shape.
// Tri/quad-state facts use lowercase string enums instead of booleans so the
// question engine can distinguish a real "no" from "we don't know" or
// "it's debated" — see js/engine/questionEngine.js.
//
// @typedef {Object} Character
// @property {string} id                    - unique slug, e.g. "moses"
// @property {string} name                   - display name
// @property {string[]} alternate_names      - other names/spellings/titles
// @property {'OT'|'NT'} testament
// @property {'M'|'F'} gender
// @property {string} era                    - short label, e.g. "Judges"
// @property {string} approximate_period     - human-readable, e.g. "c. 1000 BC"
// @property {number} timeline_order         - rough chronological rank used only
//     for relative "before/after <person>" questions. Not a claimed date.
// @property {'before'|'after'|'na'} before_or_after_flood
// @property {'before'|'during'|'after'|'na'} before_or_after_first_temple
// @property {'before'|'during'|'after'|'na'} before_or_after_babylonian_exile
// @property {string[]} occupation
// @property {string[]} roles
// @property {'yes'|'no'|'debated'} king
// @property {'yes'|'no'|'debated'} judge
// @property {'yes'|'no'|'debated'} prophet
// @property {'yes'|'no'|'debated'} priest
// @property {'yes'|'no'|'debated'} disciple - a follower of Jesus (broader than the Twelve)
// @property {'yes'|'no'|'debated'} apostle  - one of "the Twelve" or explicitly called an apostle (e.g. Paul)
// @property {'yes'|'no'|'debated'} wrote_biblical_book
// @property {boolean} genealogy_recorded    - a genealogy naming them appears in Scripture
// @property {Object.<string,string>} [notes] - optional short clarifying sentence keyed by
//     fact name (e.g. notes.king), shown alongside "debated" or nuanced answers
// @property {string[]} family_members       - "Relation: Name" strings
// @property {string[]} associated_people
// @property {string[]} associated_events
// @property {string[]} books_mentioned_in   - Bible books where they appear or are named
// @property {'good'|'bad'|'mixed'|'neutral'} good_bad_neutral
// @property {'yes'|'no'|'unknown'} married
// @property {'yes'|'no'|'unknown'} had_children
// @property {'yes'|'no'|'unknown'} violent_death
// @property {'easy'|'medium'|'hard'|'expert'} difficulty
// @property {string[]} scripture_references
// @property {string} short_description

export const OT_BOOKS = [
  'Genesis','Exodus','Leviticus','Numbers','Deuteronomy','Joshua','Judges','Ruth',
  '1 Samuel','2 Samuel','1 Kings','2 Kings','1 Chronicles','2 Chronicles','Ezra',
  'Nehemiah','Esther','Job','Psalms','Proverbs','Ecclesiastes','Song of Songs',
  'Isaiah','Jeremiah','Lamentations','Ezekiel','Daniel','Hosea','Joel','Amos',
  'Obadiah','Jonah','Micah','Nahum','Habakkuk','Zephaniah','Haggai','Zechariah','Malachi',
];

export const NT_BOOKS = [
  'Matthew','Mark','Luke','John','Acts','Romans','1 Corinthians','2 Corinthians',
  'Galatians','Ephesians','Philippians','Colossians','1 Thessalonians','2 Thessalonians',
  '1 Timothy','2 Timothy','Titus','Philemon','Hebrews','James','1 Peter','2 Peter',
  '1 John','2 John','3 John','Jude','Revelation',
];

export const DIFFICULTIES = ['easy', 'medium', 'hard', 'expert'];
