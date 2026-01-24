import mongoose, { Schema } from "mongoose"
import type { TaskStatus, TaskStep, McpCall } from "../types.js"

export type TaskDocument = {
  title?: string
  prompt?: string
  status: TaskStatus
  steps?: TaskStep[]
  mcp?: McpCall
  result?: unknown
  error?: string
  createdAt: Date
  updatedAt: Date
}

const TaskSchema = new Schema<TaskDocument>(
  {
    title: { type: String },
    prompt: { type: String },
    status: { type: String, required: true },
    steps: { type: [Schema.Types.Mixed], default: [] },
    mcp: { type: Schema.Types.Mixed },
    result: { type: Schema.Types.Mixed },
    error: { type: String }
  },
  { timestamps: true }
)

export const Task = mongoose.model<TaskDocument>("Task", TaskSchema)
