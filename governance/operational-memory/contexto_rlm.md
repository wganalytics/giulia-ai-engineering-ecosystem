# 🧠 CONTEXTO RLM — Giulia AI Engineering Ecosystem

> **Leia este documento em até 30 segundos. Ele é sua porta de entrada.**
> **Versão:** 8.0 — Lost in Middle Reorder
> **Última Atualização:** 2026-08-05

---

## 🚨 Regras Invioláveis

1. **Nunca commitar `.env`** — use `.env.template`
2. **Nunca criar projeto manualmente** — use `prj_init.py`
3. **Sempre rodar `validate_ecosystem.py`** ao fim de cada sessão
4. **Notas técnicas são obrigatórias** em tasks movidas para `Done` (min. 50 chars)
5. **No Vibe Coding:** Use o Agente de Code Review para garantir Clean Code e SRP.
6. **TDD é Lei:** O `ecosystem/automation/run_tdd_pipeline.sh <PROJETO_ID> <TASK_ID> <SDD_FILE>` (orquestra `cognition_router.py` → `dynamic_escalator.py` → `circuit_breaker.py`) exige que os testes isolados de cada pasta PRJ rodem perfeitamente (Red-Green-Refactor).
7. **Documentação BMAD + SDD:** Toda arquitetura de projeto RAG deve ser orquestrada com Mermaid e Especificações Comportamentais (Guardrails PII/Sandwich). Specs ficam em `docs/specs/` (padrão de mercado) e diagramas em `docs/architecture/`.
8. **Protocolo de Atualização (MANDATÓRIO):** Sempre que concluir uma feature ou modificar a estrutura do repositório, o agente DEVE listar os arquivos alterados e perguntar: *"Deseja que eu atualize o Diário de Bordo/Manual do Ecossistema?"*. Se sim, invocar `atualizar_ecossistema.py`.
9. **Isolamento de VectorDB (Dimensionalidade):** Coleções no ChromaDB devem OBRIGATORIAMENTE possuir o sufixo do provedor (ex: `knowledge_books_openai`, `knowledge_books_gemini`) para evitar falha de 'Dimensionality Mismatch' ao trocar de LLM no `.env`. Nunca faça hardcode de nomes de collections genéricas em retrievers.
10. **Princípio do Foco de Contexto Estrito (Strict Context Focus):** No bootstrap da sessão, alinhe o escopo de trabalho/projeto com o usuário e limite todas as ferramentas de busca e comandos estritamente ao diretório desse projeto, prevenindo buscas globais, otimizando performance e garantindo segurança de dados.
11. **Protocolo GARE-3F (OBRIGATÓRIO):** Para qualquer tarefa de código, siga obrigatoriamente as 3 fases em sequência: (1) LOCALIZAR (mapeie e liste os arquivos afetados no chat antes de editar), (2) IMPLEMENTAR (edite apenas os arquivos mapeados), (3) VALIDAR (execute os testes unitários/integrados do projeto e validate_ecosystem.py antes de marcar como Done). Referência: Agentless (arXiv:2407.01489).
12. **CodeCompass OBRIGATÓRIO em Tarefas G3 (MANDATÓRIO):** Para qualquer refatoração arquitetural, antes de editar o código, chame a tool `get_structural_neighborhood(filepath)` para mapear as dependências e o impacto de modificações nas classes e heranças. Referência: CodeCompass (arXiv:2602.20048).
    *Checklist pré-implementação:*
    - [ ] Chamei `get_structural_neighborhood()` para o arquivo principal?
    - [ ] Identifiquei todos os arquivos que o importam?
    - [ ] Verifiquei heranças e classes filhas?
    - [ ] O escopo de impacto está documentado?
13. **Nunca assumir dado de sistema externo sem validar (MANDATÓRIO):** Antes de criar/modificar qualquer recurso em sistema externo (Jira, GitHub, etc.) a partir de um valor lido de config local (ex: `JIRA_PROJECT_KEY` do `.env`), consulte a API para confirmar o que aquele valor realmente representa e mostre ao usuário antes de agir. Incidente de origem: um épico foi criado no board errado ao assumir que uma chave lida do `.env` raiz era um board genérico — cada PRJ-XX tem seu próprio board dedicado. O wizard `ecosystem/automation/prj_init.py` já valida a chave do épico contra o Jira real antes de prosseguir; siga o mesmo princípio em qualquer ação manual fora do wizard.

