# P0-03: ImportAndTagAssets

## 概要
实现素材导入与元数据管理 Skill：支持从本地/网络/云导入素材，并为素材打标签、记录来源、生成缩略图与时间码索引，便于 Planner/Executor 调用。

## 目标
- 提供 `import_assets(paths_or_urls, metadata)` 接口
- 自动生成 asset id，支持 tags、duration、format、resolution
- 缓存/索引素材以便快速检索

## 验收标准
- 能导入常见视频/音频/图片格式并返回标准化 metadata
- 能按 tag/metadata 查询素材
- 有单元测试和示例

## 子任务
- [ ] 设计 metadata schema
- [ ] 实现导入逻辑与本地缓存路径管理
- [ ] 缩略图生成
- [ ] 测试与示例

## 优先级
P0

## 估时
2-4 天
