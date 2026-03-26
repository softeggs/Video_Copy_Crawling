import { LoginResponse } from "../types/api";
import { requestJson } from "./client";

export function login(username: string, password: string): Promise<LoginResponse> {
  return requestJson<LoginResponse>("/auth/login", {
    method: "POST",
    body: JSON.stringify({ username, password })
  });
}

export function register(username: string, email: string, displayName: string, password: string): Promise<LoginResponse> {
  return requestJson<LoginResponse>("/auth/register", {
    method: "POST",
    body: JSON.stringify({
      username,
      email,
      display_name: displayName,
      password
    })
  });
}
