#!/usr/bin/env python3
"""
lifecycle_manager.py — Gerenciador de Ciclo de Vida Kanban do Ecossistema GARE

Automatiza transições em cascata no Jira seguindo o fluxo:
    Backlog → Selected for Development → In Progress → Done

Fluxo de abertura (top-down):
    start-project: Épico → In Progress, Tasks filhas → Selected
    start-task:    Task → In Progress, Subtasks filhas → Selected
    start-subtask: Subtask → In Progress

Fluxo de fechamento (bottom-up):
    complete:      Card → Done, verifica auto-promoção do pai

Uso:
    python3 ecosystem/jira/lifecycle_manager.py start-project GARE-88
    python3 ecosystem/jira/lifecycle_manager.py start-task GARE-89
    python3 ecosystem/jira/lifecycle_manager.py start-subtask GARE-96
    python3 ecosystem/jira/lifecycle_manager.py complete GARE-89 --nota "Texto técnico..."
    python3 ecosystem/jira/lifecycle_manager.py status GARE-88
"""

from __future__ import annotations

import os
import sys
import argparse
import time
import json
import requests
from datetime import datetime
from pathlib import Path
from requests.auth import HTTPBasicAuth

# Setup path for imports
root_dir = Path(__file__).resolve().parents[2]
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))

try:
    from ecosystem.jira.context_loader import JIRA_DOMAIN, JIRA_EMAIL, JIRA_TOKEN, get_current_jira_project_key
except ImportError as e:
    print(f"⚠️ Aviso: Não foi possível carregar ecosystem/jira/context_loader.py: {e}")
    JIRA_DOMAIN = os.environ.get("JIRA_DOMAIN")
    JIRA_EMAIL = os.environ.get("JIRA_EMAIL")
    JIRA_TOKEN = os.environ.get("JIRA_TOKEN")
    def get_current_jira_project_key(): return None

PROJECT_KEY = get_current_jira_project_key()
if not PROJECT_KEY:
    PROJECT_KEY = os.environ.get("JIRA_PROJECT_KEY", "GARE")
START_DATE_FIELD = os.environ.get("JIRA_START_DATE_FIELD", "customfield_10015")

if not all([JIRA_DOMAIN, JIRA_EMAIL, JIRA_TOKEN]):
    print("❌ ERRO: Variáveis JIRA_DOMAIN, JIRA_EMAIL, JIRA_TOKEN não encontradas.")
    sys.exit(1)

AUTH = HTTPBasicAuth(JIRA_EMAIL, JIRA_TOKEN)
HEADERS = {"Accept": "application/json", "Content-Type": "application/json"}
BASE = f"https://{JIRA_DOMAIN}/rest/api/3"

# IDs de transição do board GARE (confirmados via API)
TRANSITION_IDS = {
    "Backlog": "11",
    "Selected for Development": "21",
    "In Progress": "31",
    "Done": "41",
}


# ============================================
# FUNÇÕES BASE
# ============================================

def api_get(endpoint: str, params: dict = None) -> dict | None:
    """GET request à API do Jira."""
    url = f"{BASE}{endpoint}"
    r = requests.get(url, params=params, auth=AUTH, headers=HEADERS)
    if r.status_code == 200:
        return r.json()
    return None


def api_put(endpoint: str, payload: dict) -> bool:
    """PUT request à API do Jira."""
    url = f"{BASE}{endpoint}"
    r = requests.put(url, json=payload, auth=AUTH, headers=HEADERS)
    return r.status_code in (200, 204)


def api_post(endpoint: str, payload: dict) -> dict | None:
    """POST request à API do Jira."""
    url = f"{BASE}{endpoint}"
    r = requests.post(url, json=payload, auth=AUTH, headers=HEADERS)
    if r.status_code in (200, 201, 204):
        if r.status_code == 204:
            return {"success": True}
        return r.json()
    return None


