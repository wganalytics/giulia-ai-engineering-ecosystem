#!/usr/bin/env python3
"""
Git-Jira Link - Integração entre Commits e Issues do Jira

Uso:
    python git_jira_link.py --link          # Link commits não liés ao Jira
    python git_jira_link.py --validate      # Valida formato dos commits
    python git_jira_link.py --hook          # Gera pre-commit hook
    python git_jira_link.py --log            # Mostra commits com issues detectadas

Funcionalidades:
- Detecta chaves de issues nos commits (ex: RAG-333, PRJ-XX-5)
- Cria links no Jira entre commits e issues
- Valida formato Conventional Commits
- Gera pre-commit hook opcional
"""

import os
import sys
import re
import argparse
import subprocess
import requests
from requests.auth import HTTPBasicAuth
import tomli as tomli

try:
    from dotenv import load_dotenv
    load_dotenv(os.path.join(os.path.dirname(__file__), '.env'))
except ImportError:
    pass

# ============================================
# CONFIGURAÇÕES
# ============================================

JIRA_DOMAIN = os.environ.get("JIRA_DOMAIN")
JIRA_EMAIL = os.environ.get("JIRA_EMAIL")
JIRA_TOKEN = os.environ.get("JIRA_TOKEN")
PROJECT_KEY = os.environ.get("JIRA_PROJECT_KEY", "RAG")

if not all([JIRA_DOMAIN, JIRA_EMAIL, JIRA_TOKEN]):
    print("❌ ERRO: Variáveis de ambiente faltando no .env")
    sys.exit(1)

URL_BASE = f"https://{JIRA_DOMAIN}/rest/api/2"
AUTH = HTTPBasicAuth(JIRA_EMAIL, JIRA_TOKEN)
HEADERS = {"Accept": "application/json", "Content-Type": "application/json"}

# Regex para detectar chaves de issues no padrão Conventional Commits
JIRA_KEY_PATTERN = re.compile(r'\b([A-Z]{2,}-\d+)\b')

# Padrão Conventional Commits (opcional)
COMMIT_PATTERN = re.compile(
    r'^(feat|fix|docs|style|refactor|test|chore|perf|ci|build|revert)'
    r'(\([a-zA-Z0-9_-]+\))?(!)?:\s+.+'
)

# ============================================
# FUNÇÕES DE GIT
# ============================================

def run_git_command(args):
    """Executa um comando git e retorna a saída."""
    try:
        result = subprocess.run(
            args,
            capture_output=True,
            text=True,
            check=True
        )
        return result.stdout.strip(), True
    except subprocess.CalledProcessError as e:
        return e.stderr, False

def get_commits(since=None, until=None, limit=50):
    """Busca commits do repositório git."""
    cmd = ["git", "log", f"-{limit}", "--format=%H|%s|%an|%ai"]

    if since:
        cmd.extend(["--since", since])
    if until:
        cmd.extend(["--until", until])

    output, success = run_git_command(cmd)

    if not success:
        print(f"⚠️ Erro ao buscar commits: {output}")
        return []

    commits = []
    for line in output.split('\n'):
        if '|' in line:
            parts = line.split('|')
            if len(parts) >= 4:
                commits.append({
                    'hash': parts[0],
                    'message': parts[1],
                    'author': parts[2],
                    'date': parts[3]
                })

    return commits

def extract_jira_keys(commit_message):
    """Extrai chaves de issues Jira de uma mensagem de commit."""
    keys = JIRA_KEY_PATTERN.findall(commit_message)
    # Filtrar apenas chaves do projeto configurado
    return list(set([k for k in keys if k.startswith(PROJECT_KEY.split('-')[0])]))

def validate_commit_message(message):
    """Valida se o commit segue o padrão Conventional Commits."""
    lines = message.split('\n')
    first_line = lines[0]

    if COMMIT_PATTERN.match(first_line):
        return True, "✅ Conventional Commits válido"

    # Verificar se pelo menos tem uma chave de issue
    keys = extract_jira_keys(message)
    if keys:
        return True, f"⚠️ Não é Conventional Commits, mas tem issue: {', '.join(keys)}"

    return False, "❌ Não segue padrão e não tem referência de issue"

