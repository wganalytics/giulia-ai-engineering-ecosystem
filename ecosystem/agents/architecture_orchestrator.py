import os
import json
from pathlib import Path
from datetime import datetime

# Estrutura do Template Global (BMAD + SDD + TDD)
TEMPLATE_BMAD_SDD_TDD = """# {project_name} - Architecture & Spec

> **Padrão Oficial:** BMAD (Baseline Markdown Architecture) + SDD (Spec-Driven) + TDD (Test-Driven)
> **Última Atualização:** {date}

---

## 1. 🏗️ BMAD (Baseline Architecture)
*Visão de alto nível de como os componentes se integram.*

```mermaid
graph TD
    A[Usuário/Frontend] --> B[API Router]
    B --> C[Engine Principal]
    C --> D[(Vector Store)]
    C --> E[LLM Inference]
```

## 2. 📝 SDD (Spec-Driven Development)
*Especificação de comportamento, regras de negócio e guardrails.*

- **Objetivo Principal:** [Descrever o propósito do módulo]
- **Restrições (Guardrails):** 
  - Proteção contra Prompt Injection.
  - Anonimização de PII (Lei de Proteção de Dados).
- **Fluxo de Exceções:** 
  - Timeout da LLM deve retornar HTTP 503 com fallback.

## 3. 🧪 TDD (Test-Driven Development)
*Garantia de Qualidade e Cobertura (Red-Green-Refactor).*

- **Casos de Teste Obrigatórios:**
  - `test_engine_initialization`: O motor deve carregar com sucesso.
  - `test_guardrail_block`: Entradas maliciosas devem ser barradas imediatamente.
  - `test_integration_flow`: O RAG completo deve recuperar documentos e responder.
- **Status Atual (via TDD Orchestrator):** A ser validado pelo pipeline de CI/CD.
"""

def generate_docs():
    root_dir = Path(__file__).resolve().parent.parent.parent
    projects_dir = root_dir / "dev" / "rag"
    docs_dir = root_dir / "docs" / "architecture"
    
    # Criar pasta se não existir
    docs_dir.mkdir(parents=True, exist_ok=True)
    
    print("🤖 Iniciando Architecture Orchestrator (BMAD + SDD + TDD)...")
    
    # Pegar todos os PRJ-*
    projects = sorted([d for d in projects_dir.iterdir() if d.is_dir() and d.name.startswith("PRJ-")])
    
    for prj in projects:
        project_name = prj.name
        output_file = docs_dir / f"{project_name}_SDD.md"
        
        # Preencher template
        content = TEMPLATE_BMAD_SDD_TDD.format(
            project_name=project_name,
            date=datetime.now().strftime("%Y-%m-%d")
        )
        
        # Salvar documento
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(content)
            
        print(f"✅ Documentação gerada: {output_file.relative_to(root_dir)}")
        
    print("\n🎉 Todas as especificações geradas com sucesso na pasta docs/architecture/ !")

if __name__ == "__main__":
    generate_docs()
