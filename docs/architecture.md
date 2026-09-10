# Firmware Forge：架构说明

当前提供 Codex 和 DSH 两种宿主入口；三个技能可独立使用，DSH 工作台提供可选的构建与烧录集成。项目按需求、设计、实现和验证组织工作，设计取舍见 [设计理念](design-philosophy.md)。

## 分层

| 层 | 组件 | 职责 |
| --- | --- | --- |
| 装配层 | `preset/`、`install.ps1` | 向 DSH 注册 preset，并把技能、插件和脚本部署到本机。 |
| 规则层 | 协议、固件、测试三个 `SKILL.md` | 分别负责公开交互契约、固件执行与资源归属、验证方法与证据边界；见 [技能分工](skills-integration.md)。 |
| 证据层 | `stm32cli`、`map-parser`、`check_state_model.py` | 分别提供芯片数据库查询、构建产物分析和抽象状态图检查。图检查不证明运行时收敛或硬件安全。 |
| 执行层 | `/build`、`/flash`、`mdk.ps1`、烧录后端 | 在明确工程、Target、MCU 和后端后构建或烧录。 |

## 一次典型工作流

1. 明确当前需求、失败行为和验收条件；扩展时检查变化及依赖。
2. 检查项目契约、代码、`.ioc`、链接脚本、日志和厂商资料。冲突需明确，不能用通用技能规则覆盖产品要求或硬件限制。
3. 按任务选择协议、固件或测试技能；真实等待才增加局部阶段和退出期限。
4. 需要芯片数据或已有产物证据时，使用 `stm32cli` / `map-parser` 并核对实际配置；纯协议讨论不要求这些工具。
   对已显式建模的等待/恢复，可按需用 `embedded-test-engineer/scripts/check_state_model.py` 检查结构出口与超时环；保持模型与实际实现的映射。
5. 执行相关验证，需要构建或烧录时使用 `/build`、`/flash`。烧录前明确工程、Target、MCU 和后端，记录未验证部分。

工具输出是核验线索，不能独立证明运行时正确性。需求、实际行为和厂商限制冲突时，保留证据并说明需要解决的差异。

## 边界

- 技能重点支持 Cortex-M / STM32、FreeRTOS 与设备交互；MDK 命令集成面向 Windows、DSH 和 Keil MDK。
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

技能整合及相关工具发布可运行以下检查；日常修改按 [贡献指南](../CONTRIBUTING.md) 选择与风险相称的范围：

```powershell
python -X utf8 scripts/validate_skills.py
python -X utf8 -m unittest discover -s arm-cortex-expert/tools/stm32cli/tests -v
python -m unittest discover -s embedded-test-engineer/tests -v
node --check plugins/mdk/mdk-commands.mjs
node --test plugins/mdk/tests/mdk-commands.test.mjs
```

修改对应集成行为或宣称支持新的环境时，还应在真实 DSH、CubeMX 数据库、Keil MDK 或烧录器上完成相关 smoke test，记录版本和结果。文档修改不要求安装或烧录设备，离线检查不能替代实机结论。
