# SDD — GARE-152: ADRs (Architecture Decision Records) para Decisões Críticas

**Versão:** 1.0  
**Issue Jira:** GARE-152  
**Autor:** Wemerson (RLM Session #009)  
**Data:** 2026-08-05  
**Status:** Draft  
**Fundamentação:** Histórico e Rastreabilidade de Decisões de Engenharia (ADRs)

---

## 1. Contexto e Problema

### 1.1 Perda de Contexto Histórico

O ecossistema evolui rapidamente através de sessões iterativas com diferentes agentes de IA. Várias decisões técnicas cruciais foram tomadas ao longo do tempo (ex: *"usar sufixos de provedores nas coleções do ChromaDB para evitar erros de dimensionalidade"* ou *"proibir deploy direto em produção sem commit correspondente"*).

Atualmente, o histórico dessas decisões está fragmentado:
- Misturado em descrições de sessões longas no `diario_de_bordo.md` (174KB).
- Diluído em commits antigos.
- Enterrado na memória dos agentes de IA em conversas passadas.

Sem um repositório centralizado, estruturado e imutável de decisões de arquitetura (ADRs), novos agentes de IA correm o risco de reverter decisões deliberadas anteriores, causando regressões silenciosas de arquitetura.

---

## 2. Objetivo

Implementar a estrutura formal de **Architecture Decision Records (ADRs)** na pasta `governance/architecture-decisions/` seguindo a metodologia padrão de mercado. O objetivo é documentar o "porquê" por trás das escolhas de engenharia mais sensíveis do ecossistema.

---

## 3. Padrão Técnico do ADR

Cada documento de decisão de arquitetura deve seguir estritamente o seguinte template Markdown em `governance/architecture-decisions/adr-xxx_template.md`:

```markdown
# ADR-XXX: [Título Curto da Decisão]

* **Status:** [Draft | Approved | Superseded por ADR-YYY]
* **Data:** YYYY-MM-DD
* **Autor:** [Nome do Autor/Agente]
* **Jira:** [Chave da Issue, ex: GARE-XX]

---

## 1. Contexto
[Qual é o problema ou cenário técnico que exige uma decisão? Descreva as forças em jogo.]

## 2. Decisão
[Qual alternativa foi escolhida e qual o racional técnico por trás dela? Seja específico e direto.]

## 3. Consequências
[Quais os impactos positivos e negativos desta decisão no ecossistema?]
* **Positivo:** ...
* **Negativo/Dívida:** ...
```

---

## 4. Escopo Inicial (Primeiros 3 ADRs)

A issue GARE-152 exige a criação imediata dos primeiros 3 registros históricos que já foram validados nas sprints passadas:

1. **`adr-001-sufixo-provedor-vectordb.md`** — Documenta a obrigatoriedade do uso de sufixo no ChromaDB (`_openai`, `_gemini`) para evitar o erro de Dimensionality Mismatch ao alternar a LLM do `.env`.
2. **`adr-002-isolamento-tdd-projetos.md`** — Documenta a obrigatoriedade de cada projeto `/dev/` possuir sua própria suíte de testes unitários isolada, executável de forma independente do monorepo.
3. **`adr-003-gate-revisao-code-review.md`** — Documenta o uso obrigatório do Code Review Agent impedindo commits no "Vibe Coding" sem passar pelas guardrails de arquitetura e SRP.

---

## 5. Critérios de Aceite

- [ ] **CA-1:** O template de ADR `governance/architecture-decisions/adr-xxx_template.md` é criado com a estrutura padrão.
- [ ] **CA-2:** Os 3 primeiros ADRs (`ADR-001`, `ADR-002`, `ADR-003`) são escritos e persistidos com status `Approved`.
- [ ] **CA-3:** O index central `governance/architecture-decisions/readme.md` é atualizado listando os ADRs cadastrados.
- [ ] **CA-4:** O `contexto_rlm.md` aponta a pasta de ADRs como caminho crítico na tabela de navegação.

---

## 6. Referências

- Documenting Architecture Decisions (Michael Nygard).
- Issue Jira: [GARE-152](https://wganalytics.atlassian.net/browse/GARE-152)
