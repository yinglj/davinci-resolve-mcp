export default function Topbar({
  title
}: {
  title: string
}) {
  return (
    <header className="topbar">
      <div className="topbar-title">{title}</div>
    </header>
  )
}
