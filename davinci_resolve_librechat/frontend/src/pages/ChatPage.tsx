import { useEffect, useMemo, useRef, useState } from "react"
import type { Task } from "../types"

type Message = {
  id: string
  role: "user" | "assistant"
  content: string
  taskId?: string
}

type Conversation = {
  id: string
  title: string
  messages: Message[]
}

const initialConversations: Conversation[] = [
  {
    id: "convo-1",
    title: "示例对话",
    messages: [
      { id: "m1", role: "assistant", content: "欢迎进入 DaVinci Resolve LibreChat。" }
    ]
  }
]

export default function ChatPage({
  onCreateTask,
  taskUpdate
}: {
  onCreateTask: (input: {
    prompt: string
    mcpMethod?: string
    mcpParams?: string
  }) => Promise<Task>
  taskUpdate: Task | null
}) {
  const [conversations, setConversations] = useState<Conversation[]>(initialConversations)
  const [activeId, setActiveId] = useState<string>(initialConversations[0].id)
  const [input, setInput] = useState("")
  const [mcpMethod, setMcpMethod] = useState("")
  const [mcpParams, setMcpParams] = useState("")
  const taskMetaRef = useRef<Record<string, { convoId: string; status?: string }>>({})

  const activeConversation = useMemo(
    () => conversations.find((item) => item.id === activeId),
    [conversations, activeId]
  )

  const handleNewChat = () => {
    const id = `convo-${Date.now()}`
    const next: Conversation = {
      id,
      title: "新对话",
      messages: [{ id: `m-${Date.now()}`, role: "assistant", content: "新对话已开始。" }]
    }
    setConversations((prev) => [next, ...prev])
    setActiveId(id)
  }

  const handleSend = async () => {
    const prompt = input.trim()
    if (!prompt || !activeConversation) {
      return
    }
    setInput("")
    const userMessage: Message = {
      id: `m-${Date.now()}`,
      role: "user",
      content: prompt
    }
    try {
      const task = await onCreateTask({
        prompt,
        mcpMethod: mcpMethod || undefined,
        mcpParams: mcpParams || undefined
      })
      taskMetaRef.current[task._id] = { convoId: activeId, status: task.status }
      const assistantMessage: Message = {
        id: `m-${Date.now()}-assistant`,
        role: "assistant",
        content: `任务已创建：${task.status}`,
        taskId: task._id
      }
      setConversations((prev) =>
        prev.map((item) =>
          item.id === activeId
            ? { ...item, messages: [...item.messages, userMessage, assistantMessage] }
            : item
        )
      )
    } catch (error) {
      const assistantMessage: Message = {
        id: `m-${Date.now()}-assistant`,
        role: "assistant",
        content: error instanceof Error ? error.message : "任务创建失败"
      }
      setConversations((prev) =>
        prev.map((item) =>
          item.id === activeId
            ? { ...item, messages: [...item.messages, userMessage, assistantMessage] }
            : item
        )
      )
    }
  }

  useEffect(() => {
    if (!taskUpdate) {
      return
    }
    const meta = taskMetaRef.current[taskUpdate._id]
    if (!meta) {
      return
    }
    if (meta.status === taskUpdate.status) {
      return
    }
    meta.status = taskUpdate.status
    const content =
      taskUpdate.status === "completed"
        ? `任务完成：${renderTaskResult(taskUpdate)}`
        : taskUpdate.status === "failed"
          ? `任务失败：${taskUpdate.error || "未知错误"}`
          : `任务状态更新：${taskUpdate.status}`
    const assistantMessage: Message = {
      id: `m-${Date.now()}-assistant`,
      role: "assistant",
      content,
      taskId: taskUpdate._id
    }
    setConversations((prev) =>
      prev.map((item) =>
        item.id === meta.convoId
          ? { ...item, messages: [...item.messages, assistantMessage] }
          : item
      )
    )
  }, [taskUpdate])

  const renderTaskResult = (task: Task) => {
    if (task.result === undefined) {
      return "无结果"
    }
    if (typeof task.result === "string") {
      return task.result
    }
    return JSON.stringify(task.result, null, 2)
  }

  return (
    <div className="chat-layout">
      <div className="chat-sidebar">
        <div className="chat-sidebar-header">
          <div>对话</div>
          <button type="button" className="ghost" onClick={handleNewChat}>
            新对话
          </button>
        </div>
        <div className="chat-convo-list">
          {conversations.map((item) => (
            <button
              key={item.id}
              type="button"
              className={item.id === activeId ? "chat-convo active" : "chat-convo"}
              onClick={() => setActiveId(item.id)}
            >
              {item.title}
            </button>
          ))}
        </div>
      </div>
      <div className="chat-panel">
        <div className="chat-messages">
          {activeConversation?.messages.map((msg) => (
            <div key={msg.id} className={`chat-message ${msg.role}`}>
              <div className="chat-bubble">{msg.content}</div>
            </div>
          ))}
        </div>
        <div className="chat-input">
          <textarea
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="输入剪辑需求或任务指令"
          />
          <div className="chat-toolbar">
            <input
              placeholder="MCP 方法"
              value={mcpMethod}
              onChange={(e) => setMcpMethod(e.target.value)}
            />
            <input
              placeholder="MCP 参数(JSON)"
              value={mcpParams}
              onChange={(e) => setMcpParams(e.target.value)}
            />
          </div>
          <button type="button" className="primary" onClick={handleSend}>
            发送
          </button>
        </div>
      </div>
    </div>
  )
}
