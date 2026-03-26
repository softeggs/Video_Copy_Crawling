import { TypeStatDTO, VideoListResponse, VideoOverviewResponse, VideoRecordDTO, VideoSubmitResponse } from "../types/api";
import { requestJson } from "./client";

function authHeaders(token: string): HeadersInit {
  return { Authorization: `Bearer ${token}` };
}

export function submitVideo(token: string, url: string): Promise<VideoSubmitResponse> {
  return requestJson<VideoSubmitResponse>("/videos/submit", {
    method: "POST",
    headers: authHeaders(token),
    body: JSON.stringify({ url, table_id: "" })
  });
}

export function fetchVideos(token: string, page = 1, statusFilter?: string): Promise<VideoListResponse> {
  const params = new URLSearchParams({
    page: String(page),
    page_size: "20"
  });

  if (statusFilter) {
    params.set("status", statusFilter);
  }

  return requestJson<VideoListResponse>(`/videos?${params.toString()}`, {
    headers: authHeaders(token)
  });
}

export function fetchVideo(token: string, videoId: string): Promise<VideoRecordDTO> {
  return requestJson<VideoRecordDTO>(`/videos/${videoId}`, {
    headers: authHeaders(token)
  });
}

export function fetchTypeStats(token: string): Promise<TypeStatDTO[]> {
  return requestJson<TypeStatDTO[]>("/videos/stats", {
    headers: authHeaders(token)
  });
}

export function fetchOverview(token: string): Promise<VideoOverviewResponse> {
  return requestJson<VideoOverviewResponse>("/videos/overview", {
    headers: authHeaders(token)
  });
}
