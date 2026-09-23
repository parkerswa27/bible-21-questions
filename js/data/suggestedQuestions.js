// Static suggested-question chips for the game screen. This is UI sugar only —
// the actual question text still goes through the server's rule engine / AI
// fallback like any typed question. Kept separate from game logic on purpose:
// the frontend has no game logic of its own anymore (see js/api.js).
export const SUGGESTED_QUESTIONS = [
  'Are you from the Old Testament?',
  'Are you a woman?',
  'Were you a king?',
  'Were you a prophet?',
  'Did you write a book of the Bible?',
  'Are you generally considered a good character?',
  'Were you married?',
  'Did you live before the Babylonian exile?',
];
