# 设计理念：任务明确，适度设计，验证结果

Firmware Forge 面向嵌入式开发，维护一组可组合的 AI 技能、命令与工具。当前工程能力集中在 STM32 / Cortex-M、FreeRTOS、外设与数据处理、设备交互和测试验证。

技能帮助 AI 做判断与实现，命令提供明确的构建和烧录入口，工具处理芯片数据、map 文件或状态模型。它们彼此独立，也按需协作；项目并不要求任何任务都走完「协议设计 → 固件实现 → 测试规划」这一整条链。

## 1. 从当前任务出发，而不是从模板出发

新功能当然需要先说清行为与验收条件。但对已有工程的修复、评审、优化或工具调用，更自然的起点是手头的请求、现有实现，以及已经确定的约束。需求先行，不等于每次改代码都要重写产品规格，更不等于先设计一版通信协议。

排查 DMA 旧数据，应先看 buffer 归属与实际 cache 配置；优化滤波器，应先明确误差、延迟与 CPU 预算；执行构建，应先识别工程、Target 与工具链。只澄清那些真正会改变本次决策的缺失信息，其余留给已有事实。

## 2. 做够用的方案，而不是更漂亮的架构

工程里已经满足要求的 RTOS、DMA、驱动和测试设施，应当保留。所谓简单，包含修改成本、运行成本与长期维护成本；阻塞调用、中断、DMA、缓冲或任务划分，应按当前需求选择，而不是按教条升级。

优先使用现有接口，以及厂商支持的配置与扩展点。当某种做法反复出现且足够稳定时，再提取公共组件。「将来也许会扩展」本身，不足以成为搭通用框架的理由。

## 3. 专项规则用在对应的风险上

DMA / ISR / cache 规则，用于真实的硬件数据路径；DSP 与回放规则，用于数值处理；持久化规则，用于写入一致性与掉电恢复；协议规则，用于对外交互契约。普通的函数优化不必生成状态图，单独编译一次也不必重做架构设计。

但凡涉及共享资源或真实异步等待，仍需说清谁拥有资源、完成证据是什么、多久必须退出、失败之后怎么办。计数器和位图同样是状态；把 enum 改小，并不等于复杂度下降。协议层面的可靠性改进，目标应是让失败可控——细节见[状态与交互执行](../arm-cortex-expert/references/state-and-interaction.md)。

## 4. 让结论落在证据上

需求描述预期，代码体现实现，日志与测试反映特定条件下的行为。芯片数据库和 map 工具的输出，必须结合实际芯片、工程与厂商资料核对。工具失败时应保留原因；空查询结果不能被解释成「芯片不支持」。

单元测试、数值回放、抽象模型、仿真与目标测试，各自能证明的事情不同。回放与旧基线一致，不等于测量精度达标；构建成功，不等于功能正确；图上存在出口，也不等于真实调度必然收敛。

## 5. 扩展落在相关模块

新增外设时，优先复用驱动边界；改变算法时，只重查受影响的数值与性能条件；新增测试接缝，应以能否验证收益为依据。多通道采集要同时考虑数据率、同步关系、资源与生命周期，不能仅凭命令或状态的数量来定结构。

协议是本项目的一项专项能力。接口变化时，检查两端语义与兼容性；接口不变的内部修复，通常保持原约定即可。参数配置、异步阶段、请求去重或对象字典，分别由真实需求决定，而不是预置选项。

## 6. 执行与维护要经得起回看

构建、烧录和查询应有明确的输入、目标、结果与诊断。烧录作用于真实设备，必须先确认目标；超时或中断时，如实报告已经知道的结果。测试和文档随相关行为一起更新，一次提交只表达一个可理解、可验证的目的。

技能、命令与工具的新增同样如此：先说明它解决什么当前问题。单纯增加目录或技能数量，不是项目演进的目标。

## 按任务选择起点

| 当前任务 | 合适的起点 | 交付与验证重点 |
|---|---|---|
| ADC DMA 偶发旧数据 | 固件技能的 core/family 与 DMA/cache 规则 | 缓存行、内存可达性、buffer 交接及目标证据 |
| 滤波 CPU 占用过高 | 固件 DSP 参考；需要回归时使用测试技能 | 在允许误差与延迟内比较回放结果和周期预算 |
| SPI Flash 写入影响采集 | 存储与采集参考 | 总线占用、设备 busy、调度及容量边界 |
| 新建标定回放回归 | 直接使用测试技能 | 数据可追溯、容差依据、数值与通道/时间一致性 |
| 分析已有 Keil map | 直接调用 map 工具 | 看清真实产物中的占用与布局，不必牵出协议 |
| 编译指定工程 | DSH `/build <昵称>` | 锁定工程、日志与结果；烧录是独立动作 |
| 新增 START/STOP 或改变重连行为 | 协议技能；实现或测试时再协作 | 完成与重复语义、兼容性、真实等待与失败退出 |

更细的分工见[技能分工](skills-integration.md)、[使用指南](workbench-usage.md)与[贡献指南](../CONTRIBUTING.md)。

## English overview

Firmware Forge provides skills, commands and tools for embedded development, currently focused on STM32 / Cortex-M firmware. Start from the current task and the evidence already in the project. Requirements-first does not mean writing a new specification for every patch. Drivers, DSP, storage, networking, verification and protocol design each have their own entry point; protocol design is one specialty, not a prerequisite for all work.

Keep infrastructure that already works. Apply domain rules where their risks actually exist. Shared-resource ownership and real asynchronous waits must stay explicit, without forcing state graphs onto unrelated tasks. Match every claim to the kind of evidence that can support it: builds, replay, model checks and hardware tests establish different facts. Commands and tools may be used directly, as long as inputs, targets and outcomes stay clear.
