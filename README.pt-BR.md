# ContentForge

🌐 **Read this in:** [English](README.md) · [हिन्दी](README.hi.md) · [中文](README.zh-CN.md) · [日本語](README.ja.md) · [한국어](README.ko.md) · [Español](README.es.md) · [Português](README.pt-BR.md) · [العربية](README.ar.md) · [اردو](README.ur.md) · [தமிழ்](README.ta.md) · [বাংলা](README.bn.md) · [Русский](README.ru.md)

> **Sincronizado com o README em inglês v4.1.2 (2026-08-17).** O [README em inglês](README.md) é a fonte da verdade — as notas de versão, o catálogo completo de skills e comandos, a arquitetura, a solução de problemas e o FAQ completo estão lá. Esta tradução cobre tudo o que você precisa para instalar, executar e atualizar o ContentForge.

> **Você precisa entregar 30 artigos neste trimestre que soem humanos, citem fontes reais, se conectem ao seu funil e sobrevivam a um editor que confere tudo. Sua equipe tem três pessoas. Você tem nove semanas. Seu último lote "escrito por IA" foi sinalizado por estatísticas alucinadas — e o lote anterior envelheceu em silêncio sem que ninguém percebesse.**

Execute `/contentforge:create-content` para cada tema. O pipeline de 10 fases produz um `.docx` pronto para publicação, com um humanizador de 43 padrões, um subagente de checagem de fatos, links internos em três categorias e proveniência C2PA para conformidade com o EU AI Act — em 30 a 60 minutos por peça. E então vem a parte que nenhuma ferramenta de resposta única tem: **o loop de ciclo de vida.** Cada peça publicada é medida, auditada quanto ao desgaste e realimenta o próximo calendário e o próximo briefing — por meio de contratos de arquivo duráveis, para que o que o sistema aprende sobre a sua marca sobreviva à sessão em que foi aprendido.

