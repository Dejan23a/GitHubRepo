class PlayerService:
    SETTINGS_FILE = "settings.json"
    MAX_NAME_LENGTH = 20

    def __init__(self, storage_service) -> None:
        self.storage_service = storage_service

    def normalize_name(self, player_name: str) -> str:
        normalized = (player_name or "").strip()
        if not normalized:
            raise ValueError("Player name is required.")
        if len(normalized) > self.MAX_NAME_LENGTH:
            raise ValueError(f"Player name must be at most {self.MAX_NAME_LENGTH} characters.")
        return normalized

    def get_settings(self) -> dict[str, str]:
        payload = self.storage_service.read_json(
            self.SETTINGS_FILE,
            {"last_player_name": ""},
        )
        stored_name = payload.get("last_player_name", "")
        if not isinstance(stored_name, str):
            stored_name = ""
        stored_name = stored_name.strip()
        if len(stored_name) > self.MAX_NAME_LENGTH:
            stored_name = stored_name[: self.MAX_NAME_LENGTH]
        return {"last_player_name": stored_name}

    def get_last_player_name(self) -> str:
        return self.get_settings()["last_player_name"]

    def save_player_name(self, player_name: str) -> str:
        normalized = self.normalize_name(player_name)
        self.storage_service.write_json(
            self.SETTINGS_FILE,
            {"last_player_name": normalized},
        )
        return normalized
