# P0-04: RenderPresetRunner

## 概要
实现渲染触发器 Skill：根据渲染预设（编码、分辨率、路径）启动渲染任务，返回任务 id 与状态，并支持回调/事件通知。

## 目标
- 提供 `render_timeline(project, timeline_name, preset)` 接口
- 支持异步队列（任务状态查询、取消、重试）
- 提供 hooks 发回渲染进度（百分比、帧区间）

## 验收标准
- 成功触发一个渲染任务并获取输出路径
- 支持失败重试策略与超时处理
- 有单元/集成测试（需要 mock 渲染）

## 子任务
- [ ] 定义 render preset schema
- [ ] 实现触发器 + 状态管理
- [ ] 实现回调与事件机制
- [ ] 测试与 docs

## 优先级
P0

## 估时
3-5 天
