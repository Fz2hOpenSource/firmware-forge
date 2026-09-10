# 技能分工与维护

[设计理念](design-philosophy.md) · [安装与使用](workbench-usage.md) · [贡献指南](../CONTRIBUTING.md)

本项目提供嵌入式开发的技能、命令和工具。先辨识当前任务，再选择合适入口；固件开发、协议设计与测试验证没有固定的先后依赖。

## 三个技能的责任

| 技能 | 决策责任 | 按需参考 |
|---|---|---|
| [arm-cortex-expert](../arm-cortex-expert/SKILL.md) | 驱动、DMA/RTOS/cache、采集/DSP、存储、网络和性能排障 | common、core/family、measurement-dsp、persistent-storage、lwip-ethernet；真实等待涉及 state-and-interaction |
| [embedded-test-engineer](../embedded-test-engineer/SKILL.md) | 单元/驱动测试、测试接缝、回放、容差、时序与 HIL | test-strategy、test-doubles、data-replay、timing-and-hil；交互验证涉及 protocol-state-testing |
| [embedded-protocol-designer](../embedded-protocol-designer/SKILL.md) | 公开交互契约、帧与命令、重复/失败语义及兼容演进 | requirements-and-growth、frame-and-fields、command-space、operation-lifecycle |

## 如何组合

- 固件修复或优化从实际驱动和数据路径开始。接口语义未变时，不先重做协议设计。
- 回放与测试接缝可以直接从测试技能开始。算法误差和参考数据不足时，先解决验证依据，而不是生成无关状态模型。
- 协议设计只处理交互契约；需要实现或验证时再协作。协议需求不会自动扩大到所有产品需求。
- 单独查询芯片、分析 map、构建或烧录可直接使用相关工具/命令，核对输入和目标；工具结果不清楚或需要工程判断时再加载相关技能。
- 新功能或跨模块问题按需要组合技能，沿用已有约定。冲突时保留证据，按产品需求和实际硬件限制解决。

## 命令与工具

DSH 的 `/build`、`/build -r` 与 `/flash` 封装已有工程的执行；Python 工具分别提供 CubeMX 查询、map 分析和可选状态图检查。命令不负责替用户决定设计，检查器不承担固件运行时控制。入口及依赖见 [使用指南](workbench-usage.md)。

## 源码与宿主适配

三个技能目录中的 `SKILL.md` 和相对路径资源为共用内容，不依赖本仓库的人类文档才能执行。格式上可被其它支持 `SKILL.md` 的宿主加载，但**本版本仅支持并验证 Codex 与 DSH 两种入口**；其它宿主适配与兼容性验证留待实际需求。

DSH 的 `preset/`、MDK 插件和 PowerShell 脚本是宿主适配；复制技能不会获得 `/build`。安装到哪里、如何刷新由宿主决定，使用实际加载路径，见 [安装指南](workbench-usage.md)。

仓库是共用规则的维护源。历史安装副本可能带不同工具版本或本地扩展，更新时：

1. 核对源码版本、目标加载路径及双方差异。
2. 验证拟同步的文件，备份目标中将被替换的内容。
3. 按明确文件合并，保留未纳入改动的专用能力，并检查结果。

不要把文档同步顺便变成工具版本替换。`stm32cli`、map 工具的参数和输出可能随版本变化，先看当前 `--help`。

现有 DSH 安装器采用受管目录镜像，不能承担以上差异合并：有定制副本时应先备份/合并，或者把额外内容移到宿主支持的非受管位置，再明确运行安装。Codex 更新不使用该安装器。

## 验证与演进

[行为验收场景](skill-behavior-cases.md) 覆盖驱动排障、DSP/存储、数值回放、工具调用与协议交互，评价 AI 是否选择了相关入口和适当工作量。它们是判据，不是已经执行过的设备测试。

共用检查及相关工具测试见 [贡献指南](../CONTRIBUTING.md)。研究中的退出检查已作为测试技能的可选工具；当前没有提供通用固件状态机引擎。公共代码应来自真实项目的稳定需求与复用价值。

当前整合及证据范围见 [2026-09-10 整合记录](integration-2026-09-10.md)，前期内容审查见 [2026-09-08 审查记录](skills-audit-2026-09-08.md)。历史验证只针对记录中的版本和条件，不能替代对新变更的检查。
