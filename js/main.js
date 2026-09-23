import * as api from './api.js';
import { recordGameResult, loadStats } from './game/stats.js';
import { renderHome } from './ui/home.js';
import { renderGame } from './ui/game.js';
import { renderResult } from './ui/result.js';
import { renderStats } from './ui/stats.js';

const app = document.getElementById('app');

const state = {
  view: 'home', // 'home' | 'playing' | 'result' | 'stats'
  selectedDifficulty: 'easy',
  round: null, // { roundId, difficulty, maxQuestions, questionsUsed, questionsRemaining, status, history: [] }
  reveal: null, // set once the round ends — see api.fetchReveal
  busy: false,
  resultRecorded: false,
  previousView: 'home',
};

function render() {
  if (state.view === 'home') {
    renderHome(app, {
      selectedDifficulty: state.selectedDifficulty,
      onSelectDifficulty: (d) => { state.selectedDifficulty = d; render(); },
      onStart: startGame,
      onViewStats: () => goToStats('home'),
    });
  } else if (state.view === 'playing') {
    renderGame(app, {
      round: state.round,
      busy: state.busy,
      onAsk: handleAsk,
      onGuess: handleGuess,
      onRestart: startGame,
      onQuit: () => { state.view = 'home'; render(); },
    });
  } else if (state.view === 'result') {
    renderResult(app, {
      round: state.round,
      reveal: state.reveal,
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

async function startGame() {
  state.busy = true;
  state.view = 'playing';
  state.round = { roundId: null, difficulty: state.selectedDifficulty, maxQuestions: 21, questionsUsed: 0, questionsRemaining: 21, status: 'playing', history: [] };
  state.reveal = null;
  state.resultRecorded = false;
  render();
  try {
    const round = await api.createRound(state.selectedDifficulty);
    state.round = { ...round, history: [] };
  } catch (e) {
    state.round.history.push({ kind: 'unrecognized', text: `Couldn't start a new round: ${e.message}` });
  }
  state.busy = false;
  render();
}

async function handleAsk(text) {
  if (state.busy) return;
  state.busy = true;
  render();
  try {
    const res = await api.askQuestion(state.round.roundId, text);
    state.round = { ...state.round, ...res.round, history: [...state.round.history, res.entry] };
  } catch (e) {
    state.round.history.push({ kind: 'unrecognized', text: `Something went wrong: ${e.message}` });
  }
  state.busy = false;
  await maybeEndRound();
  render();
}

async function handleGuess(text) {
  if (state.busy) return;
  state.busy = true;
  render();
  try {
    const res = await api.makeGuess(state.round.roundId, text);
    state.round = { ...state.round, ...res.round, history: [...state.round.history, res.entry] };
  } catch (e) {
    state.round.history.push({ kind: 'unrecognized', text: `Something went wrong: ${e.message}` });
  }
  state.busy = false;
  await maybeEndRound();
  render();
}

async function maybeEndRound() {
  const { status } = state.round;
  if (status !== 'won' && status !== 'lost') return;

  try {
    state.reveal = await api.fetchReveal(state.round.roundId);
  } catch {
    state.reveal = null;
  }

  if (!state.resultRecorded) {
    state.resultRecorded = true;
    recordGameResult({
      difficulty: state.round.difficulty,
      won: status === 'won',
      questionsUsed: state.round.questionsUsed,
      characterId: state.reveal ? state.reveal.name : 'unknown',
    });
  }
  state.view = 'result';
}

render();
