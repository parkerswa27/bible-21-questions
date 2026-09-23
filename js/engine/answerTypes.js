// Canonical answer shape returned by every question handler and by the engine.
// type: 'yes' | 'no' | 'sometimes' | 'unknown'
//
// SECURITY / GAME-INTEGRITY RULE: answers returned from here must never be able to
// identify or narrow down the secret character. That means:
//   - No character name, ever.
//   - No per-character `notes` text (character.notes exists for the POST-GAME
//     reveal screen only — see js/ui/result.js — and must never be threaded
//     through to an in-round answer).
//   - The only optional clarifying text allowed is a generic, question-level
//     hint (e.g. "This depends on how the term is defined.") that is identical
//     for every character who could produce that answer, so it can never single
//     one out. Pass it as `hint` from questionBank.js, never derived per-character.

export const DISPLAY_LABEL = {
  yes: 'Yes',
  no: 'No',
  sometimes: 'Sometimes',
  unknown: 'Not enough information',
};

export function makeAnswer(type, { hint } = {}) {
  const label = DISPLAY_LABEL[type] || DISPLAY_LABEL.unknown;
  return {
    type,
    label,
    hint: hint || null,
    text: hint ? `${label}. ${hint}` : `${label}.`,
  };
}

// Maps a tri-state fact field ('yes' | 'no' | 'debated') to an answer.
// `sometimesHint`, if given, must be a generic, question-level sentence — never
// anything derived from the specific character.
export function answerFromTriState(value, { sometimesHint } = {}) {
  if (value === 'yes') return makeAnswer('yes');
  if (value === 'no') return makeAnswer('no');
  if (value === 'debated') return makeAnswer('sometimes', { hint: sometimesHint });
  return makeAnswer('unknown');
}

// Maps a boolean field to a plain yes/no answer.
export function answerFromBoolean(value) {
  return makeAnswer(value ? 'yes' : 'no');
}

// Maps a 'yes' | 'no' | 'unknown' field (married, had_children, violent_death) to an answer.
export function answerFromYesNoUnknown(value) {
  if (value === 'yes') return makeAnswer('yes');
  if (value === 'no') return makeAnswer('no');
  return makeAnswer('unknown');
}

// Maps a before/during/after/spans landmark field, relative to the asked direction.
export function answerFromTimeline(value, direction, { sometimesHint } = {}) {
  if (value === 'spans' || value === 'during') return makeAnswer('sometimes', { hint: sometimesHint });
  if (value === 'na') return makeAnswer('unknown');
  const isBefore = value === 'before';
  const matches = direction === 'before' ? isBefore : !isBefore;
  return makeAnswer(matches ? 'yes' : 'no');
}
