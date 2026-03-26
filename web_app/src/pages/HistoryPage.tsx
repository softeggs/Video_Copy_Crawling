import { useQuery } from "@tanstack/react-query";
import { useState } from "react";
import { Link } from "react-router-dom";

import { fetchVideos } from "../api/videos";
import { getStoredSession } from "../lib/session";

const STATUS_OPTIONS = [
  { label: "全部状态", value: "" },
  { label: "待处理", value: "待处理" },
  { label: "处理中", value: "处理中" },
  { label: "已完成", value: "已完成" },
  { label: "失败", value: "失败" }
];

export function HistoryPage() {
  const session = getStoredSession();
  const [page, setPage] = useState(1);
  const [statusFilter, setStatusFilter] = useState("");

  const query = useQuery({
    queryKey: ["videos", session.token, page, statusFilter],
    queryFn: () => fetchVideos(session.token ?? "", page, statusFilter || undefined),
    enabled: Boolean(session.token)
  });

  const totalItems = query.data?.total ?? 0;
  const currentPage = query.data?.page ?? page;
  const totalPages = query.data ? Math.max(1, Math.ceil(query.data.total / query.data.page_size)) : 1;

  function handleStatusChange(value: string) {
    setStatusFilter(value);
    setPage(1);
  }

  return (
    <section className="card">
      <div className="section-header">
        <div>
          <h2>历史记录</h2>
          <p className="muted-text">按状态筛选并分页浏览你的处理记录。</p>
        </div>
        <div className="history-toolbar">
          <label className="filter-field">
            <span>状态筛选</span>
            <select value={statusFilter} onChange={(event) => handleStatusChange(event.target.value)}>
              {STATUS_OPTIONS.map((option) => (
                <option key={option.value || "all"} value={option.value}>
                  {option.label}
                </option>
              ))}
            </select>
          </label>
        </div>
      </div>

      {query.isLoading ? <p>加载中...</p> : null}
      {query.isError ? <p className="error-text">历史记录加载失败，请稍后重试。</p> : null}

      {!query.isLoading && !query.isError && query.data?.items.length === 0 ? (
        <div className="empty-state">
          <strong>当前筛选条件下还没有记录</strong>
          <p className="muted-text">你可以先去提交一个视频链接，或者切换筛选状态看看。</p>
        </div>
      ) : null}

      {query.data?.items.map((item) => (
        <Link className="list-item" key={item.id} to={`/history/${item.id}`}>
          <div>
            <strong>{item.title || "未命名视频"}</strong>
            <p>{item.author || "未知作者"}</p>
            <p className="muted-text">创建时间：{new Date(item.created_at).toLocaleString()}</p>
          </div>
          <span className="status-chip">{item.status}</span>
        </Link>
      ))}

      {query.data?.items.length ? (
        <div className="pagination-bar">
          <p className="muted-text">
            第 {currentPage} / {totalPages} 页，共 {totalItems} 条记录
          </p>
          <div className="pagination-actions">
            <button
              className="secondary-button"
              disabled={currentPage <= 1 || query.isFetching}
              onClick={() => setPage((value) => Math.max(1, value - 1))}
              type="button"
            >
              上一页
            </button>
            <button
              className="secondary-button"
              disabled={!query.data?.has_more || query.isFetching}
              onClick={() => setPage((value) => value + 1)}
              type="button"
            >
              下一页
            </button>
          </div>
        </div>
      ) : null}
    </section>
  );
}
