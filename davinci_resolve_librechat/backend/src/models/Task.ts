import mongoose, { Schema } from "mongoose"
import type { TaskStatus, TaskStep, McpCall, TaskAssets } from "../types.js"

export type TaskDocument = {
  ownerId?: string
  title?: string
  prompt?: string
  scenarioId?: string
  scenarioVersion?: number
  assets?: TaskAssets
  status: TaskStatus
  steps?: TaskStep[]
  mcp?: McpCall
  result?: unknown
  error?: string
  retryCount?: number
  createdAt: Date
  updatedAt: Date
}

const TaskSchema = new Schema<TaskDocument>(
  {
    ownerId: { type: String, index: true },
    title: { type: String },
    prompt: { type: String },
    scenarioId: { type: String },
    scenarioVersion: { type: Number },
    assets: { type: Schema.Types.Mixed },
    status: { type: String, required: true },
    steps: { type: [Schema.Types.Mixed], default: [] },
    mcp: { type: Schema.Types.Mixed },
    result: { type: Schema.Types.Mixed },
    error: { type: String },
    retryCount: { type: Number, default: 0 }
  },
  { timestamps: true }
)

export const Task = mongoose.model<TaskDocument>("Task", TaskSchema)
