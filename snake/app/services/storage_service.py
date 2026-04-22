import json
from copy import deepcopy
from pathlib import Path


class JsonStorageService:
    def __init__(self, data_dir: Path) -> None:
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)

    def bootstrap_defaults(self) -> None:
        self.ensure_file("scores.json", {"scores": []})
        self.ensure_file("settings.json", {"last_player_name": ""})

    def ensure_file(self, filename: str, default_data: dict) -> Path:
        path = self.data_dir / filename
        if not path.exists():
            self.write_json(filename, default_data)
        return path

    def read_json(self, filename: str, default_data: dict) -> dict:
        path = self.ensure_file(filename, default_data)
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            fallback = deepcopy(default_data)
            self.write_json(filename, fallback)
            return fallback

    def write_json(self, filename: str, payload: dict) -> Path:
        path = self.data_dir / filename
        path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
        return path
