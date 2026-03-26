import { useQuery } from "@tanstack/react-query";
import { useParams } from "react-router-dom";

import { fetchVideo } from "../api/videos";
import { getStoredSession } from "../lib/session";

export function DetailPage() {
  const session = getStoredSession();
  const { videoId = "" } = useParams();
  const query = useQuery({
    queryKey: ["video-detail", session.token, videoId],
    queryFn: () => fetchVideo(session.token ?? "", videoId),
    enabled: Boolean(session.token && videoId)
  });

  if (!videoId) {
    return (
      <section className="card">
        <div className="state-panel empty-panel">
          <strong>缺少视频 ID</strong>
          <p className="muted-text">当前无法定位详情记录，请从历史记录页重新进入。</p>
        </div>
      </section>
    );
  }

  return (
    <section className="card page-stack">
      {query.isLoading ? (
        <div className="state-panel loading-panel">
          <strong>正在加载视频详情</strong>
          <p className="muted-text">正在从后端读取摘要、状态和 Markdown 内容。</p>
        </div>
      ) : null}

      {query.isError ? (
        <div className="state-panel error-panel">
          <strong>详情加载失败</strong>
          <p className="muted-text">请稍后重试；如果问题持续存在，优先去调试台排查该记录。</p>
        </div>
      ) : null}

      {!query.isLoading && !query.isError && !query.data ? (
        <div className="state-panel empty-panel">
          <strong>没有找到对应视频</strong>
          <p className="muted-text">这条记录可能已被清理，或者当前账号没有访问权限。</p>
        </div>
      ) : null}

      {query.data ? (
        <>
          <div className="section-block">
            <h2>{query.data.title || "未命名视频"}</h2>
            <p>{query.data.summary || "当前还没有生成摘要内容。"}</p>
            <div className="meta-grid">
              <span>作者：{query.data.author || "未知作者"}</span>
              <span>类型：{query.data.video_type || "未分类"}</span>
              <span>状态：{query.data.status}</span>
            </div>
          </div>

          <div className="section-block">
            <h3>处理结果</h3>
            {query.data.markdown_content ? (
              <pre className="markdown-preview">{query.data.markdown_content}</pre>
            ) : (
              <div className="state-panel empty-panel compact-panel">
                <strong>Markdown 结果暂未生成</strong>
                <p className="muted-text">如果状态仍是待处理或处理中，可以稍后回来刷新。</p>
              </div>
            )}
          </div>
        </>
      ) : null}
    </section>
  );
}
