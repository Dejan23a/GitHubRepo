# Snake Game Initial Implementation Design

## Goal

Design an initial implementation of a Snake game with:

- Python backend
- HTML web user interface
- Python-based game logic
- Planning only in this document, with no runnable code changes

This version treats Python as the source of truth for gameplay rules and state transitions, while the browser is responsible for rendering and player input.

## Recommended Approach

Use a lightweight Python web server to:

- serve the HTML interface
- manage game sessions
- execute game logic on the server
- persist player settings and high scores

Recommended stack:

- Backend: Python with `Flask`
- Frontend: plain HTML, CSS, and JavaScript
- Persistence: JSON files for local development

Rationale:

- Flask keeps the server simple for an initial version
- Plain HTML and JavaScript keep the UI lightweight
- Python-owned game logic makes rule handling deterministic and centralized
- JSON storage is enough for a first implementation and can later be replaced by SQLite

## High-Level Architecture

The application is split into two parts.

### 1. Python Backend

Responsibilities:

- Serve the main HTML page and static assets
- Maintain authoritative game state
- Execute snake movement and collision rules
- Spawn food and walls
- Manage score saving and player settings
- Expose API endpoints for game actions and state retrieval

### 2. HTML Web UI

Responsibilities:

- Render the board and control panel
- Capture keyboard input
- Send input commands to the backend
- Poll or fetch the latest game state from the backend
- Display score, status, instructions, and high scores

## Recommended Interaction Model

For the initial version, use a request-response model rather than WebSockets.

Suggested flow:

- Frontend creates or resumes a game session
- Frontend sends direction changes to the backend
- Frontend calls a tick endpoint on a fixed interval
- Backend advances the game by one step and returns updated state
- Frontend renders the returned state

Why this is a good first version:

- Easier to implement than bidirectional sockets
- Keeps all gameplay logic in Python
- Works well for a single-player browser game

## Functional Scope

### Gameplay

- Grid-based Snake movement
- Arrow key controls, optionally WASD
- Snake grows after eating food
- Boundary collision causes game over
- Self-collision causes game over
- One new wall appears after each food pickup
- Wall collision causes game over
- Snake color changes after each food pickup
- Restart resets the full game state

### Player and Persistence

- Player enters a name before starting
- Name must be confirmed through Enter or OK button
- If the name changes, gameplay pauses until reconfirmed
- Score is saved once on game over
- High scores persist between sessions
- Last confirmed player name is loaded automatically

## Proposed Project Structure

```text
snake/
  snake_prompt.md
  snake_prompt.txt
  game_snake_implement.md
  app/
    __init__.py
    server.py
    routes.py
    services/
      game_service.py
      score_service.py
      player_service.py
      storage_service.py
    models/
      game_state.py
      session_store.py
    data/
      scores.json
      settings.json
    templates/
      index.html
    static/
      css/
        style.css
      js/
        api.js
        ui.js
        renderer.js
      assets/
        favicon.ico
  tests/
    test_game_service.py
    test_scores.py
    test_routes.py
  requirements.txt
  README.md
```

## Responsibility by Module

### Backend Files

#### `app/server.py`

- Application entry point
- Creates Flask app
- Registers routes
- Starts development server

#### `app/routes.py`

- Defines page and API routes
- Handles game session requests
- Handles player setting and high score requests

#### `app/services/game_service.py`

- Core game rules and state transitions
- Movement handling
- Collision detection
- Food and wall spawning
- Restart and session reset logic

#### `app/services/score_service.py`

- Saves high scores
- Validates score payloads
- Sorts and limits saved records if needed

#### `app/services/player_service.py`

- Loads and stores last confirmed player name
- Validates basic player input

#### `app/services/storage_service.py`

- Shared JSON read/write utilities
- Creates default data when files do not exist

#### `app/models/game_state.py`

- Defines the game state structure
- Holds snake, direction, food, walls, score, status, color cycle, and flags

#### `app/models/session_store.py`

- Maps session IDs to active in-memory game states
- Supports restart, lookup, and cleanup

### Frontend Files

#### `templates/index.html`

- Main page layout
- Includes title, instructions, controls, canvas, score panel, and high scores panel

