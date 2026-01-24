import type { User } from "../types"

export default function ProfilePage({ user }: { user: User }) {
  return (
    <div className="profile-card">
      <div className="card-title">个人信息</div>
      <div className="profile-row">
        <span>姓名</span>
        <span>{user.name}</span>
      </div>
      <div className="profile-row">
        <span>邮箱</span>
        <span>{user.email}</span>
      </div>
      <div className="profile-row">
        <span>权限</span>
        <span>基础用户</span>
      </div>
    </div>
  )
}
