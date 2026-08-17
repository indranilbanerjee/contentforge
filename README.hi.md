# ContentForge

🌐 **Read this in:** [English](README.md) · [हिन्दी](README.hi.md) · [中文](README.zh-CN.md) · [日本語](README.ja.md) · [한국어](README.ko.md) · [Español](README.es.md) · [Português](README.pt-BR.md) · [العربية](README.ar.md) · [اردو](README.ur.md) · [தமிழ்](README.ta.md) · [বাংলা](README.bn.md) · [Русский](README.ru.md)

> **अंग्रेज़ी README v4.1.1 (2026-08-17) के साथ सिंक किया गया।** [अंग्रेज़ी README](README.md) ही सत्य का स्रोत है — रिलीज़ नोट्स, स्किल्स/कमांड्स की पूरी सूची, आर्किटेक्चर, समस्या-निवारण और संपूर्ण FAQ वहीं उपलब्ध हैं। ContentForge को इंस्टॉल करने, चलाने और अपडेट करने के लिए आवश्यक हर जानकारी इस अनुवाद में मौजूद है।

> **आपको इस तिमाही में 30 ऐसे लेख प्रकाशित करने हैं जो इंसानी लगें, असली स्रोतों का हवाला दें, आपके फ़नल से जुड़ें, और उस संपादक की जाँच से पार उतरें जो सचमुच जाँच करता है। आपकी टीम में तीन लोग हैं। आपके पास नौ हफ़्ते हैं। आपका पिछला "AI-लिखित" बैच मनगढ़ंत आँकड़ों के कारण पकड़ा गया — और उससे पहले वाला बैच चुपचाप बासी हो गया और किसी का ध्यान तक नहीं गया।**

हर विषय पर `/contentforge:create-content` चलाइए। 10-चरणीय पाइपलाइन प्रकाशन-योग्य `.docx` तैयार करती है — 43-पैटर्न ह्यूमनाइज़र, fact-checker सबएजेंट, तीन-श्रेणी आंतरिक लिंकिंग और EU AI Act अनुपालन के लिए C2PA प्रोवेनेंस के साथ — प्रति लेख 30–60 मिनट में। और फिर वह हिस्सा जो किसी भी सिंगल-शॉट टूल के पास नहीं है: **लाइफ़साइकल लूप।** हर प्रकाशित लेख मापा जाता है, क्षरण (decay) के लिए ऑडिट होता है, और अगले कैलेंडर तथा अगली ब्रीफ़ में वापस जोड़ा जाता है — टिकाऊ फ़ाइल कॉन्ट्रैक्ट्स के ज़रिए, ताकि सिस्टम आपके ब्रांड के बारे में जो कुछ सीखता है, वह उस सत्र के ख़त्म होने के बाद भी बना रहे जिसमें उसने वह सीखा था।

