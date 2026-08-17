# ContentForge

🌐 **Read this in:** [English](README.md) · [हिन्दी](README.hi.md) · [中文](README.zh-CN.md) · [日本語](README.ja.md) · [한국어](README.ko.md) · [Español](README.es.md) · [Português](README.pt-BR.md) · [العربية](README.ar.md) · [اردو](README.ur.md) · [தமிழ்](README.ta.md) · [বাংলা](README.bn.md) · [Русский](README.ru.md)

> **英語版 README v4.1.1(2026-08-17)と同期済み。** 信頼できる唯一の情報源は[英語版 README](README.md)です — リリースノート、スキル/コマンドの完全カタログ、アーキテクチャ、トラブルシューティング、FAQ 全文はそちらに掲載されています。本翻訳には、ContentForge のインストール・実行・アップデートに必要な情報がすべて含まれています。

> **今四半期中に 30 本の記事を出稿しなければならない。人間らしく読めて、実在するソースを引用し、ファネルへ内部リンクを張り、細部まで確認する編集者のチェックにも耐える記事を。チームは 3 人。残された期間は 9 週間。前回の「AI 生成」バッチは統計のハルシネーションでフラグが立ち、その前のバッチはいつの間にか陳腐化して、誰も気づかなかった。**

各トピックに対して `/contentforge:create-content` を実行してください。10 フェーズのパイプラインが、43 パターンのヒューマナイザー、ファクトチェッカーのサブエージェント、3 カテゴリの内部リンク、EU AI Act 準拠のための C2PA 来歴情報を備えた出稿可能な `.docx` を、1 本あたり 30〜60 分で生成します。そしてその先に、単発生成型ツールには決して真似できない仕組みがあります。それが**ライフサイクルループ**です。公開されたすべての記事は計測され、陳腐化がないか監査され、次のカレンダーと次のブリーフへフィードバックされます — 永続的なファイルコントラクトを通じて行われるため、システムがあなたのブランドについて学んだことは、それを学んだセッションが終わっても失われません。

