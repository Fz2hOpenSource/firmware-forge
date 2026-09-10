# 技能分工与维护

[设计理念](design-philosophy.md) · [安装与使用](workbench-usage.md) · [贡献指南](../CONTRIBUTING.md)

先确定当前需求，再设计最小交互与状态，实施并验证；需求变化时分析受影响行为并局部扩展。

## 三个技能的责任

| 技能 | 决策责任 | 主要参考 |
|---|---|---|
| [embedded-protocol-designer](../embedded-protocol-designer/SKILL.md) | 对外行为、命令/状态约定、重复与失败语义、兼容性 | requirements-and-growth、state-and-timing、operation-lifecycle |
| [arm-cortex-expert](../arm-cortex-expert/SKILL.md) | 状态写者、实际等待与调度、资源交还、硬件观测 | state-and-interaction、common、measurement-streaming |
| [embedded-test-engineer](../embedded-test-engineer/SKILL.md) | 故障事件序列、资源/时间验证、验证层级与限制 | protocol-state-testing、state-model-format |

简单同步启停可以只用短表和一个 owner；真实异步等待才有局部阶段。同步多通道可共用采集状态机，独立通道按需实例化，共享时钟等由资源 owner 协调。技能例子不是固定产品需求。

按当前任务加载需要的技能，不要求每次全部加载。协议、固件、测试的约定冲突时，保留证据并根据产品需求和实际硬件限制解决，不能让某个技能文字静默覆盖它们。

## 源码与宿主适配

三个技能目录中的 `SKILL.md` 和相对路径资源为共用内容，可独立复制到支持该格式的宿主。它们不依赖本仓库的人类文档才能执行。

DSH 的 `preset/`、MDK 插件和 PowerShell 脚本是宿主适配；复制技能不会让其它宿主自动获得 `/build`。安装到哪里、如何刷新由宿主决定，使用实际加载路径，见 [安装指南](workbench-usage.md)。

仓库是共用规则的维护源。历史安装副本可能带不同工具版本或本地扩展，更新时：

1. 核对源码版本、目标加载路径及双方差异。
2. 验证拟同步的文件，备份目标中将被替换的内容。
3. 按明确文件合并，保留未纳入改动的专用能力，并检查结果。

不要把文档同步顺便变成工具版本替换。`stm32cli`、map 工具的参数和输出可能随版本变化，先看当前 `--help`。

现有 DSH 安装器采用受管目录镜像，不能承担以上差异合并：有定制副本时应先备份/合并，或者把额外内容移到宿主支持的非受管位置，再明确运行安装。Codex 更新不使用该安装器。

## 验证与演进

[行为验收场景](skill-behavior-cases.md) 用于评价 AI 是否保持简单、正确处理多通道扩展、未知结果和有界恢复。它们是判据，不是已经执行过的设备测试。

共用检查及相关工具测试见 [贡献指南](../CONTRIBUTING.md)。研究中的退出检查已作为测试技能的可选工具；当前没有提供通用固件状态机引擎。公共代码应来自真实项目的稳定需求与复用价值。

当前整合及证据范围见 [2026-09-10 整合记录](integration-2026-09-10.md)，前期内容审查见 [2026-09-08 审查记录](skills-audit-2026-09-08.md)。历史验证只针对记录中的版本和条件，不能替代对新变更的检查。
