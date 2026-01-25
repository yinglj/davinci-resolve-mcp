import TaskForm from "../components/TaskForm"
import TaskList from "../components/TaskList"
import type { Scenario, Task, TaskAssetInput } from "../types"

export default function TasksPage({
  tasks,
  scenarios,
  apiBaseUrl,
  onCreate,
  onRetry
}: {
  tasks: Task[]
  scenarios: Scenario[]
  apiBaseUrl: string
  onCreate: (input: {
    title?: string
    prompt?: string
    scenarioId?: string
    assets?: TaskAssetInput
  }) => Promise<void>
  onRetry: (id: string) => Promise<void>
}) {
  return (
    <div className="tasks-layout">
      <TaskForm scenarios={scenarios} apiBaseUrl={apiBaseUrl} onSubmit={onCreate} />
      <TaskList tasks={tasks} onRetry={onRetry} />
    </div>
  )
}
