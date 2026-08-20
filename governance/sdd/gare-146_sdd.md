# SDD — GARE-146: Reordenar contexto_rlm.md

**Versão:** 1.0  
**Issue Jira:** GARE-146  
**Autor:** Wemerson (RLM Session #009)  
**Data:** 2026-08-05  
**Status:** Draft  
**Fundamentação Científica:** Liu et al., 2023 — *"Lost in the Middle: How Language Models Use Long Contexts"* ([arXiv:2307.03172](https://arxiv.org/abs/2307.03172))

---

## 1. Contexto e Problema

### 1.1 Evidência Empírica (Paper)

O paper *Lost in the Middle* (Liu et al., Stanford NLP, 2023) demonstrou empiricamente que:

> *"Performance is often highest when relevant information occurs at the beginning or end of the input context, and significantly degrades when models must access relevant information in the middle of long contexts."*

O estudo testou modelos como GPT-3.5-Turbo, Claude 1.3, MPT-30B-Instruct e LongChat-13B em tarefas de Q&A multi-documento e recuperação key-value. O resultado foi consistente em todos: **queda de até 20 pontos percentuais de acurácia** quando a informação crítica estava no meio do contexto.

### 1.2 Nossa Situação Atual

O arquivo `governance/operational-memory/contexto_rlm.md` é o **documento de bootstrap** do ecossistema — lido por agentes no início de cada sessão. Ele contém informações críticas na seguinte ordem **problemática**:

```
Linhas 1-8     → Título e versão (OK)
Linhas 9-15    → Localização do monorepo (OK)
Linhas 17-55   → Descrição do ecossistema e portfólio (MÉDIO)
Linhas 59-72   → Caminhos críticos (IMPORTANTE - mas enterrado)
Linhas 75-84   → Stack técnica (MÉDIO)
Linhas 87-99   → Comandos essenciais (IMPORTANTE - enterrado)
Linhas 102-116 → Hierarquia RLM (IMPORTANTE - enterrado)
Linhas 120-131 → 🚨 REGRAS INVIOLÁVEIS (CRÍTICO - no final!)
```

**As 10 Regras Invioláveis — que definem o comportamento mais importante do agente — estão nas últimas linhas do arquivo.** Conforme demonstrado pelo paper, a LLM degrada drasticamente ao processar informações nessa posição.

---

## 2. Objetivo

Reordenar o `contexto_rlm.md` aplicando o princípio **Primacy-Recency** validado cientificamente:
- Informações **críticas para ação** → topo do arquivo
- Informações **contextuais/auxiliares** → meio
- Informações **de referência** → final

---

## 3. Arquitetura da Solução

### 3.1 Nova Estrutura Proposta

```
[TOPO — PRIMACY ZONE] ← máxima retenção da LLM
├── Título + Versão + Data
├── 🚨 REGRAS INVIOLÁVEIS (10 regras)
├── ⚡ Comandos Essenciais (bash snippets)
└── 📋 Hierarquia RLM (o que ler em seguida)

[MEIO — CONTEXT ZONE] ← zona de degradação
├── 📍 Localização do Monorepo / Board Jira
├── 🏗️ O Que É Este Ecossistema (descrição)
└── 🗂️ Caminhos Críticos (tabela de navegação)

[FINAL — REFERENCE ZONE] ← zona de degradação menor que o meio
├── 📊 Estado Atual do Portfólio
└── 🔧 Stack Técnica
```

### 3.2 Justificativa de Posicionamento

| Seção | Posição Atual | Posição Proposta | Motivo |
|---|---|---|---|
| Regras Invioláveis | Linha 120 (final) | Linha 5 (topo) | Crítico — comportamento do agente |
| Comandos Essenciais | Linha 87 (meio) | Linha após regras | Alta frequência de uso |
| Hierarquia RLM | Linha 102 (meio) | Linha após comandos | Fluxo de leitura do agente |
| Portfólio/Status | Linha 39 (início) | Final | Referência, não ação |
| Stack Técnica | Linha 75 (meio) | Final | Referência, não ação |

---

## 4. Critérios de Aceite

Baseados nas métricas do paper (compliance de recuperação de informação):

- [ ] **CA-1:** Agente cita corretamente pelo menos 1 das Regras Invioláveis em qualquer resposta que envolva commit de código (sem precisar ser perguntado).
- [ ] **CA-2:** Agente aplica o Princípio do Foco de Contexto Estrito (Regra 10) espontaneamente ao iniciar trabalho num projeto — sem lembrete.
- [ ] **CA-3:** O arquivo reordenado mantém **100% do conteúdo original** — nenhuma informação é removida, apenas reposicionada.
- [ ] **CA-4:** A nova versão do arquivo deve ter no máximo **140 linhas** (manter concisão).
- [ ] **CA-5:** O cabeçalho de versão é atualizado para **v8.0 — Lost in Middle Reorder**.

---

## 5. Impacto e Riscos

| Item | Avaliação |
|---|---|
| **Impacto no agente** | Alto — muda o comportamento de toda sessão de trabalho |
| **Risco de regressão** | Baixo — nenhuma lógica de código é alterada |
| **Esforço estimado** | 30 minutos (edição + validação manual) |
| **Rollback** | Trivial — arquivo está sob controle de versão Git |

---

## 6. Referências

- Liu, N. F., Lin, K., Hewitt, J., et al. (2023). *Lost in the Middle: How Language Models Use Long Contexts.* arXiv:2307.03172. [PDF](https://arxiv.org/pdf/2307.03172)
- Arquivo alvo: `governance/operational-memory/contexto_rlm.md`
- Issue: [GARE-146](https://wganalytics.atlassian.net/browse/GARE-146)
