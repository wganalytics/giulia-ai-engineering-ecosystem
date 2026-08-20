import subprocess
from pathlib import Path

# Raiz do monorepo
MONOREPO_ROOT = Path(__file__).resolve().parents[2]
GARE_CLI_SCRIPT = MONOREPO_ROOT / "ecosystem" / "cli" / "gare_cli.py"

def test_gare_cli_exists():
    """Garante que o script de CLI unificado dos agentes existe no monorepo"""
    assert GARE_CLI_SCRIPT.exists(), "Script gare_cli.py não encontrado!"

def test_gare_cli_help():
    """Garante que rodar a CLI com --help retorna as instruções corretas de uso"""
    res = subprocess.run(
        ["python3", str(GARE_CLI_SCRIPT), "--help"],
        capture_output=True,
        text=True
    )
    
    assert res.returncode == 0, f"gare_cli.py falhou ao rodar com --help! Erro: {res.stderr}"
    assert "project" in res.stdout, "Subcomando 'project' ausente na ajuda da CLI!"
    assert "jira" in res.stdout, "Subcomando 'jira' ausente na ajuda da CLI!"
    assert "validate" in res.stdout, "Subcomando 'validate' ausente na ajuda da CLI!"

def test_gare_cli_project_list():
    """Garante que rodar 'gare project list' executa sem erro.

    Sem projetos cadastrados em shared/REGISTRY/projects.json, o comando deve
    informar isso de forma graciosa; com projetos cadastrados, deve formatar
    a saída como tabela Markdown.
    """
    res = subprocess.run(
        ["python3", str(GARE_CLI_SCRIPT), "project", "list"],
        capture_output=True,
        text=True
    )

    assert res.returncode == 0, f"Falha ao executar 'gare project list'! Erro: {res.stderr}"
    assert res.stdout.strip(), "O comando 'project list' não produziu nenhuma saída!"
    assert "|" in res.stdout or "Nenhum projeto encontrado" in res.stdout, (
        "Saída inesperada de 'project list': deve ser uma tabela Markdown "
        "ou a mensagem de registro vazio."
    )
