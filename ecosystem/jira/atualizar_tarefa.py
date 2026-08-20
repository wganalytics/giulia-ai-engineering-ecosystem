#!/usr/bin/env python3
"""
atualizar_tarefa.py
Atualiza e gerencia o status e progresso de tarefas no Jira Cloud de forma inteligente e integrada.
"""

from __future__ import annotations

import os
import sys
import argparse
from pathlib import Path

import requests
from requests.auth import HTTPBasicAuth
from datetime import datetime
import time

# Setup paths
root_dir = Path(__file__).resolve().parents[2]
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))

# Adicionar lib ao path
lib_dir = root_dir / "shared" / "infra" / "lib"
if str(lib_dir) not in sys.path:
    sys.path.insert(0, str(lib_dir))

try:
    from ecosystem.jira.context_loader import (
        JIRA_DOMAIN,
        JIRA_EMAIL,
        JIRA_TOKEN,
        get_current_jira_project_key
    )
except ImportError as e:
    print(f"❌ Erro ao carregar ecosystem/jira/context_loader.py: {e}")
    sys.exit(1)

# Dinamicamente pega a PROJECT_KEY baseado no diretório atual
PROJECT_KEY = get_current_jira_project_key()
if not PROJECT_KEY:
    PROJECT_KEY = os.environ.get("JIRA_PROJECT_KEY", "GARE")
    print(f"⚠️ Aviso: Não foi possível detectar o projeto Jira pelo diretório. Usando padrão: {PROJECT_KEY}")

# Campos customizados (lidos do .env ou usa padrão)
START_DATE_FIELD = os.environ.get("JIRA_START_DATE_FIELD", "customfield_10015")
TIME_TRACKING_FIELD = os.environ.get("JIRA_TIME_TRACKING_FIELD", "timetracking")

# Debug mode
DEBUG = os.environ.get("JIRA_DEBUG", "false").lower() == "true"

if not all([JIRA_DOMAIN, JIRA_EMAIL, JIRA_TOKEN]):
    print("❌ ERRO: Faltam variáveis no .env global (JIRA_DOMAIN, JIRA_EMAIL, JIRA_TOKEN)")
    sys.exit(1)

URL_BASE = f"https://{JIRA_DOMAIN}/rest/api/2/issue"
AUTH = HTTPBasicAuth(JIRA_EMAIL, JIRA_TOKEN)
HEADERS = {
    "Accept": "application/json",
    "Content-Type": "application/json"
}

# Cache para transições (evita múltiplas chamadas)
_transitions_cache = {}

def log_debug(msg):
    if DEBUG:
        print(f"  🔍 DEBUG: {msg}")

def get_transitions(issue_key):
    if issue_key in _transitions_cache:
        return _transitions_cache[issue_key]

    url = f"{URL_BASE}/{issue_key}/transitions"
    trans_response = requests.get(url, auth=AUTH, headers=HEADERS)
    if trans_response.status_code != 200:
        print("❌ Erro ao buscar as transições.")
        return []

    transitions = trans_response.json().get("transitions", [])
    _transitions_cache[issue_key] = transitions
    return transitions

def get_issue_data(issue_key):
    url = f"{URL_BASE}/{issue_key}?fields=created,updated,duedate,timespent,timeoriginalestimate,status"
    response = requests.get(url, auth=AUTH, headers=HEADERS)
    if response.status_code == 200:
        return response.json()
    return None

def set_start_date(issue_key):
    url = f"{URL_BASE}/{issue_key}"
    today = datetime.now().strftime("%Y-%m-%d")
    payload = {
        "fields": {
            START_DATE_FIELD: today
        }
    }

    log_debug(f"Set Start Date payload: {payload}")

    response = requests.put(url, json=payload, auth=AUTH, headers=HEADERS)
    if response.status_code == 204:
        print(f"  📅 Start Date definida: {today}")
    else:
        log_debug(f"Response: {response.text}")
        print(f"  ⚠️ Não foi possível definir Start Date: {response.text[:100]}")

def calcular_tempo_real(issue_data):
    created_str = issue_data.get("fields", {}).get("created")
    updated_str = issue_data.get("fields", {}).get("updated")

    if not created_str or not updated_str:
        return None

    created = datetime.fromisoformat(created_str.replace("Z", "+00:00"))
    updated = datetime.fromisoformat(updated_str.replace("Z", "+00:00"))

    delta = updated - created
    horas = delta.total_seconds() / 3600
    if horas < 24:
        return f"{horas:.1f}h"
    else:
        dias = horas / 8  # Convertendo para dias úteis (8h/dia)
        return f"{dias:.1f}d"

