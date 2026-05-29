Component({
  properties: {
    item: {
      type: Object,
      value: {}
    }
  },
  methods: {
    handleRevoke() {
      this.triggerEvent("revoke", { id: this.data.item.id });
    }
  }
});
