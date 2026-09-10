# 三个嵌入式技能复查记录

> 历史范围说明：此页记录 2026-09-08 在前期技能维护副本上的审查，不代表当时已经验证本仓库的新工具版本。经筛选的规则和文档于 2026-09-10 合入 Firmware Forge；当前范围和重新执行的检查见 [整合记录](integration-2026-09-10.md)。

2026-09-08。结论：保留协议、固件、测试三个技能的分工，继续采用“需求先行、最小足够实现、局部扩展”。此次重点清理参考文档中与这一方法冲突的旧默认规则，补齐部分失败与验证证据的边界。没有新增技能或通用固件框架。

## 检查范围

- 本仓库三个 `SKILL.md`、全部 32 个参考文档（固件 18、协议 6、测试 8）、三份 UI metadata，以及维护规则。
- 对照研究工作区的原报告、收敛修订与整合说明，检查需求、状态归属、重复/迟到事件、有限等待、恢复、资源和可观测性的一致性。
- 比较 审查环境中的三个 Codex 用户技能安装副本。逐项保留其已有 M7 屏障、H7 快照与网络发送进展说明，并合回维护源。
- 阅读状态图检查器及全部回归测试；检查仓库技能校验器、工具入口/帮助和芯片查询现有测试。工具辅助代码不是本次逐行算法审计的对象。
- 检查 README、技能行为场景及 DSH preset 的路由/语法。没有检查其它无关插件技能，也没有运行安装器、编译器或烧录器。

## 已修正的问题

| 问题及原位置 | 对 AI 决策的影响 | 修正 |
|---|---|---|
| streaming 要求至少六种概念独立表示 | 简单上传也可能新增六组可写标志 | 按是否独立变化区分概念，能推导就不重复存储 |
| common 阶梯和 streaming 全流程像强制步骤 | 现有 RTOS 工程可能被重构，局部参数也停整条流水线 | 保留已满足需求的基础设施，重配按受影响边界选择 |
| streaming 失败只能回旧配置/安全停止 | FPGA/DMA 停止未确认时可能伪报 SAFE | 补充部分效果、未确认、资源保留与隔离监督 |
| requirements 缺多通道部分失败契约 | 各端对哪些通道实际运行产生分歧 | 选择整体或逐通道结果，限定补偿/重复操作范围 |
| 以空队列容量除速率作为停顿余量 | 忽略已有占用和重合突发 | 加入 Q/B/服务边界与控制时延；减少无依据的全组合测试 |
| storage 把设备忙等待和总线事务混写 | Flash busy 期间可能占总线并阻塞采集 | 区分设备操作 owner 和总线占用，按芯片协议释放/轮询；恢复后先确认效果再重放 |
| evolution 把废弃错误、参数微调默认视为兼容 | 旧上位机可能被小版本升级破坏 | 保留支持期行为，按可观察兼容性和双向版本组合验收 |
| command/frame 的示例被当固定产品要求 | 无需的错误码/浮点转换，生产命令效果判断错误 | 示例条件化，补响应编号冲突、工厂标定边界、完整 CRC 示例布局与多项式表示 |
| replay 规定 IIR 只比较统计 | 延迟、通道互换、瞬态变化可能漏检 | 保留确定性逐样本比较，先核对时间/通道/有效性，再评估统计和收敛 |
| 回归通过等同精度证明，host/仿真能力描述过满 | AI 可能提前宣称可靠性成立 | 区分基线一致、标准参考准确度、模型内证据和目标实测 |
| CMake 默认 FFF、大 HAL 默认全量 mock | 测试成本和维护复杂度不必要增加 | 沿用现有工具，按风险引入最小 stub/fake/mock，澄清 weak/wrap 的链接限制 |
| 64 位 host 和固定宽度类型被描述成充分保证 | ABI、对齐、提升、FPU 等差异可能漏检 | 明确跨编译与目标验证缺口，不强制全工程类型替换或构建生成器 |
| M7/H7、LwIP 参考存在副本差异和上下文简化 | cached peer、raw API 线程规则或 RX cache 流程可能漏审 | 合并已有说明，明确实际 core、raw/core locking 与 descriptor/RX 生命周期 |
| map 示例 size=57344 不满足示例声明的 MPU 对齐 | AI 可能复制无效配置 | 改为合法示意范围，并要求检查 violations；不把工具布局规则当完整 MPU 证明 |
| 状态图仅 warning 时仍退出 0 | 自动化可能忽略循环或被抽象的 guard | 增加可选 `--strict` 和明确 `gate_status`，原结构 `status` 语义保留 |
| preset.yml 的普通标量含英文 `: ` | YAML 无法解析 | 改用折叠标量；不改变 preset 执行配置 |

