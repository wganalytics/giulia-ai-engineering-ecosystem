# 🧠 CONTEXTO RLM — Snapshot do Ecossistema (legado)

> **Última atualização:** 2026-05-13 | **Sessão:** #020 | **Agente ativo:** Antigravity (Gemini)

---

## Estado Atual (Em uma olhada)

| Item | Valor |
|------|-------|
| **Próximo foco** | Manutenção & Novas Funcionalidades |
| **Status Geral** | Ver `governance/operational-memory/status.md` |
| **Modelo LLM** | `llama3.2:3b` / `llama3.2:7b` via Ollama |
| **Embedding** | `nomic-embed-text` via Ollama (local) |
| **Board Jira** | Projeto `GARE` (GIULIA AI) — 10 épicos, ~60 tasks |
| **Automação Jira** | Completa (V3 - CLI) ✅ |
| **Logging** | Automático ✅ — Arquivos em infra/logs/ |

---

## O Que Já Existe (Não Refazer!)

### Estrutura de Pastas
```
RAG/
├── governance/                 # ← Documentação centralizada
│   ├── ecossistema/            #   Manual, RLM, Jira Docs
│   ├── acompanhamento/         #   INDEX, STATUS, DIARIO
│   └── projetos/               #   docs por projeto
│
├── infra/                      # ← Scripts e configuração
│   ├── core/                   #   jira_sync, atualizar_tarefa, jira_manager, sync_all_projects
│   ├── lib/                    #   sync_state, logger, file_logger, observatory
│   ├── config/                 #   projetos.yaml, pyproject.toml, .env
│   ├── start_project.py        #   Script de start de projetos
│   ├── atualizar_diario.py     #   Atualiza diario_de_bordo.md automaticamente
│   └── logs/                   #   Arquivos de log rotativos
│
├── DEV/                        # ← Código dos projetos
│   └── PRJ-XX_nome_do_projeto/ # scaffold vazio até criar um projeto
│
├── REGISTRY/projects.json      # ← Estado global dos projetos
├── .github/workflows/          # ← CI/CD
└── ARTIGOS/                    # ← Artigos técnicos
```

---

## Hierarquia de Leitura (OBRIGATÓRIA para qualquer LLM)

Quando você (nova LLM) entrar neste projeto, **leia nesta ordem**:

1. **[contexto_rlm.md](./contexto_rlm.md)** ← Você está aqui (30 segundos)
2. **[diario_de_bordo.md](../acompanhamento/diario_de_bordo.md)** ← Estado das sessões (2 minutos)
3. **[status.md](../acompanhamento/status.md)** ← Dashboard dos projetos (1 minuto)
4. **[manual_do_ecossistema.md](../standards/manual_do_ecossistema.md)** ← Regras completas (sob demanda)

---

## Ferramentas Disponíveis

| Ferramenta | Caminho | O que faz |
|------------|---------|-----------|
| `jira_manager.py` | `infra/core/` | Gerenciamento completo CLI de épicos/tasks |
| `sync_all_projects.py` | `infra/core/` | Sincroniza projetos.yaml → Jira |
| `jira_sync.py` | `infra/core/` | Cria Épicos + Tasks em massa |
| `atualizar_tarefa.py` | `infra/core/` | Move cards Jira + cascata subtasks + auto-promoção |
| `lifecycle_manager.py` | `infra/core/` | **Gerenciador de Lifecycle Kanban** (start-project/task/complete) |
| `git_jira_link.py` | `infra/core/` | Link commits ↔ Jira + valida Conventional Commits |
| `governance_snapshot.py` | `infra/core/` | Salva histórico técnico nos project_context/ |
| `validate_ecosystem.py` | `infra/core/` | Valida consistência (registry ↔ docs ↔ Jira) |
| `rebuild_sync_state.py` | `infra/core/` | Reconstrói .sync_state.json a partir do Jira |
| `fix_duplicate_subtasks.py` | `infra/core/` | Audita/remove subtasks duplicadas |
| `fix_estimates.py` | `infra/core/` | Corrige Original Estimate zerado nos cards |
| `start_project.py` | `infra/` | Cria novo projeto automaticamente |
| `atualizar_diario.py` | `infra/` | Atualiza diario_de_bordo.md automaticamente |
| `logs/` | `infra/logs/` | Arquivos de auditoria |

---

## Como Usar as Ferramentas

```bash
# Listar épicos
python3 infra/core/jira_manager.py --epics

# Listar tasks
python3 infra/core/jira_manager.py --tasks

# Ver detalhes de uma issue
python3 infra/core/jira_manager.py --details GARE-67

# Atualizar campos
python3 infra/core/jira_manager.py --update GARE-70 --summary "Novo título"
python3 infra/core/jira_manager.py --update GARE-70 --priority High
python3 infra/core/jira_manager.py --update GARE-70 --storypoints 3
python3 infra/core/jira_manager.py --update GARE-70 --estimate 6

# Mover status
python3 infra/core/jira_manager.py --move GARE-70 "In Progress"

# Modo interativo
python3 infra/core/jira_manager.py --interactive

# Sincronizar projetos (YAML → Jira)
python3 infra/core/sync_all_projects.py --dry-run  # Simula
python3 infra/core/sync_all_projects.py            # Executa
```

---

## Status do Portfólio no Jira

| Projeto | Épico | Tasks | Status |
|---------|-------|-------|--------|

_Sem dados ainda — populado conforme novos projetos são criados e sincronizados com o Jira._

---

## Decisões Recentes (Últimas sessões)

_Ver `governance/operational-memory/diario_de_bordo.md` para o histórico cronológico de sessões._

---

## Regras Inegociáveis

- 🔒 **Privacy-first:** Core sempre 100% local via Ollama
- 🔒 **Isolamento:** Cada PRJ-XX tem seu próprio venv e .env
- 🔒 **Jira via CLI:** Nunca mover cards manualmente
- 🔒 **Documentar primeiro:** `ideia.md` + `implementation_plan.md` antes de codar
- 🔒 **Atualizar diário:** Toda sessão → atualizar diario_de_bordo.md
- 🔒 **Logging:** Scripts registram execuções automaticamente

---

> **Referência conceitual:** [Vídeo Sandeco — RLM](https://www.youtube.com/watch?v=AALTWpRyDGs) | Paper: MIT CSAIL (arXiv:2512.24601)
>
> **Princípio:** RLM = Não carregar tudo na memória de uma vez, mas navegar sob demanda (analogia com GTA streaming)