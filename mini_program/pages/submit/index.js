const { requireSession } = require("../../utils/auth");
const { extractVideoUrl } = require("../../utils/url");
const { normalizeErrorMessage } = require("../../utils/errors");
const { fetchTypeStats, submitVideo } = require("../../services/videos");
const { getClipboardData, showModal } = require("../../utils/wx");

Page({
  data: {
    url: "",
    isSubmitting: false,
    isLoadingStats: false,
    errorMessage: "",
    typeStats: []
  },

  onShow() {
    const session = requireSession();
    if (!session) {
      return;
    }
    this.loadTypeStats(session.token);
  },

  onPullDownRefresh() {
    const session = requireSession();
    if (!session) {
      wx.stopPullDownRefresh();
      return;
    }
    this.loadTypeStats(session.token).finally(() => wx.stopPullDownRefresh());
  },

  onUrlInput(event) {
    this.setData({ url: event.detail.value });
  },

  async pasteFromClipboard() {
    try {
      const result = await getClipboardData();
      const extracted = extractVideoUrl(result.data || "");
      if (extracted) {
        this.setData({ url: extracted, errorMessage: "" });
      } else {
        this.setData({
          url: (result.data || "").trim(),
          errorMessage: "未识别到可提交的视频链接，请检查剪贴板内容。"
        });
      }
    } catch (error) {
      this.setData({
        errorMessage: "读取剪贴板失败，请手动粘贴。"
      });
    }
  },

  async handleSubmit() {
    const session = requireSession();
    if (!session || this.data.isSubmitting) {
      return;
    }

    const extractedUrl = extractVideoUrl(this.data.url);
    if (!extractedUrl) {
      this.setData({ errorMessage: "未识别到可提交的视频链接，请检查粘贴内容。" });
      return;
    }

    this.setData({
      isSubmitting: true,
      errorMessage: ""
    });

    try {
      const response = await submitVideo(session.token, extractedUrl);
      this.setData({ url: "" });
      await this.loadTypeStats(session.token);
      await showModal({
        title: "提交成功",
        content: `该视频已加入处理队列。当前状态：${response.status}`,
        showCancel: false
      });
    } catch (error) {
      this.setData({
        errorMessage: normalizeErrorMessage(error, "提交失败，请稍后重试。")
      });
    } finally {
      this.setData({ isSubmitting: false });
    }
  },

  async loadTypeStats(token) {
    this.setData({ isLoadingStats: true });
    try {
      const typeStats = await fetchTypeStats(token);
      this.setData({ typeStats });
    } catch (error) {
      this.setData({
        errorMessage: this.data.errorMessage || "类型统计加载失败，不影响提交主流程。"
      });
    } finally {
      this.setData({ isLoadingStats: false });
    }
  }
});
