const { login } = require("../../services/auth");
const { normalizeErrorMessage } = require("../../utils/errors");

Page({
  data: {
    username: "",
    password: "",
    isLoading: false,
    errorMessage: ""
  },

  onShow() {
    const app = getApp();
    if (app.globalData.session && app.globalData.session.token) {
      wx.switchTab({ url: "/pages/submit/index" });
    }
  },

  onUsernameInput(event) {
    this.setData({ username: event.detail.value });
  },

  onPasswordInput(event) {
    this.setData({ password: event.detail.value });
  },

  async handleLogin() {
    if (this.data.isLoading || !this.data.username || !this.data.password) {
      return;
    }

    this.setData({ isLoading: true, errorMessage: "" });

    try {
      const response = await login(this.data.username.trim(), this.data.password);
      getApp().setSession(response);
      wx.switchTab({ url: "/pages/submit/index" });
    } catch (error) {
      this.setData({
        errorMessage: normalizeErrorMessage(error, "登录失败，请稍后重试。")
      });
    } finally {
      this.setData({ isLoading: false });
    }
  },

  goRegister() {
    wx.navigateTo({ url: "/pages/register/index" });
  }
});
