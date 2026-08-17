# ContentForge

🌐 **Read this in:** [English](README.md) · [हिन्दी](README.hi.md) · [中文](README.zh-CN.md) · [日本語](README.ja.md) · [한국어](README.ko.md) · [Español](README.es.md) · [Português](README.pt-BR.md) · [العربية](README.ar.md) · [اردو](README.ur.md) · [தமிழ்](README.ta.md) · [বাংলা](README.bn.md) · [Русский](README.ru.md)

> **Синхронизировано с английским README v4.1.2 (2026-08-17).** [Английский README](README.md) — источник истины: там находятся примечания к релизам, полный каталог навыков и команд, описание архитектуры, руководство по устранению неполадок и полный FAQ. Этот перевод покрывает всё необходимое, чтобы установить, запустить и обновлять ContentForge.

> **Вам нужно выпустить за квартал 30 статей — таких, которые звучат по-человечески, ссылаются на реальные источники, встраиваются в вашу воронку и выдерживают проверку редактора, который действительно проверяет. В команде три человека. У вас девять недель. Прошлую партию «написанного ИИ» контента завернули за выдуманную статистику, а партия до неё тихо устарела — и никто этого не заметил.**

Запустите `/contentforge:create-content` для каждой темы. 10-фазный конвейер выдаёт готовый к публикации `.docx`: хуманизатор с 43 паттернами против ИИ-детекции, субагент-фактчекер, внутренняя перелинковка по трём категориям и C2PA-подпись происхождения для соответствия EU AI Act — за 30–60 минут на материал. А дальше — то, чего нет ни у одного «одноразового» инструмента: **петля жизненного цикла.** Каждый опубликованный материал измеряется, проверяется на устаревание и возвращается в следующий календарь и следующий бриф — через долговечные файловые контракты, так что всё, что система узнала о вашем бренде, переживает сессию, в которой это было узнано.

