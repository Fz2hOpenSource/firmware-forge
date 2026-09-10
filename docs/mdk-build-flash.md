# Keil MDK 编译/烧录 SOP

工作台通过统一脚本 `scripts/mdk/mdk.ps1` 封装 Keil UV4 的编译与烧录。`/build`、`/flash` 两个 slash 命令，以及 AI 的 shell 调用，都走这个脚本。本文是这两个命令的权威参考。烧录后端（keil/stlink/dap/jlink）实现在 `scripts/mdk/flash-backends.ps1`。

工作台总览与快速开始见 [README](../README.md)；安装后的日常管理见 [workbench-usage.md](workbench-usage.md)。

## 配置

`mdk.ps1` 默认自动探测，优先级如下：

1. **UV4.exe**：`MDK_UV4` 环境变量 → `mdk.config.ps1` 中的 `$Uv4Path` → 注册表（`HKLM\SOFTWARE\WOW6432Node\Keil\Products\MDK` 的 `Path`）→ 常见路径 `C:\Keil_v5\UV4\UV4.exe`。均未命中则报错。
2. **工程 .uvprojx**：从当前目录（slash 命令会传入会话工作区）只向下递归搜索 `*.uvprojx`（默认 6 层深，`-SearchDepth` 可调；不向上爬父目录）。唯一命中则选中；多个候选则报错，需用 `-Project` 指定。

自动探测失败时（非标准安装路径，或工程不在工作区），编辑 `$DSH_HOME\.agent-presets\embedded\scripts\mdk\mdk.config.ps1`：

```powershell
$Uv4Path     = ''   # 留空=自动探测；手动填：'C:\Keil_v5\UV4\UV4.exe'
$ProjectPath = ''   # 留空=自动搜索；手动填：'C:\path\to\project.uvprojx'
$FlashBackend = 'keil'   # keil | stlink | dap | jlink
```

也可用环境变量 `MDK_UV4` / `MDK_PROJECT` 临时覆盖，不落盘。

## 多 MCU 工程（一个仓库多个 .uvprojx）

向下递归发现多个工程时，默认报错并列出候选。两种消歧方式都配置在 `mdk.config.ps1`：

1. **工程昵称表**（推荐）：

   ```powershell
   $MdkProjects = @{
     'main'   = 'firmware\MCU_Code\main\MDK-ARM\main.uvprojx'    # 相对工作区
     'sensor' = 'firmware\MCU_Code\sensor\MDK-ARM\sensor.uvprojx'
   }
   ```

   之后使用 `-Project main`。未知昵称会报错，并提示可用昵称。
2. **默认工程自动选中**：设置 `$MdkDefaultProject = 'main'`。多候选中按 uvprojx 文件名（不含扩展名）唯一命中时自动选中；否则仍报错列出。

烧录不提供“全部烧录”模式；多 MCU 工程必须各自显式指定目标。

## slash 命令用法

`/build` 只负责编译，`/flash` 只负责烧录。烧录始终是一次显式决定。

| 命令 | 动作 |
|---|---|
| `/build` | 增量编译 |
| `/build -r` | 全量重编译 |
| `/build <昵称>` | 编译指定工程 |
| `/flash` | 烧录下载 |
| `/flash <昵称>` | 烧录指定工程 |

不带昵称时：唯一工程自动选中；多工程报错并列出候选与可用昵称。烧录没有“先编译”链式开关。先执行 `/build` 并确认成功，再执行 `/flash`。

slash 插件向包装脚本传入 `-WaitTimeoutSec 900`，外层等待为 960 秒，为 UV4 的超时处理与结果收集留出余量。直接调用脚本时可另设 `-WaitTimeoutSec`。该参数约束 UV4 等待，不限制其它烧录后端的内部等待。外层中断时会报告结果不确定；需核对进程、日志和目标状态后再决定是否重试。

## AI 调用方式（shell 工具）

AI 通过 PowerShell 工具调用同一脚本。长编译应放入后台任务：

```powershell
$workbenchHome = if ($env:DSH_HOME) { $env:DSH_HOME } else { Join-Path $env:USERPROFILE ".dsh" }
$mdkScript = Join-Path $workbenchHome ".agent-presets\embedded\scripts\mdk\mdk.ps1"
& $mdkScript build
# 确认构建成功及烧录目标后，单独执行：
& $mdkScript flash
```

