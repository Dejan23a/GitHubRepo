from __future__ import annotations

import random
import uuid

from app.models.game_state import COLOR_PALETTE, GameState, Position


DIRECTION_VECTORS = {
    "up": (0, -1),
    "down": (0, 1),
    "left": (-1, 0),
    "right": (1, 0),
}

OPPOSITE_DIRECTIONS = {
    "up": "down",
    "down": "up",
    "left": "right",
    "right": "left",
}


class GameService:
    def __init__(
        self,
        score_service=None,
        board_width: int = 20,
        board_height: int = 20,
        rng: random.Random | None = None,
    ) -> None:
        self.score_service = score_service
        self.board_width = board_width
        self.board_height = board_height
        self.rng = rng or random.Random()

    def create_session(
        self,
        player_name: str = "",
        player_confirmed: bool = False,
    ) -> GameState:
        session_id = uuid.uuid4().hex
        return self.build_initial_state(
            session_id=session_id,
            player_name=player_name,
            player_confirmed=player_confirmed,
        )

    def build_initial_state(
        self,
        session_id: str,
        player_name: str = "",
        player_confirmed: bool = False,
    ) -> GameState:
        start_x = self.board_width // 2
        start_y = self.board_height // 2
        snake = [
            Position(start_x, start_y),
            Position(start_x - 1, start_y),
            Position(start_x - 2, start_y),
        ]

        if player_confirmed:
            status = "running"
        elif player_name:
            status = "paused_for_player"
        else:
            status = "waiting_for_player"

        state = GameState(
            session_id=session_id,
            board_width=self.board_width,
            board_height=self.board_height,
            player_name=player_name,
            player_confirmed=player_confirmed,
            status=status,
            snake=snake,
            direction="right",
            next_direction="right",
            color_index=0,
        )
        state.food = self._choose_free_position(state)
        return state

    def restart_game(self, state: GameState) -> GameState:
        restarted_state = self.build_initial_state(
            session_id=state.session_id,
            player_name=state.player_name,
            player_confirmed=state.player_confirmed,
        )
        return restarted_state

    def confirm_player(self, state: GameState, player_name: str) -> GameState:
        normalized_name = (player_name or "").strip()
        if not normalized_name:
            raise ValueError("Player name is required.")
        if len(normalized_name) > 20:
            raise ValueError("Player name must be at most 20 characters.")

        state.player_name = normalized_name
        state.player_confirmed = True
        state.status = "running" if not state.game_over else "game_over"
        return state

    def pause_for_player_edit(self, state: GameState) -> GameState:
        if state.game_over:
            return state
        state.player_confirmed = False
        state.status = "paused_for_player" if state.player_name else "waiting_for_player"
        return state

    def set_direction(self, state: GameState, direction: str) -> GameState:
        if direction not in DIRECTION_VECTORS:
            raise ValueError("Direction must be one of up, down, left, or right.")

        if len(state.snake) > 1 and direction == OPPOSITE_DIRECTIONS[state.direction]:
            return state

        state.next_direction = direction
        return state

    def tick_game(self, state: GameState) -> GameState:
        if state.game_over:
            self._save_score_once(state)
            return state

        if not state.player_confirmed:
            state.status = "paused_for_player" if state.player_name else "waiting_for_player"
            return state

        state.direction = self._resolve_direction(state)
        next_head = self._next_head(state)
        eating_food = state.food is not None and next_head == state.food

        if self._is_collision(state, next_head, eating_food):
            return self._mark_game_over(state)

        new_snake = [next_head, *state.snake]
        if not eating_food:
            new_snake.pop()
        else:
            state.score += 1
            state.color_index = (state.color_index + 1) % len(COLOR_PALETTE)

        state.snake = new_snake
        state.tick_count += 1
        state.status = "running"

        if eating_food:
            self._spawn_wall(state)
            state.food = self._choose_free_position(state)
            if state.food is None:
                return self._mark_game_over(state)

        return state

    def _resolve_direction(self, state: GameState) -> str:
        requested_direction = state.next_direction
        if len(state.snake) > 1 and requested_direction == OPPOSITE_DIRECTIONS[state.direction]:
            return state.direction
        return requested_direction

    def _next_head(self, state: GameState) -> Position:
        delta_x, delta_y = DIRECTION_VECTORS[state.direction]
        current_head = state.snake[0]
        return Position(current_head.x + delta_x, current_head.y + delta_y)

    def _is_collision(self, state: GameState, next_head: Position, eating_food: bool) -> bool:
        if next_head.x < 0 or next_head.x >= state.board_width:
            return True
        if next_head.y < 0 or next_head.y >= state.board_height:
            return True

        if next_head in state.walls:
            return True

        body_to_check = state.snake if eating_food else state.snake[:-1]
        return next_head in body_to_check

    def _spawn_wall(self, state: GameState) -> None:
        new_wall = self._choose_free_position(state)
        if new_wall is not None:
            state.walls.append(new_wall)

    def _choose_free_position(self, state: GameState) -> Position | None:
        occupied = {self._as_tuple(segment) for segment in state.snake}
        occupied.update(self._as_tuple(wall) for wall in state.walls)
        if state.food is not None:
            occupied.add(self._as_tuple(state.food))

        free_cells = [
            Position(x, y)
            for y in range(state.board_height)
            for x in range(state.board_width)
            if (x, y) not in occupied
        ]
        if not free_cells:
            return None
        return self.rng.choice(free_cells)

    def _mark_game_over(self, state: GameState) -> GameState:
        state.game_over = True
        state.status = "game_over"
        self._save_score_once(state)
        return state

    def _save_score_once(self, state: GameState) -> None:
        if state.score_saved or not state.player_name or self.score_service is None:
            return
        self.score_service.save_score(state.player_name, state.score)
        state.score_saved = True

    @staticmethod
    def _as_tuple(position: Position) -> tuple[int, int]:
        return position.x, position.y
