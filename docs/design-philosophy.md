# 设计理念：简单开发，有界失败，局部扩展

Firmware Forge 为 AI 和工程师提供共同的判断依据：在 STM32、FreeRTOS、FPGA 和上位机协作中，让小功能容易实现，让复杂功能仍能解释、维护和验证。

> 可靠性优化应让失败更可控，而不是让正常开发越来越复杂。

本文解释项目取舍；具体设计和实现规则由三个技能维护。它不规定所有设备使用相同的状态数量、协议格式或框架。

## 1. 先确定行为，再决定结构

先说清谁发起交互、命令承诺什么、失败时允许怎样处理，以及怎样验收。例如“停止读取”可能是停止采样、停止发包或两者都停；没有这项约定，任何漂亮的状态图都可能实现错需求。

需求可以分阶段确定：落实当前版本，记录未决定的问题和扩展边界。无需预先穷尽产品全部未来能力；后续变化要能指出受影响的约定和代码。

## 2. 选择最小足够方案

清楚且有界的函数、一个状态所有者和一张短表可能已足够。真实异步等待出现时增加局部阶段；独立生命周期出现时拆分状态域；反复出现稳定共性时再提取公共组件。

保持已有工程中满足要求的 RTOS、DMA 或测试基础设施。简单性包括修改成本和维护成本，不要求为了少一个模块而重写成熟代码，也不要求为了未来可能扩展先造框架。

## 3. 如实表达状态，减少重复事实

后续行为依赖的历史必须有明确归属。计数器、位图和回调上下文同样是状态；把 enum 改成一组 flag 不会消除组合空间。

能从权威状态推导的 busy/ready 不另存可写副本。设备运行情况、通信可达性和操作结果在需求中含义不同时应分别表达。上位机等待超时不能直接变成“设备没有执行”，软件写入 IDLE 也不能证明硬件已经停下。

## 4. 实际等待有结束方式

跨事件的等待需要完成证据、时间/重试预算和预算耗尽后的处置。恢复也会失败，不能每次恢复都重建无限预算。长期稳定的空闲、运行或需维护的锁存故障可以持续存在；不必强迫它们自动退出。

“结果未确认”是一种需要处理的信息状态。它应帮助调用方结束无限等待、保留资源和确定下一步，而不能用来掩盖安全性未经确认的事实。超时逻辑本身能否得到调度，需要实现与目标测试支持。

## 5. 让扩展影响相关部分

参数通常先作为配置，多通道按生命周期和共享资源划分。外部接口表达稳定的业务行为，内部步骤可以演进；上位机无需复制 FPGA 每个等待阶段。

增加可靠性机制前说明：解决哪种当前失败、需要记住什么、由谁处理、何时结束、影响哪些旧行为和测试。需求撤销时，也考虑移除其专用机制。

## 6. 结论与证据对应

设计约定描述应该怎样，代码反映实际实现，测试提供一定范围内的证据。状态图出口、host 测试、仿真和实机各有边界；不能把某一层通过扩展成整个产品可靠。

测试按风险选择。小文档改动不要求完整硬件测试；改变停止时限或 DMA 资源释放，则不能只以文档检查代替相关验证。

## 示例 A：只开始和停止上传

假设当前要求是单客户端、单次采集，STOP 同时停采集和上传；运行中不调参。

| 问题 | 最小约定 |
|---|---|
| 重复 START | 同参数返回已运行；不同参数按本版本约定拒绝 |
| 重复 STOP | 已停止时返回已停止；进行中时按同一操作范围处理 |
| 什么时候回答成功 | 产品承诺的实际效果已确认 |
| 需要等待硬件确认 | 增加局部 STARTING/STOPPING、截止点和必要关联 |
| 停止失败或无法确认 | 报告实际已知效果，保留仍被使用的资源，按产品策略处理 |

若调用确实有界且失败后状态可确认，IDLE/RUNNING 可能足够。若这些前提不成立，就不能为了保持“两状态”而隐藏真实等待和不确定性。完整说明见 [需求与增长](../embedded-protocol-designer/references/requirements-and-growth.md)。

## 示例 B：从单通道扩展为多通道

| 新需求 | 优先考虑 | 需要验证 |
|---|---|---|
| 八通道同步启停 | 同一采集生命周期＋通道配置 | 总吞吐、共同启停和数据关联 |
| 通道独立启停 | 复用通道逻辑，保存局部实例 | 独立完成、重复输入及资源释放 |
| 通道共用时钟或 DMA | 明确共享资源 owner 与合法配置 | 冲突接纳、受影响通道和控制延迟 |
| 一次操作中部分通道失败 | 明确整体或逐通道结果契约 | 实际效果、补偿结果和未确认部分 |

增加通道数不自动要求对象字典、HSM 或每通道一个任务。采用这些机制应有当前的发现需求、重复行为或调度依据。

## 怎样体现到贡献中

一个小改动可以用几句话说明需求、变化和验证。涉及新机制时补充其成本和适用边界；不要求填写固定长模板。示例用于解释选择，不能升级为所有设备的强制规则。

- 协议约定：[embedded-protocol-designer](../embedded-protocol-designer/SKILL.md)
- 固件执行：[arm-cortex-expert](../arm-cortex-expert/SKILL.md)
- 验证证据：[embedded-test-engineer](../embedded-test-engineer/SKILL.md)
- 贡献方式：[CONTRIBUTING.md](../CONTRIBUTING.md)

## English overview

Define current behavior and acceptance criteria first. Choose the smallest sufficient design and preserve existing infrastructure that already meets the requirements. Represent necessary history honestly: flags and counters also create state space. Give actual waits and recovery attempts bounded outcomes, including uncertainty when effects cannot be confirmed. Extend local lifecycles while making shared-resource constraints explicit. Match each reliability claim to evidence at the appropriate layer.

A simple START/STOP interface may need only IDLE/RUNNING if calls are bounded and failure effects remain known. Asynchronous completion requires local phases and deadlines. Synchronized channels can share a lifecycle; independently controlled channels need local instances and coordination for shared hardware. None of these examples mandates a framework for every device.
