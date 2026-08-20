# SDD — GARE-140 (+ GARE-141/142/143/144): CodeCompass — Navegação por Grafo Estrutural

**Versão:** 1.0  
**Issues Jira:** GARE-140 (Epic) → GARE-141, 142, 143, 144 (Sub-tasks)  
**Autor:** Wemerson (RLM Session #009)  
**Data:** 2026-08-05  
**Status:** Draft  
**Fundamentação Científica:**
- Xia et al., 2025 — *"CodeCompass: Navigating the Navigation Paradox"* ([arXiv:2602.20048](https://arxiv.org/abs/2602.20048))
- Liu et al., 2024 — *"CodexGraph: Bridging LLMs and Code Repositories via Code Graph Databases"* ([arXiv:2408.03910](https://arxiv.org/abs/2408.03910))

---

## 1. Contexto e Problema

### 1.1 O Navigation Paradox (arXiv:2602.20048)

O paper *CodeCompass* define o problema central que esta SDD resolve:

> *"Agents perform poorly not due to context limits, but because navigation and retrieval are fundamentally distinct problems."*

Testes em repositório FastAPI de produção com 258 trials automatizados revelaram:

| Método | Tarefas Ocultas (G3) | Impacto |
|---|---|---|
| Agente vanilla (sem ferramenta) | 76.2% | Baseline |
| BM25 / Vector Search (RAG) | 78.2% | +2.0pp |
| **CodeCompass (Grafo estrutural)** | **99.4%** | **+23.2pp** |

O ponto crítico: **58% dos agentes com acesso ao grafo fizeram zero chamadas à ferramenta**. O problema não é a ferramenta — é que a IA não a usa sem ser explicitamente instruída.

### 1.2 A Taxonomia de Tarefas (G1/G2/G3)

O paper classifica tarefas de desenvolvimento em 3 categorias:

- **G1 — Semântica:** Arquivo encontrável por keyword/embedding. Ex: *"altere a mensagem de erro de autenticação"*. RAG resolve.
- **G2 — Estrutural:** Arquivo encontrável seguindo imports explícitos. RAG + tentativa de navegação resolve.
- **G3 — Dependência Oculta:** Arquivo crítico não tem sobreposição lexical com a tarefa. Apenas travessia de grafo encontra. Ex: *"refatore o sistema de autenticação"* → arquivo de configuração de roles em camada totalmente diferente.

**Nosso ecossistema é majoritariamente G3:** projetos com múltiplas camadas, heranças entre classes RAG, e dependências cruzadas entre módulos de agents, observability e governance.

### 1.3 CodexGraph (arXiv:2408.03910)

O paper *CodexGraph* fornece a implementação de referência:

> *"By leveraging the structural properties of graph databases and the flexibility of the graph query language, CodexGraph enables the LLM agent to construct and execute queries, allowing for precise, code structure-aware context retrieval."*

Ele valida que um banco de grafos com interface de query (Neo4j + Cypher) é mais preciso que similarity-based retrieval para repositórios inteiros.

---

## 2. Objetivo

Construir o **CodeCompass GARE** — uma infraestrutura de navegação por grafo para o ecossistema, composta por 4 camadas correspondentes às sub-tasks do épico:

```
GARE-141 → Data Layer    → Extração AST + Neo4j
GARE-142 → Service Layer → MCP Server
GARE-143 → Governance    → Prompt Engineering
GARE-144 → Observability → Telemetria do Veto Protocol
```

---

## 3. Arquitetura da Solução

### 3.1 Diagrama de Alto Nível

```
┌────────────────────────────────────────────────────────────┐
│                   CODECOMPASS GARE                         │
│                                                            │
│  ┌──────────────────┐     ┌──────────────────────────┐    │
│  │  GARE-141        │     │  GARE-142                │    │
│  │  AST Extractor   │────►│  MCP Server              │    │
│  │                  │     │  (ecosystem/mcp/codecompass_mcp.py)│    │
│  │  ast.parse()     │     │                          │    │
│  │  IMPORTS         │     │  Tool:                   │    │
│  │  INHERITS        │     │  get_structural_          │    │
│  │  INSTANTIATES    │     │  neighborhood(filepath)  │    │
│  └──────────────────┘     └──────────────────────────┘    │
│          │                          │                      │
│          ▼                          ▼                      │
│  ┌──────────────────┐     ┌──────────────────────────┐    │
│  │  Neo4j           │     │  GARE-143                │    │
│  │  Graph DB        │     │  Prompt Engineering      │    │
│  │                  │     │                          │    │
│  │  (:File)         │     │  CONTEXTO_RLM Regra 12   │    │
│  │  (:Class)        │     │  Checklist-at-END        │    │
│  │  (:Function)     │     │  Forçamento de uso       │    │
│  │  [:IMPORTS]      │     └──────────────────────────┘    │
│  │  [:INHERITS]     │                                      │
│  │  [:INSTANTIATES] │     ┌──────────────────────────┐    │
│  └──────────────────┘     │  GARE-144                │    │
│                            │  Veto Protocol Telemetry │    │
│                            │                          │    │
│                            │  telemetry_aggregator.py │    │
│                            │  evento: veto_protocol   │    │
│                            └──────────────────────────┘    │
└────────────────────────────────────────────────────────────┘
```

---

## 4. GARE-141: Data Layer — AST Extractor & Neo4j

**Localização:** `ecosystem/mcp/ast_extractor.py`

### Especificação Técnica

```python
# Tipos de relações a extrair
RELATION_TYPES = {
    "IMPORTS":      # import X / from X import Y
    "INHERITS":     # class MyClass(BaseClass)
    "INSTANTIATES"  # obj = MyClass()
}

# Schema Neo4j (Cypher)
# Nós
CREATE (:File {path: string, project: string, language: string})
CREATE (:Class {name: string, file_path: string})
CREATE (:Function {name: string, file_path: string, class_name: string})

# Arestas
CREATE (f1:File)-[:IMPORTS]->(f2:File)
CREATE (c1:Class)-[:INHERITS]->(c2:Class)
CREATE (f:Function)-[:INSTANTIATES]->(c:Class)
```

### Comportamento Esperado

1. Recebe `root_path` como argumento.
2. Varre recursivamente todos os arquivos `.py` do repositório.
3. Para cada arquivo, usa `ast.parse()` para extrair `import`, `ImportFrom`, `ClassDef` (bases), e `Call` (instanciações).
4. Persiste os nós e arestas no Neo4j via `neo4j-driver`.
5. É idempotente — segundo run faz `MERGE`, não duplica.

---

## 5. GARE-142: Service Layer — MCP Server

**Localização:** `ecosystem/mcp/codecompass_mcp.py`

### Especificação da Tool Principal

```python
def get_structural_neighborhood(filepath: str, hops: int = 1) -> dict:
    """
    Dado o caminho de um arquivo, retorna sua vizinhança estrutural.
    
    Args:
        filepath: caminho relativo ao root do repositório
        hops: profundidade do grafo (default=1, direto)
    
    Returns:
        {
          "imports": ["/path/a.py", "/path/b.py"],
          "imported_by": ["/path/c.py"],
          "inherits": ["BaseClass em /path/base.py"],
          "inherited_by": ["ChildClass em /path/child.py"],
          "instantiated_in": ["/path/main.py"]
        }
    """
```

### Protocolo MCP

O server expõe via MCP (Model Context Protocol):
- **Tool:** `get_structural_neighborhood`
- **Tool:** `find_files_by_class(class_name: str)`
- **Tool:** `get_dependency_chain(filepath: str, depth: int)`
- **Resource:** `graph_stats` — estatísticas do grafo (nós, arestas, projetos indexados)

---

## 6. GARE-143: Governance Layer — Prompt Engineering

**Crítico:** O paper alerta que 58% dos agentes ignoram a ferramenta de grafo mesmo quando disponível.

### Regra 12 a ser inserida no contexto_rlm.md

```markdown
12. **CodeCompass OBRIGATÓRIO em Tarefas G3:** Para qualquer tarefa de refatoração
    arquitetural, antes de propor qualquer edição de código, VOCÊ DEVE chamar a tool
    `get_structural_neighborhood(filepath)` para cada arquivo envolvido.
    
    Checklist pré-implementação (preencher antes de editar):
    - [ ] Chamei get_structural_neighborhood() para o arquivo principal?
    - [ ] Identifiquei todos os arquivos que o importam?
    - [ ] Verifiquei heranças e classes filhas?
    - [ ] O escopo de impacto está documentado?
    
    Referência: CodeCompass (arXiv:2602.20048) — 58% dos agentes ignoram
    o grafo sem este checklist explícito.
```

---

## 7. GARE-144: Observability — Veto Protocol

### Evento a Capturar

O *Veto Protocol* é definido como: **o grafo encontra um arquivo que o vector search não encontraria.**

```python
# Em telemetry_aggregator.py, novo tipo de evento:
{
    "event_type": "veto_protocol",
    "timestamp": "ISO-8601",
    "task_id": "GARE-XXX",
    "query": "descrição da busca original",
    "vector_result": [],            # o que o RAG retornou (vazio ou errado)
    "graph_result": ["/path/file"], # o que o grafo encontrou
    "file_found": "/path/to/hidden_file.py"
}
```

O dashboard deve exibir a métrica: **"Veto Protocol activations this sprint"** — prova viva de ROI do CodeCompass.

---

## 8. Critérios de Aceite do Épico

- [ ] **CA-1 (GARE-141):** `ast_extractor.py` indexa 100% dos arquivos `.py` do repositório sem erro. Neo4j contém nós para todos os projetos indexados do ecossistema.
- [ ] **CA-2 (GARE-142):** `get_structural_neighborhood("dev/dominio/prj-xx_nome_do_projeto/modulo.py")` retorna os arquivos corretos de imports e heranças.
- [ ] **CA-3 (GARE-143):** Em uma task de refatoração, o agente usa o CodeCompass **antes** de qualquer edição, sem prompt explícito do usuário.
- [ ] **CA-4 (GARE-144):** O dashboard de telemetria exibe a métrica "Veto Protocol" com pelo menos 1 evento registrado após a primeira execução completa.
- [ ] **CA-5 (Integração):** O fluxo completo AST → Neo4j → MCP → Agente funciona end-to-end em menos de 30 segundos para uma query simples.

---

## 9. Referências

- Xia, C. S. et al. (2025). *CodeCompass: Navigating the Navigation Paradox in Agentic Code Intelligence.* arXiv:2602.20048. [PDF](https://arxiv.org/pdf/2602.20048)
- Liu, Z. et al. (2024). *CodexGraph: Bridging Large Language Models and Code Repositories via Code Graph Databases.* arXiv:2408.03910. [PDF](https://arxiv.org/pdf/2408.03910)
- Epic: [GARE-140](https://wganalytics.atlassian.net/browse/GARE-140)
- Sub-tasks: [GARE-141](https://wganalytics.atlassian.net/browse/GARE-141) | [GARE-142](https://wganalytics.atlassian.net/browse/GARE-142) | [GARE-143](https://wganalytics.atlassian.net/browse/GARE-143) | [GARE-144](https://wganalytics.atlassian.net/browse/GARE-144)
- Dependências: GARE-146, GARE-148 (devem ser concluídas primeiro)
