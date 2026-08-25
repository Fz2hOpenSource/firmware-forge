# 嵌入式开发工作台 · 使用说明

「嵌入式开发工作台」是一个 DSH **agent preset**（会话级组合），把嵌入式固件开发常用能力打包成一个可一键启用、可移植的工作台：不必在 DSH、Keil MDK、命令行之间来回切换。

## 它能做什么

- 内置技能：
  - `arm-cortex-expert` —— Cortex-M 固件设计/评审（DMA、ISR、缓存、RTOS、LwIP）。
  - `embedded-test-engineer` —— 固件验证策略（测试分层、测试替身、数据回放回归、HIL 规划）。
  - `embedded-protocol-designer` —— 设备通信协议设计与评审（帧格式、命令空间、状态门控、版本冻结）。
- 内置 Keil MDK 编译/烧录命令：`/build`（默认增量编译；`-r` 全量重编译、`-f` 烧录、`-rf` 重编译后烧录）。
- 其余能力与「标准模式」一致（文件编辑、Shell、检索、子代理、工作流等）。

## 安装（一次）

```powershell
cd 到本仓库根目录
.\install.ps1
```

安装脚本会把内容同步到 `$DSH_HOME\.agent-presets\embedded\`。**通常无需再配置**：UV4.exe 走注册表自动探测，工程 `.uvprojx` 从工作区自动搜索。仅当自动探测失败时才需要编辑 `$DSH_HOME\.agent-presets\embedded\scripts\mdk\mdk.config.ps1` 手动指定。

安装即镜像：仓库里已删除或改名的技能，其在安装目录 `skills\` 下的旧副本会被自动清理，不会继续暴露给会话。

## 启用

1. 打开 DSH，新建会话。
2. 在会话的 preset 菜单里选「嵌入式开发工作台」（选一次即记住为默认）。

## 更新

改了仓库后，重跑 `.\install.ps1` 即可（`git pull` + 重跑 = 更新）。
需要"改仓库即实时生效"时，用 `.\install.ps1 -Symlink`（Windows 需开发者模式/管理员）。

## 目录结构

```
dsh-embedded-workbench/
├── arm-cortex-expert/            # 技能（源）
├── preset/                       # preset 元数据 + 组合文件
│   ├── preset.yml
│   └── agent.cordis.yml
├── plugins/mdk/                  # 命令插件
│   └── mdk-commands.mjs          #   /build（-r / -f / -rf 后缀）
├── scripts/mdk/                  # 脚本封装
│   ├── mdk.ps1                   #   UV4 封装 + 日志解析
│   ├── flash-backends.ps1        #   烧录后端层（keil / stlink / dap / jlink）
│   └── mdk.config.ps1.example    #   本机配置模板
├── docs/                         # 文档（人类阅读，不进 AI 上下文）
└── install.ps1                   # 一键安装/更新
```

## 技能放哪（通用 vs 嵌入式专属）

进入嵌入式工作台后，技能目录是**叠加合并**的——其它技能不会消失。按用途放对位置：

| 用途 | 放哪 | 可见范围 |
|---|---|---|
| 通用技能（表格、文档、翻译等） | `~/.dsh/skills` 或 `~/.agents/skills` | 所有 preset（含嵌入式工作台） |
| 嵌入式专属技能 | 本仓库 `skills/`（随 preset 分发） | 仅嵌入式工作台 |

同名冲突时的优先级：项目级 > preset 自定义 > 用户级 > 内置。

> 设计原则：「薄入口 + 按需加载」。preset 文件与技能 `SKILL.md` 保持极小，只做路由；重内容放在 `references/`、`docs/`，按需读取。这样内容再多也不会撑爆上下文。
