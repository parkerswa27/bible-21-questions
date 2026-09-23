// Game mode registry. Only "classic" is implemented for the MVP; the rest are
// listed so the menu can show them as "coming soon" and so future work has a
// clear slot to land in without restructuring the game loop.
//
// A mode that gets implemented later just needs a `run` entry point (or its own
// small module) plus a flip of `implemented` to true — gameState.js and the UI
// only depend on the shape below, not on "classic" specifically.

export const GAME_MODES = [
  {
    id: 'classic',
    name: 'Classic 21 Questions',
    description: 'Ask up to 21 yes/no questions to identify a secret Bible character.',
    implemented: true,
    maxQuestions: 21,
  },
  { id: 'daily', name: 'Daily Character', description: 'Everyone gets the same secret character each day.', implemented: false },
  { id: 'timed', name: 'Timed Mode', description: 'Race the clock instead of the question count.', implemented: false },
  { id: 'multiplayer', name: 'Multiplayer', description: 'Compete with friends to guess first.', implemented: false },
  { id: 'streak', name: 'Streak Mode', description: 'Keep guessing correctly to build a streak.', implemented: false },
  { id: 'vs', name: 'Character vs Character', description: 'Compare two characters head to head.', implemented: false },
  { id: 'clues', name: 'Guess From Clues', description: 'Identify the character from a list of clues instead of asking questions.', implemented: false },
  { id: 'custom', name: 'Custom Difficulty', description: 'Build your own character pool and rules.', implemented: false },
];

export function getMode(id) {
  return GAME_MODES.find((m) => m.id === id) || GAME_MODES[0];
}
