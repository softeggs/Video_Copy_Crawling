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

  return (
    <section className="card">
      {query.isLoading ? <p>加载中...</p> : null}
      {query.data ? (
        <>
          <h2>{query.data.title || "未命名视频"}</h2>
          <p>{query.data.summary || "暂无摘要"}</p>
          <div className="meta-grid">
            <span>作者：{query.data.author || "未知"}</span>
            <span>类型：{query.data.video_type}</span>
            <span>状态：{query.data.status}</span>
          </div>
          <pre className="markdown-preview">{query.data.markdown_content || "暂无 Markdown 内容"}</pre>
        </>
      ) : null}
    </section>
  );
}
