# Keil MDK 编译/烧录 SOP

工作台通过一个统一脚本 `scripts/mdk/mdk.ps1` 封装 Keil UV4 的编译与烧录；`/build` 命令（带后缀）和 AI 的 shell 调用都走它。烧录后端（keil/stlink/dap/jlink）独立在 `scripts/mdk/flash-backends.ps1`。

> 分工说明：本文是 `/build` 与编译/烧录的**唯一权威参考**。工作台总览与快速开始见 [README](../README.md)；装好之后的日常管理（preset 切换、技能摆放、更新卸载）见 [workbench-usage.md](workbench-usage.md)。

## 配置（通常无需手动配，自动探测）

`mdk.ps1` 会**自动探测**，优先级如下：

1. **UV4.exe**：注册表（`HKLM\SOFTWARE\WOW6432Node\Keil\Products\MDK` 的 `Path`）→ 常见路径 `C:\Keil_v5\UV4\UV4.exe` → 都找不到才报错。
2. **工程 .uvprojx**：从当前目录（slash 命令会传入会话工作区）**只向下递归搜索** `*.uvprojx`（默认 6 层深，`-SearchDepth` 可调；不向上爬父目录，避免误抓工作区之外的工程）；唯一命中就用它，多个则报错让你用 `-Project` 指定。

只有自动探测失败（非标准安装路径、工程不在工作区）时，才需要编辑 `$DSH_HOME\.agent-presets\embedded\scripts\mdk\mdk.config.ps1`：

```powershell
$Uv4Path     = ''   # 留空=自动探测；手动填：'C:\Keil_v5\UV4\UV4.exe'
$ProjectPath = ''   # 留空=自动搜索；手动填：'C:\path\to\project.uvprojx'
$FlashBackend = 'keil'   # keil | stlink | dap | jlink
```

也可用环境变量 `MDK_UV4` / `MDK_PROJECT` 临时覆盖（不落盘）。

## 多 MCU 工程（一个仓库多个 .uvprojx）

向下递归发现**多个**工程时默认报错并列出候选，两种消歧方式（都在 `mdk.config.ps1` 配置）：

1. **工程昵称表**（推荐）：

   ```powershell
   $MdkProjects = @{
     'main'   = 'firmware\MCU_Code\main\MDK-ARM\main.uvprojx'    # 相对工作区
     'sensor' = 'firmware\MCU_Code\sensor\MDK-ARM\sensor.uvprojx'
   }
   ```

   之后 `-Project main` 即可；未知昵称报错并提示可用昵称。
2. **默认工程自动选中**：`$MdkDefaultProject = 'main'`——多候选中按 uvprojx 文件名（不含扩展名）**唯一命中**则自动选中，否则仍报错列出。

安全底线：flash 不提供"全部烧录"模式，多 MCU 各自显式指定目标。

## slash 命令用法（/build 后缀）

一个命令 `/build`，加后缀切换动作：

- `/build`      —— 增量编译（默认，等同 `-b`）
- `/build -r`   —— 全量重编译
- `/build -f`   —— 烧录下载
- `/build -rf`  —— 全量重编译后烧录（重编译有错误则跳过烧录）

## AI 调用方式（shell 工具）

AI 通过 PowerShell 工具调用同一个脚本（长编译放后台）：

```powershell
pwsh -File "$env:DSH_HOME\.agent-presets\embedded\scripts\mdk\mdk.ps1" build
pwsh -File "$env:DSH_HOME\.agent-presets\embedded\scripts\mdk\mdk.ps1" flash
```

## 原理与命令映射

日志分两段：UV4 的 `-o` 只接受**相对工程目录的文件名**（传绝对路径时目录部分被丢弃，见已知坑 4），所以脚本让 UV4 把日志直接写进**工程目录**，解析完再归档一份到安装根的 `logs\` 目录（`$DSH_HOME\.agent-presets\embedded\logs\`）——**重装/更新不会丢失故障现场**；归档目录每次启动自动清理 30 天前的旧文件，单文件按动作覆盖写，不会无限堆积。

| 动作 | UV4 命令 | 说明 |
|---|---|---|
| build | `UV4.exe -b <proj> -j0 -o uv4-build.log` | 日志落在工程目录，脚本读取判定后归档到 `logs\` |
| rebuild | `UV4.exe -r <proj> -j0 -o uv4-rebuild.log` | 同上 |
| flash | 分发到烧录后端（见下） | keil 后端同理（`uv4-flash.log`） |

## 四个已知坑

1. **UV4 退出码不可靠**：即使编译有 Error，UV4 也可能返回 0。所以编译成败以日志里的 `N Error(s)` / `N Warning(s)` 计数为准，不看退出码。
2. **编译慢**：几十秒到几分钟。slash 命令会同步等待；AI 侧应把 build 放后台任务跑，避免阻塞。
3. **Keil 烧录默认完全静默**：`-j0` 隐藏窗口且不回传结果。现在 flash 同样写日志 `uv4-flash.log`，成功判据为 `Verify OK / Programming Done / Load finished / Application running` 且无失败关键字；出现 `Error / failed / cannot / No Algorithm / Verify failed` 即失败并列出相关行，非零退出。
4. **UV4 的 `-o` 忽略绝对路径中的目录部分**：`-o C:\...\logs\uv4-build.log` 实际会把日志写到 `<工程目录>\uv4-build.log`。症状是编译本身每次都正常执行，但包装脚本在集中日志目录永远等不到文件，误报"结果不确定"。修法即上文的两段式：只向 `-o` 传裸文件名、从工程目录读取、解析后归档。

## 烧录后端（keil / stlink / dap / jlink）

`flash` 动作分发到 `scripts/mdk/flash-backends.ps1`，用 `$FlashBackend` 选择：

| 后端 | 工具 | 命令要点 | 依赖 |
|---|---|---|---|
| `keil` | UV4.exe | `UV4 -f <proj> -j0 -o uv4-flash.log`（日志在工程目录，脚本归档；工程配置的调试器，成败按日志判定） | Keil MDK |
| `stlink` | STM32_Programmer_CLI.exe | `-c port=SWD -w <hex> [-addr] -v -rst` | STM32CubeProgrammer |
| `dap` | pyocd | `pyocd flash -t <target> [--base-address <addr>] <hex>`；需配置 `$DapTarget` | pyocd |
| `jlink` | JLink.exe | CommanderScript：`loadfile <hex> [addr]`；需配置 `$JlinkDevice` | SEGGER J-Link |

镜像自动定位规则：优先使用所选工程的 Target 输出目录；只认 `.hex/.axf`，命中多个候选会报错并列出（用 `-Image` 指定其一）。`.bin` 没有内嵌地址——必须显式 `-Image` 且配 `-FlashAddress`。也可用 `$FlashImage` 固定镜像。

切换后端：改 `mdk.config.ps1` 的 `$FlashBackend`，或命令行 `mdk.ps1 flash -Backend stlink`。

### 新增后端（分层，两步）

1. 在 `flash-backends.ps1` 的 `$FlashBackends` 加一行：`'名字' = 'Invoke-Flash名字'`
2. 写一个 `Invoke-Flash<名字>` 函数（约定参数 `-ProjectFile -Image -ImageDir -FlashAddress`）：定位工具 → 拼命令 → 运行；失败 `Write-Error` + `exit 1`