オープンソースのエンタープライズ向けコンテンツ制作システム — **22 スキル · 13 の専門エージェント · 10 の品質ゲート · 43 パターンの AI 検出ヒューマナイザー · すべてのゲートを再検証してからでなければランに完了を宣言させないランオーディター · 標準ライブラリのみで動く 28 本の Python スクリプト**。開発者: [Indranil Banerjee](https://indranil.in) · [LinkedIn](https://www.linkedin.com/in/askneelnow/) · [X](https://x.com/askneelnow)。

**バージョン 4.1.1** · [変更履歴](CHANGELOG.md) · MIT ライセンス · [このプロジェクトを支援する ❤](https://github.com/sponsors/indranilbanerjee)

---

## ContentForge を選ぶ理由

ほとんどの AI ライティングツールは、単一のトーンでドラフトを 1 本生成するだけで、品質ゲートを持たず、出稿した瞬間にその記事のことを忘れてしまいます。ContentForge はこれをエンドツーエンドで解決します:

| 機能 | なぜ重要か |
|---|---|
| **各フェーズの後に品質ゲートを置く 10 フェーズパイプライン** | 不良な出力は下流へ伝播する前に検出され、再実行されます |
| **43 パターンの AI 検出ヒューマナイザー** + 自己批評メタパス | 出力は AI ではなく人間の文章として読めます — 感覚ではなく、計測に基づいて |
| **ファクトチェッカーのサブエージェント**が URL を検証し、主張をクロスチェック | 引用は実際に機能し、ハルシネーションではありません — すべての統計は検証済み台帳のエントリまで遡れます |
| **3 カテゴリの内部リンク**(トピック / コマーシャル / オーソリティ) | コンテンツが孤立したページではなく、ファネルになります |
| SEO・品質・制作・内部リンクの付録が付いた**本物の `.docx` 出力** | 編集者が受け取るのは markdown ではなく、そのまま使える Word ファイルです |
| **すべてのゲートを成果物から再導出するランオーディター** | 「パイプラインが完了したと言っている」と「成果物が完了を証明している」が、静かに乖離することは決してありません |
| **ライフサイクルループ(v4.0)** — 監査 → リフレッシュ → 計測 → 計画をファイルコントラクトで連結 | 公開済みコンテンツが「出しっぱなし」ではなくなります: 陳腐化は検出され、リフレッシュはデータに基づいて優先順位付けされます |
| EU AI Act 第 50 条準拠のための **C2PA コンテンツ来歴署名** | EU 市場で配信される AI 支援の長文コンテンツには、2026 年 8 月 2 日以降、来歴情報が必要です |

## 実際のランによる、実際の結果

エンドツーエンドの検証ラン(2026 年 8 月、デジタル保存分野のテストブランド、キーワード「link rot」に関する 1,200 語のブログ記事)の結果を、起きたことをそのまま報告します:

- ファクトチェックフェーズが、リサーチフェーズによる統計の読み違えを検出し、修正済みの文言を検証済み台帳にロックし、元の文がドラフトに入ることを禁止しました。この修正は一字一句そのまま、納品された Word ファイルまで残りました。
- 検証フェーズは 42 件の主張を台帳と突き合わせました: **ハルシネーションはゼロ**。
- ヒューマナイザーは 7 カテゴリにわたる 20 件の AI パターンを除去し(パターンごとに計測し、すべての編集に before/after のログを記録)、その間もすべての事実・引用・SEO 配置をバイト単位で維持しました。
- レビューフェーズは **9.0/10(グレード A)** で承認 — コンテンツ品質 8.8、引用の完全性 8.9、ブランド準拠 9.6、SEO 8.6、可読性 8.8。
- ランオーディターがディスク上の成果物からすべてを再導出: **14 チェック合格、失敗 0 件** — これを経て初めて、ランは自らを完了と宣言することを許されました。

重要なのは、パイプラインが決して間違えないことではありません。間違いが編集者の目に触れる前に、パイプライン自身の仕組みによって、記録に残る形で捕捉されるということです。実際の成果物(実際のチャート、実際の before/after 編集、実際のスコアカード)は[英語版 README](README.md#examples)でご覧いただけます。

---

## クイックスタート

### 1. インストール

**Claude Code(CLI または VS Code/JetBrains 拡張機能):**

```bash
/plugin marketplace add indranilbanerjee/neels-plugins
/plugin install contentforge@neels-plugins
```

**Anthropic Cowork:** UI の **Plugins** パネルを開く → Add marketplace → `indranilbanerjee/neels-plugins` → ContentForge をインストール。(Cowork では `/plugin` スラッシュコマンドは動作しません — UI パネルをご利用ください。)その後、チームで共有できる出力先として Google Drive を接続するために、`/contentforge:cf-cowork-setup` を一度だけ実行してください。

**OpenAI Codex(CLI + IDE + アプリ):**

```bash
codex plugin marketplace add indranilbanerjee/neels-plugins
codex plugin install contentforge@neels-plugins
```

**その他のプラットフォーム:**

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

**claude.ai(Web 版):** [最新リリース](https://github.com/indranilbanerjee/contentforge/releases/latest)からヒーロースキル — `cf-brief.skill`、`cf-social-adapt.skill`、`cf-translate.skill`、`cf-video-script.skill`、`cf-aeo-check.skill` のいずれか — をダウンロードし、claude.ai で **Settings → Capabilities**(*Code execution and file creation* を有効化)→ **Customize → Skills → Upload skill** の順に進みます。フルパイプラインにはサブエージェントのディスパッチが必要なため、上記のプラットフォームで動作します。ヒーロースキルは単体で動作します。

**ChatGPT およびその他の Agent Plugins 1.0 ホスト:** ContentForge は、OpenAI のベンダー中立な Agent Plugins 1.0 標準に準拠したルート `plugin.json` を同梱しています。サブエージェントのディスパッチを持たないホストでは、**ポータブル実行レーン**がフルパイプラインを 1 つの会話内で順次実行します — フェーズも、成果物も、品質ゲートも同じままで。

### 2. 最初のブランドを設定する

```
/contentforge:brand-setup
```

エージェントが、ブランドボイス、用語、ガードレール、引用ルール、内部リンク用のサイト構造を対話形式で設定します。ウェブサイトを指定すると、確認ステップ 1 回で検証済みのページインベントリを収集します。

### 3. コンテンツを生成する

```
/contentforge:create-content
```

コンテンツタイプ、ブランド、トピック、語数、オーディエンスを選択します。パイプラインは 10 フェーズ(リサーチ → ファクトチェック → ドラフト → ビジュアル → 検証 → 構成 → SEO → ヒューマナイズ → レビュー → 出力)を実行し、各フェーズの後に品質ゲートを適用し、完了したランを自身の成果物と突き合わせて監査したうえで、本物の `.docx` を書き出します。

### 4. 出力を確認する

```
~/Documents/ContentForge/<brand-slug>/<content-type>/<YYYY-MM>/<slug>.docx
```

この `.docx` には、本文と参考文献に加えて、4 つの付録 — SEO スコアカード、品質スコアカード、制作詳細、内部リンクマップ — が含まれます。

### 5. ループを閉じる

```
/contentforge:cf-aeo-check           # record which pieces AI engines cite
/contentforge:audit-content          # freshness-score the library; findings are RECORDED
/contentforge:cf-calendar --from-audit=latest   # next period: refreshes + gaps, from data
/contentforge:content-refresh        # execute a refresh at the audit's recommended scope
```

各コマンドは、前のコマンドが記録した内容を読み取ります — 新しいセッションでも、別の日でも、別のチームメンバーが実行しても。

---

## 対応プラットフォーム(v4.1.1)

9 つのネイティブプラットフォーム + claude.ai へのアップロード + 35 以上の Agent Skills クライアント:

| プラットフォーム | インストール |
|---|---|
| **Claude Code**(CLI + IDE) | `/plugin install contentforge@neels-plugins` |
| **Anthropic Cowork** | Plugins パネル → Add marketplace → `indranilbanerjee/neels-plugins` |
| **OpenAI Codex** | `codex plugin install contentforge@neels-plugins` |
| **Cursor 2.5+** | `/add-plugin contentforge@https://github.com/indranilbanerjee/contentforge` |
| **GitHub Copilot CLI** | `copilot plugin install contentforge@neels-plugins` |
| **Google Antigravity 2.0** | `agy plugin install https://github.com/indranilbanerjee/contentforge` |
| **Hermes Agent** | `hermes plugins install indranilbanerjee/contentforge` |
| **OpenClaw** | `openclaw plugins install git:github.com/indranilbanerjee/contentforge` |
| **Grok**(xAI Build CLI) | `grok plugin install indranilbanerjee/contentforge` |
| **claude.ai**(Web 版) | [リリース](https://github.com/indranilbanerjee/contentforge/releases/latest)からヒーロー `.skill` をアップロード |
| **ChatGPT / Agent Plugins 1.0 ホスト** | ルート `plugin.json` パッケージ + ポータブル実行レーン |

22 個すべての SKILL.md ファイルは、Agent Skills オープン標準によりプラットフォーム間で移植可能です — 互換クライアントから `https://github.com/indranilbanerjee/contentforge/tree/master/skills` を指定してください。

---

## アップデート

**Claude Code:** サードパーティ製マーケットプレイスは、デフォルトでは自動更新がオフになっています。一度だけ有効化してください: `/plugin` → **Marketplaces** タブ → `neels-plugins` → **Enable auto-update**。または手動で更新します: `/plugin marketplace update neels-plugins` を実行した後、`/plugin uninstall` + `/plugin install contentforge@neels-plugins` + `/reload-plugins` を実行してください。

**Cowork / claude.ai / Claude Desktop:** Plugins UI パネルを開く → ContentForge を削除 → マーケットプレイスから再インストール(再取得によって最新バージョンが取り込まれます)。

**Codex:** `codex plugin update contentforge` · **Cursor:** `/add-plugin` を再実行 · **Copilot CLI:** `copilot plugin update contentforge` · **Antigravity:** `agy plugin update contentforge` · **Hermes:** `hermes plugins update contentforge` · **OpenClaw:** `openclaw plugins update contentforge` · **Grok:** `grok plugin update contentforge` · **claude.ai アップロード:** 最新リリースから `.skill` を再ダウンロードして、再アップロードしてください。

---

## FAQ(要点)

**データはどこに保存されますか?** すべてローカルに保存されます: ブランドプロファイルとラン成果物は `~/.claude-marketing/<brand>/` に、納品物は `~/Documents/ContentForge/` に置かれます。お使いのプラットフォーム自身が行うモデル呼び出し以外に、データがどこかへ送信されることはありません。

**MCP や外部連携の接続は必要ですか?** いいえ。同梱の `.mcp.json` は意図的に空になっており、自動接続されるサーバーはゼロです。コネクタはオプトイン式のカタログです(`/contentforge:cf-connect`)。

**EU AI Act に対応していますか?** はい — 第 50 条の AI 開示アサーションを含む C2PA コンテンツ来歴署名に加えて、ブランドごとに設定できる開示レイヤー(不確実 ⇒ 開示のフェイルセーフ)を備えています。

**フルパイプラインは Claude Code 以外でも動作しますか?** はい — サブエージェントのディスパッチを持たないプラットフォームでは、ポータブル実行レーンが、すべてのゲートを維持したまま 10 フェーズすべてを順次実行します。唯一の例外は claude.ai への `.skill` アップロードです。これらは単体で動作するヒーロースキルであり、パイプラインそのものではありません。

---

## メンテナーについて

ContentForge の開発と保守は **[Indranil "Neel" Banerjee](https://indranil.in)** が行っています — 情報セキュリティにルーツを持ち、グロースマーケティング、エンタープライズのデジタルオペレーション、AI トランスフォーメーションへと活動の幅を広げてきたビルダーであり、システム思考の実践者です。ContentForge は、[Digital Marketing Pro](https://github.com/indranilbanerjee/digital-marketing-pro) および [SocialForge](https://github.com/indranilbanerjee/socialforge) とともに、3 プラグイン構成の **Neelverse Marketing Suite** を成しています。

ContentForge がチームの時間を節約できたなら、[⭐ リポジトリにスターを付けて](https://github.com/indranilbanerjee/contentforge/stargazers)、[プロジェクトへのスポンサー支援 ❤](https://github.com/sponsors/indranilbanerjee)もぜひご検討ください — 持続可能なリリースサイクルの維持につながります。

**ライセンス:** MIT · **セキュリティ:** [非公開アドバイザリ](https://github.com/indranilbanerjee/contentforge/security/advisories/new) · **Issues:** [GitHub Issues](https://github.com/indranilbanerjee/contentforge/issues)
