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
  name: string
  description: string
  method: string
  version: number
  requiresPrompt: boolean
  requiredAssets: {
    videos?: boolean
    images?: boolean
    audios?: boolean
  }
  buildParams: (prompt: string) => Record<string, unknown>
}

const scenarioDefinitions: ScenarioDefinition[] = [
  {
    id: "color-style",
    name: "自动调色",
    description: "按风格应用基础调色",
    method: "color_apply_style",
    version: 1,
    requiresPrompt: true,
    requiredAssets: { videos: true },
    buildParams: (prompt) => ({ style: "cinematic", prompt })
  },
  {
    id: "audio-normalize",
    name: "音频标准化",
    description: "规范响度并清理音轨",
    method: "audio_normalize_loudness",
    version: 1,
    requiresPrompt: false,
    requiredAssets: { audios: true },
    buildParams: (prompt) => ({ targetLufs: -14, prompt })
  },
  {
    id: "fusion-transition",
    name: "转场生成",
    description: "为片段添加转场效果",
    method: "fusion_add_transition",
    version: 1,
    requiresPrompt: true,
    requiredAssets: { videos: true },
    buildParams: (prompt) => ({ transition: "smooth", prompt })
  }
]

const scenarioMap = new Map(scenarioDefinitions.map((item) => [item.id, item]))

const hasAssets = (assets: TaskInput["assets"], key: "videos" | "images" | "audios") =>
  Boolean(assets?.[key]?.length)

const validateScenarioAssets = (scenario: ScenarioDefinition, assets: TaskInput["assets"]) => {
  const required = scenario.requiredAssets
  if (required.videos && !hasAssets(assets, "videos")) {
    return "videos are required for scenario"
  }
  if (required.images && !hasAssets(assets, "images")) {
    return "images are required for scenario"
  }
  if (required.audios && !hasAssets(assets, "audios")) {
    return "audios are required for scenario"
  }
  return null
}

const applyScenarioToInput = (input: TaskInput) => {
  if (input.scenarioId && input.mcp?.method) {
    return { input, error: "mcp is not allowed with scenarioId" }
  }
  if (input.scenarioId && input.scenarioVersion !== undefined) {
    return { input, error: "scenarioVersion is not allowed with scenarioId" }
  }
  if (!input.scenarioId || input.mcp?.method) {
    return { input }
  }
  const scenario = scenarioMap.get(input.scenarioId)
  if (!scenario) {
    return { input, error: "scenarioId is invalid" }
  }
  const prompt = input.prompt || ""
  if (scenario.requiresPrompt && !prompt) {
    return { input, error: "prompt is required for scenario" }
  }
  const assetError = validateScenarioAssets(scenario, input.assets)
  if (assetError) {
    return { input, error: assetError }
  }
  return {
    input: {
      ...input,
      scenarioVersion: scenario.version,
      mcp: { method: scenario.method, params: scenario.buildParams(prompt) }
    }
  }
}

tasksRouter.use(requireAuth)

tasksRouter.get(
  "/scenarios",
  asyncHandler(async (_req: AuthedRequest, res) => {
    res.json({
      scenarios: scenarioDefinitions.map((scenario) => ({
        id: scenario.id,
        name: scenario.name,
        description: scenario.description,
        version: scenario.version,
        requiresPrompt: scenario.requiresPrompt,
        requiredAssets: scenario.requiredAssets
      }))
    })
  })
)

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
