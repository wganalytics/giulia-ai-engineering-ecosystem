import os
import requests
from dotenv import load_dotenv

load_dotenv("dev/mcp/.env")

domain = os.environ.get("JIRA_DOMAIN")
email = os.environ.get("JIRA_EMAIL")
token = os.environ.get("JIRA_TOKEN")

auth = (email, token)
headers = {"Accept": "application/json"}
url = f"https://{domain}/rest/api/3/search?jql=project=MCP&maxResults=100&fields=summary,issuetype,status,parent"

response = requests.get(url, auth=auth, headers=headers)
data = response.json()

for issue in data.get('issues', []):
    key = issue['key']
    summary = issue['fields']['summary']
    issuetype = issue['fields']['issuetype']['name']
    status = issue['fields']['status']['name']
    print(f"{key} [{issuetype}] - {status}: {summary}")

