const JSON_HEADERS = {
  "Content-Type": "application/json",
};

async function request(url, options = {}) {
  const response = await fetch(url, options);
  const payload = await response.json().catch(() => ({}));

  if (!response.ok) {
    throw new Error(payload.error || `Request failed with status ${response.status}.`);
  }

  return payload;
}

export function createSession() {
  return request("/api/game/session", { method: "POST" });
}

export function getSession(sessionId) {
  return request(`/api/game/session/${sessionId}`);
}

export function confirmPlayer(sessionId, playerName) {
  return request(`/api/game/session/${sessionId}/confirm-player`, {
    method: "POST",
    headers: JSON_HEADERS,
    body: JSON.stringify({ player: playerName }),
  });
}

export function pauseForPlayerEdit(sessionId) {
  return request(`/api/game/session/${sessionId}/pause-player`, {
    method: "POST",
  });
}

export function sendDirection(sessionId, direction) {
  return request(`/api/game/session/${sessionId}/direction`, {
    method: "POST",
    headers: JSON_HEADERS,
    body: JSON.stringify({ direction }),
  });
}

export function tickSession(sessionId) {
  return request(`/api/game/session/${sessionId}/tick`, {
    method: "POST",
  });
}

export function restartSession(sessionId) {
  return request(`/api/game/session/${sessionId}/restart`, {
    method: "POST",
  });
}

export function getHighScores() {
  return request("/api/high-scores");
}

export function getPlayerSettings() {
  return request("/api/player-settings");
}
