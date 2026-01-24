import { useMemo, useState } from "react"
import type { Conversation } from "../types"
import { promptToken, scenarios } from "../scenarios"

export default function ChatPage({
  conversations,
  activeId,
  onSend
}: {
  conversations: Conversation[]
  activeId: string
  onSend: (input: {
    prompt: string
    scenarioId?: string
    mcpMethod?: string
    mcpParams?: string
  }) => Promise<void>
}) {
  const [input, setInput] = useState("")
  const [mcpMethod, setMcpMethod] = useState("")
  const [mcpParams, setMcpParams] = useState("")
  const [scenarioId, setScenarioId] = useState("")

  const activeConversation = useMemo(
    () => conversations.find((item) => item.id === activeId),
    [conversations, activeId]
  )

  const selectedScenario = useMemo(
    () => scenarios.find((item) => item.id === scenarioId),
    [scenarioId]
  )

  const handleScenarioChange = (id: string) => {
    setScenarioId(id)
    const scenario = scenarios.find((item) => item.id === id)
    if (!scenario) {
      return
    }
    setMcpMethod(scenario.method)
    setMcpParams(JSON.stringify(scenario.buildParams(promptToken), null, 2))
  }

  const handleSend = async () => {
    const prompt = input.trim()
    if (!prompt) {
      return
    }
    setInput("")
    let method = mcpMethod
    let params = mcpParams
    if (selectedScenario) {
      method = method || selectedScenario.method
      const baseParams =
        params || JSON.stringify(selectedScenario.buildParams(promptToken), null, 2)
      params = baseParams.replaceAll(promptToken, prompt)
    }
    await onSend({
      prompt,
      scenarioId: scenarioId || undefined,
      mcpMethod: method || undefined,
      mcpParams: params || undefined
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
          <select
            value={scenarioId}
            onChange={(e) => handleScenarioChange(e.target.value)}
          >
            <option value="">场景模式</option>
            {scenarios.map((item) => (
              <option key={item.id} value={item.id}>
                {item.name}
              </option>
            ))}
          </select>
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