def get_issue(key: str) -> dict | None:
    """Busca dados de uma issue."""
    return api_get(f"/issue/{key}?fields=summary,status,issuetype,parent,subtasks")


def get_issue_status(key: str) -> str:
    """Retorna o status atual de uma issue."""
    data = api_get(f"/issue/{key}?fields=status")
    if data:
        return data["fields"]["status"]["name"]
    return ""


def get_children(parent_key: str, child_type: str = "Task") -> list[dict]:
    """Busca issues filhas de um parent via JQL."""
    jql = f'project = {PROJECT_KEY} AND parent = {parent_key} ORDER BY key ASC'
    payload = {"jql": jql, "maxResults": 100, "fields": ["key", "summary", "status"]}
    result = api_post("/search/jql", payload)
    if result:
        return result.get("issues", [])
    return []


def log_handoff_trace(issue_key: str, status: str, justification: str = "Transicao automatica de lifecycle") -> None:
    """Log the state change into the project's handoff_trace.jsonl if it exists in the CWD."""
    trace_path = Path("handoff_trace.jsonl")
    if not trace_path.exists():
        alt_path = Path("../handoff_trace.jsonl")
        if alt_path.exists():
            trace_path = alt_path
        else:
            return

    record = {
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "projeto_id": PROJECT_KEY,
        "jira_issue_key": issue_key,
        "skill_utilizada": "lifecycle_manager",
        "solucao_decidida": f"Card movido para {status}",
        "justification": justification,
        "status": status,
        "consecutive_failures": 0
    }
    try:
        with open(trace_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(record) + "\n")
        print(f"  📝 Handoff trace local atualizado ({issue_key} -> {status})")
    except Exception as e:
        print(f"  ⚠️ Falha ao salvar handoff_trace.jsonl: {e}")


def transition_issue(key: str, target_status: str) -> bool:
    """Move uma issue para o status alvo usando transition ID."""
    transition_id = TRANSITION_IDS.get(target_status)
    if not transition_id:
        print(f"  ❌ Status '{target_status}' não mapeado.")
        return False

    # Verificar status atual para não fazer transição desnecessária
    current = get_issue_status(key)
    if current == target_status:
        return True  # Já está no status correto

    payload = {"transition": {"id": transition_id}}
    result = api_post(f"/issue/{key}/transitions", payload)
    if result:
        log_handoff_trace(key, target_status)
        return True
    print(f"  ❌ Falha ao mover {key} para {target_status}")
    return False


def set_start_date(key: str) -> None:
    """Define Start Date = hoje."""
    today = datetime.now().strftime("%Y-%m-%d")
    payload = {"fields": {START_DATE_FIELD: today}}
    if api_put(f"/issue/{key}", payload):
        print(f"  📅 Start Date: {today}")
    else:
        print(f"  ⚠️  Não foi possível definir Start Date para {key}")


def add_comment(key: str, text: str) -> None:
    """Adiciona comentário ADF a uma issue."""
    payload = {
        "body": {
            "type": "doc",
            "version": 1,
            "content": [{"type": "paragraph", "content": [{"type": "text", "text": text}]}]
        }
    }
    api_post(f"/issue/{key}/comment", payload)


# ============================================
# COMANDOS PRINCIPAIS
# ============================================

