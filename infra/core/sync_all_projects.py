#!/usr/bin/env python3
"""
Jira Project Sync - Sincroniza todos os projetos cadastrados em projetos.yaml para o Jira
用法: python sync_all_projects.py [--dry-run] [--force]
"""

import os
import re
import sys
import yaml
import requests
from datetime import datetime, timedelta
from pathlib import Path
from requests.auth import HTTPBasicAuth
from dotenv import load_dotenv

# Carregar config
config_dir = Path(__file__).parent.parent / "config"
env_path = config_dir / ".env"
if env_path.exists():
    load_dotenv(env_path)

JIRA_DOMAIN = os.environ.get("JIRA_DOMAIN")
JIRA_EMAIL = os.environ.get("JIRA_EMAIL")
JIRA_TOKEN = os.environ.get("JIRA_TOKEN")
PROJECT_KEY = os.environ.get("JIRA_PROJECT_KEY", "RAG")

if not all([JIRA_DOMAIN, JIRA_EMAIL, JIRA_TOKEN]):
    print("❌ ERRO: Variáveis de ambiente faltando")
    sys.exit(1)

AUTH = HTTPBasicAuth(JIRA_EMAIL, JIRA_TOKEN)
HEADERS = {"Accept": "application/json", "Content-Type": "application/json"}

URL_BASE = f"https://{JIRA_DOMAIN}/rest/api/3"


def make_request(method, endpoint, **kwargs):
    url = f"{URL_BASE}{endpoint}"
    response = requests.request(method, url, auth=AUTH, headers=HEADERS, **kwargs)
    if response.status_code in [200, 201, 204]:
        if response.status_code == 204:
            return {"success": True}
        return response.json()
    else:
        print(f"❌ Erro {response.status_code}: {response.text[:200] if response.text else ''}")
        return None


def get_existing_issues():
    """Busca todos os épicos e tasks existentes"""
    jql = f"project={PROJECT_KEY}"
    result = make_request("POST", "/search/jql", json={"jql": jql, "maxResults": 200, "fields": ["summary", "issuetype", "parent"]})
    if result:
        issues = result.get("issues", [])
        # Buscar por ID do projeto (ex: PRJ-XX, PRJ-YY, ...) no summary
        epics = {}
        tasks = {}
        prj_id_pattern = re.compile(r"PRJ-\d+")
        for i in issues:
            summary = i["fields"]["summary"]
            issue_type = i["fields"]["issuetype"]["name"]
            key = i["key"]

            if issue_type == "Epic":
                # Extrai PRJ-XX do summary
                match = prj_id_pattern.search(summary)
                prj_id = match.group(0) if match else None

                if prj_id:
                    epics[prj_id] = key
                else:
                    epics[summary] = key
            elif issue_type in ["Task", "Sub-task"]:
                tasks[summary] = key
        
        return epics, tasks
    return {}, {}


def criar_epico(summary, description, start_date, story_points):
    """Cria um épico no Jira"""
    payload = {
        "fields": {
            "project": {"key": PROJECT_KEY},
            "summary": summary,
            "description": {
                "type": "doc",
                "version": 1,
                "content": [{"type": "paragraph", "content": [{"type": "text", "text": description}]}]
            },
            "issuetype": {"name": "Epic"},
            "customfield_10015": start_date,
            "customfield_10016": story_points,
            "customfield_10033": story_points
        }
    }
    result = make_request("POST", "/issue", json=payload)
    if result:
        print(f"  ✅ Épico criado: {result.get('key')}")
        return result.get("key")
    return None


def criar_task(summary, description, parent_key, priority, estimate_hours, story_points, due_date, start_date, labels):
    """Cria uma task no Jira"""
    labels_list = labels if labels else []
    
    payload = {
        "fields": {
            "project": {"key": PROJECT_KEY},
            "summary": summary,
            "description": {
                "type": "doc",
                "version": 1,
                "content": [{"type": "paragraph", "content": [{"type": "text", "text": description}]}]
            },
            "issuetype": {"name": "Task"},
            "priority": {"name": priority},
            "labels": labels_list,
            "customfield_10015": start_date,
            "customfield_10016": story_points,
            "duedate": due_date,
            "timetracking": {"originalEstimateSeconds": int(estimate_hours * 3600)}
        }
    }
    
    if parent_key:
        payload["fields"]["parent"] = {"key": parent_key}
    
    result = make_request("POST", "/issue", json=payload)
    if result:
        key = result.get("key")
        print(f"    ✅ Task: {key}")
        return key
    return None


