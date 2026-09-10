# Firmware Forge · 嵌入式开发技能与工作台

[English](README.en.md) · [安装与使用](docs/workbench-usage.md) · [设计理念](docs/design-philosophy.md) · [参与贡献](CONTRIBUTING.md)

为 AI 辅助的 **STM32 / Cortex-M 固件、FreeRTOS 与 MCU–FPGA 交互开发**提供三个可独立使用的技能，以及可选的 DSH 编译/烧录工作台。

它帮助你先确定需求，再设计最小协议与状态，完成实现和验证；从简单的开始/停止上传，到多通道采集和异步恢复，都按实际需求增加机制。

## 选择你需要的能力

| 你的任务 | 使用哪个技能 | 主要交付 |
|---|---|---|
| 设计设备与上位机/FPGA 的交互，或扩展已有协议 | [embedded-protocol-designer](embedded-protocol-designer/SKILL.md) | 行为约定、命令/状态、重复和失败语义、兼容性 |
| 实现或排查固件的采集、DMA、任务和状态退出 | [arm-cortex-expert](arm-cortex-expert/SKILL.md) | 代码与资源归属、执行边界、平台验证要求 |
| 验证解析、事件序列、测量回放和恢复行为 | [embedded-test-engineer](embedded-test-engineer/SKILL.md) | 相关测试、结果及实机验证缺口 |

一次小改动只需相关技能。技能是 AI 的工程指导与配套工具，不是直接运行在 MCU 上的协议栈或通用状态机引擎。

## 设计理念

**可靠性优化应让失败更可控，而不是让正常开发越来越复杂。**

先确定行为与验收条件，选择最小足够方案；真实状态有明确所有者，实际等待有结束方式，需求变化时局部扩展。判断依据是维护成本与可验证的行为，而非枚举数量。设计、实现、测试和实机证据分别说明。

具体取舍与简单启停、多通道实例见 [设计理念](docs/design-philosophy.md)。

## 快速开始

### 1. 获取项目

```sh
git clone https://github.com/Fz2hOpenSource/firmware-forge.git
cd firmware-forge
```

### 2. 选择入口

| 使用方式 | 下一步 | 需要什么 |
|---|---|---|
| 在 Codex 使用技能 | 按 [Codex 安装](docs/workbench-usage.md#codex) 复制所需完整技能目录，然后显式点名使用 | Codex；不要求 DSH、Keil 或开发板 |
| 在 DSH 使用工作台 | 阅读 [DSH 安装与更新范围](docs/workbench-usage.md#dsh)，再运行 `./install.ps1`（Windows 也可双击 `install.bat`） | 支持本 preset 的 DSH；当前 MDK 插件使用 Windows PowerShell |
| 先试离线工具 | 运行下面的状态图示例 | Python 3.10+；不需要 AI 宿主或硬件 |

### 3. 给 AI 一个明确的起始需求

安装后，在你的固件项目中使用：

```text
使用 $embedded-protocol-designer。
设备使用 STM32 + FreeRTOS，由一个上位机控制。
当前只需要 START、STOP、STATUS；STOP 要同时停止采集和上传。
运行中不调参，后续可能扩展为同步多通道。
先检查项目已有约定，给出最小行为表、重复命令和失败处理。
列出尚需确认的事实，不为未来需求预建框架；这一步先做设计。
```

预期得到相关需求、命令/状态短表、完成与失败语义和待验证条件。若必须跨事件等待，AI 应说明局部阶段、截止点和退出结果；驱动是否真正有界，需结合项目证据确认。

完整设计→实现→验证用法见 [使用示例](docs/workbench-usage.md#example)。

### 无硬件示例

以下命令均在本仓库根目录运行：

```sh
python embedded-test-engineer/scripts/check_state_model.py embedded-test-engineer/assets/reconfigure-model.json --json --strict
python embedded-test-engineer/scripts/check_state_model.py embedded-test-engineer/assets/stuck-model.json --json --strict
```

第一个示例应输出 `gate_status: pass`、退出 `0`；第二个故意包含超时恢复环，应报告 `TIMEOUT_CYCLE`、退出 `1`。它们是抽象图演示，不是设备测试。不要在一次“遇错即停”的脚本中把第二个当作成功步骤。

## 配套工具与依赖

| 能力 | 路径 | 使用条件 |
|---|---|---|
| 有限状态图检查 | `embedded-test-engineer/scripts/check_state_model.py` | Python 3.10+ 标准库；检查器 [格式与限制](embedded-test-engineer/references/state-model-format.md) |
| CubeMX 数据查询 | `arm-cortex-expert/tools/stm32cli/stm32cli.py` | Python；本地 CubeMX 数据库；[查询说明](arm-cortex-expert/references/tools-stm32cli.md) |
| Keil map 分析 | `arm-cortex-expert/tools/map-parser/map-parser.py` | Python；armlink 生成的 map；[工具说明](arm-cortex-expert/references/tools-map-parser.md) |
| MDK 编译/烧录 | `scripts/mdk/` 与 `plugins/mdk/` | Windows、Keil UV4、所选烧录工具及目标配置；[详细指南](docs/mdk-build-flash.md) |

新环境可统一使用 Python 3.10+；最近记录的工具测试环境为 Python 3.14.2，不代表完整跨版本/跨平台认证。第三方编译器、芯片数据库和烧录工具需自行安装，按各自许可使用。

## 文档与项目边界

- [安装、使用、更新和排错](docs/workbench-usage.md)
- [技能分工与维护](docs/skills-integration.md)
- [项目架构](docs/architecture.md) 与 [DSH 集成](docs/dsh-integration.md)
- [本次整合与验证记录](docs/integration-2026-09-10.md)
- [贡献指南](CONTRIBUTING.md) 与面向 AI 的 [项目约束](AGENTS.md)
- [行为验收场景](docs/skill-behavior-cases.md) 与 [2026-09-08 审查记录](docs/skills-audit-2026-09-08.md)

图检查不能证明固件调度、DMA/cache、FPGA CDC 或物理安全；芯片查询和 map 工具也不能替代实际项目和厂商证据。实机结论需要对应测试。

## 许可

本项目采用 [MIT License](LICENSE)。问题和改进建议可通过 [GitHub Issues](https://github.com/Fz2hOpenSource/firmware-forge/issues) 提交。
