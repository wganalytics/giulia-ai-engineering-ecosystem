import os
import requests
from requests.auth import HTTPBasicAuth
import sys
import time

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

JIRA_DOMAIN = os.environ.get("JIRA_DOMAIN")
JIRA_EMAIL = os.environ.get("JIRA_EMAIL")
JIRA_TOKEN = os.environ.get("JIRA_TOKEN")
PROJECT_KEY = os.environ.get("JIRA_PROJECT_KEY")

if not all([JIRA_DOMAIN, JIRA_EMAIL, JIRA_TOKEN, PROJECT_KEY]):
    print("❌ ERRO: Faltam variáveis no .env")
    sys.exit(1)

URL_SEARCH = f"https://{JIRA_DOMAIN}/rest/api/3/search/jql"
URL_ISSUE = f"https://{JIRA_DOMAIN}/rest/api/2/issue"

AUTH = HTTPBasicAuth(JIRA_EMAIL, JIRA_TOKEN)
HEADERS = {"Accept": "application/json", "Content-Type": "application/json"}

def limpar_quadro():
    print(f"🔍 Buscando todas as tarefas no projeto {PROJECT_KEY}...")

    # Query JQL para buscar tudo que está aberto no projeto atual (via GET, pois a antiga API de json sumiu)
    qPayload = {"jql": f"project={PROJECT_KEY}", "maxResults": 100}
    response = requests.get(URL_SEARCH, params=qPayload, auth=AUTH, headers=HEADERS)

    if response.status_code != 200:
        print("❌ Erro ao buscar tarefas:", response.text)
        return

    issues = response.json().get("issues", [])
    if not issues:
        print("Mesa limpa! Nenhuma tarefa encontrada para apagar.")
        return

    print(f"🗑️ Foram encontradas {len(issues)} tarefas (incluindo tarefas antigas soltas). Iniciando deleção...")

    deletadas = 0
    for issue in issues:
        key = issue.get("id") # The new endpoint returns 'id' instead of 'key'
        del_url = f"{URL_ISSUE}/{key}"
        res = requests.delete(del_url, auth=AUTH)

        if res.status_code == 204:
            print(f"  └─ 💥 Deletada: {key}")
            deletadas += 1
        else:
            print(f"  └─ ⚠️ Erro ao deletar {key}: {res.status_code}")

        time.sleep(0.5) # Anti-bloqueio rápido

    print(f"\n✅ Concluído! {deletadas} issues apagadas do Backlog.")

if __name__ == "__main__":
    limpar_quadro()
