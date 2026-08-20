# SDD — GARE-153: Auto-geração do Diário de Bordo via Git Hook

**Versão:** 1.0  
**Issue Jira:** GARE-153  
**Autor:** Wemerson (RLM Session #009)  
**Data:** 2026-08-05  
**Status:** Draft  
**Fundamentação:** Redução de Atrito Operacional & Automatização de Rastreabilidade

---

## 1. Contexto e Problema

### 1.1 O Fator Fricção

O `diario_de_bordo.md` é a âncora de continuidade entre os agentes de IA. No entanto, sua atualização manual ao final de cada sessão apresenta problemas clássicos de UX/DX:
1. **Esquecimento:** Desenvolvedores e agentes esquecem de rodar o script `atualizar_ecossistema.py` ou de registrar a sessão antes de encerrar.
2. **Duplicação de Esforço:** A informação sobre o que mudou já está documentada no histórico do Git (arquivos modificados e mensagens de commit). Pedir para a IA digitar novamente gera custos redundantes de tokens e tempo.
3. **Inconsistência de Numeração:** Devido à edição manual, existem problemas recorrentes de sessões com numerações repetidas ou fora de ordem cronológica.

---

## 2. Objetivo

Desenvolver um script de automação (`ecosystem/automation/auto_diary.py`) integrado ao Git hook de pós-commit (`.git/hooks/post-commit`). Toda vez que um commit for gerado na branch local, o diário de bordo será atualizado automaticamente com as métricas reais do commit.

---

## 3. Arquitetura da Solução

### 3.1 Fluxo Operacional

```text
Git Commit ──► Trigger Hook (.git/hooks/post-commit)
                   │
                   ▼
       auto_diary.py executa:
         1. Recupera hash, autor, msg e arquivos do HEAD
         2. Auto-incrementa número da sessão (#099, #100...)
         3. Estrutura a entrada no formato RLM
         4. Prepende no diario_de_bordo.md
```

### 3.2 Parsing do Git Commit

O script executará comandos git locais para obter os dados:

```bash
# Mensagem do commit
git log -1 --pretty=%B

# Autor do commit
git log -1 --pretty=%an

# Lista de arquivos alterados
git diff-tree --no-commit-id --name-only -r HEAD
```

---

## 4. Estrutura da Entrada Gerada Automaticamente

A entrada inserida no diário seguirá o padrão restrito RLM:

```markdown
### Sessão #099 — YYYY-MM-DD
**Agente:** [Nome do Autor do Commit] (ex: Antigravity/Wemerson)
**Foco:** [Primeira linha da mensagem do commit]

**Features entregues:**
- [Arquivo alterado 1] (ex: modificado /docs/specs/PRJ-XX_SDD.md)
- [Arquivo alterado 2] (ex: criado /dev/mcp/server.py)

*Nota: Entrada gerada automaticamente via Git Commit [Hash Short]*
```

### 4.1 Incremento Automático

O script lerá o diário, localizará a última linha contendo `### Sessão #` e extrairá o número inteiro para somar `+1`, garantindo que não haverá colisões de numeração de sessões.

---

## 5. Critérios de Aceite

- [ ] **CA-1:** O script `ecosystem/automation/auto_diary.py` é executado com sucesso de forma isolada e aceita a flag `--dry-run` (imprime no terminal em vez de escrever no diário).
- [ ] **CA-2:** Criar um commit git na branch local aciona o hook `post-commit` e atualiza o diário sem erros.
- [ ] **CA-3:** O script detecta automaticamente a numeração da sessão lendo a entrada anterior e incrementando de forma correta.
- [ ] **CA-4:** O script não atualiza o diário caso o commit seja do tipo `merge` automático ou não possua alterações em pastas críticas de desenvolvimento (ex: commit que altere apenas `.gitignore` ou arquivos internos do `.git` não gera sessão).

---

## 6. Referências

- Issue Jira: [GARE-153](https://wganalytics.atlassian.net/browse/GARE-153)
