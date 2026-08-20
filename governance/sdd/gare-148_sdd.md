# SDD — GARE-148: Protocolo de 3 Fases (Localizar → Implementar → Validar)

**Versão:** 1.0  
**Issue Jira:** GARE-148  
**Autor:** Wemerson (RLM Session #009)  
**Data:** 2026-08-05  
**Status:** Draft  
**Fundamentação Científica:** Xia et al., 2024 — *"Agentless: Demystifying LLM-based Software Engineering Agents"* ([arXiv:2407.01489](https://arxiv.org/abs/2407.01489))

---

## 1. Contexto e Problema

### 1.1 Evidência Empírica (Paper)

O paper *Agentless* (Xia et al., UIUC, 2024) desafiou o consenso da área ao provar que abordagens baseadas em agentes autônomos complexos **não superam métodos lineares simples**:

> *"The simplistic Agentless is able to achieve both the highest performance (32.00%, 96 correct fixes) and low cost ($0.70) compared with all existing open-source software agents."*

O método Agentless emprega **três fases obrigatórias e sequenciais**, sem permitir que a LLM decida seus próximos passos de forma não-estruturada:

1. **Localization** — Identificar todos os arquivos e funções que devem ser modificados, usando estrutura de árvore do repositório. Apenas leitura, nenhuma edição.
2. **Repair** — Gerar os patches de código para os locais identificados na Fase 1. A LLM edita apenas o que foi mapeado.
3. **Patch Validation** — Executar testes automatizados sobre os patches gerados. Patches que não passam nos testes são descartados.

### 1.2 Nossa Situação Atual

**Não existe um protocolo padrão de execução de tarefa no ecossistema GARE.**

Atualmente, quando um agente recebe uma task de desenvolvimento:
- Pode começar a editar arquivos diretamente, sem mapear o escopo completo
- Pode tentar corrigir um arquivo sem verificar dependências
- Nunca há uma fase obrigatória de validação pós-implementação
- O resultado é inconsistente e difícil de auditar

Isso viola diretamente o princípio do paper: *"without letting the LLM decide future actions or operate with complex tools."*

---

## 2. Objetivo

Implementar o **Protocolo GARE-3F** (3 Fases) como regra obrigatória do ecossistema, codificado em dois documentos:
1. Uma nova **Regra 11** no `contexto_rlm.md`
2. Uma seção **"Workflow de Desenvolvimento"** no `manual_do_ecossistema.md`

---

## 3. Arquitetura da Solução

### 3.1 O Protocolo GARE-3F

```
┌─────────────────────────────────────────────────────────┐
│               PROTOCOLO GARE-3F                         │
│                                                         │
│  FASE 1 — LOCALIZAR (READ ONLY)                         │
│  ┌─────────────────────────────────────────────────┐   │
│  │ 1. Ler a descrição da task no Jira              │   │
│  │ 2. Mapear arquivos afetados (via CodeCompass    │   │
│  │    quando disponível, ou busca semântica)       │   │
│  │ 3. Listar EXPLICITAMENTE os arquivos que        │   │
│  │    serão modificados                            │   │
│  │ 4. ⚠️ NENHUMA EDIÇÃO NESTA FASE                │   │
│  └─────────────────────────────────────────────────┘   │
│                         ↓                               │
│  FASE 2 — IMPLEMENTAR (WRITE)                           │
│  ┌─────────────────────────────────────────────────┐   │
│  │ 1. Editar APENAS os arquivos da Fase 1          │   │
│  │ 2. Respeitar Clean Architecture + SRP           │   │
│  │ 3. Seguir padrões do manual_do_ecossistema      │   │
│  │ 4. Registrar no Diário de Bordo                 │   │
│  └─────────────────────────────────────────────────┘   │
│                         ↓                               │
│  FASE 3 — VALIDAR (VERIFY)                              │
│  ┌─────────────────────────────────────────────────┐   │
│  │ 1. Executar pytest do projeto                   │   │
│  │ 2. Se testes falharem → voltar à Fase 2         │   │
│  │ 3. Executar validate_ecosystem.py               │   │
│  │ 4. Só mover Jira para Done após verde           │   │
│  └─────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────┘
```

### 3.2 Texto da Regra 11 (a ser inserida no contexto_rlm.md)

```markdown
11. **Protocolo GARE-3F (OBRIGATÓRIO):** Para qualquer tarefa de código, siga 
    obrigatoriamente as 3 fases em sequência:
    - FASE 1 — LOCALIZAR: Mapeie e liste todos os arquivos afetados. Nenhuma 
      edição nesta fase.
    - FASE 2 — IMPLEMENTAR: Edite apenas os arquivos mapeados na Fase 1.
    - FASE 3 — VALIDAR: Execute os testes do projeto. Só conclua após verde.
    Referência: Agentless (arXiv:2407.01489) — 32% de aprovação no SWE-bench 
    com este método simples, superando todos os agentes complexos.
```

### 3.3 Seção do Manual (a ser adicionada ao manual_do_ecossistema.md)

Uma seção dedicada "Workflow de Desenvolvimento: Protocolo GARE-3F" com:
- Diagrama do fluxo
- Exemplos concretos para os tipos de projeto do ecossistema (RAG, MCP, agentes)
- Checklist de validação por tipo de projeto

---

## 4. Critérios de Aceite

- [ ] **CA-1:** Regra 11 inserida no `contexto_rlm.md`, na seção de Regras Invioláveis, com referência ao arXiv:2407.01489.
- [ ] **CA-2:** Seção "Protocolo GARE-3F" adicionada ao `manual_do_ecossistema.md` com diagrama e exemplos.
- [ ] **CA-3:** Em qualquer nova task de código, o agente deve listar os arquivos afetados **antes** de fazer qualquer edição. Verificável via inspeção do log da sessão.
- [ ] **CA-4:** Nenhuma task pode ter status "Done" no Jira sem uma nota técnica de validação (comprovando que testes passaram).

---

## 5. Impacto e Riscos

| Item | Avaliação |
|---|---|
| **Impacto no processo** | Alto — padroniza o comportamento de todos os agentes |
| **Risco de regressão** | Nenhum — apenas adição de documentação e regras |
| **Esforço estimado** | 1 hora (escrita + testes de comportamento do agente) |
| **Dependências** | GARE-146 (deve ser feito após reordenar o CONTEXTO_RLM) |

---

## 6. Métricas de Sucesso

Conforme o paper Agentless estabelece, o sucesso é medido por:
- **Taxa de aprovação em testes pós-implementação** → meta: > 90%
- **Frequência de tarefas que exigem retrabalho** → meta: < 10%
- **Cobertura de mapeamento na Fase 1** → meta: 100% dos arquivos afetados identificados antes da edição

---

## 7. Referências

- Xia, C. S., Deng, Y., Dunn, S., Zhang, L. (2024). *Agentless: Demystifying LLM-based Software Engineering Agents.* arXiv:2407.01489. [PDF](https://arxiv.org/pdf/2407.01489)
- Arquivo alvo 1: `governance/operational-memory/contexto_rlm.md`
- Arquivo alvo 2: `governance/standards/manual_do_ecossistema.md`
- Issue: [GARE-148](https://wganalytics.atlassian.net/browse/GARE-148)
- Dependência: [GARE-146](https://wganalytics.atlassian.net/browse/GARE-146)
