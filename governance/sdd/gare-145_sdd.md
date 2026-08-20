# SDD — GARE-145: GARE-bench (Ecosystem Agent Benchmark)

**Versão:** 1.0  
**Issue Jira:** GARE-145  
**Autor:** Wemerson (RLM Session #009)  
**Data:** 2026-08-05  
**Status:** Draft  
**Fundamentação Científica:** Jimenez et al., 2023 — *"SWE-bench: Can Language Models Resolve Real-World GitHub Issues?"* ([arXiv:2310.06770](https://arxiv.org/abs/2310.06770))

---

## 1. Contexto e Problema

### 1.1 Evidência Empírica (Paper)

O paper *SWE-bench* (Princeton, 2023) estabeleceu o benchmark mais respeitado do mercado para avaliar a capacidade de agentes inteligentes de IA resolverem problemas de engenharia no mundo real.

> *"Resolving issues in SWE-bench frequently requires understanding and coordinating changes across multiple functions, classes, and even files simultaneously... our evaluations show that both state-of-the-art proprietary models and fine-tuned models can resolve only the simplest issues."*

Os autores comprovaram que testes simples de preenchimento de código (como HumanEval) dão uma falsa impressão de capacidade das LLMs. Em cenários reais, a IA precisa navegar em bases complexas, localizar o bug, gerar o patch correto e testá-lo.

### 1.2 Nossa Situação Atual

No monorepo GARE, criamos e evoluímos múltiplos projetos de IA (agentes, pipelines de indexação, CLI, MCP). Contudo:
1. **Falta de Regressão Sistêmica:** Não sabemos se a atualização de uma regra de governança ou o upgrade do modelo local do Ollama (`llama3.2` para um modelo superior) quebrou a capacidade de outros agentes de resolverem tarefas de código no repositório.
2. **Dificuldade de Medição:** Não há dados sobre a taxa de sucesso real de nossos agentes. A avaliação é puramente subjetiva ("Vibe Evaluation").

---

## 2. Objetivo

Implementar a infraestrutura de benchmark interno **GARE-bench** (`ecosystem/bench/`), composta por um catálogo de tarefas reais de teste e um runner automatizado. O GARE-bench medirá quantitativamente a taxa de sucesso dos agentes de IA no monorepo.

---

## 3. Arquitetura da Solução

O GARE-bench será constituído por 3 componentes:

```text
  ┌────────────────────────────────────────────────────────┐
  │                   GARE-BENCH RUNNER                    │
  │                                                        │
  │  ┌──────────────────────┐    ┌────────────────────┐    │
  │  │  Benchmark Database  │───►│  Sandbox Runner    │    │
  │  │  (tasks.json)        │    │  (reset & run)     │    │
  │  └──────────────────────┘    └────────────────────┘    │
  │                                        │               │
  │                                        ▼               │
  │  ┌──────────────────────┐    ┌────────────────────┐    │
  │  │  Verification Engine │◄───│  Telemetry & Repo  │    │
  │  │  (pytest result)     │    │  (score.json)      │    │
  │  └──────────────────────┘    └────────────────────┘    │
  └────────────────────────────────────────────────────────┘
```

### 3.1 Catálogo de Tarefas (`ecosystem/bench/tasks.json`)

Uma coleção de tarefas pré-definidas com escopo real do repositório:

```json
[
  {
    "task_id": "GARE-BENCH-001",
    "description": "Corrigir o timeout HTTP no endpoint de upload de arquivos do PRJ-XX.",
    "project_key": "PRJ-XX",
    "base_commit": "43fe41e",
    "verification_command": "pytest dev/dominio/PRJ-XX/tests/test_upload.py::test_timeout_handling",
    "difficulty": "Easy"
  },
  {
    "task_id": "GARE-BENCH-002",
    "description": "Adicionar suporte a collections baseadas no sufixo de provedor no PRJ-YY.",
    "project_key": "PRJ-YY",
    "base_commit": "2a77b07",
    "verification_command": "pytest dev/dominio/PRJ-YY/tests/test_vector_isolation.py",
    "difficulty": "Medium"
  }
]
```

### 3.2 O Runner (`ecosystem/bench/runner.py`)

O executor do benchmark realizará o seguinte fluxo para cada tarefa selecionada:
1. **Checkout Limpo:** Efetua stash local e faz checkout do repositório no `base_commit` da tarefa.
2. **Execução do Agente:** Dispara o agente de teste dando como prompt a `description` da tarefa.
3. **Validação:** Roda o `verification_command`.
4. **Relatório:** Consolida se o teste passou (Pass) ou falhou (Fail).
5. **Teardown:** Restaura o estado original do repositório (`git reset --hard` e `git stash pop`).

---

## 4. Métricas de Avaliação

O resultado final será salvo em `observability/metrics/bench_results.json` e conterá:
- **Task Success Rate (%):** Razão de tarefas resolvidas com sucesso.
- **Average Cost per Task ($):** Custo de tokens gastos por tarefa.
- **Average Resolution Time (s):** Tempo médio gasto pelo agente por tarefa.

---

## 5. Critérios de Aceite

- [ ] **CA-1:** O arquivo `ecosystem/bench/tasks.json` contém pelo menos 3 tarefas cadastradas representando diferentes projetos e níveis de dificuldade.
- [ ] **CA-2:** Executar `python3 ecosystem/bench/runner.py --task GARE-BENCH-001 --dry-run` simula o fluxo completo sem acionar a IA, validando o setup Git de base.
- [ ] **CA-3:** O executor do benchmark gera o arquivo de telemetria `bench_results.json` ao término da rodada completa.
- [ ] **CA-4:** O teardown funciona perfeitamente, garantindo que o working tree do desenvolvedor retorne ao estado idêntico ao de antes do início do benchmark.

---

## 6. Referências

- Jimenez, C. et al. (2023). *SWE-bench: Can Language Models Resolve Real-World GitHub Issues?* arXiv:2310.06770. [PDF](https://arxiv.org/pdf/2310.06770)
- Issue Jira: [GARE-145](https://wganalytics.atlassian.net/browse/GARE-145)
