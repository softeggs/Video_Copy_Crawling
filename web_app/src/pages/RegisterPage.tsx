import { FormEvent, useState } from "react";
import { Link, useNavigate } from "react-router-dom";

import { register } from "../api/auth";
import { setSession } from "../lib/session";

export function RegisterPage() {
  const navigate = useNavigate();
  const [username, setUsername] = useState("");
  const [email, setEmail] = useState("");
  const [displayName, setDisplayName] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setSubmitting(true);
    setError(null);

    try {
      const response = await register(username, email, displayName, password);
      setSession(response.token, response.user);
      navigate("/submit", { replace: true });
    } catch (submitError) {
      setError(submitError instanceof Error ? submitError.message : "注册失败");
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <div className="auth-page">
      <form className="card auth-card" onSubmit={handleSubmit}>
        <h1>注册</h1>
        <p>第一版仅使用账号密码体系。</p>
        <input placeholder="用户名" value={username} onChange={(event) => setUsername(event.target.value)} />
        <input placeholder="邮箱" value={email} onChange={(event) => setEmail(event.target.value)} />
        <input placeholder="显示名称" value={displayName} onChange={(event) => setDisplayName(event.target.value)} />
        <input
          placeholder="密码"
          type="password"
          value={password}
          onChange={(event) => setPassword(event.target.value)}
        />
        {error ? <p className="error-text">{error}</p> : null}
        <button className="primary-button" disabled={submitting} type="submit">
          {submitting ? "注册中..." : "注册"}
        </button>
        <Link to="/login">已有账号？去登录</Link>
      </form>
    </div>
  );
}
