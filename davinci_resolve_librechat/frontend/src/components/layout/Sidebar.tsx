import { NavLink } from "react-router-dom"

const navItems = [
  { to: "/chats", label: "对话" },
  { to: "/tasks", label: "任务" },
  { to: "/profile", label: "个人信息" },
  { to: "/settings", label: "设置" }
]

export default function Sidebar() {
  return (
    <aside className="sidebar">
      <div className="sidebar-logo">DaVinci Resolve LibreChat</div>
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
    </aside>
  )
}
