import type { Task } from "../types"

export default function TaskList({ tasks }: { tasks: Task[] }) {
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
              </div>
              <div className={`status status-${task.status}`}>{task.status}</div>
            </div>
          ))
        )}
      </div>
    </div>
  )
}
