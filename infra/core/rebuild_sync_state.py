#!/usr/bin/env python3
"""
rebuild_sync_state.py
Reconstrói o .sync_state.json a partir do estado real do Jira.

Consulta todos os épicos, tasks e subtasks via API e gera um state
consistente — eliminando a raiz de problemas de duplicação.

Uso:
    python3 rebuild_sync_state.py              # Dry-run (mostra o que seria gerado)
    python3 rebuild_sync_state.py --execute    # Salva o .sync_state.json
"""

import os
import sys
import json
import time
import requests
from datetime import datetime
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

STATE_PATH = Path(__file__).parent.parent / "config" / ".sync_state.json"

# Mapeamento épico → projeto.
# Este dicionário deve ser preenchido pelo operador com os épicos reais do
# seu Jira antes de rodar o script (ex: "GARE-1": "PRJ-XX").
EPIC_TO_PROJECT = {
    # "GARE-1": "PRJ-XX",
}


def jira_search(jql: str, fields: str = "key,summary,status,timetracking,subtasks",
                max_results: int = 100) -> list:
    """Busca issues via JQL."""
    all_issues = []
    start_at = 0

    while True:
        url = f"{base}/search/jql"
        params = {
            "jql": jql,
            "maxResults": max_results,
            "startAt": start_at,
            "fields": fields
        }
        r = requests.get(url, params=params, auth=auth, headers=headers)
        if r.status_code != 200:
            # Fallback
            url = f"{base}/search"
            r = requests.get(url, params=params, auth=auth, headers=headers)
            if r.status_code != 200:
                print(f"  ⚠️  Erro na busca: HTTP {r.status_code}")
                break

        data = r.json()
        issues = data.get("issues", [])
        all_issues.extend(issues)

        if start_at + len(issues) >= data.get("total", 0):
            break
        start_at += len(issues)

    return all_issues


def get_subtasks(parent_key: str) -> list:
    """Busca subtasks de uma task."""
    url = f"{base}/issue/{parent_key}?fields=subtasks"
    r = requests.get(url, auth=auth, headers=headers)
    if r.status_code != 200:
        return []
    return r.json().get("fields", {}).get("subtasks", [])


def get_issue_summary(key: str) -> str:
    """Busca summary de uma issue."""
    url = f"{base}/issue/{key}?fields=summary"
    r = requests.get(url, auth=auth, headers=headers)
    if r.status_code != 200:
        return ""
    return r.json().get("fields", {}).get("summary", "")


def rebuild():
    """Reconstrói o sync state a partir do Jira."""
    state = {
        "version": "2.0",
        "last_sync": datetime.now().isoformat(),
        "rebuilt_from": "Jira API (rebuild_sync_state.py)",
        "projetos": {},
        "epicos": {},
        "tasks": {},
        "subtasks": {},
        "links": {}
    }

    print("\n📋 Fase 1: Registrando épicos...")
    for epic_key, proj_id in EPIC_TO_PROJECT.items():
        if proj_id.endswith("-dup"):
            continue  # Ignorar épicos duplicados
        state["projetos"][proj_id] = {
            "epico_key": epic_key,
            "registered_at": datetime.now().isoformat()
        }
        print(f"  ✅ {proj_id} → {epic_key}")

    print("\n📋 Fase 2: Registrando tasks...")
    task_count = 0
    for epic_key, proj_id in EPIC_TO_PROJECT.items():
        if proj_id.endswith("-dup"):
            continue

        jql = f'project = {PROJECT} AND parent = {epic_key} AND issuetype = Task ORDER BY key ASC'
        tasks = jira_search(jql, fields="key,summary,timetracking,duedate")

        for i, task in enumerate(tasks, 1):
            task_key = task["key"]
            summary = task["fields"]["summary"]
            task_id = f"{proj_id}-TASK-{i}"

            tt = task["fields"].get("timetracking") or {}
            estimate_sec = tt.get("originalEstimateSeconds", 0) or 0
            estimate_str = f"{estimate_sec // 3600}h" if estimate_sec > 0 else ""

            duedate = task["fields"].get("duedate", "")

            state_key = f"{PROJECT}:{task_id}"
            state["tasks"][state_key] = {
                "jira_key": task_key,
                "task_id": task_id,
                "project_key": PROJECT,
                "due_date": duedate or "",
                "estimate": estimate_str,
                "created_at": datetime.now().isoformat()
            }
            task_count += 1
            print(f"  ✅ {task_key} → {task_id} ({summary[:40]}...)")

            # Buscar subtasks
            subtasks = get_subtasks(task_key)
            for st in subtasks:
                st_key = st["key"]
                st_summary = get_issue_summary(st_key)
                st_state_key = f"{task_key}:{st_summary[:40]}"
                state["subtasks"][st_state_key] = {
                    "jira_key": st_key,
                    "parent": task_key,
                    "created_at": datetime.now().isoformat()
                }

            time.sleep(0.3)  # Rate limiting

    print(f"\n📊 Resumo: {len(state['projetos'])} projetos, {task_count} tasks, "
          f"{len(state['subtasks'])} subtasks")

    return state


if __name__ == "__main__":
    dry_run = "--execute" not in sys.argv

    print("=" * 60)
    if dry_run:
        print("🔍 MODO DRY-RUN — State NÃO será salvo.")
        print("   Use --execute para salvar o .sync_state.json")
    else:
        print("🔧 MODO EXECUTE — State será RECONSTRUÍDO e salvo.")
    print("=" * 60)

    state = rebuild()

    if dry_run:
        print(f"\n📄 State que seria salvo ({len(json.dumps(state))} bytes):")
        print(json.dumps(state, indent=2, ensure_ascii=False)[:2000])
        print("... (truncado)")
    else:
        # Backup do state atual
        if STATE_PATH.exists():
            backup_path = STATE_PATH.with_suffix(".json.bak2")
            import shutil
            shutil.copy2(STATE_PATH, backup_path)
            print(f"\n💾 Backup salvo em {backup_path}")

        with open(STATE_PATH, 'w', encoding='utf-8') as f:
            json.dump(state, f, indent=2, ensure_ascii=False)
        print(f"\n✅ State reconstruído e salvo em {STATE_PATH}")

    print("=" * 60)
