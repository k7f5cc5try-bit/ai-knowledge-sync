# AI Knowledge Sync

把 AI 知识讲解按“中英文名称、概念、作用、怎么用、总结、易混淆的概念”沉淀为 Markdown 学习笔记，并按条件使用 Obsidian 双链、按需导出 PNG 配图。

当前发布版本：**v0.1.5**。按应用逐步安装、验证和不可用原因见 [INSTALL.md](INSTALL.md)，覆盖 WorkBuddy、Codex、Claude Code、Cursor、VS Code Copilot、Gemini CLI 及通用手动接入。

默认只在你要求保存时归档；可主动开启自动归档。不需要云服务或 API 密钥。

## 一句话安装

把下面这句话发给具有联网和文件操作能力的 agent：

> 帮我安装这个 skill：https://github.com/k7f5cc5try-bit/ai-knowledge-sync

“安装这个”“帮我装一下这个技能”等同义说法都可以，不需要固定口令。Agent 应先阅读本仓库说明，再按 [INSTALL.md](INSTALL.md) 完成安装和配置。只有一个链接、没有明确安装意图时，不应直接执行安装。

仓库若包含外层首页与内层同名目录，实际安装的是包含 SKILL.md 的 `ai-knowledge-sync/` 子目录；下载后的文件结构才是最终依据。

说明文件能帮助可读取仓库的 agent 理解任务，但不能让原本不能联网、写文件或执行命令的聊天界面自动获得这些能力；也不保证每个宿主都会主动打开链接。读取失败时，用户可提供解压文件或 INSTALL.md。

## 环境

本项目不绑定 WorkBuddy 或特定模型，不依赖专有工具接口。能力兼容不代表所有平台均已实测。

| Agent 能力 | 接入方式与可用范围 |
| --- | --- |
| 能加载 skills、读写文件并运行 Python | 按宿主安装规则加载整个文件夹，可执行笔记归档 |
| 能读文件、运行 Python，但不自动识别 skills | 明确让 agent 读取本项目 SKILL.md 并按其完成当前任务 |
| 云端运行、能操作工作区 | 配置云端路径；需下载笔记或挂载存储，不能直接填写本机磁盘路径 |
| 只有聊天能力 | 使用内容规范生成 Markdown 草稿；无法自动保存本地文件 |

PNG 转换另需执行端的 Chrome/Edge。不支持自动发现 skills 时，可以这样提示：

> 请读取我提供的 ai-knowledge-sync/SKILL.md，使用该目录中的配置和脚本，将本次 AI 学习内容整理并归档。若缺少文件或执行能力，展示待保存正文并说明未保存。

运行依赖：

- 支持加载本地 `SKILL.md` 且能读写文件、执行命令的 agent。
- Python 3.10 或更新版本；脚本只使用标准库。
- SVG 转 PNG 另需本机 Chrome 或 Edge。仅保存笔记不需要浏览器。
- 保存普通 UTF-8 Markdown 无需安装 Obsidian；双链检查需要可访问的 Obsidian 仓库和唯一的已有目标。
- 当前验证环境和范围见 [VALIDATION.md](VALIDATION.md)。其他平台及宿主的安装路径、权限机制可能不同，不承诺未经测试的兼容性。

## 安装与配置

1. 下载仓库，将完整的 `ai-knowledge-sync` 文件夹放入宿主应用支持的 skills 目录。不要只复制 SKILL.md，脚本也需要一起保留。具体目录以宿主文档为准。
2. 复制 `config.example.json` 为 `config.local.json`。
   默认 `destination_kind: unconfigured` 会拒绝归档。明确测试时设为 `test`；正式保存普通 Markdown 设为 `notes`；保存真实 Obsidian 设为 `obsidian`，并填写真实仓库根目录 `vault_path` 和仓库内的 `note_path`。旧配置缺少该字段时也会停止，需明确完成迁移。
3. 修改 `note_path` 与 `image_dir`。相对路径以配置文件目录为基准；Windows 绝对路径推荐写成 `D:/Notes/AI-learning.md`，避免 JSON 反斜杠转义问题。
4. 按宿主要求重新加载 skill。如果应用不支持 skill，也可直接运行下方命令。

| 配置项 | 含义 |
| --- | --- |
| `archive_mode` | `explicit`：明确要求时归档；`auto`：用户主动开启 AI 学习讲解自动归档 |
| `destination_kind` | `unconfigured`：拒绝保存；`test`：仅测试；`notes`：普通笔记；`obsidian`：真实仓库 |
| `note_path` | 笔记文件路径；不存在时自动创建 |
| `image_dir` | PNG 保存目录 |
| `browser_path` | 可选 Chrome/Edge 程序路径，空字符串表示自动查找 |
| `vault_path` | 正式 Obsidian 保存必须明确填写仓库根目录；仅双链检查时允许留空向上查找；相对配置文件解析 |
| `wikilinks` | `auto`：检查仓库及目标后链接；`off`：只保留普通名称 |

