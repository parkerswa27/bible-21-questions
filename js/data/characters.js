import { EASY_CHARACTERS } from './characters.easy.js';
import { MEDIUM_CHARACTERS } from './characters.medium.js';
import { HARD_CHARACTERS } from './characters.hard.js';
import { EXPERT_CHARACTERS } from './characters.expert.js';

export const ALL_CHARACTERS = [
  ...EASY_CHARACTERS,
  ...MEDIUM_CHARACTERS,
  ...HARD_CHARACTERS,
  ...EXPERT_CHARACTERS,
];

export const CHARACTERS_BY_DIFFICULTY = {
  easy: EASY_CHARACTERS,
  medium: MEDIUM_CHARACTERS,
  hard: HARD_CHARACTERS,
  expert: EXPERT_CHARACTERS,
};

export function getCharactersForDifficulty(difficulty) {
  return CHARACTERS_BY_DIFFICULTY[difficulty] || [];
}

export function findCharacterByName(query) {
  const q = query.trim().toLowerCase();
  if (!q) return null;
  return (
    ALL_CHARACTERS.find((c) => c.name.toLowerCase() === q) ||
    ALL_CHARACTERS.find((c) => c.alternate_names.some((a) => a.toLowerCase() === q)) ||
    ALL_CHARACTERS.find((c) => c.name.toLowerCase().includes(q) && q.length >= 3) ||
    null
  );
}
