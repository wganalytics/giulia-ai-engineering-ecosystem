# Padrões de Estrutura e Workflow do Ecossistema

Este documento consolida as decisões arquiteturais de processos, pastas e da comunicação estruturada entre o desenvolvedor (ou agente IA) e o rastreamento de tarefas no Jira para o **GIULIA AI Engineering Ecosystem**.

## 1. Estrutura de Diretórios e Planejamento

O desenvolvimento ocorre subdividido pela clareza do escopo de atuação.
- **`governance/`**: O "coração estratégico" dos projetos. Todo novo projeto deve ter seus "Implementation Plans", "ideia.md" (Visão/Conceitos) e documentações arquiteturais armazenados aqui **antes** da codificação inicial.
- **`DEV/`**: Pasta raiz dos workspaces. Cada projeto possui seu subdiretório (ex: `PRJ-XX_nome_do_projeto`), mantendo `.env`, repositório local e dependências `venv` isolados.
- **`infra/`**: O centro de automação do ecossistema. Concentra os scripts Python em `infra/core/` (ex: `lifecycle_manager.py`, `atualizar_tarefa.py`, `validate_ecosystem.py`) projetados para gerenciar o ciclo de vida Kanban de forma autônoma.

## 2. Padrão de Integração Ágil (Agent/Jira Flow)

O modelo dinâmico definido exige o cruzamento inteligente entre Agente IA e o Jira Kanban do usuário sem interrupção humana em botões de UI web. 

### Regras de Workflow:
1. **O Gatilho:** Antes de iniciar a codificação ou o detalhamento de qualquer etapa técnica estipulada no *Implementation Plan*, o desenvolvedor/usuário invoca a tarefa informando sua Issue Key. Exemplo: *"Temos que fazer a GARE-190"*.
2. **"Selected for Development":** Imediatamente, o Agente assume a demanda, e opcionalmente transiciona a tarefa provisoriamente para Selecionado.
3. **"In Progress":** Ao acatar a ordem de ação no prompt, o Agente invoca autonomamente via CLI o script `atualizar_tarefa.py` migrando para a coluna **In Progress**. O desenvolvimento do código/plano então começa localmente.
4. **"Done", Git Commit e Divulgação (Marketing):** Assim que a tarefa for finalizada localmente e **passar em todos os testes TDD**, o agente DEVE obrigatoriamente:
   - Atualizar os arquivos de gestão local (`projects.json` e afins).
   - Criar um **Roteiro de Teste Manual** (`roteiro_teste_manual.md`) na pasta do projeto, contendo passos claros para validação humana via UI ou API.
   - Elaborar um artigo/post para o LinkedIn na pasta `ARTIGOS/` focado em mostrar a engenharia de software e atrair recrutadores (utilizando técnicas avançadas de copywriting).
   - Realizar o commit das alterações no Git (`git add . && git commit -m "..."`).
   - Enviar as alterações (`git push origin main`).
   - Só então encerrar a tarefa enviando atrelada uma nota técnica da execução para o Jira, consolidando o ciclo.

5. **Protocolo de Encerramento (Wrap-up):** Sempre que o usuário usar gatilhos como *"vamos finalizar"* ou *"encerrar por hoje"*, o Agente DEVE executar a seguinte ordem estrita de salvamento:
   1. Atualizar os controles internos (ex: `projects.json`, arquivos `.md` pendentes).
   2. Sincronizar o Jira via script (`atualizar_tarefa.py`) com notas técnicas das atividades do dia.
   3. Realizar o Commit Semântico das alterações seguindo as melhores práticas do Git (`git add . && git commit -m "chore/feat/fix: descritivo"`).
   4. Efetuar o Push (`git push origin main`) para garantir que o *Save State* na nuvem esteja intacto para a próxima sessão.

### Como a IA invoca a automação
A execução é efetuada através do CLI no orquestrador de ciclo de vida:
```bash
# Iniciar Épico (cascateia tasks para Selected)
python3 infra/core/lifecycle_manager.py start-project <EPIC-KEY>

# Iniciar Task (cascateia subtasks para Selected)
python3 infra/core/lifecycle_manager.py start-task <TASK-KEY>

# Conclusão (com auto-promoção recursiva do pai)
python3 infra/core/lifecycle_manager.py complete <ISSUE-KEY>

# Visualizar Board Visual
python3 infra/core/lifecycle_manager.py status <EPIC-KEY>
```

## 3. Princípios de Desenvolvimento de Sistemas e Codificação
O ecossistema adota diretrizes rigorosas visando manutenibilidade, resiliência e privacidade:

- **Privacy-first / 100% On-Premise**: os projetos do ecossistema rodam *Ollama* localmente por padrão. Dependências da cloud global devem ser ignoradas dentro deste ecossistema para o core lógico dos modelos, salvo exceção justificada e documentada por projeto.
- **Proteção de Credenciais**: O arquivo `.env` de configuração nunca é commitado. Há uso imperativo do `.env.template` como referência.
- **Manutenção Preventiva (Design Patterns)**: Conforme o Capítulo 4 de nossa fundação de Engenharia de Software, exigimos:
  - **Padrão Strategy**: Desacoplar a lógica central do modelo subjacente. Trocas de LLMs ou estratégias de recuperação (Web vs Vector) devem ocorrer via injeção sem alterar o orquestrador principal.
  - **Padrão Observer**: Garantir telemetria e observabilidade sem poluir o núcleo. O fluxo de pensamentos (Thought Trace), métricas e guardrails comportam-se como *Observers* ouvindo eventos do agente.
- **Cobertura de Testes Unitários (TDD)**: O código não é considerado "Pronto" sem testes. Exigimos o uso de `pytest` para testes modulares das classes lógicas centrais (core), visando validar comportamento isolado das ferramentas e do agente, evitando falhas silenciosas.
- **Spec-Driven Development (SDD)**: Projetos complexos exigem a criação de um documento formal de especificação (`PRJ-XX-spec.md`) antes do início do plano técnico.
