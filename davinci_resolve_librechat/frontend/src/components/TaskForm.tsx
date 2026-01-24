import { useState, type ChangeEvent, type FormEvent } from "react"

export default function TaskForm({
  onSubmit
}: {
  onSubmit: (input: {
    title?: string
    prompt?: string
    mcpMethod?: string
    mcpParams?: string
  }) => Promise<void> | void
}) {
  const [title, setTitle] = useState("")
  const [prompt, setPrompt] = useState("")
  const [mcpMethod, setMcpMethod] = useState("")
  const [mcpParams, setMcpParams] = useState("")

  const handleSubmit = async (event: FormEvent) => {
    event.preventDefault()
    await onSubmit({
      title: title || undefined,
      prompt: prompt || undefined,
      mcpMethod: mcpMethod || undefined,
      mcpParams: mcpParams || undefined
    })
    setTitle("")
    setPrompt("")
    setMcpMethod("")
    setMcpParams("")
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
          <span>MCP 方法</span>
          <input
            value={mcpMethod}
            onChange={(e: ChangeEvent<HTMLInputElement>) => setMcpMethod(e.target.value)}
          />
        </label>
        <label className="field">
          <span>MCP 参数(JSON)</span>
          <textarea
            value={mcpParams}
            onChange={(e: ChangeEvent<HTMLTextAreaElement>) => setMcpParams(e.target.value)}
          />
        </label>
      </div>
      <button type="submit" className="primary">
        提交
      </button>
    </form>
  )
}
