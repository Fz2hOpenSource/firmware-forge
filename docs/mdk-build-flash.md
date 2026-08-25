# Keil MDK 编译/烧录 SOP

工作台通过一个统一脚本 `scripts/mdk/mdk.ps1` 封装 Keil UV4 的编译与烧录；`/build` 命令（带后缀）和 AI 的 shell 调用都走它。烧录后端（keil/stlink/dap/jlink）独立在 `scripts/mdk/flash-backends.ps1`。

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
2. **默认工程自动选中**：`$MdkDefaultProject = 'vibrating'`——多候选中按 uvprojx 文件名（不含扩展名）**唯一命中**则自动选中，否则仍报错列出。

安全底线：flash 不提供"全部烧录"模式，多 MCU 各自显式指定目标。

## 人怎么用（slash 命令）

一个命令 `/build`，加后缀切换动作：

- `/build`      —— 增量编译（默认，等同 `-b`）
- `/build -r`   —— 全量重编译
- `/build -f`   —— 烧录下载
- `/build -rf`  —— 全量重编译后烧录（重编译有错误则跳过烧录）

## AI 怎么用

AI 通过 PowerShell 工具调用同一个脚本（长编译放后台）：

```powershell
pwsh -File "$env:DSH_HOME\.agent-presets\embedded\scripts\mdk\mdk.ps1" build
pwsh -File "$env:DSH_HOME\.agent-presets\embedded\scripts\mdk\mdk.ps1" flash
```

## 原理与命令映射

运行日志统一写在安装根的 `logs\` 目录（`$DSH_HOME\.agent-presets\embedded\logs\`），**重装/更新不会丢失故障现场**；脚本每次启动自动清理 30 天前的旧日志，单文件按动作覆盖写，不会无限堆积。

| 动作 | UV4 命令 | 说明 |
|---|---|---|
| build | `UV4.exe -b <proj> -j0 -o logs\uv4-build.log` | 增量编译，无窗口，日志落盘 |
| rebuild | `UV4.exe -r <proj> -j0 -o logs\uv4-rebuild.log` | 全量重编译 |
| flash | 分发到烧录后端（见下） | keil 后端写 `logs\uv4-flash.log` |

## 三个已知坑

1. **UV4 退出码不可靠**：即使编译有 Error，UV4 也可能返回 0。所以编译成败以日志里的 `N Error(s)` / `N Warning(s)` 计数为准，不看退出码。
2. **编译慢**：几十秒到几分钟。slash 命令会同步等待；AI 侧应把 build 放后台任务跑，避免阻塞。
3. **Keil 烧录默认完全静默**：`-j0` 隐藏窗口且不回传结果。现在 flash 同样写日志 `uv4-flash.log`，成功判据为 `Verify OK / Programming Done / Load finished / Application running` 且无失败关键字；出现 `Error / failed / cannot / No Algorithm / Verify failed` 即失败并列出相关行，非零退出。

## 烧录后端（keil / stlink / dap / jlink）

`flash` 动作分发到 `scripts/mdk/flash-backends.ps1`，用 `$FlashBackend` 选择：

| 后端 | 工具 | 命令要点 | 本机状态 |
|---|---|---|---|
| `keil` | UV4.exe | `UV4 -f <proj> -j0`（工程配置的调试器） | ✅ |
| `stlink` | STM32_Programmer_CLI.exe | `-c port=SWD -w <hex> -v -rst` | ✅ 已装，自动探测 |
| `dap` | pyocd | `pyocd flash -t <target> <hex>` | ⚠️ 需 `pip install pyocd` |
| `jlink` | JLink.exe | CommanderScript：`loadfile <hex>` | ⚠️ 需装 SEGGER J-Link |

镜像 `.hex` 自动定位（工程输出目录取最新；你的工程 `<CreateHexFile>1</CreateHexFile>` 会生成 `MDK-ARM\ad7176\ad7176.hex`）。也可用 `-Image` 参数或 `$FlashImage` 手动指定。

切换后端：改 `mdk.config.ps1` 的 `$FlashBackend`，或命令行 `mdk.ps1 flash -Backend stlink`。

### 新增后端（分层，两步）

1. 在 `flash-backends.ps1` 的 `$FlashBackends` 加一行：`'名字' = 'Invoke-Flash名字'`
2. 写一个 `Invoke-Flash<名字>` 函数（约定参数 `-ProjectFile -Image`）：定位工具 → 拼命令 → 运行；失败 `Write-Error` + `exit 1`
