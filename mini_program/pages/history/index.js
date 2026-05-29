const { requireSession } = require("../../utils/auth");
const { normalizeErrorMessage } = require("../../utils/errors");
const { fetchAllVideos, deleteVideo, toggleFavorite } = require("../../services/videos");
const { CATEGORY_ALL, collectCategories, filterAndSortRecords, enrichRecord } = require("../../utils/records");
const { displayDate, getStatusTone } = require("../../utils/format");
const { showActionSheet, showModal } = require("../../utils/wx");

Page({
  data: {
    allRecords: [],
    displayedRecords: [],
    categories: [CATEGORY_ALL],
    categoryIndex: 0,
    categoryValue: CATEGORY_ALL,
    sortOptions: ["最新优先", "最早优先"],
    sortIndex: 0,
    searchText: "",
    isLoading: false,
    errorMessage: ""
  },

  onShow() {
    const session = requireSession();
    if (!session) {
      return;
    }
    if (!this.data.allRecords.length) {
      this.refreshRecords();
    } else {
      this.applyFilters();
    }
  },

  onPullDownRefresh() {
    this.refreshRecords().finally(() => wx.stopPullDownRefresh());
  },

  onSearchInput(event) {
    this.setData({ searchText: event.detail.value }, () => this.applyFilters());
  },

  onSortChange(event) {
    const sortIndex = Number(event.detail.value);
    this.setData({ sortIndex }, () => this.applyFilters());
  },

  onCategoryChange(event) {
    const categoryIndex = Number(event.detail.value);
    const categoryValue = this.data.categories[categoryIndex] || CATEGORY_ALL;
    this.setData({ categoryIndex, categoryValue }, () => this.applyFilters());
  },

  async refreshRecords() {
    const session = requireSession();
    if (!session) {
      return;
    }

    this.setData({ isLoading: true, errorMessage: "" });
    try {
      const items = await fetchAllVideos(session.token);
      const allRecords = items.map((item) => this.decorateRecord(enrichRecord(item)));
      const categories = collectCategories(allRecords);
      const categoryIndex = categories.includes(this.data.categoryValue) ? categories.indexOf(this.data.categoryValue) : 0;
      const categoryValue = categories[categoryIndex];
      this.setData({ allRecords, categories, categoryIndex, categoryValue }, () => this.applyFilters());
    } catch (error) {
      this.setData({
        errorMessage: normalizeErrorMessage(error, "记录加载失败，请稍后重试。")
      });
    } finally {
      this.setData({ isLoading: false });
    }
  },

  applyFilters() {
    const sortKey = this.data.sortIndex === 1 ? "oldest" : "newest";
    const displayedRecords = filterAndSortRecords(
      this.data.allRecords,
      this.data.searchText,
      this.data.categoryValue,
      sortKey
    ).map((item) => this.decorateRecord(item));

    this.setData({ displayedRecords });
  },

  decorateRecord(record) {
    return Object.assign({}, record, {
      displayDate: displayDate(record.processed_at || record.created_at),
      statusTone: getStatusTone(record.status)
    });
  },

  openDetail(event) {
    const { id } = event.detail;
    wx.navigateTo({ url: `/pages/detail/index?id=${id}` });
  },

  async handleFavorite(event) {
    const session = requireSession();
    if (!session) {
      return;
    }

    const { id } = event.detail;
    const target = this.data.allRecords.find((item) => item.id === id);
    if (!target) {
      return;
    }

    try {
      const result = await toggleFavorite(session.token, id, !target.is_favorited);
      const allRecords = this.data.allRecords.map((item) => {
        if (item.id === id) {
          return this.decorateRecord(Object.assign({}, item, { is_favorited: result.is_favorited }));
        }
        return item;
      });
      this.setData({ allRecords }, () => this.applyFilters());
    } catch (error) {
      wx.showToast({
        title: normalizeErrorMessage(error, "收藏操作失败"),
        icon: "none"
      });
    }
  },

  async handleMore(event) {
    const { id, title } = event.detail;
    try {
      await showActionSheet({
        itemList: ["删除记录"]
      });
    } catch (error) {
      return;
    }

    const confirm = await showModal({
      title: "确认删除",
      content: `确定要删除「${title || "该记录"}」吗？此操作无法撤销。`
    });
    if (!confirm.confirm) {
      return;
    }
    const session = requireSession();
    if (!session) {
      return;
    }
    try {
      await deleteVideo(session.token, id);
      const allRecords = this.data.allRecords.filter((item) => item.id !== id);
      const categories = collectCategories(allRecords);
      const categoryValue = categories.includes(this.data.categoryValue) ? this.data.categoryValue : CATEGORY_ALL;
      const categoryIndex = categories.indexOf(categoryValue);
      this.setData({ allRecords, categories, categoryValue, categoryIndex }, () => this.applyFilters());
      wx.showToast({ title: "已删除", icon: "success" });
    } catch (error) {
      wx.showToast({
        title: normalizeErrorMessage(error, "删除失败"),
        icon: "none"
      });
    }
  }
});