# ============================================
# FUNÇÕES DE JIRA
# ============================================

def link_commit_to_issue(issue_key, commit_hash, commit_message):
    """Cria um link de comentário no Jira associando ao commit."""
    url = f"{URL_BASE}/issue/{issue_key}/comment"

    # Formatar como comentário com referência ao commit
    comment = f"""|*Commit*|
|---|
| `{commit_hash[:7]}` |
| *{commit_message[:200]}* |
| |
| [Ver no Git](command:git.show?hash={commit_hash}) |"""

    payload = {"body": comment}
    response = requests.post(url, json=payload, auth=AUTH, headers=HEADERS)

    if response.status_code == 201:
        return True
    return False

def get_issue_comments(issue_key):
    """Busca comentários de uma issue."""
    url = f"{URL_BASE}/issue/{issue_key}/comment"
    response = requests.get(url, auth=AUTH, headers=HEADERS)

    if response.status_code == 200:
        return response.json().get("comments", [])
    return []

def is_commit_linked(issue_key, commit_hash):
    """Verifica se um commit já está linked a uma issue."""
    comments = get_issue_comments(issue_key)

    for comment in comments:
        body = comment.get("body", "")
        if commit_hash[:7] in body or commit_hash in body:
            return True

    return False

# ============================================
# AÇÕES PRINCIPAIS
# ==========================================

def action_link(args):
    """Link commits não relacionados ao Jira."""
    print("🔗 Buscando commits para linkar...")

    commits = get_commits(since=args.since, limit=args.limit)

    if not commits:
        print("Nenhum commit encontrado.")
        return

    linked_count = 0
    skipped_count = 0

    for commit in commits:
        jira_keys = extract_jira_keys(commit['message'])

        if not jira_keys:
            skipped_count += 1
            continue

        for key in jira_keys:
            if is_commit_linked(key, commit['hash']):
                skipped_count += 1
                continue

            if args.dry_run:
                print(f"  [DRY RUN] Linkaria {commit['hash'][:7]} → {key}")
                linked_count += 1
            else:
                if link_commit_to_issue(key, commit['hash'], commit['message']):
                    print(f"  ✅ {commit['hash'][:7]} → {key}: {commit['message'][:50]}...")
                    linked_count += 1
                else:
                    print(f"  ❌ Falha ao linkar {commit['hash'][:7]} → {key}")

    print(f"\n📊 Resultado: {linked_count} linkados, {skipped_count} pulados")

def action_validate(args):
    """Valida formato dos commits."""
    print("🔍 Validando commits...")

    commits = get_commits(limit=args.limit)

    valid_count = 0
    invalid_count = 0

    for commit in commits:
        is_valid, message = validate_commit_message(commit['message'])

        if is_valid:
            valid_count += 1
            status = "✅"
        else:
            invalid_count += 1
            status = "❌"

        print(f"  {status} {commit['hash'][:7]} - {commit['message'][:60]}...")
        print(f"      {message}")

    print(f"\n📊 Resultado: {valid_count} válidos, {invalid_count} inválidos")

    if invalid_count > 0 and not args.continue_on_error:
        print("\n💡 Dica: Configure um pre-commit hook para validar antes de commits")

def action_log(args):
    """Mostra log de commits com issues detectadas."""
    print("📋 Commits com referências de issues:\n")

    commits = get_commits(limit=args.limit)

    for commit in commits:
        keys = extract_jira_keys(commit['message'])

        if keys:
            print(f"  {commit['hash'][:7]} | {commit['date'][:10]} | {keys[0]}")
            print(f"    {commit['message'][:70]}...")
            print()

