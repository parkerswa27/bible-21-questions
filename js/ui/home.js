const DIFFICULTY_INFO = {
  easy: { label: 'Easy', desc: 'Very recognizable Bible characters — Adam, Moses, David, Jesus.' },
  medium: { label: 'Medium', desc: 'Recognizable but less obvious — Ruth, Gideon, Esther, Timothy.' },
  hard: { label: 'Hard', desc: 'Less famous — you\'ll need sharper questions to pin them down.' },
  expert: { label: 'Expert', desc: 'Minor prophets, obscure kings and priests, and other named figures.' },
};

export function renderHome(root, { selectedDifficulty, onSelectDifficulty, onStart, onViewStats }) {
  root.innerHTML = `
    <div class="home">
      <div class="ornament"><span>A Bible Guessing Game</span></div>
      <h1 class="home__title">Bible <span class="accent">21</span> Questions</h1>
      <p class="home__subtitle">A secret Bible character is waiting to be discovered. Ask up to 21 yes/no questions, then make your guess.</p>

      <div class="card home__panel">
        <div class="section-label">Choose a difficulty</div>
        <div class="difficulty-grid" id="difficulty-grid">
          ${Object.entries(DIFFICULTY_INFO).map(([key, info]) => `
            <button type="button" class="difficulty-card" data-difficulty="${key}" aria-pressed="${key === selectedDifficulty}">
              <div class="difficulty-card__name"><span class="difficulty-dot dot-${key}"></span>${info.label}</div>
              <div class="difficulty-card__desc">${info.desc}</div>
            </button>
          `).join('')}
        </div>
        <button type="button" class="btn btn-primary btn-block" id="start-btn">Start Game</button>
      </div>

      <div class="home__nav">
        <button type="button" class="btn-ghost" id="stats-link">View Statistics</button>
      </div>
    </div>
  `;

  root.querySelectorAll('.difficulty-card').forEach((cardEl) => {
    cardEl.addEventListener('click', () => onSelectDifficulty(cardEl.dataset.difficulty));
  });
  root.querySelector('#start-btn').addEventListener('click', onStart);
  root.querySelector('#stats-link').addEventListener('click', onViewStats);
}
