# SDD — GARE-149: Schema de Grafo Unificado (Graph Schema)

**Versão:** 1.0  
**Issue Jira:** GARE-149  
**Autor:** Wemerson (RLM Session #009)  
**Data:** 2026-08-05  
**Status:** Draft  
**Fundamentação Científica:** Liu et al., 2024 — *"CodexGraph: Bridging Large Language Models and Code Repositories via Code Graph Databases"* ([arXiv:2408.03910](https://arxiv.org/abs/2408.03910))

---

## 1. Contexto e Problema

### 1.1 A Necessidade de Padronização

O ecossistema GARE possui múltiplos projetos de IA que lidam com estruturas em grafo:
1. **PRJ-XX (indexador documental):** Armazena o grafo documental de livros e referências no Neo4j.
2. **GARE-141 (CodeCompass - AST):** Armazena o grafo de dependências do código fonte do próprio repositório para auxiliar na navegação da IA.

Atualmente, se implementarmos essas duas frentes de forma isolada, cada uma usará seu próprio conjunto de nós, propriedades e arestas no Neo4j. Isso impede a criação de ferramentas transversais (ex: uma busca na IA que cruze a referência do livro da pasta `/shared/` com o código fonte que implementa aquele conceito no `/dev/`).

---

## 2. Objetivo

Definir o **Schema de Grafo Unificado** em `shared/schemas/graph_schema.cypher`. Esse schema servirá como contrato arquitetural estrito para qualquer indexação em grafo (seja de código ou de documentos) dentro do ecossistema.

---

## 3. Especificação do Schema (Nós e Relacionamentos)

```text
               ┌───────────────┐
               │   :Project    │
               └───────────────┘
                       ▲
                       │ :BELONGS_TO
                       │
 ┌──────────┐    :DEFINES    ┌──────────┐
 │  :Class  │◄───────────────│  :File   │
 └──────────┘                └──────────┘
      │                           │
      │ :INHERITS                 │ :IMPORTS
      ▼                           ▼
 ┌──────────┐                ┌──────────┐
 │  :Class  │                │  :File   │
 └──────────┘                └──────────┘
```

### 3.1 Definição dos Nós (Nodes)

#### 1. `(:Project)`
Representa um projeto cadastrado no ecossistema (RAG, MCP, etc.).
- `key`: String (ID único, ex: "PRJ-XX")
- `name`: String (ex: "Nome do Projeto")
- `domain`: String (ex: "rag", "mcp")
- `status`: String (ex: "Concluído", "Desenvolvimento")

#### 2. `(:File)`
Representa qualquer arquivo físico do repositório (código, markdown, pdf).
- `path`: String (caminho relativo único a partir do root, ex: "dev/dominio/PRJ-XX/app.py")
- `filename`: String (ex: "app.py")
- `type`: String (ex: "code", "documentation")
- `language`: String (ex: "python", "markdown", "javascript")

#### 3. `(:Class)`
Representa uma classe estruturada de programação.
- `name`: String (ex: "GraphRetriever")
- `file_path`: String (link de origem)

#### 4. `(:Function)`
Representa uma função ou método isolado.
- `name`: String (ex: "get_neighborhood")
- `file_path`: String

#### 5. `(:DocSection)`
Representa um fragmento/chunk de documento textual (usado na indexação documental em grafo).
- `id`: String (uuid do chunk)
- `content`: String (conteúdo do texto)
- `source_file`: String

---

### 3.2 Definição dos Relacionamentos (Edges)

| Relação | Origem ──► Destino | Significado / Regra |
|---|---|---|
| `[:BELONGS_TO]` | `(:File)` ──► `(:Project)` | O arquivo pertence à estrutura física daquele projeto. |
| `[:IMPORTS]` | `(:File)` ──► `(:File)` | O arquivo de origem importa dependências do arquivo de destino. |
| `[:INHERITS]` | `(:Class)` ──► `(:Class)` | Relação de herança orientada a objetos (classe base). |
| `[:DEFINES]` | `(:File)` ──► `(:Class)` ou `(:Function)` | O arquivo contém a definição da classe ou função. |
| `[:REFERENCES]` | `(:DocSection)` ──► `(:File)` | O trecho de documentação cita ou descreve aquele arquivo ou código. |

---

## 4. Arquivos a Serem Criados

1. **`shared/schemas/graph_schema.cypher`** — O arquivo contendo as instruções DDL do Neo4j (criação de restrições de unicidade e índices).

```cypher
// Restrições de Unicidade
CREATE CONSTRAINT UNIQUE_PROJECT_KEY IF NOT EXISTS
FOR (p:Project) REQUIRE p.key IS UNIQUE;

CREATE CONSTRAINT UNIQUE_FILE_PATH IF NOT EXISTS
FOR (f:File) REQUIRE f.path IS UNIQUE;

// Índices de busca rápida
CREATE INDEX INDEX_CLASS_NAME IF NOT EXISTS
FOR (c:Class) ON (c.name);
```

---

## 5. Critérios de Aceite

- [ ] **CA-1:** O arquivo `shared/schemas/graph_schema.cypher` é criado com a sintaxe Cypher válida.
- [ ] **CA-2:** O `ast_extractor.py` (GARE-141) consome e respeita estritamente esse schema ao persistir dependências de código no Neo4j.
- [ ] **CA-3:** O indexador documental (PRJ-XX) consome e respeita esse schema ao persistir referências de documentação.
- [ ] **CA-4:** O banco de dados Neo4j local possui as constraints de unicidade para `Project.key` e `File.path` ativas.

---

## 6. Referências

- Liu, Z. et al. (2024). *CodexGraph: Bridging Large Language Models and Code Repositories via Code Graph Databases.* arXiv:2408.03910. [PDF](https://arxiv.org/abs/2408.03910)
- Issue Jira: [GARE-149](https://wganalytics.atlassian.net/browse/GARE-149)
