export type TaskStatus = "pending" | "running" | "completed" | "failed"

export type McpCall = {
  method: string
  params?: unknown
}

export type Task = {
  _id: string
  title?: string
  prompt?: string
  scenarioId?: string
  scenarioVersion?: number
  assets?: TaskAssets
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
  scenarioId?: string
  assets?: TaskAssetInput
  mcp?: McpCall
}

export type TaskAssetInput = {
  videos?: string[]
  images?: string[]
  audios?: string[]
}

export type TaskAssetItem = {
  url: string
  type: "video" | "image" | "audio"
  source: "url" | "upload"
  status: "validated" | "invalid" | "unverified"
  size?: number
  mime?: string
  error?: string
}

export type TaskAssets = {
  videos?: TaskAssetItem[]
  images?: TaskAssetItem[]
  audios?: TaskAssetItem[]
}

export type Scenario = {
  id: string
  name: string
  description: string
  version: number
  requiresPrompt: boolean
  requiredAssets: {
    videos?: boolean
    images?: boolean
    audios?: boolean
  }
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
