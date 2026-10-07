from datetime import datetime, timezone
from threading import Lock

_states = {}
_lock = Lock()


def _state(interview_id: str):
    return _states.setdefault(
        interview_id,
        {
            "interview_id": interview_id,
            "updated_at": None,
            "latest_analysis": {},
            "latest_window": {},
        },
    )


def update_analysis(interview_id: str, analysis: dict):
    with _lock:
        state = _state(interview_id)
        if isinstance(analysis, dict):
            state["latest_analysis"].update(analysis)
        else:
            state["latest_analysis"] = {}
        state["updated_at"] = datetime.now(timezone.utc).isoformat()
        return dict(state)


def update_window(interview_id: str, window: dict):
    with _lock:
        state = _state(interview_id)
        state["latest_window"] = window or {}
        state["updated_at"] = datetime.now(timezone.utc).isoformat()
        return dict(state)


def get_state(interview_id: str):
    with _lock:
        state = _states.get(interview_id)
        if state is None:
            return {
                "interview_id": interview_id,
                "updated_at": None,
                "latest_analysis": {},
                "latest_window": {},
            }
        return dict(state)


def clear_state(interview_id: str):
    with _lock:
        _states.pop(interview_id, None)
