import os
import sys
import time
from typing import List

# Adiciona o diretório raiz ao path para importar infra e src
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'DEV', 'prj-xx_nome_do_projeto')))

from src.core.hybrid_retriever import HybridEngine
from src.core.fusion_engine import FusionEngine
from src.core.reranker import Reranker

def run_stress_test(num_tests=10):
    print(f"🚀 Iniciando Teste de Stress: {num_tests} execuções consecutivas...\n")
    
    # Inicializa o sistema
    hybrid = HybridEngine()
    fusion = FusionEngine(hybrid)
    reranker = Reranker(tracker=hybrid.tracker)
    
    # Ingestão de teste
    text = "O Ecossistema GARE é focado em automação de engenharia de IA. Este projeto de exemplo foca em busca híbrida, fusion e rerank."
    hybrid.ingest([text])

    query = "Como este projeto melhora a precisão da busca?"
    
    for i in range(num_tests):
        print(f"🔄 Teste {i+1}/{num_tests}...", end=" ", flush=True)
        start_time = time.perf_counter()
        
        hybrid.tracker.start()
        # Pipeline completo
        fusion_results = fusion.hybrid_fusion_retrieve(query)
        final_results = reranker.rerank(query, fusion_results)
        hybrid.tracker.stop()
        
        duration = time.perf_counter() - start_time
        print(f"✅ Concluído em {duration:.2f}s")
        
    print(f"\n✨ Teste de Stress finalizado. Verifique os logs em infra/logs/rag_metrics.json")

if __name__ == "__main__":
    run_stress_test(10)
