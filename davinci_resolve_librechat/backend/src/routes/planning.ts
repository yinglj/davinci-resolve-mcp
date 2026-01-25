import { Router, Request, Response } from "express"
import { callMcp } from "../services/mcpClient.js"
import { requireAuth, type AuthedRequest } from "../middleware/auth.js"

type PlanStep = {
  name: string
  tool?: string
}

const asyncHandler =
  (fn: (req: Request, res: Response) => Promise<void>) =>
  (req: Request, res: Response) => {
    fn(req, res).catch((error) => {
      res.status(500).json({ error: error instanceof Error ? error.message : "Server error" })
    })
  }

const buildRuleBasedPlan = (input: {
  scenarioId?: string
  prompt?: string
  hasVideo?: boolean
  hasImage?: boolean
  hasAudio?: boolean
  toolNames: string[]
}) => {
  const steps: PlanStep[] = []
  if (input.hasVideo) {
    steps.push({ name: "解析视频结构", tool: input.toolNames.find((t) => t.includes("video")) })
  }
  if (input.hasImage) {
    steps.push({ name: "读取图片素材", tool: input.toolNames.find((t) => t.includes("image")) })
  }
  if (input.hasAudio) {
    steps.push({ name: "分析音频轨道", tool: input.toolNames.find((t) => t.includes("audio")) })
  }
  if (input.scenarioId === "color-style") {
    steps.push({ name: "风格调色应用", tool: input.toolNames.find((t) => t.includes("color")) })
  }
  if (input.scenarioId === "audio-normalize") {
    steps.push({ name: "音量标准化", tool: input.toolNames.find((t) => t.includes("audio")) })
  }
  if (input.scenarioId === "fusion-transition") {
    steps.push({ name: "生成转场序列", tool: input.toolNames.find((t) => t.includes("transition")) })
  }
  if (input.prompt) {
    steps.push({ name: "根据需求合成输出", tool: input.toolNames.find((t) => t.includes("render")) })
  }
  return steps.length ? steps : [{ name: "生成基础剪辑方案" }]
}

export const planningRouter = Router()

planningRouter.use(requireAuth)

planningRouter.post(
  "/plan",
  asyncHandler(async (req: AuthedRequest, res) => {
    const { scenarioId, prompt, assets } = (req.body || {}) as {
      scenarioId?: string
      prompt?: string
      assets?: {
        videos?: { url: string }[] | string[]
        images?: { url: string }[] | string[]
        audios?: { url: string }[] | string[]
      }
    }
    let tools: unknown = []
    try {
      tools = await callMcp({ method: "list_tools" })
    } catch {
      tools = []
    }
    const toolNames =
      Array.isArray((tools as { name?: string }[])) && (tools as { name?: string }[]).length
        ? (tools as { name?: string }[]).map((tool) => tool.name || "").filter(Boolean)
        : []
    const hasVideo = Boolean(assets?.videos && assets.videos.length)
    const hasImage = Boolean(assets?.images && assets.images.length)
    const hasAudio = Boolean(assets?.audios && assets.audios.length)
    const steps = buildRuleBasedPlan({
      scenarioId,
      prompt,
      hasVideo,
      hasImage,
      hasAudio,
      toolNames
    })
    res.json({
      plan: {
        scenarioId,
        steps,
        tools: toolNames
      }
    })
  })
)
