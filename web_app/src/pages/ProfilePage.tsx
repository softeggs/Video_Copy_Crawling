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
    <section className="card">
      <h2>个人信息</h2>
      <p>用户：{session.user?.display_name ?? session.user?.username ?? "未登录"}</p>
      <p>表格绑定：{session.user?.table_id || "当前由后端统一管理"}</p>
      <div className="meta-grid">
        <span>总视频：{query.data?.total ?? 0}</span>
        <span>今日新增：{query.data?.today ?? 0}</span>
        <span>待处理：{query.data?.pending ?? 0}</span>
      </div>
    </section>
  );
}
