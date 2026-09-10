# 参与贡献 / Contributing

欢迎通过 [Issues](https://github.com/Fz2hOpenSource/firmware-forge/issues) 报告问题或提出改进，通过 [Pull Requests](https://github.com/Fz2hOpenSource/firmware-forge/pulls) 提交修改。小修复可以直接提交；新框架、依赖或大范围结构变化，先说明当前需求和预期收益。

## 改哪里

| 内容 | 维护位置 |
|---|---|
| 协议需求、命令、重复/失败与兼容性 | `embedded-protocol-designer/` |
| 固件执行、DMA、任务、资源与硬件约束 | `arm-cortex-expert/` |
| 测试方法、回放与状态图检查器 | `embedded-test-engineer/` |
| 项目理念与人类使用说明 | README 与 `docs/` |
| DSH / Keil 适配 | `preset/`、`plugins/mdk/`、`scripts/mdk/`、`install.ps1`、`install.bat` |

请先阅读 [设计理念](docs/design-philosophy.md) 和相关技能入口。AI 协作者另遵循 [AGENTS.md](AGENTS.md)。共享原则保持一个维护位置，专项步骤按需放参考，不把某个设备的例子变成所有项目的硬要求。

## 轻量提交流程

1. 查看现有差异，明确这次要改变的行为和验收条件。
2. 做聚焦修改；相关代码、测试和使用说明放在同一个完整提交中。
3. 运行与改动相称的检查，查看 `git diff --cached` 和 `git diff --cached --check`。
4. 用简短标题说明目的，PR 描述补充必要的原因、验证和限制。多个独立目的可分多次提交；小修改不强制拆分。

不要求复杂分支命名或固定长模板。外部贡献者可通过自己的 fork 发起 PR；本地提交与远端推送分别处理。不要混入个人工具配置、密钥、会话记录或无法公开的产品数据。

## 验证

在源码根目录运行共用检查：

```sh
python -X utf8 scripts/validate_skills.py
```

它只做当前仓库约定的浅层检查。文档还需核对本地链接、示例和入口一致性；YAML 修改需额外语法解析，不能执行其中的 JS 标签来代替解析。修改中文首页的定位、安装或核心示例时，同步英文首页。

按改动选择相关测试：

```sh
# 修改状态检查器时
python -m unittest discover -s embedded-test-engineer/tests -v
# 修改芯片查询工具时
python -m unittest discover -s arm-cortex-expert/tools/stm32cli/tests -v
# 修改 MDK 命令插件时（Node.js 20+，使用替身进程，不构建或烧录）
node --test plugins/mdk/tests/mdk-commands.test.mjs
```

PowerShell 文件保持仓库要求的 UTF-8 BOM。修改安装/烧录代码时，先在隔离目录或替身工具上验证目标选择和失败行为，再按需要补真实环境验证。不要仅为文档改动触发安装、烧录或全量硬件测试。

说明实际执行的检查、版本和未覆盖部分。状态图通过不是固件可靠性证明；AI 行为评估应记录输入、输出和判断依据，而非只断言文档包含某个关键词。

## 报告问题

提供可复现的最小信息：项目提交版本、宿主/工具版本、使用的技能、具体步骤或事件序列、预期与实际行为、相关脱敏日志。若报告技能决策问题，附最小输入和 AI 输出；若涉及真实设备，补 MCU/RTOS/接口和必要时序条件。先删去凭据、个人信息和不可公开的固件/采集数据。

## English

Use Issues for reproducible problems and proposals, and pull requests for changes. Explain the current need before introducing a new framework or dependency. Keep one complete purpose per commit, with its code, tests and documentation together. No elaborate branch naming or long PR template is required.

Edit the skill responsible for the behavior; shared philosophy belongs in the project documentation, while operational detail belongs in relevant skill references. Keep Chinese and English README positioning, installation and core examples aligned. Run the shared validator above and only the additional tests relevant to the change; check links and examples separately. Report what was actually tested and remaining gaps. Do not upload secrets, personal configuration, private transcripts or product data.
