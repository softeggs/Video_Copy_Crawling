const { request } = require("./request");

function login(username, password) {
  return request({
    path: "/auth/login",
    method: "POST",
    authenticated: false,
    data: {
      username,
      password
    }
  });
}

function register(payload) {
  return request({
    path: "/auth/register",
    method: "POST",
    authenticated: false,
    data: payload
  });
}

module.exports = {
  login,
  register
};
