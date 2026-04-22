from datetime import datetime, timezone


class ScoreService:
    SCORES_FILE = "scores.json"
    MAX_RECORDS = 10

    def __init__(self, storage_service) -> None:
        self.storage_service = storage_service

    def get_high_scores(self) -> list[dict]:
        payload = self.storage_service.read_json(self.SCORES_FILE, {"scores": []})
        scores = self._normalize_scores(payload.get("scores", []))
        if scores != payload.get("scores", []):
            self.storage_service.write_json(self.SCORES_FILE, {"scores": scores})
        return scores

    def save_score(self, player_name: str, score: int) -> dict:
        normalized_name = (player_name or "").strip()
        if not normalized_name:
            raise ValueError("Player name is required to save a score.")
        if not isinstance(score, int) or score < 0:
            raise ValueError("Score must be a non-negative integer.")

        payload = self.storage_service.read_json(self.SCORES_FILE, {"scores": []})
        record = {
            "player": normalized_name,
            "score": score,
            "played_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        }
        payload["scores"].append(record)
        payload["scores"] = self._normalize_scores(payload["scores"])
        self.storage_service.write_json(self.SCORES_FILE, payload)
        return record

    def _normalize_scores(self, raw_scores) -> list[dict]:
        if not isinstance(raw_scores, list):
            return []

        normalized_scores: list[dict] = []
        for entry in raw_scores:
            if not isinstance(entry, dict):
                continue

            player_name = entry.get("player", "")
            score = entry.get("score")
            played_at = entry.get("played_at", "")

            if not isinstance(player_name, str):
                continue
            player_name = player_name.strip()
            if not player_name:
                continue
            if not isinstance(score, int) or score < 0:
                continue
            if not isinstance(played_at, str):
                played_at = ""

            normalized_scores.append(
                {
                    "player": player_name,
                    "score": score,
                    "played_at": played_at,
                }
            )

        return sorted(
            normalized_scores,
            key=lambda item: (-item["score"], item["played_at"]),
        )[: self.MAX_RECORDS]
