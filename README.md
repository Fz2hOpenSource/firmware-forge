# Firmware Forge · 嵌入式开发技能、命令与工具

[English](README.en.md) · [安装与使用](docs/workbench-usage.md) · [设计理念](docs/design-philosophy.md) · [参与贡献](CONTRIBUTING.md)

嵌入式开发里，AI 往往卡在同一件事上：它擅长写代码，却未必知道该查哪本手册、该守哪些边界、该在何处停手。Firmware Forge 要补的正是这一段——一组面向 STM32 / Cortex-M 与 FreeRTOS 的 AI 技能，配上芯片查询、map 分析，以及 Keil MDK 的编译与烧录命令。

技能负责工程判断，命令负责真正动手，工具负责查清具体数据。三者可以合用，也可以分开用。协议设计是其中一项专项能力，而不是所有工作的必经步骤。

目前可在 **Codex** 与 **DSH** 中使用；其它宿主尚未纳入支持范围。能力边界止于固件软件工程，并不覆盖所有 MCU、嵌入式 Linux 或板级硬件设计。

## 能力地图

安装完成后，直接描述任务即可。AI 会按请求内容加载对应技能，或调用配套命令与工具。也可以在句首用 `$技能名` 指定入口。

| 你的任务 | 入口 | 主要交付 |
|---|---|---|
| 外设驱动、DMA/RTOS、采集与 DSP、存储、网络，或性能排障 | [arm-cortex-expert](arm-cortex-expert/SKILL.md) | 聚焦的实现或诊断、资源归属，以及平台侧仍需验证的部分 |
| 单元测试、驱动隔离、测量回放、精度回归或时序验证 | [embedded-test-engineer](embedded-test-engineer/SKILL.md) | 测试代码、回放结果、容差依据，以及实机验证缺口 |
| 设备与上位机 / FPGA 的交互契约、协议设计或兼容演进 | [embedded-protocol-designer](embedded-protocol-designer/SKILL.md) | 帧与命令约定、重复与失败语义、兼容性 |
| 编译、重编译或烧录已有工程 | DSH 的 `/build`、`/build -r`、`/flash` | 所选工程的执行结果与日志，详见 [MDK 指南](docs/mdk-build-flash.md) |
| 查询芯片资源、分析 map，或检查已声明的状态图 | 配套 Python 工具 | 有明确适用范围的查询与检查结果 |

## 设计理念

可靠的工程改进，应当让失败更可控，而不是让日常开发越来越重。Firmware Forge 遵循四条朴素原则：把任务说清楚，方案做到够用就好，结论落在可查的依据上，结果能被验证。

「需求先行」并不意味着每次修改都先写一版产品规格；状态建模、有界恢复等方法，也只用在确实存在风险的路径上。更多取舍与示例见[设计理念](docs/design-philosophy.md)。

## 快速开始

### 1. 获取项目

```sh
git clone https://github.com/Fz2hOpenSource/firmware-forge.git
cd firmware-forge
```

### 2. 安装到你的环境

| 使用方式 | 下一步 | 需要什么 |
|---|---|---|
| 在 Codex 使用技能 | 按 [Codex 安装](docs/workbench-usage.md#codex) 复制完整技能目录；之后直接描述任务即可 | Codex，不要求 DSH、Keil 或开发板 |
| 在 DSH 使用工作台 | 阅读 [DSH 安装说明](docs/workbench-usage.md#dsh)，再运行 `./install.ps1`（Windows 也可双击 `install.bat`） | 支持本 preset 的 DSH；当前 MDK 插件依赖 Windows PowerShell |
| 先试离线工具 | 运行下方帮助命令，先摸清工具边界 | Python 3.10+，不需要 AI 宿主或硬件 |

### 3. 从当前任务开始

```text
这是现有 STM32 + FreeRTOS 采集工程，DMA 完成后偶尔读到旧数据。
请检查实际 MCU、内存区域、缓存维护和 buffer 交接，先定位原因，
有证据后做最小修复。沿用已有采样与通信约定，说明验证结果和缺口。
```

测试同样可以直接提：

```text
为现有滤波与标定链建立回放回归。
先检查数据格式、参考结果和允许误差，再选择最小测试接缝。
区分数值回归一致性和实际测量精度。
```

更多任务示例见[使用指南](docs/workbench-usage.md#example)。

### 不依赖硬件的工具

在仓库根目录即可查看各 CLI 的用途与参数：

```sh
python arm-cortex-expert/tools/stm32cli/stm32cli.py --help
python arm-cortex-expert/tools/map-parser/map-parser.py --help
python embedded-test-engineer/scripts/check_state_model.py --help
```

芯片查询需要本地 CubeMX 数据库，map 分析需要已有的构建产物；状态图检查则针对显式建模的等待与恢复，是专项工具，不替代运行时验证。可运行的正反例见[工具试用](docs/workbench-usage.md#tools)。

## 配套工具与依赖

| 能力 | 路径 | 使用条件 |
|---|---|---|
| CubeMX 数据查询 | `arm-cortex-expert/tools/stm32cli/stm32cli.py` | Python；本地 CubeMX 数据库；[查询说明](arm-cortex-expert/references/tools-stm32cli.md) |
| Keil map 分析 | `arm-cortex-expert/tools/map-parser/map-parser.py` | Python；armlink 生成的 map；[工具说明](arm-cortex-expert/references/tools-map-parser.md) |
| MDK 编译 / 烧录 | `scripts/mdk/` 与 `plugins/mdk/` | Windows、Keil UV4、所选烧录工具及目标配置；[详细指南](docs/mdk-build-flash.md) |
| 有限状态图检查（可选） | `embedded-test-engineer/scripts/check_state_model.py` | Python 3.10+ 标准库；[格式与限制](embedded-test-engineer/references/state-model-format.md) |

新环境建议统一使用 Python 3.10+。最近记录的工具测试环境为 Python 3.14.2，这不代表已完成跨版本或跨平台认证。第三方编译器、芯片数据库和烧录工具需自行安装，并遵守各自许可。

## 文档导航

- [安装、使用、更新和排错](docs/workbench-usage.md)
- [技能分工与维护](docs/skills-integration.md)
- [项目架构](docs/architecture.md) 与 [DSH 集成](docs/dsh-integration.md)
- [本次整合与验证记录](docs/integration-2026-09-10.md)
- [发布前检查记录](docs/release-check-2026-09-10.md)
- [贡献指南](CONTRIBUTING.md) 与面向 AI 的 [项目约束](AGENTS.md)
- [行为验收场景](docs/skill-behavior-cases.md) 与 [2026-09-08 审查记录](docs/skills-audit-2026-09-08.md)

需要强调的是：状态图检查证明不了固件调度、DMA/cache、FPGA CDC 或物理安全；芯片查询与 map 工具也不能替代实际工程与厂商资料。涉及真实设备的结论，仍须落在对应测试上。

## 许可

本项目采用 [MIT License](LICENSE)。问题与改进建议欢迎通过 [GitHub Issues](https://github.com/Fz2hOpenSource/firmware-forge/issues) 提交。
