const { API_BASE_URL } = require("../config/env");

function request(options) {
  const {
    path,
    method = "GET",
    token = "",
    data,
    authenticated = true
  } = options;

  return new Promise((resolve, reject) => {
    wx.request({
      url: `${API_BASE_URL}${path}`,
      method,
      data,
      timeout: 20000,
      header: {
        Accept: "application/json",
        "Content-Type": "application/json",
        ...(authenticated && token ? { Authorization: `Bearer ${token}` } : {})
      },
      success(response) {
        const { statusCode, data: payload } = response;
        if (statusCode >= 200 && statusCode < 300) {
          resolve(payload);
          return;
        }

        const message = extractErrorMessage(payload);
        if (statusCode === 401) {
          const app = getApp();
          if (app && typeof app.clearSession === "function") {
            app.clearSession();
          }
          wx.reLaunch({ url: "/pages/login/index" });
          reject(new Error(message || "登录已失效，请重新登录。"));
          return;
        }

        reject(new Error(message || `请求失败(${statusCode})`));
      },
      fail(error) {
        reject(new Error(error.errMsg || "网络异常，请稍后重试。"));
      }
    });
  });
}

function extractErrorMessage(payload) {
  if (!payload) {
    return "";
  }

  if (typeof payload.detail === "string") {
    return payload.detail;
  }

  if (Array.isArray(payload.detail)) {
    const message = payload.detail
      .map((item) => item && item.msg)
      .filter(Boolean)
      .join("\n");
    return message;
  }

  if (typeof payload.message === "string") {
    return payload.message;
  }

  return "";
}

module.exports = {
  request
};
