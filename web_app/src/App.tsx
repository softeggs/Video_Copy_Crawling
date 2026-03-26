import { Link, Navigate, Route, Routes, useLocation, useNavigate } from "react-router-dom";

import { LoginPage } from "./pages/LoginPage";
import { RegisterPage } from "./pages/RegisterPage";
import { SubmitPage } from "./pages/SubmitPage";
import { HistoryPage } from "./pages/HistoryPage";
import { DetailPage } from "./pages/DetailPage";
import { ProfilePage } from "./pages/ProfilePage";
import { clearSession, getStoredSession } from "./lib/session";

function AppShell() {
  const navigate = useNavigate();
  const location = useLocation();
  const session = getStoredSession();

  if (!session.token || !session.user) {
    return <Navigate to="/login" replace />;
  }

  return (
    <div className="shell">
      <aside className="sidebar">
        <div>
          <h1>视频情报</h1>
          <p>本地联调版 Web 用户端</p>
        </div>

        <nav className="nav">
          <Link className={location.pathname === "/submit" ? "active" : ""} to="/submit">
            提交视频
          </Link>
          <Link className={location.pathname === "/history" ? "active" : ""} to="/history">
            历史记录
          </Link>
          <Link className={location.pathname === "/profile" ? "active" : ""} to="/profile">
            我的
          </Link>
        </nav>

        <button
          className="secondary-button"
          onClick={() => {
            clearSession();
            navigate("/login", { replace: true });
          }}
          type="button"
        >
          退出登录
        </button>
      </aside>

      <main className="content">
        <Routes>
          <Route path="/submit" element={<SubmitPage />} />
          <Route path="/history" element={<HistoryPage />} />
          <Route path="/history/:videoId" element={<DetailPage />} />
          <Route path="/profile" element={<ProfilePage />} />
          <Route path="*" element={<Navigate to="/submit" replace />} />
        </Routes>
      </main>
    </div>
  );
}

export default function App() {
  const session = getStoredSession();

  return (
    <Routes>
      <Route path="/login" element={session.token ? <Navigate to="/submit" replace /> : <LoginPage />} />
      <Route path="/register" element={session.token ? <Navigate to="/submit" replace /> : <RegisterPage />} />
      <Route path="/*" element={<AppShell />} />
    </Routes>
  );
}