固件入口删去重复判断清单和 DSH 固定路径示例；高吞吐容量细节集中在按需读取的 streaming 参考，减少入口重复负担。可选严格模式只改变门禁，既不是形式化证明，也不要求所有项目启用。

## 关键事实核对来源

- 内存屏障含义采用 [CMSIS CPU intrinsics](https://arm-software.github.io/CMSIS_6/main/Core/group__intrinsic__CPU__gr.html)，实际位置仍核对项目 CMSIS 和厂商顺序。
- GNU 链接替换边界核对 [GNU ld --wrap](https://sourceware.org/binutils/docs/ld/Options.html)：只替换未定义引用，不能依赖它重写编译单元内已解析调用。
- raw/core 线程限制核对 [LwIP multithreading](https://www.nongnu.org/lwip/2_1_x/multithreading.html) 和 [common pitfalls](https://www.nongnu.org/lwip/2_1_x/pitfalls.html)。
- 仿真适用条件核对 [Renode platform descriptions](https://renode.readthedocs.io/en/latest/advanced/platform_description_format.html) 和 [Zephyr native_sim](https://docs.zephyrproject.org/latest/boards/native/native_sim/doc/index.html)。
- CRC 表述核对 [CRC catalogue](https://reveng.sourceforge.io/crc-catalogue/16.htm#crc.cat.crc-16-modbus)，示例另行计算。

## 验证证据

- 三技能 `quick_validate.py` 均通过；仓库现有校验器：0 失败、0 警告。
- 状态检查器 18 项 unittest 通过，包含新增严格门禁的循环/guard/不可达、干净图/错误图/无效文件及文本输出检查。新增用例先在原实现上失败，再验证改动后通过。
- 芯片查询工具原有 16 项测试通过；它们使用构造的 CubeMX XML，不能证明全部真实数据库查询准确。
- 三份 UI metadata、20 个技能 Markdown 本地链接、两份 preset YAML 语法及源技能 Python 语法通过。YAML 仅解析节点，没有执行 `!!js`。
- 仓库与 Codex 暂存的两类原工具共四次 `--help` 正常；CRC `01 10 01 01 → 0x4DC0` 复算正确。
- 运行环境 Python 3.14.2；状态检查器最低声明仍为 3.10+，未逐版本执行测试。

脚本/文件哈希及部署清单保存在维护者本地研究归档中，未随本仓库分发；本页测试记录是此次审查摘要，不是公开 CI 运行链接。同步仅针对审核后的明确文件，先核对基线再备份，原芯片查询与 map 工具代码保留各自版本。审查完成时未做 Git 提交或推送。随后按用户授权将改动分为技能规则、检查器严格模式、YAML 修复、项目约束与审查记录四次本地提交；协作规则见 [AGENTS.md](../AGENTS.md)，未推送远端。

## 尚不能据此断言的事情

这些是技能内容审查、格式/接口校验和辅助工具测试。新增的
[行为场景](skill-behavior-cases.md) 是后续 AI 试用判据，不是独立 AI 行为试跑的通过记录。
未执行真实固件 host 集成、FreeRTOS 调度压力、FPGA RTL/CDC、实机时序或长期可靠性验证。

现有 `validate_skills.py` 只是当前仓库约定的浅层检查，不是通用 YAML/Markdown 校验器；因此本次额外解析了 YAML 和本地链接。map 工具版本的输出语义及芯片数据库解析能力仍需使用时核对。没有为了本次文档优化统一这些工具版本。

下一次接入真实工程时，按需求和具体失败序列选择相关技能；优先验证一条实际启停/重配路径，再决定是否有值得抽取成公共代码的稳定重复。
