const { loadSession } = require("../store/session");

function getSession() {
  const app = getApp();
  return app && app.globalData ? app.globalData.session || loadSession() : loadSession();
}

function requireSession() {
  const session = getSession();
  if (!session || !session.token || !session.user) {
    wx.reLaunch({ url: "/pages/login/index" });
    return null;
  }
  return session;
}

module.exports = {
  getSession,
  requireSession
};
