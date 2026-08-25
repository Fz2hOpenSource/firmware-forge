# DSH 嵌入式开发工作台

面向 **STM32 / Keil MDK** 的 DSH 固件工作台。它帮助你在同一个 agent 会话里评审固件、查询芯片资源、定位 map 问题，并调用带防呆保护的 MDK 构建或烧录。

它不替代参考手册，也不替你猜硬件配置；项目代码、`.ioc`、链接脚本、实测结果和厂商资料始终优先。

## 适合的任务

| 你正在做的事 | 工作台提供什么 |
| --- | --- |
| 评审 SPI/ADC/UART + DMA | 检查 DMA 缓冲所有权、ISR 边界、Cache 一致性与 RTOS 优先级。 |
| 接手陌生 STM32 | 用 `stm32cli` 查询芯片、外设、DMA、引脚、时钟与中断。 |
| 定位 HardFault / 内存异常 | 用 `map-parser` 从 Keil `.map` 定位 PC、符号、内存区域和 MPU 对齐问题。 |
| 给固件补验证 | 规划主机单测、测试接缝、数据回放回归、容差与 HIL。 |
| 设计 UART / RS-485 / CAN 协议 | 约束帧格式、状态门控、超时重试与兼容性。 |
| 构建或烧录 MDK 工程 | 用 `/build` 统一执行编译和受防呆保护的烧录。 |

## 它不做什么

- 不取代项目代码、`.ioc`、链接脚本、实测结果或厂商资料；它们优先级更高。
- 不做 PCB、器件选型、电气参数或 EMC 设计。
- 不默认修改 HAL、RTOS、LwIP 等中间件内部；优先使用配置、回调、hook、weak override 与项目自有适配层。
- 不在多个工程或镜像之间猜测烧录目标；需要显式选择。

## 5 分钟上手

### 安装

双击 `install.bat`，或在终端运行：

```powershell
git clone <本仓库>
cd <仓库目录>
.\install.ps1          # 安装/更新到 $DSH_HOME\.agent-presets\embedded\
.\install.ps1 -Symlink # 开发模式：改仓库即生效
```

脚本会探测 `UV4.exe`，并从会话工作区向下搜索唯一的 `.uvprojx`。自动探测不满足时，编辑 `scripts\mdk\mdk.config.ps1`；多工程与后端配置见 [MDK 编译/烧录 SOP](docs/mdk-build-flash.md)。

### 启用与第一条指令

在 DSH 新建会话，选择「嵌入式开发工作台」preset。随后直接描述工程问题，例如：

- “评审这段 SPI + DMA 接收代码的缓存一致性。”
- “STM32H723 的 SPI1 RX 可以用哪个 DMA？”
- “HardFault 的 PC 是 `0x0800b455`，帮我从 map 定位。”

```text
/build        # 增量编译
/build -r     # 全量重编译
/build -f     # 烧录
/build -rf    # 全量重编译成功后再烧录
```

## 工作方式与安全护栏

工作台遵循“**最简单的充分方案**”：能用裸机就不上 RTOS，IRQ 足够就不上 DMA，单缓冲足够就不上环形队列；升级复杂度必须有项目证据或明确需求。

但 ISR/RTOS 优先级合规、DMA 缓冲所有权、M7/H7 Cache 一致性与 DMA 可访问内存、长度/索引边界检查，以及超时、溢出、DMA 错误的可观测性不是可选优化。完整规则见 [通用准则](arm-cortex-expert/references/common.md)。

组件关系、能力如何集成、边界与扩展方式见 [架构说明](docs/architecture.md)。

## 环境与支持范围

| 组件 | 必需性 | 用途 |
| --- | --- | --- |
| DSH | 必需 | preset 宿主。 |
| Python 3.8+ | 工具调用 | `stm32cli` 与 `map-parser`。 |
| STM32CubeMX 数据库 | 可选 | 仅 `stm32cli` 使用；通过 `--db-path` 或 `STM32CUBEMX_DB_PATH` 指定。 |
| Keil MDK / UV4 | 可选 | 仅构建与烧录使用。 |
| ST-Link / pyOCD / J-Link | 按后端需要 | 相应烧录后端。 |

当前重点支持 Windows、DSH、Cortex-M / STM32 与 Keil MDK。其他 IDE、芯片族和 DSH 版本不应被视为已验证支持。

## 文档导航

| 想了解什么 | 阅读位置 |
| --- | --- |
| 安装后的 preset、技能放置、更新与卸载 | [日常使用手册](docs/workbench-usage.md) |
| 工程、镜像与四种烧录后端 | [MDK 编译/烧录 SOP](docs/mdk-build-flash.md) |
| 四层架构、边界与扩展点 | [架构说明](docs/architecture.md) |
| host / isolate realm 与 preset 维护 | [DSH 集成说明](docs/dsh-integration.md) |
| 每项技能的完整契约 | 各技能目录的 `SKILL.md` 与 `references/` |
| English README | [README.en.md](README.en.md) |

## 仓库结构

```text
firmware-forge/
├── arm-cortex-expert/            # 固件设计/评审技能 + stm32cli、map-parser
├── embedded-test-engineer/       # 验证策略技能
├── embedded-protocol-designer/   # 通信协议设计技能
├── preset/                       # DSH 元数据与 agent 组合
├── plugins/mdk/                  # /build 插件
├── scripts/mdk/                  # MDK 与烧录后端脚本
├── docs/                         # 使用者与维护者文档
├── install.bat / install.ps1     # Windows 安装入口
└── LICENSE                       # MIT
```

## 许可

本项目以 [MIT License](LICENSE) 开源发布。
