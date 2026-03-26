import { UserDTO } from "../types/api";

const TOKEN_KEY = "video-copy-web-token";
const USER_KEY = "video-copy-web-user";

export interface SessionState {
  token: string | null;
  user: UserDTO | null;
}

export function getStoredSession(): SessionState {
  const token = localStorage.getItem(TOKEN_KEY);
  const userRaw = localStorage.getItem(USER_KEY);
  return {
    token,
    user: userRaw ? (JSON.parse(userRaw) as UserDTO) : null
  };
}

export function setSession(token: string, user: UserDTO): void {
  localStorage.setItem(TOKEN_KEY, token);
  localStorage.setItem(USER_KEY, JSON.stringify(user));
}

export function clearSession(): void {
  localStorage.removeItem(TOKEN_KEY);
  localStorage.removeItem(USER_KEY);
}
