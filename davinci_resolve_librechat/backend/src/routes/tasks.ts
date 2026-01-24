import { Router, Request, Response } from "express"
import { createTask, getTaskById, listTasks } from "../services/taskService.js"
import type { TaskInput } from "../types.js"

export const tasksRouter = Router()

const asyncHandler =
  (fn: (req: Request, res: Response) => Promise<void>) =>
  (req: Request, res: Response) => {
    fn(req, res).catch((error) => {
      res.status(500).json({ error: error instanceof Error ? error.message : "Server error" })
    })
  }

tasksRouter.get(
  "/",
  asyncHandler(async (_req, res) => {
    const tasks = await listTasks()
    res.json({ tasks })
  })
)

tasksRouter.get(
  "/:id",
  asyncHandler(async (req, res) => {
    const task = await getTaskById(req.params.id)
    if (!task) {
      res.status(404).json({ error: "Task not found" })
      return
    }
    res.json({ task })
  })
)

tasksRouter.post(
  "/",
  asyncHandler(async (req, res) => {
    const input = req.body as TaskInput
    if (!input.title && !input.prompt && !input.mcp) {
      res.status(400).json({ error: "title or prompt or mcp is required" })
      return
    }
    if (input.mcp && !input.mcp.method) {
      res.status(400).json({ error: "mcp.method is required" })
      return
    }
    const task = await createTask(input)
    res.status(201).json({ task })
  })
)
