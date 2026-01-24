import { useMemo, useState } from "react"
import type { Conversation } from "../types"

export default function ChatPage({
  conversations,
  activeId,
  onSend
}: {
  conversations: Conversation[]
  activeId: string
  onSend: (input: { prompt: string; mcpMethod?: string; mcpParams?: string }) => Promise<void>
}) {
  const [input, setInput] = useState("")
  const [mcpMethod, setMcpMethod] = useState("")
  const [mcpParams, setMcpParams] = useState("")

  const activeConversation = useMemo(
    () => conversations.find((item) => item.id === activeId),
    [conversations, activeId]
  )

  const handleSend = async () => {
    const prompt = input.trim()
    if (!prompt) {
      return
    }
    setInput("")
    await onSend({
      prompt,
      mcpMethod: mcpMethod || undefined,
      mcpParams: mcpParams || undefined
    })
  }

  return (
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
  )
}
