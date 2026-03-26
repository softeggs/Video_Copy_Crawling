import { useQuery } from "@tanstack/react-query";

import { fetchOverview } from "../api/videos";
import { getStoredSession } from "../lib/session";

export function ProfilePage() {
  const session = getStoredSession();
  const query = useQuery({
    queryKey: ["overview", session.token],
    queryFn: () => fetchOverview(session.token ?? ""),
    enabled: Boolean(session.token)
  });

  return (
    <section className="card page-stack">
      <div className="section-block">
        <h2>个人信息</h2>
        <p>用户：{session.user?.display_name ?? session.user?.username ?? "未登录"}</p>
        <p>表格绑定：{session.user?.table_id || "当前由后端统一管理"}</p>
      </div>

      {query.isLoading ? (
        <div className="state-panel loading-panel">
          <strong>正在加载个人概览</strong>
          <p className="muted-text">即将展示总视频数、今日新增和待处理数量。</p>
        </div>
      ) : null}

      {query.isError ? (
        <div className="state-panel error-panel">
          <strong>个人概览加载失败</strong>
          <p className="muted-text">后端概览接口暂时不可用，请稍后刷新再试。</p>
        </div>
      ) : null}

      {query.data ? (
        <div className="section-block">
          <h3>数据概览</h3>
          <div className="meta-grid">
            <span>总视频：{query.data.total}</span>
            <span>今日新增：{query.data.today}</span>
            <span>待处理：{query.data.pending}</span>
          </div>
        </div>
      ) : null}
    </section>
  );
}
