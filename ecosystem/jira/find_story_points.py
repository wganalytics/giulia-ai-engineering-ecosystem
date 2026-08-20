import os, requests
from dotenv import load_dotenv

load_dotenv("dev/<cliente>/<PRJ-XX_projeto>/.env")  # ajuste para o projeto ativo

DOMAIN = os.getenv("JIRA_DOMAIN")
AUTH = (os.getenv("JIRA_EMAIL"), os.getenv("JIRA_TOKEN"))
HEADERS = {"Accept": "application/json"}

print("Buscando campos do Jira para achar Story Points...")
url = f"https://{DOMAIN}/rest/api/3/field"
res = requests.get(url, auth=AUTH, headers=HEADERS)
if res.ok:
    fields = res.json()
    for f in fields:
        name = f.get("name", "").lower()
        if "story point" in name or "point" in name:
            print(f"Encontrado: {f.get('id')} -> {f.get('name')}")
else:
    print("Erro Fields:", res.text)
