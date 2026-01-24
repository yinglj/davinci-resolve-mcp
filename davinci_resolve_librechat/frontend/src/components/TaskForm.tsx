import { useState, type ChangeEvent, type FormEvent } from "react"
import type { Scenario, TaskAssetInput } from "../types"

export default function TaskForm({
  scenarios,
  onSubmit
}: {
  scenarios: Scenario[]
  onSubmit: (input: {
    title?: string
    prompt?: string
    scenarioId?: string
    assets?: TaskAssetInput
  }) => Promise<void> | void
}) {
  const [title, setTitle] = useState("")
  const [prompt, setPrompt] = useState("")
  const [scenarioId, setScenarioId] = useState("")
  const [videoUrls, setVideoUrls] = useState("")
  const [imageUrls, setImageUrls] = useState("")
  const [audioUrls, setAudioUrls] = useState("")

  const parseUrls = (value: string) =>
    value
      .split(/[\n,]+/g)
      .map((item) => item.trim())
      .filter(Boolean)

  const handleSubmit = async (event: FormEvent) => {
    event.preventDefault()
    const videos = parseUrls(videoUrls)
    const images = parseUrls(imageUrls)
    const audios = parseUrls(audioUrls)
    await onSubmit({
      title: title || undefined,
      prompt: prompt || undefined,
      scenarioId: scenarioId || undefined,
      assets: {
        videos: videos.length ? videos : undefined,
        images: images.length ? images : undefined,
        audios: audios.length ? audios : undefined
      }
    })
    setTitle("")
    setPrompt("")
    setScenarioId("")
    setVideoUrls("")
    setImageUrls("")
    setAudioUrls("")
  }

  return (
    <form className="card" onSubmit={handleSubmit}>
      <div className="card-title">创建任务</div>
      <div className="form-grid">
        <label className="field">
          <span>标题</span>
          <input
            value={title}
            onChange={(e: ChangeEvent<HTMLInputElement>) => setTitle(e.target.value)}
          />
        </label>
        <label className="field">
          <span>描述</span>
          <textarea
            value={prompt}
            onChange={(e: ChangeEvent<HTMLTextAreaElement>) => setPrompt(e.target.value)}
          />
        </label>
        <label className="field">
          <span>场景模式</span>
          <select value={scenarioId} onChange={(e) => setScenarioId(e.target.value)}>
            <option value="">请选择场景</option>
            {scenarios.map((scenario) => (
              <option key={scenario.id} value={scenario.id}>
                {scenario.name}
              </option>
            ))}
          </select>
        </label>
        <label className="field">
          <span>视频素材URL</span>
          <textarea
            value={videoUrls}
            onChange={(e: ChangeEvent<HTMLTextAreaElement>) => setVideoUrls(e.target.value)}
            placeholder="支持多条，逗号或换行分隔"
          />
        </label>
        <label className="field">
          <span>图片素材URL</span>
          <textarea
            value={imageUrls}
            onChange={(e: ChangeEvent<HTMLTextAreaElement>) => setImageUrls(e.target.value)}
            placeholder="支持多条，逗号或换行分隔"
          />
        </label>
        <label className="field">
          <span>音乐素材URL</span>
          <textarea
            value={audioUrls}
            onChange={(e: ChangeEvent<HTMLTextAreaElement>) => setAudioUrls(e.target.value)}
            placeholder="支持多条，逗号或换行分隔"
          />
        </label>
      </div>
      <button type="submit" className="primary">
        提交
      </button>
    </form>
  )
}
