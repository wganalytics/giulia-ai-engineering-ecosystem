# GIULIA AI ENGINEERING ECOSYSTEM

> **Versão:** 9.1
> **Última Atualização:** 2026-08-16
> **Autor:** Wemerson Souza

> 🛑 **[AI SYSTEM INSTRUCTION / BOOTSTRAP]:** Se você é uma Inteligência Artificial (Antigravity, Claude Code, Gemini CLI, OpenCode, Codex, Aider, Cursor, etc.) lendo este repositório, PARE AGORA. O seu System Prompt, o estado atual do projeto e as regras do ecossistema (BMAD, SDD, TDD) **NÃO** estão aqui. Vá ler o arquivo `governance/operational-memory/contexto_rlm.md` IMEDIATAMENTE antes de iniciar qualquer interação com o usuário.
> ⚠️ **[UPDATE GUARDRAIL MANDATORY]:** Ao final de qualquer tarefa ou mudança de código, você **DEVE** listar os arquivos alterados e perguntar ao usuário: *"Deseja que eu atualize o Diário de Bordo/Manual com estas alterações?"*. Se o usuário disser sim, invoque `atualizar_ecossistema.py`. Nunca encerre uma sessão silenciosamente após realizar alterações.

---

## Visão Geral

O **Giulia AI Engineering Ecosystem** é um ecossistema modular de engenharia para desenvolvimento de aplicações avançadas de IA Generativa, agentes autônomos, sistemas multiagentes, automações inteligentes, pipelines de IA, arquiteturas cognitivas e soluções baseadas em LLMs.

Embora as primeiras implementações do ecossistema tenham sido centradas em arquiteturas RAG (Retrieval-Augmented Generation), o framework foi evoluído para suportar **qualquer tipo de sistema de AI Engineering moderno**, incluindo:

- agentes autônomos;
- sistemas orientados a ferramentas;
- workflows cognitivos;
- plataformas de automação inteligente;
- aplicações multimodais;
- observabilidade de IA;
- governança de ecossistemas de IA;
- plataformas cloud-native;
- pipelines de inferência e orquestração.

> RAG foi apenas o primeiro domínio utilizado para validar e amadurecer a arquitetura-base do framework.

---

## Arquitetura Geral do Monorepo

```text
giulia-ai-engineering-ecosystem/
│
├── config/           # Configurações globais e variáveis de ambiente
├── deployment/       # Deploy cloud-native (Docker, CI/CD, AWS/GCP)
├── dev/              # Runtime Layer — código-fonte dos projetos
│   ├── agents/       #   Agentes autônomos e sistemas multiagentes
│   ├── clients/      #   Projetos de clientes
│   ├── data-engineering/ # Pipelines de dados
│   ├── experiments/  #   Experimentos e protótipos
│   ├── mcp/          #   Model Context Protocol
│   └── rag/          #   Projetos de Retrieval-Augmented Generation
├── docs/             # Documentação pública e portais
├── ecosystem/        # CLI, automações, Jira, standards, workflows
├── governance/       # Governance Layer — memória e rastreabilidade
├── observability/    # Logs, métricas, telemetria, traces
├── portfolio/        # Portfolio Layer — showcase profissional
├── publishing/       # Publicação e exportação de conteúdo
├── registry/         # Registro centralizado de projetos
├── scripts/          # Scripts de automação e migração
├── shared/           # Componentes compartilhados entre projetos
└── website/          # Site público do ecossistema
```

---

## Camadas do Ecossistema

### 1. Runtime Layer — `dev/`

Projetos de AI Engineering organizados por domínio. A estrutura foi projetada para suportar **múltiplos domínios de IA e automação avançada** — não apenas RAG.

Este repositório contém apenas o framework de governança/metodologia (scaffold, automações, padrões). Projetos concretos construídos com o framework (RAG, MCP, agentes ou qualquer outro domínio) vivem em `dev/<domínio>/PRJ-XX_nome/` e são publicados como repositórios públicos independentes quando concluídos.

**Estrutura padrão de cada projeto:**

```text
PRJ-XX/
├── app/
├── assets/
├── docs/
├── frontend/
├── notebooks/
├── project_context/
├── scripts/
├── src/
├── tests/
├── README.md
└── requirements.txt
```

---

### 2. Governance Layer — `governance/`

Rastreabilidade arquitetural e memória operacional do ecossistema.

```text
governance/
├── architecture-decisions/   # ADRs — Architectural Decision Records
├── onboarding/               # Guias para novos desenvolvedores e agentes
├── operational-memory/       # DIARIO_DE_BORDO, STATUS, CONTEXTO_RLM
├── projects/                 # Scaffold vazio: docs de governança do próximo projeto (ideia, spec, plan)
├── sdd/                      # Spec-Driven Development
├── snapshots/                # Scaffold vazio: Governance Snapshots pós-entrega
├── standards/                # manual_do_ecossistema, padrões técnicos
├── tdd/                      # Test-Driven Development
└── traceability/             # Rastreabilidade end-to-end
```

---

### 3. Observability Layer — `observability/`

Centraliza métricas, traces, telemetria e relatórios técnicos.

