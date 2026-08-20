#!/usr/bin/env python3
"""
Jira Manager - Gerenciador completo de Épicos, Tasks e Subtarefas
用法: python jira_manager.py --help
"""

import os
import sys
import requests
import argparse
import json
from datetime import datetime, timedelta
from requests.auth import HTTPBasicAuth
from dotenv import load_dotenv

from dotenv import load_dotenv
from pathlib import Path

# Carrega .env da pasta config
config_dir = Path(__file__).parent.parent / "config"
env_path = config_dir / ".env"
if env_path.exists():
    load_dotenv(env_path)
else:
    load_dotenv(os.path.join(os.path.dirname(__file__), '../config/.env'))

JIRA_DOMAIN = os.environ.get("JIRA_DOMAIN")
JIRA_EMAIL = os.environ.get("JIRA_EMAIL")
JIRA_TOKEN = os.environ.get("JIRA_TOKEN")
PROJECT_KEY = os.environ.get("JIRA_PROJECT_KEY")

if not all([JIRA_DOMAIN, JIRA_EMAIL, JIRA_TOKEN, PROJECT_KEY]):
    print("❌ ERRO: Variáveis de ambiente faltando no .env.")
    sys.exit(1)

AUTH = HTTPBasicAuth(JIRA_EMAIL, JIRA_TOKEN)
HEADERS = {"Accept": "application/json", "Content-Type": "application/json"}

BASE_URL = f"https://{JIRA_DOMAIN}/rest/api/3"


def make_request(method, endpoint, **kwargs):
    url = f"{BASE_URL}{endpoint}"
    
    if method == "POST" and "search/jql" not in endpoint:
        # Para endpoints que não são search/jql, ainda usa POST
        response = requests.post(url, auth=AUTH, headers=HEADERS, **kwargs)
    elif method == "GET":
        response = requests.get(url, auth=AUTH, headers=HEADERS, **kwargs)
    else:
        response = requests.request(method, url, auth=AUTH, headers=HEADERS, **kwargs)
    
    if response.status_code in [200, 201, 204]:
        if response.status_code == 204:
            return {"success": True}
        return response.json()
    else:
        print(f"❌ Erro {response.status_code}: {response.text[:200]}...")
        return None


# ============================================
# FUNÇÕES DE CONSULTA
# ============================================

def list_epics():
    """Lista todos os épicos do projeto"""
    jql = f"project={PROJECT_KEY} AND type=Epic ORDER BY created DESC"
    payload = {"jql": jql, "maxResults": 100, "fields": ["summary", "status", "assignee", "created", "duedate", "priority", "labels", "parent"]}
    result = make_request("POST", "/search/jql", json=payload)
    if result:
        issues = result.get("issues", [])
    if result:
        issues = result.get("issues", [])
        print(f"\n{'='*80}")
        print(f"📋 ÉPICOS DO PROJETO {PROJECT_KEY} ({len(issues)} encontrados)")
        print(f"{'='*80}\n")
        for issue in issues:
            fields = issue.get("fields", {})
            status = fields.get("status", {}).get("name", "N/A")
            assignee = fields.get("assignee", {})
            assignee_name = assignee.get("displayName", "Não atribuído") if assignee else "Não atribuído"
            print(f"[{issue['key']}] {fields.get('summary', 'N/A')}")
            print(f"   📊 Status: {status} | 👤 Responsável: {assignee_name}")
            print(f"   📅 Criado: {fields.get('created', 'N/A')[:10]}")
            if fields.get("duedate"):
                print(f"   ⏰ Prazo: {fields.get('duedate')}")
            print()
    return result


def list_tasks(epic_key=None):
    """Lista tasks, opcionalmente filtradas por épico"""
    if epic_key:
        jql = f"project={PROJECT_KEY} AND type=Task AND parent={epic_key} ORDER BY created DESC"
    else:
        jql = f"project={PROJECT_KEY} AND type=Task ORDER BY created DESC"
    
    payload = {"jql": jql, "maxResults": 100, "fields": ["summary", "status", "priority", "labels", "parent", "created"]}
    result = make_request("POST", "/search/jql", json=payload)
    if result:
        issues = result.get("issues", [])
        parent = f" do épico {epic_key}" if epic_key else ""
        print(f"\n{'='*80}")
        print(f"📝 TASKS{parent} ({len(issues)} encontradas)")
        print(f"{'='*80}\n")
        
        for issue in issues:
            fields = issue.get("fields", {})
            status = fields.get("status", {}).get("name", "N/A")
            priority = fields.get("priority", {}).get("name", "N/A")
            labels = fields.get("labels", [])
            labels_str = f" [{', '.join(labels)}]" if labels else ""
            
            print(f"[{issue['key']}] {fields.get('summary', 'N/A')}")
            print(f"   📊 Status: {status} | ⚡ Prioridade: {priority}{labels_str}")
            print()
    return result


