const SESSION_KEY = "video_copy_session";

function loadSession() {
  try {
    return wx.getStorageSync(SESSION_KEY) || null;
  } catch (error) {
    return null;
  }
}

function saveSession(session) {
  wx.setStorageSync(SESSION_KEY, session);
}

function clearSession() {
  wx.removeStorageSync(SESSION_KEY);
}

function getToken() {
  const session = loadSession();
  return session && session.token ? session.token : "";
}

module.exports = {
  loadSession,
  saveSession,
  clearSession,
  getToken
};
