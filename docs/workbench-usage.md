# 嵌入式开发工作台 · 日常使用手册

工作台是什么、怎么装、能做什么，见 [README](../README.md)；编译/烧录的一切见 [mdk-build-flash.md](mdk-build-flash.md)。本文只讲**装好之后**的事：preset 与会话、技能摆放、更新与卸载。

## 文档分工

| 需要回答的问题 | 文档 |
| --- | --- |
| 这个项目适不适合当前任务、如何第一次跑通 | [README](../README.md) |
| preset、技能放置、更新与卸载 | 本文 |
| 工程选择、镜像定位与烧录后端 | [MDK 编译/烧录 SOP](mdk-build-flash.md) |
| 工作台的分层、边界与扩展 | [架构说明](architecture.md) |
| DSH host / isolate realm 与组合维护 | [DSH 集成说明](dsh-integration.md) |


## Preset 与会话

- 工作台是一个 DSH **agent preset**（会话级组合）。新建会话时在 preset 菜单选「嵌入式开发工作台」，选一次即记住为默认，之后的新会话自动沿用，直到你改选其它 preset；想切回来，菜单里再选一次即可，无需重装。
- preset 是**叠加合并**的：进入本工作台不会关掉其它能力——文件编辑、Shell、检索、子代理、工作流等与「标准模式」一致，用户级全局技能也仍然可见。

## 技能放哪（通用 vs 嵌入式专属）

| 用途 | 放哪 | 可见范围 |
|---|---|---|
| 通用技能（表格、文档、翻译等） | `~/.dsh/skills` 或 `~/.agents/skills` | 所有 preset（含本工作台） |
| 嵌入式专属技能 | 本仓库顶层新建 `<skill-name>/` 目录 | 仅本工作台 |

嵌入式专属技能的分发规则：

- 内置三个技能（`arm-cortex-expert`、`embedded-test-engineer`、`embedded-protocol-designer`）就在仓库**顶层目录**，安装时由 install.ps1 同步到安装目录的 `skills\` 下随 preset 分发。
- 新增自定义嵌入式技能：仓库顶层建好目录后，把名字加进 `install.ps1` 的 `$skillList` 再重跑安装。**没进 `$skillList` 的目录不会分发**，且安装目录 `skills\` 里不在名单中的残留目录会在下次安装时被镜像清理自动删除。
- 同名冲突优先级：项目级 > preset 自定义 > 用户级 > 内置。

> 设计取向（薄入口 + 按需加载）：技能 `SKILL.md` 保持极小只做路由，重内容放各自 `references/`，按需读取不撑爆上下文。

## 更新与卸载

- **更新**：`git pull` 后重跑 `.\install.ps1`（或再次双击 `install.bat`）。安装是镜像式整树替换，但两件事有特殊处理：本机配置 `scripts\mdk\mdk.config.ps1` 会被自动备份并在装完后恢复（没有则从模板生成）；仓库里已删除或改名的技能，其安装目录下的旧副本会被自动清理——不会继续暴露给会话。
- **实时生效**：开发期用 `.\install.ps1 -Symlink`（Windows 需开发者模式或管理员），改仓库即刻反映到安装目录。
- **卸载**：删除 `$DSH_HOME\.agent-presets\embedded\` 整个目录即可；运行日志也在其中（`logs\` 子目录），随之一起移除。
