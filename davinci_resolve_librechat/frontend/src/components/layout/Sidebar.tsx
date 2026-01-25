import { NavLink, useNavigate } from "react-router-dom"
import { useState } from "react"
import logo from "../../assets/logo.svg"
import type { Conversation, User } from "../../types"

const navItems = [
  { to: "/chats", label: "对话", icon: "💬" },
  { to: "/tasks", label: "任务", icon: "🧰" }
]

export default function Sidebar({
  collapsed,
  conversations,
  activeConversationId,
  onSelectConversation,
  onNewConversation,
  user,
  onLogout,
  theme,
  onToggleTheme
}: {
  collapsed: boolean
  conversations?: Conversation[]
  activeConversationId?: string
  onSelectConversation?: (id: string) => void
  onNewConversation?: () => void
  user: User
  onLogout: () => void
  theme: "black" | "light"
  onToggleTheme: () => void
}) {
  const navigate = useNavigate()
  const [menuOpen, setMenuOpen] = useState(false)
  const initials = user?.name ? user.name.slice(0, 2).toUpperCase() : "U"
  return (
    <aside className={`sidebar ${collapsed ? "collapsed" : ""}`}>
      <div className="sidebar-logo">
        <img src={logo} alt="Davinci Resolve LibreChat" />
        <div>
          <div className="sidebar-title">DaVinci Resolve</div>
          <div className="sidebar-subtitle">LibreChat</div>
        </div>
      </div>
      <nav className="sidebar-nav">
        {navItems.map((item) => (
          <NavLink
            key={item.to}
            to={item.to}
            className={({ isActive }: { isActive: boolean }) =>
              isActive ? "nav-link active" : "nav-link"
            }
          >
            <span className="nav-icon">{item.icon}</span>
            <span className="nav-label">{item.label}</span>
          </NavLink>
        ))}
      </nav>
      {conversations && onSelectConversation && !collapsed ? (
        <div className="sidebar-section">
          <div className="sidebar-section-title">
            <span>Chats</span>
            {onNewConversation ? (
              <button type="button" className="ghost" onClick={onNewConversation}>
                新对话
              </button>
            ) : null}
          </div>
          <div className="sidebar-chat-list">
            {conversations.map((item) => (
              <button
                key={item.id}
                type="button"
                className={item.id === activeConversationId ? "sidebar-chat active" : "sidebar-chat"}
                onClick={() => onSelectConversation(item.id)}
              >
                {item.title}
              </button>
            ))}
          </div>
        </div>
      ) : null}
      <div className="sidebar-footer">
        <button
          type="button"
          className="sidebar-user-button"
          onClick={() => setMenuOpen((prev) => !prev)}
        >
          <div className="sidebar-user-avatar">
            {user.avatarUrl ? <img src={user.avatarUrl} alt={user.name} /> : initials}
          </div>
        </button>
        {menuOpen ? (
          <div className="sidebar-user-menu">
            <button
              type="button"
              className="sidebar-menu-item"
              onClick={() => {
                navigate("/settings")
                setMenuOpen(false)
              }}
            >
              Settings
            </button>
            <button
              type="button"
              className="sidebar-menu-item"
              onClick={() => {
                navigate("/tasks")
                setMenuOpen(false)
              }}
            >
              Tasks
            </button>
            <button type="button" className="sidebar-menu-item" onClick={() => setMenuOpen(false)}>
              Files
            </button>
            <button type="button" className="sidebar-menu-item" onClick={() => setMenuOpen(false)}>
              Grokipedia
            </button>
            <button type="button" className="sidebar-menu-item" onClick={() => setMenuOpen(false)}>
              Help
            </button>
            <button
              type="button"
              className="sidebar-menu-item"
              onClick={() => {
                onToggleTheme()
                setMenuOpen(false)
              }}
            >
              {theme === "black" ? "🌙" : "☀️"} Theme
            </button>
            <button type="button" className="sidebar-menu-item" onClick={() => setMenuOpen(false)}>
              Upgrade plan
            </button>
            <button
              type="button"
              className="sidebar-menu-item"
              onClick={() => {
                onLogout()
                setMenuOpen(false)
              }}
            >
              Sign Out
            </button>
          </div>
        ) : null}
      </div>
    </aside>
  )
}
