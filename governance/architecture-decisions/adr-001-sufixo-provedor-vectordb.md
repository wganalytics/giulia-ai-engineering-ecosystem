# ADR-001: Sufixo do Provedor no VectorDB

* **Status:** Approved
* **Data:** 2026-08-05
* **Autor:** Wemerson
* **Jira:** GARE-152

---

## 1. Contexto
No ecossistema RAG/AI, diferentes modelos de linguagem (LLMs) geram embeddings com diferentes tamanhos de vetores (por exemplo, `nomic-embed-text` gera 768 dimensões, enquanto modelos OpenAI geram 1536 dimensões). Se o sistema tentar reinserir ou recuperar dados usando uma coleção ChromaDB genérica após alternar o provedor de LLM no arquivo `.env`, ocorrerá um erro fatal de "Dimensionality Mismatch" (incompatibilidade de dimensionalidade).

## 2. Decisão
Adotamos como regra de arquitetura obrigatória que todas as coleções persistidas e recuperadas no ChromaDB/VectorDB devem possuir o sufixo do provedor correspondente (ex: `knowledge_books_openai`, `knowledge_books_gemini`). É proibido o uso de coleções sem sufixo ou com nomes genéricos estáticos no código de recuperação.

## 3. Consequências
* **Positivo:** Evita erros de colisão de dimensionalidade e falhas de runtime ao alternar provedores de embeddings/LLMs.
* **Negativo/Dívida:** Aumenta a complexidade de mapeamento de coleções nas configurações dos retrievers.
