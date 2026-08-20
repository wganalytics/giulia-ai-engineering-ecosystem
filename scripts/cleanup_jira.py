import os, requests
from dotenv import load_dotenv

load_dotenv("dev/<cliente>/<PRJ-XX_projeto>/.env")  # ajuste para o projeto ativo

DOMAIN = os.getenv("JIRA_DOMAIN")
EMAIL = os.getenv("JIRA_EMAIL")
TOKEN = os.getenv("JIRA_TOKEN")

AUTH = (EMAIL, TOKEN)
HEADERS = {"Accept": "application/json"}

for i in range(2, 50):
    issue_key = f"CARS-{i}"
    url = f"https://{DOMAIN}/rest/api/2/issue/{issue_key}"
    res = requests.delete(url, auth=AUTH, headers=HEADERS)
    if res.status_code == 204:
        print(f"Deletado: {issue_key}")
    elif res.status_code != 404:
        print(f"Erro em {issue_key}: {res.status_code} - {res.text}")