## 原理与命令映射

UV4 的 `-o` 只接受相对工程目录的文件名；传入绝对路径时，目录部分会被丢弃。因此脚本让 UV4 把日志写进工程目录，解析后再归档到安装根的 `logs\` 目录（`$DSH_HOME\.agent-presets\embedded\logs\`）。安装器会保留该日志目录，但日志不构成永久历史归档；归档目录每次启动自动清理 30 天前的旧文件，单文件按动作覆盖写。

| 动作 | UV4 命令 | 说明 |
|---|---|---|
| build | `UV4.exe -b <proj> -j0 -o uv4-build.log` | 日志落在工程目录，脚本读取判定后归档到 `logs\` |
| rebuild | `UV4.exe -r <proj> -j0 -o uv4-rebuild.log` | 同上 |
| flash | 分发到烧录后端（见下） | keil 后端同理（`uv4-flash.log`） |

## 五个已知问题

1. **UV4 退出码不可靠**：即使编译有 Error，UV4 也可能返回 0。编译成败以日志里的 `N Error(s)` / `N Warning(s)` 计数为准，不看退出码。
2. **编译较慢**：几十秒到几分钟。slash 命令会同步等待；AI 侧应把 build 放入后台任务，避免阻塞。
3. **Keil 烧录默认完全静默**：`-j0` 隐藏窗口且不回传结果。flash 同样写日志 `uv4-flash.log`。成功判据为 `Verify OK / Programming Done / Load finished / Application running` 且无失败关键字；出现 `Error / failed / cannot / No Algorithm / Verify failed` 即失败，并列出相关行，非零退出。
4. **UV4 的 `-o` 忽略绝对路径中的目录部分**：`-o C:\...\logs\uv4-build.log` 实际会把日志写到 `<工程目录>\uv4-build.log`。编译本身每次正常执行，但包装脚本在集中日志目录等不到文件，会误报“结果不确定”。处理方式即上文的两段式：只向 `-o` 传裸文件名，从工程目录读取，解析后归档。
5. **UV4.exe 是 GUI 子系统进程**：shell 的 `&` 不会等待它结束。脚本启动 UV4 后会立即继续，此时 `$LASTEXITCODE` 为空、日志尚未生成，会误报“结果不确定”。Keil 文档要求使用 `START /WAIT`。包装脚本改用 `Start-Process -PassThru` 获取进程，再用 `WaitForExit` 有限等待（`-WaitTimeoutSec` 可调，默认 900 秒；超时杀进程并按“结果不确定”退出，避免许可证弹窗挂死会话）。

## 烧录后端（keil / stlink / dap / jlink）

`flash` 动作分发到 `scripts/mdk/flash-backends.ps1`，由 `$FlashBackend` 选择：

| 后端 | 工具 | 命令要点 | 依赖 |
|---|---|---|---|
| `keil` | UV4.exe | `UV4 -f <proj> -j0 -o uv4-flash.log`（日志在工程目录，脚本归档；使用工程配置的调试器，成败按日志判定） | Keil MDK |
| `stlink` | STM32_Programmer_CLI.exe | `-c port=SWD -w <hex> [-addr] -v -rst` | STM32CubeProgrammer |
| `dap` | pyocd | `pyocd flash -t <target> [--base-address <addr>] <hex>`；需配置 `$DapTarget` | pyocd |
| `jlink` | JLink.exe | CommanderScript：`loadfile <hex> [addr]`；需配置 `$JlinkDevice` | SEGGER J-Link |

镜像自动定位规则：优先使用所选工程的 Target 输出目录；只认 `.hex/.axf`。命中多个候选会报错并列出，可用 `-Image` 指定其一。`.bin` 没有内嵌地址，必须显式 `-Image` 且配 `-FlashAddress`。也可用 `$FlashImage` 固定镜像。

切换后端：修改 `mdk.config.ps1` 的 `$FlashBackend`，或命令行 `mdk.ps1 flash -Backend stlink`。

### 新增后端

1. 在 `flash-backends.ps1` 的 `$FlashBackends` 加一行：`'名字' = 'Invoke-Flash名字'`
2. 编写 `Invoke-Flash<名字>` 函数（约定参数 `-ProjectFile -Image -ImageDir -FlashAddress`）：定位工具、拼命令、运行；失败时 `Write-Error` 并 `exit 1`。