ओपन-सोर्स एंटरप्राइज़ कंटेंट प्रोडक्शन सिस्टम — **22 स्किल्स · 13 विशेषज्ञ एजेंट · 10 क्वालिटी गेट · 43-पैटर्न AI-डिटेक्शन ह्यूमनाइज़र · एक रन ऑडिटर जो रन के स्वयं को पूर्ण घोषित करने से पहले हर गेट को दोबारा व्युत्पन्न करता है · 28 Python स्क्रिप्ट, केवल stdlib**। निर्माता: [Indranil Banerjee](https://indranil.in) · [LinkedIn](https://www.linkedin.com/in/askneelnow/) · [X](https://x.com/askneelnow)।

**संस्करण 4.1.1** · [चेंजलॉग](CHANGELOG.md) · MIT लाइसेंस · [इस प्रोजेक्ट को स्पॉन्सर करें ❤](https://github.com/sponsors/indranilbanerjee)

---

## ContentForge ही क्यों

अधिकांश AI लेखन टूल एक ही ड्राफ़्ट, एक ही लहजे में बनाते हैं, बिना किसी क्वालिटी गेट के — और लेख के प्रकाशित होते ही उसे भूल जाते हैं। ContentForge इसे शुरू से अंत तक ठीक करता है:

| क्षमता | यह क्यों मायने रखती है |
|---|---|
| **हर चरण के बाद क्वालिटी गेट वाली 10-चरणीय पाइपलाइन** | खराब आउटपुट आगे फैलने से पहले ही पकड़ा जाता है और दोबारा चलाया जाता है |
| **43-पैटर्न AI-डिटेक्शन ह्यूमनाइज़र** + आत्म-समीक्षा मेटा-पास | आउटपुट इंसानी लगता है, AI जैसा नहीं — अंदाज़े से नहीं, माप से सिद्ध |
| **Fact-checker सबएजेंट** URL सत्यापित करता है और दावों का क्रॉस-रेफ़रेंस करता है | उद्धरण काम करते हैं और मनगढ़ंत नहीं होते — हर आँकड़ा एक सत्यापित लेजर प्रविष्टि तक ट्रेस होता है |
| **तीन-श्रेणी आंतरिक लिंकिंग** (विषयगत / व्यावसायिक / प्राधिकार) | कंटेंट एक फ़नल बनता है, अलग-थलग पड़ा हुआ पन्ना नहीं |
| **असली `.docx` आउटपुट** — SEO + क्वालिटी + प्रोडक्शन + आंतरिक-लिंक परिशिष्टों के साथ | आपके संपादक को चालू हालत की Word फ़ाइल मिलती है, markdown नहीं |
| **एक रन ऑडिटर जो आर्टिफ़ैक्ट्स से हर गेट को दोबारा व्युत्पन्न करता है** | "पाइपलाइन कहती है कि काम पूरा हुआ" और "आर्टिफ़ैक्ट्स सिद्ध करते हैं कि पूरा हुआ" — ये दोनों कभी चुपचाप एक-दूसरे से अलग नहीं हो सकते |
| **लाइफ़साइकल लूप (v4.0)** — ऑडिट → रिफ़्रेश → मापन → योजना, फ़ाइल कॉन्ट्रैक्ट्स से आपस में जुड़े | प्रकाशित कंटेंट अब 'छोड़ो और भूल जाओ' नहीं रहता: क्षरण पकड़ा जाता है और रिफ़्रेश की प्राथमिकता डेटा से तय होती है |
| **C2PA कंटेंट प्रोवेनेंस साइनिंग** — EU AI Act के Article 50 अनुपालन के लिए | EU बाज़ारों में वितरित लंबे AI-सहायता-प्राप्त कंटेंट के लिए 2 अगस्त 2026 से प्रोवेनेंस अनिवार्य है |

## असली नतीजे, एक असली रन से

एक एंड-टू-एंड सत्यापन रन (अगस्त 2026, डिजिटल-संरक्षण परीक्षण ब्रांड, कीवर्ड "link rot" पर 1,200 शब्दों का ब्लॉग) — ठीक वैसा ही दर्ज, जैसा घटित हुआ:

- तथ्य-जाँच चरण ने पकड़ा कि शोध चरण ने एक आँकड़ा ग़लत पढ़ लिया था; उसने सुधारा हुआ वाक्यांश सत्यापित लेजर में लॉक कर दिया और मूल वाक्य को ड्राफ़्ट से प्रतिबंधित कर दिया। वह सुधार अक्षरशः, डिलीवर हुई Word फ़ाइल तक कायम रहा।
- सत्यापन चरण ने 42 दावों का लेजर से मिलान किया: **शून्य हैलुसिनेशन**।
- ह्यूमनाइज़र ने 7 श्रेणियों में फैले 20 AI-पैटर्न उदाहरण हटाए (हर पैटर्न के स्तर पर मापा गया, हर संपादन का पहले/बाद रिकॉर्ड लॉग हुआ) — जबकि हर तथ्य, उद्धरण और SEO प्लेसमेंट बाइट-स्तर पर अपरिवर्तित रहा।
- समीक्षा चरण ने **9.0/10 (ग्रेड A)** पर मंज़ूरी दी — कंटेंट गुणवत्ता 8.8, उद्धरण अखंडता 8.9, ब्रांड अनुपालन 9.6, SEO 8.6, पठनीयता 8.8।
- रन ऑडिटर ने डिस्क पर मौजूद आर्टिफ़ैक्ट्स से सब कुछ दोबारा व्युत्पन्न किया: **14 जाँचें उत्तीर्ण, 0 विफल** — तभी जाकर रन को स्वयं को पूर्ण घोषित करने की अनुमति मिली।

बात यह नहीं कि पाइपलाइन कभी ग़लती नहीं करती — बात यह है कि उसकी ग़लतियाँ उसकी अपनी मशीनरी द्वारा, रिकॉर्ड पर, आपके संपादक की नज़र फ़ाइल पर पड़ने से पहले ही पकड़ ली जाती हैं। असली आर्टिफ़ैक्ट्स (वास्तविक चार्ट, वास्तविक पहले/बाद के संपादन, वास्तविक स्कोरकार्ड) [अंग्रेज़ी README](README.md#examples) में देखें।

---

## त्वरित शुरुआत

### 1. इंस्टॉल करें

**Claude Code (CLI या VS Code/JetBrains एक्सटेंशन):**

```bash
/plugin marketplace add indranilbanerjee/neels-plugins
/plugin install contentforge@neels-plugins
```

**Anthropic Cowork:** UI में **Plugins** पैनल खोलें → Add marketplace → `indranilbanerjee/neels-plugins` → ContentForge इंस्टॉल करें। (`/plugin` स्लैश कमांड Cowork में काम नहीं करते — UI पैनल का उपयोग करें।) फिर टीम के साथ साझा किए जा सकने वाले आउटपुट के लिए Google Drive को जोड़ने हेतु `/contentforge:cf-cowork-setup` एक बार चलाएँ।

**OpenAI Codex (CLI + IDE + ऐप):**

```bash
codex plugin marketplace add indranilbanerjee/neels-plugins
codex plugin install contentforge@neels-plugins
```

**अन्य प्लेटफ़ॉर्म:**

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

**claude.ai (वेब):** [नवीनतम रिलीज़](https://github.com/indranilbanerjee/contentforge/releases/latest) से कोई हीरो स्किल डाउनलोड करें — `cf-brief.skill`, `cf-social-adapt.skill`, `cf-translate.skill`, `cf-video-script.skill`, या `cf-aeo-check.skill` — फिर claude.ai में: **Settings → Capabilities** (*Code execution and file creation* सक्षम करें) → **Customize → Skills → Upload skill**। पूरी पाइपलाइन को सबएजेंट डिस्पैच चाहिए और वह ऊपर बताए गए प्लेटफ़ॉर्म पर चलती है; हीरो स्किल्स अपने आप में स्वतंत्र रूप से काम करती हैं।

**ChatGPT और अन्य Agent Plugins 1.0 होस्ट:** ContentForge OpenAI के वेंडर-न्यूट्रल Agent Plugins 1.0 मानक पर एक रूट `plugin.json` के साथ आता है। जिन होस्ट में सबएजेंट डिस्पैच नहीं है, वहाँ **पोर्टेबल एग्ज़ीक्यूशन लेन** पूरी पाइपलाइन को एक ही बातचीत में क्रमवार चलाती है — वही चरण, वही आर्टिफ़ैक्ट्स, वही क्वालिटी गेट।

### 2. अपना पहला ब्रांड सेट करें

```
/contentforge:brand-setup
```

एजेंट आपको ब्रांड वॉइस, शब्दावली, गार्डरेल, उद्धरण नियमों और आंतरिक लिंकिंग के लिए आपकी साइट-संरचना से चरण-दर-चरण गुज़ारता है। जब आप उसे कोई वेबसाइट देते हैं, तो वह एक ही पुष्टि-चरण में सत्यापित पेज इन्वेंटरी तैयार कर लेता है।

### 3. कंटेंट बनाएँ

```
/contentforge:create-content
```

कंटेंट का प्रकार, ब्रांड, विषय, शब्द-संख्या और लक्षित पाठक चुनें। पाइपलाइन 10 चरण चलाती है (शोध → तथ्य-जाँच → ड्राफ़्ट → विज़ुअल → सत्यापन → संरचना → SEO → ह्यूमनाइज़ → समीक्षा → आउटपुट), हर चरण के बाद क्वालिटी गेट लागू करती है, पूर्ण हुए रन का उसके अपने आर्टिफ़ैक्ट्स के विरुद्ध ऑडिट करती है, और एक असली `.docx` लिखती है।

### 4. अपना आउटपुट कहाँ मिलेगा

```
~/Documents/ContentForge/<brand-slug>/<content-type>/<YYYY-MM>/<slug>.docx
```

`.docx` में मुख्य पाठ, संदर्भ और चार परिशिष्ट शामिल हैं: SEO स्कोरकार्ड, क्वालिटी स्कोरकार्ड, प्रोडक्शन विवरण और आंतरिक लिंक मैप।

### 5. लूप पूरा करें

```
/contentforge:cf-aeo-check           # record which pieces AI engines cite
/contentforge:audit-content          # freshness-score the library; findings are RECORDED
/contentforge:cf-calendar --from-audit=latest   # next period: refreshes + gaps, from data
/contentforge:content-refresh        # execute a refresh at the audit's recommended scope
```

हर कमांड वही पढ़ती है जो पिछली कमांड ने दर्ज किया था — नए सत्र में, किसी और दिन, किसी और टीम-साथी के हाथों।

---

## समर्थित प्लेटफ़ॉर्म (v4.1.1)

नौ नेटिव प्लेटफ़ॉर्म + claude.ai अपलोड + 35+ Agent Skills क्लाइंट:

| प्लेटफ़ॉर्म | इंस्टॉल |
|---|---|
| **Claude Code** (CLI + IDE) | `/plugin install contentforge@neels-plugins` |
| **Anthropic Cowork** | Plugins पैनल → Add marketplace → `indranilbanerjee/neels-plugins` |
| **OpenAI Codex** | `codex plugin install contentforge@neels-plugins` |
| **Cursor 2.5+** | `/add-plugin contentforge@https://github.com/indranilbanerjee/contentforge` |
| **GitHub Copilot CLI** | `copilot plugin install contentforge@neels-plugins` |
| **Google Antigravity 2.0** | `agy plugin install https://github.com/indranilbanerjee/contentforge` |
| **Hermes Agent** | `hermes plugins install indranilbanerjee/contentforge` |
| **OpenClaw** | `openclaw plugins install git:github.com/indranilbanerjee/contentforge` |
| **Grok** (xAI Build CLI) | `grok plugin install indranilbanerjee/contentforge` |
| **claude.ai** (वेब) | [रिलीज़](https://github.com/indranilbanerjee/contentforge/releases/latest) से हीरो `.skill` अपलोड करें |
| **ChatGPT / Agent Plugins 1.0 होस्ट** | रूट `plugin.json` पैकेज + पोर्टेबल एग्ज़ीक्यूशन लेन |

सभी 22 SKILL.md फ़ाइलें Agent Skills ओपन स्टैंडर्ड के ज़रिए प्लेटफ़ॉर्म-पोर्टेबल हैं — किसी भी संगत क्लाइंट को `https://github.com/indranilbanerjee/contentforge/tree/master/skills` पर पॉइंट करें।

---

## अपडेट करना

**Claude Code:** थर्ड-पार्टी मार्केटप्लेस में ऑटो-अपडेट डिफ़ॉल्ट रूप से बंद (OFF) रहता है। इसे एक बार चालू करें: `/plugin` → **Marketplaces** टैब → `neels-plugins` → **Enable auto-update**। या मैन्युअल रूप से: `/plugin marketplace update neels-plugins`, फिर `/plugin uninstall` + `/plugin install contentforge@neels-plugins` + `/reload-plugins`।

**Cowork / claude.ai / Claude Desktop:** Plugins UI पैनल खोलें → ContentForge हटाएँ → मार्केटप्लेस से दोबारा इंस्टॉल करें (दोबारा खींचने पर नवीनतम संस्करण आ जाता है)।

**Codex:** `codex plugin update contentforge` · **Cursor:** `/add-plugin` दोबारा चलाएँ · **Copilot CLI:** `copilot plugin update contentforge` · **Antigravity:** `agy plugin update contentforge` · **Hermes:** `hermes plugins update contentforge` · **OpenClaw:** `openclaw plugins update contentforge` · **Grok:** `grok plugin update contentforge` · **claude.ai अपलोड:** नवीनतम रिलीज़ से `.skill` दोबारा डाउनलोड करके फिर से अपलोड करें।

---

## FAQ (ज़रूरी बातें)

**मेरा डेटा कहाँ रहता है?** सब कुछ लोकल है: ब्रांड प्रोफ़ाइल और रन आर्टिफ़ैक्ट्स `~/.claude-marketing/<brand>/` के अंतर्गत, डिलीवरेबल्स `~/Documents/ContentForge/` के अंतर्गत। आपके अपने प्लेटफ़ॉर्म द्वारा किए जाने वाले मॉडल कॉल के अलावा कहीं कुछ नहीं भेजा जाता।

**क्या मुझे MCP/इंटीग्रेशन कनेक्ट करने होंगे?** नहीं। शिप की गई `.mcp.json` जान-बूझकर खाली रखी गई है — शून्य ऑटो-कनेक्टिंग सर्वर। कनेक्टर एक ऑप्ट-इन कैटलॉग हैं (`/contentforge:cf-connect`)।

**क्या यह EU AI Act के लिए तैयार है?** हाँ — Article 50 AI-प्रकटीकरण एसर्शन के साथ C2PA कंटेंट प्रोवेनेंस साइनिंग, साथ ही ब्रांड-कॉन्फ़िगर होने योग्य प्रकटीकरण परत (अनिश्चित ⇒ प्रकट करें — फ़ेल-सेफ़)।

**क्या पूरी पाइपलाइन Claude Code के बाहर भी चलती है?** हाँ — जिन प्लेटफ़ॉर्म में सबएजेंट डिस्पैच नहीं है, वहाँ पोर्टेबल एग्ज़ीक्यूशन लेन सभी 10 चरण क्रमवार चलाती है, हर गेट यथावत रहते हुए। एकमात्र अपवाद claude.ai के `.skill` अपलोड हैं: वे स्वतंत्र हीरो स्किल्स हैं, पाइपलाइन नहीं।

---

## मेंटेनर के बारे में

ContentForge को **[Indranil "Neel" Banerjee](https://indranil.in)** बनाते और सँभालते हैं — सूचना सुरक्षा में जड़ें रखने वाले एक बिल्डर और सिस्टम्स-थिंकर, जिनकी दूसरी पारी ग्रोथ मार्केटिंग, एंटरप्राइज़ डिजिटल ऑपरेशंस और AI ट्रांसफ़ॉर्मेशन तक फैली है। यह [Digital Marketing Pro](https://github.com/indranilbanerjee/digital-marketing-pro) और [SocialForge](https://github.com/indranilbanerjee/socialforge) के साथ तीन-प्लगइन **Neelverse Marketing Suite** का हिस्सा है।

अगर ContentForge आपकी टीम का समय बचाता है, तो [⭐ रिपो को स्टार करें](https://github.com/indranilbanerjee/contentforge/stargazers) और [प्रोजेक्ट को स्पॉन्सर करने ❤](https://github.com/sponsors/indranilbanerjee) पर विचार करें — इसी से रिलीज़ की रफ़्तार टिकाऊ बनी रहती है।

**लाइसेंस:** MIT · **सुरक्षा:** [निजी एडवाइज़री](https://github.com/indranilbanerjee/contentforge/security/advisories/new) · **समस्याएँ:** [GitHub Issues](https://github.com/indranilbanerjee/contentforge/issues)
