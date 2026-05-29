const { requireSession } = require("../../utils/auth");
const { normalizeErrorMessage } = require("../../utils/errors");
const { fetchOverview } = require("../../services/videos");

Page({
  data: {
    user: null,
    shortcutInstallUrl: "https://www.icloud.com/shortcuts/c8d471ecbc54424388ec070917e00885",
    overview: {
      total: 0,
      today: 0,
      pending: 0
    },
    isLoadingOverview: false,
    errorMessage: ""
  },

  onShow() {
    const session = requireSession();
    if (!session) {
      return;
    }
    this.setData({ user: session.user });
    this.loadOverview(session.token);
  },

  async loadOverview(token) {
    this.setData({ isLoadingOverview: true, errorMessage: "" });
    try {
      const overview = await fetchOverview(token);
      this.setData({ overview });
    } catch (error) {
      this.setData({
        errorMessage: normalizeErrorMessage(error, "个人概览加载失败，请稍后重试。")
      });
    } finally {
      this.setData({ isLoadingOverview: false });
    }
  },

  openShortcutTutorial() {
    wx.navigateTo({ url: "/pages/shortcut-tutorial/index" });
  },

  copyShortcutInstallUrl() {
    wx.setClipboardData({
      data: this.data.shortcutInstallUrl
    });
  },

  openShortcutKeys() {
    wx.navigateTo({ url: "/pages/shortcut-keys/index" });
  },

  showPlaceholder(event) {
    const title = event.currentTarget.dataset.title;
    wx.showToast({
      title: `${title}尚未开放`,
      icon: "none"
    });
  },

  logout() {
    getApp().clearSession();
    wx.reLaunch({ url: "/pages/login/index" });
  }
});
