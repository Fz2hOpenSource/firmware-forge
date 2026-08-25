# DSH 嵌入式开发工作台：架构说明

本文件说明工作台如何把设计规则、工程证据与执行动作放在同一条可追溯的流程中。

## 分层

| 层 | 组件 | 职责 |
| --- | --- | --- |
| 装配层 | `preset/`、`install.ps1` | 向 DSH 注册 preset，并把技能、插件和脚本部署到本机。 |
| 规则层 | 三个 `SKILL.md` | 约束固件设计评审、验证策略与协议演进应如何决策。 |
| 证据层 | `stm32cli`、`map-parser` | 查询 CubeMX 数据库或已生成的 Keil map，给出可核验的工程事实。 |
| 执行层 | `/build`、`mdk.ps1`、烧录后端 | 在明确工程、Target、MCU 和后端后构建或烧录。 |

## 一次典型工作流

1. 从项目代码、`.ioc`、链接脚本、日志和厂商资料取得事实；它们永远优先于本工作台的规则或工具输出。
2. 用 `stm32cli` 补全芯片、DMA、引脚、时钟或中断信息；用 `map-parser` 分析已有产物。
3. 由技能选择最简单、仍能满足项目证据的架构，并保留 DMA、ISR、Cache、RTOS 等硬安全边界。
4. 需要时由验证或协议技能补齐测试策略、数据回放、通信契约与版本治理。
5. 最后才运行 `/build` 或 `flash`；烧录链路拒绝猜测多个工程或模糊的镜像目标。

这不是自动替代参考手册的流程。工具输出是缩小排查范围的线索；与项目或厂商资料冲突时，以后者为准。

## 边界

- 当前重点支持 Cortex-M / STM32、Windows、DSH 和 Keil MDK。
- 不进行 PCB、器件选型、电气参数或 EMC 设计。
- 不默认修改 HAL、RTOS、LwIP 等中间件内部；优先配置、回调、hook 和项目自有适配层。
- 构建和烧录是有副作用的动作，必须先确认目标；诊断、查询与评审应先使用只读路径。

## 如何扩展

### 新增技能

在仓库顶层创建技能目录及 `SKILL.md`，把名称加入 `install.ps1` 的 `$skillList`，再补齐对应 references 与结构校验。仅创建目录不会使技能随 preset 分发。

### 新增烧录后端

在 `scripts/mdk/flash-backends.ps1` 注册后端并实现约定函数。函数应先定位工具、显式验证镜像与目标、在失败时返回非零状态；不要把“自动猜测正确目标”当作易用性。

### 调整 DSH 组合

服务所在的 host 或 isolate realm 会影响跨 session 可见性与注册冲突。修改 `preset/agent.cordis.yml` 前，请阅读 [DSH 集成说明](dsh-integration.md)，并在目标 DSH 版本上做一次启动 smoke test。

## 维护检查

发布前至少运行：

```powershell
python -X utf8 scripts/validate_skills.py
python -X utf8 -m unittest discover -s arm-cortex-expert/tools/stm32cli/tests -v
node --check plugins/mdk/mdk-commands.mjs
```

还应在真实 DSH、CubeMX 数据库、Keil MDK 和烧录器环境中完成一条最小的查询、构建和烧录 smoke test。
