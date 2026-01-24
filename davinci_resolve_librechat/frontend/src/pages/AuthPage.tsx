import { useState, type FormEvent } from "react"
import { useNavigate, Link } from "react-router-dom"
import { loginUser, registerUser, setAuthToken } from "../api"
import type { User } from "../types"

export default function AuthPage({
  mode,
  apiBaseUrl,
  onAuth
}: {
  mode: "login" | "register"
  apiBaseUrl: string
  onAuth: (user: User) => void
}) {
  const navigate = useNavigate()
  const [name, setName] = useState("")
  const [email, setEmail] = useState("")
  const [password, setPassword] = useState("")
  const [error, setError] = useState("")
  const isRegister = mode === "register"

  const handleSubmit = async (event: FormEvent) => {
    event.preventDefault()
    setError("")
    try {
      const payload = isRegister
        ? await registerUser(apiBaseUrl, { name, email, password })
        : await loginUser(apiBaseUrl, { email, password })
      setAuthToken(payload.token)
      onAuth(payload.user)
      navigate("/chats", { replace: true })
    } catch (err) {
      setError(err instanceof Error ? err.message : "请求失败")
    }
  }

  return (
    <div className="auth-layout">
      <div className="auth-card">
        <div className="auth-title">{isRegister ? "注册" : "登录"}</div>
        <form className="auth-form" onSubmit={handleSubmit}>
          {isRegister ? (
            <label className="field">
              <span>姓名</span>
              <input value={name} onChange={(e) => setName(e.target.value)} />
            </label>
          ) : null}
          <label className="field">
            <span>邮箱</span>
            <input value={email} onChange={(e) => setEmail(e.target.value)} />
          </label>
          <label className="field">
            <span>密码</span>
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
            />
          </label>
          {error ? <div className="auth-error">{error}</div> : null}
          <button type="submit" className="primary">
            {isRegister ? "创建账号" : "登录"}
          </button>
        </form>
        <div className="auth-switch">
          {isRegister ? (
            <span>
              已有账号？<Link to="/login">去登录</Link>
            </span>
          ) : (
            <span>
              还没有账号？<Link to="/register">去注册</Link>
            </span>
          )}
        </div>
      </div>
    </div>
  )
}
