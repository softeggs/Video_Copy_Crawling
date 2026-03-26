import { FormEvent, useState } from "react";
import { Link, useNavigate } from "react-router-dom";

import { login } from "../api/auth";
import { setSession } from "../lib/session";

export function LoginPage() {
  const navigate = useNavigate();
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setSubmitting(true);
    setError(null);

    try {
      const response = await login(username, password);
      setSession(response.token, response.user);
      navigate("/submit", { replace: true });
    } catch (submitError) {
      setError(submitError instanceof Error ? submitError.message : "登录失败");
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <div className="auth-page">
      <form className="card auth-card" onSubmit={handleSubmit}>
        <h1>登录</h1>
        <p>默认对接本地后端，统一用户数据。</p>
        <input placeholder="用户名" value={username} onChange={(event) => setUsername(event.target.value)} />
        <input
          placeholder="密码"
          type="password"
          value={password}
          onChange={(event) => setPassword(event.target.value)}
        />
        {error ? <p className="error-text">{error}</p> : null}
        <button className="primary-button" disabled={submitting} type="submit">
          {submitting ? "登录中..." : "登录"}
        </button>
        <Link to="/register">没有账号？去注册</Link>
      </form>
    </div>
  );
}
