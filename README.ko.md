# ContentForge

🌐 **Read this in:** [English](README.md) · [हिन्दी](README.hi.md) · [中文](README.zh-CN.md) · [日本語](README.ja.md) · [한국어](README.ko.md) · [Español](README.es.md) · [Português](README.pt-BR.md) · [العربية](README.ar.md) · [اردو](README.ur.md) · [தமிழ்](README.ta.md) · [বাংলা](README.bn.md) · [Русский](README.ru.md)

> **영문 README v4.1.1 (2026-08-17)과 동기화되었습니다.** [영문 README](README.md)가 공식 원본입니다 — 릴리스 노트, 전체 스킬/명령어 카탈로그, 아키텍처, 문제 해결 가이드, 전체 FAQ는 모두 그곳에 있습니다. 이 번역본에는 ContentForge를 설치하고, 실행하고, 업데이트하는 데 필요한 모든 내용이 담겨 있습니다.

> **이번 분기에 기사 30편을 내보내야 합니다. 사람이 쓴 것처럼 읽히고, 실제 출처를 인용하고, 퍼널로 연결되며, 꼼꼼히 확인하는 편집자의 검수까지 통과해야 합니다. 팀원은 3명, 남은 시간은 9주. 지난번 "AI가 쓴" 원고 묶음은 환각으로 지어낸 통계 때문에 반려되었고, 그 전 묶음은 조용히 낡아 가는데도 아무도 눈치채지 못했습니다.**

각 주제에 대해 `/contentforge:create-content`를 실행하십시오. 10단계 파이프라인이 43가지 패턴의 휴머나이저, 팩트체커 서브에이전트, 3가지 범주의 내부 링크, EU AI Act 준수를 위한 C2PA 출처 증명을 갖춘, 즉시 게재 가능한 `.docx`를 편당 30–60분 만에 만들어 냅니다. 그리고 어떤 원샷 도구도 갖지 못한 것이 이어집니다: **라이프사이클 루프.** 게재된 모든 콘텐츠는 성과가 측정되고, 노후화 여부가 감사되며, 다음 캘린더와 다음 브리프에 다시 반영됩니다 — 지속되는 파일 계약을 통해서입니다. 시스템이 브랜드에 대해 학습한 내용은 학습이 이루어진 세션이 끝나도 살아남습니다.

