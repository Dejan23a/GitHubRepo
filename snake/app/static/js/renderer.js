const CELL_SIZE = 24;
const GRID_LINE_COLOR = "rgba(255, 255, 255, 0.06)";
const WALL_COLOR = "#8a6d4d";
const FOOD_COLOR = "#ff5f5f";
const BOARD_BG = "#10212b";

function statusOverlayText(status) {
  if (status === "waiting_for_player") {
    return "Confirm a player";
  }
  if (status === "paused_for_player") {
    return "Paused";
  }
  if (status === "game_over") {
    return "Game Over";
  }
  return "";
}

function resizeCanvas(canvas, state) {
  const expectedWidth = state.board_width * CELL_SIZE;
  const expectedHeight = state.board_height * CELL_SIZE;

  if (canvas.width !== expectedWidth) {
    canvas.width = expectedWidth;
  }

  if (canvas.height !== expectedHeight) {
    canvas.height = expectedHeight;
  }
}

function drawGrid(context, state) {
  context.fillStyle = BOARD_BG;
  context.fillRect(0, 0, context.canvas.width, context.canvas.height);

  context.strokeStyle = GRID_LINE_COLOR;
  context.lineWidth = 1;

  for (let x = 0; x <= state.board_width; x += 1) {
    context.beginPath();
    context.moveTo(x * CELL_SIZE, 0);
    context.lineTo(x * CELL_SIZE, context.canvas.height);
    context.stroke();
  }

  for (let y = 0; y <= state.board_height; y += 1) {
    context.beginPath();
    context.moveTo(0, y * CELL_SIZE);
    context.lineTo(context.canvas.width, y * CELL_SIZE);
    context.stroke();
  }
}

function drawCell(context, position, color, inset = 2) {
  context.fillStyle = color;
  context.fillRect(
    position.x * CELL_SIZE + inset,
    position.y * CELL_SIZE + inset,
    CELL_SIZE - inset * 2,
    CELL_SIZE - inset * 2,
  );
}

function drawFood(context, food) {
  if (!food) {
    return;
  }

  const centerX = food.x * CELL_SIZE + CELL_SIZE / 2;
  const centerY = food.y * CELL_SIZE + CELL_SIZE / 2;
  const radius = CELL_SIZE * 0.32;

  context.fillStyle = FOOD_COLOR;
  context.beginPath();
  context.arc(centerX, centerY, radius, 0, Math.PI * 2);
  context.fill();
}

function drawOverlay(context, message) {
  if (!message) {
    return;
  }

  context.fillStyle = "rgba(7, 12, 16, 0.55)";
  context.fillRect(0, 0, context.canvas.width, context.canvas.height);

  context.fillStyle = "#fff4df";
  context.font = '700 30px "Trebuchet MS", sans-serif';
  context.textAlign = "center";
  context.fillText(message, context.canvas.width / 2, context.canvas.height / 2);
}

export function renderGame(canvas, state) {
  const context = canvas.getContext("2d");
  resizeCanvas(canvas, state);
  drawGrid(context, state);

  state.walls.forEach((wall) => drawCell(context, wall, WALL_COLOR, 3));
  drawFood(context, state.food);

  state.snake.forEach((segment, index) => {
    const segmentColor = index === 0 ? state.snake_head_color : state.snake_color;
    drawCell(context, segment, segmentColor, 2);
  });

  drawOverlay(context, statusOverlayText(state.status));
}