def calcular_eficiencia(issue_data):
    fields = issue_data.get("fields", {})

    time_spent = fields.get("timeSpent")
    original_estimate = fields.get("timeOriginalEstimate")

    if not original_estimate or original_estimate == 0:
        return None

    if not time_spent:
        time_spent = 0

    estimate_horas = original_estimate / 3600
    spent_horas = time_spent / 3600

    if estimate_horas > 0:
        percentual = (spent_horas / estimate_horas) * 100
    else:
        percentual = 0

    if percentual <= 80:
        emoji = "🟢"
        status = "Antes do prazo"
    elif percentual <= 120:
        emoji = "🟡"
        status = "Dentro do prazo"
    else:
        emoji = "🔴"
        status = "Estouro de prazo"

    return {
        "estimado": f"{estimate_horas:.1f}h",
        "real": f"{spent_horas:.1f}h" if spent_horas > 0 else "N/A",
        "percentual": f"{percentual:.0f}%",
        "emoji": emoji,
        "status": status
    }

def verificar_bloqueios(issue_key):
    url = f"{URL_BASE}/{issue_key}?fields=issuelinks"
    response = requests.get(url, auth=AUTH, headers=HEADERS)

    if response.status_code != 200:
        return []

    data = response.json()
    links = data.get("fields", {}).get("issuelinks", [])

    bloqueada_por = []
    for link in links:
        if link.get("type", {}).get("inward") == "is blocked by":
            blocking_issue = link.get("inwardIssue", {})
            bloqueada_por.append({
                "key": blocking_issue.get("key"),
                "summary": blocking_issue.get("summary", "")[:50]
            })

    return bloqueada_por

def adicionar_comentario(issue_key, comentario):
    if not comentario:
        return
    url = f"{URL_BASE}/{issue_key}/comment"
    payload = {"body": comentario}
    response = requests.post(url, json=payload, auth=AUTH, headers=HEADERS)
    if response.status_code == 201:
        print(f"✅ Comentário anexado com sucesso na {issue_key}.")
    else:
        print(f"❌ Erro ao adicionar comentário na {issue_key}: {response.text}")

def mover_para_status(issue_key, status_alvo):
    transitions = get_transitions(issue_key)
    if not transitions:
        return False

    target_id = None

    mapa_palavras = {
        "selected": ["selected", "selecionado", "to do", "a fazer", "selecionar"],
        "in_progress": ["in progress", "andamento", "em andamento", "doing", "desenvolvimento"],
        "done": ["done", "concluído", "concluido", "fechar", "resolver", "resolve", "encerrar", "pronto"]
    }

    palavras_chave = mapa_palavras.get(status_alvo.lower(), [status_alvo.lower()])

    for t in transitions:
        nome_transicao = t.get("name", "").lower()
        if any(palavra in nome_transicao for palavra in palavras_chave):
            target_id = t["id"]
            break

    if target_id:
        payload = {"transition": {"id": target_id}}
        r = requests.post(f"{URL_BASE}/{issue_key}/transitions", json=payload, auth=AUTH, headers=HEADERS)
        if r.status_code == 204:
            print(f"✅ Task {issue_key} movida para {status_alvo.upper()} com sucesso!")
            return True
        else:
            print(f"❌ Erro ao modificar a coluna da {issue_key}: {r.text}")
            return False
    else:
        print(f"⚠️ Rota de status não encontrada para '{status_alvo}'.")
        print("   Transições disponíveis:", [x['name'] for x in transitions])
        return False

def get_subtasks_of_issue(issue_key):
    url = f"{URL_BASE}/{issue_key}?fields=subtasks"
    r = requests.get(url, auth=AUTH, headers=HEADERS)
    if r.status_code == 200:
        return r.json().get("fields", {}).get("subtasks", [])
    return []


def get_parent_key(issue_key):
    url = f"{URL_BASE}/{issue_key}?fields=parent"
    r = requests.get(url, auth=AUTH, headers=HEADERS)
    if r.status_code == 200:
        parent = r.json().get("fields", {}).get("parent")
        return parent.get("key") if parent else None
    return None


def get_siblings_status(parent_key):
    jql = f'project = "{PROJECT_KEY}" AND parent = {parent_key}'
    url = f"https://{JIRA_DOMAIN}/rest/api/3/search/jql"
    r = requests.get(url, params={"jql": jql, "maxResults": 100, "fields": "status"},
                     auth=AUTH, headers=HEADERS)
    if r.status_code == 200:
        issues = r.json().get("issues", [])
        return [i["fields"]["status"]["name"] for i in issues]
    return []


def cascade_subtasks_to_selected(issue_key):
    subtasks = get_subtasks_of_issue(issue_key)
    if not subtasks:
        return

    moved = 0
    for st in subtasks:
        st_key = st["key"]
        url = f"{URL_BASE}/{st_key}?fields=status"
        r = requests.get(url, auth=AUTH, headers=HEADERS)
        if r.status_code == 200:
            st_status = r.json()["fields"]["status"]["name"]
            if st_status == "Backlog":
                if mover_para_status(st_key, "selected"):
                    moved += 1
                    time.sleep(0.2)

    if moved > 0:
        print(f"  📋 {moved} subtask(s) movida(s) para 'Selected for Development'")