오픈소스 엔터프라이즈 콘텐츠 프로덕션 시스템 — **22개 스킬 · 13개 전문 에이전트 · 10개 품질 게이트 · 43가지 패턴의 AI 탐지 휴머나이저 · 실행이 스스로 완료를 선언하기 전에 모든 게이트를 재검증하는 런 오디터 · 표준 라이브러리만 사용하는 28개 Python 스크립트**. 제작자: [Indranil Banerjee](https://indranil.in) · [LinkedIn](https://www.linkedin.com/in/askneelnow/) · [X](https://x.com/askneelnow).

**버전 4.1.1** · [체인지로그](CHANGELOG.md) · MIT 라이선스 · [이 프로젝트 후원하기 ❤](https://github.com/sponsors/indranilbanerjee)

---

## 왜 ContentForge인가

대부분의 AI 글쓰기 도구는 초안 하나를, 톤 하나로, 품질 게이트 없이 만들어 내고, 결과물이 나가는 순간 그 콘텐츠를 잊어버립니다. ContentForge는 이 문제를 처음부터 끝까지 해결합니다:

| 기능 | 왜 중요한가 |
|---|---|
| **모든 단계 뒤에 품질 게이트가 있는 10단계 파이프라인** | 불량 출력이 다운스트림으로 전파되기 전에 잡혀서 재실행됩니다 |
| **43가지 패턴의 AI 탐지 휴머나이저** + 자기 비평 메타 패스 | 결과물이 AI가 아니라 사람이 쓴 글로 읽힙니다 — 감이 아니라 측정으로 확인합니다 |
| **팩트체커 서브에이전트**가 URL을 검증하고 주장을 교차 확인 | 인용이 실제로 작동하며 환각이 아닙니다 — 모든 통계가 검증된 원장 항목으로 추적됩니다 |
| **3가지 범주의 내부 링크** (토피컬 / 커머셜 / 권위) | 콘텐츠가 고립된 페이지가 아니라 퍼널이 됩니다 |
| SEO + 품질 + 프로덕션 + 내부 링크 부록이 포함된 **실제 `.docx` 출력** | 편집자가 마크다운이 아니라 바로 열리는 Word 파일을 받습니다 |
| **아티팩트로부터 모든 게이트를 재도출하는 런 오디터** | "파이프라인이 끝났다고 말한다"와 "아티팩트가 끝났음을 증명한다"가 조용히 어긋나는 일이 결코 없습니다 |
| **라이프사이클 루프(v4.0)** — 감사 → 리프레시 → 측정 → 계획, 파일 계약으로 연결 | 게재된 콘텐츠가 더 이상 쏘고 잊는 대상이 아닙니다: 노후화가 감지되고, 리프레시 우선순위가 데이터로 정해집니다 |
| EU AI Act Article 50 준수를 위한 **C2PA 콘텐츠 출처 서명** | 2026년 8월 2일부터 EU 시장에 배포되는 AI 지원 장문 콘텐츠에는 출처 증명이 필요합니다 |

## 실제 실행에서 얻은 실제 결과

엔드투엔드 검증 실행(2026년 8월, 디지털 보존 분야 테스트 브랜드, 키워드 "link rot"에 대한 1,200단어 블로그) — 실제로 일어난 그대로 보고합니다:

- 팩트체크 단계가 리서치 단계의 통계 오독을 잡아냈고, 수정된 문구를 검증 원장에 고정한 뒤 원래 문장을 초안에서 금지했습니다. 이 수정은 한 글자도 바뀌지 않은 채 최종 전달된 Word 파일까지 그대로 살아남았습니다.
- 검증 단계가 42개의 주장을 원장과 대조했습니다: **환각 0건**.
- 휴머나이저가 7개 범주에 걸쳐 20건의 AI 패턴 사례를 제거하면서(패턴별로 측정, 모든 수정에 대해 전/후 기록) 모든 사실, 인용, SEO 배치를 바이트 단위로 그대로 유지했습니다.
- 리뷰 단계가 **9.0/10 (A 등급)** 으로 승인했습니다 — 콘텐츠 품질 8.8, 인용 무결성 8.9, 브랜드 준수 9.6, SEO 8.6, 가독성 8.8.
- 런 오디터가 디스크에 있는 아티팩트로부터 모든 것을 재도출했습니다: **14개 검사 통과, 0개 실패** — 그런 뒤에야 실행이 스스로를 완료로 선언할 수 있었습니다.

요점은 파이프라인이 절대 실수하지 않는다는 것이 아닙니다 — 실수가 나더라도 편집자가 파일을 보기 전에, 기록에 남는 방식으로, 파이프라인 자체의 장치가 잡아낸다는 것입니다. 실제 아티팩트(실제 차트, 실제 전/후 수정 내역, 실제 스코어카드)는 [영문 README](README.md#examples)에서 확인할 수 있습니다.

---

## 빠른 시작

### 1. 설치

**Claude Code (CLI 또는 VS Code/JetBrains 확장):**

```bash
/plugin marketplace add indranilbanerjee/neels-plugins
/plugin install contentforge@neels-plugins
```

**Anthropic Cowork:** UI에서 **Plugins** 패널 열기 → Add marketplace → `indranilbanerjee/neels-plugins` → ContentForge 설치. (`/plugin` 슬래시 명령은 Cowork에서 작동하지 않습니다 — UI 패널을 사용하십시오.) 그다음 `/contentforge:cf-cowork-setup`을 한 번 실행하여 팀 공유가 가능한 출력을 위해 Google Drive를 연결하십시오.

**OpenAI Codex (CLI + IDE + 앱):**

```bash
codex plugin marketplace add indranilbanerjee/neels-plugins
codex plugin install contentforge@neels-plugins
```

**기타 플랫폼:**

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

**claude.ai (웹):** [최신 릴리스](https://github.com/indranilbanerjee/contentforge/releases/latest)에서 히어로 스킬 — `cf-brief.skill`, `cf-social-adapt.skill`, `cf-translate.skill`, `cf-video-script.skill`, `cf-aeo-check.skill` 중 하나 — 을 내려받은 뒤, claude.ai에서 **Settings → Capabilities** (*Code execution and file creation* 활성화) → **Customize → Skills → Upload skill** 순서로 업로드하십시오. 전체 파이프라인은 서브에이전트 디스패치가 필요하므로 위에 나열된 플랫폼에서 실행되며, 히어로 스킬은 단독으로 작동합니다.

**ChatGPT 및 기타 Agent Plugins 1.0 호스트:** ContentForge는 OpenAI의 벤더 중립 표준인 Agent Plugins 1.0에 따라 루트 `plugin.json`을 제공합니다. 서브에이전트 디스패치가 없는 호스트에서는 **포터블 실행 레인**이 하나의 대화 안에서 전체 파이프라인을 순차 실행합니다 — 동일한 단계, 동일한 아티팩트, 동일한 품질 게이트 그대로입니다.

### 2. 첫 브랜드 설정

```
/contentforge:brand-setup
```

에이전트가 브랜드 보이스, 용어, 가드레일, 인용 규칙, 그리고 내부 링크를 위한 사이트 구조 설정을 안내합니다. 웹사이트 주소를 알려 주면 확인 한 번으로 검증된 페이지 인벤토리를 수집합니다.

### 3. 콘텐츠 생성

```
/contentforge:create-content
```

콘텐츠 유형, 브랜드, 주제, 단어 수, 대상 독자를 선택하십시오. 파이프라인이 10단계(리서치 → 팩트체크 → 초안 → 비주얼 → 검증 → 구조화 → SEO → 휴머나이즈 → 리뷰 → 출력)를 실행하고, 각 단계 뒤에 품질 게이트를 적용하며, 완료된 실행을 자체 아티팩트와 대조해 감사한 뒤, 실제 `.docx`를 작성합니다.

### 4. 결과물 찾기

```
~/Documents/ContentForge/<brand-slug>/<content-type>/<YYYY-MM>/<slug>.docx
```

`.docx`에는 본문, 참고 문헌, 그리고 4개의 부록 — SEO 스코어카드, 품질 스코어카드, 프로덕션 세부 정보, 내부 링크 맵 — 이 포함됩니다.

### 5. 루프 닫기

```
/contentforge:cf-aeo-check           # record which pieces AI engines cite
/contentforge:audit-content          # freshness-score the library; findings are RECORDED
/contentforge:cf-calendar --from-audit=latest   # next period: refreshes + gaps, from data
/contentforge:content-refresh        # execute a refresh at the audit's recommended scope
```

모든 명령은 이전 명령이 기록한 내용을 읽습니다 — 새 세션에서든, 다른 날이든, 다른 팀원이 실행하든 마찬가지입니다.

---

## 지원 플랫폼 (v4.1.1)

9개 네이티브 플랫폼 + claude.ai 업로드 + 35개 이상의 Agent Skills 클라이언트:

| 플랫폼 | 설치 방법 |
|---|---|
| **Claude Code** (CLI + IDE) | `/plugin install contentforge@neels-plugins` |
| **Anthropic Cowork** | Plugins 패널 → Add marketplace → `indranilbanerjee/neels-plugins` |
| **OpenAI Codex** | `codex plugin install contentforge@neels-plugins` |
| **Cursor 2.5+** | `/add-plugin contentforge@https://github.com/indranilbanerjee/contentforge` |
| **GitHub Copilot CLI** | `copilot plugin install contentforge@neels-plugins` |
| **Google Antigravity 2.0** | `agy plugin install https://github.com/indranilbanerjee/contentforge` |
| **Hermes Agent** | `hermes plugins install indranilbanerjee/contentforge` |
| **OpenClaw** | `openclaw plugins install git:github.com/indranilbanerjee/contentforge` |
| **Grok** (xAI Build CLI) | `grok plugin install indranilbanerjee/contentforge` |
| **claude.ai** (웹) | [릴리스](https://github.com/indranilbanerjee/contentforge/releases/latest)에서 히어로 `.skill` 업로드 |
| **ChatGPT / Agent Plugins 1.0 호스트** | 루트 `plugin.json` 패키지 + 포터블 실행 레인 |

22개의 SKILL.md 파일 전부가 Agent Skills 오픈 표준을 통해 플랫폼 간 이식이 가능합니다 — 호환되는 어떤 클라이언트든 `https://github.com/indranilbanerjee/contentforge/tree/master/skills`를 가리키게 하면 됩니다.

---

## 업데이트

**Claude Code:** 서드파티 마켓플레이스는 기본적으로 자동 업데이트가 꺼져 있습니다. 한 번만 켜 두십시오: `/plugin` → **Marketplaces** 탭 → `neels-plugins` → **Enable auto-update**. 또는 수동으로: `/plugin marketplace update neels-plugins` 실행 후 `/plugin uninstall` + `/plugin install contentforge@neels-plugins` + `/reload-plugins`.

**Cowork / claude.ai / Claude Desktop:** Plugins UI 패널 열기 → ContentForge 제거 → 마켓플레이스에서 재설치(다시 받아오면서 최신 버전이 설치됩니다).

**Codex:** `codex plugin update contentforge` · **Cursor:** `/add-plugin` 재실행 · **Copilot CLI:** `copilot plugin update contentforge` · **Antigravity:** `agy plugin update contentforge` · **Hermes:** `hermes plugins update contentforge` · **OpenClaw:** `openclaw plugins update contentforge` · **Grok:** `grok plugin update contentforge` · **claude.ai 업로드:** 최신 릴리스에서 `.skill`을 다시 내려받아 다시 업로드하십시오.

---

## FAQ (핵심)

**내 데이터는 어디에 저장됩니까?** 모든 것이 로컬에 있습니다: 브랜드 프로필과 실행 아티팩트는 `~/.claude-marketing/<brand>/` 아래에, 결과물은 `~/Documents/ContentForge/` 아래에 저장됩니다. 사용 중인 플랫폼이 직접 수행하는 모델 호출 외에는 어떤 것도 외부로 전송되지 않습니다.

**MCP나 통합을 연결해야 합니까?** 아니요. 기본 제공되는 `.mcp.json`은 의도적으로 비어 있습니다 — 자동 연결되는 서버가 하나도 없습니다. 커넥터는 옵트인 카탈로그로 제공됩니다(`/contentforge:cf-connect`).

**EU AI Act에 대비되어 있습니까?** 예 — Article 50의 AI 공개 어설션을 포함한 C2PA 콘텐츠 출처 서명에, 브랜드별로 구성 가능한 공개 레이어(불확실하면 공개하는 페일세이프)까지 갖추고 있습니다.

**전체 파이프라인이 Claude Code 밖에서도 실행됩니까?** 예 — 서브에이전트 디스패치가 없는 플랫폼에서는 포터블 실행 레인이 모든 게이트를 그대로 유지한 채 10단계 전부를 순차 실행합니다. 유일한 예외는 claude.ai의 `.skill` 업로드입니다: 이는 파이프라인이 아니라 독립 실행형 히어로 스킬입니다.

---

## 메인테이너 소개

ContentForge는 **[Indranil "Neel" Banerjee](https://indranil.in)** 가 만들고 유지 관리합니다 — 정보 보안에 뿌리를 두고 그로스 마케팅, 엔터프라이즈 디지털 운영, AI 트랜스포메이션으로 두 번째 여정을 이어 온 빌더이자 시스템 사상가입니다. [Digital Marketing Pro](https://github.com/indranilbanerjee/digital-marketing-pro), [SocialForge](https://github.com/indranilbanerjee/socialforge)와 함께 3개 플러그인으로 구성된 **Neelverse Marketing Suite**의 일부입니다.

ContentForge가 팀의 시간을 아껴 준다면 [⭐ 리포지토리에 스타](https://github.com/indranilbanerjee/contentforge/stargazers)를 눌러 주시고, [프로젝트 후원 ❤](https://github.com/sponsors/indranilbanerjee)도 고려해 주십시오 — 지속 가능한 릴리스 주기를 유지하는 데 힘이 됩니다.

**라이선스:** MIT · **보안:** [비공개 보안 권고](https://github.com/indranilbanerjee/contentforge/security/advisories/new) · **이슈:** [GitHub Issues](https://github.com/indranilbanerjee/contentforge/issues)
