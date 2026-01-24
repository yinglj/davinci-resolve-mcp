export type TaskStatus = "pending" | "running" | "completed" | "failed"

export type McpCall = {
  method: string
  params?: unknown
}

export type Task = {
  _id: string
  title?: string
  prompt?: string
  status: TaskStatus
  result?: unknown
  error?: string
  retryCount?: number
  createdAt?: string
  updatedAt?: string
  mcp?: McpCall
}

export type TaskInput = {
  title?: string
  prompt?: string
  mcp?: McpCall
}
