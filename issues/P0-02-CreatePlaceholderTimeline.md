# P0-02: CreatePlaceholderTimeline

## 概要
根据 shot-list 在 DaVinci Resolve 中自动创建 timeline，并为每个 shot 插入占位片段（可选静态图/黑屏），设置 track、markers 与时间码，作为后续自动填充的基础。

## 目标
- 在 `src/agent/executor` 中创建对应 Skill/Task
- 可配置占位类型（black/placeholder-image/duration）
- 提供 API：create_placeholder_timeline(project, shot_list, options)

## 验收标准
- 能根据给定 shot_list 创建可打开的 Resolve timeline
- 支持配置：framerate、resolution、track 设置
- 辅以单元或集成测试（mock Resolve 环境）

## 子任务
- [ ] 定义 API 与参数
- [ ] 实现基础创建逻辑（使用现有 project_operations）
- [ ] 编写测试（使用 mocks）
- [ ] 提供 example

## 优先级
P0

## 估时
3-5 天
