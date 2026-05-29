Component({
  properties: {
    url: {
      type: String,
      value: ""
    }
  },
  methods: {
    handleCopy() {
      wx.setClipboardData({
        data: this.data.url
      });
    }
  }
});
