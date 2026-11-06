# good-good-study

面向各种主题的通用学习 skill。根据你的目标和基础安排讲解、示范、练习与反馈；持续学习时，通过分工对话和长期记忆接续进度。

可以学习数学、编程、语言、研究方法、职业技能、摄影、音乐和生活技能等内容，也可以带着自己的教材、大纲或项目开始。

## 快速开始

在支持该 skill 的 Codex 环境中输入：

```text
用 $good-good-study 带我学 Python，从基础开始。
```

也可以给出更具体的目标：

```text
用 $good-good-study 帮我理解条件概率，用直观例子解释，再让我练两题。

用 $good-good-study 带我学摄影，结合我的照片安排练习和反馈。

用 $good-good-study 带我系统学习线性代数，每天30分钟，保存进度并安排复习。

用 $good-good-study 继续上次的学习，先读取进度和未完成任务。
```

你可以随时调整节奏，例如“讲得更简单”“给我一点提示”“直接给出完整讲解”“增加实践”“复习上次的内容”。

## 安装

需要 Git，以及支持本地 skills 的 Codex 环境。Python 3.9+ 仅在运行附带的数据库检查脚本或测试时需要。

### 用户级全局安装

在 macOS 或 Linux 的终端执行：

```bash
mkdir -p "$HOME/.agents/skills"
git clone https://github.com/isclin123/good-good-study.git \
  "$HOME/.agents/skills/good-good-study"
```

安装后可在不同项目中调用 `$good-good-study`。自动匹配已启用；显式写出名称可以清楚地选择这个 skill。如果列表尚未刷新，可重新启动 Codex。

如果目标目录已经存在，请先检查现有安装。通过 Git 克隆安装的副本可以这样更新：

```bash
git -C "$HOME/.agents/skills/good-good-study" pull --ff-only
```

### 仅为当前项目安装

在项目根目录执行：

```bash
mkdir -p .agents/skills
git clone https://github.com/isclin123/good-good-study.git \
  .agents/skills/good-good-study
```

只需选择一种安装方式。目录规范与调用方式见 [OpenAI 官方 skills 文档](https://learn.chatgpt.com/docs/build-skills)。

## 学习方式

- **即时指导**：解释一个概念、演示一种方法，或帮助跨过当前障碍。
- **专题学习**：围绕目标组织小节，补齐先修知识并安排练习。
- **持续学习**：建立路线、学习项目、分工对话、长期记忆和复习安排。
- **接续学习**：读取已保存的状态，从暂停点继续。

教学形式随主题变化。概念学习可以用类比、反例与复述；数理学习注重推理和变式；编程通过运行、观察与调试；实践和艺术围绕操作、作品和具体反馈。

每轮聚焦一个小目标：解释 → 示范 → 真实尝试 → 反馈 → 调整。练习可以是问答、计算、代码、讨论、操作或作品。

## 持续学习与角色协作

持续项目按需要设置总控教练、专项教练、测评复盘和资料研究角色。角色围绕学习目标划分，可合并和调整。

总控管理整体路线；专项教练保存本领域的活动与反馈；测评汇总证据并提出调整建议。角色通过共享文件、数据库和持久任务队列交接。

具备相应工具与授权时，可以创建或复用应用中的分工 Chat；其他环境可使用角色启动文件。各角色启动时读取共享状态，按需要检索历史证据。

## 四层长期记忆

1. **稳定记忆**：目标、相关偏好、已验证的起点和能力信息。
2. **情景记忆**：真实学习活动、原始回答或作品、反馈与评价依据。
3. **知识记忆**：概念、技能、错误模式、资源、熟练度与复习历史。
4. **运行记忆**：当前路线、任务、暂停点、未完成练习和角色交接。

持续项目优先使用本地 SQLite 保存结构化记录；状态摘要和报告可以重新生成。不同课程通过项目标识隔离进度，下一次对话从保存的记忆恢复。

具体协议见 [记忆管理](references/memory-continuity.md)、[角色与对话协作](references/roles-and-chats.md) 和 [项目架构](references/architecture.md)。

## 仓库内容与运行方式

本仓库提供 skill 指令、参考协议，以及一个只读 SQLite 检查工具。具体课程、数据库和练习入口由执行 skill 的助手根据学习目标和可用环境按需建立。

```text
good-good-study/
├── SKILL.md                       # 教学与学习项目工作流
├── agents/openai.yaml             # 展示信息与自动匹配设置
├── references/
│   ├── architecture.md            # 持续学习架构
│   ├── memory-continuity.md        # 四层记忆、绑定与恢复
│   └── roles-and-chats.md          # 分工对话与交接协议
├── scripts/probe_memory.py        # 只读数据库结构检查
└── tests/test_memory_probe.py      # 检查工具的行为测试
```

持久化和跨角色同步依靠实际的文件与命令执行。对话创建、媒体分析和后台任务取决于宿主提供的能力。教学反馈以用户实际提供的回答、代码、操作过程或作品为依据。

## 数据库检查工具

在仓库根目录运行：

```bash
python3 scripts/probe_memory.py --db /absolute/path/to/learning.sqlite3
```

脚本检查现有库的路径、表、schema 版本、行数、基础完整性和外键问题。它使用只读连接，不初始化、迁移或写入数据库，也不输出学习答案。检查成功不代表已经加载课程上下文。

退出码：`0` 表示检查通过，`1` 表示打开或读取失败，`2` 表示检查发现完整性或外键问题。

## 验证

使用 Python 标准库运行测试，无需安装第三方依赖：

```bash
python3 -m unittest discover -s tests -v
```

测试覆盖只读检查、内容保持、缺失及无效文件、特殊路径和表名、外键错误、WAL 已提交数据，以及 FTS 内部表处理。具体课程的持久化和角色协作应在建项时单独验证。

## Contributor

[Sicheng Yi (@isclin123)](https://github.com/isclin123)
