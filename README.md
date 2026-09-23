# Bible 21 Questions

A Bible-character guessing game. The server secretly picks one of 218 named
Bible characters; you ask up to 21 yes/no questions to identify them, then guess.

- **Play:** ask things like "Were you a king?", "Did you write a book of the
  Bible?", "Did you live before the Babylonian exile?" — or type a free-form
  question and the AI fallback will take a swing at it.
- **Four difficulty tiers:** Easy, Medium, Hard, Expert — from Adam and David to
  minor prophets and one-verse Pauline companions.
- **The secret character never reaches your browser.** It lives only in server
  memory for the life of your round; the page you're looking at only ever gets
  a yes/no/sometimes/unknown answer, never the character data itself.

## Quick start (local)

Requires Python 3.10+.

```bash
cd server
pip install -r requirements.txt
python3 app.py
```

Open **http://localhost:8778**. That's it — one process serves both the static
frontend and the game API, so there's nothing else to run and no CORS to
configure.

The AI fallback is optional. Without an API key configured, the game still
plays fully on the ~24 rule-based question types; anything outside that just
gets a friendly "I didn't understand that" instead of an AI-backed answer. To
enable it, copy `.env.example` to `.env` in the project root and set
`AI_API_KEY` (see [Configuring the AI fallback](#configuring-the-ai-fallback)).

## How the game works

1. `POST /api/rounds` picks a random character from the chosen difficulty tier
   and returns a `roundId` — nothing else.
2. Every question goes to `POST /api/rounds/<id>/questions`. The server tries
   a rule-based engine first (~24 structured question types: testament,
   gender, king/prophet/priest/judge/disciple/apostle, wrote a book,
   good/bad, married, had children, violent death, before/after the Flood /
   First Temple / Babylonian exile, and "did you live before/after
   `<other person>`"). If that doesn't confidently match, it falls back to an
   AI classifier (see below). Either way, the response is only ever
   `{type, label, hint}` — `hint`, when present, is a fixed generic sentence
   ("This depends on how the term 'king' is defined.") that's identical for
   every character who could produce that answer, so it can never single one
   out.
3. `POST /api/rounds/<id>/guess` checks a guess against the secret character's
   name (or a known alternate name) server-side.
4. `GET /api/rounds/<id>/reveal` only works once the round has ended (won or
   lost) — it 403s otherwise. Only then do you get the character's name,
   description, and scripture references.

A question that the engine (and AI fallback) can't answer doesn't cost you one
of your 21 — you just get nudged to rephrase.

## Project structure

```
bible-21-questions/
├── index.html, css/, js/          the frontend — a thin API client, no game
│                                   logic or character data of its own
│   ├── js/api.js                  fetch wrappers for the API below
│   ├── js/ui/                     screen renderers (home/game/result/stats)
│   └── js/game/stats.js           personal stats, kept in the browser's
│                                   localStorage (games played/won, streaks,
│                                   per-difficulty win rate) — this one stays
│                                   client-side since it's just your own history
├── data/
│   ├── characters.json            the full 218-character database (single
│   │                               source of truth, loaded by the server)
│   └── authoring/                 how the database was built and how to
│       ├── AUTHORING_SPEC.md      extend it: full field/schema reference,
│       └── MASTER_LIST.md         timeline conventions, and the hard rules
│                                   (no invented facts, mark unknowns honestly,
│                                   disambiguate reused names deliberately)
└── server/                        Flask backend — the only thing that ever
    ├── app.py                     sees the secret character
    ├── data_loader.py             loads data/characters.json once at startup
    ├── game_store.py              in-memory round state (see caveat below)
    ├── question_bank.py           the ~24 rule-based question handlers
    ├── question_engine.py         parses free text, tries the bank, resolves
    │                               "before/after <person>" via timeline_order
    ├── ai_fallback.py             the AI-backed fallback (see below)
    ├── answer_types.py            Yes/No/Sometimes/Unknown formatting —
    │                               the one place the "never leak" rule lives
    ├── validate_data.py           standalone database validator (see below)
    └── requirements.txt
```

### Why the frontend has no character data

Earlier versions of this game ran entirely in the browser, which meant the
"secret" character was sitting in plain JavaScript memory the whole time —
inspectable by anyone who opened devtools. Every game rule now lives on the
server; the browser only ever holds a `roundId` and whatever the server chose
to tell it. See [Secret-character protection](#secret-character-protection)
for the specifics.

## The character database

`data/characters.json` has 218 characters (25 easy / 55 medium / 61 hard / 77
expert; 141 Old Testament / 77 New Testament), each with the full schema
described in `data/authoring/AUTHORING_SPEC.md`: testament, gender, era,
occupation, roles, king/judge/prophet/priest/disciple/apostle (yes/no/debated),
whether they wrote a Bible book, genealogy, family, associated people/events,
every book they're mentioned in, a good/bad/mixed/neutral read, married/had
children/died violently (yes/no/unknown), and 1+ scripture references for
every entry. Nothing is invented — where Scripture doesn't say, the field is
honestly `"unknown"`, and disputed points (e.g. "was Jesus a king?", "did
Solomon really write that?") are `"debated"` rather than a confident guess.

The Bible reuses names constantly — this database has two Ananiases, two
Zechariahs, three Jameses, and a Paul/Saul, a Levi/Matthew, and a Barnabas/
Joseph, all deliberately disambiguated with distinct ids and a `notes.name`
explaining who's who (see `AUTHORING_SPEC.md` rule 5 if you're adding more).

### Validating the database

```bash
cd server
python3 validate_data.py
```

Checks: missing required fields, invalid enum values, duplicate ids, missing
scripture references, unrecognized book names, a few cross-field
contradiction checks, and flags every case where two different characters
share a name or alternate name (so you can confirm it's a deliberate,
disambiguated case and not an accidental collision). Exits non-zero on any
error; the current database passes clean (5 expected name-collision warnings,
all reviewed and intentional).

## Configuring the AI fallback

The rule-based engine handles the ~24 structured question types. Anything else
("Did you have anything to do with the construction of the Temple?") goes to
an AI classifier — but only ever comes back as one of four words.

1. Get an API key from [console.anthropic.com](https://console.anthropic.com/).
2. Copy `.env.example` to `.env` in the project root and set `AI_API_KEY`.
3. Restart the server.

**Architecture:**

```
Player question → rule engine → confidently matched? → answer, done
                        ↓ no
                  AI fallback (server/ai_fallback.py)
                        ↓
        strict system prompt + the character's structured data
                        ↓
        raw model output, parsed & validated server-side
                        ↓
        exactly one of YES / NO / SOMETIMES / UNKNOWN
                        ↓
              frontend shows only the bare category
```

The system prompt explicitly tells the model to distinguish explicitly-stated
Scripture from inference, tradition, and disputed interpretation, to answer
UNKNOWN whenever it isn't confident, and to never explain itself or name the
character. The raw model response is never sent to the browser — the server
parses it against exactly four allowed tokens and **separately** scans it for
the secret character's name or any alternate name; if either check fails
(garbage output, a name slipped in despite the prompt, a network error), the
answer is forced to `UNKNOWN` server-side before anything is returned. See
`server/ai_fallback.py` for the actual sanitization code, and its
`answer_question()` for how a caught leak degrades safely instead of
crashing the round.

## Secret-character protection

- The character lives in `server/game_store.py`'s in-memory round dict and is
  never serialized into an API response — every route builds its response
  through `public_round_view` / `public_entry_view` / `public_reveal` in
  `server/app.py`, which only ever pull out the specific safe fields.
- `GET /api/rounds/<id>/reveal` 403s until the round has ended.
- In-round answers carry no character-specific text — only a fixed type
  (yes/no/sometimes/unknown) and, for "sometimes", a generic hint that's
  identical across every character who could produce it (see
  `answer_types.py`'s module docstring for why).
- The AI fallback's raw output is sanitized server-side (above) before it's
  ever forwarded.
- No console/debug output anywhere in the frontend touches game state.

**Caveat worth knowing:** `game_store.py` keeps rounds in a single process's
memory. That's correct and simple for one instance, but it means (a) restarting
the server clears in-progress rounds, and (b) you cannot run this behind a
multi-worker/multi-instance setup without first moving round state to
something shared like Redis — the deployment config below pins the server to
a single worker specifically because of this.

## Deployment

**Recommended: [Render](https://render.com).** Reasoning: this app is a
single stateful Python process (in-memory round storage, no database), not a
static site or a set of independent serverless functions. Platforms built
around serverless functions (Vercel, Netlify, Cloudflare Workers) would run
each request in a fresh, isolated instance — game state would randomly vanish
between your question and the server's answer. Render (and similarly Railway
or Fly.io) instead runs one long-lived container, which is exactly what this
needs, and it has a free tier, git-push deploys, environment variables, and
automatic HTTPS out of the box.

A `render.yaml` is already in the repo:

1. Push this repo to GitHub (see below).
2. On Render: **New → Blueprint**, point it at the repo. It reads
   `render.yaml` automatically.
3. Set the `AI_API_KEY` environment variable in the Render dashboard (it's
   marked `sync: false` in the blueprint specifically so it's never stored in
   the repo — you enter it once in Render's UI).
4. Deploy. Render gives you an `https://<name>.onrender.com` URL.

The free tier spins down after inactivity (a ~30-60s cold start on the next
visit) — fine for a hobby project; upgrade to a paid instance if you want it
always warm. A `Procfile` is also included for Railway/Heroku-style platforms
that prefer that convention instead.

**Note on scaling:** the blueprint pins `--workers 1` deliberately (see the
in-memory caveat above). If this ever needs to handle serious concurrent
traffic, move `game_store.py`'s dict to Redis first, then remove that pin.

## What's next

- Daily Character, Timed, Streak, and the other modes described in the
  original design are intentionally not built yet — `server/game_store.py`'s
  round shape and `js/api.js` were kept narrow on purpose so they're additive,
  not a rewrite.
- Rate limiting on the API isn't implemented — fine for a hobby deployment,
  worth adding (e.g. Flask-Limiter) before wide public traffic.
- Moving round state to Redis, as above, if this ever needs multiple workers.
