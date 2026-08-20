#!/usr/bin/env python3
"""
jira_project_sync.py — Sincroniza dados ricos do Jira para o projetos.yaml local.
"""

import os
import sys
import yaml
from pathlib import Path
from datetime import datetime

# Setup path for imports
root_dir = Path(__file__).resolve().parents[2]
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))

try:
    from ecosystem.jira.context_loader import JIRA_DOMAIN, JIRA_EMAIL, JIRA_TOKEN
    from ecosystem.jira.lifecycle_manager import get_issue
except ImportError as e:
    print(f"❌ ERRO: Não foi possível carregar dependências: {e}")
    sys.exit(1)

def find_projetos_yaml():
    search = Path.cwd()
    for _ in range(4):
        p = search / "projetos.yaml"
        if p.exists():
            return p
        search = search.parent
    return None

def main():
    yaml_path = find_projetos_yaml()
    if not yaml_path:
        print("❌ ERRO: projetos.yaml não encontrado na árvore de diretórios.")
        sys.exit(1)

    with open(yaml_path, "r", encoding="utf-8") as f:
        config = yaml.safe_load(f) or {}

    epic_key = config.get("jira", {}).get("epic_key")
    project_key = config.get("jira", {}).get("project_key")

    if not epic_key or not project_key:
        print("❌ ERRO: projetos.yaml não possui jira.epic_key ou jira.project_key")
        sys.exit(1)

    print(f"🔄 Sincronizando dados para o épico {epic_key} (Projeto: {project_key})...")
    
    epic = get_issue(epic_key)
    if not epic:
        print(f"❌ ERRO: Épico {epic_key} não encontrado no Jira.")
        sys.exit(1)
    epic_summary = epic["fields"]["summary"]
    
    # 2. Obter todas as issues (Tasks, Subtasks)
    # JQL: project = PROJECT_KEY AND "Epic Link" = epic_key
    # Na API v3, parent = epic_key costuma pegar as filhas diretas.
    # Vamos usar JQL para buscar tudo daquela árvore ou simplesmente project=X.
    jql = f'project = "{project_key}"'
    import requests
    from ecosystem.jira.lifecycle_manager import BASE, AUTH, HEADERS
    
    search_url = f"{BASE}/search/jql"
    issues = []
    next_token = None

    while True:
        payload = {
            "jql": jql,
            "maxResults": 100,  # real limit of /search/jql endpoint
            "fields": ["key", "summary", "status", "issuetype", "parent"]
        }
        if next_token:
            payload["nextPageToken"] = next_token

        r = requests.post(search_url, json=payload, auth=AUTH, headers=HEADERS, timeout=30)

        if r.status_code != 200:
            print(f"❌ ERRO: Falha ao buscar issues via JQL. Status: {r.status_code}")
            print(f"Response: {r.text}")
            sys.exit(1)

        data = r.json()
        page_issues = data.get("issues", [])
        issues.extend(page_issues)

        next_token = data.get("nextPageToken")
        if data.get("isLast") or not next_token:
            break

        if len(issues) > 10000:
            print("⚠️  Interrompido em 10.000 issues — verificar paginação.")
            break

    print(f"📥 {len(issues)} issues carregadas do projeto {project_key}")

    if len(issues) == 0:
        myself_url = f"{BASE}/myself"
        mr = requests.get(myself_url, auth=AUTH, headers=HEADERS, timeout=10)
        if mr.status_code != 200:
            print(f"❌ ERRO: Token provavelmente expirado ou inválido (JQL retornou 0 issues e /myself retornou status {mr.status_code}).")
            sys.exit(1)
        else:
            print(f"⚠️  Aviso: JQL retornou 0 issues, mas a autenticação com o usuário '{mr.json().get('emailAddress')}' está OK.")
    
    # Filtrar apenas as issues da árvore deste épico
    # (simplificado: pegamos todas do projeto se for um projeto de 1 épico, ou validamos pelo parent)
    
    status_count = {"Done": 0, "Backlog": 0, "In Progress": 0, "Selected for Development": 0}
    em_progresso = []
    
    for i in issues:
        status = i["fields"]["status"]["name"]
        summary = i["fields"]["summary"]
        key = i["key"]
        
        # Mapeamento simples
        if status in status_count:
            status_count[status] += 1
        elif status == "To Do":
            status_count["Backlog"] += 1
        else:
            status_count.setdefault(status, 0)
            status_count[status] += 1
            
        if status == "In Progress":
            em_progresso.append({"id": key, "summary": summary})

    # Atualizar o arquivo
    prj_id = config.get("projeto_id", "PRJ-XX")
    
    if "projetos" not in config:
        config["projetos"] = {}
        
    if prj_id not in config["projetos"]:
        config["projetos"][prj_id] = {}
        
    prj_node = config["projetos"][prj_id]
    
    prj_node["nome"] = epic_summary
    prj_node["descricao"] = "Sincronizado automaticamente via Jira API."
    
    prj_node["jira"] = {
        "site": JIRA_DOMAIN,
        "projeto_key": project_key,
        "total_issues": len(issues),
        "sincronizado_em": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    
    prj_node["resumo_status"] = {
        "done": status_count.get("Done", 0),
        "backlog": status_count.get("Backlog", 0) + status_count.get("To Do", 0),
        "em_progresso": status_count.get("In Progress", 0),
        "selecionado_para_dev": status_count.get("Selected for Development", 0)
    }
    
    prj_node["em_progresso_agora"] = em_progresso
    
    # Salvar
    with open(yaml_path, "w", encoding="utf-8") as f:
        yaml.dump(config, f, allow_unicode=True, sort_keys=False)
        
    print(f"✅ projetos.yaml atualizado com sucesso! Encontradas {len(issues)} issues.")

if __name__ == "__main__":
    main()
