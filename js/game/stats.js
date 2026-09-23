// localStorage-backed statistics. Kept as a small isolated module so it can be
// swapped for a server-backed store later without touching the game logic.

const STORAGE_KEY = 'bible21q_stats_v1';
const DIFFICULTIES = ['easy', 'medium', 'hard', 'expert'];

function emptyStats() {
  const perDifficulty = {};
  for (const d of DIFFICULTIES) perDifficulty[d] = { played: 0, won: 0 };
  return {
    gamesPlayed: 0,
    gamesWon: 0,
    totalQuestionsOnWins: 0,
    currentStreak: 0,
    longestWinStreak: 0,
    perDifficulty,
    guessedCharacterIds: [],
  };
}

export function loadStats() {
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    if (!raw) return emptyStats();
    const parsed = JSON.parse(raw);
    // merge with defaults so older/newer shapes don't crash the UI
    return { ...emptyStats(), ...parsed, perDifficulty: { ...emptyStats().perDifficulty, ...(parsed.perDifficulty || {}) } };
  } catch {
    return emptyStats();
  }
}

function saveStats(stats) {
  try {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(stats));
  } catch {
    // localStorage unavailable (private mode, etc.) — fail silently, stats just won't persist
  }
}

export function recordGameResult({ difficulty, won, questionsUsed, characterId }) {
  const stats = loadStats();
  stats.gamesPlayed += 1;
  if (!stats.perDifficulty[difficulty]) stats.perDifficulty[difficulty] = { played: 0, won: 0 };
  stats.perDifficulty[difficulty].played += 1;

  if (won) {
    stats.gamesWon += 1;
    stats.totalQuestionsOnWins += questionsUsed;
    stats.perDifficulty[difficulty].won += 1;
    stats.currentStreak += 1;
    stats.longestWinStreak = Math.max(stats.longestWinStreak, stats.currentStreak);
    if (!stats.guessedCharacterIds.includes(characterId)) stats.guessedCharacterIds.push(characterId);
  } else {
    stats.currentStreak = 0;
  }

  saveStats(stats);
  return stats;
}

export function averageQuestionsUsed(stats) {
  return stats.gamesWon > 0 ? stats.totalQuestionsOnWins / stats.gamesWon : null;
}

export function winRateForDifficulty(stats, difficulty) {
  const d = stats.perDifficulty[difficulty];
  if (!d || d.played === 0) return null;
  return d.won / d.played;
}

export function resetStats() {
  saveStats(emptyStats());
  return emptyStats();
}
