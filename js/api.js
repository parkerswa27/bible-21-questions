// Thin client for the game API (server/app.py). The secret character never
// crosses this boundary — every response here is already the narrow, safe view
// the server decided to expose. See server/app.py's public_round_view /
// public_entry_view / public_reveal for exactly what that is.

async function postJson(url, body) {
  const res = await fetch(url, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body || {}),
  });
  const data = await res.json().catch(() => ({}));
  if (!res.ok) {
    const err = new Error(data.error || `Request failed (${res.status})`);
    err.status = res.status;
    err.data = data;
    throw err;
  }
  return data;
}

async function getJson(url) {
  const res = await fetch(url);
  const data = await res.json().catch(() => ({}));
  if (!res.ok) {
    const err = new Error(data.error || `Request failed (${res.status})`);
    err.status = res.status;
    err.data = data;
    throw err;
  }
  return data;
}

export function fetchDifficulties() {
  return getJson('/api/difficulties');
}

export function createRound(difficulty) {
  return postJson('/api/rounds', { difficulty });
}

export function askQuestion(roundId, question) {
  return postJson(`/api/rounds/${roundId}/questions`, { question });
}

export function makeGuess(roundId, guess) {
  return postJson(`/api/rounds/${roundId}/guess`, { guess });
}

export function fetchReveal(roundId) {
  return getJson(`/api/rounds/${roundId}/reveal`);
}
