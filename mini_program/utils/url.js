const SUPPORTED_HOSTS = [
  "bilibili.com",
  "b23.tv",
  "xiaohongshu.com",
  "xhslink.com",
  "douyin.com",
  "iesdouyin.com",
  "v.douyin.com"
];

function trimNoise(text) {
  return String(text || "").trim();
}

function removeFragment(value) {
  return value.split("#")[0];
}

function stripTrailingShareNoise(value) {
  let nextValue = value.replace(/[，。；！？)\]>'"\s]+$/g, "");
  const mailtoIndex = nextValue.toLowerCase().indexOf("/mailto:");
  if (mailtoIndex !== -1) {
    nextValue = nextValue.slice(0, mailtoIndex + 1);
  }
  const firstWhitespaceIndex = nextValue.search(/\s/);
  if (firstWhitespaceIndex !== -1) {
    nextValue = nextValue.slice(0, firstWhitespaceIndex);
  }
  return nextValue;
}

function extractHost(candidate) {
  const matched = candidate.match(/^(https?:\/\/)?([^/?#]+)/i);
  return matched ? matched[2].toLowerCase() : "";
}

function isSupportedHost(host) {
  return SUPPORTED_HOSTS.some((item) => host === item || host.endsWith(`.${item}`));
}

function normalizeSupportedUrl(candidate) {
  const trimmed = trimNoise(candidate);
  if (!trimmed) {
    return "";
  }

  const valueWithScheme = trimmed.includes("://") ? trimmed : `https://${trimmed}`;
  const cleaned = stripTrailingShareNoise(removeFragment(valueWithScheme));
  const host = extractHost(cleaned);
  if (!host || !isSupportedHost(host)) {
    return "";
  }
  return cleaned;
}

function extractVideoUrl(text) {
  const raw = trimNoise(text);
  if (!raw) {
    return "";
  }

  const direct = normalizeSupportedUrl(raw);
  if (direct) {
    return direct;
  }

  const matches = raw.match(/https?:\/\/[^\s"'<>`]+/gi) || [];
  for (let index = 0; index < matches.length; index += 1) {
    const normalized = normalizeSupportedUrl(matches[index]);
    if (normalized) {
      return normalized;
    }
  }

  const hostMatches = raw.match(/(?:www\.)?(?:b23\.tv|(?:www\.)?bilibili\.com|(?:www\.)?xiaohongshu\.com|xhslink\.com|(?:www\.)?douyin\.com|iesdouyin\.com|v\.douyin\.com)[^\s"'<>`]*/gi) || [];
  for (let index = 0; index < hostMatches.length; index += 1) {
    const normalized = normalizeSupportedUrl(hostMatches[index]);
    if (normalized) {
      return normalized;
    }
  }

  return "";
}

module.exports = {
  SUPPORTED_HOSTS,
  extractVideoUrl,
  normalizeSupportedUrl
};
