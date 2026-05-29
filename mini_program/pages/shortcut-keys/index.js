const { requireSession } = require("../../utils/auth");
const { normalizeErrorMessage } = require("../../utils/errors");
const { listShortcutKeys, createShortcutKey, revokeShortcutKey } = require("../../services/shortcutKeys");
const { showModal } = require("../../utils/wx");

Page({
  data: {
    keys: [],
    isLoading: false,
    errorMessage: "",
    newKeyName: "",
    createdKey: null
  },

  onShow() {
    const session = requireSession();
    if (!session) {
      return;
    }
    this.loadKeys(session.token);
  },

  onPullDownRefresh() {
    const session = requireSession();
    if (!session) {
      wx.stopPullDownRefresh();
      return;
    }
    this.loadKeys(session.token).finally(() => wx.stopPullDownRefresh());
  },

  onNameInput(event) {
    this.setData({ newKeyName: event.detail.value });
  },

  async loadKeys(token) {
    this.setData({ isLoading: true, errorMessage: "" });
    try {
      const keys = await listShortcutKeys(token);
      this.setData({ keys: this.decorateKeys(keys) });
    } catch (error) {
      this.setData({
        errorMessage: normalizeErrorMessage(error, "密钥列表加载失败。")
      });
    } finally {
      this.setData({ isLoading: false });
    }
  },

  async handleCreate() {
    const session = requireSession();
    if (!session || this.data.isLoading) {
      return;
    }

    const name = this.data.newKeyName.trim() || "快捷指令密钥";
    this.setData({ isLoading: true, errorMessage: "" });
    try {
      const createdKey = await createShortcutKey(session.token, name);
      const normalizedCreatedKey = Object.assign({}, createdKey, {
        created_date: String(createdKey.created_at || "").slice(0, 10)
      });
      this.setData({
        createdKey: normalizedCreatedKey,
        newKeyName: "",
        keys: this.decorateKeys([
          {
            id: normalizedCreatedKey.id,
            key_prefix: normalizedCreatedKey.key_prefix,
            name: normalizedCreatedKey.name,
            is_active: true,
            created_at: normalizedCreatedKey.created_at,
            last_used_at: null
          }
        ].concat(this.data.keys))
      });
    } catch (error) {
      this.setData({
        errorMessage: normalizeErrorMessage(error, "生成密钥失败。")
      });
    } finally {
      this.setData({ isLoading: false });
    }
  },

  copyCreatedKey() {
    if (!this.data.createdKey) {
      return;
    }
    wx.setClipboardData({
      data: this.data.createdKey.key
    });
  },

  async handleRevoke(event) {
    const session = requireSession();
    if (!session) {
      return;
    }

    const keyId = event.detail.id;
    const confirm = await showModal({
      title: "确认吊销密钥",
      content: "吊销后该密钥立即失效，无法恢复。确定要吊销吗？"
    });
    if (!confirm.confirm) {
      return;
    }

    try {
      await revokeShortcutKey(session.token, keyId);
      const keys = this.decorateKeys(this.data.keys.map((item) => {
        if (item.id === keyId) {
          return Object.assign({}, item, { is_active: false });
        }
        return item;
      }));
      this.setData({ keys });
    } catch (error) {
      wx.showToast({
        title: normalizeErrorMessage(error, "吊销失败"),
        icon: "none"
      });
    }
  },

  decorateKeys(keys) {
    return keys.map((item) =>
      Object.assign({}, item, {
        created_date: String(item.created_at || "").slice(0, 10),
        last_used_label: item.last_used_at ? `最后使用：${String(item.last_used_at).slice(0, 10)}` : "从未使用"
      })
    );
  }
});
