export function renderResult(root, { round, onPlayAgain, onChangeDifficulty, onViewStats }) {
  const won = round.status === 'won';
  const c = round.character;

  root.innerHTML = `
    <div class="result">
      <h1 class="result__headline ${won ? 'won' : 'lost'}">${won ? 'You got it! 🎉' : 'You ran out of questions!'}</h1>
      <p class="result__sub">${won
        ? `Solved in ${round.questionsUsed} question${round.questionsUsed === 1 ? '' : 's'} on ${round.difficulty} difficulty.`
        : `The character has been revealed below.`}</p>

      <div class="card result__panel">
        <div class="result__name">${c.name}</div>
        <div class="result__meta">
          <span class="tag">${round.difficulty}</span>
          <span class="tag">${c.testament === 'OT' ? 'Old Testament' : 'New Testament'}</span>
          <span class="tag">${round.questionsUsed} question${round.questionsUsed === 1 ? '' : 's'} used</span>
        </div>
        <p class="result__desc">${c.short_description}</p>
        <div class="result__refs-label">Scripture References</div>
        <div class="result__refs">
          ${c.scripture_references.map((r) => `<span class="ref-chip">${r}</span>`).join('')}
        </div>
      </div>

      <div class="result__actions">
        <button type="button" class="btn btn-primary" id="play-again">Play Again</button>
        <button type="button" class="btn btn-secondary" id="change-difficulty">Change Difficulty</button>
        <button type="button" class="btn-ghost" id="view-stats">View Statistics</button>
      </div>
    </div>
  `;

  root.querySelector('#play-again').addEventListener('click', onPlayAgain);
  root.querySelector('#change-difficulty').addEventListener('click', onChangeDifficulty);
  root.querySelector('#view-stats').addEventListener('click', onViewStats);
}
