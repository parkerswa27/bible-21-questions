"""In-memory per-IP rate limiting for AI-fallback calls specifically (the rule
engine is free — only AI calls cost real money, so only they're limited here).

Same storage model as game_store.py: a single process's memory, fine for the
single-worker deployment this project targets (see render.yaml). If this ever
scales to multiple workers/instances, move this to Redis alongside game_store's
round state — a per-process counter can't enforce a shared limit across processes.
"""

import os
import threading
import time
from collections import defaultdict, deque

MAX_AI_CALLS_PER_IP_PER_HOUR = int(os.environ.get("AI_MAX_CALLS_PER_IP_PER_HOUR", "100"))
WINDOW_SECONDS = 60 * 60

_calls_by_ip = defaultdict(deque)  # ip -> deque of call timestamps, oldest first
_lock = threading.Lock()


def allow_ai_call(ip):
    """Returns True and records the call if `ip` is under its hourly budget;
    returns False (recording nothing) if the caller should be denied."""
    ip = ip or "unknown"
    now = time.time()
    cutoff = now - WINDOW_SECONDS

    with _lock:
        timestamps = _calls_by_ip[ip]
        while timestamps and timestamps[0] < cutoff:
            timestamps.popleft()

        if len(timestamps) >= MAX_AI_CALLS_PER_IP_PER_HOUR:
            if not timestamps:
                del _calls_by_ip[ip]
            return False

        timestamps.append(now)
        return True


def reset():
    """Test-only helper."""
    with _lock:
        _calls_by_ip.clear()