def check_auto_promote_parent(issue_key):
    parent_key = get_parent_key(issue_key)
    if not parent_key:
        return

    siblings_statuses = get_siblings_status(parent_key)
    if not siblings_statuses:
        return

    all_done = all(s == "Done" for s in siblings_statuses)
    done_count = sum(1 for s in siblings_statuses if s == "Done")
    total = len(siblings_statuses)

    print(f"\n  🔍 Verificando auto-promoção de {parent_key}: {done_count}/{total} filhos concluídos")

    if all_done:
        print(f"  🎉 Todos filhos concluídos! Promovendo {parent_key} para Done...")
        if mover_para_status(parent_key, "done"):
            comentario = (
                f"🎉 Auto-promovido para Done\n"
                f"Todos {total} filhos foram concluídos.\n"
                f"Data: {datetime.now().strftime('%Y-%m-%d %H:%M')}"
            )
            adicionar_comentario(parent_key, comentario)
            check_auto_promote_parent(parent_key)
    else:
        pending = total - done_count
        print(f"  ℹ️  Ainda faltam {pending} filhos — {parent_key} permanece no status atual")


def processar_inicio(issue_key):
    print(f"\n📋 PROCESSANDO: {issue_key} → IN PROGRESS")
    set_start_date(issue_key)
    cascade_subtasks_to_selected(issue_key)

    bloqueios = verificar_bloqueios(issue_key)
    if bloqueios:
        print("  ⚠️ ATENÇÃO: Issue está bloqueada por:")
        for b in bloqueios:
            print(f"     • {b['key']}: {b['summary']}...")
        print(f"  💡 Recomendação: Resolver {bloqueios[0]['key']} primeiro!")

def processar_conclusao(issue_key, nota_tecnica):
    print(f"\n📋 PROCESSANDO: {issue_key} → DONE")
    
    if not nota_tecnica or len(nota_tecnica.strip()) < 50:
        print("❌ ERRO: A nota técnica fornecida é muito curta ou inexistente.")
        print("   Como Analista/Engenheiro Sênior, você DEVE fornecer um check-in detalhado (mínimo 50 caracteres)")
        print("   explicando CLARAMENTE QUAIS ARQUIVOS foram alterados e QUAIS TÉCNICAS foram implementadas.")
        sys.exit(1)

    issue_data = get_issue_data(issue_key)
    if not issue_data:
        print("  ⚠️ Não foi possível buscar dados da issue.")
        return

    tempo_real = calcular_tempo_real(issue_data)
    eficiencia = calcular_eficiencia(issue_data)

    relatorio = "h3. 📊 Relatório de Conclusão\n\n"
    relatorio += "{{panel}}\n"
    relatorio += "|| Campo || Valor ||\n"

    if tempo_real:
        relatorio += f"| Tempo Real | {tempo_real} |\n"

    if eficiencia:
        relatorio += f"| Tempo Estimado | {eficiencia['estimado']} |\n"
        relatorio += f"| Tempo Gasto | {eficiencia['real']} |\n"
        relatorio += f"| Eficiência | {eficiencia['emoji']} {eficiencia['percentual']} ({eficiencia['status']}) |\n"

    current_status = issue_data.get("fields", {}).get("status", {}).get("name", "Desconhecido")
    relatorio += f"| Status Final | ✅ {current_status} |\n"
    relatorio += "{{panel}}\n"

    if nota_tecnica:
        relatorio += f"\nh3. 📝 Resumo Técnico\n\n{{quote}}\n{nota_tecnica}\n{{quote}}"

    adicionar_comentario(issue_key, relatorio)
    check_auto_promote_parent(issue_key)

def main():
    parser = argparse.ArgumentParser(description="JIRA Pipeline Executor Automático")
    parser.add_argument("issue_key", type=str, help="Chave da issue (ex: RAG-12)")
    parser.add_argument("status", type=str, choices=["selected", "in_progress", "done"], help="Status alvo")
    parser.add_argument("--nota", type=str, help="Notas técnicas para anexar ao card")

    args = parser.parse_args()
    issue_key = args.issue_key.upper()
    status_alvo = args.status

    print(f"\n{'='*50}")
    print(f"🎯 JIRA AUTOMATION - {issue_key}")
    print(f"{'='*50}")

    sucesso = mover_para_status(issue_key, status_alvo)

    if not sucesso:
        sys.exit(1)

    time.sleep(1)

    if status_alvo == "in_progress":
        processar_inicio(issue_key)
    elif status_alvo == "done":
        processar_conclusao(issue_key, args.nota)

if __name__ == "__main__":
    main()
