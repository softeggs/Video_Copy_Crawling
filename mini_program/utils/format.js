function displayDate(value) {
  if (!value) {
    return "--";
  }
  return String(value).slice(0, 10);
}

function displayDateTime(value) {
  if (!value) {
    return "--";
  }
  return String(value).replace("T", " ").replace("Z", "").slice(0, 19);
}

function getStatusTone(status) {
  switch (status) {
    case "已完成":
      return "completed";
    case "处理中":
      return "processing";
    case "失败":
      return "failed";
    default:
      return "pending";
  }
}

module.exports = {
  displayDate,
  displayDateTime,
  getStatusTone
};
