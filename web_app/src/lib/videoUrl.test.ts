import { describe, expect, it } from "vitest";

import { normalizeVideoUrl, validateVideoUrl } from "./videoUrl";

describe("videoUrl validation", () => {
  it("normalizes links without protocol", () => {
    expect(normalizeVideoUrl("www.bilibili.com/video/BV1xx411c7mD")).toBe(
      "https://www.bilibili.com/video/BV1xx411c7mD"
    );
  });

  it("rejects invalid short values", () => {
    expect(validateVideoUrl("1")).toEqual({
      isValid: false,
      normalizedUrl: "1",
      error: "请输入有效的视频链接"
    });
  });
});
