---
applyTo: '**'
---
Provide project context and coding guidelines that AI should follow when generating code, answering questions, or reviewing changes.
#
- 我们之间使用中文交互
- 代码使用英文注释
- 代码风格遵循 PEP 8 和常见 Python 最佳实践
- 变量和函数命名使用有意义的英文单词，遵循蛇形命名法
- 保持函数简洁，每个函数只做一件事
- 提供必要的错误处理和异常捕获
- 包含类型提示以提高代码可读性
- 提供单元测试覆盖主要功能
- 遵循项目的架构设计和模块划分
- 在生成 PR 时，附上详细的变更说明和相关文档链接
- issues存放在 issues/ 目录下，包含详细的设计和实现计划
- 代码存放在 src/ 目录下，按功能模块划分子目录
- 测试代码存放在 tests/ 目录下，覆盖主要功能和边界情况
- 文档存放在 docs/ 目录下，包含使用说明和开发指南 
- davinci-resolve-mcp 项目旨在通过 AI 助手简化 DaVinci Resolve 的视频制作流程
- 项目采用 MCP 框架，支持多 Agent 协同工作
- 主要功能包括脚本解析、自动剪辑、Fusion 合成、调色和音频处理等
- 项目分为多个阶段，每个阶段有明确的目标和交付物
- 未来计划包括扩展更多 AI 能力和优化用户体验