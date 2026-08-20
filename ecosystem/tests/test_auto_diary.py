import subprocess
from pathlib import Path

# Raiz do monorepo
MONOREPO_ROOT = Path(__file__).resolve().parents[2]
AUTO_DIARY_SCRIPT = MONOREPO_ROOT / "ecosystem" / "automation" / "auto_diary.py"

def test_auto_diary_script_exists():
    """Garante que o script auto_diary.py existe na pasta correta de automação"""
    assert AUTO_DIARY_SCRIPT.exists(), "Script auto_diary.py não encontrado!"

def test_auto_diary_dry_run():
    """Garante que rodar auto_diary.py com a flag --dry-run não falha e imprime a sessão simulada"""
    res = subprocess.run(
        ["python3", str(AUTO_DIARY_SCRIPT), "--dry-run"],
        capture_output=True,
        text=True
    )
    
    assert res.returncode == 0, f"O script auto_diary.py falhou ao rodar com --dry-run! Erro: {res.stderr}"
    assert "Sessão #" in res.stdout, "O output do dry-run não gerou uma entrada estruturada de sessão RLM!"
    assert "Agente:" in res.stdout, "O output do dry-run não detectou ou listou o agente!"
