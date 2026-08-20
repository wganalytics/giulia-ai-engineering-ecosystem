import os
import sys
import requests
import argparse
from requests.auth import HTTPBasicAuth
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(__file__), '.env'))

JIRA_DOMAIN = os.environ.get("JIRA_DOMAIN")
JIRA_EMAIL = os.environ.get("JIRA_EMAIL")
JIRA_TOKEN = os.environ.get("JIRA_TOKEN")
PROJECT_KEY = os.environ.get("JIRA_PROJECT_KEY")

if not all([JIRA_DOMAIN, JIRA_EMAIL, JIRA_TOKEN, PROJECT_KEY]):
    print("❌ ERRO: Variáveis de ambiente faltando no .env.")
    sys.exit(1)

AUTH = HTTPBasicAuth(JIRA_EMAIL, JIRA_TOKEN)
HEADERS = {"Accept": "application/json", "Content-Type": "application/json"}

def list_issues(target_epic=None):
    jql = f"project={PROJECT_KEY}"
    if target_epic:
        jql += f" AND parent={target_epic}"

    search_url = f"https://{JIRA_DOMAIN}/rest/api/3/search/jql"
    payload = {"jql": jql, "maxResults": 50}
    response = requests.post(search_url, json=payload, auth=AUTH, headers=HEADERS)

    if response.status_code == 200:
        issues = response.json().get('issues', [])
        for issue in issues:
            if 'key' in issue:
                print(f"{issue['key']} | {issue.get('fields', {}).get('status', {}).get('name', 'N/A')} | {issue.get('fields', {}).get('summary', 'N/A')}")
            else:
                print("Issue formato desconhecido:", issue)
    else:
        print(f"Erro ao buscar: {response.text}")

def get_transitions(issue_key):
    trans_url = f"https://{JIRA_DOMAIN}/rest/api/2/issue/{issue_key}/transitions"
    response = requests.get(trans_url, auth=AUTH, headers=HEADERS)
    if response.status_code == 200:
        transitions = response.json().get('transitions', [])
        print(f"Transições para {issue_key}:")
        for t in transitions:
            print(f"[{t['id']}] {t['name']} -> Vai para: {t['to']['name']}")
    else:
        print(f"Erro ao buscar transições: {response.text}")

def transition_issue(issue_key, transition_id):
    url = f"https://{JIRA_DOMAIN}/rest/api/2/issue/{issue_key}/transitions"
    payload = {"transition": {"id": transition_id}}
    response = requests.post(url, json=payload, auth=AUTH, headers=HEADERS)

    if response.status_code == 204:
        print(f"✅ Issue {issue_key} transicionada com sucesso!")
    else:
        print(f"❌ Erro ao transicionar issue: {response.text}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Jira Helper")
    parser.add_argument("--list", action="store_true", help="Lista todas as issues")
    parser.add_argument("--transitions", type=str, metavar="ISSUE_KEY", help="Lista transições possíveis para uma issue")
    parser.add_argument("--move", nargs=2, metavar=("ISSUE_KEY", "TRANSITION_ID"), help="Move a issue usando o ID da transição")

    args = parser.parse_args()

    if args.list:
        list_issues()
    elif args.transitions:
        get_transitions(args.transitions)
    elif args.move:
        transition_issue(args.move[0], args.move[1])
    else:
        parser.print_help()
