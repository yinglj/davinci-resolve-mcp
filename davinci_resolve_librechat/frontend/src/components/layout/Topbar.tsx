export default function Topbar({
  title,
  showSidebar,
  showRightbar,
  onToggleSidebar,
  onToggleRightbar
}: {
  title: string
  showSidebar: boolean
  showRightbar: boolean
  onToggleSidebar: () => void
  onToggleRightbar: () => void
}) {
  return (
    <header className="topbar">
      <div className="topbar-title">{title}</div>
      <div className="topbar-actions">
        <button type="button" className="ghost" onClick={onToggleSidebar}>
          {showSidebar ? "隐藏左栏" : "显示左栏"}
        </button>
        <button type="button" className="ghost" onClick={onToggleRightbar}>
          {showRightbar ? "隐藏右栏" : "显示右栏"}
        </button>
      </div>
    </header>
  )
}
