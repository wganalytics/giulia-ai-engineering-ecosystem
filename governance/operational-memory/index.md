# 📋 Índice - Documentação do Ecossistema

> **Propósito:** Guia de navegação para qualquer agente de IA ou desenvolvedor

---

## 🧠 Leitura Obrigatória (Ordem Sugerida)

Para entender o ecossistema, leia nesta ordem:

1. **[contexto_rlm.md](./contexto_rlm.md)** ← Snapshot rápido (30s)
2. **[diario_de_bordo.md](./diario_de_bordo.md)** ← Estado atual
3. **[status.md](./status.md)** ← Dashboard geral
4. **[manual_do_ecossistema.md](../standards/manual_do_ecossistema.md)** ← Referência completa

---

## 📂 Estrutura de Documentação

```
governance/
│
├── 🏛️ architecture-decisions/    # ADRs, padrões técnicos, contexto RLM local
│   ├── adr-*.md                  # Decisões de arquitetura registradas
│   ├── governance_snapshot_standard.md
│   ├── rag_metrics_standard.md
│   └── jira_docs/
│       └── readme.md
│
├── 📊 operational-memory/        # Acompanhamento de estado e sessões do ecossistema
│   ├── index.md                  # ← Você está aqui
│   ├── status.md                 # Dashboard geral
│   ├── diario_de_bordo.md        # Histórico de sessões
│   ├── lista_de_arquivos.md      # Árvore completa do repositório
│   └── .contexto_navegacao.md    # Índice "Se precisa de X, leia Y"
│
├── 📁 projects/                  # Scaffold vazio — docs (ideia, plan, walkthrough) do
│   └── PRJ-XX_*/                 # próximo projeto criado com o framework
│
├── 📐 standards/                 # Manual do ecossistema, padrões de segurança e engenharia
├── 🧪 tdd/                       # Testes por projeto (TDD)
├── 📝 sdd/                       # Specs de features do próprio ecossistema
└── 📦 snapshots/                 # Scaffold vazio — Governance Snapshots pós-entrega por projeto
```

---

## 🚀 Quick Start para Novos Agentes

```bash
# Listar projetos
python infra/start_project.py --list

# Ver status
python infra/start_project.py --status PRJ-XX

# Criar novo projeto
python infra/start_project.py

# Sincronizar Jira
python infra/core/jira_sync.py

# Validar consistência do ecossistema
python3 ecosystem/automation/validate_ecosystem.py
```

---

## 📚 Referências Técnicas

| Tópico | Arquivo |
|--------|---------|
| Arquitetura e regras completas | `governance/standards/manual_do_ecossistema.md` |
| Padrão Jira | `governance/architecture-decisions/jira_docs/readme.md` |
| Workflow atual | `governance/architecture-decisions/estrutura_e_workflow.md` |
| Scaffold do próximo projeto (vazio) | `governance/projects/PRJ-XX_*/` |
| **Segurança — como verificar e como construir** | **`governance/standards/padrao_seguranca_aplicacoes.md`** |
| Engenharia de software com IA (anti vibe-coding) | `governance/standards/diretrizes_desenvolvimento_ia.md` |

---

## 🔐 Padrão de Segurança — leitura obrigatória antes de mexer em autenticação

`governance/standards/padrao_seguranca_aplicacoes.md` (v1.1) destila 8 vulnerabilidades reais
achadas e corrigidas em um sistema real do ecossistema em jul-ago/2026. Três partes:

- **Como verificar** — 7 critérios de varredura em ordem crescente de alcance. Cada um pegou
  uma classe de defeito que os anteriores deixaram passar. Inclui sessão copiada (Critério 6,
  com receita de teste em `curl`) e prompt injection (Critério 7).
- **Como construir** — 11 padrões por omissão, com o código real que os implementa.
- **Como a verificação mente** — erros de método que quase produziram dano, incluindo
  *"antes de afirmar ou agir sobre produção, leia produção"*.

Fecha com checklist de saída de 18 itens e o **Apêndice B de lacunas abertas**, que é onde
está o que ainda NÃO está coberto.

---

## 🔧 Estrutura do Repositório

```
.
├── 📋 governance/        # ← Documentação (onde você está)
├── 🛠️  ecosystem/        # CLI, Jira, automações, agentes
├── 🛠️  infra/            # Scripts e configurações de infraestrutura
├── 📊 observability/     # Logs, métricas, relatórios, telemetria
├── 🚀 deployment/        # Compose, configs e docker
└── 🔧 scripts/           # Scripts de governança, migração e manutenção
```

Veja [lista_de_arquivos.md](./lista_de_arquivos.md) para a árvore completa e atualizada.
