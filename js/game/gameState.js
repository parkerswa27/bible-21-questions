import { getCharactersForDifficulty, ALL_CHARACTERS } from '../data/characters.js';
import { answerQuestion, checkGuess } from '../engine/questionEngine.js';
import { getMode } from './modes.js';

// A single round of (currently only) Classic 21 Questions. Framed as a small class
// rather than a framework-specific store so it stays reusable if a future mode
// wraps or subclasses it (e.g. Timed Mode swapping the win/lose condition).
export class GameRound {
  constructor(difficulty, modeId = 'classic') {
    this.difficulty = difficulty;
    this.mode = getMode(modeId);
    this.maxQuestions = this.mode.maxQuestions || 21;
    this.pool = getCharactersForDifficulty(difficulty);
    if (this.pool.length === 0) throw new Error(`No characters available for difficulty "${difficulty}"`);
    this.character = this.pool[Math.floor(Math.random() * this.pool.length)];
    this.questionsUsed = 0;
    this.history = []; // { kind: 'question'|'guess'|'unrecognized', text, answer?, correct? }
    this.status = 'playing'; // 'playing' | 'won' | 'lost'
  }

  get questionsRemaining() {
    return Math.max(0, this.maxQuestions - this.questionsUsed);
  }

  askQuestion(rawText) {
    if (this.status !== 'playing') return null;
    const trimmed = rawText.trim();
    if (!trimmed) return null;

    const result = answerQuestion(trimmed, this.character, ALL_CHARACTERS);

    if (!result.matched) {
      const entry = { kind: 'unrecognized', text: trimmed };
      this.history.push(entry);
      return entry;
    }

    this.questionsUsed += 1;
    const entry = { kind: 'question', text: trimmed, answer: result.answer, questionNumber: this.questionsUsed };
    this.history.push(entry);

    if (this.questionsUsed >= this.maxQuestions) {
      this.status = 'lost';
    }
    return entry;
  }

  makeGuess(rawText) {
    if (this.status !== 'playing') return null;
    const trimmed = rawText.trim();
    if (!trimmed) return null;

    const correct = checkGuess(trimmed, this.character);
    const entry = { kind: 'guess', text: trimmed, correct };
    this.history.push(entry);

    if (correct) this.status = 'won';
    return entry;
  }
}