Sistema open-source de produção de conteúdo de nível corporativo — **22 skills · 13 agentes especialistas · 10 gates de qualidade · humanizador anti-detecção de IA com 43 padrões · um auditor de execução que rederiva cada gate antes que uma execução possa se declarar concluída · 28 scripts Python, apenas stdlib**. Criado por [Indranil Banerjee](https://indranil.in) · [LinkedIn](https://www.linkedin.com/in/askneelnow/) · [X](https://x.com/askneelnow).

**Versão 4.1.2** · [Changelog](CHANGELOG.md) · Licença MIT · [Patrocine este projeto ❤](https://github.com/sponsors/indranilbanerjee)

---

## Por que o ContentForge

A maioria das ferramentas de escrita com IA produz um único rascunho, em um único tom, sem gates de qualidade, e esquece a peça no instante em que ela é publicada. O ContentForge resolve isso de ponta a ponta:

| Capacidade | Por que importa |
|---|---|
| **Pipeline de 10 fases com um gate de qualidade após cada fase** | Saídas ruins são capturadas e reexecutadas antes de se propagarem para as fases seguintes |
| **Humanizador anti-detecção de IA com 43 padrões** + meta-passada de autocrítica | O texto soa humano, não IA — medido, não no achismo |
| **Subagente de checagem de fatos** verifica URLs e cruza referências das alegações | As citações funcionam e não são alucinadas — cada estatística remonta a uma entrada do registro verificado |
| **Links internos em três categorias** (temática / comercial / autoridade) | O conteúdo vira funil, não uma página isolada |
| **Saída real em `.docx`** com apêndices de SEO + Qualidade + Produção + Links internos | Seu editor recebe um arquivo Word funcional, não markdown |
| **Um auditor de execução que rederiva cada gate a partir dos artefatos** | "O pipeline diz que terminou" e "os artefatos provam que terminou" nunca podem divergir em silêncio |
| **O loop de ciclo de vida (v4.0)** — auditar → atualizar → medir → planejar, unidos por contratos de arquivo | O conteúdo publicado deixa de ser "publicou, esqueceu": o desgaste é detectado e as atualizações são priorizadas a partir de dados |
| **Assinatura de proveniência de conteúdo C2PA** para conformidade com o Artigo 50 do EU AI Act | Conteúdo longo assistido por IA distribuído em mercados da UE precisa de proveniência a partir de 2 de agosto de 2026 |

## Resultados reais, de uma execução real

Uma execução de validação de ponta a ponta (agosto de 2026, uma marca de teste de preservação digital, um blog de 1.200 palavras sobre a palavra-chave "link rot") — relatada exatamente como aconteceu:

- A fase de checagem de fatos flagrou a fase de pesquisa interpretando mal uma estatística, travou a redação corrigida em um registro verificado e baniu a frase original do rascunho. A correção sobreviveu, palavra por palavra, até o arquivo Word entregue.
- A fase de validação comparou 42 alegações contra o registro: **zero alucinações**.
- O humanizador removeu 20 ocorrências de padrões de IA em 7 categorias (medidas por padrão, registradas com antes/depois de cada edição), mantendo cada fato, citação e posicionamento de SEO estáveis byte a byte.
- A fase de revisão aprovou com **9.0/10 (conceito A)** — qualidade do conteúdo 8.8, integridade das citações 8.9, conformidade com a marca 9.6, SEO 8.6, legibilidade 8.8.
- O auditor de execução rederivou tudo a partir dos artefatos em disco: **14 verificações aprovadas, 0 reprovadas** — só então a execução pôde se declarar concluída.

A questão não é que o pipeline nunca erra — é que os erros dele são capturados pela sua própria maquinaria, com tudo registrado, antes que seu editor sequer veja o arquivo. Veja os artefatos reais (o gráfico de verdade, as edições antes/depois de verdade, o scorecard de verdade) no [README em inglês](README.md#examples).

---

## Início rápido

### 1. Instale

**Claude Code (CLI ou extensão para VS Code/JetBrains):**

```bash
/plugin marketplace add indranilbanerjee/neels-plugins
/plugin install contentforge@neels-plugins
```

**Anthropic Cowork:** abra o painel **Plugins** na interface → Adicionar marketplace → `indranilbanerjee/neels-plugins` → Instalar o ContentForge. (Os comandos de barra `/plugin` não funcionam no Cowork — use o painel da interface.) Depois, execute `/contentforge:cf-cowork-setup` uma única vez para conectar o Google Drive e ter saídas compartilháveis com a equipe.

**OpenAI Codex (CLI + IDE + App):**

```bash
codex plugin marketplace add indranilbanerjee/neels-plugins
codex plugin install contentforge@neels-plugins
```

**Outras plataformas:**

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

**claude.ai (web):** baixe uma skill de destaque a partir da [release mais recente](https://github.com/indranilbanerjee/contentforge/releases/latest) — `cf-brief.skill`, `cf-social-adapt.skill`, `cf-translate.skill`, `cf-video-script.skill` ou `cf-aeo-check.skill` — e, no claude.ai: **Configurações → Capacidades** (ative *Execução de código e criação de arquivos*) → **Personalizar → Skills → Enviar skill**. O pipeline completo exige despacho de subagentes e roda nas plataformas acima; as skills de destaque funcionam de forma autônoma.

**ChatGPT e outros hosts Agent Plugins 1.0:** o ContentForge traz um `plugin.json` na raiz, seguindo o padrão neutro de fornecedor Agent Plugins 1.0 da OpenAI. Em hosts sem despacho de subagentes, a **trilha de execução portátil** roda o pipeline completo sequencialmente em uma única conversa — mesmas fases, mesmos artefatos, mesmos gates de qualidade.

### 2. Configure sua primeira marca

```
/contentforge:brand-setup
```

O agente conduz você pela voz da marca, terminologia, guardrails, regras de citação e a estrutura do seu site para links internos. Quando você informa um site, ele coleta um inventário verificado de páginas em uma única etapa de confirmação.

### 3. Gere conteúdo

```
/contentforge:create-content
```

Escolha o tipo de conteúdo, a marca, o tema, a contagem de palavras e o público. O pipeline executa 10 fases (pesquisa → checagem de fatos → rascunho → visuais → validação → estrutura → SEO → humanização → revisão → saída), aplica um gate de qualidade após cada fase, audita a execução concluída contra os próprios artefatos e grava um `.docx` de verdade.

### 4. Encontre o resultado

```
~/Documents/ContentForge/<brand-slug>/<content-type>/<YYYY-MM>/<slug>.docx
```

O `.docx` inclui o corpo do texto, as referências e quatro apêndices: scorecard de SEO, scorecard de qualidade, detalhes de produção e o mapa de links internos.

### 5. Feche o ciclo

```
/contentforge:cf-aeo-check           # record which pieces AI engines cite
/contentforge:audit-content          # freshness-score the library; findings are RECORDED
/contentforge:cf-calendar --from-audit=latest   # next period: refreshes + gaps, from data
/contentforge:content-refresh        # execute a refresh at the audit's recommended scope
```

Cada comando lê o que o anterior registrou — em uma nova sessão, em outro dia, por outro colega de equipe.

---

## Superfícies suportadas (v4.1.2)

Nove plataformas nativas + uploads no claude.ai + mais de 35 clientes Agent Skills:

| Plataforma | Instalação |
|---|---|
| **Claude Code** (CLI + IDE) | `/plugin install contentforge@neels-plugins` |
| **Anthropic Cowork** | Painel Plugins → Adicionar marketplace → `indranilbanerjee/neels-plugins` |
| **OpenAI Codex** | `codex plugin install contentforge@neels-plugins` |
| **Cursor 2.5+** | `/add-plugin contentforge@https://github.com/indranilbanerjee/contentforge` |
| **GitHub Copilot CLI** | `copilot plugin install contentforge@neels-plugins` |
| **Google Antigravity 2.0** | `agy plugin install https://github.com/indranilbanerjee/contentforge` |
| **Hermes Agent** | `hermes plugins install indranilbanerjee/contentforge` |
| **OpenClaw** | `openclaw plugins install git:github.com/indranilbanerjee/contentforge` |
| **Grok** (xAI Build CLI) | `grok plugin install indranilbanerjee/contentforge` |
| **claude.ai** (web) | Envie uma `.skill` de destaque a partir das [releases](https://github.com/indranilbanerjee/contentforge/releases/latest) |
| **ChatGPT / hosts Agent Plugins 1.0** | Pacote `plugin.json` na raiz + trilha de execução portátil |

Todos os 22 arquivos SKILL.md são portáveis entre plataformas via o padrão aberto Agent Skills — aponte qualquer cliente compatível para `https://github.com/indranilbanerjee/contentforge/tree/master/skills`.

---

## Como atualizar

**Claude Code:** marketplaces de terceiros vêm com a atualização automática DESLIGADA por padrão. Ative uma única vez: `/plugin` → aba **Marketplaces** → `neels-plugins` → **Enable auto-update**. Ou manualmente: `/plugin marketplace update neels-plugins` e depois `/plugin uninstall` + `/plugin install contentforge@neels-plugins` + `/reload-plugins`.

**Cowork / claude.ai / Claude Desktop:** abra o painel Plugins da interface → remova o ContentForge → reinstale a partir do marketplace (a reinstalação baixa a versão mais recente).

**Codex:** `codex plugin update contentforge` · **Cursor:** execute novamente `/add-plugin` · **Copilot CLI:** `copilot plugin update contentforge` · **Antigravity:** `agy plugin update contentforge` · **Hermes:** `hermes plugins update contentforge` · **OpenClaw:** `openclaw plugins update contentforge` · **Grok:** `grok plugin update contentforge` · **uploads no claude.ai:** baixe novamente a `.skill` da release mais recente e reenvie.

---

## FAQ (o essencial)

**Onde ficam meus dados?** Tudo é local: perfis de marca e artefatos de execução em `~/.claude-marketing/<brand>/`, entregáveis em `~/Documents/ContentForge/`. Nada é enviado a lugar nenhum além das chamadas de modelo que a sua própria plataforma faz.

**Preciso conectar MCPs/integrações?** Não. O `.mcp.json` incluído é vazio por design — zero servidores de conexão automática. Os conectores são um catálogo opt-in (`/contentforge:cf-connect`).

**Está pronto para o EU AI Act?** Sim — assinatura de proveniência de conteúdo C2PA com a asserção de divulgação de IA do Artigo 50, mais uma camada de divulgação configurável por marca (fail-safe: em caso de incerteza ⇒ divulgar).

**O pipeline completo roda fora do Claude Code?** Sim — em plataformas sem despacho de subagentes, a trilha de execução portátil roda as 10 fases sequencialmente com todos os gates intactos. Os uploads de `.skill` no claude.ai são a única exceção: são skills de destaque autônomas, não o pipeline.

---

## Sobre o mantenedor

O ContentForge é construído e mantido por **[Indranil "Neel" Banerjee](https://indranil.in)** — um builder e pensador de sistemas com raízes em segurança da informação e um segundo ato em growth marketing, operações digitais corporativas e transformação com IA. Faz parte da suíte de três plugins **Neelverse Marketing Suite**, junto com o [Digital Marketing Pro](https://github.com/indranilbanerjee/digital-marketing-pro) e o [SocialForge](https://github.com/indranilbanerjee/socialforge).

Se o ContentForge economiza tempo da sua equipe, [⭐ dê uma estrela ao repositório](https://github.com/indranilbanerjee/contentforge/stargazers) e considere [patrocinar o projeto ❤](https://github.com/sponsors/indranilbanerjee) — é o que mantém o ritmo de lançamentos sustentável.

**Licença:** MIT · **Segurança:** [avisos privados](https://github.com/indranilbanerjee/contentforge/security/advisories/new) · **Issues:** [GitHub Issues](https://github.com/indranilbanerjee/contentforge/issues)
