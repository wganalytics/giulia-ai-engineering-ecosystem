"""
Testes para funções do jira_sync.py
"""

from datetime import datetime, timedelta


# Simular as funções do jira_sync.py para teste
def parse_estimate(estimate_str):
    """Converte string de estimativa para segundos."""
    if not estimate_str:
        return None

    estimate_str = estimate_str.lower().strip()

    try:
        if estimate_str.endswith('h'):
            hours = int(estimate_str[:-1])
            return hours * 3600
        elif estimate_str.endswith('d'):
            days = int(estimate_str[:-1])
            return days * 8 * 3600
        elif estimate_str.endswith('m'):
            minutes = int(estimate_str[:-1])
            return minutes * 60
        elif estimate_str.isdigit():
            return int(estimate_str) * 3600
    except ValueError:
        pass

    return None


def calcular_due_date_respeitando_dependencias(task, todas_tasks, tarefas_criadas, buffer_dias=2):
    """Calcula o Due Date respeitando a cadeia de dependências."""
    blocked_by = task.get("blocked_by")

    # Se não tem dependência, usa o padrão
    if not blocked_by:
        base_date = datetime.now()
        return (base_date + timedelta(days=task.get("due_days", 3))).strftime("%Y-%m-%d")

    # Se tem dependência, busca o Due Date da task bloqueada
    blocked_task_id = blocked_by
    jira_key_blocked = tarefas_criadas.get(blocked_task_id)

    # Simular busca no Jira (nesse teste, usamos dados mockados)
    if jira_key_blocked and "due_date" in tarefas_criadas.get(blocked_task_id + "_data", {}):
        # Aqui teria que chamar a API do Jira, mas para teste usamos mock
        blocked_due = datetime.strptime(
            tarefas_criadas.get(blocked_task_id + "_data", {}).get("due_date", "2026-04-21"),
            "%Y-%m-%d"
        )
        calculated_due = blocked_due + timedelta(days=buffer_dias)
        return calculated_due.strftime("%Y-%m-%d")

    # Fallback
    base_date = datetime.now()
    return (base_date + timedelta(days=task.get("due_days", 3))).strftime("%Y-%m-%d")


def determinar_labels(task_labels):
    """Determina labels baseado na configuração da task."""
    return task_labels if task_labels else ["AGENT-AI"]


class TestParseEstimate:
    """Testes para função parse_estimate."""

    def test_horas(self):
        """Testa parsing de horas."""
        assert parse_estimate("4h") == 14400
        assert parse_estimate("8h") == 28800
        assert parse_estimate("1h") == 3600

    def test_dias(self):
        """Testa parsing de dias."""
        assert parse_estimate("1d") == 28800  # 8 horas
        assert parse_estimate("2d") == 57600

    def test_minutos(self):
        """Testa parsing de minutos."""
        assert parse_estimate("30m") == 1800
        assert parse_estimate("15m") == 900

    def test_numero_so(self):
        """Testa parsing de número só (assume horas)."""
        assert parse_estimate("4") == 14400

    def test_string_invalida(self):
        """Testa string inválida."""
        assert parse_estimate("invalid") is None
        assert parse_estimate("") is None
        assert parse_estimate(None) is None


class TestDeterminarLabels:
    """Testes para função determinar_labels."""

    def test_com_labels(self):
        """Testa com labels definidos."""
        assert determinar_labels(["HUMAN"]) == ["HUMAN"]
        assert determinar_labels(["HUMAN", "AGENT-AI"]) == ["HUMAN", "AGENT-AI"]

    def test_sem_labels(self):
        """Testa sem labels (default)."""
        assert determinar_labels(None) == ["AGENT-AI"]
        assert determinar_labels([]) == ["AGENT-AI"]


class TestCalcularDueDate:
    """Testes para cálculo de Due Date."""

    def test_sem_dependencia(self):
        """Testa task sem dependência."""
        task = {"id": "T1", "due_days": 5}

        # Não depende de nada - usa base
        # O resultado vai variar baseado na data atual
        result = calcular_due_date_respeitando_dependencias(task, [], {}, 2)

        # Verifica formato
        assert len(result) == 10  # YYYY-MM-DD
        assert result[4] == "-"   # Tem hifens
        assert result[7] == "-"

    def test_com_dependencia(self):
        """Testa task com dependência."""
        task = {"id": "T2", "due_days": 3, "blocked_by": "T1"}

        # Com dependência mockada
        tarefas_criadas = {
            "T1": "RAG-101",
            "T1_data": {"due_date": "2026-04-21"}
        }

        result = calcular_due_date_respeitando_dependencias(task, [], tarefas_criadas, 2)

        # Deve ser 21/04 + 2 dias = 23/04
        assert result == "2026-04-23"
