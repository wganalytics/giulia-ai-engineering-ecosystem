import os, requests
from dotenv import load_dotenv

load_dotenv("dev/<cliente>/<PRJ-XX_projeto>/.env")  # ajuste para o projeto ativo

DOMAIN = os.getenv("JIRA_DOMAIN")
EMAIL = os.getenv("JIRA_EMAIL")
TOKEN = os.getenv("JIRA_TOKEN")

AUTH = (EMAIL, TOKEN)

print("Buscando usuários no Jira...")
url = f"https://{DOMAIN}/rest/api/3/user/search?query=giulia"
res = requests.get(url, auth=AUTH)
if res.ok:
    print("Busca por Giulia:", res.json())
else:
    print("Erro Giulia:", res.text)

url2 = f"https://{DOMAIN}/rest/api/3/user/search?query=agent"
res2 = requests.get(url2, auth=AUTH)
if res2.ok:
    print("Busca por agent:", res2.json())
else:
    print("Erro Agent:", res2.text)
