const PENDING_LIKE_STATUSES = ["待处理", "处理中", "AI润色中"];
const CATEGORY_ALL = "全部类别";

const STAGE_LABELS = {
  queued: "排队中",
  downloading: "下载视频",
  transcribing: "语音转写",
  ai_polishing: "AI 润色",
  syncing: "同步结果",
  completed: "已完成",
  failed: "失败"
};

function normalizeVideoType(rawValue) {
  const compacted = String(rawValue || "").trim().replace(/\s+/g, "");
  if (!compacted) {
    return "其他";
  }

  if (compacted.includes("工具推荐")) {
    return "工具推荐";
  }
  if (compacted.includes("教程")) {
    return "教程";
  }

  const suffixes = ["类型", "类别", "类", "分享"];
  let normalized = compacted;
  suffixes.forEach((suffix) => {
    if (normalized.endsWith(suffix) && normalized.length > suffix.length) {
      normalized = normalized.slice(0, -suffix.length);
    }
  });

  return normalized || "其他";
}

function buildSearchableContent(record) {
  return [
    record.title,
    record.author,
    record.summary,
    record.corrected_text,
    (record.core_points || []).join(" "),
    (record.golden_sentences || []).join(" "),
    (record.tags || []).join(" "),
    record.video_type,
    normalizeVideoType(record.video_type)
  ]
    .join(" ")
    .toLowerCase();
}

function collectCategories(records) {
  const categories = new Set();
  records.forEach((item) => {
    categories.add(normalizeVideoType(item.video_type));
  });
  return [CATEGORY_ALL].concat(Array.from(categories).sort());
}

function sortRecords(records, sortKey) {
  const sorted = records.slice();
  sorted.sort((left, right) => {
    const leftValue = left.processed_at || left.created_at || "";
    const rightValue = right.processed_at || right.created_at || "";
    if (sortKey === "oldest") {
      return leftValue.localeCompare(rightValue);
    }
    return rightValue.localeCompare(leftValue);
  });
  return sorted;
}

function filterAndSortRecords(records, query, category, sortKey) {
  const normalizedQuery = String(query || "").trim().toLowerCase();
  let result = records.slice();

  if (normalizedQuery) {
    result = result.filter((item) => buildSearchableContent(item).includes(normalizedQuery));
  }

  if (category && category !== CATEGORY_ALL) {
    result = result.filter((item) => normalizeVideoType(item.video_type) === category);
  }

  return sortRecords(result, sortKey);
}

function enrichRecord(record) {
  const normalizedType = normalizeVideoType(record.video_type);
  const stageLabel = record.processing_stage ? STAGE_LABELS[record.processing_stage] || record.processing_stage : "";
  const isProcessing = PENDING_LIKE_STATUSES.includes(record.status);
  return Object.assign({}, record, {
    normalizedVideoType: normalizedType,
    stageLabel,
    isProcessing
  });
}

module.exports = {
  CATEGORY_ALL,
  PENDING_LIKE_STATUSES,
  STAGE_LABELS,
  normalizeVideoType,
  collectCategories,
  filterAndSortRecords,
  enrichRecord
};
