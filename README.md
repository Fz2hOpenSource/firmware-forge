# Firmware Forge · 嵌入式开发技能、命令与工具

[English](README.en.md) · [安装与使用](docs/workbench-usage.md) · [设计理念](docs/design-philosophy.md) · [参与贡献](CONTRIBUTING.md)

Firmware Forge 是面向嵌入式开发的 **AI 技能、命令与工具集**。当前重点覆盖 **STM32 / Cortex-M 固件、FreeRTOS、设备交互与测试验证**，配套芯片查询、构建产物分析和 Keil MDK 构建烧录能力。

当前提供 **Codex 技能安装**与 **DSH 工作台**两种宿主入口；其它宿主适配留待实际需求。现有能力以固件软件工程为主，不代表已覆盖所有 MCU、嵌入式 Linux 或板级硬件设计。

## 选择你需要的能力

| 你的任务 | 入口 | 主要交付 |
|---|---|---|
| 外设驱动、DMA/RTOS、采集与 DSP、存储、网络或性能排障 | [arm-cortex-expert](arm-cortex-expert/SKILL.md) | 聚焦实现或诊断、资源归属、平台验证要求 |
| 单元测试、驱动隔离、测量回放、精度回归或时序验证 | [embedded-test-engineer](embedded-test-engineer/SKILL.md) | 测试代码、回放结果、容差依据和实机验证缺口 |
| 设备与上位机/FPGA 的交互契约、协议设计或兼容演进 | [embedded-protocol-designer](embedded-protocol-designer/SKILL.md) | 帧与命令约定、重复/失败语义、兼容性 |
| 编译、重编译或烧录已有工程 | DSH `/build`、`/build -r`、`/flash` | 所选工程的执行结果与日志，见 [MDK 指南](docs/mdk-build-flash.md) |
| 查询芯片资源、分析 map 或检查已声明状态图 | 配套 Python 工具 | 有明确适用范围的查询与检查结果 |

技能提供工程指导，命令提供执行入口，工具处理具体数据。按任务组合，也可独立使用；协议设计并非固件开发、测试或构建的前置步骤。

## 设计理念

**任务明确、方案适度、依据可查、结果可验证。**

先明确本次任务和验收条件，沿用有效的工程基础，按需要实现、排障、测试或执行命令。需求先行不等于每次重写需求规格；状态建模、有界恢复等方法用于存在相关风险的路径。

取舍与驱动、算法、工具和交互示例见 [设计理念](docs/design-philosophy.md)。

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
| 先试离线工具 | 运行下面的工具帮助命令 | Python 3.10+；不需要 AI 宿主或硬件 |

### 3. 从当前任务开始

例如，在已有固件项目中请求 DMA 排障：

```text
使用 $arm-cortex-expert。
这是现有 STM32 + FreeRTOS 采集工程，DMA 完成后偶尔读到旧数据。
请检查实际 MCU、内存区域、缓存维护和 buffer 交接，先定位原因，
有证据后做最小修复。沿用已有采样与通信约定，说明验证结果和缺口。
```

测试工作可直接请求：

```text
使用 $embedded-test-engineer，为现有滤波与标定链建立回放回归。
先检查数据格式、参考结果和允许误差，再选择最小测试接缝。
区分数值回归一致性和实际测量精度。
```

更多独立任务与协议协作示例见 [使用示例](docs/workbench-usage.md#example)。

### 不依赖硬件的工具入口

在仓库根目录查看配套 CLI 的用途和参数：

```sh
python arm-cortex-expert/tools/stm32cli/stm32cli.py --help
python arm-cortex-expert/tools/map-parser/map-parser.py --help
python embedded-test-engineer/scripts/check_state_model.py --help
```

实际查询需准备 CubeMX 数据库，map 分析需已有构建产物；状态图检查需显式模型，是专项可选工具。可运行的正反例见 [工具试用](docs/workbench-usage.md#tools)。

## 配套工具与依赖

| 能力 | 路径 | 使用条件 |
|---|---|---|
| CubeMX 数据查询 | `arm-cortex-expert/tools/stm32cli/stm32cli.py` | Python；本地 CubeMX 数据库；[查询说明](arm-cortex-expert/references/tools-stm32cli.md) |
| Keil map 分析 | `arm-cortex-expert/tools/map-parser/map-parser.py` | Python；armlink 生成的 map；[工具说明](arm-cortex-expert/references/tools-map-parser.md) |
| MDK 编译/烧录 | `scripts/mdk/` 与 `plugins/mdk/` | Windows、Keil UV4、所选烧录工具及目标配置；[详细指南](docs/mdk-build-flash.md) |
| 有限状态图检查（可选） | `embedded-test-engineer/scripts/check_state_model.py` | Python 3.10+ 标准库；检查器 [格式与限制](embedded-test-engineer/references/state-model-format.md) |

新环境可统一使用 Python 3.10+；最近记录的工具测试环境为 Python 3.14.2，不代表完整跨版本/跨平台认证。第三方编译器、芯片数据库和烧录工具需自行安装，按各自许可使用。

## 文档与项目边界

- [安装、使用、更新和排错](docs/workbench-usage.md)
- [技能分工与维护](docs/skills-integration.md)
- [项目架构](docs/architecture.md) 与 [DSH 集成](docs/dsh-integration.md)
- [本次整合与验证记录](docs/integration-2026-09-10.md)
- [发布前检查记录](docs/release-check-2026-09-10.md)
- [贡献指南](CONTRIBUTING.md) 与面向 AI 的 [项目约束](AGENTS.md)
- [行为验收场景](docs/skill-behavior-cases.md) 与 [2026-09-08 审查记录](docs/skills-audit-2026-09-08.md)

图检查不能证明固件调度、DMA/cache、FPGA CDC 或物理安全；芯片查询和 map 工具也不能替代实际项目和厂商证据。实机结论需要对应测试。

## 许可

本项目采用 [MIT License](LICENSE)。问题和改进建议可通过 [GitHub Issues](https://github.com/Fz2hOpenSource/firmware-forge/issues) 提交。
