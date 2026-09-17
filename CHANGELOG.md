# 更新日志 / Changelog

记录各版本面向使用者的变化。当前使用阶段性版本编号，兼容性以每版迁移说明为准；版本约定见 [贡献指南](CONTRIBUTING.md)。

## V1.1.1 — 技能规则与行为验收修订

版本准备日期：2026-09-17。变更范围：`V1.1.0` 之后的技能与文档修改。

### 改进与修正

- 固件技能补充同步依赖复核与跨入口一致性检查：同步须覆盖读写双方和在途访问，不仅保护写端；保留已有有效的停止与等待机制。
- 代次信息、预热状态与 HIL 前置条件按实际风险和机制选择，避免把测量项目经验变成所有任务的强制清单。
- 明确保存、运行态应用与新结果有效性的区别；操作失败可连同硬件状态不确定一并报告，不以恢复成功为报错前提。
- 协议与测试技能明确部分更新、空值、非法值和整体替换的契约边界；不能根据实现差异反推合法例外，测试预期应来自已声明契约。
- 强化回归测试的前置状态与定向反证、时序观测的证据边界，以及验证来源和条件化交接要求。
- 增加 A–I 行为验收输入、契约配对与同步修法案例，分开记录核心识别、修法、证据及额外工作量。

### 兼容性与验证范围

- 本版仅修订技能指令与文档，不修改工具实现、安装器、DSH 配置或构建/烧录命令接口；无新增命令迁移要求。
- 仓库结构校验、三个技能的基础校验及差异格式检查通过；行为案例仅是复测材料，不等于已通过的固件测试。
- 本地探索性行为试跑仍发现契约执行偏差和附带技术解释错误；样本少、模型条件未完全固定且无同步旧版/无技能对照，不宣称行为稳定性、泛化能力或修订收益已获证明。原始试跑记录未随版本纳入 Git。
- 本轮未新增真实宿主加载、UV4 构建、目标烧录或实机验证，也未重跑 V1.1.0 的工具测试；历史结果仍只适用于其记录范围。
- 更新技能前按 [使用指南](docs/workbench-usage.md) 比较并备份安装副本，保留宿主扩展与不同工具实现。

### English summary

This documentation-only patch clarifies synchronization coverage, configuration-update contracts, result validity, evidence limits and conditional handoffs. It adds paired behavior-review scenarios without changing tools or host command interfaces. Structural checks pass; exploratory agent runs still show errors and do not establish reliable behavior, generalization or improvement over a baseline. No new live-host or hardware validation is claimed.

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
