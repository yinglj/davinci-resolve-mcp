# P0-01: ScriptToShots

## 概要
将用户提供的自然语言脚本/分镜（storyboard）解析为按镜头（shot）分解的结构化计划（JSON），每个 shot 包含：id, summary, duration_sec (估算), shot_type（wide/close/insert/etc.）, assets_needed, notes。

## 目标
- 提供一个轻量、可扩展的解析器（`src/agent/planner/skills/script_to_shots.py`）
- 支持多种输入风格：段落叙述、分镜编号、场景标题。
- 输出符合 schema 的 JSON，便于 executor 消费。
- 提供单元测试覆盖常见/边缘案例。
- 提供一个 `examples/generate_short_from_script.py` 演示脚本。

## 验收标准
- 解析器能把至少 3 种格式的脚本转为 shot-list，并包含 duration 估算
- 单元测试通过（pytest）
- 示例脚本运行并输出 JSON 到 stdout 或文件

## 子任务
- [ ] 设计 JSON schema
- [ ] 实现解析器函数 parse_script_to_shots(text) 返回 list[dict]
- [ ] 编写单元测试覆盖关键场景
- [ ] 增加示例脚本
- [ ] 文档说明（README 或 skills 列表更新）

## 优先级
P0

## 估时
3-5 天（POC + tests + docs）
