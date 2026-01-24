import { useEffect, useMemo, useState } from "react"
import { BrowserRouter, Navigate, Route, Routes, useLocation } from "react-router-dom"
import { io } from "socket.io-client"
import { createTask, listTasks, retryTask, fetchMe, getAuthToken, setAuthToken } from "./api"
import type { Task, User } from "./types"
import Sidebar from "./components/layout/Sidebar"
import Topbar from "./components/layout/Topbar"
import AuthPage from "./pages/AuthPage"
import ChatPage from "./pages/ChatPage"
import TasksPage from "./pages/TasksPage"
import ProfilePage from "./pages/ProfilePage"
import SettingsPage from "./pages/SettingsPage"

const apiBaseUrl = import.meta.env.VITE_API_BASE_URL || "http://localhost:3001"

function MainLayout({ user, onLogout }: { user: User; onLogout: () => void }) {
  const location = useLocation()
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

  const handleRetry = async (id: string) => {
    await retryTask(apiBaseUrl, id)
  }

  const titleMap: Record<string, string> = {
    "/chats": "对话",
    "/tasks": "任务",
    "/profile": "个人信息",
    "/settings": "设置"
  }
  const title = titleMap[location.pathname] || "对话"

  return (
    <div className="layout">
      <Sidebar />
      <div className="layout-main">
        <Topbar title={title} user={user} onLogout={onLogout} />
        <div className="layout-content">
          <Routes>
            <Route path="/chats" element={<ChatPage />} />
            <Route
              path="/tasks"
              element={<TasksPage tasks={tasks} onCreate={handleCreate} onRetry={handleRetry} />}
            />
            <Route path="/profile" element={<ProfilePage user={user} />} />
            <Route path="/settings" element={<SettingsPage />} />
            <Route path="*" element={<Navigate to="/chats" replace />} />
          </Routes>
        </div>
      </div>
    </div>
  )
}

function AppRoutes() {
  const [user, setUser] = useState<User | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const token = getAuthToken()
    if (!token) {
      setLoading(false)
      return
    }
    fetchMe(apiBaseUrl)
      .then((result: User | undefined | null) => {
        if (result) {
          setUser(result)
        }
      })
      .catch(() => {
        setAuthToken(null)
      })
      .finally(() => setLoading(false))
  }, [])

  const handleLogout = () => {
    setAuthToken(null)
    setUser(null)
  }

  if (loading) {
    return <div className="page-loading">加载中</div>
  }

  return (
    <Routes>
      <Route
        path="/login"
        element={<AuthPage mode="login" apiBaseUrl={apiBaseUrl} onAuth={setUser} />}
      />
      <Route
        path="/register"
        element={<AuthPage mode="register" apiBaseUrl={apiBaseUrl} onAuth={setUser} />}
      />
      <Route
        path="/*"
        element={user ? <MainLayout user={user} onLogout={handleLogout} /> : <Navigate to="/login" replace />}
      />
    </Routes>
  )
}

export default function App() {
  return (
    <BrowserRouter>
      <AppRoutes />
    </BrowserRouter>
  )
}
