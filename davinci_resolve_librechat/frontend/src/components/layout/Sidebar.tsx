import { NavLink } from "react-router-dom"
import logo from "../../assets/logo.svg"
import type { Conversation } from "../../types"

const navItems = [
  { to: "/chats", label: "对话" },
  { to: "/tasks", label: "任务" },
  { to: "/profile", label: "个人信息" },
  { to: "/settings", label: "设置" }
]

export default function Sidebar({
  conversations,
  activeConversationId,
  onSelectConversation,
  onNewConversation
}: {
  conversations?: Conversation[]
  activeConversationId?: string
  onSelectConversation?: (id: string) => void
  onNewConversation?: () => void
}) {
  return (
    <aside className="sidebar">
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
            {item.label}
          </NavLink>
        ))}
      </nav>
      {conversations && onSelectConversation ? (
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
    </aside>
  )
}
