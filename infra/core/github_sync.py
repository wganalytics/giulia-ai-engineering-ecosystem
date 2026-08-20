#!/usr/bin/env python3
"""
🚀 GARE - GitHub Sync Automation
Sincroniza o monorepo local com o GitHub usando padrões profissionais.

Uso:
    python infra/core/github_sync.py --type feat --scope infra --msg "add git automation" --task GARE-123
"""

import os
import sys
import subprocess
import argparse
from pathlib import Path
from dotenv import load_dotenv

# Configuração de Paths
BASE_DIR = Path(__file__).parent.parent.parent
sys.path.insert(0, str(BASE_DIR))

from infra.lib.sync_state import criar_state_manager

# Carregar variáveis de ambiente
load_dotenv(BASE_DIR / "infra/config/.env")

GITHUB_USER = os.getenv("GITHUB_USER")
GITHUB_REPO = os.getenv("GITHUB_REPO")
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
PROJECT_KEY = os.getenv("JIRA_PROJECT_KEY", "GARE")

def run_command(command: list[str], cwd: Path = BASE_DIR) -> str:
    """Executa um comando shell e retorna a saída."""
    try:
        result = subprocess.run(
            command,
            cwd=cwd,
            capture_output=True,
            text=True,
            check=True
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        print(f"❌ Erro ao executar comando: {' '.join(command)}")
        print(f"Saída de erro: {e.stderr}")
        sys.exit(1)

def validate_git_setup():
    """Valida se o ambiente Git está configurado."""
    if not (BASE_DIR / ".git").exists():
        print("❌ Erro: Repositório Git não inicializado.")
        sys.exit(1)
    
    if GITHUB_TOKEN == "SEU_TOKEN_AQUI" or not GITHUB_TOKEN:
        print("⚠️  Aviso: GITHUB_TOKEN não configurado no .env.")

def get_current_task(task_arg: str) -> str:
    """Resolve a issue key do Jira."""
    if task_arg and task_arg.upper() != "AUTO":
        return task_arg.upper()
    
    # Tenta buscar do sync_state
    state = criar_state_manager()
    last_key = None
    
    # Busca a task com created_at mais recente
    tasks = state.state.get("tasks", {})
    if tasks:
        sorted_tasks = sorted(
            tasks.values(), 
            key=lambda x: x.get("created_at", ""), 
            reverse=True
        )
        last_key = sorted_tasks[0].get("jira_key")
    
    if last_key:
        print(f"ℹ️  Task detectada automaticamente: {last_key}")
        return last_key
    
    print("❌ Erro: Nenhuma task encontrada. Forneça via --task GARE-XXX")
    sys.exit(1)

def main():
    parser = argparse.ArgumentParser(description="GARE GitHub Sync")
    parser.add_argument("--type", required=True, choices=["feat", "fix", "docs", "style", "refactor", "test", "chore", "infra"], help="Tipo do commit (Conventional Commits)")
    parser.add_argument("--scope", required=True, help="Escopo da alteração (ex: core, infra, prj-xx)")
    parser.add_argument("--msg", required=True, help="Descrição curta da alteração")
    parser.add_argument("--task", default="AUTO", help="Chave da task Jira (ex: GARE-123). Use AUTO para detectar a última.")
    parser.add_argument("--dry-run", action="store_true", help="Simula o processo sem fazer push")
    
    args = parser.parse_args()
    
    validate_git_setup()
    
    jira_key = get_current_task(args.task)
    
    # Formata mensagem: type(scope): msg #GARE-XXX
    commit_msg = f"{args.type}({args.scope}): {args.msg} #{jira_key}"
    
    print(f"🚀 Iniciando sincronização GARE...")
    print(f"📝 Mensagem: {commit_msg}")
    
    if args.dry_run:
        print("\n[DRY RUN] Comandos que seriam executados:")
        print(f"  git add .")
        print(f"  git commit -m \"{commit_msg}\"")
        print(f"  git push origin main")
        return

    # Execução Real
    # 1. Add
    print("  ➕ Adicionando arquivos...")
    run_command(["git", "add", "."])
    
    # 2. Commit
    print("  💾 Realizando commit...")
    try:
        run_command(["git", "commit", "-m", commit_msg])
    except SystemExit:
        print("  ℹ️  Nada para commitar (working tree clean).")
        return

    # 3. Push
    print("  ⬆️  Enviando para o GitHub...")
    # Usar o token na URL para o push se necessário (se não estiver cacheado via SSH)
    remote_url = f"https://{GITHUB_USER}:{GITHUB_TOKEN}@github.com/{GITHUB_USER}/{GITHUB_REPO}.git"
    
    # Temporariamente ajusta a URL para usar o token (silencioso para não vazar token no log se possível)
    try:
        # Se for a primeira vez ou mudar token, garante que o remote está ok
        # Mas para simplificar, usamos origin main
        run_command(["git", "push", "origin", "main"])
        print("\n✅ Sucesso! Código versionado e publicado no Giullia AI: RAG Ecosystem.")
    except Exception:
        print("  ⚠️  Falha no push via origin. Tentando via URL com Token...")
        # Fallback se o origin não estiver configurado para autenticação automática
        subprocess.run(
            ["git", "push", remote_url, "main"],
            capture_output=True,
            check=True
        )
        print("\n✅ Sucesso! Código versionado via Token.")

if __name__ == "__main__":
    main()
