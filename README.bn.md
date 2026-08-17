# ContentForge

🌐 **Read this in:** [English](README.md) · [हिन्दी](README.hi.md) · [中文](README.zh-CN.md) · [日本語](README.ja.md) · [한국어](README.ko.md) · [Español](README.es.md) · [Português](README.pt-BR.md) · [العربية](README.ar.md) · [اردو](README.ur.md) · [தமிழ்](README.ta.md) · [বাংলা](README.bn.md) · [Русский](README.ru.md)

> **ইংরেজি README v4.1.2 (2026-08-17)-এর সঙ্গে সিঙ্ক করা।** [ইংরেজি README](README.md)-ই সত্যের একমাত্র উৎস — রিলিজ নোট, স্কিল ও কমান্ডের পূর্ণাঙ্গ ক্যাটালগ, আর্কিটেকচার, ট্রাবলশুটিং এবং সম্পূর্ণ FAQ সেখানেই রয়েছে। ContentForge ইনস্টল, চালানো ও আপডেট করতে যা যা লাগে, তার সবই এই অনুবাদে পাবেন।

> **এই কোয়ার্টারে আপনাকে 30টি আর্টিকেল শিপ করতে হবে — এমন আর্টিকেল যা পড়তে মানুষের লেখা লাগে, সত্যিকারের সোর্স উদ্ধৃত করে, আপনার ফানেলের সঙ্গে লিংক হয়, আর এমন একজন এডিটরের পরীক্ষায় টেকে যিনি সত্যিই যাচাই করেন। আপনার টিমে মানুষ তিনজন। হাতে সময় নয় সপ্তাহ। আপনার শেষ "AI-লেখা" ব্যাচ হ্যালুসিনেটেড পরিসংখ্যানের জন্য ধরা পড়েছিল — আর তার আগের ব্যাচটা চুপচাপ বাসি হয়ে গিয়েছিল, কেউ খেয়ালই করেনি।**

প্রতিটি টপিকের জন্য `/contentforge:create-content` চালান। 10-ফেজ পাইপলাইন একটি প্রকাশনা-প্রস্তুত `.docx` তৈরি করে — সঙ্গে 43-প্যাটার্ন হিউম্যানাইজার, একটি ফ্যাক্ট-চেকার সাবএজেন্ট, তিন-ক্যাটাগরি ইন্টারনাল লিংকিং, এবং EU AI Act কমপ্লায়েন্সের জন্য C2PA প্রভেন্যান্স — প্রতিটি লেখায় সময় লাগে 30–60 মিনিট। তারপর আসে সেই অংশ, যা কোনো সিঙ্গল-শট টুলের নেই: **লাইফসাইকেল লুপ।** প্রকাশিত প্রতিটি লেখা পরিমাপ করা হয়, ফ্রেশনেস-ক্ষয়ের জন্য অডিট হয়, এবং পরের ক্যালেন্ডার ও পরের ব্রিফে ফিরে আসে — টেকসই ফাইল কন্ট্র্যাক্টের মাধ্যমে, যাতে আপনার ব্র্যান্ড সম্পর্কে সিস্টেম যা শেখে, তা শেখার সেশনটি ফুরিয়ে গেলেও টিকে থাকে।