Система производства контента корпоративного уровня с открытым исходным кодом — **22 навыка · 13 агентов-специалистов · 10 гейтов качества · хуманизатор с 43 паттернами против ИИ-детекции · аудитор прогонов, заново выводящий каждый гейт, прежде чем прогон получит право назвать себя завершённым · 28 Python-скриптов, только стандартная библиотека**. Автор — [Indranil Banerjee](https://indranil.in) · [LinkedIn](https://www.linkedin.com/in/askneelnow/) · [X](https://x.com/askneelnow).

**Версия 4.1.2** · [История изменений](CHANGELOG.md) · Лицензия MIT · [Поддержать проект ❤](https://github.com/sponsors/indranilbanerjee)

---

## Почему ContentForge

Большинство ИИ-инструментов для текстов выдают один черновик, в одном тоне, без контроля качества — и забывают о материале в момент публикации. ContentForge закрывает эту проблему от начала до конца:

| Возможность | Почему это важно |
|---|---|
| **10-фазный конвейер с гейтом качества после каждой фазы** | Плохой результат отлавливается и переделывается до того, как расползётся дальше по конвейеру |
| **Хуманизатор с 43 паттернами ИИ-детекции** + мета-проход самокритики | Текст читается как человеческий, а не машинный — и это измеряется, а не оценивается «на глаз» |
| **Субагент-фактчекер** проверяет URL и сверяет утверждения с источниками | Цитаты работают и не выдуманы — каждая цифра прослеживается до записи в верифицированном реестре |
| **Внутренняя перелинковка по трём категориям** (тематическая / коммерческая / авторитетная) | Контент становится воронкой, а не изолированной страницей |
| **Настоящий `.docx` на выходе** с приложениями: SEO, качество, производство, карта внутренних ссылок | Редактор получает рабочий файл Word, а не markdown |
| **Аудитор прогонов, заново выводящий каждый гейт из артефактов** | «Конвейер говорит, что завершился» и «артефакты доказывают, что он завершился» больше не могут незаметно разойтись |
| **Петля жизненного цикла (v4.0)** — аудит → обновление → измерение → планирование, связанные файловыми контрактами | Опубликованный контент перестаёт жить по принципу «выстрелил и забыл»: устаревание обнаруживается, обновления приоритизируются по данным |
| **C2PA-подпись происхождения контента** для соответствия статье 50 EU AI Act | Длинному контенту, созданному с участием ИИ и распространяемому на рынках ЕС, метка происхождения нужна со 2 августа 2026 года |

## Реальные результаты, из реального прогона

Сквозной валидационный прогон (август 2026, тестовый бренд в сфере цифрового архивирования, блог-пост на 1200 слов по ключевому слову «link rot») — описан ровно так, как он прошёл:

- Фаза фактчекинга поймала фазу исследования на неверном прочтении статистики, зафиксировала исправленную формулировку в верифицированном реестре и запретила исходное предложение в черновике. Исправление дошло до финального файла Word дословно.
- Фаза валидации сверила 42 утверждения с реестром: **ноль галлюцинаций**.
- Хуманизатор убрал 20 вхождений ИИ-паттернов по 7 категориям (замер по каждому паттерну, лог «до/после» для каждой правки), при этом каждый факт, каждая цитата и каждое SEO-размещение остались нетронутыми байт в байт.
- Фаза ревью одобрила материал с оценкой **9.0/10 (класс A)** — качество контента 8.8, целостность цитирования 8.9, соответствие бренду 9.6, SEO 8.6, читабельность 8.8.
- Аудитор прогона заново вывел всё из артефактов на диске: **14 проверок пройдено, 0 провалено** — и только после этого прогону было позволено назвать себя завершённым.

Суть не в том, что конвейер никогда не ошибается, — а в том, что его ошибки ловит его же собственная механика, под запись, прежде чем файл увидит ваш редактор. Реальные артефакты (настоящий график, настоящие правки «до/после», настоящая карточка оценок) — в [английском README](README.md#examples).

---

## Быстрый старт

### 1. Установка

**Claude Code (CLI или расширение для VS Code/JetBrains):**

```bash
/plugin marketplace add indranilbanerjee/neels-plugins
/plugin install contentforge@neels-plugins
```

**Anthropic Cowork:** откройте панель **Plugins** в интерфейсе → Add marketplace → `indranilbanerjee/neels-plugins` → установите ContentForge. (Слэш-команды `/plugin` в Cowork не работают — используйте панель в UI.) Затем один раз запустите `/contentforge:cf-cowork-setup`, чтобы подключить Google Drive и сделать результаты доступными всей команде.

**OpenAI Codex (CLI + IDE + приложение):**

```bash
codex plugin marketplace add indranilbanerjee/neels-plugins
codex plugin install contentforge@neels-plugins
```

**Другие платформы:**

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

**claude.ai (веб):** скачайте один из флагманских навыков со страницы [последнего релиза](https://github.com/indranilbanerjee/contentforge/releases/latest) — `cf-brief.skill`, `cf-social-adapt.skill`, `cf-translate.skill`, `cf-video-script.skill` или `cf-aeo-check.skill` — затем в claude.ai: **Settings → Capabilities** (включите *Code execution and file creation*) → **Customize → Skills → Upload skill**. Полному конвейеру нужна диспетчеризация субагентов — он работает на перечисленных выше платформах; флагманские навыки работают автономно.

**ChatGPT и другие хосты Agent Plugins 1.0:** ContentForge поставляет корневой `plugin.json` по вендор-нейтральному стандарту Agent Plugins 1.0 от OpenAI. На хостах без диспетчеризации субагентов **портативный режим выполнения** прогоняет весь конвейер последовательно в одном диалоге — те же фазы, те же артефакты, те же гейты качества.

### 2. Настройте первый бренд

```
/contentforge:brand-setup
```

Агент проведёт вас через голос бренда, терминологию, ограничители, правила цитирования и структуру вашего сайта для внутренней перелинковки. Если вы дадите ему адрес сайта, он за один шаг подтверждения соберёт верифицированную опись страниц.

### 3. Сгенерируйте контент

```
/contentforge:create-content
```

Выберите тип контента, бренд, тему, объём в словах и аудиторию. Конвейер проходит 10 фаз (исследование → фактчекинг → черновик → визуал → валидация → структура → SEO → хуманизация → ревью → выпуск), применяет гейт качества после каждой фазы, сверяет завершённый прогон с его собственными артефактами и записывает настоящий `.docx`.

### 4. Найдите результат

```
~/Documents/ContentForge/<brand-slug>/<content-type>/<YYYY-MM>/<slug>.docx
```

`.docx` включает основной текст, список источников и четыре приложения: карточку оценок SEO, карточку оценок качества, детали производства и карту внутренних ссылок.

### 5. Замкните петлю

```
/contentforge:cf-aeo-check           # record which pieces AI engines cite
/contentforge:audit-content          # freshness-score the library; findings are RECORDED
/contentforge:cf-calendar --from-audit=latest   # next period: refreshes + gaps, from data
/contentforge:content-refresh        # execute a refresh at the audit's recommended scope
```

Каждая команда читает то, что записала предыдущая, — в новой сессии, в другой день, руками другого коллеги.

---

## Поддерживаемые платформы (v4.1.2)

Девять нативных платформ + загрузки на claude.ai + 35+ клиентов Agent Skills:

| Платформа | Установка |
|---|---|
| **Claude Code** (CLI + IDE) | `/plugin install contentforge@neels-plugins` |
| **Anthropic Cowork** | Панель Plugins → Add marketplace → `indranilbanerjee/neels-plugins` |
| **OpenAI Codex** | `codex plugin install contentforge@neels-plugins` |
| **Cursor 2.5+** | `/add-plugin contentforge@https://github.com/indranilbanerjee/contentforge` |
| **GitHub Copilot CLI** | `copilot plugin install contentforge@neels-plugins` |
| **Google Antigravity 2.0** | `agy plugin install https://github.com/indranilbanerjee/contentforge` |
| **Hermes Agent** | `hermes plugins install indranilbanerjee/contentforge` |
| **OpenClaw** | `openclaw plugins install git:github.com/indranilbanerjee/contentforge` |
| **Grok** (xAI Build CLI) | `grok plugin install indranilbanerjee/contentforge` |
| **claude.ai** (веб) | Загрузите флагманский `.skill` со страницы [релизов](https://github.com/indranilbanerjee/contentforge/releases/latest) |
| **ChatGPT / хосты Agent Plugins 1.0** | Корневой пакет `plugin.json` + портативный режим выполнения |

Все 22 файла SKILL.md переносимы между платформами благодаря открытому стандарту Agent Skills — направьте любой совместимый клиент на `https://github.com/indranilbanerjee/contentforge/tree/master/skills`.

---

## Обновление

**Claude Code:** у сторонних маркетплейсов автообновление по умолчанию ВЫКЛЮЧЕНО. Включите его один раз: `/plugin` → вкладка **Marketplaces** → `neels-plugins` → **Enable auto-update**. Или вручную: `/plugin marketplace update neels-plugins`, затем `/plugin uninstall` + `/plugin install contentforge@neels-plugins` + `/reload-plugins`.

**Cowork / claude.ai / Claude Desktop:** откройте панель Plugins в UI → удалите ContentForge → установите заново из маркетплейса (при переустановке подтянется последняя версия).

**Codex:** `codex plugin update contentforge` · **Cursor:** повторно выполните `/add-plugin` · **Copilot CLI:** `copilot plugin update contentforge` · **Antigravity:** `agy plugin update contentforge` · **Hermes:** `hermes plugins update contentforge` · **OpenClaw:** `openclaw plugins update contentforge` · **Grok:** `grok plugin update contentforge` · **загрузки на claude.ai:** заново скачайте `.skill` из последнего релиза и загрузите его повторно.

---

## FAQ (главное)

**Где хранятся мои данные?** Всё локально: профили брендов и артефакты прогонов — в `~/.claude-marketing/<brand>/`, готовые материалы — в `~/Documents/ContentForge/`. Никуда ничего не отправляется, кроме обращений к модели, которые делает ваша собственная платформа.

**Нужно ли подключать MCP-серверы или интеграции?** Нет. Поставляемый `.mcp.json` намеренно пуст — ноль автоподключающихся серверов. Коннекторы — это опциональный каталог (`/contentforge:cf-connect`).

**Готов ли ContentForge к EU AI Act?** Да — C2PA-подпись происхождения контента с декларацией об использовании ИИ по статье 50, плюс настраиваемый на уровне бренда слой раскрытия (принцип «не уверен ⇒ раскрой» как отказоустойчивое поведение).

**Работает ли полный конвейер вне Claude Code?** Да — на платформах без диспетчеризации субагентов портативный режим выполнения проходит все 10 фаз последовательно, со всеми гейтами качества. Единственное исключение — загрузки `.skill` на claude.ai: это автономные флагманские навыки, а не конвейер.

---

## Об авторе

ContentForge создаёт и сопровождает **[Indranil "Neel" Banerjee](https://indranil.in)** — инженер и системный мыслитель с корнями в информационной безопасности и вторым актом карьеры в growth-маркетинге, цифровых операциях предприятий и ИИ-трансформации. Часть трио плагинов **Neelverse Marketing Suite** вместе с [Digital Marketing Pro](https://github.com/indranilbanerjee/digital-marketing-pro) и [SocialForge](https://github.com/indranilbanerjee/socialforge).

Если ContentForge экономит время вашей команде, [⭐ поставьте репозиторию звезду](https://github.com/indranilbanerjee/contentforge/stargazers) и подумайте о [спонсорстве проекта ❤](https://github.com/sponsors/indranilbanerjee) — это помогает поддерживать стабильный ритм релизов.

**Лицензия:** MIT · **Безопасность:** [приватные уведомления об уязвимостях](https://github.com/indranilbanerjee/contentforge/security/advisories/new) · **Вопросы и баги:** [GitHub Issues](https://github.com/indranilbanerjee/contentforge/issues)