开启自动归档意味着你允许 agent 在 AI 学习讲解后向配置的笔记新增内容。单次“不保存”指令优先。命令行脚本执行明确的写入操作，不自行判断会话授权。

如果希望“问到 AI 相关知识就沉淀笔记”，完成保存路径配置后，将 `archive_mode` 改为 `auto`，并让宿主重新加载配置。之后无需每次说“保存”；宿主仍需在 AI 学习问题中加载本 skill。普通排错或仅提及 AI 的非学习任务不会因此自动归档。

## 笔记内容要求

先抓核心能力与机制，再组织六项；不平均铺陈。以 Agent 为例，重点是目标驱动、动态决策、工具行动、反馈调整，不能只给流程名称或长例子。复杂规划、长期记忆、多智能体属于可选设计，不当作统一必要条件。

每个主要概念都包含中英文名称、概念、作用、怎么用、总结、易混淆的概念。“怎么用”需要具体步骤或情境示例；“总结”提炼最重要的记忆点和使用判断；“易混淆”用一句话对比关键区别；另设可选“相关笔记”，最多 3 个，只链接确认存在的目标，不确定就不加。非缩写术语不编造英文全称。

双链须同时满足：笔记位于可识别的 Obsidian 仓库中，且目标笔记或可识别标题已经存在并能唯一定位。不满足时保留普通名称，不创建空笔记。条目标题现在采用纯文本，旧版历史条目不会被改写。

例如问“什么是 RAG”，笔记不仅记录 Retrieval-Augmented Generation，还要解释检索如何为生成提供上下文、适合解决什么问题，以及如何通过“准备资料 → 检索相关段落 → 结合资料回答 → 检查来源”实际使用。

## 使用示例

> 解释 RAG 和微调的区别，并保存到我的学习笔记。

> 把刚才的 AI 知识讲解归档，有现成配图的话另存 PNG。

> 这次只解释，不保存。

笔记样式见 [示例](examples/sample-note.md)。示例未包含运行时生成的内部去重标记，不应当作生产笔记的重复检测数据。

在 skill 目录运行命令行示例：

```text
python scripts/archive_note.py --config config.local.json --title RAG --body-file examples/body.md --entry-id demo-rag-001
python scripts/svg2png.py --config config.local.json --source examples/diagram.svg --topic RAG --width 680 --height 290
python scripts/resolve_links.py --config config.local.json --names 微调 提示工程
python -m unittest discover -s tests -v
```

如系统仅提供 `python3` 或 `py -3`，替换命令前缀。重试笔记保存时复用相同 entry-id；新内容使用新 ID。

用户要求保存到 Obsidian 时，归档命令必须加 `--require-obsidian`。即使测试目录带有模拟 `.obsidian`，`destination_kind: test` 也会被拒绝。测试完成后必须切换真实路径，不能仅修改类型标签把模拟目录当成正式仓库。Agent 应根据用户请求选择目的地，脚本无法独立理解聊天中的意图。

## 数据保护与限制

- 保存笔记采用临时文件加原子替换；语义上只插入新条目，原有字节不被改写。这与手动编辑器的增量写入实现不同。
- 已有文件必须有且只有一个独立行锚点 `## 关键纠正清单（易错点）`。缺失或重复时不写入，请先人工检查笔记结构。
- 标题和正文完全相同的脚本生成条目会去重；改写措辞、无同步标记的历史条目不保证识别为重复。
- 锁仅协调本项目脚本，不协调 Obsidian、云同步或其他编辑器。保存时避免其他程序同时写该文件。异常终止可能留下 `.lock`：确认没有任务运行后再人工移除。
- 日期采用运行机器的本地日期。图片使用唯一文件名，不自动清理历史图片；再次转换会生成新文件。
- PNG 转换器针对本地、可信、自包含静态 SVG，不是恶意 SVG 的安全沙箱。不要将下载的不可信文件直接交给它处理。
- 浏览器会在独立临时配置目录运行，未禁用浏览器沙箱。此项目无上传逻辑，但不保证浏览器本身完全不产生网络请求。
- 程序检查 PNG 结构、校验和、压缩数据和尺寸；字体、裁切、视觉质量仍需查看图片。不支持动画、外部字体/图片及脚本。
- 脚本只负责可靠保存；归档知识的事实质量仍取决于生成内容和来源核验。

## 分享和贡献

发布完整目录到公开 GitHub 仓库即可。发布前排除 `config.local.json`、`output/`、真实笔记、截图中的个人信息；`.gitignore` 不会移除已被 Git 跟踪的文件。

发布 `v0.1.5` 时附上已测试环境。提交问题时提供系统、Python/浏览器版本、脱敏错误与最小复现，不上传私人笔记或配置。改动保存逻辑时运行 tests；改动渲染时实际转换并查看图像。

代码及文档采用 [MIT License](LICENSE)。你自行创建的学习笔记与图片不因使用本工具而自动改用本项目许可证。
