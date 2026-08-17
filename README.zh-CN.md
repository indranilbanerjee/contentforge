# ContentForge

🌐 **Read this in:** [English](README.md) · [हिन्दी](README.hi.md) · [中文](README.zh-CN.md) · [日本語](README.ja.md) · [한국어](README.ko.md) · [Español](README.es.md) · [Português](README.pt-BR.md) · [العربية](README.ar.md) · [اردو](README.ur.md) · [தமிழ்](README.ta.md) · [বাংলা](README.bn.md) · [Русский](README.ru.md)

> **已与英文版 README v4.1.1（2026-08-17）同步。** [英文版 README](README.md) 是唯一权威来源——发行说明、完整的技能/命令目录、架构说明、故障排查以及完整 FAQ 均在其中。本翻译涵盖了安装、运行和更新 ContentForge 所需的全部内容。

> **本季度你要交付 30 篇文章：读起来像真人写的、引用真实来源、串联进你的转化漏斗，还要经得起较真编辑的审核。你的团队只有 3 个人，时间只有 9 周。上一批“AI 写的”稿件因为编造的统计数据被打了回来——而再上一批则悄无声息地过时了，没有任何人察觉。**

对每个选题运行 `/contentforge:create-content`。10 阶段流水线会产出一份可直接发布的 `.docx`：内置 43 模式人性化引擎、事实核查子代理、三类内部链接，以及满足 EU AI Act 合规要求的 C2PA 内容溯源——每篇仅需 30–60 分钟。接下来是任何单发式工具都不具备的部分：**生命周期闭环。** 每一篇已发布的内容都会被持续度量、接受内容衰减审计，并回馈到下一期内容日历与下一份内容简报中——一切通过持久化的文件契约实现，因此系统对你品牌的认知不会随着学到它的那次会话结束而消失。