#### `static/css/style.css`

- Minimal styling
- Clear, readable layout
- Responsive spacing for standard browser sizes

#### `static/js/api.js`

- API wrappers for session creation, tick requests, direction updates, restart, score loading, and player settings

#### `static/js/ui.js`

- Binds inputs and buttons
- Updates labels and status text
- Controls the browser timer that triggers backend ticks

#### `static/js/renderer.js`

- Draws the returned backend game state on the canvas
- Renders snake, food, walls, and status overlays

## Initial Page Structure

The HTML page should include:

- Game title
- Short instructions
- Player name input
- OK button
- Score display
- Status display
- Canvas for the board
- Restart button
- High Scores list

Suggested layout:

```text
+------------------------------------------------------+
| Snake Game                                           |
| Short instructions                                   |
+-----------------------------+------------------------+
| Player name input + OK      | Score                  |
| Status message              | Current player         |
| Canvas game board           | High scores            |
| Restart button              |                        |
+-----------------------------+------------------------+
```

## Backend API Design

### `GET /`

Purpose:

- Serve the main page

### `POST /api/game/session`

Purpose:

- Create a new game session

Example response:

```json
{
  "session_id": "abc123",
  "state": {
    "status": "waiting_for_player",
    "score": 0
  }
}
```

### `GET /api/game/session/<session_id>`

Purpose:

- Fetch the current game state

### `POST /api/game/session/<session_id>/confirm-player`

Purpose:

- Confirm player name and allow the session to run

Example request:

```json
{
  "player": "Ana"
}
```

### `POST /api/game/session/<session_id>/direction`

Purpose:

- Send the latest requested direction

Example request:

```json
{
  "direction": "up"
}
```

### `POST /api/game/session/<session_id>/tick`

Purpose:

- Advance the game by one server-side step
- Return updated state

### `POST /api/game/session/<session_id>/restart`

Purpose:

- Reset the session to a fresh game state

### `GET /api/high-scores`

Purpose:

- Return saved high scores

### `POST /api/high-scores`

Purpose:

- Save a completed score

### `GET /api/player-settings`

Purpose:

- Load the last confirmed player name

### `POST /api/player-settings`

Purpose:

- Save the last confirmed player name

## Game State Model

Suggested server-side state:

```text
GameState = {
  session_id: "...",
  player_name: "",
  player_confirmed: false,
  score: 0,
  status: "waiting_for_player",
  direction: "right",
  next_direction: "right",
  snake: [...],
  food: {...},
  walls: [...],
  game_over: false,
  score_saved: false,
  color_index: 0,
  tick_count: 0
}
```

## Important State Rules

- The backend is the only place where state changes occur
- The frontend never computes collisions or food placement
- `player_confirmed` must be `true` before a tick can advance gameplay
- `score_saved` prevents duplicate high score submissions
- `next_direction` prevents illegal instant reverse turns

## Core Python Game Logic

The backend should own these behaviors:

- initialize default board state
- accept pending direction updates
- move snake on each tick
- detect boundary collisions
- detect self-collisions
- detect wall collisions
- detect food consumption
- grow snake after eating
- rotate snake color
- spawn food only on free cells
- spawn wall only on free cells
- mark game over
- save score once on terminal state

## Game Flow

### 1. Page Load

- Backend serves HTML
- Frontend loads last player name and high scores
- Frontend requests a new game session
- Session starts paused

### 2. Player Confirmation

- User enters name
- User presses Enter or clicks OK
- Frontend sends confirm-player request
- Backend validates and stores player name
- Backend updates session to active state

### 3. Direction Input

- User presses arrow or WASD key
- Frontend sends direction to backend
- Backend stores the next valid direction

### 4. Tick Cycle

- Browser timer calls tick endpoint
- Backend advances game state one step
- Backend returns full or partial state payload
- Frontend renders new board state

### 5. Game Over

- Backend marks session as game over
- Backend saves score once
- Frontend stops sending active ticks
- Frontend refreshes high score display

### 6. Restart

- Frontend requests restart
- Backend creates a fresh board for the same session
- Confirmed player name may be retained, but gameplay remains paused if desired by product decision

## Suggested Python Classes or Structures

Possible design:

- `GameState`
- `Position`
- `GameService`
- `SessionStore`
- `ScoreService`

This can be implemented with dataclasses for readability.

## Core Backend Functions

Suggested functions:

- `create_app()`
- `create_session()`
- `get_session(session_id)`
- `confirm_player(session_id, player_name)`
- `set_direction(session_id, direction)`
- `tick_game(session_id)`
- `restart_game(session_id)`
- `build_initial_state()`
- `move_snake(state)`
- `detect_collision(state)`
- `handle_food_consumption(state)`
- `spawn_food(state)`
- `spawn_wall(state)`
- `update_color_cycle(state)`
- `save_score_once(state)`
- `get_high_scores()`
- `save_high_score(player, score)`
- `get_player_settings()`
- `save_player_settings(last_player_name)`

## Frontend Responsibilities in Detail

The frontend should stay thin.

It should:

- draw the state returned by the backend
- capture user intent
- manage timer calls to `/tick`
- render score, status, and high scores
- disable active play when session status is paused or game over

It should not:

- calculate game movement
- resolve collisions
- place food or walls
- decide when a score should be saved

## Data Storage Design

### `scores.json`

Suggested structure:

```json
{
  "scores": [
    {
      "player": "Ana",
      "score": 12,
      "played_at": "2026-04-22T18:00:00Z"
    }
  ]
}
```

### `settings.json`

Suggested structure:

```json
{
  "last_player_name": "Ana"
}
```

## Session Storage Design

For the initial implementation, store active game sessions in memory.

Benefits:

- simple to implement
- fast enough for local or small-scale use
- avoids database complexity in version one

Limitations:

- server restart clears active sessions
- not suitable for scaled multi-instance deployment

This is acceptable for the first version.

## Validation Rules

### Player Name

- Trim spaces
- Reject empty values
- Limit to a reasonable maximum such as 20 characters

### Direction

- Accept only `up`, `down`, `left`, `right`
- Ignore invalid reverse moves when the snake length is greater than one

### Score

- Accept only non-negative integers

## Non-Functional Guidelines

- Keep game logic deterministic and testable
- Keep route handlers thin
- Keep browser code focused on UI rendering
- Return simple JSON payloads
- Design services so JSON storage can later be swapped for SQLite

## Suggested Milestones

### Milestone 1: Backend Skeleton

- Create Flask app
- Serve HTML template
- Add empty session and settings routes
- Add JSON storage utilities

### Milestone 2: Session-Based Python Game Model

- Define game state structure
- Implement in-memory session store
- Implement board initialization and restart

### Milestone 3: Core Python Gameplay

- Implement tick processing
- Add movement and collisions
- Add food growth behavior

### Milestone 4: Advanced Rules

- Add wall spawning
- Add wall collision
- Add snake color cycle support in returned state

### Milestone 5: Frontend Integration

- Render state from backend
- Send direction input
- Drive the game using periodic tick calls
- Confirm player names and handle pause states

### Milestone 6: Persistence

- Save last player name
- Save score once on game over
- Load and refresh leaderboard

### Milestone 7: Testing

- Unit test Python game rules
- Test route validation
- Test duplicate save prevention
- Test restart correctness

## Testing Strategy

### Backend Tests

- Initial state creation
- Valid and invalid direction updates
- Tick movement correctness
- Boundary, self, and wall collision behavior
- Food and wall spawning on free cells only
- Score save-once behavior
- Session restart behavior
- Route payload validation

### Manual UI Tests

- Page loads from Python server
- New session is created successfully
- Game stays paused until name confirmation
- Name change pauses the game again
- Direction changes are reflected correctly
- Snake grows after food pickup
- Snake color changes after food pickup
- New wall appears after each food pickup
- Game over is triggered correctly
- High scores persist after refresh

## Future Enhancements

- Replace polling with WebSockets
- Move session state to Redis or database
- Replace JSON storage with SQLite
- Add difficulty levels
- Add mobile controls
- Add sound and visual polish

## Final Recommendation

For this implementation, keep the gameplay engine entirely in Python and use the browser only as a rendering and input layer. That gives a clear separation of responsibility and makes the game rules easier to test, debug, and evolve.
