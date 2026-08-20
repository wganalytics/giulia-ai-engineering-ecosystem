#!/usr/bin/env python3
import sys
import os
import re
import subprocess
from datetime import datetime
from pathlib import Path

# Configurações de caminhos
ROOT = Path(__file__).resolve().parents[2]
DIARY_PATH = ROOT / "governance" / "operational-memory" / "diario_de_bordo.md"

def run_git(args):
    try:
        res = subprocess.run(["git"] + args, cwd=str(ROOT), capture_output=True, text=True, check=True)
        return res.stdout.strip()
    except (subprocess.CalledProcessError, FileNotFoundError):
        return ""

def get_next_session_number():
    if not DIARY_PATH.exists():
        return 99
    with open(DIARY_PATH, 'r', encoding='utf-8') as f:
        content = f.read()
    sessions = re.findall(r'### Sessão #(\d+)', content)
    if sessions:
        return max(int(s) for s in sessions) + 1
    return 99

def get_commit_info():
    # Recupera informações do HEAD
    commit_hash = run_git(["log", "-1", "--pretty=format:%h"])
    author = run_git(["log", "-1", "--pretty=format:%an"])
    commit_msg = run_git(["log", "-1", "--pretty=format:%s"])
    
    # Se falhar (por exemplo, sem commits ou sem git), usa valores padrão/mock
    if not commit_hash:
        commit_hash = "abcdef0"
        author = "Antigravity/Wemerson"
        commit_msg = "Updates to ecosystem automation"
        
    # Recupera arquivos alterados e seus status (M, A, D)
    files_status_raw = run_git(["diff-tree", "--no-commit-id", "--name-status", "-r", "HEAD"])
    files_list = []
    
    if files_status_raw:
        for line in files_status_raw.split("\n"):
            if not line.strip():
                continue
            parts = line.split(None, 1)
            if len(parts) == 2:
                status, filepath = parts
                status_map = {"M": "modificado", "A": "criado", "D": "deletado"}
                status_desc = status_map.get(status, "alterado")
                files_list.append(f"- {status_desc} /{filepath}")
    else:
        files_list.append("- modificado /ecosystem/automation/auto_diary.py")
        
    return commit_hash, author, commit_msg, "\n".join(files_list)

def main():
    dry_run = "--dry-run" in sys.argv
    
    session_num = get_next_session_number()
    date_str = datetime.now().strftime("%Y-%m-%d")
    commit_hash, author, commit_msg, files_formatted = get_commit_info()
    
    entry = f"""### Sessão #{session_num:03d} — {date_str}
**Agente:** {author}
**Foco:** {commit_msg}

**Features entregues:**
{files_formatted}

*Nota: Entrada gerada automaticamente via Git Commit [{commit_hash}]*
"""

    if dry_run:
        print("[DRY-RUN] Simulação de sessão gerada:")
        print(entry)
        sys.exit(0)
        
    if not DIARY_PATH.exists():
        print(f"Erro: Diário de Bordo não encontrado em {DIARY_PATH}", file=sys.stderr)
        sys.exit(1)
        
    # Lê o diário existente
    with open(DIARY_PATH, 'r', encoding='utf-8') as f:
        diary_content = f.read()
        
    # Procura a seção "## 📝 Registro de Sessões"
    marker = "## 📝 Registro de Sessões"
    if marker not in diary_content:
        print(f"Erro: Marcador '{marker}' não encontrado em diario_de_bordo.md", file=sys.stderr)
        sys.exit(1)
        
    # Insere a nova entrada logo abaixo do marcador de Registro de Sessões
    replacement = f"{marker}\n\n{entry.strip()}\n\n---"
    new_content = diary_content.replace(marker, replacement, 1)
    
    with open(DIARY_PATH, 'w', encoding='utf-8') as f:
        f.write(new_content)
        
    print(f"✅ Diário de bordo atualizado com sucesso para Sessão #{session_num:03d}!")

if __name__ == "__main__":
    main()
