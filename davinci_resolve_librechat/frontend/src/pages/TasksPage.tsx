import TaskForm from "../components/TaskForm"
import TaskList from "../components/TaskList"
import type { Task } from "../types"

export default function TasksPage({
  tasks,
  onCreate,
  onRetry
}: {
  tasks: Task[]
  onCreate: (input: {
    title?: string
    prompt?: string
    mcpMethod?: string
    mcpParams?: string
  }) => Promise<void>
  onRetry: (id: string) => Promise<void>
}) {
  return (
    <div className="tasks-layout">
      <TaskForm onSubmit={onCreate} />
      <TaskList tasks={tasks} onRetry={onRetry} />
    </div>
  )
}