def cmd_start_project(epic_key: str) -> None:
    """
    Inicia um projeto inteiro:
    1. Épico → In Progress + Start Date
    2. Todas Tasks filhas → Selected for Development
    """
    issue = get_issue(epic_key)
    if not issue:
        print(f"❌ Épico {epic_key} não encontrado.")
        return

    issue_type = issue["fields"]["issuetype"]["name"]
    summary = issue["fields"]["summary"]
    current_status = issue["fields"]["status"]["name"]

    print(f"\n{'='*60}")
    print(f"🚀 INICIANDO PROJETO: {epic_key}")
    print(f"   {summary}")
    print(f"   Status atual: {current_status}")
    print(f"{'='*60}")

    # 1. Mover épico para In Progress
    print(f"\n📋 Fase 1: Mover épico para In Progress...")
    if transition_issue(epic_key, "In Progress"):
        print(f"  ✅ {epic_key} → In Progress")
        set_start_date(epic_key)
    else:
        print(f"  ❌ Falha ao mover {epic_key}")
        return

    # 2. Mover todas tasks filhas para Selected for Development
    print(f"\n📋 Fase 2: Mover tasks para Selected for Development...")
    tasks = get_children(epic_key)
    moved = 0
    for task in tasks:
        task_key = task["key"]
        task_status = task["fields"]["status"]["name"]
        task_summary = task["fields"]["summary"]

        if task_status == "Backlog":
            if transition_issue(task_key, "Selected for Development"):
                print(f"  ✅ {task_key} → Selected ({task_summary[:45]}...)")
                moved += 1
            time.sleep(0.2)
        else:
            print(f"  ⏭️  {task_key} já está em '{task_status}' — pulando")

    print(f"\n{'='*60}")
    print(f"✅ Projeto {epic_key} iniciado!")
    print(f"   {moved}/{len(tasks)} tasks movidas para 'Selected for Development'")
    print(f"{'='*60}")

    add_comment(epic_key,
        f"🚀 Projeto iniciado via lifecycle_manager.py\n"
        f"• {moved}/{len(tasks)} tasks movidas para 'Selected for Development'\n"
        f"• Start Date: {datetime.now().strftime('%Y-%m-%d')}")


def cmd_start_task(task_key: str) -> None:
    """
    Inicia uma task:
    1. Task → In Progress + Start Date
    2. Subtasks filhas → Selected for Development
    """
    issue = get_issue(task_key)
    if not issue:
        print(f"❌ Task {task_key} não encontrada.")
        return

    summary = issue["fields"]["summary"]
    current_status = issue["fields"]["status"]["name"]

    print(f"\n{'='*60}")
    print(f"▶️  INICIANDO TASK: {task_key}")
    print(f"   {summary}")
    print(f"   Status atual: {current_status}")
    print(f"{'='*60}")

    # 1. Mover task para In Progress
    print(f"\n📋 Fase 1: Mover task para In Progress...")
    if transition_issue(task_key, "In Progress"):
        print(f"  ✅ {task_key} → In Progress")
        set_start_date(task_key)
    else:
        print(f"  ❌ Falha ao mover {task_key}")
        return

    # 2. Mover subtasks para Selected
    subtasks = issue["fields"].get("subtasks", [])
    if subtasks:
        print(f"\n📋 Fase 2: Mover {len(subtasks)} subtasks para Selected...")
        moved = 0
        for st in subtasks:
            st_key = st["key"]
            st_status = get_issue_status(st_key)
            if st_status == "Backlog":
                if transition_issue(st_key, "Selected for Development"):
                    st_summary = st.get("fields", {}).get("summary", "")
                    print(f"  ✅ {st_key} → Selected ({st_summary[:40]}...)")
                    moved += 1
                time.sleep(0.2)
            else:
                print(f"  ⏭️  {st_key} já está em '{st_status}'")

        print(f"\n  📊 {moved}/{len(subtasks)} subtasks movidas para Selected")
    else:
        print(f"\n  ℹ️  Task sem subtasks.")

    print(f"\n{'='*60}")
    print(f"✅ Task {task_key} iniciada!")
    print(f"{'='*60}")


def cmd_start_subtask(subtask_key: str) -> None:
    """
    Inicia uma subtask:
    1. Subtask → In Progress + Start Date
    """
    issue = get_issue(subtask_key)
    if not issue:
        print(f"❌ Subtask {subtask_key} não encontrada.")
        return

    summary = issue["fields"]["summary"]

    print(f"\n▶️  Iniciando subtask: {subtask_key} — {summary}")

    if transition_issue(subtask_key, "In Progress"):
        print(f"  ✅ {subtask_key} → In Progress")
        set_start_date(subtask_key)
    else:
        print(f"  ❌ Falha ao mover {subtask_key}")


