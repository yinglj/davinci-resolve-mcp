import jwt from "jsonwebtoken"
import type { Request, Response, NextFunction } from "express"
import { config } from "../config.js"

export type AuthedRequest = Request & { userId?: string }

export function requireAuth(req: AuthedRequest, res: Response, next: NextFunction) {
  const header = req.headers.authorization
  if (!header) {
    res.status(401).json({ error: "Unauthorized" })
    return
  }
  const [, token] = header.split(" ")
  if (!token) {
    res.status(401).json({ error: "Unauthorized" })
    return
  }
  try {
    const payload = jwt.verify(token, config.jwtSecret) as { sub?: string }
    if (!payload.sub) {
      res.status(401).json({ error: "Unauthorized" })
      return
    }
    req.userId = payload.sub
    next()
  } catch {
    res.status(401).json({ error: "Unauthorized" })
  }
}
