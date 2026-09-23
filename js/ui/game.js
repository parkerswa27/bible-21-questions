import { SUGGESTED_QUESTIONS } from '../data/suggestedQuestions.js';

function answerClass(type) {
  return `answer-${type}`;
}

function renderHistory(history) {
  if (history.length === 0) return '';
  return history.map((entry) => {
    if (entry.kind === 'question') {
      return `
        <div class="entry">
          <div class="entry__q"><span class="entry__q-num">Q${entry.questionNumber}</span>${escapeHtml(entry.text)}</div>
          <div class="entry__a ${answerClass(entry.answer.type)}" role="status">${formatAnswerHtml(entry.answer)}</div>
        </div>`;
    }
    if (entry.kind === 'guess') {
      return `
        <div class="entry entry--guess">
          <div class="entry__q">🤔 Guess: <strong>${escapeHtml(entry.text)}</strong></div>
          <div class="entry__a ${entry.correct ? 'correct' : 'incorrect'}">${entry.correct ? 'That\'s correct! 🎉' : 'Not quite — keep asking!'}</div>
        </div>`;
    }
    // unrecognized question — doesn't consume a question slot
    return `
      <div class="entry entry--system">
        <div class="entry__q">${escapeHtml(entry.text)}</div>
        <div class="entry__a">I couldn't parse that as a yes/no question (it didn't cost you a question). Try rephrasing, or tap a suggestion below.</div>
      </div>`;
  }).join('');
}

function formatAnswerHtml(answer) {
  const emoji = answer.emoji ? `${answer.emoji} ` : '';
  const note = answer.hint ? ` <span class="answer-note">${escapeHtml(answer.hint)}</span>` : '';
  return `${emoji}${escapeHtml(answer.label)}.${note}`;
}

function escapeHtml(str) {
  const div = document.createElement('div');
  div.textContent = str;
  return div.innerHTML;
}

export function renderGame(root, { round, busy, onAsk, onGuess, onRestart, onQuit }) {
  const pctUsed = Math.min(100, Math.round((round.questionsUsed / round.maxQuestions) * 100));
  const disabled = round.status !== 'playing' || !!busy;

  root.innerHTML = `
    <div class="game">
      <div class="card game__header">
        <span class="game__badge">${round.difficulty}</span>
        <div class="game__counter">
          <div class="game__counter-num">${round.questionsUsed} <span style="font-size:1.1rem;color:var(--color-text-faint);">/ ${round.maxQuestions}</span></div>
          <div class="game__counter-label">Questions asked</div>
        </div>
      </div>
      <div class="progress-track"><div class="progress-fill" style="width:${pctUsed}%"></div></div>

      <div class="card history" id="history" aria-live="polite">${renderHistory(round.history)}</div>

      <div class="card composer">
        <div class="composer__row">
          <label class="visually-hidden" for="question-input">Type a yes/no question</label>
          <input type="text" id="question-input" class="composer__input" placeholder="Ask a yes/no question… e.g. “Were you a king?”" ${disabled ? 'disabled' : ''} autocomplete="off" />
        </div>
        <div class="composer__actions">
          <button type="button" class="btn btn-primary" id="ask-btn" ${disabled ? 'disabled' : ''}>Ask Question</button>
          <button type="button" class="btn btn-secondary" id="guess-btn" ${disabled ? 'disabled' : ''}>Guess Character</button>
        </div>
        <div class="suggested">
          ${SUGGESTED_QUESTIONS.map((q) => `<button type="button" class="chip" data-q="${escapeHtml(q)}" ${disabled ? 'disabled' : ''}>${escapeHtml(q)}</button>`).join('')}
        </div>
        <div class="composer__hint">${busy ? 'Thinking…' : `${round.questionsRemaining} question${round.questionsRemaining === 1 ? '' : 's'} remaining. Guessing doesn't use up a question.`}</div>
      </div>

      <div class="game__footer">
        <button type="button" class="btn-ghost" id="restart-link">Restart round</button>
        <button type="button" class="btn-ghost" id="quit-link">Change difficulty</button>
      </div>
    </div>
  `;

  const input = root.querySelector('#question-input');
  const historyEl = root.querySelector('#history');
  historyEl.scrollTop = historyEl.scrollHeight;

  const doAsk = () => {
    if (!input.value.trim()) return;
    onAsk(input.value);
    input.value = '';
  };
  const doGuess = () => {
    if (!input.value.trim()) {
      input.placeholder = 'Type the character\'s name, then press “Guess Character”…';
      input.focus();
      return;
    }
    onGuess(input.value);
    input.value = '';
  };

  root.querySelector('#ask-btn').addEventListener('click', doAsk);
  root.querySelector('#guess-btn').addEventListener('click', doGuess);
  input.addEventListener('keydown', (e) => {
    if (e.key === 'Enter') doAsk();
  });
  root.querySelectorAll('.chip').forEach((chip) => {
    chip.addEventListener('click', () => onAsk(chip.dataset.q));
  });
  root.querySelector('#restart-link').addEventListener('click', onRestart);
  root.querySelector('#quit-link').addEventListener('click', onQuit);

  if (!disabled) input.focus();
}
