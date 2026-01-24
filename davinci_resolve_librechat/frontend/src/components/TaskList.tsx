import { useState } from "react"
import type { Task, TaskAssetItem } from "../types"

export default function TaskList({
  tasks,
  onRetry
}: {
  tasks: Task[]
  onRetry: (id: string) => void
}) {
  const [expandedMap, setExpandedMap] = useState<Record<string, boolean>>({})

  const toggle = (id: string) => {
    setExpandedMap((prev) => ({ ...prev, [id]: !prev[id] }))
  }

  const formatTime = (value?: string) => {
    if (!value) {
      return "-"
    }
    const date = new Date(value)
    if (Number.isNaN(date.getTime())) {
      return value
    }
    return date.toLocaleString()
  }

  const renderJson = (value: unknown) => {
    if (value === undefined) {
      return "-"
    }
    return JSON.stringify(value, null, 2)
  }

  const renderAssetList = (values?: TaskAssetItem[]) => {
    if (!values || values.length === 0) {
      return "-"
    }
    return values.map((item) => `${item.status} | ${item.url}`).join("\n")
  }

  return (
    <div className="card">
      <div className="card-title">任务列表</div>
      <div className="list">
        {tasks.length === 0 ? (
          <div className="empty">暂无任务</div>
        ) : (
          tasks.map((task) => (
            <div key={task._id} className="list-item">
              <div className="list-main">
                <div className="list-title">{task.title || "未命名任务"}</div>
                <div className="list-subtitle">{task.prompt || "-"}</div>
                {task.error ? <div className="list-error">{task.error}</div> : null}
                <div className="list-meta">
                  <span>状态: {task.status}</span>
                  <span>重试: {task.retryCount || 0}</span>
                  <span>更新: {formatTime(task.updatedAt)}</span>
                </div>
                <div className="list-actions">
                  <button type="button" className="ghost" onClick={() => toggle(task._id)}>
                    {expandedMap[task._id] ? "收起" : "详情"}
                  </button>
                  {task.status === "failed" && task.mcp ? (
                    <button type="button" className="ghost" onClick={() => onRetry(task._id)}>
                      重试
                    </button>
                  ) : null}
                </div>
                {expandedMap[task._id] ? (
                  <div className="list-details">
                    <div className="detail-row">
                      <div className="detail-label">场景ID</div>
                      <div className="detail-value">{task.scenarioId || "-"}</div>
                    </div>
                    <div className="detail-row">
                      <div className="detail-label">场景版本</div>
                      <div className="detail-value">
                        {task.scenarioVersion === undefined ? "-" : task.scenarioVersion}
                      </div>
                    </div>
                    <div className="detail-row">
                      <div className="detail-label">视频素材</div>
                      <pre className="detail-pre">{renderAssetList(task.assets?.videos)}</pre>
                    </div>
                    <div className="detail-row">
                      <div className="detail-label">图片素材</div>
                      <pre className="detail-pre">{renderAssetList(task.assets?.images)}</pre>
                    </div>
                    <div className="detail-row">
                      <div className="detail-label">音乐素材</div>
                      <pre className="detail-pre">{renderAssetList(task.assets?.audios)}</pre>
                    </div>
                    <div className="detail-row">
                      <div className="detail-label">结果</div>
                      <pre className="detail-pre">{renderJson(task.result)}</pre>
                    </div>
                  </div>
                ) : null}
              </div>
              <div className={`status status-${task.status}`}>{task.status}</div>
            </div>
          ))
        )}
      </div>
    </div>
  )
}
