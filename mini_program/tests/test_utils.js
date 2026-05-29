const assert = require("assert");
const { extractVideoUrl } = require("../utils/url");
const { filterAndSortRecords, normalizeVideoType, collectCategories, enrichRecord } = require("../utils/records");

function testUrlExtraction() {
  assert.strictEqual(
    extractVideoUrl("https://v.douyin.com/Xz6xQlScdQA/mailto:N@w.sr"),
    "https://v.douyin.com/Xz6xQlScdQA/"
  );
  assert.strictEqual(
    extractVideoUrl("https://v.douyin.com/Q61HfJgDQmw/ :6pm 08/11 lPk:/ P@k.CU "),
    "https://v.douyin.com/Q61HfJgDQmw/"
  );
  assert.strictEqual(extractVideoUrl("普通文本"), "");
}

function testRecordHelpers() {
  const records = [
    enrichRecord({
      id: "1",
      title: "教程视频",
      author: "作者A",
      summary: "入门总结",
      corrected_text: "详细内容一",
      core_points: ["观点一"],
      golden_sentences: ["金句一"],
      tags: ["教程"],
      video_type: "教程类",
      status: "待处理",
      created_at: "2026-05-29T10:00:00Z",
      processed_at: null,
      processing_stage: "queued",
      processing_detail: "等待执行",
      is_favorited: false
    }),
    enrichRecord({
      id: "2",
      title: "工具推荐",
      author: "作者B",
      summary: "工具总结",
      corrected_text: "详细内容二",
      core_points: [],
      golden_sentences: [],
      tags: ["工具"],
      video_type: "工具推荐",
      status: "已完成",
      created_at: "2026-05-28T10:00:00Z",
      processed_at: "2026-05-29T12:00:00Z",
      processing_stage: "",
      processing_detail: "",
      is_favorited: true
    })
  ];

  assert.strictEqual(normalizeVideoType("教程类"), "教程");
  assert.deepStrictEqual(collectCategories(records), ["全部类别", "工具推荐", "教程"]);
  assert.strictEqual(filterAndSortRecords(records, "工具", "全部类别", "newest")[0].id, "2");
  assert.strictEqual(filterAndSortRecords(records, "", "教程", "newest").length, 1);
}

testUrlExtraction();
testRecordHelpers();
console.log("mini_program utils tests passed");
