import { useMemo, useState } from "react"

type Message = {
  id: string
  role: "user" | "assistant"
  content: string
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

export default function ChatPage() {
  const [conversations, setConversations] = useState<Conversation[]>(initialConversations)
  const [activeId, setActiveId] = useState<string>(initialConversations[0].id)
  const [input, setInput] = useState("")

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

  const handleSend = () => {
    if (!input.trim() || !activeConversation) {
      return
    }
    const userMessage: Message = {
      id: `m-${Date.now()}`,
      role: "user",
      content: input
    }
    const assistantMessage: Message = {
      id: `m-${Date.now()}-assistant`,
      role: "assistant",
      content: "已收到指令，待接入任务规划与执行。"
    }
    const next = conversations.map((item) =>
      item.id === activeId
        ? { ...item, messages: [...item.messages, userMessage, assistantMessage] }
        : item
    )
    setConversations(next)
    setInput("")
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
          <button type="button" className="primary" onClick={handleSend}>
            发送
          </button>
        </div>
      </div>
    </div>
  )
}
