import { useEffect, useMemo, useRef, useState } from "react"
import { BrowserRouter, Navigate, Route, Routes, useLocation } from "react-router-dom"
import { io } from "socket.io-client"
import {
  createTask,
  listTasks,
  listScenarios,
  retryTask,
  fetchMe,
  getAuthToken,
  setAuthToken,
  updateProfile
} from "./api"
import type { Conversation, Scenario, Task, TaskAssetInput, TaskStatus, User } from "./types"
import Sidebar from "./components/layout/Sidebar"
import Topbar from "./components/layout/Topbar"
import Rightbar from "./components/layout/Rightbar"
import AuthPage from "./pages/AuthPage"
import ChatPage from "./pages/ChatPage"
import TasksPage from "./pages/TasksPage"
import ProfilePage from "./pages/ProfilePage"
import SettingsPage from "./pages/SettingsPage"

const apiBaseUrl = import.meta.env.VITE_API_BASE_URL || "http://localhost:3001"

function MainLayout({
  user,
  onLogout,
  onUserUpdate
}: {
  user: User
  onLogout: () => void
  onUserUpdate: (user: User) => void
}) {
  const location = useLocation()
  const [tasks, setTasks] = useState<Task[]>([])
  const [scenarios, setScenarios] = useState<Scenario[]>([])
  const [conversations, setConversations] = useState<Conversation[]>([
    {
      id: "convo-1",
      title: "示例对话",
      messages: [
        { id: "m1", role: "assistant", content: "欢迎进入 DaVinci Resolve LibreChat。" }
      ]
    }
  ])
  const [activeConversationId, setActiveConversationId] = useState<string>("convo-1")
  const taskConversationMap = useRef<Record<string, { convoId: string; status?: TaskStatus }>>(
    {}
  )

  useEffect(() => {
    listTasks(apiBaseUrl).then((data: Task[]) => setTasks(data))
  }, [apiBaseUrl])

  useEffect(() => {
    listScenarios(apiBaseUrl).then((data: Scenario[]) => setScenarios(data))
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
      handleTaskUpdate(task)
    })
    return () => {
      socket.disconnect()
    }
  }, [socket])

  const handleCreate = async (input: {
    title?: string
    prompt?: string
    scenarioId?: string
    assets?: TaskAssetInput
  }) => {
    await createTask(apiBaseUrl, {
      title: input.title,
      prompt: input.prompt,
      scenarioId: input.scenarioId,
      assets: input.assets
    })
  }

  const handleRetry = async (id: string) => {
    await retryTask(apiBaseUrl, id)
  }

  const handleChatTaskCreate = async (input: {
    prompt: string
    scenarioId?: string
    assets?: TaskAssetInput
  }) => {
    const task = await createTask(apiBaseUrl, {
      title: input.prompt.slice(0, 24),
      prompt: input.prompt,
      scenarioId: input.scenarioId,
      assets: input.assets
    })
    return task
  }

  const appendMessage = (convoId: string, message: Conversation["messages"][number]) => {
    setConversations((prev) =>
      prev.map((item) =>
        item.id === convoId ? { ...item, messages: [...item.messages, message] } : item
      )
    )
  }

  const handleNewConversation = () => {
    const id = `convo-${Date.now()}`
    const next: Conversation = {
      id,
      title: "新对话",
      messages: [{ id: `m-${Date.now()}`, role: "assistant", content: "新对话已开始。" }]
    }
    setConversations((prev) => [next, ...prev])
    setActiveConversationId(id)
  }

  const handleSendChat = async (input: {
    prompt: string
    scenarioId?: string
    assets?: TaskAssetInput
  }) => {
    const convoId = activeConversationId
    const userMessage = {
      id: `m-${Date.now()}`,
      role: "user" as const,
      content: input.prompt
    }
    appendMessage(convoId, userMessage)
    try {
      const task = await handleChatTaskCreate(input)
      taskConversationMap.current[task._id] = { convoId, status: task.status }
      appendMessage(convoId, {
        id: `m-${Date.now()}-assistant`,
        role: "assistant",
        content: `任务已创建：${task.status}`,
        taskId: task._id
      })
    } catch (error) {
      appendMessage(convoId, {
        id: `m-${Date.now()}-assistant`,
        role: "assistant",
        content: error instanceof Error ? error.message : "任务创建失败"
      })
    }
  }

  const renderTaskResult = (task: Task) => {
    if (task.result === undefined) {
      return "无结果"
    }
    if (typeof task.result === "string") {
      return task.result
    }
    return JSON.stringify(task.result, null, 2)
  }

  const handleTaskUpdate = (task: Task) => {
    const meta = taskConversationMap.current[task._id]
    if (!meta || meta.status === task.status) {
      return
    }
    meta.status = task.status
    const content =
      task.status === "completed"
        ? `任务完成：${renderTaskResult(task)}`
        : task.status === "failed"
          ? `任务失败：${task.error || "未知错误"}`
          : `任务状态更新：${task.status}`
    appendMessage(meta.convoId, {
      id: `m-${Date.now()}-assistant`,
      role: "assistant",
      content,
      taskId: task._id
    })
  }

  const handleProfileUpdate = async (input: { name?: string; avatarUrl?: string | null }) => {
    const updated = await updateProfile(apiBaseUrl, input)
    if (updated) {
      onUserUpdate(updated)
    }
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
      <Sidebar
        conversations={location.pathname === "/chats" ? conversations : undefined}
        activeConversationId={activeConversationId}
        onSelectConversation={location.pathname === "/chats" ? setActiveConversationId : undefined}
        onNewConversation={location.pathname === "/chats" ? handleNewConversation : undefined}
      />
      <div className="layout-main">
        <Topbar title={title} />
        <div className="layout-body">
          <div className="layout-content">
            <Routes>
              <Route
                path="/chats"
                element={
                  <ChatPage
                    conversations={conversations}
                    activeId={activeConversationId}
                    scenarios={scenarios}
                    onSend={handleSendChat}
                  />
                }
              />
              <Route
                path="/tasks"
                element={
                  <TasksPage
                    tasks={tasks}
                    scenarios={scenarios}
                    onCreate={handleCreate}
                    onRetry={handleRetry}
                  />
                }
              />
              <Route
                path="/profile"
                element={<ProfilePage user={user} onUpdate={handleProfileUpdate} />}
              />
              <Route path="/settings" element={<SettingsPage />} />
              <Route path="*" element={<Navigate to="/chats" replace />} />
            </Routes>
          </div>
          <Rightbar tasks={tasks} user={user} onLogout={onLogout} />
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
        element={
          user ? (
            <MainLayout user={user} onLogout={handleLogout} onUserUpdate={setUser} />
          ) : (
            <Navigate to="/login" replace />
          )
        }
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
