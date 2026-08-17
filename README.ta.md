# ContentForge

🌐 **Read this in:** [English](README.md) · [हिन्दी](README.hi.md) · [中文](README.zh-CN.md) · [日本語](README.ja.md) · [한국어](README.ko.md) · [Español](README.es.md) · [Português](README.pt-BR.md) · [العربية](README.ar.md) · [اردو](README.ur.md) · [தமிழ்](README.ta.md) · [বাংলা](README.bn.md) · [Русский](README.ru.md)

> **ஆங்கில README v4.1.1 (2026-08-17) உடன் ஒத்திசைக்கப்பட்டது.** [ஆங்கில README](README.md)-தான் அதிகாரப்பூர்வ மூல ஆவணம் — வெளியீட்டுக் குறிப்புகள், skills/commands முழுப் பட்டியல், கட்டமைப்பு விவரம், சிக்கல்தீர்வு வழிகாட்டி, முழுமையான FAQ ஆகியவை அங்கேயே உள்ளன. ContentForge-ஐ நிறுவவும், இயக்கவும், புதுப்பிக்கவும் தேவையான அனைத்தையும் இந்த மொழிபெயர்ப்பு உள்ளடக்கியுள்ளது.

> **இந்தக் காலாண்டில் நீங்கள் 30 கட்டுரைகளை வெளியிட வேண்டும் — அவை மனிதர் எழுதியதுபோல் ஒலிக்க வேண்டும், உண்மையான ஆதாரங்களை மேற்கோள் காட்ட வேண்டும், உங்கள் funnel-க்குள் இணைய வேண்டும், கறாராகச் சரிபார்க்கும் editor-இடமும் தேற வேண்டும். உங்கள் அணியில் இருப்பது மூன்று பேர். கையில் இருப்பது ஒன்பது வாரங்கள். உங்கள் கடந்த "AI எழுதிய" தொகுப்பு கற்பனையான புள்ளிவிவரங்களுக்காகக் கொடியிடப்பட்டது — அதற்கும் முந்தைய தொகுப்பு யாரும் கவனிக்காமலேயே அமைதியாகக் காலாவதியாகிப் போனது.**

ஒவ்வொரு தலைப்புக்கும் `/contentforge:create-content` ஐ இயக்குங்கள். 10-கட்டப் பைப்லைன், 43-வடிவ humanizer, ஒரு fact-checker subagent, மூன்று-வகை உள் இணைப்பு (internal linking), EU AI Act இணக்கத்திற்கான C2PA provenance ஆகியவற்றுடன் வெளியீட்டுக்குத் தயாரான `.docx`-ஐ உருவாக்கித் தருகிறது — ஒரு கட்டுரைக்கு 30–60 நிமிடங்களில். அதன் பிறகு, வேறு எந்த single-shot கருவியிடமும் இல்லாத அம்சம்: **lifecycle loop.** வெளியிடப்பட்ட ஒவ்வொரு கட்டுரையும் அளவிடப்பட்டு, தேய்மானத்திற்காக (decay) தணிக்கை செய்யப்பட்டு, அடுத்த calendar-க்கும் அடுத்த brief-க்கும் மீண்டும் ஊட்டப்படுகிறது — நிலைத்து நிற்கும் file contracts வழியாக; எனவே உங்கள் brand பற்றி அமைப்பு கற்றுக்கொண்டவை, அவற்றைக் கற்ற session முடிந்த பிறகும் நிலைத்திருக்கும்.

