import { Router, Request, Response } from "express"
import { createTask, getTaskById, listTasks, retryTask } from "../services/taskService.js"
import type { TaskInput } from "../types.js"
import { requireAuth, type AuthedRequest } from "../middleware/auth.js"

export const tasksRouter = Router()

const asyncHandler =
  (fn: (req: Request, res: Response) => Promise<void>) =>
  (req: Request, res: Response) => {
    fn(req, res).catch((error) => {
      res.status(500).json({ error: error instanceof Error ? error.message : "Server error" })
    })
  }

type ScenarioDefinition = {
  id: string
  method: string
  buildParams: (prompt: string) => Record<string, unknown>
}

const scenarioDefinitions: ScenarioDefinition[] = [
  {
    id: "color-style",
    method: "color_apply_style",
    buildParams: (prompt) => ({ style: "cinematic", prompt })
  },
  {
    id: "audio-normalize",
    method: "audio_normalize_loudness",
    buildParams: (prompt) => ({ targetLufs: -14, prompt })
  },
  {
    id: "fusion-transition",
    method: "fusion_add_transition",
    buildParams: (prompt) => ({ transition: "smooth", prompt })
  }
]

const scenarioMap = new Map(scenarioDefinitions.map((item) => [item.id, item]))

const applyScenarioToInput = (input: TaskInput) => {
  if (!input.scenarioId || input.mcp?.method) {
    return { input }
  }
  const scenario = scenarioMap.get(input.scenarioId)
  if (!scenario) {
    return { input, error: "scenarioId is invalid" }
  }
  const prompt = input.prompt || ""
  return {
    input: {
      ...input,
      mcp: { method: scenario.method, params: scenario.buildParams(prompt) }
    }
  }
}

tasksRouter.use(requireAuth)

tasksRouter.get(
  "/",
  asyncHandler(async (req: AuthedRequest, res) => {
    const tasks = await listTasks(req.userId)
    res.json({ tasks })
  })
)

tasksRouter.get(
  "/:id",
  asyncHandler(async (req: AuthedRequest, res) => {
    const task = await getTaskById(req.params.id, req.userId)
    if (!task) {
      res.status(404).json({ error: "Task not found" })
      return
    }
    res.json({ task })
  })
)

tasksRouter.post(
  "/:id/retry",
  asyncHandler(async (req: AuthedRequest, res) => {
    const task = await retryTask(req.params.id, req.userId)
    if (!task) {
      res.status(404).json({ error: "Task not found" })
      return
    }
    res.status(200).json({ task })
  })
)

tasksRouter.post(
  "/",
  asyncHandler(async (req: AuthedRequest, res) => {
    const rawInput = req.body as TaskInput
    const { input, error } = applyScenarioToInput(rawInput)
    if (error) {
      res.status(400).json({ error })
      return
    }
    if (!input.title && !input.prompt && !input.mcp) {
      res.status(400).json({ error: "title or prompt or mcp is required" })
      return
    }
    if (input.mcp && !input.mcp.method) {
      res.status(400).json({ error: "mcp.method is required" })
      return
    }
    const task = await createTask(input, req.userId)
    res.status(201).json({ task })
  })
)
