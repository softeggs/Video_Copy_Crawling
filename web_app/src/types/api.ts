export interface UserDTO {
  user_id: string;
  username: string;
  display_name: string;
  table_id: string;
}

export interface LoginResponse {
  token: string;
  user: UserDTO;
}

export interface VideoSubmitResponse {
  success: boolean;
  record_id: string;
  status: string;
  estimated_time: string | null;
  message: string | null;
}

export interface VideoRecordDTO {
  id: string;
  title: string;
  author: string;
  url: string;
  summary: string;
  core_points: string[];
  corrected_text: string;
  golden_sentences: string[];
  tags: string[];
  video_type: string;
  status: string;
  markdown_content: string;
  created_at: string;
  processed_at: string | null;
}

export interface VideoListResponse {
  total: number;
  page: number;
  page_size: number;
  items: VideoRecordDTO[];
  has_more: boolean;
}

export interface TypeStatDTO {
  video_type: string;
  count: number;
}

export interface VideoOverviewResponse {
  total: number;
  today: number;
  pending: number;
}
