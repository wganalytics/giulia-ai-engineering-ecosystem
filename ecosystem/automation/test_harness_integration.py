# ecosystem/automation/test_harness_integration.py
import unittest
from unittest.mock import MagicMock, patch
from pathlib import Path
import shutil
import tempfile
import json
import yaml

from ecosystem.automation.agent_harness import AgentHarness

class TestAgentHarnessIntegration(unittest.TestCase):
    def setUp(self):
        # Criar diretório temporário para simular um projeto do ecossistema
        self.test_dir = Path(tempfile.mkdtemp())
        
        # Criar manifesto projetos.yaml básico
        self.projetos_yaml = self.test_dir / "projetos.yaml"
        with open(self.projetos_yaml, "w", encoding="utf-8") as f:
            yaml.dump({
                "projeto_id": "test_project",
                "jira_issue_key": "GIULIA-TEST",
                "gerenciador_projetos": "jira",
                "status": "active"
            }, f)
            
        # Criar diretórios necessários
        (self.test_dir / "specs").mkdir(parents=True)
        (self.test_dir / "tests").mkdir(parents=True)
        
        # Instanciar o Harness apontando para a pasta temporária
        self.harness = AgentHarness(str(self.test_dir))
        # Mock do tracker para evitar chamadas de API externas
        self.harness.tracker = MagicMock()

    def tearDown(self):
        shutil.rmtree(self.test_dir)

    @patch("subprocess.run")
    def test_tdd_success_flow(self, mock_run):
        # Mock do teste passando (returncode = 0)
        mock_run.return_value = MagicMock(returncode=0)
        
        callback = MagicMock(return_value=("def test(): pass", "justificativa sucesso"))
        
        self.harness.executar_passo_agente("Implementation Agent", "PRD", callback)
        
        # Verificar se os testes foram executados
        self.assertTrue(mock_run.called)
        # Sucesso reseta falhas
        self.assertEqual(self.harness.consecutive_failures, 0)
        self.assertEqual(self.harness.modelo_atual, "llama3.2:3b")

    @patch("subprocess.run")
    def test_tdd_failure_escalation_flow(self, mock_run):
        # Mock do teste falhando (returncode = 1)
        mock_run.return_value = MagicMock(returncode=1)
        
        callback = MagicMock(return_value=("def test(): fail", "justificativa erro"))
        
        # Primeira falha
        self.harness.executar_passo_agente("Implementation Agent", "PRD", callback)
        self.assertEqual(self.harness.consecutive_failures, 1)
        self.assertEqual(self.harness.modelo_atual, "llama3.2:3b") # Primeira falha não escala ainda
        
        # Segunda falha
        self.harness.executar_passo_agente("Implementation Agent", "PRD", callback)
        self.assertEqual(self.harness.consecutive_failures, 2)
        # Na segunda falha consecutiva, deve escalar para qwen3.5:35b
        self.assertEqual(self.harness.modelo_atual, "qwen3.5:35b")

        # Mock do teste agora passando na terceira tentativa com o modelo escalado
        mock_run.return_value = MagicMock(returncode=0)
        self.harness.executar_passo_agente("Implementation Agent", "PRD", callback)
        
        # Sucesso deve resetar o contador e restaurar o modelo padrão
        self.assertEqual(self.harness.consecutive_failures, 0)
        self.assertEqual(self.harness.modelo_atual, "llama3.2:3b")

if __name__ == "__main__":
    unittest.main()
