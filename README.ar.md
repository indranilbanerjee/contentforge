# ContentForge

🌐 **Read this in:** [English](README.md) · [हिन्दी](README.hi.md) · [中文](README.zh-CN.md) · [日本語](README.ja.md) · [한국어](README.ko.md) · [Español](README.es.md) · [Português](README.pt-BR.md) · [العربية](README.ar.md) · [اردو](README.ur.md) · [தமிழ்](README.ta.md) · [বাংলা](README.bn.md) · [Русский](README.ru.md)

> **مُتزامنة مع النسخة الإنجليزية v4.1.1 من README (بتاريخ 2026-08-17).** يبقى [ملف README الإنجليزي](README.md) هو المرجع الأساسي — فهناك تجد ملاحظات الإصدارات، والكتالوج الكامل للمهارات والأوامر، والبنية المعمارية، ودليل استكشاف الأخطاء وإصلاحها، والأسئلة الشائعة كاملة. أما هذه الترجمة فتغطي كل ما تحتاجه لتثبيت ContentForge وتشغيله وتحديثه.

> **مطلوب منك تسليم 30 مقالاً هذا الربع، تبدو بشرية الصياغة، وتستشهد بمصادر حقيقية، وترتبط بمسار التحويل لديك، وتصمد أمام محرر يدقق كل شيء. فريقك ثلاثة أشخاص، وأمامك تسعة أسابيع. دفعتك الأخيرة من المحتوى «المكتوب بالذكاء الاصطناعي» جرى التبليغ عنها بسبب إحصاءات مُختلَقة — والدفعة التي سبقتها فقدت حداثتها بصمت دون أن ينتبه أحد.**

شغّل `/contentforge:create-content` على كل موضوع. ينتج خط الإنتاج المؤلف من 10 مراحل ملف `.docx` جاهزاً للنشر، مزوداً بمُؤنسِن يكشف 43 نمطاً من أنماط الذكاء الاصطناعي، ووكيل فرعي لتدقيق الحقائق، وربط داخلي بثلاث فئات، وإثبات مصدر C2PA للامتثال لقانون EU AI Act — في غضون 30–60 دقيقة لكل قطعة. ثم يأتي الجزء الذي لا تملكه أي أداة تكتفي بمسودة واحدة: **حلقة دورة الحياة.** كل قطعة منشورة تُقاس، وتُدقَّق بحثاً عن التقادم، وتُغذّى مجدداً في التقويم التالي والموجز التالي — عبر عقود ملفات دائمة، بحيث يبقى ما يتعلمه النظام عن علامتك التجارية حياً بعد انتهاء الجلسة التي تعلّمه فيها.

