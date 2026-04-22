from .game_state import GameState


class SessionStore:
    def __init__(self) -> None:
        self._sessions: dict[str, GameState] = {}

    def get_session(self, session_id: str) -> GameState | None:
        return self._sessions.get(session_id)

    def save_session(self, state: GameState) -> GameState:
        self._sessions[state.session_id] = state
        return state

    def delete_session(self, session_id: str) -> None:
        self._sessions.pop(session_id, None)
