# 📑 Padrão de Métricas e Observabilidade - Ecossistema GARE

Este documento define os KPIs e a metodologia de monitoramento para garantir a qualidade, performance e transparência de todos os projetos RAG do portfólio.

## 1. KPIs de Qualidade (RAG Triad)

Para medir a eficácia da recuperação e geração, utilizaremos o framework baseado no **RAGAS**:

| KPI | Descrição | O que mede |
|-----|-----------|------------|
| **Faithfulness** | Fidelidade | Se a resposta contém apenas fatos presentes no contexto. |
| **Answer Relevance** | Relevância da Resposta | Se a resposta atende à pergunta sem redundâncias. |
| **Context Precision** | Precisão do Contexto | Se os documentos recuperados estão no topo do ranking. |
| **Context Recall** | Recall do Contexto | Se todos os fatos necessários foram recuperados. |

## 2. Métricas de Performance (Latency & Resource)

Essas métricas são capturadas em tempo real durante a execução:

- **TTFT (Time to First Token)**: Latência percebida (ms).
- **Total Latency**: Tempo total do pipeline (s).
- **Latency Breakdown**:
    - `t_retrieve`: Tempo de busca no banco.
    - `t_rerank`: Tempo de re-rankeamento.
    - `t_generate`: Tempo de inferência do LLM.
- **Tokens per Second (TPS)**: Vazão do modelo local.

## 3. Implementação Técnica

### Módulo `GARE Observatory`
Localizado em `infra/lib/observatory.py`, este módulo fornece:
- **`MetricsTracker`**: Classe singleton para acumular métricas por sessão.
- **`@track_step`**: Decorator para medir o tempo de execução de componentes específicos.
- **`BenchmarkReport`**: Gerador de relatório para visualização no Streamlit.

## 4. Benchmarking
Cada projeto deve conter um teste de benchmark que processa um conjunto de queries "Golden Set" e reporta os scores médios.
