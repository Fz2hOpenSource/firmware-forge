# DSH Embedded Workbench（嵌入式开发工作台）

面向 **Cortex-M / STM32 固件开发**的 [DSH](https://github.com/deepseek-ai) agent preset。把固件设计评审技能、芯片数据库查询工具、Keil map 分析工具和 MDK 编译/烧录命令打包成一个可一键启用的工作台——在 DSH 会话里完成「设计 → 编码 → 编译 → 烧录 → 调试」的完整闭环。

## 为什么做这个

AI 写固件代码很快，但缺资深工程师的约束：DMA 缓存一致性、中断优先级错序、RTOS 任务边界这些坑，没人提醒就不存在。查一颗陌生芯片的外设资源要翻几百页手册，而 AI 明明可以直接查 CubeMX 数据库；HardFault 到手只有一行 PC 值，与其盲猜不如直接解析 `.map` 定位到符号。这个工作台把这三件事变成开箱即用的技能和工具，再把编译烧录接进来，让整个调试闭环留在同一个会话里。

## 核心能力

按你要做的事来看（而不是按仓库里有什么）：

| 你想做什么 | 它怎么帮你 |
|---|---|
| 🧠 让 AI 按资深嵌入式的标准评审设计 | `arm-cortex-expert` 审查 SPI+DMA 的缓存一致性、中断优先级错序、RTOS 任务边界违规、驱动分层——按你的芯片型号自动加载对应参考 |
| 🧪 给固件立一套验证策略，而不是裸奔上板 | `embedded-test-engineer` 规划测试分层、测试替身与接缝、测量数据回放回归、容差判定、HIL 覆盖 |
| 📡 设计一条设备通信协议并守住演进规则 | `embedded-protocol-designer` 定义帧格式、命令空间、状态门控、超时重传，并治理版本冻结（RS-485/UART/CAN 等） |
| 🔍 摸清一颗陌生 STM32 的家底 | `stm32cli` 直查 CubeMX 数据库：芯片能力、外设实例、DMA 请求映射、引脚复用、时钟树、中断向量 |
| 🗺️ 定位 HardFault、看内存被谁吃掉 | `map-parser` 解析 Keil `.map`：符号查找、内存区域分析、PC 值定位、体积排名、MPU 对齐检查 |
| ⚙️ 编译烧录不出会话 | `/build` 一条命令完成 UV4 编译与烧录（keil/stlink/dap/jlink 四后端），详见 [编译/烧录 SOP](docs/mdk-build-flash.md) |

## 复杂度阶梯

本工作台的方法论底座：**六级停点**——每一级问自己一个问题，答案是"是"就停在那里，不要往上爬：

1. 裸机超循环能满足时延、抖动和可维护性吗？能就不用 RTOS。
2. 阻塞/轮询/中断驱动 I/O 够用吗？够就不上 DMA。
3. 单缓冲加清晰的所有权扛得住最坏消费延迟吗？扛得住就不上双缓冲/环形队列。
4. 非缓存 DMA 区域能解决 Cache 一致性吗？能就不做逐次 clean/invalidate。
5. 整数/定点误差低于实测噪声预算吗？是就别上浮点/CMSIS-DSP（有 FPU 且实测安全也不强制定点）。
6. 直接驱动 API 保得住所有权与背压吗？保得住就不引框架/队列/网络传输层。

停点是上限不是台阶：升级必须由项目证据或明确需求触发，并写下升级理由；硬安全边界（中断临界区、Cache 维护、DMA 可访问性）不参与简化。完整定义见 [arm-cortex-expert/references/common.md](arm-cortex-expert/references/common.md)。

## 快速开始

### ① 安装（一次）

最简单的方式：**在文件管理器里双击 `install.bat`**，按提示等它跑完即可。

也可以用命令行：

```powershell
git clone <本仓库>
cd <仓库目录>
.\install.ps1          # 同步到 $DSH_HOME\.agent-presets\embedded\
.\install.ps1 -Symlink # 开发模式：改仓库即生效（需开发者模式/管理员）
```

通常**无需任何配置**：UV4.exe 走注册表自动探测，工程 `.uvprojx` 从会话工作区向下自动搜索。仅当自动探测失败时才需要编辑 `$DSH_HOME\.agent-presets\embedded\scripts\mdk\mdk.config.ps1`（字段详解见 [SOP](docs/mdk-build-flash.md)）。

### ② 启用

在 DSH 新建会话，preset 菜单选择「嵌入式开发工作台」（选一次即记住为默认）。

### ③ 第一条命令

对 AI 直接说需求即可：

- 「评审这段 SPI+DMA 接收代码的缓存一致性」→ M7/H7 场景自动加载对应参考
- 「查一下 STM32H723 的 SPI1 RX 走哪个 DMA」→ 内部调用 `stm32cli`
- 「这个 HardFault，PC=0x0800b455，帮我定位」→ 内部调用 `map-parser fault`

编译/烧录用斜杠命令（后缀含义详见 [SOP](docs/mdk-build-flash.md)）：

```text
/build        # 增量编译（默认）
/build -r     # 全量重编译
/build -f     # 烧录下载
/build -rf    # 重编译后烧录（编译有错误则跳过烧录）
```

## 环境要求

| 组件 | 必需性 | 说明 |
|---|---|---|
| DSH | 必需 | agent preset 宿主 |
| Python 3.8+ | 工具调用用 | stm32cli / map-parser |
| STM32CubeMX 数据库 | 仅 stm32cli 用 | `--db-path` 或环境变量 `STM32CUBEMX_DB_PATH` |
| Keil MDK (UV4) | 编译/烧录用 | 注册表自动探测，未安装则跳过编译功能 |
| 烧录器驱动 | 对应后端用 | ST-Link(CubeProgrammer) / CMSIS-DAP(pyocd) / J-Link |

## 仓库结构

```text
firmware-forge/
├── arm-cortex-expert/            # 固件设计/评审技能（SKILL.md + 分层参考 + Python 工具）
│   ├── references/               #   cores/ families/ lwip 等，按 CPU 型号按需加载
│   └── tools/
│       ├── stm32cli/             #   CubeMX 数据库查询 CLI
│       └── map-parser/           #   Keil .map 文件分析 CLI
├── embedded-test-engineer/       # 固件验证策略技能（测试金字塔/测试替身/数据回放/HIL）
├── embedded-protocol-designer/   # 设备协议设计技能（帧格式/命令空间/版本治理）
├── preset/                       # preset 元数据 + agent 组合文件
├── plugins/mdk/                  # /build 斜杠命令插件（mdk-commands.mjs）
├── scripts/mdk/                  # mdk.ps1 统一封装 + flash-backends.ps1 四后端 + 配置模板
├── docs/                         # 文档（人类阅读）：使用手册 + 编译/烧录 SOP
├── install.bat                   # Windows 双击安装入口（封装 install.ps1）
├── install.ps1                   # 一键安装/更新到 DSH
└── LICENSE                       # MIT
```

## 文档导航

| 想做什么 | 去哪 |
|---|---|
| 5 分钟装好、跑起来 | 本文件 · 快速开始 |
| 装好之后的日常：切换 preset、放技能、更新与卸载 | [docs/workbench-usage.md](docs/workbench-usage.md) |
| 编译/烧录的一切：探测优先级、多工程、四个后端、三个已知坑 | [docs/mdk-build-flash.md](docs/mdk-build-flash.md)（`/build` 权威参考） |
| 看懂某个技能的完整契约 | 各技能目录下的 `SKILL.md`，细节在 `references/` |
| 英文版说明 | [README.en.md](README.en.md) |

## 设计原则

- **薄入口 + 按需加载**：`SKILL.md` 只做路由，重内容放 `references/` 按 CPU 型号读取，不撑爆上下文
- **证据优先级**：项目代码/.ioc/链接脚本 > 厂商手册 > 技能参考 > 一般经验，推断必须声明
- **中间件只读**：HAL/RTOS/LwIP 内部默认不修改，走配置点、回调与 weak 覆盖
- **工具非权威**：stm32cli/map-parser 是加速器，输出与工程证据冲突时以工程为准

## License

本项目基于 [MIT License](LICENSE) 开源发布。
