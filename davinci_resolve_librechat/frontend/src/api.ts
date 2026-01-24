import type { Task, TaskInput } from "./types"

export async function listTasks(baseUrl: string) {
  try {
    const response = await fetch(`${baseUrl}/tasks`)
    const payload = (await response.json()) as { tasks: Task[] }
    return payload.tasks || []
  } catch {
    return []
  }
}

export async function createTask(baseUrl: string, input: TaskInput) {
  const response = await fetch(`${baseUrl}/tasks`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(input)
  })
  const payload = (await response.json()) as { task: Task }
  return payload.task
}
