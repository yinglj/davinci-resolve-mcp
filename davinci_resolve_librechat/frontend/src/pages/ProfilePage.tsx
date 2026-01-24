import { useEffect, useState, type ChangeEvent } from "react"
import type { User } from "../types"

export default function ProfilePage({
  user,
  onUpdate
}: {
  user: User
  onUpdate: (input: { name?: string; avatarUrl?: string | null }) => Promise<void>
}) {
  const [name, setName] = useState(user.name)
  const [avatarUrl, setAvatarUrl] = useState<string | null>(user.avatarUrl || null)
  const [error, setError] = useState("")
  const [saving, setSaving] = useState(false)

  useEffect(() => {
    setName(user.name)
    setAvatarUrl(user.avatarUrl || null)
  }, [user])

  const handleAvatarChange = (event: ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0]
    if (!file) {
      return
    }
    const reader = new FileReader()
    reader.onload = () => {
      if (typeof reader.result === "string") {
        setAvatarUrl(reader.result)
      }
    }
    reader.readAsDataURL(file)
  }

  const handleSave = async () => {
    setSaving(true)
    setError("")
    try {
      await onUpdate({ name, avatarUrl })
    } catch (err) {
      setError(err instanceof Error ? err.message : "更新失败")
    } finally {
      setSaving(false)
    }
  }

  return (
    <div className="profile-card">
      <div className="card-title">个人信息</div>
      <div className="profile-avatar">
        <div className="profile-avatar-preview">
          {avatarUrl ? <img src={avatarUrl} alt={user.name} /> : user.name.slice(0, 2)}
        </div>
        <div className="profile-avatar-actions">
          <input type="file" accept="image/*" onChange={handleAvatarChange} />
          {avatarUrl ? (
            <button type="button" className="ghost" onClick={() => setAvatarUrl(null)}>
              移除头像
            </button>
          ) : null}
        </div>
      </div>
      <label className="field">
        <span>姓名</span>
        <input value={name} onChange={(e) => setName(e.target.value)} />
      </label>
      <div className="profile-row">
        <span>邮箱</span>
        <span>{user.email}</span>
      </div>
      <div className="profile-row">
        <span>权限</span>
        <span>基础用户</span>
      </div>
      {error ? <div className="profile-error">{error}</div> : null}
      <button type="button" className="primary" onClick={handleSave} disabled={saving}>
        {saving ? "保存中..." : "保存资料"}
      </button>
    </div>
  )
}
