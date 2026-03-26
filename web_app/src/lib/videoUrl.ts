const INVALID_VIDEO_URL_MESSAGE = "请输入有效的视频链接";

export interface VideoUrlValidationResult {
  isValid: boolean;
  normalizedUrl: string;
  error: string | null;
}

export function normalizeVideoUrl(rawUrl: string): string {
  const candidate = rawUrl.trim();

  if (!candidate) {
    throw new Error(INVALID_VIDEO_URL_MESSAGE);
  }

  if (candidate.startsWith("#")) {
    throw new Error(INVALID_VIDEO_URL_MESSAGE);
  }

  const lowered = candidate.toLowerCase();
  if (lowered.includes("netscape http cookie") || lowered.includes("cookie_spec")) {
    throw new Error(INVALID_VIDEO_URL_MESSAGE);
  }

  const withProtocol =
    candidate.startsWith("http://") || candidate.startsWith("https://") ? candidate : `https://${candidate}`;

  let parsed: URL;
  try {
    parsed = new URL(withProtocol);
  } catch {
    throw new Error(INVALID_VIDEO_URL_MESSAGE);
  }

  if (!["http:", "https:"].includes(parsed.protocol)) {
    throw new Error(INVALID_VIDEO_URL_MESSAGE);
  }

  if (!parsed.hostname || !parsed.hostname.includes(".")) {
    throw new Error(INVALID_VIDEO_URL_MESSAGE);
  }

  if ((parsed.pathname === "" || parsed.pathname === "/") && !parsed.search) {
    throw new Error(INVALID_VIDEO_URL_MESSAGE);
  }

  parsed.hash = "";
  return parsed.toString();
}

export function validateVideoUrl(rawUrl: string): VideoUrlValidationResult {
  try {
    const normalizedUrl = normalizeVideoUrl(rawUrl);
    return {
      isValid: true,
      normalizedUrl,
      error: null
    };
  } catch (error) {
    return {
      isValid: false,
      normalizedUrl: rawUrl.trim(),
      error: error instanceof Error ? error.message : INVALID_VIDEO_URL_MESSAGE
    };
  }
}
