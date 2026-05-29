const { register } = require("../../services/auth");
const { normalizeErrorMessage } = require("../../utils/errors");

Page({
  data: {
    username: "",
    email: "",
    displayName: "",
    password: "",
    isLoading: false,
    errorMessage: ""
  },

  onFieldInput(event) {
    const { field } = event.currentTarget.dataset;
    this.setData({
      [field]: event.detail.value
    });
  },

  async handleRegister() {
    const { username, email, displayName, password, isLoading } = this.data;
    if (isLoading || !username || !email || !displayName || !password) {
      return;
    }

    this.setData({ isLoading: true, errorMessage: "" });
    try {
      const response = await register({
        username: username.trim(),
        email: email.trim(),
        display_name: displayName.trim(),
        password
      });
      getApp().setSession(response);
      wx.switchTab({ url: "/pages/submit/index" });
    } catch (error) {
      this.setData({
        errorMessage: normalizeErrorMessage(error, "注册失败，请稍后重试。")
      });
    } finally {
      this.setData({ isLoading: false });
    }
  },

  goBack() {
    wx.navigateBack();
  }
});
