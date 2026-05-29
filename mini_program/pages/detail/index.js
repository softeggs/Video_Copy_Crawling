const { requireSession } = require("../../utils/auth");
const { normalizeErrorMessage } = require("../../utils/errors");
const { fetchVideo } = require("../../services/videos");
const { displayDate, displayDateTime } = require("../../utils/format");
const { enrichRecord } = require("../../utils/records");

Page({
  data: {
    id: "",
    record: null,
    isLoading: false,
    errorMessage: ""
  },

  onLoad(options) {
    this.setData({ id: options.id || "" });
  },

  onShow() {
    if (!this.data.id) {
      this.setData({ errorMessage: "缺少视频 ID，当前无法定位详情记录。" });
      return;
    }
    this.loadDetail();
  },

  async loadDetail() {
    const session = requireSession();
    if (!session) {
      return;
    }

    this.setData({ isLoading: true, errorMessage: "" });
    try {
      const record = await fetchVideo(session.token, this.data.id);
      this.setData({
        record: this.decorateRecord(enrichRecord(record))
      });
    } catch (error) {
      this.setData({
        errorMessage: normalizeErrorMessage(error, "详情加载失败，请稍后重试。")
      });
    } finally {
      this.setData({ isLoading: false });
    }
  },

  decorateRecord(record) {
    return Object.assign({}, record, {
      displayDate: displayDate(record.processed_at || record.created_at),
      displayDateTime: displayDateTime(record.processed_at || record.created_at)
    });
  },

  handleCopySummary() {
    if (!this.data.record) {
      return;
    }
    wx.setClipboardData({
      data: this.data.record.summary || ""
    });
  },

  handleCopyLink() {
    if (!this.data.record) {
      return;
    }
    wx.setClipboardData({
      data: this.data.record.url || ""
    });
  },

  onShareAppMessage() {
    const record = this.data.record;
    return {
      title: record ? `${record.title || "视频情报"} - 视频情报提取` : "视频情报提取",
      path: `/pages/detail/index?id=${this.data.id}`
    };
  }
});
