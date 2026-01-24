import type { Task, TaskInput, User } from "./types"

const tokenKey = "davinci_resolve_librechat_token"

export function setAuthToken(token: string | null) {
  if (token) {
    localStorage.setItem(tokenKey, token)
  } else {
    localStorage.removeItem(tokenKey)
  }
}

export function getAuthToken() {
  return localStorage.getItem(tokenKey)
}

function authHeaders(): Record<string, string> {
  const token = getAuthToken()
  if (!token) {
    return {}
  }
  return { Authorization: `Bearer ${token}` }
}

export async function listTasks(baseUrl: string) {
  try {
    const response = await fetch(`${baseUrl}/tasks`, { headers: authHeaders() })
    const payload = (await response.json()) as { tasks: Task[] }
    return payload.tasks || []
  } catch {
    return []
  }
}

export async function createTask(baseUrl: string, input: TaskInput) {
  const response = await fetch(`${baseUrl}/tasks`, {
    method: "POST",
    headers: { "Content-Type": "application/json", ...authHeaders() },
    body: JSON.stringify(input)
  })
  const payload = (await response.json()) as { task: Task }
  return payload.task
}

export async function retryTask(baseUrl: string, id: string) {
  const response = await fetch(`${baseUrl}/tasks/${id}/retry`, {
    method: "POST",
    headers: { "Content-Type": "application/json", ...authHeaders() }
  })
  const payload = (await response.json()) as { task: Task }
  return payload.task
}

export async function registerUser(baseUrl: string, input: { email: string; password: string; name: string }) {
  const response = await fetch(`${baseUrl}/auth/register`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(input)
  })
  const payload = (await response.json()) as { user: User; token: string; error?: string }
  if (!response.ok) {
    throw new Error(payload.error || "Register failed")
  }
  return payload
}

export async function loginUser(baseUrl: string, input: { email: string; password: string }) {
  const response = await fetch(`${baseUrl}/auth/login`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(input)
  })
  const payload = (await response.json()) as { user: User; token: string; error?: string }
  if (!response.ok) {
    throw new Error(payload.error || "Login failed")
  }
  return payload
}

export async function fetchMe(baseUrl: string) {
  const response = await fetch(`${baseUrl}/auth/me`, {
    headers: authHeaders()
  })
  const payload = (await response.json()) as { user?: User; error?: string }
  if (!response.ok) {
    throw new Error(payload.error || "Unauthorized")
  }
  return payload.user
}
