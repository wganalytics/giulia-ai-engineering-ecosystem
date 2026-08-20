# 🛡️ Padrão: Governance Snapshot (Engineering Knowledge Capsule)

## 1. Propósito
O **Governance Snapshot** é o mecanismo oficial do ecossistema GIULIA AI para garantir a persistência da memória operacional e técnica de forma descentralizada. 

Ao transformar cada projeto em uma **Cápsula de Conhecimento de Engenharia**, garantimos que:
- Um projeto possa ser mantido sem ler todo o histórico global do ecossistema.
- Agentes de IA (GPT, Claude, Gemini, Antigravity) possam assumir o trabalho com perda mínima de contexto.
- Decisões arquiteturais e "alternativas rejeitadas" fiquem registradas junto ao código.

## 2. Estrutura Obrigatória (`project_context/`)

Todo projeto deve conter os seguintes arquivos numerados para priorização de leitura por IAs:

| Arquivo | Conteúdo Principal |
|---------|-------------------|
| `00_SNAPSHOT_INDEX.md` | Índice e guia de uso para novos agentes. |
| `01_OPERATIONAL_MEMORY.md` | Sessões do diário filtradas e notas de handoff. |
| `02_ARCHITECTURE_LOG.md` | Overview, Componentes e **Rejected Alternatives**. |
| `03_MAINTENANCE_GUIDE.md` | Ops, Testes e **Emergency Recovery**. |
| `04_OBSERVABILITY_REPORT.md` | Métricas GARE e Gaps de Observabilidade. |
| `05_GOVERNANCE_TRACE.md` | Rastreabilidade Jira, Registry e **Git Traceability**. |
| `06_LESSONS_LEARNED.md` | Reflexões de engenharia, bugs e insights TDD/SDD. |

## 3. Regras de Ouro

### 3.1. Seções Mandatórias
- **Rejected Alternatives**: É obrigatório documentar o que NÃO foi feito e por quê.
- **Emergency Recovery**: Procedimentos para resetar bancos (Chroma/Neo4j) e recuperar o ambiente.
- **Git Traceability**: Registro do branch e último commit de referência.

### 3.2. Segurança e Blindagem
O gerador de snapshot **NUNCA** deve copiar ou expor:
- Arquivos `.env` ou segredos.
- Tokens ou credenciais.
- Binários de banco de dados (`vector_db`, `sqlite`).
- Documentos PDF de fonte original.

### 3.3. Handoff Multi-Agente
O snapshot deve ser escrito em Markdown estruturado, otimizado para que uma LLM identifique rapidamente:
1. **Estado Atual**: O que está funcionando e onde paramos.
2. **Arquitetura**: O "Porquê" das decisões técnicas.
3. **Ops**: Como rodar e validar o projeto em 30 segundos.

## 4. Workflow de Atualização
O snapshot deve ser gerado ou atualizado:
1. Ao final de cada fase importante (SDD, TDD, Encerramento).
2. Antes de trocar de modelo de IA (ex: de Gemini para Claude).
3. Após correções arquiteturais significativas.

**Comando:** `python infra/start_project.py --snapshot PRJ-XX`

---
## Engineering Knowledge Capsule Principle
> *"Cada projeto deve conter contexto operacional, arquitetural, de manutenção e de governança suficiente para permitir que um futuro agente humano ou de IA entenda e mantenha o projeto sem ler toda a história global do ecossistema."*
