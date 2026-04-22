import {
  confirmPlayer,
  createSession,
  getHighScores,
  getPlayerSettings,
  pauseForPlayerEdit,
  restartSession,
  sendDirection,
  tickSession,
} from "./api.js";
import { renderGame } from "./renderer.js";

const TICK_INTERVAL_MS = 150;
const DIRECTION_KEYS = {
  ArrowUp: "up",
  ArrowDown: "down",
  ArrowLeft: "left",
  ArrowRight: "right",
  w: "up",
  W: "up",
  s: "down",
  S: "down",
  a: "left",
  A: "left",
  d: "right",
  D: "right",
};

const appState = {
  sessionId: null,
  sessionState: null,
  lastConfirmedName: "",
  tickHandle: null,
  tickInFlight: false,
  transientMessage: "",
};

const elements = {
  board: document.querySelector("#game-board"),
  confirmButton: document.querySelector("#confirm-player"),
  currentPlayer: document.querySelector("#current-player"),
  highScores: document.querySelector("#high-scores"),
  nameInput: document.querySelector("#player-name"),
  restartButton: document.querySelector("#restart-game"),
  score: document.querySelector("#score"),
  status: document.querySelector("#status"),
};

document.addEventListener("DOMContentLoaded", () => {
  void initializeUi();
});

function translateStatus(sessionState) {
  if (appState.transientMessage) {
    return appState.transientMessage;
  }

  const typedPlayerName = elements.nameInput.value.trim();

  if (!sessionState) {
    return "Creating a new session...";
  }

  if (sessionState.status === "waiting_for_player") {
    return "Enter a player name and confirm it to start.";
  }

  if (sessionState.status === "paused_for_player") {
    return typedPlayerName
      ? `Confirm ${typedPlayerName} to resume this run.`
      : "Game paused until the updated player name is confirmed.";
  }

  if (sessionState.status === "game_over") {
    return "Game over. Restart to try again.";
  }

  return "Steer with Arrow keys or WASD.";
}

function renderHighScores(scores) {
  const items = scores.length
    ? scores.map(
        (item) =>
          `<li><strong>${escapeHtml(item.player)}</strong> <span>${item.score}</span></li>`,
      )
    : ["<li>No scores yet.</li>"];

  elements.highScores.innerHTML = items.join("");
}

function escapeHtml(value) {
  return value
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;");
}

function applySessionState(sessionState) {
  appState.sessionState = sessionState;
  const typedPlayerName = elements.nameInput.value.trim();

  if (sessionState.player_confirmed) {
    appState.lastConfirmedName = sessionState.player_name;
  }

  elements.score.textContent = String(sessionState.score);
  elements.currentPlayer.textContent = sessionState.player_confirmed
    ? sessionState.player_name
    : typedPlayerName
      ? `${typedPlayerName} (confirm to play)`
      : "Waiting for confirmation";
  elements.status.textContent = translateStatus(sessionState);
  renderGame(elements.board, sessionState);

  if (shouldTick()) {
    startTicking();
  } else {
    stopTicking();
  }
}

function shouldTick() {
  return Boolean(
    appState.sessionId &&
      appState.sessionState &&
      appState.sessionState.status === "running" &&
      appState.sessionState.player_confirmed &&
      !appState.sessionState.game_over,
  );
}

function startTicking() {
  if (appState.tickHandle !== null) {
    return;
  }

  appState.tickHandle = window.setInterval(() => {
    void tickOnce();
  }, TICK_INTERVAL_MS);
}

function stopTicking() {
  if (appState.tickHandle === null) {
    return;
  }

  window.clearInterval(appState.tickHandle);
  appState.tickHandle = null;
}

