"""
Testes para sync_state.py - Módulo de Idempotência
"""

import pytest
import os
import tempfile
import shutil
from sync_state import SyncState


class TestSyncState:
    """Testes para a classe SyncState."""

    @pytest.fixture
    def temp_dir(self):
        """Cria diretório temporário para testes."""
        temp = tempfile.mkdtemp()
        yield temp
        shutil.rmtree(temp)

    @pytest.fixture
    def state(self, temp_dir):
        """Cria instância de SyncState com diretório temporário."""
        return SyncState(state_dir=temp_dir)

    def test_estado_vazio_inicial(self, state):
        """Testa se estado inicial é criado corretamente."""
        assert state.state["version"] == "1.0"
        assert state.state["projetos"] == {}
        assert state.state["tasks"] == {}

    def test_registrar_epico(self, state):
        """Testa registro de épico."""
        state.register_epico("PRJ-01", "RAG-100")

        epico = state.get_epico_key("PRJ-01")
        assert epico == "RAG-100"

    def test_registrar_task(self, state):
        """Testa registro de task."""
        state.register_task("PRJ-01-TASK-1", "RAG", "RAG-101", "2026-04-21", "4h")

        key = state.get_task_jira_key("PRJ-01-TASK-1", "RAG")
        assert key == "RAG-101"

    def test_task_existe(self, state):
        """Testa verificação de task existente."""
        state.register_task("PRJ-01-TASK-1", "RAG", "RAG-101", "2026-04-21", "4h")

        assert state.is_task_exists("PRJ-01-TASK-1", "RAG") is True
        assert state.is_task_exists("PRJ-01-TASK-999", "RAG") is False

    def test_registrar_subtask(self, state):
        """Testa registro de subtask."""
        state.register_subtask("RAG-101", "ST1: Testar algo", "RAG-102")

        # Verifica se foi criado
        assert "RAG-101:ST1: Testar algo" in state.state["subtasks"]

    def test_registrar_link(self, state):
        """Testa registro de link."""
        state.register_link("RAG-102", "RAG-101", "Blocks")

        assert state.is_link_exists("RAG-102", "RAG-101", "Blocks") is True
        assert state.is_link_exists("RAG-102", "RAG-999", "Blocks") is False

    def test_save_e_load(self, state):
        """Testa persistência do estado."""
        state.register_epico("PRJ-01", "RAG-100")
        state.register_task("T1", "RAG", "RAG-101", "2026-04-21", "4h")
        state.save()

        # Cria nova instância que deve carregar o estado salvo
        state2 = SyncState(state_dir=os.path.dirname(state.state_path))

        assert state2.get_epico_key("PRJ-01") == "RAG-100"
        assert state2.get_task_jira_key("T1", "RAG") == "RAG-101"

    def test_clear(self, state):
        """Testa limpeza do estado."""
        state.register_epico("PRJ-01", "RAG-100")
        state.clear()

        assert state.state["projetos"] == {}
        assert state.state["tasks"] == {}

    def test_get_summary(self, state):
        """Testa geração de resumo."""
        state.register_epico("PRJ-01", "RAG-100")
        state.register_task("T1", "RAG", "RAG-101", None, None)
        state.register_task("T2", "RAG", "RAG-102", None, None)

        summary = state.get_summary()

        assert summary["projetos"] == 1
        assert summary["tasks"] == 2
