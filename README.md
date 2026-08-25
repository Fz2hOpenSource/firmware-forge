# DSH Embedded Workbench（嵌入式开发工作台）

面向 **Cortex-M / STM32 固件开发**的 [DSH](https://github.com/deepseek-ai) agent preset：把固件设计评审技能、芯片数据库查询工具、Keil map 分析工具和 MDK 编译/烧录命令打包成一个可一键启用的工作台，在 DSH 会话里完成"设计 → 编码 → 编译 → 烧录 → 调试"的完整闭环。

## 它能做什么

| 能力 | 说明 |
|---|---|
| 🧠 固件设计/评审技能 | `arm-cortex-expert`：DMA 管道、ISR/任务边界、中断优先级、缓存一致性、RTOS 任务架构、驱动分层、LwIP/以太网集成 |
| 🧪 固件验证技能 | `embedded-test-engineer`：测试分层策略、测试替身与接缝、测量数据回放回归、容差判定、HIL 覆盖规划 |
| 📡 协议设计技能 | `embedded-protocol-designer`：RS-485/UART/CAN 设备通信协议设计与评审——帧格式、命令空间、状态门控、超时重传、版本冻结治理 |
| 🔩 复杂度阶梯方法论 | 从裸机超循环到 DMA 双缓冲，六级停点按证据逐级升级，避免过度设计；硬安全边界不可妥协 |
| 🔍 stm32cli | 查询 CubeMX 数据库：芯片能力、外设、DMA 请求映射、引脚复用、时钟树、中断向量 |
| 🗺️ map-parser | 解析 Keil `.map` 文件：符号查找、内存区域分析、HardFault 定位、体积排名、MPU 对齐检查 |
| ⚙️ `/build` 命令 | 一条命令完成 UV4 编译（`-r` 全量）/ 烧录（`-f`，支持 keil/stlink/dap/jlink 四后端）/ 重编译后烧录（`-rf`） |

## 仓库结构

```text
├── arm-cortex-expert/            # 技能（SKILL.md + 分层参考 + Python 工具）
│   ├── references/               #   cores/ families/ lwip-ethernet 等，按 CPU 按需加载
│   └── tools/
│       ├── stm32cli/             #   CubeMX 数据库查询 CLI
│       └── map-parser/           #   Keil .map 文件分析 CLI
├── embedded-test-engineer/       # 技能（固件验证策略：测试金字塔/测试替身/数据回放/HIL）
├── embedded-protocol-designer/   # 技能（设备协议设计：帧格式/命令空间/版本治理）
├── preset/                       # DSH agent preset 元数据与组合文件
├── plugins/mdk/                  # /build 斜杠命令插件
├── scripts/mdk/                  # mdk.ps1 统一封装 + 四烧录后端 + 配置模板
├── docs/                         # 使用说明与编译/烧录 SOP
└── install.ps1                   # 一键安装/更新到 DSH
```

## 快速开始

### 1. 安装（一次）

```powershell
git clone <本仓库>
cd <仓库目录>
.\install.ps1          # 同步到 $DSH_HOME\.agent-presets\embedded\
.\install.ps1 -Symlink # 开发模式：改仓库即生效（需开发者模式/管理员）
```

通常**无需任何配置**：UV4.exe 走注册表自动探测，工程 `.uvprojx` 从会话工作区自动搜索。仅当自动探测失败时才编辑 `$DSH_HOME\.agent-presets\embedded\scripts\mdk\mdk.config.ps1`。

### 2. 启用

在 DSH 新建会话，preset 菜单选择「嵌入式开发工作台」。

### 3. 使用

对 AI 直接说需求即可，例如：

- 「评审这段 SPI+DMA 接收代码的缓存一致性」（M7/H7 场景会自动加载对应参考）
- 「查一下 STM32H723 的 SPI1 RX 走哪个 DMA」→ 内部调用 `stm32cli`
- 「这个 HardFault，PC=0x0800b455，帮我定位」→ 内部调用 `map-parser fault`

编译/烧录用斜杠命令：

```text
/build        增量编译（默认）
/build -r     全量重编译
/build -f     烧录下载
/build -rf    全量重编译后烧录（编译失败则跳过烧录）
```

## 环境要求

| 组件 | 必需性 | 说明 |
|---|---|---|
| DSH | 必需 | agent preset 宿主 |
| Keil MDK (UV4) | 编译/烧录用 | 注册表自动探测，未安装则跳过编译功能 |
| Python 3.8+ | 工具调用用 | stm32cli / map-parser |
| STM32CubeMX 数据库 | 仅 stm32cli 用 | 通过 `--db-path` 或环境变量 `STM32CUBEMX_DB_PATH` 指定 |
| 烧录器驱动 | 对应后端用 | ST-Link(CubeProgrammer) / CMSIS-DAP(pyocd) / J-Link |

## 设计原则

- **薄入口 + 按需加载**：`SKILL.md` 只做路由，重内容放 `references/` 按 CPU 型号读取，不撑爆上下文
- **证据优先级**：项目代码/.ioc/链接脚本 > 厂商手册 > 技能参考 > 一般经验，推断必须声明
- **中间件只读**：HAL/RTOS/LwIP 内部默认不修改，走配置点、回调与 weak 覆盖
- **工具非权威**：stm32cli/map-parser 是加速器，输出与工程证据冲突时以工程为准

详细说明见 [docs/workbench-usage.md](docs/workbench-usage.md)、[docs/mdk-build-flash.md](docs/mdk-build-flash.md)，技能全文见 [arm-cortex-expert/SKILL.md](arm-cortex-expert/SKILL.md)。

English documentation: [README.en.md](README.en.md)

## License

本项目基于 [MIT License](LICENSE) 开源发布。