ওপেন-সোর্স এন্টারপ্রাইজ কনটেন্ট প্রোডাকশন সিস্টেম — **22টি স্কিল · 13টি বিশেষজ্ঞ এজেন্ট · 10টি কোয়ালিটি গেট · 43-প্যাটার্ন AI-ডিটেকশন হিউম্যানাইজার · এমন এক রান অডিটর যা কোনো রান নিজেকে সম্পন্ন ঘোষণা করার আগে প্রতিটি গেট নতুন করে যাচাই করে · 28টি Python স্ক্রিপ্ট, শুধুই stdlib**। নির্মাতা [Indranil Banerjee](https://indranil.in) · [LinkedIn](https://www.linkedin.com/in/askneelnow/) · [X](https://x.com/askneelnow)।

**ভার্সন 4.1.2** · [চেঞ্জলগ](CHANGELOG.md) · MIT লাইসেন্স · [প্রজেক্টটি স্পনসর করুন ❤](https://github.com/sponsors/indranilbanerjee)

---

## কেন ContentForge

বেশিরভাগ AI রাইটিং টুল একটাই খসড়া দেয়, একটাই টোনে, কোনো কোয়ালিটি গেট ছাড়া — আর লেখাটা শিপ হওয়ার মুহূর্তেই তাকে ভুলে যায়। ContentForge এই সমস্যা গোড়া থেকে শেষ পর্যন্ত সমাধান করে:

| সক্ষমতা | কেন এটা গুরুত্বপূর্ণ |
|---|---|
| **প্রতিটি ফেজের পরে কোয়ালিটি গেটসহ 10-ফেজ পাইপলাইন** | খারাপ আউটপুট ডাউনস্ট্রিমে ছড়িয়ে পড়ার আগেই ধরা পড়ে এবং আবার চালানো হয় |
| **43-প্যাটার্ন AI-ডিটেকশন হিউম্যানাইজার** + সেলফ-ক্রিটিক মেটা-পাস | আউটপুট পড়তে মানুষের লেখা লাগে, AI নয় — আন্দাজে নয়, পরিমাপে প্রমাণিত |
| **ফ্যাক্ট-চেকার সাবএজেন্ট** URL যাচাই করে এবং দাবিগুলো ক্রস-রেফারেন্স করে | সাইটেশনগুলো সত্যিই কাজ করে, হ্যালুসিনেটেড নয় — প্রতিটি পরিসংখ্যান একটি যাচাইকৃত লেজার এন্ট্রিতে ফিরে যায় |
| **তিন-ক্যাটাগরি ইন্টারনাল লিংকিং** (টপিক্যাল / কমার্শিয়াল / অথরিটি) | কনটেন্ট হয়ে ওঠে ফানেল, বিচ্ছিন্ন কোনো পেজ নয় |
| **আসল `.docx` আউটপুট** — SEO + কোয়ালিটি + প্রোডাকশন + ইন্টারনাল-লিংক পরিশিষ্টসহ | আপনার এডিটর পান একটি কার্যকর Word ফাইল, markdown নয় |
| **এমন এক রান অডিটর যা আর্টিফ্যাক্ট থেকে প্রতিটি গেট নতুন করে যাচাই করে** | "পাইপলাইন বলছে কাজ শেষ" আর "আর্টিফ্যাক্ট প্রমাণ করছে কাজ শেষ" — এই দুটি আর কখনো নিঃশব্দে আলাদা হয়ে যেতে পারে না |
| **লাইফসাইকেল লুপ (v4.0)** — অডিট → রিফ্রেশ → পরিমাপ → পরিকল্পনা, ফাইল কন্ট্র্যাক্টে বাঁধা | প্রকাশিত কনটেন্ট আর ফায়ার-অ্যান্ড-ফরগেট থাকে না: ক্ষয় ধরা পড়ে, রিফ্রেশের অগ্রাধিকার ঠিক হয় ডেটার ভিত্তিতে |
| **C2PA কনটেন্ট প্রভেন্যান্স সাইনিং** — EU AI Act Article 50 কমপ্লায়েন্সের জন্য | EU বাজারে বিতরণ করা লং-ফর্ম AI-সহায়ক কনটেন্টে 2 আগস্ট 2026 থেকে প্রভেন্যান্স লাগবেই |

## বাস্তব ফলাফল, একটি বাস্তব রান থেকে

একটি এন্ড-টু-এন্ড ভ্যালিডেশন রান (আগস্ট 2026, একটি ডিজিটাল-প্রিজারভেশন টেস্ট ব্র্যান্ড, "link rot" কিওয়ার্ডে 1,200 শব্দের একটি ব্লগ) — ঠিক যেভাবে ঘটেছিল, সেভাবেই রিপোর্ট করা:

- ফ্যাক্ট-চেকিং ফেজ ধরে ফেলে যে রিসার্চ ফেজ একটি পরিসংখ্যান ভুল পড়েছিল; সংশোধিত বাক্যটি একটি যাচাইকৃত লেজারে লক করে দেয় এবং মূল বাক্যটিকে খসড়ায় নিষিদ্ধ করে। সংশোধনটি হুবহু, অবিকৃত অবস্থায়, ডেলিভার করা Word ফাইল পর্যন্ত টিকে ছিল।
- ভ্যালিডেশন ফেজ 42টি দাবিকে লেজারের সঙ্গে মিলিয়ে দেখে: **হ্যালুসিনেশন শূন্য**।
- হিউম্যানাইজার 7টি ক্যাটাগরি জুড়ে 20টি AI-প্যাটার্ন ইনস্ট্যান্স সরিয়ে দেয় (প্রতিটি প্যাটার্ন ধরে ধরে পরিমাপ করা, প্রতিটি এডিটের আগে/পরে লগসহ) — অথচ প্রতিটি তথ্য, সাইটেশন ও SEO প্লেসমেন্ট বাইট-স্তরে অপরিবর্তিত থাকে।
- রিভিউ ফেজ অনুমোদন দেয় **9.0/10 (গ্রেড A)** — কনটেন্ট কোয়ালিটি 8.8, সাইটেশন ইন্টেগ্রিটি 8.9, ব্র্যান্ড কমপ্লায়েন্স 9.6, SEO 8.6, রিডেবিলিটি 8.8।
- রান অডিটর ডিস্কে থাকা আর্টিফ্যাক্ট থেকে সবকিছু নতুন করে যাচাই করে: **14টি চেক পাস, 0টি ফেল** — কেবল তার পরেই রানটি নিজেকে সম্পন্ন ঘোষণা করার অনুমতি পায়।

মূল কথা এই নয় যে পাইপলাইন কখনো ভুল করে না — কথা হলো, তার ভুলগুলো তার নিজেরই যন্ত্রে ধরা পড়ে, রেকর্ডসহ, আপনার এডিটরের চোখে ফাইলটি পড়ার আগেই। আসল আর্টিফ্যাক্টগুলো (আসল চার্ট, এডিটের আসল আগে/পরে, আসল স্কোরকার্ড) দেখুন [ইংরেজি README](README.md#examples)-এ।

---

## দ্রুত শুরু

### 1. ইনস্টল করুন

**Claude Code (CLI বা VS Code/JetBrains এক্সটেনশন):**

```bash
/plugin marketplace add indranilbanerjee/neels-plugins
/plugin install contentforge@neels-plugins
```

**Anthropic Cowork:** UI-তে **Plugins** প্যানেল খুলুন → Add marketplace → `indranilbanerjee/neels-plugins` → Install ContentForge। (`/plugin` স্ল্যাশ কমান্ড Cowork-এ কাজ করে না — UI প্যানেল ব্যবহার করুন।) এরপর টিমের সঙ্গে শেয়ারযোগ্য আউটপুটের জন্য Google Drive যুক্ত করতে একবার `/contentforge:cf-cowork-setup` চালান।

**OpenAI Codex (CLI + IDE + App):**

```bash
codex plugin marketplace add indranilbanerjee/neels-plugins
codex plugin install contentforge@neels-plugins
```

**অন্যান্য প্ল্যাটফর্ম:**

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

**claude.ai (ওয়েব):** [সর্বশেষ রিলিজ](https://github.com/indranilbanerjee/contentforge/releases/latest) থেকে একটি হিরো স্কিল ডাউনলোড করুন — `cf-brief.skill`, `cf-social-adapt.skill`, `cf-translate.skill`, `cf-video-script.skill`, বা `cf-aeo-check.skill` — তারপর claude.ai-তে: **Settings → Capabilities** (*Code execution and file creation* চালু করুন) → **Customize → Skills → Upload skill**। পূর্ণ পাইপলাইনের জন্য সাবএজেন্ট ডিসপ্যাচ দরকার, তাই সেটি চলে উপরের প্ল্যাটফর্মগুলোতে; হিরো স্কিলগুলো স্ট্যান্ডঅ্যালোনভাবেই কাজ করে।

**ChatGPT ও অন্যান্য Agent Plugins 1.0 হোস্ট:** ContentForge OpenAI-এর ভেন্ডর-নিরপেক্ষ Agent Plugins 1.0 স্ট্যান্ডার্ড মেনে একটি রুট `plugin.json` শিপ করে। সাবএজেন্ট ডিসপ্যাচ নেই এমন হোস্টে **পোর্টেবল এক্সিকিউশন লেন** পুরো পাইপলাইনটাই একটি কথোপকথনের মধ্যে ধাপে ধাপে চালায় — একই ফেজ, একই আর্টিফ্যাক্ট, একই কোয়ালিটি গেট।

### 2. আপনার প্রথম ব্র্যান্ড সেট আপ করুন

```
/contentforge:brand-setup
```

এজেন্ট আপনাকে ধাপে ধাপে ব্র্যান্ড ভয়েস, টার্মিনোলজি, গার্ডরেল, সাইটেশন নিয়ম এবং ইন্টারনাল লিংকিংয়ের জন্য আপনার সাইট-কাঠামো ঠিক করিয়ে নেয়। একটি ওয়েবসাইট দিলে সে মাত্র এক ধাপের নিশ্চিতকরণেই একটি যাচাইকৃত পেজ-ইনভেন্টরি সংগ্রহ করে নেয়।

### 3. কনটেন্ট তৈরি করুন

```
/contentforge:create-content
```

কনটেন্টের ধরন, ব্র্যান্ড, টপিক, শব্দসংখ্যা ও অডিয়েন্স বেছে নিন। পাইপলাইন 10টি ফেজ চালায় (রিসার্চ → ফ্যাক্ট-চেক → খসড়া → ভিজ্যুয়াল → ভ্যালিডেশন → স্ট্রাকচার → SEO → হিউম্যানাইজ → রিভিউ → আউটপুট), প্রতিটি ফেজের পরে কোয়ালিটি গেট প্রয়োগ করে, সমাপ্ত রানকে তার নিজের আর্টিফ্যাক্টের বিপরীতে অডিট করে, এবং একটি আসল `.docx` লিখে দেয়।

### 4. আপনার আউটপুট খুঁজে নিন

```
~/Documents/ContentForge/<brand-slug>/<content-type>/<YYYY-MM>/<slug>.docx
```

`.docx`-এ থাকে মূল লেখা, রেফারেন্স এবং চারটি পরিশিষ্ট: SEO স্কোরকার্ড, কোয়ালিটি স্কোরকার্ড, প্রোডাকশনের বিস্তারিত এবং ইন্টারনাল লিংক ম্যাপ।

### 5. লুপটি সম্পূর্ণ করুন

```
/contentforge:cf-aeo-check           # record which pieces AI engines cite
/contentforge:audit-content          # freshness-score the library; findings are RECORDED
/contentforge:cf-calendar --from-audit=latest   # next period: refreshes + gaps, from data
/contentforge:content-refresh        # execute a refresh at the audit's recommended scope
```

প্রতিটি কমান্ড আগের কমান্ডের রেকর্ড করা তথ্য পড়ে — নতুন সেশনে, অন্য কোনো দিনে, ভিন্ন কোনো টিমমেটের হাতেও।

---

## সমর্থিত প্ল্যাটফর্ম (v4.1.2)

নয়টি নেটিভ প্ল্যাটফর্ম + claude.ai আপলোড + 35+ Agent Skills ক্লায়েন্ট:

| প্ল্যাটফর্ম | ইনস্টল |
|---|---|
| **Claude Code** (CLI + IDE) | `/plugin install contentforge@neels-plugins` |
| **Anthropic Cowork** | Plugins প্যানেল → Add marketplace → `indranilbanerjee/neels-plugins` |
| **OpenAI Codex** | `codex plugin install contentforge@neels-plugins` |
| **Cursor 2.5+** | `/add-plugin contentforge@https://github.com/indranilbanerjee/contentforge` |
| **GitHub Copilot CLI** | `copilot plugin install contentforge@neels-plugins` |
| **Google Antigravity 2.0** | `agy plugin install https://github.com/indranilbanerjee/contentforge` |
| **Hermes Agent** | `hermes plugins install indranilbanerjee/contentforge` |
| **OpenClaw** | `openclaw plugins install git:github.com/indranilbanerjee/contentforge` |
| **Grok** (xAI Build CLI) | `grok plugin install indranilbanerjee/contentforge` |
| **claude.ai** (ওয়েব) | [রিলিজ](https://github.com/indranilbanerjee/contentforge/releases/latest) থেকে একটি হিরো `.skill` আপলোড করুন |
| **ChatGPT / Agent Plugins 1.0 হোস্ট** | রুট `plugin.json` প্যাকেজ + পোর্টেবল এক্সিকিউশন লেন |

সবগুলো — 22টি — SKILL.md ফাইল Agent Skills ওপেন স্ট্যান্ডার্ডের মাধ্যমে প্ল্যাটফর্ম-পোর্টেবল — যেকোনো সামঞ্জস্যপূর্ণ ক্লায়েন্টকে `https://github.com/indranilbanerjee/contentforge/tree/master/skills`-এ পয়েন্ট করলেই হলো।

---

## আপডেট করা

**Claude Code:** থার্ড-পার্টি মার্কেটপ্লেসে অটো-আপডেট ডিফল্টভাবে বন্ধ থাকে। একবার চালু করে নিন: `/plugin` → **Marketplaces** ট্যাব → `neels-plugins` → **Enable auto-update**। অথবা ম্যানুয়ালি: `/plugin marketplace update neels-plugins`, তারপর `/plugin uninstall` + `/plugin install contentforge@neels-plugins` + `/reload-plugins`।

**Cowork / claude.ai / Claude Desktop:** Plugins UI প্যানেল খুলুন → ContentForge রিমুভ করুন → মার্কেটপ্লেস থেকে আবার ইনস্টল করুন (নতুন করে টানলেই সর্বশেষ ভার্সন চলে আসে)।

**Codex:** `codex plugin update contentforge` · **Cursor:** `/add-plugin` আবার চালান · **Copilot CLI:** `copilot plugin update contentforge` · **Antigravity:** `agy plugin update contentforge` · **Hermes:** `hermes plugins update contentforge` · **OpenClaw:** `openclaw plugins update contentforge` · **Grok:** `grok plugin update contentforge` · **claude.ai আপলোড:** সর্বশেষ রিলিজ থেকে `.skill` আবার ডাউনলোড করে আবার আপলোড করুন।

---

## FAQ (জরুরি প্রশ্নগুলো)

**আমার ডেটা কোথায় থাকে?** সবকিছুই লোকাল: ব্র্যান্ড প্রোফাইল ও রান আর্টিফ্যাক্ট `~/.claude-marketing/<brand>/`-এর নিচে, ডেলিভারেবল `~/Documents/ContentForge/`-এর নিচে। আপনার নিজের প্ল্যাটফর্মের করা মডেল কল ছাড়া কোথাও কিছুই পাঠানো হয় না।

**MCP/ইন্টিগ্রেশন কানেক্ট করা কি জরুরি?** না। শিপ করা `.mcp.json` ইচ্ছাকৃতভাবেই খালি — স্বয়ংক্রিয়ভাবে কানেক্ট হওয়া কোনো সার্ভার নেই। কানেক্টরগুলো একটি অপ্ট-ইন ক্যাটালগ (`/contentforge:cf-connect`)।

**এটা কি EU AI Act-এর জন্য প্রস্তুত?** হ্যাঁ — Article 50 AI-ডিসক্লোজার অ্যাসারশনসহ C2PA কনটেন্ট প্রভেন্যান্স সাইনিং, সেই সঙ্গে ব্র্যান্ড-কনফিগারযোগ্য একটি ডিসক্লোজার স্তর (অনিশ্চিত হলে ⇒ ডিসক্লোজ — এই ফেল-সেফসহ)।

**পূর্ণ পাইপলাইন কি Claude Code-এর বাইরেও চলে?** হ্যাঁ — সাবএজেন্ট ডিসপ্যাচ নেই এমন প্ল্যাটফর্মে পোর্টেবল এক্সিকিউশন লেন 10টি ফেজের সবগুলোই ধাপে ধাপে চালায়, প্রতিটি গেট অক্ষুণ্ণ রেখে। একমাত্র ব্যতিক্রম claude.ai-এর `.skill` আপলোড: সেগুলো স্ট্যান্ডঅ্যালোন হিরো স্কিল, পাইপলাইন নয়।

---

## মেইনটেইনার সম্পর্কে

ContentForge তৈরি ও রক্ষণাবেক্ষণ করেন **[Indranil "Neel" Banerjee](https://indranil.in)** — ইনফরমেশন সিকিউরিটিতে যাঁর শিকড়, আর গ্রোথ মার্কেটিং, এন্টারপ্রাইজ ডিজিটাল অপারেশনস ও AI ট্রান্সফরমেশন জুড়ে যাঁর দ্বিতীয় অধ্যায় — একজন নির্মাতা ও সিস্টেমস-চিন্তক। [Digital Marketing Pro](https://github.com/indranilbanerjee/digital-marketing-pro) ও [SocialForge](https://github.com/indranilbanerjee/socialforge)-এর সঙ্গে তিন-প্লাগইনের **Neelverse Marketing Suite**-এর অংশ।

ContentForge যদি আপনার টিমের সময় বাঁচায়, তাহলে [⭐ রিপোতে স্টার দিন](https://github.com/indranilbanerjee/contentforge/stargazers) এবং [প্রজেক্টটি স্পনসর করার কথা ভাবুন ❤](https://github.com/sponsors/indranilbanerjee) — এতেই রিলিজের ধারাবাহিকতা টেকসই থাকে।

**লাইসেন্স:** MIT · **সিকিউরিটি:** [প্রাইভেট অ্যাডভাইজরি](https://github.com/indranilbanerjee/contentforge/security/advisories/new) · **ইস্যু:** [GitHub Issues](https://github.com/indranilbanerjee/contentforge/issues)
