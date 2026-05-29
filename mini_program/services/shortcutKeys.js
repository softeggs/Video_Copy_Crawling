const { request } = require("./request");

function listShortcutKeys(token) {
  return request({
    path: "/shortcut-keys",
    method: "GET",
    token
  });
}

function createShortcutKey(token, name) {
  return request({
    path: "/shortcut-keys",
    method: "POST",
    token,
    data: { name }
  });
}

function revokeShortcutKey(token, keyId) {
  return request({
    path: `/shortcut-keys/${keyId}`,
    method: "DELETE",
    token
  });
}

module.exports = {
  listShortcutKeys,
  createShortcutKey,
  revokeShortcutKey
};