திறந்த மூல, நிறுவனத் தரத்திலான உள்ளடக்க உற்பத்தி அமைப்பு — **22 skills · 13 specialist agents · 10 quality gates · 43-வடிவ AI-கண்டறிதல் humanizer · ஓர் ஓட்டம் தன்னை முடிந்ததாக அறிவிக்கும் முன் ஒவ்வொரு gate-ஐயும் மீண்டும் தருவித்துச் சரிபார்க்கும் run auditor · 28 Python scripts, stdlib-மட்டுமே**. உருவாக்கியவர்: [Indranil Banerjee](https://indranil.in) · [LinkedIn](https://www.linkedin.com/in/askneelnow/) · [X](https://x.com/askneelnow).

**பதிப்பு 4.1.1** · [Changelog](CHANGELOG.md) · MIT உரிமம் · [இந்தத் திட்டத்தை ஆதரியுங்கள் ❤](https://github.com/sponsors/indranilbanerjee)

---

## ஏன் ContentForge

பெரும்பாலான AI எழுத்துக் கருவிகள் ஒரே draft-ஐ, ஒரே தொனியில், எந்தத் தரவாயில்களும் (quality gates) இன்றி உருவாக்கிவிட்டு, வெளியான மறுகணமே அந்தக் கட்டுரையை மறந்துவிடுகின்றன. ContentForge இதைத் தொடக்கம் முதல் முடிவு வரை சரி செய்கிறது:

| திறன் | ஏன் முக்கியம் |
|---|---|
| **ஒவ்வொரு கட்டத்திற்கும் பின் quality gate கொண்ட 10-கட்டப் பைப்லைன்** | தரமற்ற வெளியீடு அடுத்த கட்டங்களுக்குப் பரவும் முன்பே பிடிக்கப்பட்டு மீண்டும் இயக்கப்படுகிறது |
| **43-வடிவ AI-கண்டறிதல் humanizer** + சுய-விமர்சன meta-pass | வெளியீடு AI போல அல்ல, மனிதர் எழுதியதுபோல் வாசிக்கிறது — உணர்வால் அல்ல, அளவீட்டால் உறுதிப்படுத்தப்படுகிறது |
| **Fact-checker subagent** URL-களைச் சரிபார்த்து, கூற்றுகளைக் குறுக்குச்சான்று செய்கிறது | மேற்கோள்கள் உண்மையில் செயல்படுகின்றன, கற்பனையானவை அல்ல — ஒவ்வொரு புள்ளிவிவரமும் சரிபார்க்கப்பட்ட ledger பதிவைச் சுட்டுகிறது |
| **மூன்று-வகை உள் இணைப்பு** (topical / commercial / authority) | உள்ளடக்கம் தனித்து நிற்கும் பக்கமாக அல்ல, ஒரு funnel-ஆக மாறுகிறது |
| SEO + Quality + Production + Internal-Link பின்னிணைப்புகளுடன் **உண்மையான `.docx` வெளியீடு** | உங்கள் editor-க்கு markdown அல்ல, நேரடியாகப் பயன்படுத்தக்கூடிய Word கோப்பு கிடைக்கிறது |
| **Artifacts-இலிருந்து ஒவ்வொரு gate-ஐயும் மீண்டும் தருவிக்கும் run auditor** | "பைப்லைன் முடிந்ததாகச் சொல்கிறது" என்பதும் "artifacts அதை நிரூபிக்கின்றன" என்பதும் யாரும் அறியாமல் விலகிச் செல்லவே முடியாது |
| **Lifecycle loop (v4.0)** — audit → refresh → measure → plan, file contracts-ஆல் இணைக்கப்பட்டது | வெளியிட்ட உள்ளடக்கம் "அனுப்பிவிட்டு மறப்பது" அல்ல: தேய்மானம் கண்டறியப்படுகிறது, refresh-கள் தரவின் அடிப்படையில் முன்னுரிமைப்படுத்தப்படுகின்றன |
| EU AI Act Article 50 இணக்கத்திற்கான **C2PA content provenance கையொப்பம்** | EU சந்தைகளில் விநியோகிக்கப்படும் நீள்வடிவ AI-உதவி உள்ளடக்கத்திற்கு 2 ஆகஸ்ட் 2026 முதல் provenance கட்டாயம் |

## உண்மையான ஓட்டத்திலிருந்து, உண்மையான முடிவுகள்

ஒரு end-to-end சரிபார்ப்பு ஓட்டம் (ஆகஸ்ட் 2026, digital-preservation துறை சார்ந்த ஒரு சோதனை brand, "link rot" என்ற keyword மீதான 1,200-சொல் blog) — நடந்தது நடந்தபடியே அறிவிக்கப்படுகிறது:

- ஒரு புள்ளிவிவரத்தை research கட்டம் தவறாகப் புரிந்துகொண்டதை fact-checking கட்டம் கண்டுபிடித்தது; திருத்தப்பட்ட வாசகத்தைச் சரிபார்க்கப்பட்ட ledger-இல் பூட்டி, மூல வாக்கியத்தை draft-இல் இடம்பெறவே தடை செய்தது. அந்தத் திருத்தம், வார்த்தைக்கு வார்த்தை மாறாமல், வழங்கப்பட்ட Word கோப்பு வரை நிலைத்தது.
- Validation கட்டம் 42 கூற்றுகளை ledger-உடன் diff செய்தது: **hallucination எதுவுமில்லை**.
- Humanizer 7 வகைகளில் 20 AI-வடிவ நிகழ்வுகளை நீக்கியது (ஒவ்வொரு வடிவத்திற்கும் தனித்தனியாக அளவிடப்பட்டு, ஒவ்வொரு திருத்தத்திற்கும் before/after பதிவுடன்) — அதே நேரத்தில் ஒவ்வொரு உண்மை, மேற்கோள், SEO இடம்பெறலையும் byte அளவில் மாறாமல் காத்தது.
- Review கட்டம் **9.0/10 (grade A)** மதிப்பீட்டில் ஒப்புதல் அளித்தது — content quality 8.8, citation integrity 8.9, brand compliance 9.6, SEO 8.6, readability 8.8.
- Run auditor அனைத்தையும் disk-இல் உள்ள artifacts-இலிருந்து மீண்டும் தருவித்தது: **14 சோதனைகள் வெற்றி, 0 தோல்வி** — அதன் பிறகுதான் ஓட்டம் தன்னை completed என அறிவிக்க அனுமதிக்கப்பட்டது.

இங்கு முக்கியமான விஷயம், பைப்லைன் ஒருபோதும் தவறே செய்யாது என்பதல்ல — அதன் தவறுகள் அதன் சொந்த இயந்திரத்தாலேயே, பதிவோடு, உங்கள் editor கோப்பைப் பார்ப்பதற்கு முன்பே பிடிக்கப்படுகின்றன என்பதே. உண்மையான artifacts-ஐ (உண்மையான chart, உண்மையான before/after திருத்தங்கள், உண்மையான scorecard) [ஆங்கில README](README.md#examples)-இல் காணலாம்.

---

## விரைவுத் தொடக்கம்

### 1. நிறுவுதல்

**Claude Code (CLI அல்லது VS Code/JetBrains extension):**

```bash
/plugin marketplace add indranilbanerjee/neels-plugins
/plugin install contentforge@neels-plugins
```

**Anthropic Cowork:** UI-இல் **Plugins** பலகையைத் திறக்கவும் → Add marketplace → `indranilbanerjee/neels-plugins` → ContentForge-ஐ நிறுவவும். (Cowork-இல் `/plugin` slash கட்டளைகள் வேலை செய்யாது — UI பலகையையே பயன்படுத்தவும்.) பிறகு, அணி முழுவதும் பகிரக்கூடிய வெளியீட்டுக்காக Google Drive-ஐ இணைக்க `/contentforge:cf-cowork-setup` ஐ ஒருமுறை இயக்கவும்.

**OpenAI Codex (CLI + IDE + App):**

```bash
codex plugin marketplace add indranilbanerjee/neels-plugins
codex plugin install contentforge@neels-plugins
```

**பிற தளங்கள்:**

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

**claude.ai (இணையம்):** [சமீபத்திய release](https://github.com/indranilbanerjee/contentforge/releases/latest)-இலிருந்து ஒரு hero skill-ஐப் பதிவிறக்கவும் — `cf-brief.skill`, `cf-social-adapt.skill`, `cf-translate.skill`, `cf-video-script.skill`, அல்லது `cf-aeo-check.skill` — பிறகு claude.ai-இல்: **Settings → Capabilities** (*Code execution and file creation*-ஐ இயக்கவும்) → **Customize → Skills → Upload skill**. முழுப் பைப்லைனுக்கு subagent dispatch தேவை; அது மேலே உள்ள தளங்களில் இயங்கும் — hero skills மட்டும் தனித்தே செயல்படும்.

**ChatGPT மற்றும் பிற Agent Plugins 1.0 hosts:** OpenAI-இன் vendor-நடுநிலை Agent Plugins 1.0 தரநிலையில் ContentForge ஒரு root `plugin.json`-ஐ வழங்குகிறது. Subagent dispatch இல்லாத hosts-இல், **portable execution lane** முழுப் பைப்லைனையும் ஒரே உரையாடலில் வரிசையாக இயக்குகிறது — அதே கட்டங்கள், அதே artifacts, அதே quality gates.

### 2. உங்கள் முதல் brand-ஐ அமைக்கவும்

```
/contentforge:brand-setup
```

Brand voice, terminology, guardrails, மேற்கோள் விதிகள், உள் இணைப்புக்கான உங்கள் site கட்டமைப்பு — இவை அனைத்தின் வழியாகவும் agent உங்களைப் படிப்படியாக அழைத்துச் செல்கிறது. ஒரு website-ஐக் கொடுத்தால், ஒரே ஒரு உறுதிப்படுத்தல் படியில் சரிபார்க்கப்பட்ட page inventory-ஐ அது சேகரித்துக்கொள்கிறது.

### 3. உள்ளடக்கத்தை உருவாக்குங்கள்

```
/contentforge:create-content
```

Content type, brand, தலைப்பு, சொல் எண்ணிக்கை, வாசகர் குழு ஆகியவற்றைத் தேர்ந்தெடுங்கள். பைப்லைன் 10 கட்டங்களை இயக்கி (research → fact-check → draft → visuals → validate → structure → SEO → humanize → review → output), ஒவ்வொரு கட்டத்திற்கும் பின் quality gate-ஐ அமல்படுத்தி, முடிந்த ஓட்டத்தை அதன் சொந்த artifacts-உக்கு எதிராகத் தணிக்கை செய்து, உண்மையான `.docx`-ஐ எழுதுகிறது.

### 4. உங்கள் வெளியீட்டைக் கண்டறியுங்கள்

```
~/Documents/ContentForge/<brand-slug>/<content-type>/<YYYY-MM>/<slug>.docx
```

இந்த `.docx`-இல் மைய உரை, references, நான்கு பின்னிணைப்புகள் உள்ளன: SEO scorecard, quality scorecard, production விவரங்கள், internal link map.

### 5. Loop-ஐ முழுமையாக்குங்கள்

```
/contentforge:cf-aeo-check           # record which pieces AI engines cite
/contentforge:audit-content          # freshness-score the library; findings are RECORDED
/contentforge:cf-calendar --from-audit=latest   # next period: refreshes + gaps, from data
/contentforge:content-refresh        # execute a refresh at the audit's recommended scope
```

முந்தைய கட்டளை பதிவு செய்ததை ஒவ்வொரு கட்டளையும் படித்துப் பயன்படுத்துகிறது — புதிய session-இல், வேறொரு நாளில், வேறொரு சக ஊழியர் இயக்கினாலும் சரி.

---

## ஆதரிக்கப்படும் தளங்கள் (v4.1.1)

ஒன்பது native தளங்கள் + claude.ai uploads + 35+ Agent Skills clients:

| தளம் | நிறுவல் |
|---|---|
| **Claude Code** (CLI + IDE) | `/plugin install contentforge@neels-plugins` |
| **Anthropic Cowork** | Plugins பலகை → Add marketplace → `indranilbanerjee/neels-plugins` |
| **OpenAI Codex** | `codex plugin install contentforge@neels-plugins` |
| **Cursor 2.5+** | `/add-plugin contentforge@https://github.com/indranilbanerjee/contentforge` |
| **GitHub Copilot CLI** | `copilot plugin install contentforge@neels-plugins` |
| **Google Antigravity 2.0** | `agy plugin install https://github.com/indranilbanerjee/contentforge` |
| **Hermes Agent** | `hermes plugins install indranilbanerjee/contentforge` |
| **OpenClaw** | `openclaw plugins install git:github.com/indranilbanerjee/contentforge` |
| **Grok** (xAI Build CLI) | `grok plugin install indranilbanerjee/contentforge` |
| **claude.ai** (இணையம்) | [releases](https://github.com/indranilbanerjee/contentforge/releases/latest)-இலிருந்து ஒரு hero `.skill`-ஐ upload செய்யவும் |
| **ChatGPT / Agent Plugins 1.0 hosts** | Root `plugin.json` தொகுப்பு + portable execution lane |

அனைத்து 22 SKILL.md கோப்புகளும் Agent Skills திறந்த தரநிலை வழியாகத் தளம்-கடந்து portable ஆனவை — இணக்கமான எந்த client-ஐயும் `https://github.com/indranilbanerjee/contentforge/tree/master/skills` நோக்கிச் சுட்டினால் போதும்.

---

## புதுப்பித்தல்

**Claude Code:** third-party marketplaces-க்கு auto-update இயல்பாக OFF நிலையில் இருக்கும். ஒருமுறை இயக்கிவிடுங்கள்: `/plugin` → **Marketplaces** tab → `neels-plugins` → **Enable auto-update**. அல்லது கைமுறையாக: `/plugin marketplace update neels-plugins`, பிறகு `/plugin uninstall` + `/plugin install contentforge@neels-plugins` + `/reload-plugins`.

**Cowork / claude.ai / Claude Desktop:** Plugins UI பலகையைத் திறந்து → ContentForge-ஐ நீக்கி → marketplace-இலிருந்து மீண்டும் நிறுவவும் (மீண்டும் இழுக்கும்போது சமீபத்திய பதிப்பு பெறப்படும்).

**Codex:** `codex plugin update contentforge` · **Cursor:** `/add-plugin`-ஐ மீண்டும் இயக்கவும் · **Copilot CLI:** `copilot plugin update contentforge` · **Antigravity:** `agy plugin update contentforge` · **Hermes:** `hermes plugins update contentforge` · **OpenClaw:** `openclaw plugins update contentforge` · **Grok:** `grok plugin update contentforge` · **claude.ai uploads:** சமீபத்திய release-இலிருந்து `.skill`-ஐ மீண்டும் பதிவிறக்கி, மீண்டும் upload செய்யவும்.

---

## FAQ (அத்தியாவசியங்கள்)

**என் தரவு எங்கே இருக்கிறது?** அனைத்தும் உங்கள் கணினியிலேயே: brand profiles-உம் run artifacts-உம் `~/.claude-marketing/<brand>/`-இன் கீழ், deliverables `~/Documents/ContentForge/`-இன் கீழ். உங்கள் சொந்தத் தளம் செய்யும் model அழைப்புகளைத் தவிர, வேறு எதுவும் எங்கும் அனுப்பப்படுவதில்லை.

**MCP-கள்/integrations இணைக்க வேண்டுமா?** தேவையில்லை. வழங்கப்படும் `.mcp.json` வேண்டுமென்றே காலியாக உள்ளது — தானாக இணையும் servers எதுவுமில்லை. Connectors ஒரு opt-in பட்டியல் (`/contentforge:cf-connect`).

**இது EU AI Act-க்குத் தயாரா?** ஆம் — Article 50 AI-disclosure assertion-உடன் கூடிய C2PA content provenance கையொப்பம், அத்துடன் brand-அளவில் கட்டமைக்கக்கூடிய disclosure அடுக்கு (உறுதியில்லை என்றால் ⇒ வெளிப்படுத்து என்ற fail-safe).

**Claude Code-க்கு வெளியே முழுப் பைப்லைன் இயங்குமா?** ஆம் — subagent dispatch இல்லாத தளங்களில், portable execution lane அனைத்து 10 கட்டங்களையும் ஒவ்வொரு gate-உம் அப்படியே இருக்க வரிசையாக இயக்குகிறது. claude.ai `.skill` uploads மட்டுமே விதிவிலக்கு: அவை தனித்தியங்கும் hero skills, முழுப் பைப்லைன் அல்ல.

---

## பராமரிப்பாளர் பற்றி

ContentForge-ஐ உருவாக்கிப் பராமரிப்பவர் **[Indranil "Neel" Banerjee](https://indranil.in)** — information security-இல் வேரூன்றி, growth marketing, enterprise digital operations, AI transformation எனப் பரந்த இரண்டாவது இன்னிங்ஸ் கொண்ட builder-உம் systems thinker-உம் ஆவார். [Digital Marketing Pro](https://github.com/indranilbanerjee/digital-marketing-pro), [SocialForge](https://github.com/indranilbanerjee/socialforge) ஆகியவற்றுடன் இணைந்த மூன்று-plugin **Neelverse Marketing Suite**-இன் ஒரு பகுதி.

ContentForge உங்கள் அணியின் நேரத்தை மிச்சப்படுத்தினால், [⭐ repo-வுக்கு star கொடுங்கள்](https://github.com/indranilbanerjee/contentforge/stargazers); மேலும் [திட்டத்திற்கு sponsor செய்வதையும் ❤](https://github.com/sponsors/indranilbanerjee) பரிசீலியுங்கள் — இது release வேகத்தை நிலையாகத் தொடர உதவுகிறது.

**உரிமம்:** MIT · **பாதுகாப்பு:** [private advisories](https://github.com/indranilbanerjee/contentforge/security/advisories/new) · **சிக்கல்கள்:** [GitHub Issues](https://github.com/indranilbanerjee/contentforge/issues)
