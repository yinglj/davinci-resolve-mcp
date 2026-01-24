import { useMemo, useState } from "react"
import type { Conversation, Scenario, TaskAssetInput } from "../types"

export default function ChatPage({
  conversations,
  activeId,
  scenarios,
  onSend
}: {
  conversations: Conversation[]
  activeId: string
  scenarios: Scenario[]
  onSend: (input: {
    prompt: string
    scenarioId?: string
    assets?: TaskAssetInput
  }) => Promise<void>
}) {
  const [input, setInput] = useState("")
  const [scenarioId, setScenarioId] = useState("")
  const [videoUrls, setVideoUrls] = useState("")
  const [imageUrls, setImageUrls] = useState("")
  const [audioUrls, setAudioUrls] = useState("")

  const activeConversation = useMemo(
    () => conversations.find((item) => item.id === activeId),
    [conversations, activeId]
  )

  const handleScenarioChange = (id: string) => {
    setScenarioId(id)
  }

  const parseUrls = (value: string) =>
    value
      .split(/[\n,]+/g)
      .map((item) => item.trim())
      .filter(Boolean)

  const handleSend = async () => {
    const prompt = input.trim()
    if (!prompt) {
      return
    }
    setInput("")
    const videos = parseUrls(videoUrls)
    const images = parseUrls(imageUrls)
    const audios = parseUrls(audioUrls)
    await onSend({
      prompt,
      scenarioId: scenarioId || undefined,
      assets: {
        videos: videos.length ? videos : undefined,
        images: images.length ? images : undefined,
        audios: audios.length ? audios : undefined
      }
    })
    setScenarioId("")
    setVideoUrls("")
    setImageUrls("")
    setAudioUrls("")
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
            placeholder="视频素材URL（逗号或换行分隔）"
            value={videoUrls}
            onChange={(e) => setVideoUrls(e.target.value)}
          />
          <input
            placeholder="图片素材URL（逗号或换行分隔）"
            value={imageUrls}
            onChange={(e) => setImageUrls(e.target.value)}
          />
          <input
            placeholder="音乐素材URL（逗号或换行分隔）"
            value={audioUrls}
            onChange={(e) => setAudioUrls(e.target.value)}
          />
        </div>
        <button type="button" className="primary" onClick={handleSend}>
          发送
        </button>
      </div>
    </div>
  )
}
