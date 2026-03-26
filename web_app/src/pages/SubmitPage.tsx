import { useMutation, useQuery } from "@tanstack/react-query";
import { FormEvent, useState } from "react";

import { fetchTypeStats, submitVideo } from "../api/videos";
import { getStoredSession } from "../lib/session";
import { validateVideoUrl } from "../lib/videoUrl";

type FeedbackState = {
  tone: "success" | "error" | "info";
  text: string;
} | null;

export function SubmitPage() {
  const session = getStoredSession();
  const [url, setUrl] = useState("");
  const [feedback, setFeedback] = useState<FeedbackState>(null);

  const validation = url.trim() ? validateVideoUrl(url) : null;

  const statsQuery = useQuery({
    queryKey: ["video-stats", session.token],
    queryFn: () => fetchTypeStats(session.token ?? ""),
    enabled: Boolean(session.token)
  });

  const submitMutation = useMutation({
    mutationFn: (value: string) => submitVideo(session.token ?? "", value),
    onSuccess: (response) => {
      setFeedback({ tone: "success", text: `提交成功，当前状态：${response.status}` });
      setUrl("");
      void statsQuery.refetch();
    },
    onError: (error) => {
      setFeedback({
        tone: "error",
        text: error instanceof Error ? error.message : "提交失败，请稍后重试"
      });
    }
  });

  function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();

    if (!validation || !validation.isValid) {
      setFeedback({
        tone: "error",
        text: validation?.error ?? "请输入有效的视频链接"
      });
      return;
    }

    setFeedback(null);
    submitMutation.mutate(validation.normalizedUrl);
  }

  return (
    <div className="page-grid">
      <form className="card" onSubmit={handleSubmit}>
        <h2>提交视频链接</h2>
        <p>支持粘贴完整 `http(s)` 链接，也支持缺省协议的域名链接。</p>
        <textarea
          placeholder="例如：https://www.bilibili.com/video/BV1xx411c7mD"
          rows={4}
          value={url}
          onChange={(event) => setUrl(event.target.value)}
        />

        {validation?.isValid && validation.normalizedUrl !== url.trim() ? (
          <p className="info-text">将自动按以下链接提交：{validation.normalizedUrl}</p>
        ) : null}

        {validation && !validation.isValid ? <p className="error-text">{validation.error}</p> : null}

        <button
          className="primary-button"
          disabled={!url.trim() || Boolean(validation && !validation.isValid) || submitMutation.isPending}
          type="submit"
        >
          {submitMutation.isPending ? "提交中..." : "提交"}
        </button>

        {feedback ? <p className={`${feedback.tone}-text`}>{feedback.text}</p> : null}
      </form>

      <section className="card">
        <h2>类型统计</h2>
        {statsQuery.isLoading ? <p>加载中...</p> : null}
        {statsQuery.isError ? <p className="error-text">统计加载失败，请稍后刷新。</p> : null}
        {statsQuery.data?.length ? (
          statsQuery.data.map((item) => (
            <div className="stat-row" key={item.video_type}>
              <span>{item.video_type}</span>
              <strong>{item.count}</strong>
            </div>
          ))
        ) : (
          !statsQuery.isLoading && <p className="muted-text">当前还没有可统计的视频类型数据。</p>
        )}
      </section>
    </div>
  );
}
