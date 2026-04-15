"""In-memory task tracker for admin background jobs.

Used by admin endpoints that fire-and-forget long-running work via
asyncio.create_task — the HTTP response returns immediately but the
work keeps going, and there's no way for the frontend to know when
it's actually done without a status endpoint to poll.

This is deliberately simple: a single process-local dict with
task_name -> status info. Safe for Railway's single-worker uvicorn
setup. For multi-worker deployments this would need Redis or a DB
table (every worker would track its own state otherwise).
"""
from __future__ import annotations

from datetime import datetime
from threading import Lock
from typing import Any, Dict, Optional


_state: Dict[str, Dict[str, Any]] = {}
_lock = Lock()


def start_task(name: str) -> None:
    """Mark `name` as running. Clears any prior run state."""
    with _lock:
        _state[name] = {
            "status": "running",
            "started_at": datetime.utcnow().isoformat() + "Z",
            "finished_at": None,
            "duration_seconds": None,
            "result": None,
            "error": None,
        }


def finish_task(name: str, result: Optional[Any] = None) -> None:
    """Mark `name` as done. Computes duration_seconds from started_at."""
    with _lock:
        entry = _state.get(name)
        if not entry:
            return
        now = datetime.utcnow()
        try:
            started = datetime.fromisoformat(entry["started_at"].rstrip("Z"))
            duration = round((now - started).total_seconds(), 1)
        except Exception:
            duration = None
        entry["status"] = "done"
        entry["finished_at"] = now.isoformat() + "Z"
        entry["duration_seconds"] = duration
        # Truncate result if it's too big to keep in memory / ship to frontend
        entry["result"] = _summarize(result)


def fail_task(name: str, error: str) -> None:
    """Mark `name` as errored."""
    with _lock:
        entry = _state.get(name)
        if not entry:
            return
        now = datetime.utcnow()
        try:
            started = datetime.fromisoformat(entry["started_at"].rstrip("Z"))
            duration = round((now - started).total_seconds(), 1)
        except Exception:
            duration = None
        entry["status"] = "error"
        entry["finished_at"] = now.isoformat() + "Z"
        entry["duration_seconds"] = duration
        entry["error"] = str(error)[:500]


def get_all() -> Dict[str, Dict[str, Any]]:
    """Snapshot of all tracked tasks."""
    with _lock:
        return {k: dict(v) for k, v in _state.items()}


def _summarize(result: Any) -> Any:
    """Keep result small — JSON-serializable, top-level counts only."""
    if result is None:
        return None
    if isinstance(result, (str, int, float, bool)):
        return result
    if isinstance(result, dict):
        out = {}
        for k, v in result.items():
            if isinstance(v, (str, int, float, bool, type(None))):
                out[k] = v
            elif isinstance(v, dict):
                # One level of nesting for sub-counts
                out[k] = {
                    kk: vv for kk, vv in v.items()
                    if isinstance(vv, (str, int, float, bool, type(None)))
                }
            elif isinstance(v, list):
                out[k] = f"[{len(v)} items]"
            else:
                out[k] = str(type(v).__name__)
        return out
    if isinstance(result, list):
        return f"[{len(result)} items]"
    return str(result)[:200]
