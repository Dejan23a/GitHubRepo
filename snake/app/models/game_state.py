from dataclasses import dataclass, field


COLOR_PALETTE = [
    {"body": "#59c36a", "head": "#2f8f46"},
    {"body": "#ffb347", "head": "#df7a21"},
    {"body": "#6ac6ff", "head": "#2b7fb7"},
    {"body": "#ff7a7a", "head": "#c93f50"},
    {"body": "#c79dff", "head": "#8058d1"},
]


@dataclass(frozen=True, slots=True)
class Position:
    x: int
    y: int

    def to_dict(self) -> dict[str, int]:
        return {"x": self.x, "y": self.y}


@dataclass(slots=True)
class GameState:
    session_id: str
    board_width: int
    board_height: int
    player_name: str = ""
    player_confirmed: bool = False
    score: int = 0
    status: str = "waiting_for_player"
    direction: str = "right"
    next_direction: str = "right"
    snake: list[Position] = field(default_factory=list)
    food: Position | None = None
    walls: list[Position] = field(default_factory=list)
    game_over: bool = False
    score_saved: bool = False
    color_index: int = 0
    tick_count: int = 0

    def color_pair(self) -> dict[str, str]:
        return COLOR_PALETTE[self.color_index % len(COLOR_PALETTE)]

    def to_dict(self) -> dict:
        colors = self.color_pair()
        return {
            "session_id": self.session_id,
            "board_width": self.board_width,
            "board_height": self.board_height,
            "player_name": self.player_name,
            "player_confirmed": self.player_confirmed,
            "score": self.score,
            "status": self.status,
            "direction": self.direction,
            "next_direction": self.next_direction,
            "snake": [segment.to_dict() for segment in self.snake],
            "food": self.food.to_dict() if self.food else None,
            "walls": [wall.to_dict() for wall in self.walls],
            "game_over": self.game_over,
            "score_saved": self.score_saved,
            "color_index": self.color_index,
            "tick_count": self.tick_count,
            "snake_color": colors["body"],
            "snake_head_color": colors["head"],
        }
