function getClipboardData() {
  return new Promise((resolve, reject) => {
    wx.getClipboardData({
      success: resolve,
      fail: reject
    });
  });
}

function showModal(options) {
  return new Promise((resolve, reject) => {
    wx.showModal({
      ...options,
      success: resolve,
      fail: reject
    });
  });
}

function showActionSheet(options) {
  return new Promise((resolve, reject) => {
    wx.showActionSheet({
      ...options,
      success: resolve,
      fail: reject
    });
  });
}

module.exports = {
  getClipboardData,
  showModal,
  showActionSheet
};
