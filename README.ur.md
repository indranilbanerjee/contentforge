# ContentForge

🌐 **Read this in:** [English](README.md) · [हिन्दी](README.hi.md) · [中文](README.zh-CN.md) · [日本語](README.ja.md) · [한국어](README.ko.md) · [Español](README.es.md) · [Português](README.pt-BR.md) · [العربية](README.ar.md) · [اردو](README.ur.md) · [தமிழ்](README.ta.md) · [বাংলা](README.bn.md) · [Русский](README.ru.md)

> **انگریزی README v4.1.1 (2026-08-17) کے ساتھ ہم آہنگ۔** حتمی ماخذ [انگریزی README](README.md) ہی ہے — ریلیز نوٹس، اسکلز/کمانڈز کا مکمل کیٹلاگ، آرکیٹیکچر، ٹربل شوٹنگ اور مکمل FAQ وہیں موجود ہیں۔ یہ ترجمہ ContentForge کو انسٹال کرنے، چلانے اور اپڈیٹ کرنے کے لیے درکار ہر چیز کا احاطہ کرتا ہے۔

> **آپ کو اس سہ ماہی میں 30 ایسے آرٹیکل شائع کرنے ہیں جو انسانی تحریر لگیں، حقیقی ماخذوں کا حوالہ دیں، آپ کے فنل سے جُڑیں، اور اُس ایڈیٹر کی جانچ سے بھی گزر جائیں جو واقعی پرکھتا ہے۔ آپ کی ٹیم تین افراد پر مشتمل ہے۔ آپ کے پاس نو ہفتے ہیں۔ آپ کا پچھلا "AI سے لکھا ہوا" بیچ من گھڑت اعداد و شمار کی وجہ سے پکڑا گیا — اور اُس سے پہلے والا بیچ خاموشی سے پرانا ہوتا گیا اور کسی کو خبر تک نہ ہوئی۔**

ہر موضوع پر `/contentforge:create-content` چلائیں۔ 10 مرحلوں کی پائپ لائن اشاعت کے لیے تیار `.docx` بناتی ہے — جس میں 43 پیٹرن والا humanizer، ایک fact-checker ذیلی ایجنٹ، تین زمروں کی اندرونی لنکنگ، اور EU AI Act کی تعمیل کے لیے C2PA پرووننس شامل ہے — ہر تحریر 30–60 منٹ میں۔ پھر وہ حصہ جو کسی سنگل شاٹ ٹول کے پاس نہیں: **لائف سائیکل لوپ۔** ہر شائع شدہ تحریر کی پیمائش ہوتی ہے، زوال (decay) کے لیے اس کا آڈٹ ہوتا ہے، اور وہ اگلے کیلنڈر اور اگلی بریف میں واپس شامل ہوتی ہے — پائیدار فائل کنٹریکٹس کے ذریعے، تاکہ سسٹم آپ کے برانڈ کے بارے میں جو کچھ سیکھے وہ اُس سیشن کے ختم ہونے کے بعد بھی باقی رہے جس میں وہ سیکھا گیا۔

