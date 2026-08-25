# DSH preset 集成说明

`preset/agent.cordis.yml` 是工作台的运行时装配文件；它不是用户手册，也不应成为 Cordis 生命周期细节的唯一载体。本文件记录维护时必须理解的约束。

## 文件职责

| 文件 | 面向对象 | 职责 |
| --- | --- | --- |
| `preset/preset.yml` | DSH 使用者 | preset 菜单显示的名称与一句话定位。 |
| `preset/agent.cordis.yml` | DSH 与维护者 | persona、工具、技能、插件及 per-agent 服务的声明。 |
| `install.ps1` | Windows 使用者 | 把 preset 及其随附内容同步到 `$DSH_HOME\.agent-presets\embedded`。 |

## host 与 isolate realm

DSH 的注册表、sandbox、审批栈、模型路由和跨 session provider 属于 host。它们必须被本 preset 消费，而不是在 preset 内重新提供。反之，plan mode、compaction 与 workflow engine 是 agent 私有状态，放在 entry-local `isolate` realm。

| 位置 | 这里的例子 | 原因 |
| --- | --- | --- |
| host | shell、filesystem、jobs、skills、goals、Web、subagent registry | 这些服务在 session 外已经存在，重复注册会冲突或不可见。 |
| isolate | `planMode`、`compaction`、`toolResultPruner`、`workflowEngine` | 这些状态应随 agent 独立存在，避免不同 session 相互污染。 |

维护规则：

- 新增的只是模型侧工具时，优先复用 host 注册表。
- 新增持久或状态型服务时，先确认它是否必须跨 session 可见；只有 agent 私有状态才放进 `isolate`。
- provider 在 host 可用，不表示该 provider 自动暴露给本 preset；可选 provider 应维持显式 `disabled` 状态。

## Persona 契约

persona 只规定工作方式：何时加载哪个技能、证据优先级、烧录前确认目标，以及长编译应后台执行。工具参数、格式细节和安全检查应由各自的 `SKILL.md`、插件或脚本承担，避免 persona 变成第二份不一致的操作手册。

## 更新与兼容性

修改 DSH 组合后，在发布前完成以下检查：

1. 用目标 DSH 版本启动 preset，确认没有 service registration / realm 冲突。
2. 确认三个技能可见，`/build` 已注册，Windows 与非 Windows 的 shell 开关符合预期。
3. 记录测试过的 DSH 版本与已知限制；`@deepseek-ai/dsh-*` 服务名或生命周期语义变化时，优先更新此文档和 smoke test。

本仓库目前不宣称跨 DSH 版本的永久兼容性。升级 DSH 后，应先进行一次最小 smoke test，再向使用者推荐更新。
