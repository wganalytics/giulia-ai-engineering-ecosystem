# 🔧 Setup GitHub e CI/CD

> **Objetivo:** Configurar o repositório GitHub com CI/CD automatizado

---

## 1. Criar Repositório no GitHub

### Via Web (Recomendado)

1. Acesse: https://github.com/new
2. Preencha:
   - **Repository name:** `rag-ecosistema`
   - **Description:** "Ecossistema de Projetos RAG - Automação Jira + IA"
   - **Public** ou **Private** (recomendo Private)
3. Não inicialize com README (iremos fazer push do código existente)
4. Clique **Create repository**

---

## 2. Conectar Repositório Local

No terminal, na pasta raiz do projeto:

```bash
# Inicializar git (se ainda não feito)
git init

# Adicionar remote
git remote add origin https://github.com/SEU_USUARIO/rag-ecosistema.git

# Adicionar todos os arquivos
git add .

# Commit inicial
git commit -m "feat: Initial ecosystem setup - Infrastructure, Jira automation, RLM patterns"

# Criar branch main
git branch -M main

#推送 ao GitHub
git push -u origin main
```

---

## 3. Configurar Secrets no GitHub

### No GitHub:

1. Acesse o repositório
2. Vá em **Settings** → **Secrets and variables** → **Actions**
3. Adicione os seguintes secrets:

| Secret | Descrição | Exemplo |
|--------|-----------|---------|
| `JIRA_DOMAIN` | Domínio do Jira | `seudominio.atlassian.net` |
| `JIRA_EMAIL` | Email do Jira | `seu@email.com` |
| `JIRA_TOKEN` | Token API do Jira | `token_gerado` |
| `JIRA_PROJECT_KEY` | Chave do projeto | `RAG` |

### Para gerar o Token Jira:

1. Acesse: https://id.atlassian.com/manage-profile/security/api-tokens
2. Clique **Create API token**
3. Dê um nome (ex: `rag-ecosistema`)
4. Copie o token e adicione como secret

---

## 4. Verificar CI/CD

Após o push, o GitHub Actions will automatically:

1. **Executar testes** (`pytest`)
2. **Verificar lint** (`ruff check`)
3. **Type checking** (`mypy`)
4. **Build do pacote**

Para verificar:
1. Acesse: `https://github.com/SEU_USUARIO/rag-ecosistema/actions`
2. Você verá o workflow em execução

---

## 5. Adicionar Badge ao README

No seu `README.md` principal, adicione:

```markdown
[![CI](https://github.com/SEU_USUARIO/rag-ecosistema/actions/workflows/ci.yml/badge.svg)](https://github.com/SEU_USUARIO/rag-ecosistema/actions)
[![Python](https://img.shields.io/badge/python-3.12-blue)](https://www.python.org/)
[![Ruff](https://img.shields.io/badge/lint-ruff-yellow)](https://docs.astral.sh/ruff/)
```

---

## 6. Fluxo de Trabalho

```bash
# Desenvolvimento normal
git add .
git commit -m "feat: Description"
git push

# CI/CD executa automaticamente:
# 1. pytest (testes)
# 2. ruff check (lint)
# 3. mypy (type check)
# 4. Build package
```

---

## 🆘 Troubleshooting

### Erro de permissão no Actions
- Verifique se o workflow tem permissões corretas
- Settings → Actions → General → "Read and Write"

### Secrets não funcionam
- Verificar se o nome das secrets está correto
- Secrets são case-sensitive

### Tests falham localmente
- Execute localmente: `pytest infra/tests/`

---

## 📝 Arquivos Ignorados (já configurado)

O `.gitignore` já inclui:
- `logs/` - Arquivos de log
- `.env` - Variáveis de ambiente
- `.sync_state.json` - Estado do sync
- `__pycache__/` - Cache Python
- `venv/` - Ambiente virtual