开源企业级内容生产系统——**22 个技能 · 13 个专家代理 · 10 道质量门 · 43 模式 AI 痕迹人性化引擎 · 一个在流水线宣告完成之前重新推导每道质量门的运行审计器 · 28 个纯标准库 Python 脚本**。由 [Indranil Banerjee](https://indranil.in) 创建 · [LinkedIn](https://www.linkedin.com/in/askneelnow/) · [X](https://x.com/askneelnow)。

**版本 4.1.1** · [更新日志](CHANGELOG.md) · MIT 许可证 · [赞助本项目 ❤](https://github.com/sponsors/indranilbanerjee)

---

## 为什么选择 ContentForge

大多数 AI 写作工具只产出一份初稿、一种语气，没有任何质量门，而且内容一经发布就被抛诸脑后。ContentForge 端到端地解决了这些问题：

| 能力 | 价值所在 |
|---|---|
| **10 阶段流水线，每个阶段之后都有一道质量门** | 劣质产出会在向下游扩散之前被拦截并重跑 |
| **43 模式 AI 痕迹人性化引擎** + 自我批判元审校 | 产出读起来像真人而非 AI——靠度量说话，不靠感觉 |
| **事实核查子代理**逐一验证 URL 并交叉核对论断 | 引用真实可用、绝非凭空捏造——每个统计数据都能追溯到已验证台账中的条目 |
| **三类内部链接**（主题类 / 商业类 / 权威类） | 内容成为漏斗的一环，而不是一座信息孤岛 |
| **真正的 `.docx` 输出**，附带 SEO、质量、生产与内链四份附录 | 你的编辑拿到的是可用的 Word 文件，而不是 markdown |
| **运行审计器从产物出发重新推导每一道质量门** | “流水线说它完成了”与“产物证明它完成了”永远不会悄然脱节 |
| **生命周期闭环（v4.0）**——审计 → 更新 → 度量 → 规划，由文件契约串联 | 已发布内容不再“发完就忘”：衰减会被发现，更新会依据数据排定优先级 |
| **C2PA 内容溯源签名**，满足 EU AI Act 第 50 条合规要求 | 自 2026 年 8 月 2 日起，在欧盟市场分发的 AI 辅助长文内容必须具备溯源信息 |

## 来自真实运行的真实结果

一次端到端验证运行（2026 年 8 月，一个数字保存领域的测试品牌，围绕关键词“link rot”撰写的一篇 1,200 词博客）——以下按实际发生情况如实汇报：

- 事实核查阶段发现研究阶段误读了一项统计数据，随即将修正后的表述锁定进已验证台账，并禁止原句进入草稿。这条修正一字不差地保留到了最终交付的 Word 文件中。
- 验证阶段将 42 条论断与台账逐一比对：**零幻觉**。
- 人性化引擎在 7 个类别中消除了 20 处 AI 模式痕迹（逐模式度量，每处修改均记录前后对照），同时让所有事实、引用与 SEO 布点保持逐字节不变。
- 评审阶段以 **9.0/10（A 级）** 通过——内容质量 8.8、引用完整性 8.9、品牌合规 9.6、SEO 8.6、可读性 8.8。
- 运行审计器基于磁盘上的产物重新推导了全部结论：**14 项检查通过，0 项失败**——此后这次运行才被允许标记为已完成。

重点不在于流水线永不出错——而在于它的错误会被自身机制当场捕获、记录在案，在你的编辑看到文件之前就已处理完毕。真实产物（真实的图表、真实的修改前后对照、真实的评分卡）见[英文版 README](README.md#examples)。

---

## 快速开始

### 1. 安装

**Claude Code（CLI 或 VS Code/JetBrains 扩展）：**

```bash
/plugin marketplace add indranilbanerjee/neels-plugins
/plugin install contentforge@neels-plugins
```

**Anthropic Cowork：**在界面中打开 **Plugins** 面板 → Add marketplace → `indranilbanerjee/neels-plugins` → 安装 ContentForge。（`/plugin` 斜杠命令在 Cowork 中不可用——请使用 UI 面板。）随后运行一次 `/contentforge:cf-cowork-setup`，接入 Google Drive 以实现团队共享输出。

**OpenAI Codex（CLI + IDE + App）：**

```bash
codex plugin marketplace add indranilbanerjee/neels-plugins
codex plugin install contentforge@neels-plugins
```

**其他平台：**

```bash
# Cursor 2.5+ (in any Cursor Agent chat):
/add-plugin contentforge@https://github.com/indranilbanerjee/contentforge

# GitHub Copilot CLI:
copilot plugin marketplace add indranilbanerjee/neels-plugins
copilot plugin install contentforge@neels-plugins

# Google Antigravity 2.0:
agy plugin install https://github.com/indranilbanerjee/contentforge

# Hermes Agent (Nous Research):
hermes plugins install indranilbanerjee/contentforge

# OpenClaw:
openclaw plugins install git:github.com/indranilbanerjee/contentforge

# Grok (xAI Build CLI):
grok plugin install indranilbanerjee/contentforge
```

**claude.ai（网页版）：**从[最新发行版](https://github.com/indranilbanerjee/contentforge/releases/latest)下载一个主打技能——`cf-brief.skill`、`cf-social-adapt.skill`、`cf-translate.skill`、`cf-video-script.skill` 或 `cf-aeo-check.skill`——然后在 claude.ai 中依次进入：**Settings → Capabilities**（启用 *Code execution and file creation*）→ **Customize → Skills → Upload skill**。完整流水线依赖子代理调度，需在上述平台运行；主打技能可独立使用。

**ChatGPT 及其他 Agent Plugins 1.0 宿主：**ContentForge 在仓库根目录提供基于 OpenAI 厂商中立标准 Agent Plugins 1.0 的 `plugin.json`。在不支持子代理调度的宿主上，**便携执行通道**会在单个对话中顺序运行完整流水线——阶段相同、产物相同、质量门相同。

### 2. 配置你的第一个品牌

```
/contentforge:brand-setup
```

代理会引导你完成品牌语调、术语表、安全边界、引用规则以及用于内部链接的站点结构配置。当你提供网站地址后，它只需一步确认即可采集一份经过验证的页面清单。

### 3. 生成内容

```
/contentforge:create-content
```

选择内容类型、品牌、主题、字数与目标受众。流水线依次运行 10 个阶段（研究 → 事实核查 → 起草 → 视觉 → 验证 → 结构 → SEO → 人性化 → 评审 → 输出），每个阶段之后强制执行一道质量门，完成后再依据自身产物对整次运行进行审计，最终写出一份真正的 `.docx`。

### 4. 查找输出

```
~/Documents/ContentForge/<brand-slug>/<content-type>/<YYYY-MM>/<slug>.docx
```

该 `.docx` 包含正文、参考文献以及四份附录：SEO 评分卡、质量评分卡、生产明细和内部链接图谱。

### 5. 闭合循环

```
/contentforge:cf-aeo-check           # record which pieces AI engines cite
/contentforge:audit-content          # freshness-score the library; findings are RECORDED
/contentforge:cf-calendar --from-audit=latest   # next period: refreshes + gaps, from data
/contentforge:content-refresh        # execute a refresh at the audit's recommended scope
```

每条命令都会读取上一条命令记录下的结果——即使换了会话、换了日期、换了同事，也依然如此。

---

## 支持的平台（v4.1.1）

9 个原生平台 + claude.ai 上传 + 35+ 个 Agent Skills 客户端：

| 平台 | 安装方式 |
|---|---|
| **Claude Code**（CLI + IDE） | `/plugin install contentforge@neels-plugins` |
| **Anthropic Cowork** | Plugins 面板 → Add marketplace → `indranilbanerjee/neels-plugins` |
| **OpenAI Codex** | `codex plugin install contentforge@neels-plugins` |
| **Cursor 2.5+** | `/add-plugin contentforge@https://github.com/indranilbanerjee/contentforge` |
| **GitHub Copilot CLI** | `copilot plugin install contentforge@neels-plugins` |
| **Google Antigravity 2.0** | `agy plugin install https://github.com/indranilbanerjee/contentforge` |
| **Hermes Agent** | `hermes plugins install indranilbanerjee/contentforge` |
| **OpenClaw** | `openclaw plugins install git:github.com/indranilbanerjee/contentforge` |
| **Grok**（xAI Build CLI） | `grok plugin install indranilbanerjee/contentforge` |
| **claude.ai**（网页版） | 从[发行版](https://github.com/indranilbanerjee/contentforge/releases/latest)上传主打 `.skill` |
| **ChatGPT / Agent Plugins 1.0 宿主** | 根目录 `plugin.json` 包 + 便携执行通道 |

全部 22 个 SKILL.md 文件均通过 Agent Skills 开放标准实现跨平台移植——任何兼容客户端都可直接指向 `https://github.com/indranilbanerjee/contentforge/tree/master/skills`。

---

## 更新

**Claude Code：**第三方市场默认关闭自动更新。只需开启一次：`/plugin` → **Marketplaces** 标签页 → `neels-plugins` → **Enable auto-update**。或手动更新：先执行 `/plugin marketplace update neels-plugins`，再执行 `/plugin uninstall` + `/plugin install contentforge@neels-plugins` + `/reload-plugins`。

**Cowork / claude.ai / Claude Desktop：**打开 Plugins UI 面板 → 移除 ContentForge → 从市场重新安装（重新拉取即会获得最新版本）。

**Codex：**`codex plugin update contentforge` · **Cursor：**重新运行 `/add-plugin` · **Copilot CLI：**`copilot plugin update contentforge` · **Antigravity：**`agy plugin update contentforge` · **Hermes：**`hermes plugins update contentforge` · **OpenClaw：**`openclaw plugins update contentforge` · **Grok：**`grok plugin update contentforge` · **claude.ai 上传：**从最新发行版重新下载 `.skill` 并重新上传。

---

## FAQ（核心问题）

**我的数据存放在哪里？**一切都在本地：品牌档案与运行产物位于 `~/.claude-marketing/<brand>/`，交付物位于 `~/Documents/ContentForge/`。除了你所在平台自身发起的模型调用之外，不会向任何地方发送任何数据。

**需要连接 MCP/集成吗？**不需要。随附的 `.mcp.json` 是有意留空的——零自动连接服务器。连接器是一个按需启用的目录（`/contentforge:cf-connect`）。

**它符合 EU AI Act 吗？**符合——提供带第 50 条 AI 披露声明的 C2PA 内容溯源签名，外加可按品牌配置的披露层（不确定 ⇒ 一律披露的故障安全策略）。

**完整流水线能在 Claude Code 之外运行吗？**能——在不支持子代理调度的平台上，便携执行通道会顺序运行全部 10 个阶段，每道质量门原样保留。唯一的例外是 claude.ai 的 `.skill` 上传：那些是独立的主打技能，并非完整流水线。

---

## 关于维护者

ContentForge 由 **[Indranil "Neel" Banerjee](https://indranil.in)** 构建并维护——一位以信息安全为起点、其后横跨增长营销、企业数字化运营与 AI 转型的构建者与系统思考者。本项目是 **Neelverse Marketing Suite** 三插件套装的一员，另外两件是 [Digital Marketing Pro](https://github.com/indranilbanerjee/digital-marketing-pro) 与 [SocialForge](https://github.com/indranilbanerjee/socialforge)。

如果 ContentForge 为你的团队节省了时间，欢迎[⭐ 为仓库加星](https://github.com/indranilbanerjee/contentforge/stargazers)，也欢迎考虑[赞助本项目 ❤](https://github.com/sponsors/indranilbanerjee)——这能让发布节奏保持可持续。

**许可证：**MIT · **安全：**[私密安全通报](https://github.com/indranilbanerjee/contentforge/security/advisories/new) · **问题反馈：**[GitHub Issues](https://github.com/indranilbanerjee/contentforge/issues)
