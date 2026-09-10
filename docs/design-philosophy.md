# 设计理念：任务明确，适度设计，验证结果

Firmware Forge 面向嵌入式开发，维护可组合的 AI 技能、命令与工具。当前工程能力重点是 STM32 / Cortex-M、FreeRTOS、外设与数据处理、设备交互和测试验证。

技能帮助 AI 判断和实现，命令提供明确的构建/烧录入口，工具处理芯片数据、map 文件或状态模型。它们各自可用；项目不规定所有任务必须经过协议设计、固件实现、测试规划的完整链条。

## 1. 明确本次任务，沿用已有事实

新功能需要明确行为与验收条件；已有工程的修复、评审、优化或工具调用，则从当前请求、实现和已确定的约束开始。需求先行不等于每次重写产品规格，也不等于先设计通信协议。

例如，排查 DMA 旧数据先检查 buffer 归属与实际 cache 配置；优化滤波器先明确误差、延迟与 CPU 预算；执行构建先识别工程、Target 与工具链。只澄清会改变本次决策的缺失信息。

## 2. 使用最小足够方案

保留已有工程中满足要求的 RTOS、DMA、驱动和测试设施。简单性包含修改成本、运行成本和长期维护成本；依据当前需求选择阻塞调用、中断、DMA、缓冲或任务划分。

优先现有接口、厂商支持的配置与扩展点。有重复且稳定的需求时再提取公共组件；未来可能扩展不构成建立通用框架的充分理由。

## 3. 专项规则按风险使用

DMA/ISR/cache 规则用于相关硬件数据路径；DSP 与回放规则用于数值处理；持久化规则用于写入一致性和掉电恢复；协议规则用于外部交互契约。普通函数优化无需生成状态图，单独构建无需重做架构设计。

涉及共享资源或真实异步等待时，仍需明确所有者、完成证据、退出期限及失败处理。计数器和位图同样保存状态，减少 enum 数量不等于降低复杂度。协议的可靠性优化应让失败可控；详见 [状态与交互执行](../arm-cortex-expert/references/state-and-interaction.md)。

## 4. 用工程证据支撑结论

需求描述预期，代码体现实现，日志与测试反映特定条件下的行为。芯片数据库和 map 工具输出需结合实际芯片、工程和厂商资料核对。工具失败应保留原因，不能把空查询结果直接解释成芯片不支持。

单元测试、数值回放、抽象模型、仿真和目标测试各有边界。回放与旧基线一致不等于测量精度达标，构建成功不等于功能正确，图上存在出口也不等于真实调度必然收敛。

## 5. 扩展落在相关模块

新增外设优先复用驱动边界，改变算法只重查受影响的数值与性能条件，新增测试接缝以验证收益为依据。多通道采集同时考虑数据率、同步关系、资源和生命周期，不能只从命令或状态数量判断结构。

协议是项目的一项专项能力。接口变化时检查两端语义和兼容性；接口不变的内部修复通常保持原约定。参数配置、异步阶段、请求去重或对象字典分别由真实需求决定。

## 6. 让执行和维护可审查

构建、烧录和查询有明确输入、目标、结果与诊断。烧录作用于实际设备，需明确目标；超时或中断时如实报告已知结果。测试和文档随相关行为一起更新，提交保持一个可理解、可验证的目的。

技能、命令和工具的新增同样应说明当前用途。单纯增加目录或技能数量不是项目演进的目标。

## 按任务选择入口

| 当前任务 | 合适的起点 | 交付与验证重点 |
|---|---|---|
| ADC DMA 偶发旧数据 | 固件技能的 core/family 与 DMA/cache 规则 | 缓存行、内存可达性、buffer 交接及目标证据 |
| 滤波 CPU 占用过高 | 固件 DSP 参考；需要回归时使用测试技能 | 保持允许误差/时延，比较回放和实际周期预算 |
| SPI Flash 写入影响采集 | 存储与采集参考 | 总线占用、设备 busy、调度及容量边界 |
| 新建标定回放回归 | 直接使用测试技能 | 数据可追溯、容差依据、数值与通道/时间一致性 |
| 分析已有 Keil map | 直接调用 map 工具 | 实际产物中的占用与布局，不强制生成协议 |
| 编译指定工程 | DSH `/build <昵称>` | 所选工程、日志与结果；烧录是独立动作 |
| 新增 START/STOP 或改变重连行为 | 协议技能；实现或测试时按需协作 | 完成与重复语义、兼容性、真实等待与失败退出 |

具体流程见 [技能分工](skills-integration.md)、[使用指南](workbench-usage.md) 和 [贡献指南](../CONTRIBUTING.md)。

## English overview

Firmware Forge provides skills, commands and tools for embedded development, currently focused on STM32 / Cortex-M firmware. Start from the current task and existing project evidence. Requirements-first does not require a new specification for every patch. Drivers, DSP, storage, networking, verification and protocol design have their own entry points; protocol design is one specialty, not a prerequisite for all work.

Preserve useful infrastructure and add mechanisms only for concrete needs. Apply domain rules where their risks exist. Keep shared-resource ownership and real asynchronous waits explicit without requiring state graphs for unrelated tasks. Match claims to evidence: builds, replay, model checks and hardware tests establish different facts. Commands and tools can be used directly with clear inputs, targets and outcomes.
