Page({
  data: {
    steps: [
      {
        icon: "1",
        title: "安装快捷指令",
        description: "在 iPhone 上打开快捷指令应用，将现有服务器提交流程导入到快捷指令库。"
      },
      {
        icon: "2",
        title: "设置轻点背面",
        description: "前往 设置 > 辅助功能 > 触控 > 轻点背面，选择双击或三击。"
      },
      {
        icon: "3",
        title: "绑定快捷指令密钥",
        description: "回到本小程序的快捷指令密钥管理页，生成密钥并填入快捷指令请求体。"
      },
      {
        icon: "4",
        title: "提交到服务器",
        description: "快捷指令通过 POST /shortcut-submit 将链接直接发到服务器，无需再写飞书多维表格。"
      }
    ],
    endpoint: "http://42.194.144.122:8002/shortcut-submit"
  },

  copyEndpoint() {
    wx.setClipboardData({
      data: this.data.endpoint
    });
  }
});
