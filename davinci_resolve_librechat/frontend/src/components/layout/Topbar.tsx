import type { User } from "../../types"

export default function Topbar({
  title,
  user,
  onLogout
}: {
  title: string
  user: User | null
  onLogout: () => void
}) {
  const initials = user?.name ? user.name.slice(0, 2).toUpperCase() : "U"
  return (
    <header className="topbar">
      <div className="topbar-title">{title}</div>
      <div className="topbar-actions">
        {user ? (
          <div className="topbar-user">
            <div className="topbar-user-avatar">
              {user.avatarUrl ? <img src={user.avatarUrl} alt={user.name} /> : initials}
            </div>
            <div className="topbar-user-meta">
              <div className="topbar-user-name">{user.name}</div>
              <div className="topbar-user-email">{user.email}</div>
            </div>
          </div>
        ) : null}
        <button type="button" className="ghost" onClick={onLogout}>
          退出
        </button>
      </div>
    </header>
  )
}
