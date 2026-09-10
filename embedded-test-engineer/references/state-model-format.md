# 有限状态图检查器 v1

路径以本技能根目录为基准：

```text
python scripts/check_state_model.py assets/reconfigure-model.json --json
python scripts/check_state_model.py assets/stuck-model.json --json
python scripts/check_state_model.py assets/reconfigure-model.json --json --strict
```

只需 Python 3.10+ 标准库。路径有空格时按 shell 规则加引号；不要求当前目录恰好是项目根目录。

## 输入结构

JSON UTF-8，可带 BOM。顶层必须有 `version: 1`、`initial`、`states`、`transitions`，可选 `description`。拒绝重复 JSON key 和未声明字段，防止拼写错误静默失效。最多 1000 状态、20000 普通迁移。

`states` 是状态名到对象的映射：

| 字段 | 约束 |
|---|---|
| kind | stable / transient / terminal |
| timeout | 只用于 transient；`after_ms` 是正整数，`to` 是已声明状态 |
| description / source_ref | 可选非空文本；source_ref 用于映射源码或规范 |

transient 缺少 timeout 是语义错误而非格式错误。stable 表示可长期驻留的业务边界，terminal 表示本次请求结束，不允许出边。想表达下一次请求，用 stable 或另一个请求模型。**不要仅改 kind 来掩盖实际临时等待**。持续服务和硬件保护属于不同模型，terminal 不代表它们已停止。

`transitions` 是对象数组：必须包含 `from/event/to` 非空字符串；可选 `guard/source_ref`。from/to 必须已声明。同一源的 event 唯一；有条件分支时将 event 标成带条件的不同抽象事件，或显式展开状态。`@timeout` 是工具保留事件，由 state.timeout 自动生成，不能手写普通迁移冒充。

guard 只是标签，**不执行、不检查互斥或可满足性**；出现 guard 会报告 `GUARDS_ABSTRACTED`。没有列出的事件不在模型中，工具不知道它们是忽略、拒绝还是漏处理。

## 检查内容

| 代码 | 级别 | 意义 |
|---|---|---|
| MISSING_TIMEOUT | error | 临时状态未声明 timeout fallback，即使存在完成出边也报错 |
| TERMINAL_OUTGOING | error | 一次请求的终态仍能转移，可能反转历史结果 |
| NO_BOUNDARY_PATH | error | 可达临时状态没有到稳定/终态边界的路径 |
| TIMEOUT_CYCLE | error | 可达的纯超时链反复进入相同状态，存在无限恢复环 |
| TRANSIENT_CYCLE | warning | 临时状态子图中存在循环，需要外部预算/守卫/调度证明 |
| UNREACHABLE | warning | 从 initial 不可达，可能遗漏入口或无效声明 |
| GUARDS_ABSTRACTED | warning | guard 被当作可能为真，不能由图可达性证明实现可达性 |

结构契约（如缺 timeout）检查全部声明状态；路径和恢复环从 initial 的可达集检查。修复不可达入口后应重跑。SCC 循环警告包含自循环，也可能对应设计正确的有限重试；把剩余次数显式展开，或在审查中提交真正不续命的总 deadline 与调度证据，不要删除实有的循环边来通过检查。

输出 `witness` 是从 initial 到问题状态的最短抽象事件路径；TIMEOUT_CYCLE 另有 cycle。路径忽略 guard，不能当成已经在固件复现的执行轨迹。

`timeout_chain_budgets` 对可达 transient 计算“此时起只触发 timeout”到首个边界的声明等待毫秒之和。它**不含 action、调度延迟和其他事件循环**，既不保证整条操作时长，也不能当安全响应实测值。若链缺出口或循环，不给该起点的有限预算。

## 退出码与限制

- `0`：结构检查没有 error；warning 仍须解释。
- `1`：模型有效但有结构 error。
- `2`：文件/JSON/输入契约错误或 CLI 参数错误。

可选 `--strict` 在有 warning 时也返回 `1`，用于需要人工解释警告后才能放行的流程。
JSON 的 `status` 仍表示结构 error 的检查结果；`gate_status` 表示本次门禁是否通过，
`warnings_as_errors` 标明模式。自动化读取退出码或 `gate_status`，不能只看 `status`。
严格模式不增加证明能力；不要为了放行删掉真实循环或 guard。对合理警告保留独立审查依据，
按项目流程处理，不强制所有项目启用严格模式。

这个工具不是运行时状态机、C/RTL 检查器或完整模型检查器。它不证明请求去重、观测有效性、deadline 投递/执行、事件穷尽、资源释放、全局 operation budget、CDC 或物理安全。示例中 `MATCHING_*` 事件名声明已经关联验证，但工具不执行关联逻辑。

复杂场景用明确的组合模型或 TLA+/Spin 等验证 guard、计数器、队列和公平性；把工具失败及其修复保留为回归测试，再以目标平台故障注入验证时序。仅有图上的出口时，结论应写为“结构存在出口，实际收敛待验证”。
