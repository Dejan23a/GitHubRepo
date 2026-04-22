# Snake Control Room

A server-backed Snake game built with Flask plus plain HTML, CSS, and JavaScript. The browser handles rendering and input, while Python owns the game rules and state transitions.

## Run It

1. Open a terminal in `snake`.
2. Install dependencies with `python -m pip install -r requirements.txt`.
3. Start the app with `python -m app.server`.
4. Open `http://127.0.0.1:5000`.

## Manual Checks

1. The page loads with a canvas, player input, status, and high scores panel.
2. The last confirmed player name is prefilled after refresh, and the game stays paused until you confirm it with Enter or `OK`.
3. Arrow keys and WASD change direction after confirmation.
4. Eating food increases the score, changes the snake color, and adds exactly one wall.
5. Hitting the boundary, the snake body, or a wall ends the game.
6. Restart resets the snake, score, walls, direction, food, and color cycle.
7. After a game over, the score appears in the high score list only once and both the leaderboard and confirmed player name survive refresh.
