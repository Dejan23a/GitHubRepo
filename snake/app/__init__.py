from pathlib import Path

from flask import Flask

from .routes import api_blueprint
from .models.session_store import SessionStore
from .services.game_service import GameService
from .services.player_service import PlayerService
from .services.score_service import ScoreService
from .services.storage_service import JsonStorageService


def create_app() -> Flask:
    app = Flask(__name__, template_folder="templates", static_folder="static")

    data_dir = Path(__file__).resolve().parent / "data"
    storage_service = JsonStorageService(data_dir)
    storage_service.bootstrap_defaults()

    score_service = ScoreService(storage_service)
    player_service = PlayerService(storage_service)
    session_store = SessionStore()
    game_service = GameService(score_service=score_service)

    app.extensions["snake_services"] = {
        "storage_service": storage_service,
        "score_service": score_service,
        "player_service": player_service,
        "session_store": session_store,
        "game_service": game_service,
    }

    app.register_blueprint(api_blueprint)
    return app
