# P1-02: Fusion Dynamic Composition

## 概要
封装 Fusion 模板和动态图形生成能力，提供 API 用于插入自动生成的片头/转场/动效。

## 目标
- 建立 Fusion template 管理与参数化接口
- 提供工具 `generate_fusion_clip(template, params)` 并返回 clip placeholder
- Integrate with task_executor to insert generated clips into timeline

## 估时
4-7 天