def list_subtasks(task_key):
    """Lista subtarefas de uma task"""
    jql = f"project={PROJECT_KEY} AND parent={task_key} ORDER BY created DESC"
    payload = {"jql": jql, "maxResults": 50, "fields": ["summary", "status", "created"]}
    result = make_request("POST", "/search/jql", json=payload)
    if result:
        issues = result.get("issues", [])
        print(f"\n{'='*80}")
        print(f"🔹 SUBTASKS da task {task_key} ({len(issues)} encontradas)")
        print(f"{'='*80}\n")
        for issue in issues:
            fields = issue.get("fields", {})
            status = fields.get("status", {}).get("name", "N/A")
            print(f"[{issue['key']}] {fields.get('summary', 'N/A')}")
            print(f"   📊 Status: {status}")
            print()
    return result


def get_issue_details(issue_key):
    """Mostra todos os detalhes de uma issue (épico, task ou subtask)"""
    result = make_request("GET", f"/issue/{issue_key}")
    if result:
        fields = result.get("fields", {})
        issue_type = fields.get("issuetype", {}).get("name", "N/A")
        
        print(f"\n{'='*80}")
        print(f"🔍 DETALHES DA {issue_type.upper()}: {issue_key}")
        print(f"{'='*80}\n")
        
        print(f"📌 Resumo: {fields.get('summary', 'N/A')}")
        print(f"📋 Tipo: {issue_type}")
        print(f"📊 Status: {fields.get('status', {}).get('name', 'N/A')}")
        print(f"⚡ Prioridade: {fields.get('priority', {}).get('name', 'N/A')}")
        
        assignee = fields.get("assignee")
        if assignee:
            print(f"👤 Responsável: {assignee.get('displayName', 'N/A')}")
        else:
            print(f"👤 Responsável: Não atribuído")
        
        print(f"📅 Criado em: {fields.get('created', 'N/A')}")
        
        start_date = fields.get("customfield_10015") or fields.get("startDate")
        if start_date:
            print(f"▶️  Início: {start_date}")
        
        due_date = fields.get("duedate") or fields.get("dueDate")
        if due_date:
            print(f"⏰ Prazo: {due_date}")
        
        time_tracking = fields.get("timetracking", {})
        if time_tracking:
            original = time_tracking.get("originalEstimateSeconds", 0)
            remaining = time_tracking.get("remainingEstimateSeconds", 0)
            if original:
                hours = original / 3600
                print(f"⏱️  Estimativa Original: {hours}h")
            if remaining:
                hours = remaining / 3600
                print(f"⏱️  Restante: {hours}h")
        
        labels = fields.get("labels", [])
        if labels:
            print(f"🏷️  Labels: {', '.join(labels)}")
        
        parent = fields.get("parent")
        if parent:
            print(f"📦 Pai: [{parent.get('key')}] {parent.get('summary', 'N/A')}")
        
        print(f"\n📝 Descrição:")
        desc = fields.get("description")
        if desc:
            if isinstance(desc, dict):
                content = desc.get("content", [])
                for block in content:
                    for item in block.get("content", []):
                        print(f"   {item.get('text', '')}")
            else:
                print(f"   {desc}")
        else:
            print("   (sem descrição)")
        
        print(f"\n🔗 Links:")
        issuelinks = fields.get("issuelinks", [])
        if issuelinks:
            for link in issuelinks:
                if "outwardIssue" in link:
                    out = link["outwardIssue"]
                    print(f"   → [{out['key']}] {out.get('summary', '')}")
                if "inwardIssue" in link:
                    inn = link["inwardIssue"]
                    print(f"   ← [{inn['key']}] {inn.get('summary', '')}")
        else:
            print("   (sem links)")
        
        print()
    return result


