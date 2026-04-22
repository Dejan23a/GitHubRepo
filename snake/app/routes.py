from flask import Blueprint, current_app, jsonify, render_template, request


api_blueprint = Blueprint("snake", __name__)


def _services():
    return current_app.extensions["snake_services"]


def _session_or_404(session_id: str):
    session_store = _services()["session_store"]
    state = session_store.get_session(session_id)
    if state is None:
        return None, (jsonify({"error": "Session not found."}), 404)
    return state, None


def _json_payload():
    return request.get_json(silent=True) or {}


@api_blueprint.get("/")
def index():
    return render_template("index.html")


@api_blueprint.post("/api/game/session")
def create_session():
    services = _services()
    last_player_name = services["player_service"].get_last_player_name()
    state = services["game_service"].create_session(player_name=last_player_name)
    services["session_store"].save_session(state)
    return jsonify({"session_id": state.session_id, "state": state.to_dict()})


@api_blueprint.get("/api/game/session/<session_id>")
def get_session(session_id: str):
    state, error = _session_or_404(session_id)
    if error:
        return error
    return jsonify({"session_id": state.session_id, "state": state.to_dict()})


@api_blueprint.post("/api/game/session/<session_id>/confirm-player")
def confirm_player(session_id: str):
    state, error = _session_or_404(session_id)
    if error:
        return error

    payload = _json_payload()
    player_name = payload.get("player", "")

    services = _services()

    try:
        services["game_service"].confirm_player(state, player_name)
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400

    services["player_service"].save_player_name(state.player_name)
    services["session_store"].save_session(state)
    return jsonify({"session_id": state.session_id, "state": state.to_dict()})


@api_blueprint.post("/api/game/session/<session_id>/pause-player")
def pause_player(session_id: str):
    state, error = _session_or_404(session_id)
    if error:
        return error

    _services()["game_service"].pause_for_player_edit(state)
    _services()["session_store"].save_session(state)
    return jsonify({"session_id": state.session_id, "state": state.to_dict()})


@api_blueprint.post("/api/game/session/<session_id>/direction")
def set_direction(session_id: str):
    state, error = _session_or_404(session_id)
    if error:
        return error

    payload = _json_payload()
    direction = payload.get("direction", "")

    try:
        _services()["game_service"].set_direction(state, direction)
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400

    _services()["session_store"].save_session(state)
    return jsonify({"session_id": state.session_id, "state": state.to_dict()})


@api_blueprint.post("/api/game/session/<session_id>/tick")
def tick_game(session_id: str):
    state, error = _session_or_404(session_id)
    if error:
        return error

    _services()["game_service"].tick_game(state)
    _services()["session_store"].save_session(state)
    return jsonify({"session_id": state.session_id, "state": state.to_dict()})


@api_blueprint.post("/api/game/session/<session_id>/restart")
def restart_game(session_id: str):
    state, error = _session_or_404(session_id)
    if error:
        return error

    restarted_state = _services()["game_service"].restart_game(state)
    _services()["session_store"].save_session(restarted_state)
    return jsonify({"session_id": restarted_state.session_id, "state": restarted_state.to_dict()})


@api_blueprint.get("/api/high-scores")
def get_high_scores():
    scores = _services()["score_service"].get_high_scores()
    return jsonify({"scores": scores})


@api_blueprint.post("/api/high-scores")
def save_high_score():
    payload = _json_payload()

    try:
        record = _services()["score_service"].save_score(
            payload.get("player", ""),
            payload.get("score", 0),
        )
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400

    return jsonify({"score": record}), 201


@api_blueprint.get("/api/player-settings")
def get_player_settings():
    return jsonify(_services()["player_service"].get_settings())


@api_blueprint.post("/api/player-settings")
def save_player_settings():
    payload = _json_payload()

    try:
        saved_name = _services()["player_service"].save_player_name(
            payload.get("last_player_name", ""),
        )
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400

    return jsonify({"last_player_name": saved_name})
