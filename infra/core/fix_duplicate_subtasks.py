#!/usr/bin/env python3
"""
fix_duplicate_subtasks.py
Remove subtasks duplicadas mantendo sempre a de menor número (GARE-XX mais baixo).
Lógica: agrupa subtasks por summary, mantém a primeira, deleta as demais.

Uso:
    python3 fix_duplicate_subtasks.py              # Dry-run (auditar)
    python3 fix_duplicate_subtasks.py --execute    # Aplicar correções
"""

import os
import sys
import requests
from collections import defaultdict
from pathlib import Path

try:
    from dotenv import load_dotenv
    config_dir = Path(__file__).parent.parent / "config"
    env_path = config_dir / ".env"
    if env_path.exists():
        load_dotenv(env_path)
    else:
        load_dotenv()
except ImportError:
    pass

DOMAIN = os.getenv("JIRA_DOMAIN")
EMAIL = os.getenv("JIRA_EMAIL")
TOKEN = os.getenv("JIRA_TOKEN")
PROJECT = os.getenv("JIRA_PROJECT_KEY", "GARE")

if not all([DOMAIN, EMAIL, TOKEN]):
    print("❌ ERRO: Variáveis JIRA_DOMAIN, JIRA_EMAIL, JIRA_TOKEN não encontradas.")
    sys.exit(1)

auth = (EMAIL, TOKEN)
headers = {"Accept": "application/json", "Content-Type": "application/json"}
base = f"https://{DOMAIN}/rest/api/3"


def get_subtasks(parent_key: str) -> list:
    """Busca subtasks de um parent via API."""
    url = f"{base}/issue/{parent_key}?fields=subtasks"
    r = requests.get(url, auth=auth, headers=headers)
    if r.status_code != 200:
        print(f"  ⚠️  Erro ao buscar {parent_key}: HTTP {r.status_code}")
        return []
    data = r.json()
    return data.get("fields", {}).get("subtasks", [])


def get_issue_summary(key: str) -> str:
    """Busca summary de uma issue."""
    url = f"{base}/issue/{key}?fields=summary"
    r = requests.get(url, auth=auth, headers=headers)
    if r.status_code != 200:
        return ""
    return r.json().get("fields", {}).get("summary", "")


def delete_issue(key: str) -> int:
    """Deleta a issue — use com cuidado."""
    url = f"{base}/issue/{key}"
    r = requests.delete(url, auth=auth)
    return r.status_code


def audit_parent(parent_key: str, dry_run: bool = True) -> int:
    """Audita um parent para subtasks duplicadas. Retorna quantidade removida."""
    subtasks = get_subtasks(parent_key)
    if not subtasks:
        print(f"  ℹ️  {parent_key}: Sem subtasks.")
        return 0

    by_summary = defaultdict(list)
    for st in subtasks:
        summary = get_issue_summary(st["key"])
        by_summary[summary].append(st["key"])

    removed = 0
    for summary, keys in by_summary.items():
        if len(keys) > 1:
            # Mantém o menor número (primeira criação)
            keys_sorted = sorted(keys, key=lambda k: int(k.split("-")[1]))
            keep = keys_sorted[0]
            to_remove = keys_sorted[1:]
            print(f"\n  ⚠️  DUPLICATA: '{summary[:60]}'")
            print(f"     ✅ Manter: {keep}")
            print(f"     ❌ Remover: {to_remove}")

            if not dry_run:
                for key in to_remove:
                    status = delete_issue(key)
                    if status in (200, 204):
                        print(f"     🗑️  {key} removido (HTTP {status})")
                        removed += 1
                    else:
                        print(f"     ❌ Falha ao remover {key} (HTTP {status})")
            else:
                removed += len(to_remove)

    if removed == 0:
        print(f"  ✅ {parent_key}: Sem duplicatas.")

    return removed


def get_all_tasks_for_epic(epic_key: str) -> list:
    """Busca todas as tasks filhas de um épico via JQL."""
    jql = f'project = {PROJECT} AND parent = {epic_key} AND issuetype = Task'
    url = f"{base}/search/jql"
    r = requests.get(
        url,
        params={"jql": jql, "maxResults": 50, "fields": "key,summary"},
        auth=auth,
        headers=headers
    )
    if r.status_code != 200:
        # Try older endpoint
        url = f"{base}/search"
        r = requests.get(
            url,
            params={"jql": jql, "maxResults": 50, "fields": "key,summary"},
            auth=auth,
            headers=headers
        )
        if r.status_code != 200:
            return []
    return [i["key"] for i in r.json().get("issues", [])]


if __name__ == "__main__":
    dry_run = "--execute" not in sys.argv

    print("=" * 60)
    if dry_run:
        print("🔍 MODO DRY-RUN — Nenhuma alteração será feita.")
        print("   Use --execute para aplicar as correções.")
    else:
        print("🔧 MODO EXECUTE — Duplicatas serão REMOVIDAS.")
    print("=" * 60)

    # Épicos conhecidos do ecossistema GARE.
    # Preencha com os épicos reais do seu Jira antes de rodar o script
    # (ex: "GARE-1": "PRJ-XX (Nome do Projeto) - descrição").
    epics = {
        # "GARE-1": "PRJ-XX (Nome do Projeto) - descrição",
    }

    total_removed = 0

    for epic_key, label in epics.items():
        print(f"\n📋 Auditando: {epic_key} — {label}")

        # Buscar tasks filhas do épico
        tasks = get_all_tasks_for_epic(epic_key)
        if tasks:
            for task_key in tasks:
                print(f"\n  🔹 Task: {task_key}")
                total_removed += audit_parent(task_key, dry_run=dry_run)
        else:
            # O épico pode ter subtasks diretas
            total_removed += audit_parent(epic_key, dry_run=dry_run)

    print(f"\n{'=' * 60}")
    action = "encontradas" if dry_run else "removidas"
    print(f"📊 Total de duplicatas {action}: {total_removed}")
    print("=" * 60)
