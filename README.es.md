# ContentForge

🌐 **Read this in:** [English](README.md) · [हिन्दी](README.hi.md) · [中文](README.zh-CN.md) · [日本語](README.ja.md) · [한국어](README.ko.md) · [Español](README.es.md) · [Português](README.pt-BR.md) · [العربية](README.ar.md) · [اردو](README.ur.md) · [தமிழ்](README.ta.md) · [বাংলা](README.bn.md) · [Русский](README.ru.md)

> **Sincronizado con el README en inglés v4.1.2 (2026-08-17).** El [README en inglés](README.md) es la fuente de verdad: allí encontrarás las notas de versión, el catálogo completo de skills y comandos, la arquitectura, la resolución de problemas y las preguntas frecuentes completas. Esta traducción cubre todo lo que necesitas para instalar, ejecutar y actualizar ContentForge.

> **Tienes que publicar 30 artículos este trimestre que suenen humanos, citen fuentes reales, enlacen con tu embudo y superen la revisión de un editor exigente. Tu equipo es de tres personas. Tienes nueve semanas. Tu último lote «escrito con IA» fue señalado por estadísticas alucinadas — y el lote anterior quedó desactualizado sin que nadie se diera cuenta.**

Ejecuta `/contentforge:create-content` con cada tema. El pipeline de 10 fases produce un `.docx` listo para publicar, con un humanizador de 43 patrones, un subagente verificador de datos, enlazado interno de tres categorías y procedencia C2PA para cumplir con la EU AI Act — en 30–60 minutos por pieza. Y después, lo que ninguna herramienta de un solo disparo ofrece: **el ciclo de vida completo.** Cada pieza publicada se mide, se audita en busca de deterioro y alimenta el siguiente calendario y el siguiente brief — mediante contratos de archivos duraderos, de modo que lo que el sistema aprende sobre tu marca sobrevive a la sesión en la que lo aprendió.

