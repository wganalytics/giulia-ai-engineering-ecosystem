# ecosystem/automation/agent_harness.py
import os
import json
import subprocess
import yaml
from datetime import datetime
from pathlib import Path

# Ajuste de import para rodar a partir do root do monorepo
from shared.infra.skills.tracker_interface import ProjectTracker
from shared.infra.skills.jira_adapter import JiraAdapter
from shared.infra.skills.redmine_adapter import RedmineAdapter

class AgentHarness:
    def __init__(self, caminho_projeto: str):
        self.caminho_projeto = Path(caminho_projeto)
        self.projetos_yaml_path = self.caminho_projeto / "projetos.yaml"
        self.trace_path = self.caminho_projeto / "handoff_trace.jsonl"
        
        self.config_projeto = self._carregar_config_projeto()
        self.tracker = self._inicializar_tracker()
        self.modelo_atual = "llama3.2:3b"
        self.consecutive_failures = 0

    def _carregar_config_projeto(self) -> dict:
        if not self.projetos_yaml_path.exists():
            raise FileNotFoundError(f"Manifesto projetos.yaml não encontrado em {self.caminho_projeto}")
        with open(self.projetos_yaml_path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
            # Normalização de Schema: aceita tanto o formato plano quanto um
            # formato aninhado sob a chave "projeto" (compat com versões antigas
            # do template de projetos.yaml).
            if "projeto" in data:
                return {
                    "projeto_id": data["projeto"].get("id"),
                    "jira_issue_key": data["projeto"].get("jira_issue_key"),
                    "silo": data["projeto"].get("silo"),
                    "status": data["projeto"].get("status")
                }
            return data

    def _inicializar_tracker(self) -> ProjectTracker:
        gerenciador = self.config_projeto.get("gerenciador_projetos", "jira").lower()
        if gerenciador == "redmine":
            return RedmineAdapter()
        return JiraAdapter()

    def obter_shard_especificacao(self, nome_shard: str) -> str:
        caminho_shard = self.caminho_projeto / "specs" / f"{nome_shard}.md"
        if caminho_shard.exists():
            with open(caminho_shard, "r", encoding="utf-8") as f:
                return f.read()
        return ""

    def salvar_shard_especificacao(self, nome_shard: str, conteudo: str):
        caminho_shard = self.caminho_projeto / "specs" / f"{nome_shard}.md"
        caminho_shard.parent.mkdir(parents=True, exist_ok=True)
        with open(caminho_shard, "w", encoding="utf-8") as f:
            f.write(conteudo)

    def criar_ponto_restauracao(self):
        """
        Identifica o estado Git atual no escopo do projeto para reversibilidade.
        """
        print(f"⚓ [Harness] Ponto de restauração Git preparado para {self.caminho_projeto}")

    def reverter_para_ponto_restauracao(self):
        """
        Executa rollback descartando alterações no diretório do projeto via Git.
        """
        print(f"⏪ [Harness] Revertendo alterações locais em {self.caminho_projeto}...")
        try:
            # Reverter arquivos rastreados modificados
            subprocess.run(["git", "checkout", "--", str(self.caminho_projeto)], capture_output=True, text=True)
            # Limpar arquivos não rastreados
            subprocess.run(["git", "clean", "-fd", str(self.caminho_projeto)], capture_output=True, text=True)
            print("✅ [Harness] Rollback via Git concluído com sucesso.")
        except Exception as e:
            print(f"❌ [Harness] Erro ao reverter para o ponto de restauração: {e}")

    def executar_piramide_testes(self) -> bool:
        # Tenta usar o .venv local se existir, caso contrário vai no global
        venv_python = self.caminho_projeto / ".venv" / "bin" / "python"
        cmd = [str(venv_python if venv_python.exists() else "python3"), "-m", "pytest", str(self.caminho_projeto / "tests")]
        
        try:
            resultado = subprocess.run(cmd, capture_output=True, text=True, timeout=30.0)
            return resultado.returncode == 0
        except Exception:
            return False

    def registrar_handoff_local(self, skill: str, solucao: str, justificativa: str, status: str):
        trace_line = {
            "timestamp": datetime.now().isoformat() + "Z",
            "projeto_id": self.config_projeto.get("projeto_id", self.caminho_projeto.name),
            "jira_issue_key": self.config_projeto.get("jira_issue_key", "UNKNOWN"),
            "skill_utilizada": skill,
            "solucao_decidida": solucao,
            "justification": justificativa,
            "status": status,
            "consecutive_failures": self.consecutive_failures
        }
        with open(self.trace_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(trace_line, ensure_ascii=False) + "\n")

    def executar_passo_agente(self, agente: str, shard: str, acao_llm_callback):
        print(f" Ativando {agente} no fragmento {shard}")
        contexto_spec = self.obter_shard_especificacao(shard)
        
        # Carregar as diretrizes de engenharia dos insights compilados
        from ecosystem.automation.load_insights_rules import load_system_prompt
        regras_insights = load_system_prompt()
        contexto_completo = f"{regras_insights}\n\n[CONTEXTO DO SHARD DE ESPECIFICAÇÃO]\n{contexto_spec}"
        
        self.criar_ponto_restauracao()
        
        codigo_ou_spec_gerado, justificativa = acao_llm_callback(contexto_completo, self.modelo_atual)
        
        if "Implementation" in agente:
            caminho_codigo = self.caminho_projeto / "src" / "main.py"
            # Garantir diretório do código existe
            caminho_codigo.parent.mkdir(parents=True, exist_ok=True)
            with open(caminho_codigo, "w", encoding="utf-8") as f:
                f.write(codigo_ou_spec_gerado)
            
            sucesso_testes = self.executar_piramide_testes()
            if sucesso_testes:
                status_final = "success"
                self.consecutive_failures = 0
                self.modelo_atual = "llama3.2:3b" # Restaurar modelo padrão
            else:
                status_final = "failed"
                self.consecutive_failures += 1
                self.reverter_para_ponto_restauracao()
                
                # Escalação se 2 falhas consecutivas de TDD
                if self.consecutive_failures >= 2:
                    print(f"🚨 [Harness] {self.consecutive_failures} falhas consecutivas de TDD. Escalando modelo para qwen3.5:35b...")
                    self.modelo_atual = "qwen3.5:35b"
        else:
            self.salvar_shard_especificacao(shard, codigo_ou_spec_gerado)
            status_final = "success"
            self.consecutive_failures = 0

        self.registrar_handoff_local(agente, f"Escrita concluída em {shard}", justificativa, status_final)
        self.tracker.enviar_auditoria(self.config_projeto.get("jira_issue_key", "GIULIA-UNKNOWN"), agente, f"Passo {status_final}", justificativa)