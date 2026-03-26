import { describe, expect, it } from "vitest";

import { buildApiUrl } from "./client";

describe("buildApiUrl", () => {
  it("normalises relative paths", () => {
    expect(buildApiUrl("/health")).toContain("/health");
    expect(buildApiUrl("videos")).toContain("/videos");
  });
});