Sistema de producción de contenido empresarial de código abierto — **22 skills · 13 agentes especialistas · 10 puertas de calidad · humanizador anti-detección de IA de 43 patrones · un auditor de ejecución que rederiva cada puerta antes de que una ejecución pueda darse por terminada · 28 scripts de Python, solo con la biblioteca estándar**. Creado por [Indranil Banerjee](https://indranil.in) · [LinkedIn](https://www.linkedin.com/in/askneelnow/) · [X](https://x.com/askneelnow).

**Versión 4.1.2** · [Registro de cambios](CHANGELOG.md) · Licencia MIT · [Patrocina este proyecto ❤](https://github.com/sponsors/indranilbanerjee)

---

## Por qué ContentForge

La mayoría de las herramientas de escritura con IA producen un solo borrador, en un solo tono, sin puertas de calidad, y olvidan la pieza en cuanto se publica. ContentForge resuelve esto de principio a fin:

| Capacidad | Por qué importa |
|---|---|
| **Pipeline de 10 fases con una puerta de calidad tras cada fase** | Los resultados deficientes se detectan y se reejecutan antes de propagarse a las fases siguientes |
| **Humanizador anti-detección de IA de 43 patrones** + metapase de autocrítica | El texto se lee humano, no como IA — medido con datos, no con sensaciones |
| **Subagente verificador de datos** que valida URLs y contrasta las afirmaciones | Las citas funcionan y no son alucinadas — cada estadística se remonta a una entrada verificada del registro |
| **Enlazado interno de tres categorías** (temático / comercial / de autoridad) | El contenido se convierte en un embudo, no en una página huérfana |
| **Salida real en `.docx`** con apéndices de SEO + Calidad + Producción + Enlaces internos | Tu editor recibe un archivo de Word funcional, no markdown |
| **Un auditor de ejecución que rederiva cada puerta a partir de los artefactos** | «El pipeline dice que terminó» y «los artefactos demuestran que terminó» nunca pueden divergir en silencio |
| **El ciclo de vida (v4.0)** — auditar → refrescar → medir → planificar, unido por contratos de archivos | El contenido publicado deja de ser «publicar y olvidar»: el deterioro se detecta y los refrescos se priorizan con datos |
| **Firma de procedencia de contenido C2PA** para cumplir el Artículo 50 de la EU AI Act | El contenido largo asistido por IA distribuido en mercados de la UE necesita procedencia desde el 2 de agosto de 2026 |

## Resultados reales, de una ejecución real

Una ejecución de validación de extremo a extremo (agosto de 2026, una marca de prueba de preservación digital, un blog de 1.200 palabras sobre la palabra clave "link rot") — reportada exactamente como ocurrió:

- La fase de verificación de datos detectó que la fase de investigación había malinterpretado una estadística, fijó la redacción corregida en un registro verificado y prohibió la frase original en el borrador. La corrección sobrevivió, palabra por palabra, hasta el archivo de Word entregado.
- La fase de validación contrastó 42 afirmaciones contra el registro: **cero alucinaciones**.
- El humanizador eliminó 20 instancias de patrones de IA en 7 categorías (medidas por patrón, con registro del antes y el después de cada edición) manteniendo intactos, byte a byte, cada dato, cita y colocación SEO.
- La fase de revisión aprobó con **9.0/10 (calificación A)** — calidad de contenido 8.8, integridad de citas 8.9, cumplimiento de marca 9.6, SEO 8.6, legibilidad 8.8.
- El auditor de ejecución rederivó todo a partir de los artefactos en disco: **14 comprobaciones superadas, 0 fallidas** — solo entonces se permitió que la ejecución se declarara completada.

La cuestión no es que el pipeline nunca se equivoque, sino que sus errores los detecta su propia maquinaria, con constancia documentada, antes de que tu editor vea el archivo. Consulta los artefactos reales (el gráfico real, las ediciones reales de antes y después, la ficha de puntuación real) en el [README en inglés](README.md#examples).

---

## Inicio rápido

### 1. Instalación

**Claude Code (CLI o extensión de VS Code/JetBrains):**

```bash
/plugin marketplace add indranilbanerjee/neels-plugins
/plugin install contentforge@neels-plugins
```

**Anthropic Cowork:** abre el panel **Plugins** en la interfaz → Add marketplace → `indranilbanerjee/neels-plugins` → Instala ContentForge. (Los comandos de barra `/plugin` no funcionan en Cowork — usa el panel de la interfaz.) Después ejecuta `/contentforge:cf-cowork-setup` una vez para conectar Google Drive y compartir la salida con tu equipo.

**OpenAI Codex (CLI + IDE + App):**

```bash
codex plugin marketplace add indranilbanerjee/neels-plugins
codex plugin install contentforge@neels-plugins
```

**Otras plataformas:**

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

**claude.ai (web):** descarga una skill destacada desde [la última versión publicada](https://github.com/indranilbanerjee/contentforge/releases/latest) — `cf-brief.skill`, `cf-social-adapt.skill`, `cf-translate.skill`, `cf-video-script.skill` o `cf-aeo-check.skill` — y luego, en claude.ai: **Settings → Capabilities** (activa *Code execution and file creation*) → **Customize → Skills → Upload skill**. El pipeline completo requiere el despacho de subagentes y se ejecuta en las plataformas anteriores; las skills destacadas funcionan de forma independiente.

**ChatGPT y otros hosts de Agent Plugins 1.0:** ContentForge incluye un `plugin.json` raíz conforme al estándar neutral de proveedor Agent Plugins 1.0 de OpenAI. En hosts sin despacho de subagentes, el **carril de ejecución portátil** ejecuta el pipeline completo de forma secuencial en una sola conversación — mismas fases, mismos artefactos, mismas puertas de calidad.

### 2. Configura tu primera marca

```
/contentforge:brand-setup
```

El agente te guía por la voz de marca, la terminología, las salvaguardas, las reglas de citación y la estructura de tu sitio para el enlazado interno. Cuando le proporcionas un sitio web, recopila un inventario verificado de páginas en un solo paso de confirmación.

### 3. Genera contenido

```
/contentforge:create-content
```

Elige el tipo de contenido, la marca, el tema, la extensión y la audiencia. El pipeline ejecuta 10 fases (investigación → verificación de datos → borrador → visuales → validación → estructura → SEO → humanización → revisión → salida), aplica una puerta de calidad tras cada fase, audita la ejecución terminada contra sus propios artefactos y genera un `.docx` real.

### 4. Encuentra tu resultado

```
~/Documents/ContentForge/<brand-slug>/<content-type>/<YYYY-MM>/<slug>.docx
```

El `.docx` incluye el cuerpo, las referencias y cuatro apéndices: ficha de puntuación SEO, ficha de puntuación de calidad, detalles de producción y el mapa de enlaces internos.

### 5. Cierra el ciclo

```
/contentforge:cf-aeo-check           # record which pieces AI engines cite
/contentforge:audit-content          # freshness-score the library; findings are RECORDED
/contentforge:cf-calendar --from-audit=latest   # next period: refreshes + gaps, from data
/contentforge:content-refresh        # execute a refresh at the audit's recommended scope
```

Cada comando lee lo que el anterior dejó registrado — en una sesión nueva, en un día distinto, por otro compañero de equipo.

---

## Plataformas compatibles (v4.1.2)

Nueve plataformas nativas + cargas en claude.ai + más de 35 clientes de Agent Skills:

| Plataforma | Instalación |
|---|---|
| **Claude Code** (CLI + IDE) | `/plugin install contentforge@neels-plugins` |
| **Anthropic Cowork** | Panel de Plugins → Add marketplace → `indranilbanerjee/neels-plugins` |
| **OpenAI Codex** | `codex plugin install contentforge@neels-plugins` |
| **Cursor 2.5+** | `/add-plugin contentforge@https://github.com/indranilbanerjee/contentforge` |
| **GitHub Copilot CLI** | `copilot plugin install contentforge@neels-plugins` |
| **Google Antigravity 2.0** | `agy plugin install https://github.com/indranilbanerjee/contentforge` |
| **Hermes Agent** | `hermes plugins install indranilbanerjee/contentforge` |
| **OpenClaw** | `openclaw plugins install git:github.com/indranilbanerjee/contentforge` |
| **Grok** (xAI Build CLI) | `grok plugin install indranilbanerjee/contentforge` |
| **claude.ai** (web) | Sube una `.skill` destacada desde [las versiones publicadas](https://github.com/indranilbanerjee/contentforge/releases/latest) |
| **ChatGPT / hosts de Agent Plugins 1.0** | Paquete `plugin.json` raíz + carril de ejecución portátil |

Los 22 archivos SKILL.md son portables entre plataformas gracias al estándar abierto Agent Skills — apunta cualquier cliente compatible a `https://github.com/indranilbanerjee/contentforge/tree/master/skills`.

---

## Actualización

**Claude Code:** los marketplaces de terceros tienen la actualización automática DESACTIVADA por defecto. Actívala una vez: `/plugin` → pestaña **Marketplaces** → `neels-plugins` → **Enable auto-update**. O manualmente: `/plugin marketplace update neels-plugins` y luego `/plugin uninstall` + `/plugin install contentforge@neels-plugins` + `/reload-plugins`.

**Cowork / claude.ai / Claude Desktop:** abre el panel de Plugins de la interfaz → elimina ContentForge → reinstálalo desde el marketplace (la reinstalación descarga la versión más reciente).

**Codex:** `codex plugin update contentforge` · **Cursor:** vuelve a ejecutar `/add-plugin` · **Copilot CLI:** `copilot plugin update contentforge` · **Antigravity:** `agy plugin update contentforge` · **Hermes:** `hermes plugins update contentforge` · **OpenClaw:** `openclaw plugins update contentforge` · **Grok:** `grok plugin update contentforge` · **cargas en claude.ai:** vuelve a descargar la `.skill` de la última versión publicada y súbela de nuevo.

---

## Preguntas frecuentes (lo esencial)

**¿Dónde residen mis datos?** Todo es local: los perfiles de marca y los artefactos de ejecución en `~/.claude-marketing/<brand>/`, los entregables en `~/Documents/ContentForge/`. No se envía nada a ninguna parte, salvo las llamadas al modelo que hace tu propia plataforma.

**¿Necesito conectar MCPs o integraciones?** No. El `.mcp.json` incluido está vacío por diseño — cero servidores de conexión automática. Los conectores son un catálogo opcional (`/contentforge:cf-connect`).

**¿Está preparado para la EU AI Act?** Sí — firma de procedencia de contenido C2PA con la aserción de divulgación de IA del Artículo 50, más una capa de divulgación configurable por marca (ante la duda ⇒ divulgar, a prueba de fallos).

**¿El pipeline completo funciona fuera de Claude Code?** Sí — en plataformas sin despacho de subagentes, el carril de ejecución portátil ejecuta las 10 fases de forma secuencial con todas las puertas intactas. Las cargas de `.skill` en claude.ai son la única excepción: son skills destacadas independientes, no el pipeline.

---

## Sobre el mantenedor

ContentForge está creado y mantenido por **[Indranil "Neel" Banerjee](https://indranil.in)** — constructor y pensador de sistemas con raíces en la seguridad de la información y una segunda etapa en growth marketing, operaciones digitales empresariales y transformación con IA. Forma parte de la suite de tres plugins **Neelverse Marketing Suite**, junto con [Digital Marketing Pro](https://github.com/indranilbanerjee/digital-marketing-pro) y [SocialForge](https://github.com/indranilbanerjee/socialforge).

Si ContentForge le ahorra tiempo a tu equipo, [⭐ dale una estrella al repositorio](https://github.com/indranilbanerjee/contentforge/stargazers) y considera [patrocinar el proyecto ❤](https://github.com/sponsors/indranilbanerjee) — eso mantiene sostenible el ritmo de lanzamientos.

**Licencia:** MIT · **Seguridad:** [avisos privados](https://github.com/indranilbanerjee/contentforge/security/advisories/new) · **Incidencias:** [GitHub Issues](https://github.com/indranilbanerjee/contentforge/issues)
