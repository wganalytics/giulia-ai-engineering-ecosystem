# SDD — GARE-147: ACI CLI (Agent-Computer Interface CLI)

**Versão:** 1.0  
**Issue Jira:** GARE-147  
**Autor:** Wemerson (RLM Session #009)  
**Data:** 2026-08-05  
**Status:** Draft  
**Fundamentação Científica:** Yang et al., 2024 — *"SWE-agent: Agent-Computer Interfaces Enable Automated Software Engineering"* ([arXiv:2405.15793](https://arxiv.org/abs/2405.15793))

---

## 1. Contexto e Problema

### 1.1 Evidência Empírica (Paper)

O paper *SWE-agent* (Princeton, 2024) introduziu o conceito de **Agent-Computer Interface (ACI)**. A premissa central é que os sistemas operacionais, shells (bash/zsh) e editores clássicos de texto foram projetados para interação humana, com feedbacks visuais e verbosidades inadequados para IAs.

> *"Just as humans benefit from powerful software applications, such as integrated development environments, for complex tasks like software engineering, we posit that LM agents represent a new category of end users with their own needs and abilities, and would benefit from specially-built interfaces to the software they use."*

Ao desenhar ferramentas específicas com feedbacks curtos, claros, sem paginação de tela, e delimitando escopos rígidos, o desempenho de LLMs no SWE-bench subiu de **1.96%** (Claude 2 puro) para **12.5%** (SWE-agent ACI), um ganho de ~6.4x com o mesmo modelo básico.

### 1.2 Nossa Situação Atual

No ecossistema GARE, os agentes executam ferramentas de terminal cruas (ex: `find`, `grep`, `cat`, `ls`) ou scripts avulsos. Isso gera vários problemas recorrentes:
1. **Erro de Pathing:** Agentes se perdem na árvore do monorepo e leem o arquivo errado (ex: ler o `CONTEXTO_RLM` antigo da pasta `architecture-decisions` em vez da pasta `operational-memory`).
2. **Poluição de Contexto:** Comandos `cat` em arquivos gigantes estouram a janela de contexto sem necessidade.
3. **Erros de Sintaxe em Scripts:** Agentes chamam scripts Python locais com argumentos errados ou esquecem de carregar as credenciais do `.env`.
4. **Falta de Isolamento:** Comandos como `git add .` às vezes pegam arquivos de outros projetos por acidente.

---

## 2. Objetivo

Desenvolver a **GARE CLI (`ecosystem/cli/gare_cli.py`)**, uma ACI unificada que encapsula as operações do ecossistema. Toda e qualquer ação de busca, status, e interação com a governança deve ser feita via ACI para garantir zero fricção e conformidade mecânica do agente.

---

## 3. Arquitetura da Solução

O script `gare_cli.py` será uma interface CLI baseada em Python, estruturada em subcomandos:

```text
gare [subcomando] [argumentos]
```

### 3.1 Lista de Comandos da ACI

| Comando | Descrição | Input do Agente | Output da ACI (JSON/Markdown) |
|---|---|---|---|
| `project list` | Lista todos os projetos no dev/ | Nenhum | Tabela Markdown com ID, Nome, Domínio e Status. |
| `project context <key>` | Mapeia o escopo e carrega RLM do projeto | Chave (ex: `PRJ-XX`) | Conteúdo compilado de `ideia.md` + `implementation_plan.md` (filtrado para as seções críticas). |
| `project test <key>` | Roda a suíte de testes de um projeto específico | Chave (ex: `PRJ-XX`) | Resumo dos testes (total, passados, falhos) + erro do primeiro teste que falhar (evitando logs longos). |
| `jira status <issue_key>` | Consulta o card no board sem usar curl | Chave Jira (ex: `GARE-140`) | Título, Descrição, Status atual e Sub-tasks vinculadas. |
| `jira transition <issue_key> <status>` | Move o card no fluxo do Kanban | Chave + Novo Status | Confirmação da transição ou lista de blockers. |
| `validate` | Executa o validador de ecossistema | Nenhum | Status verde ou problemas listados por categorias. |

---

## 4. Especificações Técnicas de Implementação

### 4.1 Restrição de Contexto (Anti-Lost in Middle)

Para comandos que imprimem conteúdo de arquivos (como `project context`), a CLI deve filtrar o arquivo para remover ruídos. 
Por exemplo, omitir seções de changelog longo e focar nas seções de "Proposed Changes" ou "Open Questions".

### 4.2 Formatação de Output

Todo output de comando da ACI deve ser estruturado em **Markdown limpo** ou **JSON estruturado** se a flag `--json` for passada. O output deve sempre terminar com uma linha de status clara:
- `[SUCCESS] <descrição>`
- `[ERROR] <razão do erro>`

Isso ajuda a IA a validar mecanicamente o resultado do comando usando expressões regulares internas simples.

---

## 5. Critérios de Aceite

- [ ] **CA-1:** O arquivo `ecosystem/cli/gare_cli.py` é criado e importável.
- [ ] **CA-2:** Executar `python3 ecosystem/cli/gare_cli.py --help` lista todos os subcomandos de forma legível.
- [ ] **CA-3:** Executar `gare project list` retorna todos os projetos mapeados sob `dev/` em formato de tabela markdown limpa.
- [ ] **CA-4:** O comando `gare project test PRJ-XX` localiza e executa os testes do workspace do PRJ-XX usando a venv local do projeto, se existente, ou a venv do monorepo, isolando logs excessivos.
- [ ] **CA-5:** Toda a autenticação de chamadas de API (Jira) na CLI é feita importando o `context_loader.py` para garantir conformidade de segurança.

---

## 6. Referências

- Yang, J., Wu, A. M., Kiciman, E., et al. (2024). *SWE-agent: Agent-Computer Interfaces Enable Automated Software Engineering.* arXiv:2405.15793. [PDF](https://arxiv.org/pdf/2405.15793)
- Issue Jira: [GARE-147](https://wganalytics.atlassian.net/browse/GARE-147)
