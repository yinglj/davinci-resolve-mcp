import express, { Request, Response } from "express"
import cors from "cors"
import { config } from "./config.js"
import { tasksRouter } from "./routes/tasks.js"
import { authRouter } from "./routes/auth.js"
import { callMcp } from "./services/mcpClient.js"

export function createApp() {
  const app = express()
  app.use(cors({ origin: config.corsOrigin, credentials: true }))
  app.use(express.json({ limit: "10mb" }))

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

  app.use("/tasks", tasksRouter)
  app.use("/auth", authRouter)
  return app
}