نظام مفتوح المصدر لإنتاج المحتوى بمستوى المؤسسات — **22 مهارة · 13 وكيلاً متخصصاً · 10 بوابات جودة · مُؤنسِن لكشف أنماط الذكاء الاصطناعي يعمل بـ 43 نمطاً · مدقق تشغيل يعيد اشتقاق كل بوابة قبل أن يُسمح لأي تشغيل بإعلان اكتماله · 28 سكربت Python تعتمد على المكتبة القياسية وحدها**. من إنشاء [Indranil Banerjee](https://indranil.in) · [LinkedIn](https://www.linkedin.com/in/askneelnow/) · [X](https://x.com/askneelnow).

**الإصدار 4.1.1** · [سجل التغييرات](CHANGELOG.md) · رخصة MIT · [ادعم هذا المشروع ❤](https://github.com/sponsors/indranilbanerjee)

---

## لماذا ContentForge

تُنتج معظم أدوات الكتابة بالذكاء الاصطناعي مسودة واحدة، بنبرة واحدة، دون أي بوابات جودة، وتنسى القطعة لحظة تسليمها. يعالج ContentForge هذا كله من البداية إلى النهاية:

| القدرة | لماذا تهمّك |
|---|---|
| **خط إنتاج من 10 مراحل مع بوابة جودة بعد كل مرحلة** | يُلتقط الناتج الرديء ويُعاد تشغيله قبل أن ينتشر إلى المراحل اللاحقة |
| **مُؤنسِن لكشف أنماط الذكاء الاصطناعي بـ 43 نمطاً** + جولة نقد ذاتي فوقية | الناتج يُقرأ كنص بشري لا كنص آلي — بالقياس الموثَّق، لا بالانطباع |
| **وكيل فرعي لتدقيق الحقائق** يتحقق من الروابط ويقارن الادعاءات بمصادرها | الاستشهادات تعمل فعلاً وليست مُختلَقة — كل إحصائية تُقتفى إلى قيد مُوثَّق في السجل |
| **ربط داخلي بثلاث فئات** (موضوعي / تجاري / مرجعي) | يتحول المحتوى إلى مسار تحويل، لا صفحة معزولة |
| **ناتج `.docx` حقيقي** مع ملاحق SEO والجودة والإنتاج والروابط الداخلية | يحصل محررك على ملف Word جاهز للعمل، لا مجرد markdown |
| **مدقق تشغيل يعيد اشتقاق كل بوابة من المخرجات الفعلية** | لا يمكن أبداً أن يفترق «خط الإنتاج يقول إنه انتهى» عن «المخرجات تثبت أنه انتهى» في صمت |
| **حلقة دورة الحياة (v4.0)** — تدقيق ← تحديث ← قياس ← تخطيط، تربطها عقود ملفات | يكفّ المحتوى المنشور عن كونه «انشر وانسَ»: يُكشف التقادم وتُرتَّب التحديثات بالأولوية استناداً إلى البيانات |
| **توقيع C2PA لإثبات مصدر المحتوى** امتثالاً للمادة 50 من EU AI Act | المحتوى الطويل المُنتَج بمساعدة الذكاء الاصطناعي والموزَّع في أسواق الاتحاد الأوروبي يحتاج إلى إثبات مصدر اعتباراً من 2 أغسطس 2026 |

## نتائج حقيقية، من تشغيل حقيقي

تشغيل تحقق شامل من البداية إلى النهاية (أغسطس 2026، علامة تجارية اختبارية في مجال الحفظ الرقمي، ومقال مدونة من 1,200 كلمة حول الكلمة المفتاحية "link rot") — نورده هنا كما حدث بالضبط:

- التقطت مرحلة تدقيق الحقائق قراءة خاطئة لإحصائية وقعت فيها مرحلة البحث، وثبّتت الصياغة المصحَّحة في سجل مُوثَّق، وحظرت الجملة الأصلية من المسودة. وقد وصل التصحيح، حرفياً، إلى ملف Word المُسلَّم.
- قارنت مرحلة التحقق 42 ادعاءً بالسجل: **صفر هلوسات**.
- أزال المُؤنسِن 20 حالة من أنماط الذكاء الاصطناعي عبر 7 فئات (بقياس لكل نمط على حدة، مع تسجيل النص قبل التعديل وبعده لكل تعديل) مع إبقاء كل حقيقة واستشهاد وموضع SEO ثابتاً دون تغيير بايت واحد.
- اعتمدت مرحلة المراجعة النص بدرجة **9.0/10 (تقدير A)** — جودة المحتوى 8.8، سلامة الاستشهادات 8.9، الامتثال للعلامة التجارية 9.6، تحسين محركات البحث 8.6، سهولة القراءة 8.8.
- أعاد مدقق التشغيل اشتقاق كل شيء من المخرجات الموجودة على القرص: **نجاح 14 فحصاً وإخفاق 0** — وعندها فقط سُمح للتشغيل بإعلان اكتماله.

ليست الفكرة أن خط الإنتاج لا يخطئ أبداً — بل أن أخطاءه تُلتقط بآليته الذاتية، وتُدوَّن رسمياً، قبل أن يرى محررك الملف أصلاً. اطّلع على المخرجات الفعلية (المخطط الفعلي، والتعديلات الفعلية قبل وبعد، وبطاقة التقييم الفعلية) في [ملف README الإنجليزي](README.md#examples).

---

## البدء السريع

### 1. التثبيت

**Claude Code (سطر الأوامر أو امتداد VS Code/JetBrains):**

```bash
/plugin marketplace add indranilbanerjee/neels-plugins
/plugin install contentforge@neels-plugins
```

**Anthropic Cowork:** افتح لوحة **Plugins** في الواجهة ← Add marketplace ← `indranilbanerjee/neels-plugins` ← ثبّت ContentForge. (أوامر `/plugin` المائلة لا تعمل في Cowork — استخدم لوحة الواجهة.) ثم شغّل `/contentforge:cf-cowork-setup` مرة واحدة لربط Google Drive والحصول على مخرجات قابلة للمشاركة مع الفريق.

**OpenAI Codex (CLI + IDE + التطبيق):**

```bash
codex plugin marketplace add indranilbanerjee/neels-plugins
codex plugin install contentforge@neels-plugins
```

**منصات أخرى:**

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

**claude.ai (الويب):** نزّل إحدى المهارات البارزة من [أحدث إصدار](https://github.com/indranilbanerjee/contentforge/releases/latest) — `cf-brief.skill` أو `cf-social-adapt.skill` أو `cf-translate.skill` أو `cf-video-script.skill` أو `cf-aeo-check.skill` — ثم في claude.ai: **Settings → Capabilities** (فعّل *Code execution and file creation*) ← **Customize → Skills → Upload skill**. يحتاج خط الإنتاج الكامل إلى إيفاد وكلاء فرعيين ويعمل على المنصات المذكورة أعلاه؛ أما المهارات البارزة فتعمل بصورة مستقلة.

**ChatGPT وسائر مضيفي Agent Plugins 1.0:** يشحن ContentForge ملف `plugin.json` في الجذر وفق معيار Agent Plugins 1.0 المحايد تجاه المزوّدين من OpenAI. وعلى المضيفين الذين لا يدعمون إيفاد الوكلاء الفرعيين، يشغّل **مسار التنفيذ المحمول** خط الإنتاج الكامل تسلسلياً في محادثة واحدة — المراحل نفسها، والمخرجات نفسها، وبوابات الجودة نفسها.

### 2. إعداد علامتك التجارية الأولى

```
/contentforge:brand-setup
```

يرافقك الوكيل خطوة بخطوة عبر صوت العلامة التجارية، والمصطلحات، والضوابط، وقواعد الاستشهاد، وبنية موقعك لأغراض الربط الداخلي. وعندما تزوّده بموقع إلكتروني، يجمع جرداً مُوثَّقاً للصفحات في خطوة تأكيد واحدة.

### 3. إنتاج المحتوى

```
/contentforge:create-content
```

اختر نوع المحتوى، والعلامة التجارية، والموضوع، وعدد الكلمات، والجمهور. يشغّل خط الإنتاج 10 مراحل (بحث ← تدقيق حقائق ← مسودة ← مرئيات ← تحقق ← هيكلة ← SEO ← أنسنة ← مراجعة ← إخراج)، ويفرض بوابة جودة بعد كل مرحلة، ويدقق التشغيل المكتمل مقابل مخرجاته هو نفسه، ويكتب ملف `.docx` حقيقياً.

### 4. العثور على مخرجاتك

```
~/Documents/ContentForge/<brand-slug>/<content-type>/<YYYY-MM>/<slug>.docx
```

يتضمن ملف `.docx` المتن والمراجع وأربعة ملاحق: بطاقة تقييم SEO، وبطاقة تقييم الجودة، وتفاصيل الإنتاج، وخريطة الروابط الداخلية.

### 5. إغلاق الحلقة

```
/contentforge:cf-aeo-check           # record which pieces AI engines cite
/contentforge:audit-content          # freshness-score the library; findings are RECORDED
/contentforge:cf-calendar --from-audit=latest   # next period: refreshes + gaps, from data
/contentforge:content-refresh        # execute a refresh at the audit's recommended scope
```

كل أمر يقرأ ما سجّله الأمر الذي سبقه — في جلسة جديدة، وفي يوم مختلف، وعلى يد زميل آخر.

---

## المنصات المدعومة (v4.1.1)

تسع منصات أصلية + رفع المهارات إلى claude.ai + أكثر من 35 عميلاً من عملاء Agent Skills:

| المنصة | التثبيت |
|---|---|
| **Claude Code** (سطر الأوامر + بيئة التطوير) | `/plugin install contentforge@neels-plugins` |
| **Anthropic Cowork** | لوحة Plugins ← Add marketplace ← `indranilbanerjee/neels-plugins` |
| **OpenAI Codex** | `codex plugin install contentforge@neels-plugins` |
| **Cursor 2.5+** | `/add-plugin contentforge@https://github.com/indranilbanerjee/contentforge` |
| **GitHub Copilot CLI** | `copilot plugin install contentforge@neels-plugins` |
| **Google Antigravity 2.0** | `agy plugin install https://github.com/indranilbanerjee/contentforge` |
| **Hermes Agent** | `hermes plugins install indranilbanerjee/contentforge` |
| **OpenClaw** | `openclaw plugins install git:github.com/indranilbanerjee/contentforge` |
| **Grok** (xAI Build CLI) | `grok plugin install indranilbanerjee/contentforge` |
| **claude.ai** (الويب) | ارفع إحدى مهارات `.skill` البارزة من [الإصدارات](https://github.com/indranilbanerjee/contentforge/releases/latest) |
| **ChatGPT / مضيفو Agent Plugins 1.0** | حزمة `plugin.json` في الجذر + مسار التنفيذ المحمول |

جميع ملفات SKILL.md البالغ عددها 22 قابلة للنقل بين المنصات عبر معيار Agent Skills المفتوح — وجّه أي عميل متوافق إلى `https://github.com/indranilbanerjee/contentforge/tree/master/skills`.

---

## التحديث

**Claude Code:** التحديث التلقائي معطَّل افتراضياً لأسواق الإضافات الخارجية. فعّله مرة واحدة: `/plugin` ← تبويب **Marketplaces** ← `neels-plugins` ← **Enable auto-update**. أو يدوياً: `/plugin marketplace update neels-plugins` ثم `/plugin uninstall` + `/plugin install contentforge@neels-plugins` + `/reload-plugins`.

**Cowork / claude.ai / Claude Desktop:** افتح لوحة Plugins في الواجهة ← أزل ContentForge ← أعد تثبيته من السوق (إعادة السحب تجلب أحدث إصدار).

**Codex:** ‏`codex plugin update contentforge` · **Cursor:** أعد تشغيل `/add-plugin` · **Copilot CLI:** ‏`copilot plugin update contentforge` · **Antigravity:** ‏`agy plugin update contentforge` · **Hermes:** ‏`hermes plugins update contentforge` · **OpenClaw:** ‏`openclaw plugins update contentforge` · **Grok:** ‏`grok plugin update contentforge` · **المهارات المرفوعة إلى claude.ai:** أعد تنزيل ملف `.skill` من أحدث إصدار ثم أعد رفعه.

---

## الأسئلة الشائعة (الأساسيات)

**أين تُحفَظ بياناتي؟** كل شيء محلي: ملفات تعريف العلامات التجارية ومخرجات التشغيل تحت `~/.claude-marketing/<brand>/`، والتسليمات النهائية تحت `~/Documents/ContentForge/`. لا يُرسَل أي شيء إلى أي جهة باستثناء استدعاءات النماذج التي تجريها منصتك أنت.

**هل أحتاج إلى ربط خوادم MCP أو التكاملات؟** لا. ملف `.mcp.json` المُضمَّن فارغ عن قصد — صفر خوادم تتصل تلقائياً. الموصلات كتالوج اختياري بالكامل (`/contentforge:cf-connect`).

**هل هذا جاهز للامتثال لقانون EU AI Act؟** نعم — توقيع C2PA لإثبات مصدر المحتوى مع إقرار الإفصاح عن الذكاء الاصطناعي وفق المادة 50، إضافة إلى طبقة إفصاح قابلة للتهيئة حسب العلامة التجارية (مبدأ أمان: غير مؤكد ⇐ أفصِح).

**هل يعمل خط الإنتاج الكامل خارج Claude Code؟** نعم — على المنصات التي لا تدعم إيفاد الوكلاء الفرعيين، يشغّل مسار التنفيذ المحمول المراحل العشر كلها تسلسلياً مع بقاء كل بوابة على حالها. الاستثناء الوحيد هو ملفات `.skill` المرفوعة إلى claude.ai: فتلك مهارات بارزة مستقلة، وليست خط الإنتاج.

---

## عن القائم على المشروع

‏ContentForge من بناء وصيانة **[Indranil "Neel" Banerjee](https://indranil.in)** — بانٍ ومفكر منهجي بجذور في أمن المعلومات، ومسيرة ثانية تمتد عبر تسويق النمو، والعمليات الرقمية المؤسسية، والتحول بالذكاء الاصطناعي. وهو جزء من حزمة **Neelverse Marketing Suite** الثلاثية إلى جانب [Digital Marketing Pro](https://github.com/indranilbanerjee/digital-marketing-pro) و[SocialForge](https://github.com/indranilbanerjee/socialforge).

إذا كان ContentForge يوفّر وقت فريقك، فامنح [⭐ نجمة للمستودع](https://github.com/indranilbanerjee/contentforge/stargazers) وفكّر في [رعاية المشروع ❤](https://github.com/sponsors/indranilbanerjee) — فهذا ما يُبقي وتيرة الإصدارات مستدامة.

**الرخصة:** MIT · **الأمان:** [تنبيهات أمنية خاصة](https://github.com/indranilbanerjee/contentforge/security/advisories/new) · **المشكلات:** [GitHub Issues](https://github.com/indranilbanerjee/contentforge/issues)
