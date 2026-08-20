import json
import subprocess
from pathlib import Path

# Raiz do monorepo
MONOREPO_ROOT = Path(__file__).resolve().parents[2]
BENCH_DIR = MONOREPO_ROOT / "ecosystem" / "bench"
TASKS_FILE = BENCH_DIR / "tasks.json"
RUNNER_SCRIPT = BENCH_DIR / "runner.py"

def test_gare_bench_directory_and_files_exist():
    """Garante que a pasta do benchmark e seus componentes básicos existem"""
    assert BENCH_DIR.exists() and BENCH_DIR.is_dir(), "Diretório do benchmark não encontrado!"
    assert TASKS_FILE.exists(), "Arquivo tasks.json do benchmark ausente!"
    assert RUNNER_SCRIPT.exists(), "Script runner.py do benchmark ausente!"

def test_tasks_json_schema():
    """Garante que o tasks.json segue a modelagem e possui tarefas reais válidas"""
    with open(TASKS_FILE, "r", encoding="utf-8") as f:
        tasks = json.load(f)
        
    assert isinstance(tasks, list), "O tasks.json deve ser uma lista JSON!"
    assert len(tasks) >= 3, "Devem existir pelo menos 3 tarefas cadastradas no benchmark!"
    
    required_keys = {"task_id", "description", "project_key", "base_commit", "verification_command", "difficulty"}
    for task in tasks:
        for key in required_keys:
            assert key in task, f"Atributo '{key}' ausente na tarefa {task.get('task_id', 'desconhecida')}!"

def test_runner_dry_run():
    """Garante que o runner consegue simular o fluxo com a flag --dry-run"""
    # Executa o dry-run para a primeira task cadastrada
    with open(TASKS_FILE, "r", encoding="utf-8") as f:
        tasks = json.load(f)
    first_task_id = tasks[0]["task_id"]
    
    res = subprocess.run(
        ["python3", str(RUNNER_SCRIPT), "--task", first_task_id, "--dry-run"],
        capture_output=True,
        text=True
    )
    
    assert res.returncode == 0, f"O runner falhou ao executar dry-run! Erro: {res.stderr}"
    assert "[DRY-RUN]" in res.stdout, "Mensagem de dry-run ausente no log do runner!"