---

## ⚡ Comandos Essenciais

```bash
# Validar consistência do ecossistema
python3 ecosystem/automation/validate_ecosystem.py

# Ver board Jira
python3 ecosystem/jira/lifecycle_manager.py status GARE-88

# Iniciar novo projeto (wizard interativo)
python3 ecosystem/automation/prj_init.py
```

---

## 📋 Hierarquia RLM de Leitura

```
 ① ESTE ARQUIVO              ← Você está aqui (30s)
     │
 ② diario_de_bordo.md       ← Última sessão / decisões recentes
     │
 ③ manual_do_ecossistema.md ← Regras completas (sob demanda)
     │
 ④ .contexto_navegacao.md   ← "Onde encontro X?"
     │
 ⑤ governance/projects/PRJ-XX/ ← Docs do projeto ativo
```

> **Regra RLM:** Leia apenas o que for necessário para a tarefa atual. Não carregue tudo.

---

## 📍 Onde Estamos

**Repositório:** showcase público do framework de governança e metodologia de AI Engineering.
**Jira Board:** `GARE` (Giulia AI Engineering Ecosystem)

> Este repositório público contém a documentação, os padrões e a metodologia do ecossistema.
> O código-fonte dos projetos e demais domínios (agents, mcp, data-engineering) vive no monorepo
> privado completo e não é publicado aqui.

---

## 🏗️ O Que É Este Ecossistema

O **Giulia AI Engineering Ecosystem** é um framework completo de AI Engineering — não apenas RAG.

RAG foi a primeira vertical validada. O ecossistema suporta qualquer domínio:
- Agentes autônomos e multiagentes
- Pipelines de dados e inferência
- Sistemas cognitivos e MCP
- Soluções cloud-native

**Camadas deste repositório:**
```
governance/   → Memória operacional, padrões, rastreabilidade
docs/         → Arquitetura, roadmap e padrões de QA do ecossistema
ecosystem/    → CLI, Jira, automações, workflows
infra/        → Scripts e configurações de infraestrutura
observability/→ Logs, métricas, telemetria
deployment/   → Compose, configs, docker
scripts/      → Scripts de governança, migração e manutenção
```

---

## 🗂️ Caminhos Críticos

| O que precisar | Onde encontrar |
|----------------|----------------|
| Histórico completo de sessões | `governance/operational-memory/diario_de_bordo.md` |
| Padrões e workflow completo | `governance/standards/manual_do_ecossistema.md` |
| Status dos projetos ativos | `governance/operational-memory/status.md` |
| **SDDs do próprio ecossistema** | **`governance/sdd/gare-*_sdd.md`** |
| **Testes (TDD) por projeto** | **`governance/tdd/`** |
| Diagrama de arquitetura do ecossistema | `docs/architecture/ecosystem_diagram.svg` |
| Padrões de QA e TDD Orchestrator | `docs/governance/QA_STANDARDS.md` |
| Roadmap do ecossistema | `docs/roadmap/GIULIA_AI_ROADMAP_2026.md` |
| Docs por projeto (ideia, plan, walkthrough) — scaffold vazio até criar um projeto | `governance/projects/PRJ-XX_*/` |
| Scripts Jira (lifecycle, validate) | `ecosystem/jira/` e `ecosystem/automation/` |
| Índice de navegação completo | `governance/operational-memory/.contexto_navegacao.md` |

---

## 🔧 Stack Técnica

- **LLMs (local):** `llama3.2:3b` / `llama3.2:7b` via Ollama (Privacy-first)
- **Embeddings:** `nomic-embed-text` via Ollama
- **Vetorial:** ChromaDB, FAISS
- **Grafo:** Neo4j
- **API:** FastAPI + Streamlit
- **Jira:** Board `GARE` — Lifecycle Kanban automatizado
- **Metodologia:** Clean Architecture + SDD + TDD + RLM
