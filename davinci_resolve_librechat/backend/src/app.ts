import express, { Request, Response } from "express"
import fs from "fs"
import path from "path"
import cors from "cors"
import { config } from "./config.js"
import { tasksRouter } from "./routes/tasks.js"
import { authRouter } from "./routes/auth.js"
import { callMcp } from "./services/mcpClient.js"
import { assetsRouter } from "./routes/assets.js"
import { planningRouter } from "./routes/planning.js"

export function createApp() {
  const app = express()
  fs.mkdirSync(config.uploadDir, { recursive: true })
  app.use(cors({ origin: config.corsOrigin, credentials: true }))
  app.use(express.json({ limit: "10mb" }))
  app.use(`/${config.uploadDir}`, express.static(path.resolve(config.uploadDir)))

  app.get("/health", (_req: Request, res: Response) => {
    res.json({ status: "ok" })
  })

  app.post("/mcp/call", async (req: Request, res: Response) => {
    const { method, params } = req.body || {}
    if (!method) {
      res.status(400).json({ error: "method is required" })
      return
    }
    try {
      const result = await callMcp({ method, params })
      res.json({ result })
    } catch (error) {
      res.status(500).json({ error: error instanceof Error ? error.message : "MCP error" })
    }
  })

  app.get("/mcp/health", async (_req: Request, res: Response) => {
    try {
      const result = await callMcp({ method: config.mcpHealthMethod })
      res.json({ status: "ok", method: config.mcpHealthMethod, result })
    } catch (error) {
      res.status(502).json({
        status: "error",
        method: config.mcpHealthMethod,
        error: error instanceof Error ? error.message : "MCP error"
      })
    }
  })

  app.get("/mcp/tools", async (_req: Request, res: Response) => {
    try {
      const result = await callMcp({ method: "list_tools" })
      res.json({ tools: result })
    } catch (error) {
      res.status(502).json({ error: error instanceof Error ? error.message : "MCP error" })
    }
  })

  app.use("/tasks", tasksRouter)
  app.use("/assets", assetsRouter)
  app.use("/planning", planningRouter)
  app.use("/auth", authRouter)
  return app
}
