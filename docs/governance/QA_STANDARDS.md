# ⚖️ Padrões de Governança e QA

> **Propósito:** Definir os padrões de Qualidade e Governança que protegem o código do ecossistema Giulia AI de degradações.

## 1. TDD Orchestrator (Orquestração DevOps)

O ecossistema adota a prática de **Isolamento de Monorepo**. Como um monorepo pode abrigar múltiplos projetos complexos sob a pasta `dev/`, rodar um `pytest` global causaria colisões de importação e conflitos de dependências.

**O Padrão Adotado:**
- Um script central (`scripts/governance/tdd_orchestrator.py`) atua como pipeline DevOps.
- Ele itera sobre cada pasta `PRJ-*`.
- Sobrescreve dinamicamente o `PYTHONPATH` para enjaular o ambiente no root de cada projeto.
- Gera um laudo em Markdown (`governance/tdd/TDD_SNAPSHOT_*.md`) com o score de saúde do ecossistema.
- **Regra de Ouro:** *Nenhum código novo é commitado se o Health Score cair.*

## 2. Code Review Agent

A Governança Técnica é automatizada via a Skill `code-review-agent`.

- O Agente analisa os arquivos sob a ótica estrita de **Clean Code**, **SOLID** (foco em *Single Responsibility Principle*) e remoção de "Vibe Coding" (código escrito sem rigor técnico e testes).
- Ele refatora os arquivos na hora usando blocos de substituição (`replace_file_content`).

## 3. Segurança e Guardrails (Sandwich Defense)

Implementado no arquivo `ecosystem/agents/guardrails.py`, baseado no framework do livro *"Engenharia de Prompts II"*.

- **Input Validator:** Impede injeção de prompt detectando palavras como "ignorar regras anteriores", "system prompt" ou "roleplay".
- **Output Validator:** Protege contra vazamento de PII (CPFs, e-mails, telefones).
- **Defense Wrapper:** Posiciona instruções de sistema críticas não apenas no início do prompt, mas também repetidas no final, "imprensando" o input do usuário para forçar o foco no comportamento originalmente definido.