def update_issue(issue_key, **kwargs):
    """Atualiza campos de uma issue"""
    fields = {}
    
    if "summary" in kwargs:
        fields["summary"] = kwargs["summary"]
    if "description" in kwargs:
        fields["description"] = {"type": "doc", "version": 1, "content": [{"type": "paragraph", "content": [{"type": "text", "text": kwargs["description"]}]}]}
    if "priority" in kwargs:
        fields["priority"] = {"name": kwargs["priority"]}
    if "duedate" in kwargs:
        fields["duedate"] = kwargs["duedate"]
    if "startdate" in kwargs:
        fields["customfield_10015"] = kwargs["startdate"]
    if "storypoints" in kwargs:
        fields["customfield_10033"] = kwargs["storypoints"]
    if "originalestimate" in kwargs:
        hours = kwargs["originalestimate"]
        seconds = int(hours * 3600)
        fields["timetracking"] = {"originalEstimateSeconds": seconds}
    
    payload = {"fields": fields} if fields else {}
    
    result = make_request("PUT", f"/issue/{issue_key}", json=payload)
    if result and result.get("success"):
        print(f"✅ Issue {issue_key} atualizada com sucesso!")
    return result


def move_issue(issue_key, status_name):
    """Move uma issue para um novo status"""
    transitions = make_request("GET", f"/issue/{issue_key}/transitions")
    if not transitions:
        print(f"❌ Não foi possível buscar transições para {issue_key}")
        return None
    
    trans_list = transitions.get("transitions", [])
    
    status_lower = status_name.lower()
    target_transition = None
    
    for trans in trans_list:
        if trans["to"]["name"].lower() == status_lower:
            target_transition = trans
            break
    
    if not target_transition:
        available = [t["to"]["name"] for t in trans_list]
        print(f"❌ Status '{status_name}' não disponível. Status disponíveis: {', '.join(available)}")
        return None
    
    result = make_request("POST", f"/issue/{issue_key}/transitions", 
                         json={"transition": {"id": target_transition["id"]}})
    if result and result.get("success"):
        print(f"✅ Issue {issue_key} movida para '{target_transition['to']['name']}'")
    return result


def assign_issue(issue_key, assignee_name=None):
    """Atribui uma issue a alguém"""
    if assignee_name:
        account_id = input(f"Digite o accountId do usuário (ou Enter para desatribuir): ").strip()
        if not account_id:
            payload = {"name": None}
        else:
            payload = {"accountId": account_id}
    else:
        payload = {"name": None}
    
    result = make_request("PUT", f"/issue/{issue_key}/assignee", json=payload)
    if result and result.get("success"):
        print(f"✅ Issue {issue_key} atualizada")
    return result


def add_comment(issue_key, comment):
    """Adiciona comentário a uma issue"""
    payload = {
        "body": {
            "type": "doc",
            "version": 1,
            "content": [{"type": "paragraph", "content": [{"type": "text", "text": comment}]}]
        }
    }
    result = make_request("POST", f"/issue/{issue_key}/comment", json=payload)
    if result:
        print(f"✅ Comentário adicionado a {issue_key}")
    return result


def list_all():
    """Lista épicos, tasks e subtasks"""
    list_epics()
    list_tasks()
    print("\n" + "="*80)
    print("📊 RESUMO COMPLETO")
    print("="*80)


def interactive_mode():
    """Modo interativo de gerenciamento"""
    print("\n🎯 MODO INTERATIVO - Jira Manager")
    print("="*50)
    print("1. Listar todos os épicos")
    print("2. Listar todas as tasks")
    print("3. Listar tasks de um épico específico")
    print("4. Ver detalhes de uma issue")
    print("5. Atualizar resumo (summary)")
    print("6. Atualizar descrição")
    print("7. Atualizar prioridade")
    print("8. Atualizar prazo (due date)")
    print("9. Mover status")
    print("10. Adicionar comentário")
    print("11. Listar subtasks de uma task")
    print("0. Sair")
    print("="*50)
    
    choice = input("\nEscolha uma opção: ").strip()
    
    if choice == "1":
        list_epics()
    elif choice == "2":
        list_tasks()
    elif choice == "3":
        epic = input("Digite a key do épico (ex: RAG-1): ").strip()
        list_tasks(epic)
    elif choice == "4":
        key = input("Digite a key da issue (ex: RAG-1 ou RAG-101): ").strip()
        get_issue_details(key)
    elif choice == "5":
        key = input("Key da issue: ").strip()
        new_summary = input("Novo resumo: ").strip()
        update_issue(key, summary=new_summary)
    elif choice == "6":
        key = input("Key da issue: ").strip()
        desc = input("Nova descrição: ").strip()
        update_issue(key, description=desc)
    elif choice == "7":
        key = input("Key da issue: ").strip()
        print("Prioridades: Highest, High, Medium, Low, Lowest")
        priority = input("Nova prioridade: ").strip()
        update_issue(key, priority=priority)
    elif choice == "8":
        key = input("Key da issue: ").strip()
        due = input("Novo prazo (YYYY-MM-DD): ").strip()
        update_issue(key, duedate=due)
    elif choice == "9":
        key = input("Key da issue: ").strip()
        print("Status disponíveis: To Do, In Progress, Done")
        status = input("Novo status: ").strip()
        move_issue(key, status)
    elif choice == "10":
        key = input("Key da issue: ").strip()
        comment = input("Comentário: ").strip()
        add_comment(key, comment)
    elif choice == "11":
        key = input("Key da task: ").strip()
        list_subtasks(key)
    elif choice == "0":
        print("👋 Saindo...")
    else:
        print("❌ Opção inválida")


