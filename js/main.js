import { GameRound } from './game/gameState.js';
import { recordGameResult, loadStats } from './game/stats.js';
import { renderHome } from './ui/home.js';
import { renderGame } from './ui/game.js';
import { renderResult } from './ui/result.js';
import { renderStats } from './ui/stats.js';

const app = document.getElementById('app');

const state = {
  view: 'home', // 'home' | 'playing' | 'result' | 'stats'
  selectedDifficulty: 'easy',
  round: null,
  resultRecorded: false,
  previousView: 'home', // where "back" from stats should return to
};

function render() {
  if (state.view === 'home') {
    renderHome(app, {
      selectedDifficulty: state.selectedDifficulty,
      onSelectDifficulty: (d) => {
        state.selectedDifficulty = d;
        render();
      },
      onStart: startGame,
      onViewStats: () => goToStats('home'),
    });
  } else if (state.view === 'playing') {
    renderGame(app, {
      round: state.round,
      onAsk: handleAsk,
      onGuess: handleGuess,
      onRestart: startGame,
      onQuit: () => { state.view = 'home'; render(); },
    });
  } else if (state.view === 'result') {
    renderResult(app, {
      round: state.round,
      onPlayAgain: startGame,
      onChangeDifficulty: () => { state.view = 'home'; render(); },
      onViewStats: () => goToStats('result'),
    });
  } else if (state.view === 'stats') {
    renderStats(app, {
      stats: loadStats(),
      onBack: () => { state.view = state.previousView; render(); },
    });
  }
}

function goToStats(from) {
  state.previousView = from;
  state.view = 'stats';
  render();
}

function startGame() {
  state.round = new GameRound(state.selectedDifficulty, 'classic');
  state.resultRecorded = false;
  state.view = 'playing';
  render();
}

function handleAsk(text) {
  state.round.askQuestion(text);
  checkForRoundEnd();
  render();
}

function handleGuess(text) {
  state.round.makeGuess(text);
  checkForRoundEnd();
  render();
}

function checkForRoundEnd() {
  const { status } = state.round;
  if ((status === 'won' || status === 'lost') && !state.resultRecorded) {
    state.resultRecorded = true;
    recordGameResult({
      difficulty: state.round.difficulty,
      won: status === 'won',
      questionsUsed: state.round.questionsUsed,
      characterId: state.round.character.id,
    });
  }
  if (status === 'won' || status === 'lost') {
    state.view = 'result';
  }
}

render();