def action_hook(args):
    """Gera pre-commit hook para validação."""
    hook_content = """#!/bin/bash
# Pre-commit hook para validar Conventional Commits
# Instale em: .git/hooks/pre-commit

PROJECT_KEY="RAG"

# Cores
RED='\\033[0;31m'
GREEN='\\033[0;32m'
YELLOW='\\033[1;33m'
NC='\\033[0m' # No Color

echo "🔍 Validando commit..."

# Pegar mensagem do commit
COMMIT_MSG=$(cat "$1")
FIRST_LINE=$(echo "$COMMIT_MSG" | head -n 1)

# Regex para Conventional Commits
COMMIT_REGEX="^(feat|fix|docs|style|refactor|test|chore|ci|build|perf|revert)(\\([a-zA-Z0-9_-]+\\))?(!)?: .+"

# Verificar Conventional Commits
if [[ "$FIRST_LINE" =~ $COMMIT_REGEX ]]; then
    echo -e "${GREEN}✅ Conventional Commits válido${NC}"
    exit 0
fi

# Verificar se tem referência de issue
if echo "$FIRST_LINE" | grep -qE "($PROJECT_KEY-[0-9]+|[A-Z]{2,}-[0-9]+)"; then
    echo -e "${YELLOW}⚠️ Commit tem referência de issue, mas não segue Conventional Commits${NC}"
    echo "💡 Sugestão: Use o formato: type(scope): description"
    exit 0
fi

# Se chegou aqui, é inválido
echo -e "${RED}❌ Commit inválido!${NC}"
echo "Formato esperado: type(scope): description"
echo "Exemplo: feat(auth): add login with OAuth"
echo ""
echo "Ou inclua uma referência de issue: RAG-123 fix bug"
exit 1
"""

    hook_path = os.path.join(os.getcwd(), ".git", "hooks", "pre-commit")

    # Verificar se git está instalado
    _, success = run_git_command(["git", "rev-parse"])
    if not success:
        print("❌ Este script deve ser executado dentro de um repositório git")
        sys.exit(1)

    with open(hook_path, 'w') as f:
        f.write(hook_content)

    os.chmod(hook_path, 0o755)

    print(f"✅ Pre-commit hook criado em: {hook_path}")
    print("📝 O hook validará commits antes de permitir o push")

# ============================================
# MAIN
# ============================================

def main():
    parser = argparse.ArgumentParser(
        description="Git-Jira Link - Integração entre Commits e Jira",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemplos:
  python git_jira_link.py --link                  # Link commits ao Jira
  python git_jira_link.py --link --dry-run        # Simula sem linkar
  python git_jira_link.py --validate              # Valida Conventional Commits
  python git_jira_link.py --log                   # Mostra commits com issues
  python git_jira_link.py --hook                  # Cria pre-commit hook
        """
    )

    parser.add_argument("--link", action="store_true",
                        help="Link commits não liés ao Jira")
    parser.add_argument("--validate", action="store_true",
                        help="Valida formato dos commits")
    parser.add_argument("--log", action="store_true",
                        help="Mostra commits com issues detectadas")
    parser.add_argument("--hook", action="store_true",
                        help="Gera pre-commit hook para validação")

    parser.add_argument("--dry-run", action="store_true",
                        help="Simula sem fazer alterações")
    parser.add_argument("--since", type=str,
                        help="Data inicial (YYYY-MM-DD)")
    parser.add_argument("--limit", type=int, default=50,
                        help="Número de commits a processar")
    parser.add_argument("--continue-on-error", action="store_true",
                        help="Continua mesmo com commits inválidos")

    args = parser.parse_args()

    if not any([args.link, args.validate, args.log, args.hook]):
        parser.print_help()
        return

    print("=" * 50)
    print("🔗 GIT-JIRA LINK")
    print("=" * 50)

    if args.link:
        action_link(args)
    elif args.validate:
        action_validate(args)
    elif args.log:
        action_log(args)
    elif args.hook:
        action_hook(args)

if __name__ == "__main__":
    main()
