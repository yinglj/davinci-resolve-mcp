# P1-01: AutoCut & Rhythm Matching

## 概要
根据脚本节奏、音乐节拍与风格示例自动计算剪辑点与镜头时长，形成初步剪辑草案。

## 目标
- 输入：shot_list + optional music track (BPM) + style sample
- 输出：timeline edit boundaries (in/out for each shot)
- 实现简单节奏匹配算法（BPM -> beat spacing -> map shots to beats）
- 提供 visual QA helpers（生成 thumbnails/rough cuts）

## 验收标准
- 单元测试验证 beat->time mappings
- POC pipeline: ScriptToShots -> AutoCut -> Placeholder timeline with in/out set

## 估时
5-8 天
