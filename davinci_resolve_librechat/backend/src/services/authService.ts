import bcrypt from "bcryptjs"
import jwt from "jsonwebtoken"
import { config } from "../config.js"
import { User } from "../models/User.js"

export type AuthUser = {
  id: string
  email: string
  name: string
  avatarUrl?: string
}

export async function registerUser(input: { email: string; password: string; name: string }) {
  const email = input.email.toLowerCase().trim()
  const existing = await User.findOne({ email })
  if (existing) {
    throw new Error("Email already exists")
  }
  const passwordHash = await bcrypt.hash(input.password, 10)
  const user = await User.create({ email, name: input.name, passwordHash })
  return buildAuthPayload(user)
}

export async function loginUser(input: { email: string; password: string }) {
  const email = input.email.toLowerCase().trim()
  const user = await User.findOne({ email })
  if (!user) {
    throw new Error("Invalid credentials")
  }
  const match = await bcrypt.compare(input.password, user.passwordHash)
  if (!match) {
    throw new Error("Invalid credentials")
  }
  return buildAuthPayload(user)
}

export async function getUserById(id: string) {
  const user = await User.findById(id)
  if (!user) {
    return null
  }
  return toAuthUser(user)
}

export async function updateUserProfile(
  id: string,
  input: { name?: string; avatarUrl?: string | null }
) {
  const update: { name?: string; avatarUrl?: string | null } = {}
  if (input.name) {
    update.name = input.name
  }
  if (input.avatarUrl !== undefined) {
    update.avatarUrl = input.avatarUrl || null
  }
  const user = await User.findByIdAndUpdate(id, update, { new: true })
  if (!user) {
    return null
  }
  return toAuthUser(user)
}

function buildAuthPayload(user: { _id: unknown; email: string; name: string; avatarUrl?: string }) {
  const authUser = toAuthUser(user)
  const token = jwt.sign({ sub: authUser.id }, config.jwtSecret, { expiresIn: "7d" })
  return { user: authUser, token }
}

function toAuthUser(user: { _id: unknown; email: string; name: string }) {
  return {
    id: String(user._id),
    email: user.email,
    name: user.name,
    avatarUrl: "avatarUrl" in user ? (user as { avatarUrl?: string }).avatarUrl : undefined
  }
}
