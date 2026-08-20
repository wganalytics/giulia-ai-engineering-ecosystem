# 📓 Diário de Bordo do Ecossistema

> **Propósito:** Este documento é o registro cronológico de todas as sessões de desenvolvimento, decisões técnicas e progresso do projeto. Ele existe para garantir **continuidade entre diferentes agentes de IA (LLMs)**, permitindo que qualquer modelo que entre no projeto possa ler este arquivo e compreender imediatamente o estado atual, as convenções adotadas e o que falta fazer.
>
> **Regra:** Toda sessão de trabalho relevante deve gerar uma nova entrada neste diário. Ao final de cada sessão, o agente ativo deve adicionar um bloco resumindo o que foi feito e quais são os próximos passos.

---

## 🔑 Leitura Obrigatória para Novos Agentes

Se você é um agente de IA lendo este documento pela primeira vez, siga estes passos **antes de fazer qualquer coisa**:

1. **Leia o Manual:** [manual_do_ecossistema.md](../standards/manual_do_ecossistema.md) — contém toda a estrutura de pastas, convenções, ferramentas e regras do projeto.
2. **Leia a última entrada deste diário** para entender o estado atual do projeto.
3. **Verifique `ideia.md` e o `implementation_plan.md`** do projeto ativo em `governance/projects/PRJ-XX_*/` (scaffold vazio até um novo projeto ser criado com o framework).

---

## 📊 Status Geral

Veja [status.md](./status.md) para o dashboard atualizado dos projetos ativos.

---

## 📝 Registro de Sessões

### Sessão #127 — 2026-08-16
**Agente:** wganalytics
**Foco:** docs(governance): registra stub automatico da sessao #126 (hook pos-commit)

**Features entregues:**
- modificado /governance/operational-memory/diario_de_bordo.md

*Nota: Entrada gerada automaticamente via Git Commit [44c6275]*

---

### Sessão #125 — 2026-08-16
**Agente:** wganalytics
**Foco:** docs(governance): registra sessoes pendentes #110 a #124 do diario de bordo

**Features entregues:**
- modificado /governance/operational-memory/diario_de_bordo.md

*Nota: Entrada gerada automaticamente via Git Commit [fb8c254]*

---

### Sessão #124 — 2026-08-16
**Agente:** Claude Code (Sonnet 5)
**Foco:** Skill giulia + guardrails de governança contra dado externo assumido sem validar

**Features entregues:**
- Guardrail no prj_init.py: chave do epico Jira e validada contra a API real antes de prosseguir, com confirmacao do usuario
- Guardrail no prj_init.py: CLAUDE.md local agora e gerado automaticamente, vinculado aos dados reais do wizard (silo, board, epico, time)
- Regra 13 registrada em contexto_rlm.md: nunca assumir dado de sistema externo (Jira, GitHub) sem validar contra a API antes de agir
- Regra 6 de contexto_rlm.md corrigida: tdd_orchestrator.py nao existe, pipeline real e run_tdd_pipeline.sh (cognition_router -> dynamic_escalator -> circuit_breaker)
- Skill "GIULIA AI Engineering Ecosystem" criada em <local-skills-dir>/giulia: orquestrador + 5 especialistas (Jira/Governanca, Scaffolding de Projeto, TDD/Qualidade, SDD/Especificacoes, Documentacao/Diario)

**Decisões arquiteturais:**
- Especialistas da skill giulia sao delegados via subagente real (Agent tool, general-purpose) com contexto explicito passado no prompt, nao apenas leitura inline do arquivo de instrucoes - decisao tomada para evitar que um subagente assuma projeto_id ou chaves Jira por conta propria
- Specs de projetos em dev/<silo>/ sao sempre locais (pasta specs/ do proprio projeto), nunca em docs/specs/ central - essa convencao central e exclusiva de portfolios legados anteriores do ecossistema

**Próximos passos:**
- Testar os especialistas de Scaffolding, TDD e Documentacao da skill giulia em uso real (so o de Jira/Governanca foi testado ponta a ponta ate agora)
- Considerar dar Acesso Total ao Disco ao terminal para permitir listagem (ls/find) de ~/Documents, hoje bloqueada pelo TCC do macOS

---

### Sessão #117 — 2026-08-14
**Agente:** Claude Code (Sonnet 5)
**Foco:** Deploy em produção de um projeto de cliente na VPS compartilhada — padrão de infraestrutura e reuso de design system entre produtos

