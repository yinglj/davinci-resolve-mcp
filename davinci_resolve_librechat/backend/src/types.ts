export type TaskStatus = "pending" | "running" | "completed" | "failed"

export type TaskStep = {
  name: string
  status: TaskStatus
  detail?: string
}

export type McpCall = {
  method: string
  params?: unknown
}

export type TaskInput = {
  title?: string
  prompt?: string
  scenarioId?: string
  mcp?: McpCall
  steps?: TaskStep[]
}
