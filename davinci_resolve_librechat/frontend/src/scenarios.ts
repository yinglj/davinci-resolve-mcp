export type Scenario = {
  id: string
  name: string
  description: string
  method: string
  buildParams: (prompt: string) => Record<string, unknown>
}

export const promptToken = "{{prompt}}"

export const scenarios: Scenario[] = [
  {
    id: "color-style",
    name: "自动调色",
    description: "按风格应用基础调色",
    method: "color_apply_style",
    buildParams: (prompt) => ({ style: "cinematic", prompt })
  },
  {
    id: "audio-normalize",
    name: "音频标准化",
    description: "规范响度并清理音轨",
    method: "audio_normalize_loudness",
    buildParams: (prompt) => ({ targetLufs: -14, prompt })
  },
  {
    id: "fusion-transition",
    name: "转场生成",
    description: "为片段添加转场效果",
    method: "fusion_add_transition",
    buildParams: (prompt) => ({ transition: "smooth", prompt })
  }
]
