# 更新日志 / Changelog

记录各版本面向使用者的变化。当前使用阶段性版本编号，兼容性以每版迁移说明为准；版本约定见 [贡献指南](CONTRIBUTING.md)。

## V1.1.0 — 完善嵌入式开发技能与工具

版本准备日期：2026-09-10。变更范围：`V1.0.0` 之后的提交。

### 升级注意：DSH 命令有不兼容调整

构建与烧录拆分为独立命令，旧用法需要迁移：

| 旧用法 | V1.1.0 用法 |
|---|---|
| `/build -f` | `/flash` |
| `/build -rf` | 先 `/build -r`，确认成功后单独 `/flash` |
| `/build -b` | `/build` |

`/build` 与 `/build -r` 保持原用途。新版编译开关仅支持 `-r`，烧录不接受编译开关；旧的其它组合或大小写变体应改用上述规范写法。支持 `/build <昵称>`、`/build <昵称> -r` 和 `/flash <昵称>` 指定工程。已有脚本、快捷提示和使用说明也需同步更新。

DSH 更新前备份受管目录中的定制内容；安装器会镜像替换插件、脚本与技能目录。Codex 技能按 [安装指南](docs/workbench-usage.md) 比较、备份并更新完整技能目录，不使用 DSH 安装器。

### 新增与改进

- 完善面向 STM32 / Cortex-M 与 FreeRTOS 的固件开发、测试验证和协议设计技能；支持按任务独立选择，协议设计不是普通开发的前置步骤。
- 补充采集/DSP、持久化存储、DMA/cache、多通道与异步恢复指导，明确数值回放、精度证据和目标验证边界。
- 新增可选有限状态图检查器，包含严格模式、正反例及回归测试，用于检查声明模型中的退出路径和超时恢复环。
- 完善 Codex / DSH 安装、自然语言使用、命令工具入口、中英文文档、设计理念及贡献约定。

### 修复

- 修复 UV4 进程尚未结束时提前判定结果的问题，采用有限等待并依据本次日志报告结果。
- 对齐 MDK 内外层时限：UV4 等待 900 秒，插件外层等待 960 秒，给内部超时处理与结果收集留出余量。
- 外层中断时明确报告结果不确定，保留诊断信息，不自动重试。

### 验证与限制

- 已有 45 项自动化测试通过：状态检查器 18 项、芯片查询 23 项、MDK 插件 4 项。
- 安装示例、DSH 隔离复制安装/更新及格式/链接检查记录见 [发布前检查](docs/release-check-2026-09-10.md)。本次版本整理仅调整文档，工具实现保持不变。
- 上述记录不包含独立 AI 行为评估、真实 DSH 会话加载、UV4 构建或目标烧录的通过结论，也不代表跨平台/版本认证。状态图检查不证明固件调度或硬件安全。

### English upgrade summary

This milestone improves the embedded firmware skills, verification guidance and documentation, adds an optional state-graph linter, and fixes UV4 waiting and nested command deadlines.

**Breaking DSH command changes:** replace `/build -f` with `/flash`; replace `/build -rf` with `/build -r` followed by a separate `/flash` after checking success. Replace `/build -b` with `/build`. Use the documented lowercase forms; other legacy flag combinations are not supported. Back up managed DSH customizations before updating. Update Codex skills using the skill installation guide, not the DSH installer.

The 45 automated tests cover offline logic and substituted process boundaries. See the pre-release record for the remaining live-host and hardware validation gaps.
