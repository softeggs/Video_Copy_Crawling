Component({
  properties: {
    record: {
      type: Object,
      value: {}
    }
  },
  methods: {
    noop() {},
    handleTap() {
      this.triggerEvent("open", { id: this.data.record.id });
    },
    handleFavoriteTap() {
      this.triggerEvent("favorite", { id: this.data.record.id });
    },
    handleMoreTap() {
      this.triggerEvent("more", { id: this.data.record.id, title: this.data.record.title });
    }
  }
});
