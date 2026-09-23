import { averageQuestionsUsed, winRateForDifficulty } from '../game/stats.js';

export function renderStats(root, { stats, onBack }) {
  const avg = averageQuestionsUsed(stats);
  const difficulties = ['easy', 'medium', 'hard', 'expert'];

  root.innerHTML = `
    <div class="stats">
      <div class="ornament"><span>Your Progress</span></div>
      <h2 style="text-align:center;margin-bottom:4px;">Statistics</h2>

      <div class="stats__grid">
        <div class="card stat-tile"><div class="stat-tile__num">${stats.gamesPlayed}</div><div class="stat-tile__label">Games Played</div></div>
        <div class="card stat-tile"><div class="stat-tile__num">${stats.gamesWon}</div><div class="stat-tile__label">Games Won</div></div>
        <div class="card stat-tile"><div class="stat-tile__num">${avg !== null ? avg.toFixed(1) : '—'}</div><div class="stat-tile__label">Avg. Questions Used</div></div>
        <div class="card stat-tile"><div class="stat-tile__num">${stats.longestWinStreak}</div><div class="stat-tile__label">Longest Win Streak</div></div>
      </div>

      <div class="card stats__table">
        ${difficulties.map((d) => {
          const rate = winRateForDifficulty(stats, d);
          return `<div class="stats__row"><span class="stats__row-label">${d}</span><span class="stats__row-value">${rate !== null ? `${Math.round(rate * 100)}% win rate (${stats.perDifficulty[d].played} played)` : 'Not played yet'}</span></div>`;
        }).join('')}
        <div class="stats__row"><span class="stats__row-label">Characters guessed</span><span class="stats__row-value">${stats.guessedCharacterIds.length} unique</span></div>
      </div>

      <div class="result__actions">
        <button type="button" class="btn btn-secondary" id="back-btn">Back to Menu</button>
      </div>
    </div>
  `;

  root.querySelector('#back-btn').addEventListener('click', onBack);
}
