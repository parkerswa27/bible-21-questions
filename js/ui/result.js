function escapeHtml(str) {
  const div = document.createElement('div');
  div.textContent = str;
  return div.innerHTML;
}

export function renderResult(root, { round, reveal, onPlayAgain, onChangeDifficulty, onViewStats }) {
  const won = round.status === 'won';

  if (!reveal) {
    root.innerHTML = `
      <div class="result">
        <h1 class="result__headline ${won ? 'won' : 'lost'}">${won ? 'You got it! 🎉' : 'You ran out of questions!'}</h1>
        <p class="result__sub">Couldn't load the reveal from the server — you can still start a new round.</p>
        <div class="result__actions">
          <button type="button" class="btn btn-primary" id="play-again">Play Again</button>
          <button type="button" class="btn btn-secondary" id="change-difficulty">Change Difficulty</button>
        </div>
      </div>`;
    root.querySelector('#play-again').addEventListener('click', onPlayAgain);
    root.querySelector('#change-difficulty').addEventListener('click', onChangeDifficulty);
    return;
  }

  const notesEntries = Object.entries(reveal.notes || {});

  root.innerHTML = `
    <div class="result">
      <h1 class="result__headline ${won ? 'won' : 'lost'}">${won ? 'You got it! 🎉' : 'You ran out of questions!'}</h1>
      <p class="result__sub">${won
        ? `Solved in ${reveal.questionsUsed} question${reveal.questionsUsed === 1 ? '' : 's'} on ${reveal.difficulty} difficulty.`
        : `The character has been revealed below.`}</p>

      <div class="card result__panel">
        <div class="result__name">${escapeHtml(reveal.name)}</div>
        <div class="result__meta">
          <span class="tag">${escapeHtml(reveal.difficulty)}</span>
          <span class="tag">${reveal.testament === 'OT' ? 'Old Testament' : 'New Testament'}</span>
          <span class="tag">${reveal.questionsUsed} question${reveal.questionsUsed === 1 ? '' : 's'} used</span>
        </div>
        <p class="result__desc">${escapeHtml(reveal.shortDescription)}</p>
        <div class="result__refs-label">Scripture References</div>
        <div class="result__refs">
          ${reveal.scriptureReferences.map((r) => `<span class="ref-chip">${escapeHtml(r)}</span>`).join('')}
        </div>
        ${notesEntries.length ? `
          <div class="result__refs-label" style="margin-top:16px;">Did You Know?</div>
          <ul class="result__notes">
            ${notesEntries.map(([, note]) => `<li>${escapeHtml(note)}</li>`).join('')}
          </ul>
        ` : ''}
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
