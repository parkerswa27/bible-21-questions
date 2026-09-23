// Rule-based question-answering engine (no external API).
//
// This is intentionally the only implementation for now, but it is written behind
// a single entry point — `answerQuestion(text, character, allCharacters)` — so a
// future AI-backed answerer can be swapped in later (e.g. try the rule-based
// engine first for speed/reliability, fall back to an LLM call for anything it
// doesn't recognize) without touching game/gameState.js or the UI.

import { QUESTION_BANK } from './questionBank.js';
import { makeAnswer } from './answerTypes.js';
import { OT_BOOKS, NT_BOOKS } from '../data/schema.js';

export function normalize(text) {
  return text
    .toLowerCase()
    .replace(/[?.!,;:'"()]/g, ' ')
    .replace(/\byou\b/g, 'you ')
    .replace(/\s+/g, ' ')
    .trim();
}

// "Did you live before/after <name>?" — resolved via each character's timeline_order.
// A gap smaller than this is treated as "too close to call" rather than guessed at.
const TIMELINE_CONFIDENCE_GAP = 3;

function tryNamedComparison(t, character, allCharacters) {
  const direction = /\bbefore\b/.test(t) ? 'before' : /\bafter\b/.test(t) ? 'after' : null;
  if (!direction) return null;

  const candidates = allCharacters
    .filter((c) => c.id !== character.id)
    .filter((c) => {
      const names = [c.name, ...c.alternate_names].map((n) => n.toLowerCase());
      return names.some((n) => n.length >= 3 && t.includes(n));
    });
  if (candidates.length !== 1) return null; // ambiguous or no name found

  const other = candidates[0];
  const diff = character.timeline_order - other.timeline_order;
  if (Math.abs(diff) < TIMELINE_CONFIDENCE_GAP) {
    // Names the character the PLAYER typed, never the secret one — safe.
    return makeAnswer('sometimes', {
      hint: `Our timelines are too close (or overlap) to say for certain relative to ${other.name}.`,
    });
  }
  const livedBefore = diff < 0;
  const matches = direction === 'before' ? livedBefore : !livedBefore;
  return makeAnswer(matches ? 'yes' : 'no');
}

// NOTE: there is deliberately no generic keyword/event fallback here. Guessing an
// answer from loose text matches against associated_events/people/roles risks
// leaking the character (e.g. a "yes" that's only true for one person in the
// roster is itself a strong clue). Anything the QUESTION_BANK can't confidently
// answer falls through to the AI fallback (server-side), which is held to the
// same never-identify rule — see server/ai_fallback.py.

/**
 * @param {string} rawText - the player's typed question
 * @param {import('../data/schema.js').Character} character - the secret character
 * @param {import('../data/schema.js').Character[]} allCharacters - full roster, used to
 *   resolve "before/after <name>" comparisons
 * @returns {{ matched: boolean, questionId?: string, category?: string, answer?: object }}
 */
export function answerQuestion(rawText, character, allCharacters) {
  const t = normalize(rawText);
  if (!t) return { matched: false };

  const comparison = tryNamedComparison(t, character, allCharacters);
  if (comparison) {
    return { matched: true, questionId: 'named_comparison', category: 'Time period', answer: comparison };
  }

  for (const q of QUESTION_BANK) {
    if (q.match(t)) {
      return { matched: true, questionId: q.id, category: q.category, answer: q.evaluate(character) };
    }
  }

  // Cross-testament mention, derived from books_mentioned_in rather than a hand-set flag.
  if (/mentioned\b.*\bnew testament\b/.test(t) || (/\bnew testament\b/.test(t) && /mention/.test(t))) {
    const mentioned = character.testament === 'NT' || character.books_mentioned_in.some((b) => NT_BOOKS.includes(b));
    return { matched: true, questionId: 'mentioned_nt', category: 'Identity', answer: makeAnswer(mentioned ? 'yes' : 'no') };
  }
  if (/mentioned\b.*\bold testament\b/.test(t) || (/\bold testament\b/.test(t) && /mention/.test(t))) {
    const mentioned = character.testament === 'OT' || character.books_mentioned_in.some((b) => OT_BOOKS.includes(b));
    return { matched: true, questionId: 'mentioned_ot', category: 'Identity', answer: makeAnswer(mentioned ? 'yes' : 'no') };
  }

  return { matched: false };
}

export function checkGuess(guessText, character) {
  const g = guessText.trim().toLowerCase();
  if (!g) return false;
  if (character.name.toLowerCase() === g) return true;
  return character.alternate_names.some((a) => a.toLowerCase() === g);
}
