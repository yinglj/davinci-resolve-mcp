import { Router } from "express"
import { loginUser, registerUser, getUserById, updateUserProfile } from "../services/authService.js"
import { requireAuth, type AuthedRequest } from "../middleware/auth.js"

export const authRouter = Router()

authRouter.post("/register", async (req, res) => {
  const { email, password, name } = req.body || {}
  if (!email || !password || !name) {
    res.status(400).json({ error: "email, password and name are required" })
    return
  }
  try {
    const payload = await registerUser({ email, password, name })
    res.status(201).json(payload)
  } catch (error) {
    res.status(400).json({ error: error instanceof Error ? error.message : "Register failed" })
  }
})

authRouter.post("/login", async (req, res) => {
  const { email, password } = req.body || {}
  if (!email || !password) {
    res.status(400).json({ error: "email and password are required" })
    return
  }
  try {
    const payload = await loginUser({ email, password })
    res.json(payload)
  } catch (error) {
    res.status(400).json({ error: error instanceof Error ? error.message : "Login failed" })
  }
})

authRouter.get("/me", requireAuth, async (req: AuthedRequest, res) => {
  if (!req.userId) {
    res.status(401).json({ error: "Unauthorized" })
    return
  }
  const user = await getUserById(req.userId)
  if (!user) {
    res.status(404).json({ error: "User not found" })
    return
  }
  res.json({ user })
})

authRouter.put("/profile", requireAuth, async (req: AuthedRequest, res) => {
  if (!req.userId) {
    res.status(401).json({ error: "Unauthorized" })
    return
  }
  const { name, avatarUrl } = req.body || {}
  if (!name && avatarUrl === undefined) {
    res.status(400).json({ error: "name or avatarUrl is required" })
    return
  }
  const user = await updateUserProfile(req.userId, { name, avatarUrl })
  if (!user) {
    res.status(404).json({ error: "User not found" })
    return
  }
  res.json({ user })
})
