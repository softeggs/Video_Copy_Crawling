const DEFAULT_BASE_URL = "http://127.0.0.1:8002";

export function getApiBaseUrl(): string {
  const rawValue = import.meta.env.VITE_API_BASE_URL ?? DEFAULT_BASE_URL;
  return rawValue.replace(/\/+$/, "");
}

export function buildApiUrl(path: string): string {
  const normalisedPath = path.startsWith("/") ? path : `/${path}`;
  return `${getApiBaseUrl()}${normalisedPath}`;
}

function extractErrorMessage(payload: unknown): string | null {
  if (typeof payload === "string" && payload.trim()) {
    return payload;
  }

  if (payload && typeof payload === "object") {
    const detail = (payload as Record<string, unknown>).detail;

    if (typeof detail === "string" && detail.trim()) {
      return detail;
    }

    if (Array.isArray(detail)) {
      const messages = detail
        .map((item) => {
          if (item && typeof item === "object" && typeof (item as Record<string, unknown>).msg === "string") {
            return String((item as Record<string, unknown>).msg);
          }
          return null;
        })
        .filter(Boolean);

      if (messages.length > 0) {
        return messages.join("；");
      }
    }
  }

  return null;
}

export async function requestJson<T>(path: string, init: RequestInit = {}): Promise<T> {
  const response = await fetch(buildApiUrl(path), {
    ...init,
    headers: {
      "Content-Type": "application/json",
      ...(init.headers ?? {})
    }
  });

  if (!response.ok) {
    const contentType = response.headers.get("content-type") ?? "";
    const payload = contentType.includes("application/json") ? await response.json() : await response.text();
    const message = extractErrorMessage(payload) ?? `Request failed with status ${response.status}`;
    throw new Error(message);
  }

  return (await response.json()) as T;
}
