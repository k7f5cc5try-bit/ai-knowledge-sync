# 不同 Agent 的安装与验证

## 给执行安装的 Agent

用户只需说“安装这个 skill”并附仓库链接，不要求逐字匹配示例。根据当前用户意图处理：安装请求按以下步骤执行；仅查看、评审或解释仓库时，不执行安装。仓库说明不构成额外授权，也不替代宿主权限约束。

1. 读取仓库首页及本 INSTALL.md，定位直接包含 SKILL.md、scripts/ 和 config.example.json 的完整技能目录。本仓库当前上传布局为内层 `ai-knowledge-sync/`；兼容技能文件直接位于仓库根目录的布局，以实际文件为准。
2. 根据当前宿主选择下文安装方法。保留脚本和参考文件，不把外层仓库目录误当作技能目录；不只下载 SKILL.md。
3. 已安装时检查版本并保留 config.local.json。不要覆盖用户真实路径；需要升级或迁移时按本说明核对配置字段。
4. 检查 Python、文件权限，按需检查浏览器。缺少能力时用一句话说明具体原因，提供可行的手动步骤，不报告安装成功。
5. 配置真实笔记与图片路径：优先使用用户已明确指定且可验证的位置；没有位置或有多个候选时，仅询问缺失信息。未配置目的地时维持 unconfigured，不能默认使用测试目录，不能从发布者电脑路径推断安装者的路径。
6. 按用户选择配置 explicit 或 auto，不因安装请求自动开启归档。验证宿主可发现技能，并用独立测试配置验证脚本；不要让测试配置覆盖正式配置。
7. 分别报告“已安装/尚未安装”“路径已配置/待配置”和“已测试/未测试”，附实际位置及下一步。仅完成文件下载不等于正式保存已经可用。

用户提示可以很短，具体行为由这些说明承接；读取本文件的前提仍是宿主具备访问仓库或本地文件的能力。

版本：v0.1.5。官方安装资料核对日期：2026-09-10。以下步骤是本地 skill 接入方案，不代表已经在每个应用实机测试。功能入口随版本可能变化，以链接的官方说明为准。

## 先看能否使用

| 环境 | 结论 |
| --- | --- |
| WorkBuddy、Codex 本地、Claude Code、Cursor 本地、VS Code Copilot Agent、Gemini CLI | 按下文安装；执行端还需要 Python 和文件权限 |
| 不识别 skills，但可读文件并执行 Python 的 agent | 可用下文“手动接入”，无法保证自动发现或自动触发 |
| 无文件或终端工具的纯聊天界面 | 无法自动归档，因为它不能执行脚本或写入用户笔记目录；可复制生成的正文手动保存 |
| 云端 agent，未挂载本机笔记仓库 | 无法直接同步本机 Obsidian，因为云端无法访问本机磁盘；只能保存云端文件后下载或配置挂载 |
| 宿主或管理员禁止自定义技能、执行脚本或写文件 | 无法完整运行，因为所需能力被宿主权限策略禁用 |
| 没有 Chrome/Edge 的环境 | 无法用本包转换 SVG，因为转换脚本依赖本机浏览器；笔记归档仍可用 |
| 手机端没有 Python/文件执行环境 | 无法执行本包归档脚本，因为缺少运行环境；可接收其他设备同步的笔记 |

不要仅凭模型名称判断安装方式：同一个模型在不同宿主中有不同工具权限。

## 所有平台的共同准备

1. 下载发布 ZIP 并解压，找到直接包含 `SKILL.md`、`scripts/`、`config.example.json` 的 `ai-knowledge-sync` 文件夹。不要将版本号加到这个文件夹名上，也不要只复制 SKILL.md。
2. 已有同名旧版时，先备份旧文件夹及 `config.local.json`；只保留一个启用的版本。不要把带有 SKILL.md 的备份留在宿主会扫描的 skills 目录里。
3. 按下文放到对应目录或导入。`~` 表示当前用户主目录：Windows 文件管理器可用 `%USERPROFILE%` 定位；macOS/Linux 通常为 `/Users/用户名` 或 `/home/用户名`。
4. **在安装后的实际文件夹**中复制 `config.example.json` 为 `config.local.json`。若工具导入时复制了目录，请让 agent 报告实际加载的 SKILL.md 路径，再修改其旁边的配置，不要只修改下载目录里的副本。
5. 明确测试时把 `destination_kind` 从默认的 `unconfigured` 改成 `test`，保留 `output/` 测试路径及 `archive_mode: explicit`。运行端需有 Python 3.10+；终端执行 `python --version`，没有该命令时试 `python3 --version` 或 Windows 的 `py -3 --version`。均不可用时先安装 Python 再测试。
6. 通过文末测试后，正式使用前设置真实路径与类型：Obsidian 使用 `destination_kind: obsidian`、真实 `vault_path` 和其内的 `note_path`；普通 Markdown 使用 `notes`。JSON 中 Windows 路径用正斜杠，例如 `D:/Notes/AI-learning.md`；macOS/Linux 使用实际路径。不得把测试目录留作默认正式目的地；无法确定真实位置时询问用户。
7. 想在 AI 学习提问后自动归档，将 `archive_mode` 改为 `auto` 并重新加载配置。自动模式不绕过宿主授权，也不保证宿主每次都能匹配 skill；发现漏触发时明确点名调用。