```text
observability/
├── dashboards/
├── logs/
├── metrics/
├── profiling/
├── reports/
├── telemetry/
└── traces/
```

---

### 4. Portfolio Layer — `portfolio/`

Publicação técnica e showcase profissional.

```text
portfolio/
├── architecture-showcase/
├── articles/
├── assets/
├── engineering-pillars/
├── github-public/
├── project-pages/
└── screenshots/
```

---

### 5. Ecosystem Layer — `ecosystem/`

CLI, automações, Jira, standards e workflows operacionais.

```text
ecosystem/
├── agents/       # Configurações e workflows de agentes IA
├── automation/   # Scripts de automação Jira, lifecycle e auto-diário
├── bench/        # Banco de dados e runner do GARE-bench
├── cli/          # Interface CLI unificada para agentes (gare_cli.py)
├── github/       # Integração Git + GitHub Actions
├── governance/   # Scripts de governança
├── jira/         # Gestão ágil (lifecycle_manager, atualizar_tarefa, sync)
├── observatory/  # Telemetria GARE Observatory
├── standards/    # Standards aplicados por projeto
├── templates/    # Templates replicáveis
└── workflows/    # Workflows padrão de desenvolvimento
```

---

### 6. Public Export Layer

Cada projeto validado é publicado como repositório público próprio — não um único export, mas um espelho individual por projeto, mantido manualmente. Nunca são levados: `.env`, `project_context/`, `specs/`, `diario_de_bordo.md`, `handoff_trace.jsonl`, `projetos.yaml`, `__pycache__`, `.pytest_cache`, `.DS_Store` — só código, testes, README e o manifesto de dependências travado (`requirements.txt` / `uv.lock`).

---

## Princípios do Framework

| Princípio | Descrição |
|-----------|-----------|
| **Clean Architecture** | Separação estrita de camadas e responsabilidades |
| **Domain Separation** | Cada domínio de IA tem sua própria vertical em `dev/` |
| **Observability First** | Métricas e traces nativos desde o início |
| **Governance Driven** | Governança como parte da arquitetura, não opcional |
| **AI Engineering Lifecycle** | SDD → TDD → Implementação → Snapshot → Deploy |
| **Portfolio-Oriented** | Projetos nascem preparados para showcase profissional |
| **Privacy-First** | Core roda 100% local via Ollama — sem dependência de APIs pagas |

---

## Stack Tecnológico

**Runtime:** Python · LangChain · ChromaDB · Neo4j · FAISS · BM25
**LLMs:** `llama3.2:3b` / `llama3.2:7b` · `nomic-embed-text` — via Ollama (local)
**APIs:** FastAPI · Streamlit
**Gestão:** Jira Cloud (board GARE) · GitHub Actions CI/CD
**Deploy:** Docker · AWS / GCP

---

## Quick Start

```bash
# Ver estado atual do ecossistema
python3 ecosystem/jira/lifecycle_manager.py status GARE-88

# Validar consistência total e calcular o Health Score (0-100)
python3 ecosystem/automation/validate_ecosystem.py --quick

# Rodar um projeto criado com o framework (ex: PRJ-XX em dev/<domínio>/)
cd dev/<dominio>/PRJ-XX_nome && uvicorn src.main:app --reload
```

---

## Documentação

| Documento | Camada | Propósito |
|-----------|--------|-----------|
| [contexto_rlm.md](governance/operational-memory/contexto_rlm.md) | Governance | Estado atual (leitura de 30s) — porta de entrada RLM |
| [diario_de_bordo.md](governance/operational-memory/diario_de_bordo.md) | Governance | Histórico cronológico de sessões |
| [status.md](governance/operational-memory/status.md) | Governance | Dashboard de projetos ativos |
| [manual_do_ecossistema.md](governance/standards/manual_do_ecossistema.md) | Standards | Referência completa de padrões e workflow |
| [ecosystem_master_readme.md](governance/standards/ecosystem_master_readme.md) | Standards | Visão arquitetural do monorepo |

---

## Padrão RLM — Leitura para Agentes IA

Todo agente que entrar neste ecossistema deve seguir a hierarquia RLM:

```
 ① governance/operational-memory/contexto_rlm.md     ← "Onde estou?" (30s)
     │
 ② governance/operational-memory/diario_de_bordo.md  ← "O que já fizemos?"
     │
 ③ governance/standards/manual_do_ecossistema.md     ← "Quais são as regras?"
     │
 ④ governance/operational-memory/.contexto_navegacao.md ← "Onde encontro X?"
     │
 ⑤ governance/projects/PRJ-XX/                       ← ideia.md + plan.md
```

> **Regra:** Não leia tudo de uma vez. Comece pelo nível mais compacto e aprofunde sob demanda.

---

## Roadmap Futuro

- [ ] CI/CD pipelines automatizados
- [ ] GitHub Pages com Architecture Portal
- [ ] Observability dashboards interativos
- [ ] Documentação automática via agentes
- [ ] AI Evaluation pipelines
- [ ] Governance automation avançada
- [ ] Developer onboarding automation
- [ ] Novos domínios: `dev/agents/`, `dev/data-engineering/`

---

**Autor:** Wemerson Souza — framework agnóstico de agente de codificação · 2026
