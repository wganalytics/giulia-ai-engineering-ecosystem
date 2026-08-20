# AI BOOTSTRAP INSTRUCTIONS (Universal Agent Entry Point)

Se você é um modelo fundacional, CLI Agent (Claude Code, Gemini CLI, OpenCode, Codex), ou IDE Agent (Cursor, Windsurf, Aider), este arquivo serve para rotear o seu contexto.

## Ação Imediata Obrigatória
Leia o arquivo: `governance/operational-memory/contexto_rlm.md`.

## Contexto do Repositório (Root)
Você está no root do **Giulia AI Engineering Ecosystem** — o repositório público do framework de governança e metodologia de AI Engineering.
Este repositório contém a documentação, os padrões e as ferramentas do ecossistema; não é o monorepo privado completo (não há pasta `dev/` com código-fonte de projetos aqui).

**Mapeamento Rápido de Pastas:**
- **Governança, Regras e Diário:** `governance/`
- **Docs por projeto (scaffold vazio até um novo projeto ser criado):** `governance/projects/PRJ-XX_*/`
- **Documentação de Arquitetura:** `docs/architecture/`, `docs/governance/`, `docs/roadmap/`
- **Ferramentas do Ecossistema:** `ecosystem/` e `scripts/`
- **Infraestrutura e configs:** `infra/`
- **Observabilidade:** `observability/`

**Regra de Ouro (TDD e Clean Code):**
Temos pipelines rigorosos de TDD e Code Review isolados por monorepo. Para mais informações, carregue o `contexto_rlm.md`.

## Protocolo de Atualização (Obrigatório para o Agente)
No fim de **qualquer** sessão ou sempre que você realizar mudanças no ecossistema (adicionar features, alterar estrutura, modificar código):
1. Você **DEVE** listar proativamente os arquivos que modificou.
2. Você **DEVE** perguntar ao usuário: *"Deseja que eu atualize o Diário de Bordo e o Manual do Ecossistema com essas mudanças?"*
3. Se o usuário confirmar, você deve invocar (ou ajudar o usuário a rodar) o script interativo:
   `python3 ecosystem/automation/atualizar_ecossistema.py`
