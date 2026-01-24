import { useEffect, useMemo, useState } from "react"
import { io } from "socket.io-client"
import { createTask, listTasks } from "./api"
import type { Task } from "./types"
import TaskForm from "./components/TaskForm"
import TaskList from "./components/TaskList"

const apiBaseUrl = import.meta.env.VITE_API_BASE_URL || "http://localhost:3001"

export default function App() {
  const [tasks, setTasks] = useState<Task[]>([])

  useEffect(() => {
    listTasks(apiBaseUrl).then((data: Task[]) => setTasks(data))
  }, [apiBaseUrl])

  const socket = useMemo(() => io(apiBaseUrl), [apiBaseUrl])

  useEffect(() => {
    socket.on("task:update", (task: Task) => {
      setTasks((prev: Task[]) => {
        const existing = prev.find((item) => item._id === task._id)
        if (existing) {
          return prev.map((item) => (item._id === task._id ? task : item))
        }
        return [task, ...prev]
      })
    })
    return () => {
      socket.disconnect()
    }
  }, [socket])

  const handleCreate = async (input: {
    title?: string
    prompt?: string
    mcpMethod?: string
    mcpParams?: string
  }) => {
    let params: unknown = undefined
    if (input.mcpParams) {
      try {
        params = JSON.parse(input.mcpParams)
      } catch {
        params = { raw: input.mcpParams }
      }
    }
    await createTask(apiBaseUrl, {
      title: input.title,
      prompt: input.prompt,
      mcp: input.mcpMethod ? { method: input.mcpMethod, params } : undefined
    })
  }

  return (
    <div className="app">
      <header className="app-header">
        <div className="app-title">DaVinci Resolve LibreChat</div>
        <div className="app-subtitle">P0 任务入口</div>
      </header>
      <main className="app-main">
        <TaskForm onSubmit={handleCreate} />
        <TaskList tasks={tasks} />
      </main>
    </div>
  )
}