**Resumo (lições de infraestrutura, generalizadas para qualquer projeto do ecossistema):**
- Segundo produto do ecossistema publicado na VPS compartilhada em `/opt/giulia-ai/<nome>/` — confirma esse caminho (não `/opt/<nome>/`) como o padrão real de deploy: Postgres dedicado por serviço, duas redes Docker (interna + `npm_default`), roteamento por Cloudflare Tunnel + Nginx Proxy Manager.
- Primeira vez que um design system do ecossistema é conscientemente reaproveitado entre dois produtos distintos, não só entre telas do mesmo produto.
- Achado que vale para qualquer deploy futuro nessa VPS: o `.conf` do nginx do NPM só é gerado no momento da chamada de API (create/update de Proxy Host) — nunca automaticamente no boot do container. Um registro inserido direto no banco (bypass da UI) fica "invisível" pro nginx até alguém disparar uma ação real pela API ou escrever o `.conf` manualmente.
- Achado de troubleshooting: DNS "Somente DNS" (não Proxied) no Cloudflare para um hostname de Tunnel quebra a rota inteira — sintoma inicial parecia problema no NPM, causa real era o toggle de proxy desligado no registro DNS.

**Erro de método registrado:** diagnosticar "duas VPS diferentes" a partir de uma lista de Proxy Hosts inconsistente, sem checar primeiro hipóteses mais simples (cache de sessão do navegador, timing). Vale como lembrete de ordem de investigação pra qualquer sessão futura de troubleshooting de infra.

---

### Sessão #107 — 2026-08-07
**Agente:** wganalytics
**Foco:** docs(seguranca): asserção negativa que passa vazia, e a âncora que resolve

**Features entregues:**
- modificado /governance/standards/padrao_seguranca_aplicacoes.md

*Nota: Entrada gerada automaticamente via Git Commit [2c56ee8]*

---

### Sessão #106 — 2026-08-07
**Agente:** wganalytics
**Foco:** docs(seguranca): fecha as duas lacunas de prompt injection do Apêndice B

**Features entregues:**
- modificado /governance/standards/padrao_seguranca_aplicacoes.md

*Nota: Entrada gerada automaticamente via Git Commit [a44d23e]*

---

### Sessão #105 — 2026-08-07
**Agente:** wganalytics
**Foco:** docs(seguranca): padrão de como verificar e como construir, tirado do que já quebrou

**Features entregues:**
- modificado /governance/operational-memory/index.md
- criado /governance/standards/padrao_seguranca_aplicacoes.md

*Nota: Entrada gerada automaticamente via Git Commit [92ddd53]*

---

### Sessão #101 — 2026-08-05
**Agente:** wganalytics
**Foco:** docs(diario): Sessão #003 — auditoria de dependência, prazo de sessão e dois erros de método

**Features entregues:**
- modificado /governance/operational-memory/diario_de_bordo.md

*Nota: Entrada gerada automaticamente via Git Commit [b2f9008]*

---

### Sessão #099 — 2026-08-05
**Agente:** Antigravity (IA)
**Foco:** Implementação física das specs pendentes (TDD Fase Green) GARE-145 a 153

**Features entregues:**
- GARE-150: Limpeza estrutural da raiz e atualização do .gitignore
- GARE-152: Estruturação dos primeiros 3 ADRs e índice README
- GARE-153: Script auto_diary.py e hook post-commit para auto-geração do diário
- GARE-145: Banco de dados tasks.json e runner.py de benchmark do GARE-bench
- GARE-147: Interface ACI CLI gare_cli.py para agentes autônomos
- GARE-149: Cypher schema unificado de grafo para Neo4j (graph_schema.cypher)
- GARE-151: Cálculo do Health Score e telemetria JSON no validate_ecosystem.py

**Decisões arquiteturais:**
- Institucionalizada a estrutura de ADRs na pasta governance/architecture-decisions/
- Unificação do esquema de grafo (Neo4j Cypher DDL) para evitar divergências nos projetos RAG e CodeCompass

**Próximos passos:**
- Retomar o roadmap de desenvolvimento do CodeCompass, implementando o extrator AST (GARE-141) e o servidor MCP (GARE-142)
- Realizar auditorias adicionais de conformidade de código

---

### Sessão #098 — 2026-08-05
**Agente:** Antigravity (Gemini/Claude)
**Foco:** Planejamento do CodeCompass (GARE-140) e Auditoria Científica do Ecossistema

**Features entregues:**
- Criado Épico GARE-140 no Jira e 4 subtasks vinculadas (GARE-141 a 144) baseadas no CodeCompass (arXiv:2602.20048).
- Analisados 8 papers científicos e mapeados os gaps arquiteturais em relação ao ecossistema (salvo em governance/sdd/ e analise_correlacao_papers.md).
- Criadas 9 issues no Jira correspondentes aos gaps identificados (GARE-145 a GARE-153).
- Criados os Software Design Documents (SDDs) baseados em evidência científica para todos os GAPs (GARE-140, GARE-145, GARE-147, GARE-149, GARE-151, GARE-152, GARE-153) na pasta governance/sdd/.
- Criadas as suítes de teste TDD (estado Red) em ecosystem/tests/ para validar mecanicamente a entrega de todas as melhorias pendentes (GARE-145, 147, 149, 150, 151, 152, 153).
- Implementado GARE-146: Reordenado o arquivo contexto_rlm.md (v8.0) priorizando as Regras Invioláveis no topo (Lost in Middle Compliance).
- Implementado GARE-148: Adicionado o Protocolo GARE-3F (Localizar, Implementar, Validar) no contexto_rlm.md e Seção 15 no MANUAL_DO_ecossistema.md (Agentless Compliance).
- Transicionados os cards GARE-146 e GARE-148 para Done com notas técnicas no Jira.
- Rodado validate_ecosystem.py e verificado 100% de consistência.