def cmd_complete(key: str, nota: str = "") -> None:
    """
    Conclui um card:
    1. Card → Done
    2. Verifica auto-promoção do pai (se todos irmãos = Done)
    """
    issue = get_issue(key)
    if not issue:
        print(f"❌ Issue {key} não encontrada.")
        return

    summary = issue["fields"]["summary"]
    issue_type = issue["fields"]["issuetype"]["name"]

    print(f"\n{'='*60}")
    print(f"✅ CONCLUINDO: {key} ({issue_type})")
    print(f"   {summary}")
    print(f"{'='*60}")

    # Exigir nota técnica para Tasks (não para subtasks)
    if issue_type == "Task" and (not nota or len(nota.strip()) < 50):
        print("\n❌ ERRO: Nota técnica obrigatória para Tasks (mínimo 50 caracteres).")
        print('   Use: --nota "Descrição técnica detalhada..."')
        sys.exit(1)

    # 1. Mover para Done
    if transition_issue(key, "Done"):
        print(f"  ✅ {key} → Done")
    else:
        print(f"  ❌ Falha ao mover {key}")
        return

    # 2. Adicionar comentário técnico (se fornecido)
    if nota:
        add_comment(key,
            f"✅ Concluído via lifecycle_manager.py\n\n"
            f"📝 Nota técnica:\n{nota}\n\n"
            f"📅 Data: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
        print(f"  📝 Nota técnica registrada")

    # 3. Auto-promoção do pai
    parent = issue["fields"].get("parent")
    if parent:
        parent_key = parent["key"]
        print(f"\n🔍 Verificando auto-promoção do pai ({parent_key})...")
        check_auto_promote(parent_key)


def check_auto_promote(parent_key: str) -> None:
    """
    Verifica se todos os filhos de um parent estão em Done.
    Se sim, promove o parent automaticamente.
    """
    children = get_children(parent_key)
    if not children:
        return

    total = len(children)
    done = sum(1 for c in children if c["fields"]["status"]["name"] == "Done")
    pending = total - done

    print(f"  📊 Filhos de {parent_key}: {done}/{total} concluídos")

    if pending == 0:
        parent_status = get_issue_status(parent_key)
        if parent_status != "Done":
            print(f"\n  🎉 Todos filhos concluídos! Promovendo {parent_key} para Done...")
            if transition_issue(parent_key, "Done"):
                print(f"  ✅ {parent_key} → Done (auto-promovido)")
                add_comment(parent_key,
                    f"🎉 Auto-promovido para Done pelo lifecycle_manager.py\n"
                    f"• Todos {total} filhos concluídos\n"
                    f"• Data: {datetime.now().strftime('%Y-%m-%d %H:%M')}")

                # Verificar promoção do avô (ex: task → épico)
                parent_data = get_issue(parent_key)
                grandparent = parent_data.get("fields", {}).get("parent") if parent_data else None
                if grandparent:
                    grandparent_key = grandparent["key"]
                    print(f"\n  🔍 Verificando auto-promoção do avô ({grandparent_key})...")
                    check_auto_promote(grandparent_key)
    else:
        print(f"  ℹ️  Ainda faltam {pending} filhos — {parent_key} permanece no status atual")


def cmd_status(epic_key: str) -> None:
    """Mostra o status completo de um projeto (épico + tasks + subtasks)."""
    issue = get_issue(epic_key)
    if not issue:
        print(f"❌ Épico {epic_key} não encontrado.")
        return

    summary = issue["fields"]["summary"]
    status = issue["fields"]["status"]["name"]

    STATUS_EMOJI = {
        "Backlog": "⚪",
        "Selected for Development": "🔵",
        "In Progress": "🟡",
        "Done": "🟢"
    }

    print(f"\n{'='*60}")
    print(f"📊 STATUS DO PROJETO: {epic_key}")
    print(f"   {summary}")
    print(f"   {STATUS_EMOJI.get(status, '❓')} {status}")
    print(f"{'='*60}")

    tasks = get_children(epic_key)
    if not tasks:
        print("  ℹ️  Sem tasks.")
        return

    total_tasks = len(tasks)
    done_tasks = 0

    for task in tasks:
        task_key = task["key"]
        task_status = task["fields"]["status"]["name"]
        task_summary = task["fields"]["summary"]
        emoji = STATUS_EMOJI.get(task_status, "❓")

        if task_status == "Done":
            done_tasks += 1

        print(f"\n  {emoji} [{task_key}] {task_summary[:50]}")
        print(f"     Status: {task_status}")

        # Buscar subtasks
        task_detail = get_issue(task_key)
        subtasks = task_detail["fields"].get("subtasks", []) if task_detail else []
        for st in subtasks:
            st_key = st["key"]
            st_status = get_issue_status(st_key)
            st_summary = st.get("fields", {}).get("summary", "")
            st_emoji = STATUS_EMOJI.get(st_status, "❓")
            print(f"       {st_emoji} [{st_key}] {st_summary[:40]}")

    print(f"\n{'='*60}")
    if total_tasks > 0:
        print(f"📈 Progresso: {done_tasks}/{total_tasks} tasks concluídas "
              f"({(done_tasks/total_tasks*100):.0f}%)")
    else:
        print("📈 Progresso: Nenhuma task cadastrada")
    print(f"{'='*60}")


# ============================================
# MAIN
# ============================================

def main():
    parser = argparse.ArgumentParser(
        description="🔄 Lifecycle Manager — Gerenciador de Ciclo de Vida Kanban",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemplos:
  python3 lifecycle_manager.py start-project GARE-88   # Inicia projeto (épico + tasks)
  python3 lifecycle_manager.py start-task GARE-89      # Inicia task (+ subtasks)
  python3 lifecycle_manager.py start-subtask GARE-96   # Inicia subtask
  python3 lifecycle_manager.py complete GARE-89 --nota "Texto..."  # Conclui com nota
  python3 lifecycle_manager.py status GARE-88          # Status do projeto
        """
    )

    subparsers = parser.add_subparsers(dest="command", help="Comando a executar")

    # start-project
    sp = subparsers.add_parser("start-project", help="Inicia projeto (épico → In Progress, tasks → Selected)")
    sp.add_argument("key", help="Key do épico (ex: GARE-88)")

    # start-task
    st = subparsers.add_parser("start-task", help="Inicia task (→ In Progress, subtasks → Selected)")
    st.add_argument("key", help="Key da task (ex: GARE-89)")

    # start-subtask
    ss = subparsers.add_parser("start-subtask", help="Inicia subtask (→ In Progress)")
    ss.add_argument("key", help="Key da subtask")

    # complete
    cp = subparsers.add_parser("complete", help="Conclui card (→ Done, verifica auto-promoção)")
    cp.add_argument("key", help="Key do card")
    cp.add_argument("--nota", type=str, default="", help="Nota técnica (obrigatória para Tasks)")

    # status
    stt = subparsers.add_parser("status", help="Mostra status completo de um projeto")
    stt.add_argument("key", help="Key do épico")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return

    if args.command == "start-project":
        cmd_start_project(args.key.upper())
    elif args.command == "start-task":
        cmd_start_task(args.key.upper())
    elif args.command == "start-subtask":
        cmd_start_subtask(args.key.upper())
    elif args.command == "complete":
        cmd_complete(args.key.upper(), args.nota)
    elif args.command == "status":
        cmd_status(args.key.upper())


if __name__ == "__main__":
    main()
