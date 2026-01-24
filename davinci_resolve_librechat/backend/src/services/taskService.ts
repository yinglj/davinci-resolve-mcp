import type { Server } from "socket.io"
import { Task } from "../models/Task.js"
import type { TaskDocument } from "../models/Task.js"
import type { TaskInput, TaskStatus } from "../types.js"
import { callMcp } from "./mcpClient.js"

let socketServer: Server | null = null

export function setSocket(server: Server) {
  socketServer = server
}

function emitTaskUpdate(task: TaskDocument) {
  if (socketServer) {
    socketServer.emit("task:update", task)
  }
}

export async function listTasks() {
  return Task.find().sort({ updatedAt: -1 }).lean()
}

export async function getTaskById(id: string) {
  return Task.findById(id).lean()
}

export async function createTask(input: TaskInput) {
  const initialStatus: TaskStatus = input.mcp ? "running" : "pending"
  const task = await Task.create({
    title: input.title,
    prompt: input.prompt,
    status: initialStatus,
    steps: input.steps || [],
    mcp: input.mcp
  })
  const taskObject = task.toObject()
  emitTaskUpdate(taskObject)
  if (input.mcp) {
    void runMcpTask(taskObject._id.toString(), input.mcp)
  }
  return taskObject
}

async function runMcpTask(id: string, mcp: NonNullable<TaskInput["mcp"]>) {
  try {
    const result = await callMcp(mcp)
    const updated = await Task.findByIdAndUpdate(
      id,
      { status: "completed", result },
      { new: true }
    ).lean()
    if (updated) {
      emitTaskUpdate(updated)
    }
  } catch (error) {
    const message = error instanceof Error ? error.message : "Unknown error"
    const updated = await Task.findByIdAndUpdate(
      id,
      { status: "failed", error: message },
      { new: true }
    ).lean()
    if (updated) {
      emitTaskUpdate(updated)
    }
  }
}