**Próximos passos:**
- Em uma nova sessão de chat limpa, iniciar a implementação física (Fase Green) para fazer as suítes TDD passarem nos testes, começando pela limpeza de raiz (GARE-150) e ADRs (GARE-152) que são de baixo esforço.
- Prosseguir no roadmap rumo à construção do CodeCompass.

---

### Sessão #092 — 2026-07-14
**Agente:** Claude Code (Sonnet 5)
**Foco:** Diário por projeto no protocolo de atualização do ecossistema

**Features entregues:**
- Adicionada flag --projeto ao atualizar_ecossistema.py para gravar sessões no diário local de dev/Giulia/<projeto>/diario_de_bordo.md em vez de só no central
- Resolução de projeto por nome exato ou parcial (case-insensitive), com erro claro em caso de ambiguidade ou nenhum match
- Criação automática do diário local com template quando o arquivo ainda não existe
- Sugestão de commit agora referencia o path real do diário gravado (local ou central)

**Decisões arquiteturais:**
- Diário central passa a ser reservado para decisões cross-projeto; diário por projeto vira o padrão para sessões de trabalho de projetos individuais, evitando que o central vire gargalo à medida que o número de projetos cresce
- Manual do Ecossistema (Changelog) continua centralizado — é decisão institucional, não por projeto

**Próximos passos:**
- Avaliar migrar hooks/automations existentes que chamam o script para passar --projeto quando fizer sentido

---

### Sessão #054 — 2026-06-09
**Agente:** Antigravity (Gemini)
**Foco:** Isolamento de Governança para Projetos de Clientes e Múltiplos Jiras

**Features entregues:**
- **Reestruturação Arquitetural Client-Ready**: O framework agora aceita a estrutura rasa `dev/NomeCliente/PRJ-XX_NomeProjeto/`, permitindo a gestão paralela de múltiplos clientes sem quebra de diretórios. O modelo foi validado com um projeto de cliente de exemplo.
- **Desacoplamento do Registry Central**: Removida a dependência do `ecosystem_registry.json` para carregar dados do Jira. A fonte da verdade agora é o arquivo `projetos.yaml` local de cada projeto.
- **Jira Multitenant Isolado**: Atualizado o gerador `prj_init.py` para injetar o bloco `jira` no `projetos.yaml`. Projetos diferentes agora podem apontar não só para keys diferentes, mas opcionalmente para domínios inteiramente isolados do Jira, protegendo os dados dos clientes de vazamento de contexto entre as LLMs.
- **Integração Dinâmica de Ferramentas Base**: `context_loader.py` e `lifecycle_manager.py` foram refatorados para realizar *path resolution* dinâmico: o sistema sobe a árvore de arquivos até achar o `projetos.yaml` mais próximo e se autoconfigura, garantindo compatibilidade retroativa.

**Decisões arquiteturais:**
- O estado e as integrações pertencem ao projeto (`projetos.yaml`), não ao monorepo. Qualquer arquivo central de registro apresenta um risco inaceitável de vazamento de contexto inter-clientes por parte dos agentes de IA.

**Próximos passos:**
- Iniciar a especificação e desenvolvimento do primeiro projeto de cliente externo usando a nova infraestrutura isolada.

---

### Sessão #053 — 2026-06-09
**Agente:** Antigravity (Gemini)
**Foco:** Alinhamento de Engenharia: Git ACID, Escalação e Auditoria Avançada

**Features entregues:**
- **Git ACID / Reversibilidade**: Integrado mecanismo de rollback baseado em `git checkout` e `git clean` no `agent_harness.py` para desfazer modificações em caso de falha nos testes do TDD.
- **Resiliência / Escalação de Modelos**: Implementado failover em `agent_harness.py` escalando o modelo para `qwen3.5:35b` local após 2 falhas consecutivas de TDD, com restauração automática para o padrão `llama3.2:3b` após validação bem-sucedida.
- **Auditoria Expandida**: Atualizado `audit_system.py` para validar a presença de suíte de testes (TDD), verificar a ocorrência de placeholders em arquivos de especificação (`specs/`) e conferir o alinhamento de commits Git de cada projeto.
- **Compilador de Diretrizes**: Desenvolvido `load_insights_rules.py` para extrair de forma determinística 72 conceitos relevantes do livro de engenharia de software de agentes, injetando-os como regras do sistema no prompt do Harness.
- **Suíte de Testes**: Criado script `test_harness_integration.py` que isola e valida o fluxo de TDD, rollbacks e escalações do Harness com 100% de sucesso.

