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

export type TaskAssets = {
  videos?: TaskAssetItem[]
  images?: TaskAssetItem[]
  audios?: TaskAssetItem[]
}

export type TaskAssetInput = {
  videos?: string[]
  images?: string[]
  audios?: string[]
}

export type TaskAssetItem = {
  url: string
  type: "video" | "image" | "audio"
  source: "url"
  status: "validated" | "invalid" | "unverified"
  size?: number
  mime?: string
  error?: string
}

export type TaskInput = {
  title?: string
  prompt?: string
  scenarioId?: string
  scenarioVersion?: number
  assets?: TaskAssetInput
  mcp?: McpCall
  steps?: TaskStep[]
}
