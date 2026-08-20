# 📘 Manual do Ecossistema — Giulia AI Engineering Ecosystem

> **Versão:** 9.2 — Atualização Contínua
> **Data de Criação:** 2026-04-16
> **Última Atualização:** 2026-08-17
> **Autor:** Wemerson Souza + Antigravity (IA)

Este documento é a **referência central e replicável** de toda a estrutura de trabalho, convenções de camadas, ferramentas de automação e metodologia de desenvolvimento adotada no ecossistema. Serve como guia para qualquer agente ou desenvolvedor que precise entender as regras do sistema.

---

## 📑 Índice

1. [Visão Geral do Ecossistema](#1-visão-geral-do-ecossistema)
2. [Arquitetura do Monorepo (Mapa Completo)](#2-arquitetura-do-monorepo-mapa-completo)
3. [Convenções de Nomenclatura](#3-convenções-de-nomenclatura)
4. [Documentos Obrigatórios por Projeto](#4-documentos-obrigatórios-por-projeto)
5. [Padrão de Arquitetura Interna (Clean Architecture)](#5-padrão-de-arquitetura-interna-clean-architecture)
6. [Gestão Ágil Automatizada (Agent + Jira)](#6-gestão-ágil-automatizada-agent--jira)
7. [Ferramentas de Automação (Scripts)](#7-ferramentas-de-automação-scripts)
8. [Regras de Segurança e Isolamento](#8-regras-de-segurança-e-isolamento)
9. [Manutenção Preventiva e Design Patterns](#9-manutenção-preventiva-e-design-patterns)
10. [Checklist de Replicação para Novos Projetos](#10-checklist-de-replicação-para-novos-projetos)
11. [Changelog (Histórico de Decisões)](#11-changelog-histórico-de-decisões)
12. [Padrão RLM — Gerenciamento de Contexto entre Agentes](#12-padrão-rlm--gerenciamento-de-contexto-entre-agentes)
13. [Ingestão de Conhecimento (Materiais de Referência)](#13-ingestão-de-conhecimento-materiais-de-referência)
14. [Protocolo de Atualização do Ecossistema](#14-protocolo-de-atualização-do-ecossistema)
15. [Workflow de Desenvolvimento: Protocolo GARE-3F](#15-workflow-de-desenvolvimento-protocolo-gare-3f)

---

## 1. Visão Geral do Ecossistema

O **Giulia AI Engineering Ecosystem** é um framework completo de engenharia para sistemas modernos de IA. Não é apenas um conjunto de projetos RAG — é uma plataforma modular que suporta qualquer domínio de AI Engineering.

### Princípios Fundadores

- **Framework-First:** O ecossistema suporta RAG, Agentes, MCP, Data Engineering e qualquer novo paradigma de IA — RAG foi apenas a primeira vertical validada.
- **Privacy-First / 100% Local:** Todos os projetos de inferência rodam via **Ollama** sem dependência de APIs pagas.
- **Isolamento Total:** Cada projeto é um workspace independente com seu próprio `venv`, `.env` e `requirements.txt`.
- **Automação Ágil:** O Board Jira é gerenciado pelo Agente IA via scripts CLI, sem acesso à interface web.
- **Documentação como Cidadão de Primeira Classe:** Nenhum projeto inicia sem `ideia.md` e `implementation_plan.md`.
- **Governance Native:** Governança não é opcional — faz parte da arquitetura.
- **Portfolio Native:** Projetos nascem preparados para showcase, publicação e GitHub público.
- **Pilares de Arquitetura (BMAD + SDD + TDD):** Uso obrigatório de Spec-Driven Development (SDD), Base Model Architecture Diagrams (BMAD - Mermaid) e Test-Driven Development (TDD) via orquestrador próprio.
- **Segurança (Guardrails):** Projetos que utilizam IA devem sempre considerar implementações PII e arquitetura "Sandwich" para segurança do contexto.

### Domínios de Desenvolvimento

```text
dev/
├── rag/              # Retrieval-Augmented Generation (9 projetos concluídos)
├── agents/           # Agentes autônomos e sistemas multiagentes
├── mcp/              # Model Context Protocol
├── data-engineering/ # Pipelines de dados e processamento
├── experiments/      # Experimentos e protótipos
└── clients/          # Projetos de clientes
```

---

## 2. Arquitetura do Monorepo (Mapa Completo)

```text
giulia-ai-engineering-ecosystem/              # 🏠 Raiz do Monorepo
│
├── 📋 governance/                            # 🏛️ Governance Layer
│   ├── operational-memory/                   #    Memória operacional ativa
│   │   ├── contexto_rlm.md                  #    🧠 Porta de entrada RLM (30s)
│   │   ├── diario_de_bordo.md               #    📓 Registro cronológico de sessões
│   │   ├── status.md                         #    Dashboard do portfólio
│   │   ├── index.md                          #    Índice de navegação
│   │   └── .contexto_navegacao.md            #    🧭 "Se precisa de X, leia Y"
│   ├── projects/                             #    Docs por projeto
│   │   └── PRJ-XX_<NomeProjeto>/
│   │       ├── ideia.md
│   │       ├── prj-xx-spec.md
│   │       ├── PRJ-XX_implementation_plan.md
│   │       └── PRJ-XX_walkthrough.md
│   ├── standards/                            #    ← ESTE DOCUMENTO
│   │   ├── manual_do_ecossistema.md
│   │   ├── ecosystem_master_readme.md
│   │   ├── GUIA_RAPIDO_INICIALIZACAO.md
│   │   └── rag_metrics_standard.md
│   ├── architecture-decisions/               #    ADRs
│   ├── snapshots/                            #    Governance Snapshots pós-entrega
│   ├── sdd/                                  #    Spec-Driven Development
│   ├── tdd/                                  #    Test-Driven Development
│   ├── onboarding/                           #    Guias de onboarding
│   └── traceability/                         #    Rastreabilidade end-to-end
│
├── 💻 dev/                                   # 💻 Runtime Layer
│   └── <dominio>/PRJ-XX_<NomeProjeto>/       #    Workspace isolado por projeto
│       ├── .env                              #    Variáveis locais (NUNCA comitar)
│       ├── .env.template                     #    Template público
│       ├── .gitignore
│       ├── README.md
│       ├── requirements.txt
│       ├── venv/
│       ├── app/
│       ├── assets/
│       ├── docs/
│       ├── frontend/                         #    Interface visual (Streamlit)
│       ├── notebooks/
│       ├── project_context/
│       ├── scripts/
│       ├── src/                              #    Core (API + Engine)
│       │   ├── main.py
│       │   ├── api/
│       │   └── core/
│       └── tests/
│
├── 🔧 ecosystem/                             # 🎯 Ecosystem Layer (CLI + Automações)
│   ├── jira/                                 #    Gestão Jira
│   │   ├── lifecycle_manager.py              #    🔄 Lifecycle Kanban
│   │   ├── atualizar_tarefa.py               #    CLI: mover cards + cascata
│   │   ├── jira_manager.py                   #    CLI completo Jira
│   │   └── jira_sync.py                      #    Criação em massa
│   ├── automation/                           #    Automações gerais
│   │   ├── validate_ecosystem.py             #    ✅ Validação total e Health Score
│   │   ├── start_project.py                  #    🎯 Iniciar novo projeto
│   │   ├── auto_diary.py                     #    📓 Auto-geração do Diário de Bordo
│   │   └── governance_snapshot.py            #    Snapshot pós-entrega
│   ├── bench/                                #    GARE-bench Agent Benchmark
│   │   ├── runner.py                         #    Runner do benchmark
│   │   └── tasks.json                        #    Banco de tarefas de teste
│   ├── cli/                                  #    ACI CLI
│   │   └── gare_cli.py                       #    Interface unificada para agentes
│   ├── agents/                               #    Configurações de agentes IA
│   │   └── workflows/
│   │       └── padrao_desenvolvimento_jira.md
│   ├── standards/                            #    Standards aplicados
│   ├── templates/                            #    Templates replicáveis
│   └── workflows/                            #    Workflows de desenvolvimento
│
├── 📊 observability/                         # 📊 Observability Layer
│   ├── logs/
│   ├── metrics/
│   ├── telemetry/
│   ├── traces/
│   ├── dashboards/
│   ├── reports/
│   └── profiling/
│
├── 🎨 portfolio/                             # 🎨 Portfolio Layer
│   ├── articles/
│   ├── architecture-showcase/
│   ├── engineering-pillars/
│   ├── project-pages/
│   ├── github-public/
│   ├── screenshots/
│   └── assets/
│
├── 📦 shared/                                # 📦 Shared Layer
│   ├── infra/                                #    Scripts de infra reutilizáveis
│   └── articles/                             #    Artigos técnicos
│
├── registry/                                 # 📋 Catálogo de projetos (projects.json)
├── config/                                   # ⚙️ Configurações globais
├── deployment/                               # 🚀 Deploy cloud
├── publishing/                               # 📢 Publicação de conteúdo
├── scripts/                                  # 🛠️ Scripts de migração e setup
├── docs/                                     # 📖 Documentação pública
└── website/                                  # 🌐 Site do ecossistema
```

---

## 3. Convenções de Nomenclatura

### Projetos

- **Formato:** `PRJ-XX_Nome_Do_Projeto` (underscores, nunca espaços)
- **Exemplos:** `prj-xx_nome_do_projeto`, `PRJ-10_Autonomous_Agent`

### Domínios em `dev/`

- `rag/` — todos os projetos RAG
- `agents/` — agentes autônomos e sistemas multiagentes
- `mcp/` — Model Context Protocol
- `data-engineering/` — pipelines e ETL
- `experiments/` — protótipos e PoCs
- `clients/` — projetos de clientes

### Documentos de Governança

| Documento | Local | Propósito |
|-----------|-------|-----------|
| `ideia.md` | `governance/projects/PRJ-XX/` | Visão conceitual e roadmap |
| `prj-xx-spec.md` | `governance/projects/PRJ-XX/` | SDD — requisitos e comportamento |
| `PRJ-XX_implementation_plan.md` | `governance/projects/PRJ-XX/` | Plano técnico detalhado |
| `PRJ-XX_walkthrough.md` | `governance/projects/PRJ-XX/` | Resumo pós-implementação |

### Labels no Jira

| Label | Significado |
|-------|-------------|
| `HUMAN` | Requer decisão ou revisão humana |
| `AGENT-AI` | Agente IA pode executar autonomamente |
| `HUMAN` + `AGENT-AI` | Tarefa colaborativa |

---

## 4. Documentos Obrigatórios por Projeto

Todo `PRJ-XX` **deve** conter os seguintes artefatos **antes de iniciar a codificação:**

### Em `governance/projects/PRJ-XX_NomeProjeto/`

| Documento | Propósito | Quando Criar |
|-----------|-----------|--------------|
| `ideia.md` | Porquê do projeto, público-alvo, diferenciais, visão | **Antes** de qualquer código |
| `prj-xx-spec.md` | SDD detalhando requisitos e comportamento esperado | **Antes** do plano |
| `PRJ-XX_implementation_plan.md` | Plano técnico com arquitetura e verificação | **Antes** de qualquer código |
| `PRJ-XX_walkthrough.md` | Resumo pós-implementação e decisões | **Após** finalizar |

### Em `dev/<dominio>/PRJ-XX_NomeProjeto/`

| Documento | Propósito |
|-----------|-----------|
| `README.md` | Instruções completas de instalação e execução |
| `.env.template` | Template público das variáveis de ambiente |
| `.gitignore` | Proteção de `venv/`, `.env`, `data/*`, `__pycache__/` |
| `requirements.txt` | Dependências Python congeladas |

---

## 5. Padrão de Arquitetura Interna (Clean Architecture)

Todo projeto em `dev/` segue o padrão **Domain-Driven / Separação de Preocupações (SoC)**:

```text
PRJ-XX/
├── app/               # Configuração da aplicação
├── frontend/          # Camada de Apresentação (Streamlit)
├── src/               # Camada de Aplicação e Domínio
│   ├── main.py        #   Ponto de entrada (FastAPI)
│   ├── api/           #   Rotas HTTP e Schemas
│   └── core/          #   Lógica de negócio pura (Engine, LLM)
├── scripts/           # Ferramentas auxiliares de dev
├── tests/             # Suítes TDD
├── notebooks/         # Análises e experimentos Jupyter
├── project_context/   # Contexto operacional do projeto
└── assets/            # Recursos estáticos
```

### Princípios

1. **Frontend nunca importa Core diretamente** — consome via API HTTP
2. **Caminhos dinâmicos** — usar `os.path` (nunca hardcoded)
3. **Dados sujos isolados** — `data/` com `.gitkeep` e exclusão via `.gitignore`
4. **Tests first** — TDD: Red → Green → Refactor

---

## 6. Gestão Ágil Automatizada (Agent + Jira)

### Colunas do Board GARE

```
┌──────────┐    ┌────────────────────┐    ┌─────────────┐    ┌──────┐
│ BACKLOG  │ ──▶│ SELECTED FOR DEV   │ ──▶│ IN PROGRESS │ ──▶│ DONE │
│  (ID:11) │    │       (ID:21)      │    │   (ID:31)   │    │(ID:41│
└──────────┘    └────────────────────┘    └─────────────┘    └──────┘
```

### Fluxo Automático em Cascata (v6.0+)

```
start-project EPIC  →  Épico → In Progress + Start Date
                         └──▶  TODAS Tasks → Selected for Development

start-task TASK     →  Task → In Progress + Start Date
                         └──▶  TODAS Subtasks → Selected for Development

complete CARD       →  Card → Done
                         └──▶  Todos irmãos Done? → Pai → Done (recursivo)
```

### Comandos Padrão (Lifecycle Manager)

```bash
# Iniciar projeto inteiro
python3 ecosystem/jira/lifecycle_manager.py start-project GARE-XX

# Iniciar task (com cascata de subtasks)
python3 ecosystem/jira/atualizar_tarefa.py GARE-XX in_progress

# Concluir com nota técnica (auto-promoção do pai)
python3 ecosystem/jira/atualizar_tarefa.py GARE-XX done --nota "Implementado X..."

# Ver status do projeto
python3 ecosystem/jira/lifecycle_manager.py status GARE-XX
```

> **IMPORTANTE:** A nota técnica é obrigatória para Tasks (mínimo 50 caracteres).

---

## 7. Ferramentas de Automação (Scripts)

### Scripts de Lifecycle e Jira (em `ecosystem/jira/`)

| Script | Função |
|--------|--------|
| `lifecycle_manager.py` | Lifecycle Kanban completo |
| `atualizar_tarefa.py` | Move cards + cascata + auto-promoção |
| `jira_manager.py` | CLI completo de épicos/tasks |
| `jira_sync.py` | Criação em massa (anti-duplicata) |

### Scripts de Automação (em `ecosystem/automation/`)

| Script | Função |
|--------|--------|
| `validate_ecosystem.py` | Valida consistência total e gera o **Ecosystem Health Score (0-100)** |
| `start_project.py` | Cria estrutura de pastas + docs + registry |
| `governance_snapshot.py` | Snapshot pós-entrega por projeto |
| `auto_diary.py` | Auto-gera a entrada no Diário de Bordo a partir do Git log |
| `tdd_orchestrator.py` | (em `scripts/governance/`) Orquestrador central que exige que os testes isolados de cada projeto passem. |
| `runner.py` | Runner do benchmark **GARE-bench** para validar agentes |
| `gare_cli.py` | Interface CLI unificada (**ACI CLI**) para interação com o ecossistema |

### Variáveis de Ambiente Jira (`config/.env`)

```bash
JIRA_DOMAIN=seudominio.atlassian.net
JIRA_EMAIL=seu@email.com
JIRA_TOKEN=seu_token_api_atlassian
JIRA_PROJECT_KEY=GARE
JIRA_START_DATE_FIELD=customfield_10015
JIRA_DEBUG=false
```

---

## 8. Regras de Segurança e Isolamento

### Variáveis de Ambiente

- ❌ **NUNCA** comitar arquivos `.env` no Git
- ✅ **SEMPRE** manter `.env.template` atualizado como referência pública
- Cada projeto tem seu próprio `.env` isolado

### Virtual Environments

- Cada `PRJ-XX` tem seu próprio `venv/` — dependências **nunca se misturam**
- Instalar via `pip install -r requirements.txt` dentro do venv ativado

### Dados Sensíveis

- PDFs e dados do VectorDB ficam em `data/` (excluídos do Git via `.gitignore`)
- Usar `.gitkeep` para manter a estrutura no repositório

### Modelo de Inferência

- Padrão: **Ollama** local (Privacy-first)
- Modelos: `llama3.2:3b` / `llama3.2:7b`
- Embedding: `nomic-embed-text`

### Compliance com LGPD (Privacy By Design)

- Agentes que se conectem a serviços externos **devem** implementar `pii_scrubber.py`
- PII (CPF, E-mails, Telefones, Nomes) devem ser mascarados para `[REDACTED]`
- Testes `test_lgpd_compliance.py` são obrigatórios para produção
- A arquitetura "Sandwich" (Guardrails na entrada e na saída) é padrão do ecossistema.

---

## 9. Regras Invioláveis do Ecossistema

Para manter a sanidade do monorepo, as seguintes regras **nunca** devem ser quebradas por humanos ou agentes:

1. **Nunca commitar `.env`** — use `.env.template`.
2. **Nunca criar projeto manualmente** — use `start_project.py`.
3. **Sempre rodar `validate_ecosystem.py`** ao fim de cada sessão.
4. **Notas técnicas são obrigatórias** em tasks movidas para `Done` (min. 50 chars).
5. **No Vibe Coding:** Use o Agente de Code Review para garantir Clean Code e SRP.
6. **TDD é Lei:** O `tdd_orchestrator.py` exige que os testes isolados de cada pasta PRJ rodem perfeitamente (Red-Green-Refactor). Testes formais devem ser registrados no `governance/tdd/tdd_registry.md`.
7. **Documentação BMAD + SDD:** Toda arquitetura de projeto RAG deve ser orquestrada com Mermaid (BMAD) e Especificações Comportamentais (Guardrails PII/Sandwich). Specs ficam em `docs/specs/` e diagramas visuais em `docs/architecture/`.
8. **Isolamento de VectorDB (Dimensionalidade):** Coleções no ChromaDB devem OBRIGATORIAMENTE possuir o sufixo do provedor lido no `.env` (ex: `knowledge_books_openai`, `knowledge_books_gemini`). Isso previne falhas de 'Dimensionality Mismatch' caso a LLM seja alterada. Nunca faça hardcode do nome genérico da collection em sistemas de Retrieval.
9. **Princípio do Foco de Contexto Estrito (Strict Context Focus):** No início de cada sessão (chat), o agente de IA deve OBRIGATORIAMENTE alinhar com o usuário qual projeto/cliente será o foco do trabalho. Uma vez definido, toda e qualquer busca (`grep_search`, `list_dir`), execução de testes ou análise de código deve ser estritamente limitada à pasta desse projeto (ex: `dev/<cliente>/PRJ-XX_<projeto>/`), sendo proibido varrer pastas de projetos ou clientes não relacionados de modo a otimizar performance, evitar desperdício de tokens e garantir a segurança do contexto contra vazamento de informações.

---

## 10. Manutenção Preventiva e Design Patterns

### Padrão Strategy (Estratégia de Roteamento e LLM)

**Strategy** para desacoplar a lógica central do modelo subjacente — permite trocar LLM ou estratégia de recuperação em runtime sem alterar a regra de negócio.

*Onde aplicar:* Roteadores de pesquisa adaptativa, seleção dinâmica de Prompts, injeção de dependências de LLMs.

### Padrão Observer (Monitoramento e Telemetria)

**Observer** para garantir observabilidade total sem poluir o núcleo. O orchestrator age como *Subject* e ferramentas analíticas como *Observers*.

*Onde aplicar:* Atualização em tempo real do Thought Trace, telemetria, acionamento de guardrails (CRAG).

---

## 10. Checklist de Replicação para Novos Projetos

### Fase 1 — Planejamento

- [ ] Criar pasta `governance/projects/PRJ-XX_NomeProjeto/`
- [ ] Escrever `ideia.md` (Visão, Público-alvo, Diferenciais)
- [ ] Escrever `prj-xx-spec.md` (SDD — requisitos e comportamento)
- [ ] Escrever `PRJ-XX_implementation_plan.md`
- [ ] Criar Épico + Tasks no Jira via `ecosystem/jira/jira_sync.py`
- [ ] Adicionar entrada ao `registry/projects.json`

### Fase 2 — Setup Técnico

- [ ] Criar pasta `dev/<dominio>/PRJ-XX_NomeProjeto/`
- [ ] Criar `venv` isolado: `python3 -m venv venv`
- [ ] Copiar `.env.template` e preencher
- [ ] Criar `.gitignore`, `requirements.txt`
- [ ] Montar estrutura: `src/`, `frontend/`, `scripts/`, `tests/`, `app/`

### Fase 3 — Desenvolvimento

- [ ] **Iniciar o projeto:** `python3 ecosystem/jira/lifecycle_manager.py start-project GARE-XX`
- [ ] Para cada task, mover para `in_progress` (com cascata de subtasks)
- [ ] Desenvolver código seguindo Clean Architecture + TDD
- [ ] Mover task para `done` com nota técnica (auto-promoção do pai)

### Fase 4 — Encerramento

- [ ] Executar snapshot: `python3 ecosystem/automation/governance_snapshot.py PRJ-XX`
- [ ] Escrever `PRJ-XX_walkthrough.md`
- [ ] Atualizar `README.md` do projeto
- [ ] Escrever artigo em `portfolio/articles/`
- [ ] **Validar:** `python3 ecosystem/automation/validate_ecosystem.py` → EXIT 0
- [ ] Commit semântico + push

---

## 11. Changelog (Histórico de Decisões)

> Toda nova alteração de padrão deve ser adicionada como novo apêndice abaixo.
> Após qualquer decisão registrada aqui, execute `python3 ecosystem/automation/atualizar_ecossistema.py` para propagar a mudança.

### v1.0 → v6.1 — 2026-04-08 a 2026-05-11 — Fundação e Evolução do Ecossistema RAG

Versões 1.0 a 6.1 documentadas em detalhes no `governance/operational-memory/diario_de_bordo.md` (Sessões #001 a #020).

Decisões principais acumuladas:
- Estrutura de pastas modular (`DEV/`, `planning_docs/`, `infra/`, `REGISTRY/`)
- Clean Architecture padrão para todos os projetos
- Automação Jira via CLI (lifecycle_manager, atualizar_tarefa)
- Padrão SDD (Spec-Driven Development)
- Padrão RLM (Recursive Language Model) para gerenciamento de contexto
- Governance Snapshot obrigatório no encerramento
- validate_ecosystem.py como validador de integridade
- 9 projetos RAG concluídos com TDD e Deploy Cloud

---

### v7.0 — 2026-05-21 — Migração para Monorepo e Expansão do Escopo

- **Decisão:** Migração completa para monorepo em `<repo-root>/`
- **Decisão:** Renomeação do ecossistema de "RAG Ecosystem" para **"AI Engineering Ecosystem"** — escopo expandido para qualquer domínio de IA.
- **Decisão:** Nova estrutura em camadas: Runtime (`dev/`), Governance (`governance/`), Observability, Portfolio, Ecosystem, Shared.
- **Decisão:** `dev/` organizado por domínio: `rag/`, `agents/`, `mcp/`, `data-engineering/`, `experiments/`, `clients/`.
- **Decisão:** `planning_docs/` → `governance/` (com subpastas: `projects/`, `standards/`, `operational-memory/`, `architecture-decisions/`, etc.)
- **Decisão:** `infra/` → `ecosystem/` (jira/, automation/, agents/, workflows/)
- **Decisão:** `README.md` raiz atualizado com visão completa do monorepo.
- **Decisão:** `contexto_rlm.md` recriado para refletir a nova estrutura.
- **Motivação:** O ecossistema transcendeu RAG. A nova estrutura suporta crescimento para múltiplos domínios de AI Engineering sem perder a organização e rastreabilidade conquistadas.

---

### v7.1 — 2026-05-24 — Centralização de Specs (docs/specs/)

- **Decisão:** `docs/specs/` definido como local canônico para todos os arquivos SDD (`PRJ-XX_*_SDD.md`).
- **Decisão:** `governance/sdd/` arquivado — conteúdo migrado para `docs/specs/`.
- **Decisão:** `contexto_rlm.md`, `AI_BOOTSTRAP.md` e `.contexto_navegacao.md` atualizados para apontar para `docs/specs/`.
- **Decisão:** SDDs dos PRJ-02 ao PRJ-09 gerados programaticamente com base na lógica dos motores e requisitos arquiteturais.
- **Decisão:** `docs/architecture/` mantido exclusivamente para diagramas visuais (Mermaid, PNGs) — separação entre design visual e especificação técnica.
- **Motivação:** Alinhamento com padrões de mercado (docs-as-code). Eliminar ambiguidade sobre onde encontrar especificações de projetos.

---

### v8.0 — 2026-05-25 — Protocolo de Atualização Contínua do Ecossistema

- **Decisão:** Criado `ecosystem/automation/atualizar_ecossistema.py` — script unificado que, após qualquer ação no ecossistema, pergunta interativamente se o usuário deseja registrar a mudança.
- **Decisão:** O script suporta dois modos: (1) registro no **Diário de Bordo** de toda feature entregue; (2) atualização do **Manual** com nova entrada no Changelog.
- **Decisão:** O **Diário de Bordo** passa a ser o único arquivo canônico em `governance/operational-memory/diario_de_bordo.md`. O arquivo duplicado em `shared/planning_docs/` foi arquivado.
- **Decisão:** Todo registro no Diário de Bordo deve conter: número da sessão, data, agente, foco, lista de features entregues e próximos passos.
- **Decisão:** O script `atualizar_ecossistema.py` pode ser invocado standalone ou como hook ao final de qualquer outro script de automação.
- **Motivação:** Garantir que nenhuma decisão ou feature entregue fique sem registro. O ecossistema deve ser auto-documentável por padrão.

---

### v8.1 — 2026-05-25 — Formalização da Ingestão de Conhecimento (Livros/Materiais)

- **Decisão:** Documentada formalmente a estrutura de ingestão de conhecimento na Seção 13 do Manual.
- **Decisão:** Todo novo material de referência (livros, PDFs) deve ser depositado na `inbox` padrão do ecossistema: `shared/source_documents/books/inbox/`.
- **Decisão:** O processamento desse material deve ocorrer exclusivamente via a skill `book-knowledge-ingestor` (invocando o pipeline `ingest_books.py`), garantindo que o conhecimento vá para o banco vetorial local (`knowledge_books`) e o catálogo `index.md` seja atualizado.
- **Motivação:** Evitar que agentes criem novas pastas ad hoc para materiais de referência e garantir que o conhecimento fique disponível globalmente para futuras sessões.

---

### v8.2 — 2026-05-26 — Sincronização de Pilares TDD, SDD e BMAD

- **Decisão:** Adição explícita da Seção 9 ("Regras Invioláveis do Ecossistema") ao `manual_do_ecossistema.md`, espelhando a consistência do `contexto_rlm.md`.
- **Decisão:** Inclusão formal dos pilares **BMAD** (Base Model Architecture Diagrams), **SDD** (Spec-Driven Development) e **TDD** (Test-Driven Development) nos princípios centrais do ecossistema.
- **Decisão:** Documentada a existência do `tdd_orchestrator.py` e do `governance/tdd/tdd_registry.md` como ferramentas definitivas de validação técnica, vetando o "Vibe Coding".
- **Decisão:** Adicionado o requisito de arquitetura "Sandwich" (Guardrails PII/Entrada e Saída) como obrigatório para sistemas LLM.
- **Decisão:** Adicionada a regra de isolamento de coleções do VectorDB via sufixo de provedor para prevenir erros de dimensionalidade.
- **Motivação:** Refletir no Manual principal toda a maturidade de engenharia e segurança construída nas iterações mais recentes.

---

### v8.3 — 2026-05-26 — Governança RAG, Protocolo Universal de Agentes e Refatoração de Ingestão

- **Decisão:** Todos os agentes de IA agora são obrigados a listar arquivos modificados e rodar o script de atualização no fim de cada feature.
- **Decisão:** Coleções do ChromaDB devem conter o sufixo do provedor (ex: knowledge_books_openai) para prevenir falha de dimensionalidade.

---

### v8.4 — 2026-05-26 — Consolidação Máxima do Protocolo de Atualização

- **Decisão:** O README.md agora possui o guardrail de atualização hardcoded logo na primeira instrução de AI para garantir que agentes desatentos (que não leem o CONTEXTO_RLM) também cumpram o protocolo.

---

### v8.5 — 2026-05-26 — Consolidação de Governança Monorepo

- **Decisão:** Criação e padronização de validate_ecosystem.py, governance_snapshot.py e start_project.py em ecosystem/automation/
- **Decisão:** Criação de lifecycle_manager.py, jira_sync.py e atualizar_tarefa.py em ecosystem/jira/
- **Decisão:** Harmonização e teste de toda a governança e caminhos do monorepo

---

### v8.6 — 2026-05-27 — Estabilização e Otimização do Book Knowledge Ingestor

- **Decisão:** Adotar gemini-flash-latest como modelo estável padrão do Gemini para pipelines de ingestão de alto volume sob quotas do Free Tier.

---

### v8.7 — 2026-05-27 — Diretrizes de Engenharia de Software para Agentes de IA

- **Decisão:** Adotar o AI Engineering Paradigm como barreira obrigatória contra o Vibe Coding (SDD + TDD).

---

### v8.8 — 2026-06-11 — Princípio do Foco de Contexto Estrito (Strict Context Focus)

- **Decisão:** Obrigatoriedade de alinhamento e definição do escopo de trabalho/projeto no bootstrap da sessão.
- **Decisão:** Limitar escopos de busca e comandos de terminal exclusivamente ao subdiretório do projeto foco definido, bloqueando varreduras de árvore global.
- **Motivação:** Otimização do consumo de tokens, melhoria da velocidade das ferramentas de pesquisa e prevenção de vazamento de informações contextuais entre múltiplos projetos de clientes.

---

### v8.9 — 2026-06-15 — Padrão LGPD de Ciclo de Vida de Dados e Anonimização de Logs

- **Decisão:** Adotar a especificação de ciclo de vida de dados LGPD como padrão de privacidade para sistemas SaaS.
- **Decisão:** Implementação de rotinas transacionais sequenciais de exclusão em cascata (evidências -> respostas -> capítulos -> auditorias -> empresas -> usuários -> tenant) para evitar violações de chaves estrangeiras.
- **Decisão:** Obrigatoriedade de anonimização criptográfica de dados pessoais em tabelas de logs históricos (`audit_log`) ao invés de deleção física, preservando conformidade legal (Marco Civil da Internet Art. 15).
- **Motivação:** Adequação regulatória rígida à LGPD (Art. 16/18) e proteção jurídica contra eliminação inapropriada de logs de acesso e segurança.

---

### v8.10 — 2026-06-15 — Descentralização do Jira e Histórico

- **Decisão:** O estado de sincronia e integrações com o Jira agora pertencem exclusivamente à pasta do projeto (projeto.yaml e .sync_state.json), abandonando o registry central.

---

### v8.11 — 2026-07-24 — Padrão de resolução de tenant em rotas com JWT manual (fora do tenantMw padrão)

- **Decisão:** Rotas que fazem jwt.verify manualmente (bypass do fluxo authMw + tenantMw padrão, ex: endpoints públicos que aceitam token OU JWT) devem replicar a lógica de resolução de tenant do middleware/tenant.js, não reimplementar do zero — usar só o tenant_id nativo do usuário direto do banco quebra silenciosamente pra staff GIULIA AI (admin_master/admin_junior/suporte), cujo tenant_id é NULL por natureza (navegam em todos os tenants via seletor Tenant Ativo / header x-tenant-id)

---

### v8.12 — 2026-07-31 — Padrão porta+adapters para integrações e separação de roles de banco

- **Decisão:** Padrão porta+adapters (Branch by Abstraction) como forma canônica de desacoplar integração externa: porta.js expõe o contrato, adapters/legado mantém o comportamento atual, adapters/proprio traz a implementação nativa, seleção por variável de ambiente com default sempre no legado. Aplicado em integrações externas do ecossistema.
- **Decisão:** Migração de integração acontece capability por capability, nunca big bang: nenhuma rota de produção é alterada até a capability nativa ser validada individualmente contra infraestrutura real (LLM real, SMTP real), com decisão de cutover explícita e separada.
- **Decisão:** Separação obrigatória de roles de banco em projetos novos: um role dono das tabelas para migrations (CREATE/ALTER/DROP) e um role restrito sem SUPERUSER/BYPASSRLS para o runtime da aplicação. Sem isso, qualquer ROW LEVEL SECURITY é decorativa — o BYPASSRLS ignora a policy silenciosamente.
- **Decisão:** ALTER DEFAULT PRIVILEGES no role de migração é parte do provisionamento, não opcional: garante que tabelas criadas por migrations futuras já nasçam com grant para o role restrito, sem depender de alguém lembrar de rodar GRANT manual.
- **Decisão:** Revogação de JWT por versão de sessão como padrão mínimo: coluna sessao_versao no usuário, incluída no token e revalidada na mesma query que o middleware de auth já faz. Logout, troca de senha e recuperação incrementam a versão e invalidam todos os tokens antigos na hora.
- **Decisão:** Storage parametrizável de prompt de IA e de template de e-mail seguindo o mesmo desenho: ponto de uso + versão imutável após publicação + vigência com cascata tenant sobre global. Prompt de IA exige harness de teste aprovado antes de publicar; template de e-mail não (HTML é inspecionável visualmente).
- **Decisão:** SPEC as-built como artefato de replicação entre projetos do ecossistema: documenta o que existe hoje (não o ideal), inclui explicitamente os gotchas e dívidas conhecidas, e propõe a extração como módulo desacoplado.

---

### v9.0 — 2026-08-05 — Automatização de Governança, Benchmarking e Health Score (GARE-145 a GARE-153)

- **Decisão:** Limpeza estrutural da raiz do monorepo removendo arquivos órfãos e organizando workspaces.
- **Decisão:** Institucionalização de **Architecture Decision Records (ADRs)** sob `governance/architecture-decisions/` com índice README e template formal.
- **Decisão:** Automatização do Diário de Bordo via script `auto_diary.py` e hook de Git `post-commit`, eliminando a fricção de preenchimento manual.
- **Decisão:** Implementação do benchmark **GARE-bench** (`ecosystem/bench/`) composto por banco de dados `tasks.json` e runner.
- **Decisão:** Criação da interface CLI para agentes (**ACI CLI** em `ecosystem/cli/gare_cli.py`) suportando comandos de listagem de projetos, testes e consultas do Jira.
- **Decisão:** DDL de esquema unificado de grafo para o Neo4j em `shared/schemas/graph_schema.cypher`.
- **Decisão:** Adotado o **Ecosystem Health Score (0-100)** no script de validação (`validate_ecosystem.py`) persistindo logs históricos em JSON.
- **Motivação:** Escalar a governança do monorepo de forma objetiva e orientada a métricas (Green TDD), oferecendo interfaces e automações dedicadas a agentes inteligentes.

---

### v9.1 — 2026-08-06 — CodeCompass e Regra 12 de Dependências

- **Decisão:** Implementada Regra 12 (checklist obrigatório do CodeCompass em contexto_rlm.md para tarefas G3)
- **Decisão:** Implementado o ASTExtractor de dependências no Neo4j com suporte a imports herança e instanciação
- **Decisão:** Implementado o CodeCompassMCPServer com as ferramentas de grafo get_structural_neighborhood e find_files_by_class
- **Decisão:** Adicionado o rastreamento do Veto Protocol no telemetry_aggregator.py e dashboard

---

### v9.2 — 2026-08-17 — Modo Retrofit no prj_init.py

- **Decisão:** prj_init.py ganhou modo (R)etrofit: estrutura projetos que já têm código (specs/, CLAUDE.md, projetos.yaml, .agents/skills) sem sobrescrever arquivos existentes e sem criar pastas src/tests/data genéricas quando o projeto já tem layout próprio

---

## 12. Padrão RLM — Gerenciamento de Contexto entre Agentes

O ecossistema adota o padrão **RLM (Recursive Language Model)** para gerenciar a continuidade entre sessões e entre diferentes agentes de IA.

### Hierarquia de Leitura (Obrigatória para todo Agente)

```
 ① contexto_rlm.md                    ← "Onde estou?" (30 segundos)
     │
 ② diario_de_bordo.md                 ← "O que já fizemos?" (última sessão)
     │
 ③ manual_do_ecossistema.md           ← "Quais são as regras?" (sob demanda)
     │
 ④ .contexto_navegacao.md             ← "Onde encontro X?" (referência rápida)
     │
 ⑤ governance/projects/PRJ-XX/        ← ideia.md + implementation_plan.md
```

### Princípios RLM Aplicados

1. **Contexto como Ambiente Externo:** Os docs de `governance/` são o "mundo externo" — a LLM não precisa memorizar tudo, basta saber onde buscar.
2. **Inspeção Sob Demanda:** Leia apenas o que é relevante para a tarefa atual.
3. **Persistência entre Sessões:** O `diario_de_bordo.md` garante que nenhuma decisão se perca.
4. **Snapshot Express:** O `contexto_rlm.md` é o "metadata resumo" — atualizado a cada sessão significativa.

### Documentos do Sistema RLM

| Documento | Papel | Atualização |
|-----------|-------|-------------|
| `contexto_rlm.md` | Snapshot / porta de entrada | Toda sessão significativa |
| `diario_de_bordo.md` | Histórico e handoff | Toda sessão |
| `manual_do_ecossistema.md` | Regras do sistema | Quando padrões mudam |
| `.contexto_navegacao.md` | Índice de navegação | Quando novos docs surgem |
| `governance/projects/PRJ-XX/` | Chunks de domínio específico | Por projeto |

---

## 13. Ingestão de Conhecimento (Materiais de Referência)

Sempre que um novo livro, artigo ou documentação densa precisar ser utilizado como material de apoio (ex: para uma nova série de projetos), o processo de ingestão deve seguir o fluxo padrão do ecossistema, garantindo que o conhecimento fique acessível via RAG.

### Regras de Ingestão

1. **Local de Drop (Inbox):** 
   - Os arquivos brutos (PDF, EPUB) **devem** ser depositados em: `shared/source_documents/books/inbox/`.
   - **PROIBIDO** criar pastas ad hoc como `governance/reference-materials/` ou deixá-los soltos.

2. **Processamento (Skill RAG):**
   - O material deve ser processado pela skill global **`book-knowledge-ingestor`** (ou executando diretamente `python scripts/ingest_books.py --mode pending`).
   - O pipeline automático irá:
     - Extrair o texto.
     - Selecionar a LLM ideal no Ollama local.
     - Gerar resumos estruturados em `shared/source_documents/books/insights/`.
     - Criar embeddings e salvar no ChromaDB (collection: `knowledge_books`).
     - Atualizar o catálogo central: `shared/source_documents/books/index.md`.
     - Mover o arquivo para `shared/source_documents/books/processed/`.

3. **Consumo de Conhecimento:**
   - Uma vez ingerido, qualquer agente operando no monorepo pode consultar o `index.md` e buscar o conhecimento no banco vetorial para conceber novos projetos, especificações (SDDs) ou implementações técnicas.

---

## 14. Protocolo de Atualização do Ecossistema

Toda ação que modifique padrões, adicione features, ou altere a estrutura do ecossistema deve seguir este protocolo:

### Gatilhos de Atualização

| Evento | Diário de Bordo | Manual (Changelog) |
|--------|----------------|--------------------|
| Feature entregue / projeto concluído | ✅ Obrigatório | Se criar novo padrão |
| Novo padrão definido | ✅ Obrigatório | ✅ Obrigatório |
| Mudança de estrutura de pastas | ✅ Obrigatório | ✅ Obrigatório |
| Correção de bug / manutenção | ✅ Recomendado | Não necessário |
| Sessão de pesquisa / exploração | ✅ Recomendado | Não necessário |

### Como Executar

```bash
# Ao fim de qualquer sessão significativa:
python3 ecosystem/automation/atualizar_ecossistema.py

# Com feature pré-preenchida (modo não-interativo parcial):
python3 ecosystem/automation/atualizar_ecossistema.py --feature "Implementado X" --sessao 023
```

### O Que o Script Faz

1. **Pergunta:** "Deseja registrar uma entrada no Diário de Bordo? (s/n)"
   - Se `s`: solicita foco, features entregues e próximos passos → grava nova sessão
2. **Pergunta:** "Alguma mudança de padrão para registrar no Manual? (s/n)"
   - Se `s`: solicita versão, título e descrição → grava nova entrada no Changelog
3. Exibe resumo do que foi registrado e sugere commit semântico

> **📌 REGRA DE OURO:** Toda vez que um novo padrão for definido, **DEVE** ser adicionado como nova entrada no Changelog (Seção 11) deste documento, com version incremental, data e descrição da decisão.

---

## 15. Workflow de Desenvolvimento: Protocolo GARE-3F

O **Protocolo GARE-3F** (3 Fases) é a metodologia operacional padrão para qualquer tarefa de código (criação, refatoração ou correção de bugs) executada por agentes de IA ou engenheiros no ecossistema. Ele é projetado para evitar modificações impulsivas ("Vibe Coding") e garantir 100% de consistência.

Referência Científica: *Agentless* (arXiv:2407.01489) — demostrou que uma sequência linear simples de 3 fases supera sistemas complexos de agentes autônomos.

```text
  ┌───────────────────────────────────────────────────────────┐
  │                 Workflow GARE-3F                          │
  │                                                           │
  │  [FASE 1: LOCALIZAR] ──► [FASE 2: IMPLEMENTAR] ──► [FASE 3: VALIDAR]
  │   - Apenas Leitura        - Edição estrita          - pytest
  │   - Mapear dependências   - SRP / Clean Arch        - validate_ecosystem
  │   - Definir escopo        - Diário de Bordo         - Registrar notas
  └───────────────────────────────────────────────────────────┘
```

### 15.1 Fase 1: Localizar (Read-Only Scope Mappings)

Antes de fazer qualquer alteração ou escrever qualquer linha de código:
1. **Analise o problema:** Leia a issue e analise os requisitos comportamentais.
2. **Navegue no repositório:** Use ferramentas de leitura e a busca do CodeCompass (grafo de dependências) para mapear o arquivo-alvo e seus arquivos conectados.
3. **Declare o escopo:** Declare no chat quais arquivos serão editados.
4. **⚠️ Regra Estrita:** É proibido editar arquivos ou propor substituições durante esta fase. É uma fase exclusivamente analítica e de leitura.

### 15.2 Fase 2: Implementar (Controlled Execution)

Após obter a confirmação do escopo ou mapeá-lo completamente:
1. **Foco estrito:** Execute as alterações de código exclusivamente nos arquivos listados na Fase 1.
2. **Clean Architectures:** Respeite os padrões de design e convenções de nomenclatura da Seção 3.
3. **No Vibe Coding:** Aplique o Test-Driven Development (TDD) e use o Code Review Agent para validar a qualidade de código proposta antes do deploy.

### 15.3 Fase 3: Validar (Post-Implementation Verification)

Toda alteração de código deve ser rigorosamente testada antes de marcar a issue como Done no Jira:
1. **Suíte de Testes:** Execute o pytest correspondente ao projeto. Ex: `pytest dev/<dominio>/PRJ-XX/tests/`.
2. **Consistência Geral:** Execute `python3 ecosystem/automation/validate_ecosystem.py` na raiz para validar a consistência do ecossistema.
3. **Mapeamento de Resultados:** Se algum teste falhar, retorne à Fase 2 (Implementar).
4. **Fechamento:** Mova o card no Jira adicionando as notas técnicas detalhando o que foi alterado e como foi testado (comprovando que os testes passaram).
