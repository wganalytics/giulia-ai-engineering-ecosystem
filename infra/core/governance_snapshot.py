#!/usr/bin/env python3
"""
🛡️ GIULIA AI: Governance Snapshot Engine v3.0
"The Engineering Knowledge Capsule"

Objetivo: Criar uma cápsula autossuficiente de conhecimento técnico por projeto,
garantindo continuidade operacional, rastreabilidade total (Git/Jira/TDD) 
e handoff otimizado para múltiplos Agentes de IA.
"""

import os
import json
import sys
import re
import subprocess
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any, Optional

# Setup paths
SCRIPT_DIR = Path(__file__).parent
infra_DIR = SCRIPT_DIR.parent
ROOT_DIR = infra_DIR.parent
REGISTRY_PATH = ROOT_DIR / "REGISTRY" / "projects.json"
DIARY_PATH = ROOT_DIR / "governance" / "operational-memory" / "diario_de_bordo.md"
METRICS_PATH = ROOT_DIR / "infra" / "logs" / "rag_metrics.json"

# Security Guardrails (Files to NEVER copy)
SECURITY_BLACKLIST = [
    ".env", "tokens", "secrets", "credentials", "auth.ini", 
    ".sync_state.json", "vector_db", "sqlite", "binary", ".pdf"
]