**Decisões arquiteturais:**
- O Git atua como repositório transacional (ACID); qualquer intervenção malsucedida de agentes inteligentes é cancelada instantaneamente, impedindo contaminações e garantindo que o monorepo permaneça íntegro.
- Escalação progressiva e dinâmica de LLMs locais no Ollama minimiza o custo computacional operacional e eleva a resiliência em tarefas de alta complexidade.

**Próximos passos:**
- Corrigir nos projetos do portfólio os desalinhamentos apontados pela nova auditoria (placeholders remanescentes em specs e suítes de teste TDD faltantes).

---

### Sessão #042 — 2026-05-27
**Agente:** Antigravity (IA)
**Foco:** Integração de Diretrizes do Livro de Engenharia de Software no Ecossistema

**Features entregues:**
- Adicionado guia diretrizes_desenvolvimento_ia.md com diretrizes de engenharia de software de IA baseadas no livro de engenharia de software de agentes

**Decisões arquiteturais:**
- Formalização do AI Engineering Paradigm (morte do vibe coding) via spec obrigatória (SDD) e testes (TDD) para qualquer desenvolvimento.
- Definição do controle transacional via Git como mecanismo ACID e rollback instantâneo para agentes autônomos.
- Divisão arquitetural clara de extensibilidade entre Agent Skills (Poder Interno) e MCP (Poder Externo).

**Próximos passos:**
- Auditar as Agent Skills existentes sob o novo prisma estrutural POO.

---

### Sessão #041 — 2026-05-27
**Agente:** Antigravity (IA)
**Foco:** Governança e Conclusão da Pipeline de Ingestão de Conhecimento (Book Ingestor)

**Features entregues:**
- Finalização da automação da pipeline de ingestão de conhecimento (Book Ingestor) com suporte robusto a retry de backoff exponencial e uso inteligente de modelos estáveis do Gemini (gemini-flash-latest) para contornar quotas do Free Tier, resolvendo por completo a geração e regeneração de insights (INSIGHTS_MCP - Final Branca.md) para os 20 primeiros capítulos.

**Decisões arquiteturais:**
- Uso do modelo gemini-flash-latest da API do Gemini para garantir estabilidade e contornar quotas estritas de 20 RPM/dia do Free Tier.
- Regeneração isolada de insights com extração direta em JSON mantendo o isolamento de chunks no ChromaDB.

**Próximos passos:**
- Integrar OCR/Tesseract no ambiente para leitura de PDFs puramente digitalizados (scanned PDFs).

---

### Sessão #038 — 2026-05-26
**Agente:** Antigravity (IA)
**Foco:** Padronização e Governança do Ecossistema

**Features entregues:**
- Criados scripts validate_ecosystem.py, governance_snapshot.py e start_project.py em ecosystem/automation/
- Criados scripts lifecycle_manager.py, jira_sync.py e atualizar_tarefa.py em ecosystem/jira/
- Atualizado validate_ecosystem.py para resolver caminhos canônicos no monorepo e evitar falhas de validação silenciosas

**Decisões arquiteturais:**
- Isolamento total de coleções vetoriais e centralização de specs comportamentais em docs/specs/

**Próximos passos:**
- Seguir com a ingestão automatizada de livros de referência usando RAG

---

### Sessão #037 — 2026-05-26
**Agente:** Antigravity (IA)
**Foco:** Fechamento de Brecha de Governança no Entry Point (README)

**Features entregues:**
- Injetado bloco UPDATE GUARDRAIL MANDATORY no topo absoluto do README.md principal

**Decisões arquiteturais:**
- O README.md agora possui o guardrail de atualização hardcoded logo na primeira instrução de AI para garantir que agentes desatentos (que não leem o CONTEXTO_RLM) também cumpram o protocolo.

**Próximos passos:**
- Rodar a ingestão do livro MCP no modo --update

---

### Sessão #036 — 2026-05-26
**Agente:** Antigravity (IA)
**Foco:** Implementação do Protocolo de Atualização, Correção do Book Ingestor e Governança de VectorDB

**Features entregues:**
- Adicionado Protocolo de Atualização no AI_BOOTSTRAP.md, .cursorrules e contexto_rlm.md
- Adicionada regra de Isolamento de VectorDB (Dimensionalidade) no Manual e RLM
- Refatorado select_llm.py para priorizar provedores de nuvem via .env (OpenRouter, OpenAI, Gemini)
- Refatorado embed_chunks.py para suportar múltiplas collections baseadas no provedor (evitando conflitos no ChromaDB)
- Refatorado ingest_books.py para tratar falhas de embeddings com aviso crítico e interrupção.