اوپن سورس انٹرپرائز کنٹنٹ پروڈکشن سسٹم — **22 اسکلز · 13 ماہر ایجنٹس · 10 کوالٹی گیٹس · 43 پیٹرن والا AI-ڈیٹیکشن humanizer · ایک run auditor جو ہر گیٹ کو دوبارہ اخذ کرتا ہے، اس سے پہلے کہ کوئی رن خود کو مکمل قرار دے سکے · 28 Python اسکرپٹس، صرف stdlib**۔ تخلیق کار: [Indranil Banerjee](https://indranil.in) · [LinkedIn](https://www.linkedin.com/in/askneelnow/) · [X](https://x.com/askneelnow)۔

**ورژن 4.1.1** · [چینج لاگ](CHANGELOG.md) · MIT لائسنس · [اس پروجیکٹ کو اسپانسر کریں ❤](https://github.com/sponsors/indranilbanerjee)

---

## ContentForge ہی کیوں؟

زیادہ تر AI رائٹنگ ٹولز ایک ہی ڈرافٹ، ایک ہی لہجے میں، بغیر کسی کوالٹی گیٹ کے تیار کرتے ہیں، اور تحریر شائع ہوتے ہی اُسے بھول جاتے ہیں۔ ContentForge اس مسئلے کو شروع سے آخر تک حل کرتا ہے:

| صلاحیت | کیوں اہم ہے |
|---|---|
| **10 مرحلوں کی پائپ لائن، ہر مرحلے کے بعد کوالٹی گیٹ** | ناقص آؤٹ پٹ آگے پھیلنے سے پہلے پکڑ کر دوبارہ چلایا جاتا ہے |
| **43 پیٹرن والا AI-ڈیٹیکشن humanizer** + خود تنقیدی میٹا پاس | آؤٹ پٹ انسانی تحریر لگتا ہے، AI نہیں — پیمائش کی بنیاد پر، محض تاثر پر نہیں |
| **Fact-checker ذیلی ایجنٹ** URLs کی تصدیق کرتا ہے اور دعووں کا تقابلی جائزہ لیتا ہے | حوالے واقعی کام کرتے ہیں اور من گھڑت نہیں ہوتے — ہر شماریاتی دعویٰ ایک تصدیق شدہ لیجر اندراج سے جُڑا ہوتا ہے |
| **تین زمروں کی اندرونی لنکنگ** (topical / commercial / authority) | مواد ایک فنل بنتا ہے، الگ تھلگ پڑا ہوا صفحہ نہیں |
| **حقیقی `.docx` آؤٹ پٹ** — SEO + Quality + Production + Internal-Link ضمیموں کے ساتھ | آپ کے ایڈیٹر کو قابلِ استعمال Word فائل ملتی ہے، markdown نہیں |
| **ایک run auditor جو ہر گیٹ کو artifacts سے دوبارہ اخذ کرتا ہے** | "پائپ لائن کہتی ہے کام مکمل ہوا" اور "artifacts ثابت کرتے ہیں کہ مکمل ہوا" کبھی خاموشی سے ایک دوسرے سے الگ نہیں ہو سکتے |
| **لائف سائیکل لوپ (v4.0)** — آڈٹ → ریفریش → پیمائش → منصوبہ بندی، فائل کنٹریکٹس سے مربوط | شائع شدہ مواد "چھوڑ کر بھول جانے" والی چیز نہیں رہتا: زوال کا سراغ لگتا ہے اور ریفریش ڈیٹا کی بنیاد پر ترجیح پاتے ہیں |
| **C2PA کنٹنٹ پرووننس سائننگ** — EU AI Act کے Article 50 کی تعمیل کے لیے | EU منڈیوں میں تقسیم ہونے والے طویل، AI-معاون مواد کے لیے 2 اگست 2026 سے پرووننس لازم ہے |

## حقیقی نتائج، ایک حقیقی رن سے

ایک اینڈ ٹو اینڈ ویلیڈیشن رن (اگست 2026، ایک ڈیجیٹل پریزرویشن ٹیسٹ برانڈ، کلیدی لفظ "link rot" پر 1,200 الفاظ کا بلاگ) — بالکل ویسا ہی رپورٹ کیا گیا جیسا وہ پیش آیا:

- fact-checking مرحلے نے پکڑ لیا کہ ریسرچ مرحلے نے ایک اعداد و شمار کو غلط پڑھا تھا، درست شدہ عبارت کو تصدیق شدہ لیجر میں مقفل کیا، اور اصل جملے پر ڈرافٹ میں پابندی لگا دی۔ یہ تصحیح لفظ بہ لفظ حتمی Word فائل تک برقرار رہی۔
- ویلیڈیشن مرحلے نے 42 دعووں کا لیجر سے موازنہ کیا: **صفر hallucinations**۔
- humanizer نے 7 زمروں میں 20 AI-پیٹرن مثالیں ہٹائیں (ہر پیٹرن کی الگ پیمائش، ہر ترمیم کے لیے before/after لاگ کے ساتھ) جبکہ ہر حقیقت، حوالہ اور SEO پلیسمنٹ بائٹ سطح پر جوں کی توں رہی۔
- ریویو مرحلے نے **9.0/10 (گریڈ A)** پر منظوری دی — مواد کا معیار 8.8، حوالہ جاتی سالمیت 8.9، برانڈ کمپلائنس 9.6، SEO 8.6، پڑھنے کی روانی 8.8۔
- run auditor نے ڈسک پر موجود artifacts سے سب کچھ دوبارہ اخذ کیا: **14 چیکس کامیاب، 0 ناکام** — تب کہیں جا کر رن کو خود کو مکمل قرار دینے کی اجازت ملی۔

اصل بات یہ نہیں کہ پائپ لائن کبھی غلطی نہیں کرتی — بات یہ ہے کہ اس کی غلطیاں اس کی اپنی مشینری پکڑتی ہے، ریکارڈ پر، اس سے پہلے کہ آپ کا ایڈیٹر فائل تک پہنچے۔ حقیقی artifacts (اصل چارٹ، اصل before/after ترامیم، اصل اسکور کارڈ) [انگریزی README](README.md#examples) میں دیکھیں۔

---

## فوری آغاز

### 1. انسٹال کریں

**Claude Code (CLI یا VS Code/JetBrains ایکسٹینشن):**

```bash
/plugin marketplace add indranilbanerjee/neels-plugins
/plugin install contentforge@neels-plugins
```

**Anthropic Cowork:** UI میں **Plugins** پینل کھولیں → Add marketplace → `indranilbanerjee/neels-plugins` → Install ContentForge۔ (`/plugin` سلیش کمانڈز Cowork میں کام نہیں کرتیں — UI پینل استعمال کریں۔) پھر ٹیم کے ساتھ قابلِ اشتراک آؤٹ پٹ کے لیے Google Drive جوڑنے کو ایک بار `/contentforge:cf-cowork-setup` چلائیں۔

**OpenAI Codex (CLI + IDE + App):**

```bash
codex plugin marketplace add indranilbanerjee/neels-plugins
codex plugin install contentforge@neels-plugins
```

**دیگر پلیٹ فارمز:**

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

**claude.ai (ویب):** [تازہ ترین ریلیز](https://github.com/indranilbanerjee/contentforge/releases/latest) سے کوئی ہیرو اسکل ڈاؤن لوڈ کریں — `cf-brief.skill`، `cf-social-adapt.skill`، `cf-translate.skill`، `cf-video-script.skill` یا `cf-aeo-check.skill` — پھر claude.ai میں: **Settings → Capabilities** (*Code execution and file creation* فعال کریں) → **Customize → Skills → Upload skill**۔ مکمل پائپ لائن کو subagent dispatch درکار ہے اور وہ اوپر دیے گئے پلیٹ فارمز پر چلتی ہے؛ ہیرو اسکلز خود مختار طور پر کام کرتی ہیں۔

**ChatGPT اور دیگر Agent Plugins 1.0 ہوسٹس:** ContentForge اپنے روٹ میں OpenAI کے وینڈر نیوٹرل Agent Plugins 1.0 معیار پر ایک `plugin.json` فراہم کرتا ہے۔ جن ہوسٹس پر subagent dispatch میسر نہیں، وہاں **پورٹیبل ایگزیکیوشن لین** پوری پائپ لائن ایک ہی گفتگو میں یکے بعد دیگرے چلاتی ہے — وہی مراحل، وہی artifacts، وہی کوالٹی گیٹس۔

### 2. اپنا پہلا برانڈ سیٹ اپ کریں

```
/contentforge:brand-setup
```

ایجنٹ آپ کو برانڈ وائس، اصطلاحات، guardrails، حوالہ جات کے اصولوں، اور اندرونی لنکنگ کے لیے آپ کی سائٹ کے ڈھانچے سے قدم بہ قدم گزارتا ہے۔ جب آپ اسے کوئی ویب سائٹ دیتے ہیں تو یہ ایک ہی تصدیقی مرحلے میں صفحات کی تصدیق شدہ فہرست تیار کر لیتا ہے۔

### 3. مواد تیار کریں

```
/contentforge:create-content
```

مواد کی قسم، برانڈ، موضوع، الفاظ کی تعداد اور سامعین منتخب کریں۔ پائپ لائن 10 مراحل چلاتی ہے (research → fact-check → draft → visuals → validate → structure → SEO → humanize → review → output)، ہر مرحلے کے بعد کوالٹی گیٹ نافذ کرتی ہے، مکمل شدہ رن کا اس کے اپنے artifacts کے مقابل آڈٹ کرتی ہے، اور ایک حقیقی `.docx` لکھتی ہے۔

### 4. اپنا آؤٹ پٹ تلاش کریں

```
~/Documents/ContentForge/<brand-slug>/<content-type>/<YYYY-MM>/<slug>.docx
```

اس `.docx` میں متن، حوالہ جات اور چار ضمیمے شامل ہوتے ہیں: SEO اسکور کارڈ، کوالٹی اسکور کارڈ، پروڈکشن کی تفصیلات، اور اندرونی لنک میپ۔

### 5. لوپ مکمل کریں

```
/contentforge:cf-aeo-check           # record which pieces AI engines cite
/contentforge:audit-content          # freshness-score the library; findings are RECORDED
/contentforge:cf-calendar --from-audit=latest   # next period: refreshes + gaps, from data
/contentforge:content-refresh        # execute a refresh at the audit's recommended scope
```

ہر کمانڈ وہی پڑھتی ہے جو پچھلی کمانڈ نے ریکارڈ کیا تھا — نئے سیشن میں، کسی اور دن، کسی اور ٹیم ساتھی کے ہاتھوں۔

---

## معاون پلیٹ فارمز (v4.1.1)

نو نیٹو پلیٹ فارمز + claude.ai اپ لوڈز + 35+ Agent Skills کلائنٹس:

| پلیٹ فارم | انسٹال |
|---|---|
| **Claude Code** (CLI + IDE) | `/plugin install contentforge@neels-plugins` |
| **Anthropic Cowork** | Plugins پینل → Add marketplace → `indranilbanerjee/neels-plugins` |
| **OpenAI Codex** | `codex plugin install contentforge@neels-plugins` |
| **Cursor 2.5+** | `/add-plugin contentforge@https://github.com/indranilbanerjee/contentforge` |
| **GitHub Copilot CLI** | `copilot plugin install contentforge@neels-plugins` |
| **Google Antigravity 2.0** | `agy plugin install https://github.com/indranilbanerjee/contentforge` |
| **Hermes Agent** | `hermes plugins install indranilbanerjee/contentforge` |
| **OpenClaw** | `openclaw plugins install git:github.com/indranilbanerjee/contentforge` |
| **Grok** (xAI Build CLI) | `grok plugin install indranilbanerjee/contentforge` |
| **claude.ai** (ویب) | [ریلیزز](https://github.com/indranilbanerjee/contentforge/releases/latest) سے کوئی ہیرو `.skill` اپ لوڈ کریں |
| **ChatGPT / Agent Plugins 1.0 ہوسٹس** | روٹ `plugin.json` پیکیج + پورٹیبل ایگزیکیوشن لین |

تمام 22 SKILL.md فائلیں Agent Skills اوپن اسٹینڈرڈ کے ذریعے پلیٹ فارم پورٹیبل ہیں — کسی بھی ہم آہنگ کلائنٹ کو `https://github.com/indranilbanerjee/contentforge/tree/master/skills` کی طرف موڑ دیں۔

---

## اپڈیٹ کرنا

**Claude Code:** فریقِ ثالث marketplaces کے لیے آٹو اپڈیٹ بطور ڈیفالٹ OFF ہوتا ہے۔ اسے ایک بار آن کر لیں: `/plugin` → **Marketplaces** ٹیب → `neels-plugins` → **Enable auto-update**۔ یا دستی طور پر: `/plugin marketplace update neels-plugins` پھر `/plugin uninstall` + `/plugin install contentforge@neels-plugins` + `/reload-plugins`۔

**Cowork / claude.ai / Claude Desktop:** Plugins UI پینل کھولیں → ContentForge ہٹائیں → marketplace سے دوبارہ انسٹال کریں (دوبارہ حاصل کرنے پر تازہ ترین ورژن آ جاتا ہے)۔

**Codex:** `codex plugin update contentforge` · **Cursor:** `/add-plugin` دوبارہ چلائیں · **Copilot CLI:** `copilot plugin update contentforge` · **Antigravity:** `agy plugin update contentforge` · **Hermes:** `hermes plugins update contentforge` · **OpenClaw:** `openclaw plugins update contentforge` · **Grok:** `grok plugin update contentforge` · **claude.ai اپ لوڈز:** تازہ ترین ریلیز سے `.skill` دوبارہ ڈاؤن لوڈ کر کے دوبارہ اپ لوڈ کریں۔

---

## FAQ (بنیادی سوالات)

**میرا ڈیٹا کہاں رہتا ہے؟** سب کچھ لوکل ہے: برانڈ پروفائلز اور رن artifacts `~/.claude-marketing/<brand>/` کے تحت، اور تیار شدہ deliverables `~/Documents/ContentForge/` کے تحت۔ آپ کے اپنے پلیٹ فارم کی ماڈل کالز کے سوا کچھ بھی کہیں نہیں بھیجا جاتا۔

**کیا مجھے MCPs/انٹیگریشنز جوڑنے کی ضرورت ہے؟** نہیں۔ ساتھ آنے والی `.mcp.json` جان بوجھ کر خالی رکھی گئی ہے — کوئی بھی سرور خود بخود کنیکٹ نہیں ہوتا۔ کنیکٹرز ایک اختیاری (opt-in) کیٹلاگ ہیں (`/contentforge:cf-connect`)۔

**کیا یہ EU AI Act کے لیے تیار ہے؟** جی ہاں — Article 50 کے AI-ڈسکلوژر assertion کے ساتھ C2PA کنٹنٹ پرووننس سائننگ، نیز برانڈ کے مطابق قابلِ ترتیب ڈسکلوژر لیئر (غیر یقینی ⇒ ظاہر کریں کا fail-safe اصول)۔

**کیا مکمل پائپ لائن Claude Code سے باہر بھی چلتی ہے؟** جی ہاں — جن پلیٹ فارمز پر subagent dispatch میسر نہیں، وہاں پورٹیبل ایگزیکیوشن لین تمام 10 مراحل یکے بعد دیگرے چلاتی ہے اور ہر گیٹ برقرار رہتا ہے۔ صرف claude.ai کی `.skill` اپ لوڈز اس سے مستثنیٰ ہیں: وہ خود مختار ہیرو اسکلز ہیں، پائپ لائن نہیں۔

---

## مینٹینر کے بارے میں

ContentForge کو **[Indranil "Neel" Banerjee](https://indranil.in)** بناتے اور سنبھالتے ہیں — انفارمیشن سیکیورٹی میں جڑیں رکھنے والے ایک بلڈر اور سسٹمز تھنکر، جن کے سفر کا دوسرا باب growth marketing، انٹرپرائز ڈیجیٹل آپریشنز اور AI ٹرانسفارمیشن پر محیط ہے۔ یہ تین پلگ انز پر مشتمل **Neelverse Marketing Suite** کا حصہ ہے، جس میں [Digital Marketing Pro](https://github.com/indranilbanerjee/digital-marketing-pro) اور [SocialForge](https://github.com/indranilbanerjee/socialforge) بھی شامل ہیں۔

اگر ContentForge آپ کی ٹیم کا وقت بچاتا ہے تو [⭐ ریپو کو اسٹار کریں](https://github.com/indranilbanerjee/contentforge/stargazers) اور [پروجیکٹ کو اسپانسر کرنے ❤](https://github.com/sponsors/indranilbanerjee) پر غور کریں — اسی سے ریلیز کی رفتار پائیدار رہتی ہے۔

**لائسنس:** MIT · **سیکیورٹی:** [نجی ایڈوائزریز](https://github.com/indranilbanerjee/contentforge/security/advisories/new) · **مسائل:** [GitHub Issues](https://github.com/indranilbanerjee/contentforge/issues)
