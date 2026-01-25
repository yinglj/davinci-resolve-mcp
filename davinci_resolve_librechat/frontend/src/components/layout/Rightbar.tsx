import type { Task } from "../../types"

export default function Rightbar({ tasks }: { tasks: Task[] }) {
  const recentTasks = tasks.slice(0, 5)
  return (
    <aside className="rightbar">
      <div className="rightbar-section">
        <div className="rightbar-title">智能体与工具</div>
        <div className="rightbar-card">
          <div>智能体协同编辑</div>
          <div className="rightbar-muted">多工具协作与流程编排入口</div>
        </div>
        <div className="rightbar-card">
          <div>MCP 服务器</div>
          <div className="rightbar-muted">davinci_resolve_mcp</div>
        </div>
      </div>
      <div className="rightbar-section">
        <div className="rightbar-title">任务状态</div>
        <div className="rightbar-list">
          {recentTasks.length === 0 ? (
            <div className="rightbar-muted">暂无任务</div>
          ) : (
            recentTasks.map((task) => (
              <div key={task._id} className="rightbar-item">
                <div className="rightbar-item-title">{task.title || "未命名任务"}</div>
                <div className={`status status-${task.status}`}>{task.status}</div>
              </div>
            ))
          )}
        </div>
      </div>
      <div className="rightbar-section">
        <div className="rightbar-title">快捷入口</div>
        <div className="rightbar-actions">
          <button type="button" className="ghost">
            新建任务
          </button>
          <button type="button" className="ghost">
            任务模板
          </button>
          <button type="button" className="ghost">
            工具设置
          </button>
        </div>
      </div>
    </aside>
  )
}