**Decisões arquiteturais:**
- Todos os agentes de IA agora são obrigados a listar arquivos modificados e rodar o script de atualização no fim de cada feature.
- Coleções do ChromaDB devem conter o sufixo do provedor (ex: knowledge_books_openai) para prevenir falha de dimensionalidade.

**Próximos passos:**
- Rodar a ingestão do livro MCP no modo --update utilizando as correções implementadas.

---

### Sessão #035 — 2026-05-25
**Agente:** Antigravity (Claude Sonnet — Thinking)
**Foco:** Governança Documental — Centralização de Specs + Protocolo de Atualização Contínua

**Features entregues:**
- **Centralização de SDDs (`docs/specs/`):** Formalizado `docs/specs/` como local canônico para todos os arquivos Spec-Driven Development. `governance/sdd/` arquivado. `contexto_rlm.md`, `AI_BOOTSTRAP.md` e `.contexto_navegacao.md` atualizados para apontar para o novo path.
- **SDDs Gerados Programaticamente:** SDDs de todos os projetos do portfólio ativo à época criados a partir da análise da lógica dos motores e requisitos arquiteturais de cada projeto.
- **Separação Visual vs. Técnico:** `docs/architecture/` mantido exclusivamente para diagramas Mermaid/PNGs; `docs/specs/` exclusivo para especificações comportamentais.
- **Diário de Bordo Consolidado:** Identificada duplicidade entre `governance/operational-memory/diario_de_bordo.md` (canônico, sessão #021) e `shared/planning_docs/acompanhamento/diario_de_bordo.md` (legado, sessão #020). Canônico definido como `governance/operational-memory/`.
- **`atualizar_ecossistema.py` criado:** Script interativo unificado que ao fim de qualquer ação pergunta se o usuário deseja (1) registrar no Diário de Bordo e (2) atualizar o Manual com nova entrada no Changelog. Suporta modo CLI com flags `--feature` e `--sessao`.
- **Manual v8.0:** Atualizado com changelog v7.1 (Centralização de Specs), v8.0 (Protocolo de Atualização Contínua) e nova Seção 13 (Protocolo com tabela de gatilhos e instruções de uso).

**Decisões arquiteturais:**
- O Diário de Bordo é o único arquivo canônico em `governance/operational-memory/diario_de_bordo.md`.
- Toda feature entregue deve ser registrada no diário com: número de sessão, data, agente, foco e lista de entregas.
- O `atualizar_ecossistema.py` pode ser invocado standalone ou como hook de outros scripts.

**Próximos passos:**
- Arquivar `shared/planning_docs/acompanhamento/diario_de_bordo.md` (legado)
- Executar `validate_ecosystem.py` para confirmar consistência geral
- Integrar `atualizar_ecossistema.py` como hook opcional em `lifecycle_manager.py` e `governance_snapshot.py`

---

### Sessão #034 — 2026-05-22
**Agente:** Antigravity (IA)
**Foco:** Governança Avançada, Guardrails, TDD e Arquitetura Documental

**O que foi feito:**
- **Pipeline de Ingestão de Conhecimento:** Estabilizado o ingestor de PDFs (Livros) para múltiplos providers no ChromaDB, corrigindo o erro crítico que causava perda de dados na movimentação de arquivos.
- **Camada de Guardrails:** Criado o módulo `guardrails.py` inspirado no livro "Engenharia de Prompts II", implementando a Defesa em Sanduíche, Validação de Input (Prompt Injection) e Output (Vazamento de dados).
- **Code Review Agent (Anti-Vibe Coding):** Desenvolvido primeiro como script Python e depois **migrado para uma Skill Nativa** global. Ele usa a metodologia de Engenharia de Software (SRP, Clean Code, Try/Except) para revisar e consertar arquivos automaticamente via LLM.
- **TDD Orchestrator:** Implementada a automação `tdd_orchestrator.py` que aplica "Isolamento de Monorepo" (DevOps Loop). Ele entra em cada pasta `PRJ-*` isoladamente, executa o Pytest, e salva um Laudo de TDD rigoroso na pasta `governance/tdd/`.
- **Correção da Infraestrutura de Testes:** Resolvidos problemas de rotas e importações no monorepo, instaladas dependências (`langchain-neo4j`, `langchain-chroma`) e ajustados os scripts de integração (PRJ-02 e PRJ-03) para não quebrarem o pipeline do Pytest.

**Decisões Arquiteturais:**
- O Agente de Code Review tornou-se uma Skill Global para flexibilidade de refatoração imediata em qualquer repositório.
- Decidido que a documentação técnica dos RAGs (BMAD/SDD) **NÃO** ficará espalhada pelas pastas dos projetos, mas sim orquestrada de forma centralizada em `docs/architecture/PRJ-XX_SDD.md`.

**Próximos passos (Ação Imediata):**
- Desenvolver o `architecture_orchestrator.py` para gerar as documentações no formato SDD/Mermaid e popular a pasta `docs/architecture/`.

---

### Sessão #033 — 2026-05-13
**Agente:** Antigravity (Gemini)
**Foco:** Governança e Limpeza de Backlog (Jira)

**O que foi feito:**
- **Limpeza de Backlog**: Identificadas e resolvidas 6 tasks órfãs que permaneciam em `Backlog` ou `In Progress` apesar dos projetos estarem concluídos.
- **Consistência Jira**: Movidas GARE-75, GARE-80, GARE-82, GARE-85, GARE-86 e GARE-87 para `Done` com notas técnicas detalhadas.
- **Correção de Mapeamento**: Identificado que o Epic real do PRJ-01 é GARE-2 (GARE-1 era um épico duplicado/vazio). Documentação sincronizada para apontar para GARE-2.
- **Bugfix no Validador**: Identificada a causa raiz que permitiu o erro: o script `validate_ecosystem.py` usava endpoints obsoletos da API do Jira (`/search`), mascarando erros 410 (Gone). Atualizados todos os scripts (`validate_ecosystem.py`, `jira_sync.py`, `fix_*.py`, etc.) para o endpoint atual correto (`/search/jql`) com validação rigorosa de código HTTP.
- **Validação Geral Rigorosa**: Executado `validate_ecosystem.py` agora perfeitamente integrado e com sucesso real. Backlog está 100% limpo.

**Decisões:**
- Projetos concluídos devem ter 0 tasks pendentes no Jira para manter a integridade do portfólio.
- O Epic GARE-1 foi descontinuado em favor do GARE-2 na documentação oficial (RLM/Registry).

---

### Sessão #032 — 2026-05-11
**Agente:** Antigravity
**Foco:** Correções de consistência pós-auditoria (Claude)

**O que foi feito:**
- Sessão automática #019 (fora de ordem, data 08/mai) renomeada para #016
- Bloco Orientações verificado contra Jira real e fechado com ---
- Seção 2 do Manual corrigida: planning_docs com subpastas ecossistema/ e acompanhamento/
- README.md da raiz substituído por página de apresentação do portfólio GIULIA AI
- Screenshot do comentário automático Jira salvo em docs/assets/

**Verificação Jira:**
- Estado verificado via lifecycle_manager e jira_manager antes de qualquer edição
- validate_ecosystem.py executado — ✅ ecossistema CONSISTENTE

**Decisões:**
- Entradas automáticas com número conflitante são renumeradas, nunca deletadas
- README.md da raiz deve apresentar o portfólio, nunca documentação de infra interna

---

### Sessão #031 — 2026-05-10
**Agente:** Antigravity (Opus)  
**Foco:** Correção Estrutural — Auditoria Pós-Análise

**O que foi feito:**
- **Jira — Subtasks duplicadas**: Auditados todos os épicos GARE. Encontradas e removidas dezenas de subtasks duplicadas geradas por uma falha de idempotência no script de sincronização.
- **Jira — Estimativas zeradas**: Corrigidas dezenas de tasks com `Original Estimate: 0m` usando `projetos.yaml` como fonte de verdade.
- **Documentação sincronizada**: Atualizados status.md, contexto_rlm.md e diario_de_bordo.md para refletir o estado real dos projetos com keys GARE corretas.
- **README.md**: Atualizado com status corretos e modelo LLM correto.
- **Prevenção**: Scripts `fix_duplicate_subtasks.py` e `fix_estimates.py` criados. Validação remota adicionada no `jira_sync.py`. Numeração anti-colisão no `atualizar_diario.py`.

**Scripts criados:**
- `infra/core/fix_duplicate_subtasks.py` — Audita e remove subtasks duplicadas
- `infra/core/fix_estimates.py` — Corrige estimativas zeradas via YAML

**Decisões tomadas:**
- Todo épico duplicado por falha de sincronização é mantido por histórico em vez de deletado, com a divergência documentada.

---

### Sessão #029 — 2026-05-08
**Agente:** Antigravity (IA)  
**Foco:** Governança de Encerramento de Projeto

**O que foi feito:**
- **Checklist de Governança**: Implementação do script `governance_snapshot.py` para salvar o histórico técnico dentro da pasta de cada projeto ao ser encerrado.

**Decisões tomadas:**
- Adotada a técnica de "Governance Snapshot" para descentralizar o histórico técnico e facilitar manutenções futuras isoladas.
- Reforço dos guardrails de diretórios no `start_project.py`.

---

### Sessão #028 — 2026-05-08
**Agente:** Antigravity (IA)  
**Foco:** Criação do GARE Observatory (Telemetria do Ecossistema)

**O que foi feito:**
- **GARE Observatory**: Criação da infraestrutura de telemetria em `infra/lib/observatory.py` com persistência em JSON, reutilizável por qualquer projeto do ecossistema para medir performance.
- **Stress Test**: Execução de 10 rodadas consecutivas para benchmark de performance do mecanismo de telemetria.

**Decisões tomadas:**
- Uso de caminhos absolutos baseados no root para evitar quebras de logs em diferentes CWDs.
- Centralização de métricas em um arquivo JSON único por ecossistema.

---

### Sessão #026 — 2026-04-08
**Agente:** Gemini  
**Foco:** Fundação do Ecossistema

**O que foi feito:**
- Criada a estrutura raiz de diretórios: `DEV/`, `planning_docs/`, `ARTIGOS/`, `SOURCE/`, `LOGS/`
- Criado script `jira_sync.py` que popula o Jira com épicos e tasks automaticamente
- Definido sistema de labels no Jira (`HUMAN`, `AGENT-AI`) para atribuição de responsabilidades
- Integrado com o Jira Cloud via API REST v2

**Decisões tomadas:**
- Nomenclatura de projetos: `PRJ-XX_Nome_Do_Projeto`
- Labels automáticas: Planejamento/Doc → HUMAN, Setup/Pipeline → AGENT-AI, Validação → ambos

---

### Sessão #024 — 2026-04-15
**Agente:** Gemini → Claude  
**Foco:** Documentação Conceitual Padrão de Projeto

**O que foi feito:**
- Criado o padrão de documento `ideia.md` — visão conceitual obrigatória por projeto

**Decisões tomadas:**
- `ideia.md` fica em `planning_docs/` (junto ao implementation plan), nunca dentro de `DEV/`

---

### Sessão #023 — 2026-04-15
**Agente:** Claude  
**Foco:** Automação Ágil Agent + Jira

**O que foi feito:**
- Refatorado `atualizar_tarefa.py`: de script interativo para CLI 100% automatizável
- Novo script aceita 3 status: `selected`, `in_progress`, `done`
- Implementado dicionário bilíngue (PT/EN) para mapear transições do Kanban
- Adicionado parâmetro `--nota` para anexar relatórios técnicos como comentários
- Criado `jira_helper.py` para consultar issues e transições
- Criado workflow oficial `.agents/workflows/padrao_desenvolvimento_jira.md`
- Testado com sucesso: RAG-190 movido de In Progress → Done automaticamente

**Decisões tomadas:**
- Fluxo Kanban: Backlog → Selected → In Progress → Done
- Agente move cards silenciosamente via CLI ao receber Issue Key do usuário
- Notas técnicas são registradas como comentários no Jira automaticamente
- Workflow com `// turbo` permite execução automática sem aprovação manual

**Jira Issues tocadas:**
- RAG-190: Movida para Done (definições de estrutura e padrões documentadas)

---

### Sessão #022 — 2026-04-16
**Agente:** Claude  
**Foco:** Documentação Completa e Replicável

**O que foi feito:**
- Criado `planning_docs/MANUAL_DO_ecossistema.md` — documento mestre com toda a estrutura, convenções, ferramentas, workflow e checklist de replicação
- Criado `planning_docs/diario_de_bordo.md` — este documento, para garantir continuidade entre diferentes agentes de IA
- Incluído Changelog versionado (v1.0 → v1.5) no Manual
- Incluído Status Geral do Portfólio e Registro cronológico de sessões neste diário

**Decisões tomadas:**
- Todo novo ajuste de padrão deve ser registrado no Changelog do Manual (Seção 10)
- Toda sessão de trabalho relevante deve gerar uma entrada no Diário de Bordo
- Agentes de IA devem ler este diário + o Manual antes de iniciar qualquer trabalho
- O Diário de Bordo é o mecanismo oficial de "handoff" entre LLMs diferentes

**Próximos passos sugeridos:**
- Iniciar o desenvolvimento técnico real do primeiro projeto do portfólio, atacando as tasks do respectivo Épico no Jira seguindo a sequência: Estratégia de Dados → Pipeline Engine → Comunicação LLM → Validação

---

### Sessão #021 — 2026-04-16
**Agente:** Claude  
**Foco:** Adoção do Padrão RLM (Recursive Language Model)

**O que foi feito:**
- Pesquisado e analisado o conceito de RLM (Recursive Language Model) a partir da referência do vídeo do Sandeco
- Criado `planning_docs/contexto_rlm.md` — snapshot de 1 página como porta de entrada obrigatória para qualquer LLM nova
- Criado `planning_docs/.contexto_navegacao.md` — índice inteligente "Se precisa de X, leia Y"
- Atualizado `MANUAL_DO_ecossistema.md` com nova Seção 11 (Padrão RLM) + Changelog v1.7
- Atualizado `.agents/workflows/padrao_desenvolvimento_jira.md` com hierarquia RLM de 5 camadas na Seção 0
- Mapa de diretórios do Manual atualizado com os novos arquivos

**Decisões tomadas:**
- Padrão RLM adotado formalmente como filosofia de gerenciamento de contexto
- Hierarquia de leitura em 5 camadas: CONTEXTO_RLM → DIARIO → MANUAL → NAVEGAÇÃO → Docs do projeto
- `contexto_rlm.md` é o primeiro arquivo que qualquer LLM deve ler (snapshot de 30 segundos)
- `.contexto_navegacao.md` funciona como índice de redirecionamento rápido
- Regra RLM: "Não leia tudo de uma vez — comece pelo nível mais compacto e aprofunde sob demanda"

**Referências:**
- [Vídeo Sandeco — RLM (Contexto Infinito)](https://www.youtube.com/watch?v=AALTWpRyDGs)
- Paper original: MIT CSAIL (arXiv:2512.24601)

**Próximos passos sugeridos:**
- Iniciar o desenvolvimento técnico real do primeiro projeto do portfólio, atacando as tasks do respectivo Épico no Jira: Estratégia de Dados → Pipeline Engine → Comunicação LLM → Validação

---

### Sessão #020 — 2026-04-16
**Agente:** Claude  
**Foco:** Jira Manager + Sincronização de Todos os Projetos

**O que foi feito:**
- Identificado que a API do Jira usada estava desatualizada (ERA /rest/api/2/search que retornava 410 Gone)
- Corrigido o endpoint para `/rest/api/3/search/jql` (API atual do Jira Cloud)
- Criado script `infra/core/jira_manager.py` - gerenciador completo de épicos e tasks com opções CLI:
  - `--epics`: Lista todos os épicos
  - `--tasks`: Lista todas as tasks
  - `--details KEY`: Ver detalhes de uma issue
  - `--update KEY --summary/--description/--priority/--duedate/--storypoints/--estimate`: Atualiza campos
  - `--move KEY "STATUS"`: Move issue para novo status
  - `--comment KEY "TEXTO"`: Adiciona comentário
  - `--subtasks KEY`: Lista subtarefas
  - `--interactive`: Modo interativo
- Atualizado `infra/config/projetos.yaml` como fonte de verdade única de dados de projeto (descrições, User Stories, critérios de aceite, estimates, story points, due days, labels)
- Criado script `infra/core/sync_all_projects.py` que sincroniza projetos do YAML para o Jira, criado e atualizado em lote todos os épicos e tasks do portfólio ativo à época

**Decisões tomadas:**
- Story Points usa campo `customfield_10016` (Story point estimate) - o campo padrão 10033 não está disponível na tela
- Original Estimate usa campo `timetracking.originalEstimateSeconds`
- O script de sync é idempotente - detecta épicos existentes pela key PRJ-XX no summary
- API do Jira Cloud requer autenticação com email + API token (não senha)

---

### Sessão #019 — 2026-04-27
**Agente:** Claude (Antigravity)
**Foco:** Refatoração de Infra, Alinhamento Teórico e Sincronização Jira/GitHub

**O que foi feito:**
- **Alinhamento Teórico:** Validada toda a arquitetura RLM e o roadmap de 9 estágios contra o livro *"Engenharia de Software para Agentes Inteligentes"* (2026).
- **Novo Ecossistema Jira (GARE):** Migração completa do gerenciamento de tarefas para a nova chave `GARE` (GIULIA AI: RAG Ecosystem).
  - Implementado sistema de prevenção de duplicatas no `sync_all_projects.py`.
  - Sincronizados todos os épicos, tasks e subtasks (total de 94 itens de trabalho).
- **Publicação no GitHub:** Resolvidos problemas de sincronização local (git rebase) e realizado o push oficial do repositório.
- **Refatoração de Pastas:** Removida a pasta redundante `DEV/-`, movendo todo o conteúdo (PRJ-Vanilla_RAG e configs) diretamente para `DEV/` para uma estrutura mais limpa.
- **Atualização de Documentação:** Sincronizado este Diário de Bordo com os últimos acontecimentos.

**Decisões tomadas:**
- Adoção oficial da chave `GARE` no Jira para o ecossistema.
- Flattening da estrutura `DEV/` para evitar caminhos semânticos desnecessários (`DEV/-`).

**Jira Issues tocadas:**
- Todas as issues migradas para o projeto `GARE`.

---

## 🧭 Orientações para o Próximo Agente

> **⚠️ LEIA PRIMEIRO:** Antes deste diário, leia o `contexto_rlm.md`.

**O que fazer ao iniciar uma sessão:**
1. Ler `contexto_rlm.md` para o estado atual completo.
2. Ler `status.md` para o dashboard dos projetos ativos.
3. Rodar `python3 ecosystem/automation/validate_ecosystem.py` para garantir consistência.
4. Ao encerrar sessão: rodar `validate_ecosystem.py` + atualizar este diário.