async function tickOnce() {
  if (!shouldTick() || appState.tickInFlight) {
    return;
  }

  appState.tickInFlight = true;

  try {
    const response = await tickSession(appState.sessionId);
    const wasGameOver = appState.sessionState?.game_over;

    appState.transientMessage = "";
    applySessionState(response.state);

    if (!wasGameOver && response.state.game_over) {
      await refreshHighScores();
    }
  } catch (error) {
    appState.transientMessage = error.message;
    elements.status.textContent = appState.transientMessage;
    stopTicking();
  } finally {
    appState.tickInFlight = false;
  }
}

async function refreshHighScores() {
  try {
    const payload = await getHighScores();
    renderHighScores(payload.scores);
  } catch (error) {
    appState.transientMessage = error.message;
    elements.status.textContent = translateStatus(appState.sessionState);
  }
}

async function handleConfirmPlayer() {
  if (!appState.sessionId) {
    return;
  }

  const playerName = elements.nameInput.value.trim();
  if (!playerName) {
    appState.transientMessage = "Player name is required before the game can start.";
    elements.status.textContent = appState.transientMessage;
    return;
  }

  try {
    const response = await confirmPlayer(appState.sessionId, playerName);
    appState.transientMessage = "";
    applySessionState(response.state);
  } catch (error) {
    appState.transientMessage = error.message;
    elements.status.textContent = appState.transientMessage;
  }
}

async function handleRestart() {
  if (!appState.sessionId) {
    return;
  }

  try {
    const response = await restartSession(appState.sessionId);
    appState.transientMessage = "";
    applySessionState(response.state);
  } catch (error) {
    appState.transientMessage = error.message;
    elements.status.textContent = appState.transientMessage;
  }
}

async function handleNameInput() {
  const currentValue = elements.nameInput.value.trim();
  const sessionState = appState.sessionState;

  if (!sessionState || sessionState.game_over) {
    elements.status.textContent = translateStatus(sessionState);
    return;
  }

  if (sessionState.player_confirmed && currentValue !== appState.lastConfirmedName) {
    try {
      const response = await pauseForPlayerEdit(appState.sessionId);
      appState.transientMessage = "";
      applySessionState(response.state);
      return;
    } catch (error) {
      appState.transientMessage = error.message;
      elements.status.textContent = appState.transientMessage;
      return;
    }
  }

  appState.transientMessage = "";
  elements.status.textContent = translateStatus(sessionState);
}

async function handleDirectionKey(event) {
  const direction = DIRECTION_KEYS[event.key];
  if (!direction || !appState.sessionId || !appState.sessionState) {
    return;
  }

  event.preventDefault();

  try {
    const response = await sendDirection(appState.sessionId, direction);
    appState.transientMessage = "";
    applySessionState(response.state);
  } catch (error) {
    appState.transientMessage = error.message;
    elements.status.textContent = appState.transientMessage;
  }
}

function registerEvents() {
  elements.confirmButton.addEventListener("click", () => {
    void handleConfirmPlayer();
  });

  elements.restartButton.addEventListener("click", () => {
    void handleRestart();
  });

  elements.nameInput.addEventListener("input", () => {
    void handleNameInput();
  });

  elements.nameInput.addEventListener("keydown", (event) => {
    if (event.key !== "Enter") {
      return;
    }

    event.preventDefault();
    void handleConfirmPlayer();
  });

  window.addEventListener("keydown", (event) => {
    void handleDirectionKey(event);
  });
}

async function initializeUi() {
  registerEvents();
  elements.status.textContent = "Loading player settings and session...";

  try {
    const [settingsPayload, scoresPayload, sessionPayload] = await Promise.all([
      getPlayerSettings(),
      getHighScores(),
      createSession(),
    ]);

    elements.nameInput.value =
      sessionPayload.state.player_name || settingsPayload.last_player_name || "";
    renderHighScores(scoresPayload.scores);

    appState.sessionId = sessionPayload.session_id;
    applySessionState(sessionPayload.state);
  } catch (error) {
    appState.transientMessage = error.message;
    elements.status.textContent = appState.transientMessage;
  }
}