class GovernanceEngine:
    def __init__(self, project_id: str):
        self.project_id = project_id.upper()
        self.registry = self._load_json(REGISTRY_PATH)
        self.project_data = self.registry.get("projetos", {}).get(self.project_id)
        
        if not self.project_data:
            raise ValueError(f"❌ Projeto {self.project_id} não encontrado no registry.")
            
        self.dev_path = ROOT_DIR / self.project_data["caminho_dev"]
        self.docs_path = ROOT_DIR / self.project_data["caminho_docs"]
        self.context_dir = self.dev_path / "project_context"
        self.context_dir.mkdir(exist_ok=True)
        
        # Metadata
        self.timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    def _load_json(self, path: Path) -> Dict:
        if path.exists():
            with open(path, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {}

    def _get_git_info(self) -> Dict[str, str]:
        """Coleta metadados do Git com segurança."""
        try:
            branch = subprocess.check_output(["git", "rev-parse", "--abbrev-ref", "HEAD"], cwd=ROOT_DIR).decode().strip()
            last_commit = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT_DIR).decode().strip()[:8]
            commit_msg = subprocess.check_output(["git", "log", "-1", "--pretty=%B"], cwd=ROOT_DIR).decode().strip()
            return {
                "branch": branch,
                "commit": last_commit,
                "msg": commit_msg
            }
        except:
            return {"branch": "main", "commit": "N/A", "msg": "Git info not available"}

    def _filter_diary(self) -> str:
        """Filtra o diário global apenas para o projeto ativo, reduzindo ruído."""
        if not DIARY_PATH.exists(): return "Nenhum histórico global localizado."
        
        with open(DIARY_PATH, 'r', encoding='utf-8') as f:
            content = f.read()
        
        sessions = re.split(r'(?=### Sessão #)', content)
        relevant = [s for s in sessions if self.project_id in s]
        
        if not relevant: return "> Nenhuma sessão específica registrada para este projeto no diário global."
        
        return "\n---\n".join(relevant)

    def _get_metrics_analysis(self) -> Dict[str, Any]:
        """Analisa métricas do GARE Observatory ou reporta gaps."""
        if not METRICS_PATH.exists():
            return {"status": "insufficient", "gaps": ["avg_latency", "retrieval_latency", "generation_latency"]}
        
        metrics = []
        with open(METRICS_PATH, 'r', encoding='utf-8') as f:
            for line in f:
                try:
                    entry = json.loads(line)
                    # Filtra métricas que podem estar relacionadas ao projeto (simulação por data/contexto)
                    metrics.append(entry)
                except: continue
        
        if not metrics:
            return {"status": "insufficient", "gaps": ["all_metrics"]}
            
        last = metrics[-1]
        summary = {
            "status": "available",
            "last_total_latency": last.get("total_latency", "N/A"),
            "breakdown": {k: v for k, v in last.items() if k != "timestamp" and k != "total_latency"},
            "timestamp": last.get("timestamp", "N/A")
        }
        return summary

    def _preserve_manual_content(self, filename: str, default_content: str) -> str:
        """Tenta preservar conteúdo manual adicionado anteriormente pelo usuário."""
        file_path = self.context_dir / filename
        if not file_path.exists():
            return default_content
        
        # Se o arquivo existe, podemos tentar uma lógica de merge ou apenas retornar o novo se for auto-gerado
        # Para v3.0, vamos sobrescrever as seções automáticas e manter seções marcadas como [MANUAL]
        # (Lógica simplificada: se existir, lemos e tentamos identificar seções customizadas)
        return default_content # TODO: Implementar lógica de merge real no futuro

    # --- File Generators ---

    def generate_00_index(self):
        content = f"""# 🛡️ Governance Snapshot: {self.project_id}
> **Snapshot Version:** 3.0 (Engineering Knowledge Capsule)
> **Generation Timestamp:** {self.timestamp}

## 🎯 Purpose
Este snapshot é uma **Cápsula de Conhecimento de Engenharia**. Ele contém todo o contexto operacional, arquitetural e de governança necessário para que um agente (Humano ou IA) assuma o projeto sem dependência total do histórico global.

## 🤖 How an AI Agent Should Use This Snapshot
1. **Read this Index** to understand the project structure.
2. **Read [Operational Memory](01_OPERATIONAL_MEMORY.md)** to understand current state and milestones.
3. **Read [Architecture Log](02_ARCHITECTURE_LOG.md)** to understand the "Why" and Rejected Alternatives.
4. **Read [Maintenance Guide](03_MAINTENANCE_GUIDE.md)** for operational recovery and running tests.
5. **Check [Governance Trace](05_GOVERNANCE_TRACE.md)** for Jira/Git cross-references.
6. **Check [Observability Report](04_OBSERVABILITY_REPORT.md)** for performance gaps.
7. **Only then modify code.**

---
### 📂 Directory Map
- `01_OPERATIONAL_MEMORY.md`: Filtered sessions and handoff notes.
- `02_ARCHITECTURE_LOG.md`: Deep architectural reasoning.
- `03_MAINTENANCE_GUIDE.md`: Disaster recovery and ops.
- `04_OBSERVABILITY_REPORT.md`: Performance telemetry.
- `05_GOVERNANCE_TRACE.md`: Jira/Git traceability.
- `06_LESSONS_LEARNED.md`: Engineering reflection and TDD/SDD insights.
"""
        (self.context_dir / "00_SNAPSHOT_INDEX.md").write_text(content, encoding='utf-8')

    def generate_01_operational_memory(self):
        content = f"""# 🧠 Operational Memory: {self.project_id}

## 🚀 Project Milestones
- [x] Initial Planning (SDD)
- [x] Core Implementation
- [x] TDD Validation
- [x] Final Governance Snapshot

## 📓 Relevant Sessions (Filtered)
{self._filter_diary()}

## 🤝 Agent Handoff Notes
- **Current State:** Estável e validado localmente.
- **Critical Path:** Manter integridade do pipeline principal durante atualizações de dependências.
- **Focus:** [Preencher com o próximo marco/fase deste projeto.]
"""
        (self.context_dir / "01_OPERATIONAL_MEMORY.md").write_text(content, encoding='utf-8')

    def generate_02_architecture_log(self):
        # Tenta herdar dados do implementation plan
        plan_file = next(self.docs_path.glob("*implementation_plan.md"), None)
        plan_content = plan_file.read_text(encoding='utf-8') if plan_file else "Nenhum plano localizado."
        
        content = f"""# 🏗️ Architecture Log: {self.project_id}

## Architecture Overview
Implementação baseada no padrão GIULIA AI Engineering Ecosystem, utilizando Clean Architecture e isolamento por domínio.

## Core Components
- **Engine**: Core logic do domínio do projeto.
- **Retriever/Data Layer**: Interface com a fonte de dados/persistência.
- **Observatory**: Telemetria e métricas.
- **Frontend**: Interface do usuário (ex: Streamlit, API, CLI).

## Key Architecture Decisions
1. **Local-First Execution**: Priorização de execução local (ex: Ollama) para privacidade total de dados, quando aplicável.
2. **[Decisão de Arquitetura]**: [Preencher com a decisão real e sua justificativa.]

## Trade-offs
- **[Trade-off relevante]**: [Preencher com o trade-off real observado no projeto.]

## ❌ Rejected Alternatives (Mandatory)
- **[Alternativa Rejeitada]**: [Preencher com a alternativa considerada e o motivo da rejeição.]

## Risks and Mitigations
- **[Risco identificado]**: [Preencher com a mitigação adotada.]

## Future Evolution
- [Preencher com a evolução futura planejada para este projeto.]
"""
        (self.context_dir / "02_ARCHITECTURE_LOG.md").write_text(content, encoding='utf-8')

    def generate_03_maintenance_guide(self):
        content = f"""# 🔧 Maintenance Guide: {self.project_id}

## How to Run
```bash
source venv/bin/activate
streamlit run frontend/app.py
```

## How to Test
```bash
python -m pytest tests/
python tests/test_*.py
```

## Common Fixes
- **Ollama Offline**: Reiniciar o serviço Ollama local.
- **ChromaDB Corrupt**: Remover `data/vector_db` e re-rodar scripts de ingestão.

## ⚠️ Emergency Recovery (Mandatory)
1. **Corrupted Vector DB**: `rm -rf data/vector_db && python scripts/ingestion.py`
2. **Missing Environment**: Recuperar de `.env.template`.
3. **Snapshot Desatualizado**: Rodar `python infra/start_project.py --snapshot {self.project_id}`.

## Debugging Checklist
- [ ] O serviço Ollama está rodando?
- [ ] O banco ChromaDB foi populado?
- [ ] O arquivo `.env` contém as chaves corretas?

## Maintenance Risks
- Mudança de esquema no ChromaDB pode exigir re-indexação total.

## Safe Refactoring Notes
- Não alterar a interface do `Retriever` sem atualizar os scripts de teste TDD.
"""
        (self.context_dir / "03_MAINTENANCE_GUIDE.md").write_text(content, encoding='utf-8')

    def generate_04_observability_report(self):
        analysis = self._get_metrics_analysis()
        
        content = f"# 📊 Observability Report: {self.project_id}\n\n"
        
        if analysis["status"] == "available":
            content += f"## Metrics Summary\n- **Total Latency (Last):** {analysis['last_total_latency']}s\n"
            content += "\n## Latency Breakdown\n"
            for k, v in analysis["breakdown"].items():
                content += f"- **{k.capitalize()}:** {v}s\n"
            content += f"\n**Timestamp:** {analysis['timestamp']}\n"
        else:
            content += "## Metrics Summary\n> Métricas insuficientes para análise detalhada.\n"
            content += "\n## ⚠️ Observability Gaps\n"
            content += "Current telemetry is insufficient for full performance analysis.\n\n"
            content += "Required next metrics:\n"
            for gap in analysis["gaps"]:
                content += f"- {gap}\n"

        content += """
## Pipeline Bottlenecks
- [Preencher com o passo mais lento identificado no pipeline deste projeto.]

## Recommended Improvements
- [Preencher com melhorias recomendadas de performance.]
"""
        (self.context_dir / "04_OBSERVABILITY_REPORT.md").write_text(content, encoding='utf-8')

    def generate_05_governance_trace(self):
        git = self._get_git_info()
        content = f"""# 📑 Governance Trace: {self.project_id}

## Registry Metadata
- **Project Name:** {self.project_data.get('nome')}
- **Status:** {self.project_data.get('status')}
- **Tasks:** {self.project_data.get('tasks', {}).get('concluidas')}/{self.project_data.get('tasks', {}).get('total')}

## Jira Traceability
- **Epic:** {self.project_data.get('jira_epico', 'N/A')}
- **Tasks Range:** {self.project_data.get('jira_tasks_range', 'N/A')}

## 📜 Git Traceability (Mandatory)
| Item | Value |
|------|-------|
| Branch | {git['branch']} |
| Last Commit | {git['commit']} |
| Commit Message | {git['msg']} |
| Related Jira Issue | {self.project_id} |
| Release Tag | Not defined |

## Documentation Traceability
- **Implementation Plan:** [Link](file://{self.docs_path}/implementation_plan.md)
- **Walkthrough:** [Link](file://{self.docs_path}/walkthrough.md)
- **Architecture Docs:** [Link](file://{self.docs_path}/decisoes_arquiteturais.md)

## Snapshot Metadata
- **Generator Version:** 3.0
- **Generation Timestamp:** {self.timestamp}
"""
        (self.context_dir / "05_GOVERNANCE_TRACE.md").write_text(content, encoding='utf-8')

    def generate_06_lessons_learned(self):
        content = f"""# 💡 Lessons Learned: {self.project_id}

## What Worked Well
- [Preencher com o que funcionou bem neste projeto.]

## What Failed or Was Difficult
- [Preencher com dificuldades reais encontradas.]

## Bugs and Fixes
- **Fix:** [Preencher com bugs relevantes e como foram corrigidos.]

## TDD Insights
- [Preencher com aprendizados sobre a suíte de testes do projeto.]

## Future Recommendations
- [Preencher com recomendações para evolução futura do projeto.]
"""
        (self.context_dir / "06_LESSONS_LEARNED.md").write_text(content, encoding='utf-8')

    def execute_all(self):
        # 0. Security Guardrail Check (Extra safety)
        # Not creating new files that match blacklist
        
        self.generate_00_index()
        self.generate_01_operational_memory()
        self.generate_02_architecture_log()
        self.generate_03_maintenance_guide()
        self.generate_04_observability_report()
        self.generate_05_governance_trace()
        self.generate_06_lessons_learned()
        print(f"✅ Engineering Knowledge Capsule (v3.0) completa para {self.project_id}!")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: python governance_snapshot.py PRJ-XX")
    else:
        try:
            engine = GovernanceEngine(sys.argv[1])
            engine.execute_all()
        except Exception as e:
            print(f"❌ Erro ao gerar snapshot: {str(e)}")
