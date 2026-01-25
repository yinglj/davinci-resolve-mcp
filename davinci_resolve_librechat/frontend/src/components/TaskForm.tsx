import { useState, type ChangeEvent, type FormEvent } from "react"
import { uploadAssets } from "../api"
import type { Scenario, TaskAssetInput } from "../types"

export default function TaskForm({
  scenarios,
  apiBaseUrl,
  onSubmit
}: {
  scenarios: Scenario[]
  apiBaseUrl: string
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
  const [videoFiles, setVideoFiles] = useState<File[]>([])
  const [imageFiles, setImageFiles] = useState<File[]>([])
  const [audioFiles, setAudioFiles] = useState<File[]>([])
  const [submitting, setSubmitting] = useState(false)
  const [error, setError] = useState("")

  const parseUrls = (value: string) =>
    value
      .split(/[\n,]+/g)
      .map((item) => item.trim())
      .filter(Boolean)

  const handleSubmit = async (event: FormEvent) => {
    event.preventDefault()
    setSubmitting(true)
    setError("")
    const videos = parseUrls(videoUrls)
    const images = parseUrls(imageUrls)
    const audios = parseUrls(audioUrls)
    try {
      let uploaded: TaskAssetInput | undefined = undefined
      if (videoFiles.length || imageFiles.length || audioFiles.length) {
        uploaded = await uploadAssets(apiBaseUrl, {
          videos: videoFiles,
          images: imageFiles,
          audios: audioFiles
        })
      }
      const mergeList = (base: string[], extra?: string[]) => {
        const combined = [...base, ...(extra || [])]
        return combined.length ? combined : undefined
      }
      await onSubmit({
        title: title || undefined,
        prompt: prompt || undefined,
        scenarioId: scenarioId || undefined,
        assets: {
          videos: mergeList(videos, uploaded?.videos),
          images: mergeList(images, uploaded?.images),
          audios: mergeList(audios, uploaded?.audios)
        }
      })
      setTitle("")
      setPrompt("")
      setScenarioId("")
      setVideoUrls("")
      setImageUrls("")
      setAudioUrls("")
      setVideoFiles([])
      setImageFiles([])
      setAudioFiles([])
    } catch (err) {
      setError(err instanceof Error ? err.message : "素材上传失败")
    } finally {
      setSubmitting(false)
    }
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
          <span>上传视频素材</span>
          <input
            type="file"
            accept="video/*"
            multiple
            onChange={(e: ChangeEvent<HTMLInputElement>) =>
              setVideoFiles(e.target.files ? Array.from(e.target.files) : [])
            }
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
          <span>上传图片素材</span>
          <input
            type="file"
            accept="image/*"
            multiple
            onChange={(e: ChangeEvent<HTMLInputElement>) =>
              setImageFiles(e.target.files ? Array.from(e.target.files) : [])
            }
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
        <label className="field">
          <span>上传音乐素材</span>
          <input
            type="file"
            accept="audio/*"
            multiple
            onChange={(e: ChangeEvent<HTMLInputElement>) =>
              setAudioFiles(e.target.files ? Array.from(e.target.files) : [])
            }
          />
        </label>
      </div>
      {error ? <div className="auth-error">{error}</div> : null}
      <button type="submit" className="primary" disabled={submitting}>
        {submitting ? "上传中" : "提交"}
      </button>
    </form>
  )
}