def sincronizar_projetos(dry_run=False):
    """Sincroniza todos os projetos do YAML para o Jira"""
    
    # Carregar projetos
    yaml_path = Path(__file__).parent.parent / "config" / "projetos.yaml"
    if not yaml_path.exists():
        print(f"❌ ERRO: {yaml_path} não encontrado.")
        print("   Este arquivo não é distribuído com o framework — crie-o para catalogar")
        print("   as tasks Jira do seu próprio projeto antes de rodar este script.")
        sys.exit(1)
    with open(yaml_path, 'r') as f:
        data = yaml.safe_load(f)
    
    projetos = data.get("projetos", {})
    config = data.get("config", {})
    
    print(f"\n🔄 Sincronizando {len(projetos)} projetos para o Jira...\n")
    
    # Buscar issues existentes
    existing_epics, existing_tasks = get_existing_issues()
    print(f"📊 Encontrados {len(existing_epics)} épicos e {len(existing_tasks)} tasks existentes\n")
    print(f"   Épicos: {existing_epics}")
    
    start_date = datetime.now().strftime("%Y-%m-%d")
    created_count = 0
    
    for prj_id, prj_data in projetos.items():
        print(f"\n{'='*60}")
        print(f"📦 {prj_id}: {prj_data.get('nome', 'Sem nome')}")
        print(f"{'='*60}")
        
        nome = prj_data.get("nome", "")
        desc = prj_data.get("descricao", "")
        
        # Calcular story points total
        total_sp = sum(t.get("storypoints", 0) for t in prj_data.get("tasks", []))
        
        # Verificar se épico já existe (pela key PRJ-XX)
        epic_key = existing_epics.get(prj_id)
        
        if epic_key:
            print(f"  ⚠️  Épico já existe: {epic_key}")
        else:
            if dry_run:
                print(f"  🔍 [DRY-RUN] Criaria épico: {prj_id} - {nome}")
            else:
                # Criar summary com PRJ-XX
                summary = f"{prj_id} - {nome}"
                epic_key = criar_epico(summary, desc, start_date, total_sp)
                if epic_key:
                    existing_epics[prj_id] = epic_key
                    created_count += 1
        
        if not epic_key:
            print(f"  ❌ Pulando tasks - épico não pôde ser criado")
            continue
        
        # Criar tasks
        tasks = prj_data.get("tasks", [])
        for task_data in tasks:
            summary = task_data.get("summary", "")
            task_key = existing_tasks.get(summary)
            
            if task_key:
                print(f"    ⚠️  Task já existe: {task_key}")
                continue
            
            if dry_run:
                print(f"    🔍 [DRY-RUN] Criaria task: {summary}")
                continue
            
            description = task_data.get("description", "")
            priority = task_data.get("priority", "Medium")
            estimate = task_data.get("estimate", 0)
            sp = task_data.get("storypoints", 0)
            due_days = task_data.get("due_days", 0)
            labels = task_data.get("labels", [])
            
            # Calcular due date
            due_date = (datetime.now() + timedelta(days=due_days)).strftime("%Y-%m-%d")
            
            task_key = criar_task(
                summary=summary,
                description=description,
                parent_key=epic_key,
                priority=priority,
                estimate_hours=estimate,
                story_points=sp,
                due_date=due_date,
                start_date=start_date,
                labels=labels
            )
            
            if task_key:
                existing_tasks[summary] = task_key
                created_count += 1
    
    print(f"\n{'='*60}")
    print(f"✅ Sincronização concluída!")
    print(f"   Total de items criados: {created_count}")
    print(f"{'='*60}\n")


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Sincroniza projetos do YAML para o Jira")
    parser.add_argument("--dry-run", action="store_true", help="Simula sem criar")
    parser.add_argument("--force", action="store_true", help="Força recriação")
    args = parser.parse_args()
    
    sincronizar_projetos(dry_run=args.dry_run)