def main():
    parser = argparse.ArgumentParser(
        description="🎯 Jira Manager - Gerenciador completo de Épicos e Tasks",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemplos de uso:
  python jira_manager.py --epics                  # Lista todos os épicos
  python jira_manager.py --tasks                   # Lista todas as tasks
  python jira_manager.py --tasks RAG-1             # Lista tasks do épico RAG-1
  python jira_manager.py --details RAG-101        # Ver detalhes da task RAG-101
  python jira_manager.py --details RAG-1           # Ver detalhes do épico RAG-1
  python jira_manager.py --update RAG-101 --summary "Novo título"
  python jira_manager.py --move RAG-101 "In Progress"
  python jira_manager.py --comment RAG-101 "Teste de comentário"
  python jira_manager.py --subtasks RAG-101        # Lista subtasks
  python jira_manager.py --all                     # Lista tudo
  python jira_manager.py --interactive             # Modo interativo
        """
    )
    
    parser.add_argument("--epics", action="store_true", help="Lista todos os épicos")
    parser.add_argument("--tasks", nargs="?", const="all", metavar="EPIC_KEY", help="Lista tasks (opcional: filtrar por épico)")
    parser.add_argument("--details", metavar="ISSUE_KEY", help="Mostra detalhes completos de uma issue")
    parser.add_argument("--subtasks", metavar="TASK_KEY", help="Lista subtarefas de uma task")
    parser.add_argument("--update", metavar="ISSUE_KEY", help="Atualiza uma issue")
    parser.add_argument("--summary", help="Novo resumo (usar com --update)")
    parser.add_argument("--description", help="Nova descrição (usar com --update)")
    parser.add_argument("--priority", help="Nova prioridade: Highest, High, Medium, Low, Lowest")
    parser.add_argument("--duedate", help="Novo prazo: YYYY-MM-DD")
    parser.add_argument("--storypoints", type=int, help="Story Points (para tasks)")
    parser.add_argument("--estimate", type=float, help="Estimativa em horas (original estimate)")
    parser.add_argument("--move", nargs=2, metavar=("ISSUE_KEY", "STATUS"), help="Move issue para novo status")
    parser.add_argument("--comment", nargs=2, metavar=("ISSUE_KEY", "TEXT"), help="Adiciona comentário")
    parser.add_argument("--all", action="store_true", help="Lista épicos, tasks e subtasks")
    parser.add_argument("--interactive", action="store_true", help="Modo interativo")
    
    args = parser.parse_args()
    
    if args.epics:
        list_epics()
    elif args.tasks is not None:
        if args.tasks == "all":
            list_tasks()
        else:
            list_tasks(args.tasks)
    elif args.details:
        get_issue_details(args.details)
    elif args.subtasks:
        list_subtasks(args.subtasks)
    elif args.update:
        kwargs = {}
        if args.summary:
            kwargs["summary"] = args.summary
        if args.description:
            kwargs["description"] = args.description
        if args.priority:
            kwargs["priority"] = args.priority
        if args.duedate:
            kwargs["duedate"] = args.duedate
        if args.storypoints:
            kwargs["storypoints"] = args.storypoints
        if args.estimate:
            kwargs["originalestimate"] = args.estimate
        if kwargs:
            update_issue(args.update, **kwargs)
        else:
            print("❌ Nenhum campo para atualizar. Use --summary, --description, --priority, --duedate, --storypoints ou --estimate")
    elif args.move:
        move_issue(args.move[0], args.move[1])
    elif args.comment:
        add_comment(args.comment[0], args.comment[1])
    elif args.all:
        list_all()
    elif args.interactive:
        interactive_mode()
    else:
        parser.print_help()


if __name__ == "__main__":
    main()