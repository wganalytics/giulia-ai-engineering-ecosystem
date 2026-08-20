# 📋 Padrão de Gestão Ágil com Jira — Ecossistema GARE

> **Versão:** 6.1  
> **Data:** 2026-05-11  
> **Propósito:** Documentar o fluxo de ciclo de vida Kanban automatizado (GARE Lifecycle)

---

## 1. Visão Geral

Este documento define o **padrão oficial de gestão de projetos** no ecossistema GARE (GIULIA AI Engineering Ecosystem). O modelo utiliza automação total via scripts Python para gerenciar o board Jira (chave `GARE`), garantindo que o Agente IA mantenha a consistência entre código, documentação e status de tarefas.

### Princípios GARE

| Princípio | Descrição |
|-----------|-----------|
| **Lifecycle Kanban** | Cards movem-se automaticamente entre colunas via gatilhos de script |
| **Cascata Automática** | Iniciar um Épico move todas as Tasks para 'Selected for Development' |
| **Auto-Promoção** | Concluir todas as subtasks de uma task move a Task para 'Done' automaticamente |
| **Idempotência Remota** | Validação JQL impede duplicatas mesmo se o estado local for perdido |
| **Consistência Total** | Validação entre 5 fontes (Jira, Registry, Docs, STATUS, Contexto RLM) |

---

## 2. Arquitetura de Automação

### 2.1 Ferramentas Principais (`infra/core/`)

- **`lifecycle_manager.py`**: O orquestrador central. Comandos: `start-project`, `start-task`, `complete`, `status`.
- **`atualizar_tarefa.py`**: CLI para movimentação individual com suporte a notas técnicas e cascata.
- **`validate_ecosystem.py`**: Auditor de integridade que garante que o Jira bate com a documentação.
- **`jira_sync.py`**: Sincroniza o catálogo `projetos.yaml` com o board remoto (anti-duplicatas).
- **`rebuild_sync_state.py`**: Ferramenta de recuperação que reconstrói o estado local a partir do Jira.

### 2.2 Estrutura de Arquivos

```
infra/
├── core/
│   ├── lifecycle_manager.py    # 🔄 Orquestrador Kanban
│   ├── atualizar_tarefa.py     # ⚡ Movimentação CLI
│   ├── validate_ecosystem.py   # ✅ Auditor de integridade
│   └── jira_sync.py            # 📦 Sincronizador YAML ↔ Jira
├── config/
│   ├── projetos.yaml           # 📌 Catálogo de tarefas (Fonte de Verdade)
│   ├── .sync_state.json        # 🔐 Mapeamento ID local ↔ Jira Key
│   └── .env                    # 🔑 Credenciais JIRA_DOMAIN, JIRA_TOKEN, etc.
└── lib/
    └── sync_state.py           # 🛡️ Lógica de persistência e idempotência
```

---

## 3. Fluxo de Trabalho (Workflow v6.1)

### 3.1 Iniciar um Projeto (Épico)
Ao começar um novo projeto (ex: PRJ-XX):
```bash
python3 infra/core/lifecycle_manager.py start-project GARE-88
```
*   **Ação:** Épico vai para `In Progress` + Start Date definida. Todas as Tasks filhas vão para `Selected for Development`.

### 3.2 Iniciar uma Tarefa (Task)
```bash
python3 infra/core/lifecycle_manager.py start-task GARE-89
```
*   **Ação:** Task vai para `In Progress` + Start Date definida. Todas as Subtasks vão para `Selected for Development`.

### 3.3 Concluir um Card (Subtask/Task)
```bash
python3 infra/core/lifecycle_manager.py complete GARE-89
```
*   **Ação:** Move para `Done`. Verifica recursivamente se o pai (Task ou Épico) pode ser promovido para `Done`.

### 3.4 Visualizar Progresso
```bash
python3 infra/core/lifecycle_manager.py status GARE-88
```
*   **Ação:** Exibe árvore visual do projeto com emojis de status e percentual de conclusão.

---

## 4. Transition IDs (Padrão Board GARE)

Os scripts utilizam IDs fixos para garantir estabilidade:
- `11`: Backlog
- `21`: Selected for Development
- `31`: In Progress
- `41`: Done

---

## 5. Manutenção e Auditoria

Toda sessão deve ser encerrada com a validação de consistência:
```bash
python3 infra/core/validate_ecosystem.py
```
Se o script retornar falha, os metadados do ecossistema devem ser corrigidos antes do push final.

---

> **📌 Regra de Ouro:** O Agente IA deve SEMPRE usar os scripts CLI para gerenciar o board. Nunca arraste cards manualmente na interface do Jira.