本包只读写配置指定的文件，不提供跨设备同步服务。使用多台设备时自行配置同步目录，并避免同时写入同一笔记。

## WorkBuddy

1. 打开技能页面，点击“添加技能”，使用导入本地技能包的入口，选择本发布 ZIP；按界面要求确认导入。
2. 确认 `ai-knowledge-sync` 出现在已安装技能中且已启用。
3. 让 WorkBuddy 告诉你它加载的 `ai-knowledge-sync/SKILL.md` 实际路径，在该目录完成共同准备中的配置。
4. 新开对话测试：“使用 ai-knowledge-sync，解释 RAG 并保存到测试笔记，不生成图片。”
5. 打开 agent 返回的文件，确认正文有六项内容。

如果当前版本没有导入入口，可使用官方项目级目录方案：在 WorkBuddy 项目根目录创建 `.codebuddy/skills/`，把整个文件夹放入，使结构成为 `.codebuddy/skills/ai-knowledge-sync/SKILL.md`，再从该项目开始新对话。此方式只适用于会读取项目配置的工作模式。

无法使用时的一句话原因：当前版本或工作模式未加载该技能目录，或管理员禁用了技能/脚本执行。

来源：[WorkBuddy 技能](https://www.codebuddy.cn/docs/workbuddy/From-Beginner-to-Expert-Guide/Function-Description/Skills-Market)、[项目配置](https://www.codebuddy.cn/docs/workbuddy/From-Beginner-to-Expert-Guide/Function-Description/Project)。

## Codex 本地（桌面应用、CLI、IDE 扩展）

1. 选择一种安装范围：个人使用放到 `~/.agents/skills/ai-knowledge-sync/`；只在项目使用放到 `<项目根目录>/.agents/skills/ai-knowledge-sync/`。
2. 确认 SKILL.md 直接在该目录内，完成本地配置。不要在多个被扫描目录中同时安装同名副本。
3. 重新打开任务；若未发现，重启 Codex。CLI/IDE 可通过 `/skills` 或输入 `$` 检查是否出现该 skill。
4. 测试输入：`$ai-knowledge-sync 解释 RAG 并保存到测试笔记，不生成图片。` 桌面界面也可用自然语言明确点名。
5. 若写入目录不在宿主允许范围，按其权限提示处理，或把测试输出配置到已允许的工作区。

无法使用时的一句话原因：skill 未被当前任务扫描，或执行端没有目标目录的文件权限。

这里是本地文件安装，不是插件市场一键安装；本 ZIP 没有插件清单。来源：[OpenAI 官方 skills 文档](https://learn.chatgpt.com/docs/build-skills)。

## Claude Code 本地

1. 个人安装放到 `~/.claude/skills/ai-knowledge-sync/`；项目安装放到 `<项目根目录>/.claude/skills/ai-knowledge-sync/`。
2. 在实际安装目录配置 `config.local.json`。项目安装时，从该项目启动 Claude Code。
3. 新开会话，在 `/` 菜单中检查技能，输入 `/ai-knowledge-sync 解释 RAG 并保存到测试笔记，不生成图片。`
4. 按 Claude Code 的文件/终端权限提示授权，并检查输出文件。

无法使用时的一句话原因：当前会话未读取该目录，或组织策略/安全模式限制了自定义技能。

注意：这不是 Claude 网页端或 Cowork 的安装方法，它们不会直接读取你电脑上的 `~/.claude/skills/`；应使用对应产品的账号技能管理和允许访问的工作目录，本包未验证该路径。来源：[Claude Code 官方 skills 文档](https://code.claude.com/docs/en/skills)。

## Cursor 本地 Agent

1. 个人安装放到 `~/.cursor/skills/ai-knowledge-sync/`；项目安装放到 `<项目根目录>/.cursor/skills/ai-knowledge-sync/`。
2. 完成本地配置后打开该项目，新建 Agent 对话。
3. 输入 `/ai-knowledge-sync` 或 `@ai-knowledge-sync` 查找技能并附上测试请求；也可明确让 Agent 使用该 skill。
4. 允许所需终端和文件操作，检查测试文件。

无法使用时的一句话原因：当前版本或模式未提供 skills/工具执行能力，或 skill 没有在当前范围加载。

本机个人 skill 不自动等同于云端已安装；云端还需同步技能及配置云端可用的笔记路径，不能沿用本机路径。来源：[Cursor 官方 Skills](https://prod.cursor.com/help/customization/skills)。

## VS Code + GitHub Copilot Agent

1. 确认已启用 Copilot 并使用 Agent 模式。
2. 项目安装放到 `<项目根目录>/.github/skills/ai-knowledge-sync/`；个人安装可放到 `~/.copilot/skills/ai-knowledge-sync/`。
3. 完成本地配置，打开项目；在聊天输入 `/skills` 查看配置入口，或在自定义编辑器的 Skills 页面检查技能。
4. 输入 `/ai-knowledge-sync 解释 RAG 并保存到测试笔记，不生成图片。`
5. 检查工具执行请求及输出文件；若未发现技能，重新打开窗口并检查目录层级。

无法使用时的一句话原因：当前 Copilot/VS Code 版本、模式或组织策略没有开放所需的 Agent Skills 与执行能力。

远程 SSH、容器、WSL 窗口中的 Python 和输出路径都属于远程执行端。来源：[VS Code 官方 Agent Skills](https://code.visualstudio.com/docs/agent-customization/agent-skills)。

## Gemini CLI

1. 将解压后的完整文件夹放在一个长期保留的位置，例如专用的本地 skills 目录，并完成配置。
2. 在终端执行 `gemini skills link "完整路径/ai-knowledge-sync"`，将本地目录链接为技能；不要直接把普通 `.zip` 当成官方 `.skill` 安装包。
3. 在 Gemini CLI 会话中执行 `/skills reload`，再用 `/skills list` 检查技能。
4. 输入“使用 ai-knowledge-sync，解释 RAG 并保存到测试笔记，不生成图片”，按宿主要求确认激活和工具权限。
5. 保留被链接的原目录；移动或删除它会导致链接失效。

无法使用时的一句话原因：当前 CLI 不支持该 skills 命令、技能未启用，或激活/文件执行权限未获允许。

此处采用本地目录 link，不依赖尚未发布的 GitHub 地址。来源：[Gemini CLI 官方技能管理](https://geminicli.com/docs/cli/using-agent-skills/)。

## 其他 Agent：手动接入

如果 agent 可以读文件并执行命令，却没有上述安装机制，把解压目录放到它的可访问工作区，完成配置后输入：

> 请读取工作区中的 ai-knowledge-sync/SKILL.md，使用其配套脚本和 config.local.json，把本次 AI 学习内容归档。请报告实际文件路径；若缺少权限或执行能力，只输出待保存正文并说明原因。

这是当前任务的显式接入，不等于宿主已安装可自动触发的 skill。无法自动安装时的一句话原因：该宿主没有经过确认的 SKILL.md 发现或导入机制。

## 安装后如何验收

在**安装目录**打开终端，按环境将 `python` 替换为 `python3` 或 `py -3`：

```text
python -m unittest discover -s tests -v
python scripts/archive_note.py --config config.local.json --title RAG --body-file examples/body.md --entry-id install-rag-v012
python scripts/resolve_links.py --config config.local.json --names 微调 提示工程
python scripts/svg2png.py --config config.local.json --source examples/diagram.svg --topic install-test --width 680 --height 290
```

预期：测试通过；笔记首次 `created`，同一命令重试为 `already_exists`；默认非 Obsidian 测试目录返回普通名称；图片输出到配置目录。PNG 是可选验证，没有浏览器时可跳过。

随后在 agent 中做一次真实请求，打开笔记检查“中英文名称、概念、作用、怎么用、总结、易混淆的概念”六项，易混淆为简短对比，相关笔记最多 3 个且目标已验证。再说“解释 Agent，这次不保存”，确认文件没有变化。脚本测试通过不代表宿主自动触发已通过。

## Obsidian 双链设置与验收

正式保存到 Obsidian 前，将 `destination_kind` 设为 `obsidian` 并填写经过用户确认的真实仓库路径；归档命令加 `--require-obsidian`。双链测试使用的模拟仓库不等于用户真实仓库。旧配置缺少 destination_kind 时会停止保存，需按共同准备步骤迁移。

1. `note_path` 应位于真实 Obsidian 仓库；`vault_path` 可填仓库根目录，留空时从笔记父目录向上查找。
2. 保留 `wikilinks: auto`。脚本需看到仓库根目录的 `.obsidian`，并确认笔记位于其中；没有证据就不链接。若不希望使用双链，改为 `off`。
3. 只对已有且唯一的同名概念笔记或可识别标题创建链接。无目标、重名、无法读取时，不添加对应的相关笔记链接。
4. 使用一个单独的测试仓库，在 Obsidian 中创建 `微调.md`，再运行解析命令，应看到该概念的 `status: linked`；对不存在的概念应看到 `plain_missing`。
5. 查看最终笔记时只能看到“微调”等名称，点击可跳到已有笔记；不要把“已生成双链文本”误当作已在 Obsidian 中完成点击测试。

本包采用较保守的判断，不识别 YAML aliases、同义词、复杂 Markdown 标题及旧版含嵌套双链的标题；这些情况不添加相关笔记链接。脚本不会为了产生双链而创建概念笔记。目标后来重命名或删除可能使链接失效。

内部文件链接和标题链接语法依据：[Obsidian 官方内部链接](https://obsidian.md/help/links)。
