"""
Módulo de Gerenciamento de Estado de Sincronização (Idempotência)

Responsável por:
- Rastrear quais issues já foram criadas no Jira
- Permitir execução idempotente do jira_sync.py
- Evitar duplicatas no Jira
"""

from __future__ import annotations

import os
import json
from datetime import datetime
from typing import Any

STATE_FILE = ".sync_state.json"

type StateDict = dict[str, Any]
type SyncSummary = dict[str, int | str | None]


class SyncState:
    """Gerenciador de estado para sincronização idempotente."""

    def __init__(self, state_dir: str | None = None) -> None:
        if state_dir is None:
            state_dir = os.path.dirname(__file__)
        self.state_path: str = os.path.join(state_dir, STATE_FILE)
        self.state: StateDict = self._load_state()

    def _load_state(self) -> StateDict:
        """Carrega o estado do arquivo JSON ou cria novo."""
        if os.path.exists(self.state_path):
            try:
                with open(self.state_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError):
                return self._create_empty_state()
        return self._create_empty_state()

    def _create_empty_state(self) -> StateDict:
        """Cria estrutura vazia do estado."""
        return {
            "version": "1.0",
            "last_sync": None,
            "projetos": {},
            "epicos": {},
            "tasks": {},
            "subtasks": {},
            "links": {}
        }

    def _generate_key(self, task_id: str, project_key: str) -> str:
        """Gera uma chave única para a task."""
        return f"{project_key}:{task_id}"

    def get_epico_key(self, projeto_id: str) -> str | None:
        """Retorna a chave do épico criado para um projeto."""
        return self.state["projetos"].get(projeto_id, {}).get("epico_key")

    def register_epico(self, projeto_id: str, epico_key: str) -> None:
        """Registra um épico criado."""
        if "projetos" not in self.state:
            self.state["projetos"] = {}

        self.state["projetos"][projeto_id] = {
            "epico_key": epico_key,
            "registered_at": datetime.now().isoformat()
        }

    def is_task_exists(self, task_id: str, project_key: str) -> bool:
        """Verifica se uma task já foi criada."""
        key = self._generate_key(task_id, project_key)
        return key in self.state.get("tasks", {})

    def get_task_jira_key(self, task_id: str, project_key: str) -> str | None:
        """Retorna a chave Jira de uma task se existir."""
        key = self._generate_key(task_id, project_key)
        return self.state.get("tasks", {}).get(key, {}).get("jira_key")

    def register_task(
        self,
        task_id: str,
        project_key: str,
        jira_key: str,
        due_date: str | None = None,
        estimate: str | None = None
    ) -> None:
        """Registra uma task criada no Jira."""
        key = self._generate_key(task_id, project_key)

        if "tasks" not in self.state:
            self.state["tasks"] = {}

        self.state["tasks"][key] = {
            "jira_key": jira_key,
            "task_id": task_id,
            "project_key": project_key,
            "due_date": due_date,
            "estimate": estimate,
            "created_at": datetime.now().isoformat()
        }

    def register_subtask(
        self,
        parent_task_key: str,
        subtask_summary: str,
        jira_key: str
    ) -> None:
        """Registra uma subtask criada."""
        key = f"{parent_task_key}:{subtask_summary[:30]}"

        if "subtasks" not in self.state:
            self.state["subtasks"] = {}

        self.state["subtasks"][key] = {
            "jira_key": jira_key,
            "parent": parent_task_key,
            "created_at": datetime.now().isoformat()
        }

    def register_link(
        self,
        from_key: str,
        to_key: str,
        link_type: str = "Blocks"
    ) -> None:
        """Registra um link criado."""
        key = f"{from_key}:{link_type}:{to_key}"

        if "links" not in self.state:
            self.state["links"] = {}

        self.state["links"][key] = {
            "from": from_key,
            "to": to_key,
            "type": link_type,
            "created_at": datetime.now().isoformat()
        }

    def is_link_exists(
        self,
        from_key: str,
        to_key: str,
        link_type: str = "Blocks"
    ) -> bool:
        """Verifica se um link já foi criado."""
        key = f"{from_key}:{link_type}:{to_key}"
        return key in self.state.get("links", {})

    def save(self) -> None:
        """Salva o estado no arquivo."""
        self.state["last_sync"] = datetime.now().isoformat()

        with open(self.state_path, 'w', encoding='utf-8') as f:
            json.dump(self.state, f, indent=2, ensure_ascii=False)

    def clear(self) -> None:
        """Limpa todo o estado (para novo sync)."""
        self.state = self._create_empty_state()
        self.save()

    def get_summary(self) -> SyncSummary:
        """Retorna um resumo do estado atual."""
        return {
            "projetos": len(self.state.get("projetos", {})),
            "tasks": len(self.state.get("tasks", {})),
            "subtasks": len(self.state.get("subtasks", {})),
            "links": len(self.state.get("links", {})),
            "last_sync": self.state.get("last_sync")
        }


def criar_state_manager(state_dir: str | None = None) -> SyncState:
    """Factory function para criar o gerenciador de estado."""
    return SyncState(state_dir=state_dir)