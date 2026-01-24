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

export type User = {
  id: string
  email: string
  name: string
  avatarUrl?: string
}

export type ChatMessage = {
  id: string
  role: "user" | "assistant"
  content: string
  taskId?: string
}

export type Conversation = {
  id: string
  title: string
  messages: ChatMessage[]
}
