const { request } = require("./request");

function submitVideo(token, url) {
  return request({
    path: "/videos/submit",
    method: "POST",
    token,
    data: {
      url,
      table_id: ""
    }
  });
}

function fetchVideos(token, page, status) {
  const query = [`page=${page}`, "page_size=20"];
  if (status) {
    query.push(`status=${encodeURIComponent(status)}`);
  }
  return request({
    path: `/videos?${query.join("&")}`,
    method: "GET",
    token
  });
}

async function fetchAllVideos(token) {
  let page = 1;
  let hasMore = true;
  let items = [];

  while (hasMore) {
    const response = await fetchVideos(token, page);
    items = items.concat(response.items || []);
    hasMore = Boolean(response.has_more);
    page += 1;
  }

  return items;
}

function fetchVideo(token, recordId) {
  return request({
    path: `/videos/${recordId}`,
    method: "GET",
    token
  });
}

function fetchTypeStats(token) {
  return request({
    path: "/videos/stats",
    method: "GET",
    token
  });
}

function fetchOverview(token) {
  return request({
    path: "/videos/overview",
    method: "GET",
    token
  });
}

function deleteVideo(token, recordId) {
  return request({
    path: `/videos/${recordId}`,
    method: "DELETE",
    token
  });
}

function toggleFavorite(token, recordId, isFavorited) {
  return request({
    path: `/videos/${recordId}/favorite`,
    method: "POST",
    token,
    data: {
      is_favorited: isFavorited
    }
  });
}

module.exports = {
  submitVideo,
  fetchVideos,
  fetchAllVideos,
  fetchVideo,
  fetchTypeStats,
  fetchOverview,
  deleteVideo,
  toggleFavorite
};
