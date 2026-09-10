# 安装与使用

[项目首页](../README.md) · [English quick start](../README.en.md) · [设计理念](design-philosophy.md)

先选**安装入口**，不必先选运行时技能：需要固件开发、测试验证或协议设计指导，安装相应技能；需要 DSH 内的 MDK 命令，再安装工作台；芯片查询、map 分析与状态图检查可以直接运行对应 Python 工具。装好后直接描述任务，由 AI 按内容自动选用技能/命令/工具；`$技能名` 显式点名是可选的。下面路径除明确说明外均相对本仓库根目录。

当前宿主支持范围为 **Codex 和 DSH**；其它宿主的安装适配与兼容性验证留待后续需求。

## 获取源码

```sh
git clone https://github.com/Fz2hOpenSource/firmware-forge.git
cd firmware-forge
```

源码根目录直接包含 `arm-cortex-expert/`、`embedded-protocol-designer/`、`embedded-test-engineer/`。只有安装到某个宿主后，它们才位于该宿主的 `skills/` 目录中。

<a id="codex"></a>
## 在 Codex 使用技能

新安装采用用户目录 `~/.agents/skills/`，或目标固件仓库的 `.agents/skills/`。显式点名技能或按任务自动选择的行为，以及更新后未出现时的重启处理，见 [OpenAI 官方技能文档](https://learn.chatgpt.com/docs/build-skills)（2026-09-10 复核）。

三个技能的 `agents/openai.yaml` 均允许隐式调用：在固件项目里用自然语言描述任务即可，AI 会按请求自动选用已安装技能；`$技能名` 显式点名仍可用于确认或强制路由。是否实际选中以输出和加载路径为准，选错时直接纠正任务描述或点名技能。

### 首次安装

将需要的完整技能目录复制到选定位置，保留 `SKILL.md`、`references/`、`agents/` 及其配套工具。无需复制本仓库的 DSH preset 或 MDK 插件。

Windows PowerShell 示例，在源码根目录运行。可缩减 `$skillNames`；目标已有同名目录时整体停止，不直接覆盖：

```powershell
$skillNames = @('arm-cortex-expert', 'embedded-protocol-designer', 'embedded-test-engineer')
$skillDestination = Join-Path $env:USERPROFILE '.agents\skills'
foreach ($name in $skillNames) {
  if (Test-Path -LiteralPath (Join-Path $skillDestination $name)) {
    throw "Skill already exists; compare and back up before updating: $name"
  }
}
New-Item -ItemType Directory -Force -Path $skillDestination | Out-Null
foreach ($name in $skillNames) {
  Copy-Item -LiteralPath (Join-Path (Get-Location).Path $name) -Destination $skillDestination -Recurse -ErrorAction Stop
}
```

macOS/Linux 可以按上述目录布局使用文件管理器复制。项目级安装则把目的地换为目标固件仓库的 `.agents/skills/`，按团队约定纳入版本管理。

### 验证加载

在目标固件项目打开 Codex，选择技能或输入：

```text
使用 $arm-cortex-expert。先读取技能，结合当前固件任务说明适用范围和需要查看的项目证据。
```

检查返回内容对应所选技能，并确认宿主显示/读取的技能路径。看不到时检查是否误复制成 `技能名/技能名/SKILL.md`，再重启宿主。已有安装可能使用宿主实际报告的其它目录；先确认现有来源，避免在多个位置装同名副本。路径存在和 AI 声称已使用，都不能替代对输出质量的检查。

### 更新与移除

更新前查看源码版本和本地差异，再获取目标版本。比较安装副本与源码，备份被替换文件并逐项合并，特别保留宿主专用工具和本地扩展。不要把 DSH 的 `install.ps1` 用于更新 Codex。

移除时确认宿主加载路径，删除自己安装的对应技能目录或按宿主提供的方式禁用，保留所需备份。不删除整个用户 `skills` 目录。

<a id="dsh"></a>
## 在 DSH 使用工作台

需要能够加载本仓库 `preset/agent.cordis.yml` 的 DSH 环境。当前 MDK slash 插件调用 Windows 的 `powershell.exe`；本仓库未提供跨 DSH 版本或跨平台认证矩阵。宿主安装与登录按其文档完成。

### 安装和启用

先了解安装范围：`install.ps1` 将工作台安装到 `$DSH_HOME/.agent-presets/embedded/`；未设置 `DSH_HOME` 时使用用户目录下 `.dsh/.agent-presets/embedded/`。

安装器会替换该工作台的 `plugins/`、`scripts/` 和三个技能目录，并移除其 `skills/` 中不在分发名单内的其它目录。它尝试保留已有 `scripts/mdk/mdk.config.ps1`，首次安装时由模板生成。其它定制内容应先备份，个人额外技能放在该受管目录以外、由宿主支持的位置。安装不是逐文件合并。

在源码根目录运行：

```powershell
./install.ps1
```

Windows 也可双击根目录的 `install.bat`，它调用同一安装器。编译成功后需要烧录时，再显式运行 `/flash`。

随后在 DSH 新建会话，选择「嵌入式开发工作台」。在固件工程目录使用技能，或调用：

| 命令 | 行为 |
|---|---|
| `/build` | 增量编译 |
| `/build -r` | 全量重编译 |
| `/build <昵称>` | 编译指定工程 |
| `/flash` | 使用已配置目标烧录 |
| `/flash <昵称>` | 烧录指定工程 |

Keil UV4、编译环境、工程和烧录工具需自行准备。脚本会尝试自动定位 UV4 和工程，但多个工程或非标准安装仍需指定配置。完整说明见 [MDK 编译/烧录](mdk-build-flash.md)。复制技能到 Codex 不会注册这些 slash 命令。

### 更新

查看本地差异和目标版本，备份受管目录中的定制内容，再更新源码并重跑安装器。开发者可使用 `./install.ps1 -Symlink` 让受管目录链接源码；Windows 需允许创建符号链接，安装目录中的编辑会影响对应源码，不适合作为独立定制副本。

<a id="example"></a>
## 按任务使用

以下入口相互独立；已有需求和接口可以直接作为输入。只加载相关技能，单独工具调用无需先完成整套设计流程。

### 外设与 DMA 排障

```text
使用 $arm-cortex-expert。STM32 + FreeRTOS 的 ADC DMA 偶发读到旧数据。
检查实际芯片、缓存与内存布局、buffer 归属和 ISR/任务交接。
先用项目证据定位原因，再做最小修复，保留现有通信接口。
```

重点是数据生命周期和目标证据；不因为项目有上位机就先改协议。底层 SPI/I2C 事务时序仍应按器件资料检查。

### DSP 优化与数值验证

```text
使用 $arm-cortex-expert。现有滤波器 CPU 占用过高，优化时保留项目规定的误差和延迟。
先检查算法、FPU、采样率和已有性能数据；需要回归时使用 $embedded-test-engineer。
```

```text
使用 $embedded-test-engineer，为现有滤波与标定链建立回放回归。
检查原始数据、时间/通道标记、参考结果和容差依据，复用现有测试设施。
```

预期输出是针对算法的修改或测试、数值比较和平台性能缺口。已有算法接口不变时无需额外协议设计。

### 存储与网络

```text
使用 $arm-cortex-expert。SPI Flash 写入期间采集偶发丢样。
检查总线占用、设备 busy 等待、任务调度和缓冲余量，保持持久化格式不变。
```

```text
使用 $arm-cortex-expert。LwIP 上传偶发 pbuf 泄漏。
检查当前 API 的线程上下文、pbuf 生命周期及失败路径，再提出最小修复。
```

重点是驱动、存储和网络栈边界；只有确实改变对外语义时才引入协议设计。

### 直接执行命令或工具

DSH 中 `/build <昵称>` 编译，`/build <昵称> -r` 重编译；需要烧录时单独使用 `/flash <昵称>`。具体目标选择与结果判定见 [MDK 指南](mdk-build-flash.md)。Codex 使用技能并不注册这些 DSH 命令。

芯片查询或已有 map 分析可以直接调用对应 CLI，先核对 `--help` 和输入文件，见下方 [工具试用](#tools)。命令失败时优先保留日志和定位原因，不据此展开无关协议设计。

### 协议专项协作：简单启停，再扩展多通道

以下是 AI 协作示例，未绑定真实设备时序或线格式。将已存在的需求文档、固件和上位机代码提供给 AI；没有的部分明确标记为待设计。

#### 定义当前交互行为

```text
使用 $embedded-protocol-designer。
STM32 + FreeRTOS，单上位机控制，当前只需要 START、STOP、STATUS。
STOP 同时停采集和上传；运行中不调参，断线后行为尚待确定。
后续可能扩展为同步多通道。先读取项目资料，区分已定需求与待确认项，
输出最小行为表、重复/失败语义及验收条件。这一步先设计。
```

检查结果是否说明：STOP 的完成点、重复 START/STOP、忙时输入、断线行为，以及无法确认实际效果时如何报告。同步调用是否有界应列为实现条件；不要仅因为未来多通道就接受一套新的请求框架。

#### 需要固件实现时

```text
使用 $arm-cortex-expert，按已确认的启停约定修改现有工程。
先检查状态写者、DMA/buffer 归属和 FPGA/驱动完成方式。
只对真实跨事件等待增加局部阶段和截止点，列出相关改动与验证结果。
```

预期交付是聚焦的实现，以及与驱动/硬件证据对应的完成和资源释放处理。若需求在现有硬件约束下无法实现，需明确冲突，而非静默改变对外语义。

#### 需要交互验证时

```text
使用 $embedded-test-engineer，为实际启停实现选择必要测试。
覆盖重复 STOP、完成丢失、停止超时和迟到回调等实际存在的机制。
区分 host 能检查的状态/资源行为与需要目标平台验证的时序。
```

验证应引用真实实现或与其有明确映射的逻辑。用例列出事件序列、期望效果和资源归属；无相关机制的项目不必建全套测试架构。

#### 多通道扩展时

同步八通道先考虑同一生命周期和通道配置；独立启停才需要通道局部实例。共享时钟、DMA、带宽与部分失败仍需明确约定。让 AI 输出本次受影响的命令、资源、兼容性和测试，不重写无关模块。

<a id="tools"></a>
## 工具试用

从源码根目录运行：

```sh
python embedded-test-engineer/scripts/check_state_model.py embedded-test-engineer/assets/reconfigure-model.json --json --strict
python embedded-test-engineer/scripts/check_state_model.py embedded-test-engineer/assets/stuck-model.json --json --strict
```

分别预期退出 `0` / `1`，后者是故意的恢复环。默认模式只因 error 失败；`--strict` 也因 warning 失败。机器读取退出码或 `gate_status`，`status` 保持结构检查含义。文件/JSON/参数错误退出 `2`。详细格式见 [状态图检查器](../embedded-test-engineer/references/state-model-format.md)。

芯片和 map 查询先查看本地帮助：

```sh
python arm-cortex-expert/tools/stm32cli/stm32cli.py --help
python arm-cortex-expert/tools/map-parser/map-parser.py --help
```

`stm32cli` 当前源码默认查找 `~/.stm32cubemx/databases`，可用 `--db-path` 或 `STM32CUBEMX_DB_PATH` 指向含 `DB.* / db / mcu` 层级的数据库父目录。缺少数据库时按项目 `.ioc` 和厂商资料继续，不把查询失败当作芯片不支持。不同安装版本的参数可能不同，使用 [工具参考](../arm-cortex-expert/references/tools-stm32cli.md) 与实际 `--help` 核对。

## 常见问题

| 现象 | 首先检查 |
|---|---|
| AI 没选技能 | 显式点名，核对宿主加载路径与 `SKILL.md` 层级 |
| 没有 `/build` | 是否在 DSH 中加载了工作台插件；普通技能安装不会注册命令 |
| 找不到 UV4 / 工程 | 工具安装、工作目录、`MDK_UV4` / `MDK_PROJECT` 或 `-Project` |
| 查询工具没有芯片数据 | 数据库层级和版本、实际 XML，不循环相信空结果 |
| 图检查通过但设备仍卡住 | guard、调度、队列、驱动阻塞和硬件效果不在图证明范围内 |
| 更新后规则似乎没变化 | 先排查同名副本和实际路径，再按宿主要求刷新 |

报告问题时附项目/技能版本、宿主、复现步骤、预期与实际结果及脱敏日志。见 [贡献指南](../CONTRIBUTING.md)。
