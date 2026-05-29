const { loadSession, clearSession, saveSession } = require("./store/session");

App({
  globalData: {
    session: loadSession()
  },

  onLaunch() {
    this.globalData.session = loadSession();
  },

  setSession(session) {
    this.globalData.session = session;
    saveSession(session);
  },

  clearSession() {
    this.globalData.session = null;
    clearSession();
  }
});
