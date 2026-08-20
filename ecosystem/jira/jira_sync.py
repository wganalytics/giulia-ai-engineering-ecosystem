#!/usr/bin/env python3
"""
Jira Sync - Sincronizador de Projetos com Jira Cloud

Uso:
    python ecosystem/jira/jira_sync.py              # Modo normal (idempotente)
    python ecosystem/jira/jira_sync.py --force      # Força recriação
    python ecosystem/jira/jira_sync.py --dry-run    # Simula sem criar
    python ecosystem/jira/jira_sync.py --debug      # Mostra detalhes da API
"""

from __future__ import annotations

import re
import os
import sys
import argparse
from dataclasses import dataclass
from datetime import datetime, timedelta
from pathlib import Path

# Setup paths
root_dir = Path(__file__).resolve().parents[2]
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))

# Adicionar lib ao path
lib_dir = root_dir / "shared" / "infra" / "lib"
if str(lib_dir) not in sys.path:
    sys.path.insert(0, str(lib_dir))

import requests
import yaml
from requests.auth import HTTPBasicAuth
from dotenv import load_dotenv

try:
    from sync_state import SyncState, criar_state_manager
except ImportError as e:
    print(f"❌ Erro ao importar sync_state de shared/infra/lib: {e}")
    sys.exit(1)

# Variáveis globais para serem injetadas pelo setup_env
JIRA_DOMAIN = ""
JIRA_EMAIL = ""
JIRA_TOKEN = ""
PROJECT_KEY = ""
URL_BASE = ""
AUTH = None
DEFAULT_ASSIGNEE_ID = None
AGENT_ASSIGNEE_ID = "712020:41e738ba-80ad-42d6-b451-d74c0694758b"
STORY_POINTS_FIELD = "customfield_10016"
HEADERS = {"Accept": "application/json", "Content-Type": "application/json"}

def find_client_env(start_dir: Path) -> Path | None:
    current_dir = start_dir.resolve()
    while True:
        env_path = current_dir / ".env"
        if env_path.exists():
            if (current_dir / "ecosystem").exists() and (current_dir / "dev").exists():
                return None
            return env_path
        if current_dir.parent == current_dir:
            break
        current_dir = current_dir.parent
        if current_dir.name == "dev":
            break
    return None

def setup_env(project_dir: Path) -> bool:
    global JIRA_DOMAIN, JIRA_EMAIL, JIRA_TOKEN, PROJECT_KEY, URL_BASE, AUTH, DEFAULT_ASSIGNEE_ID
    
    env_path = find_client_env(project_dir)
    if env_path:
        load_dotenv(dotenv_path=env_path, override=True)
    else:
        print(f"❌ ERRO CRÍTICO (ISOLAMENTO): Nenhum arquivo .env encontrado para o cliente de {project_dir}")
        print("❌ O fallback para o .env global foi bloqueado por questões de segurança de dados.")
        return False
        
    JIRA_DOMAIN = os.environ.get("JIRA_DOMAIN", "")
    JIRA_EMAIL = os.environ.get("JIRA_EMAIL", "")
    JIRA_TOKEN = os.environ.get("JIRA_TOKEN", "")
    PROJECT_KEY = os.environ.get("JIRA_PROJECT_KEY", "")
    
    if not all([JIRA_DOMAIN, JIRA_EMAIL, JIRA_TOKEN, PROJECT_KEY]):
        return False
        
    URL_BASE = f"https://{JIRA_DOMAIN}/rest/api/2/issue"
    AUTH = HTTPBasicAuth(JIRA_EMAIL, JIRA_TOKEN)
    
    # Busca o Account ID do usuário autenticado para definir como Assignee padrão
    try:
        res = requests.get(f"https://{JIRA_DOMAIN}/rest/api/3/myself", auth=AUTH, headers=HEADERS)
        if res.status_code == 200:
            DEFAULT_ASSIGNEE_ID = res.json().get("accountId")
    except Exception:
        pass
        
    if not DEFAULT_ASSIGNEE_ID:
        DEFAULT_ASSIGNEE_ID = "712020:3dea43eb-976e-443d-a97c-751a5d89cfb1"
        
    return True

@dataclass
class Args:
    """Argumentos da linha de comando."""
    force: bool
    dry_run: bool
    debug: bool
    clear: bool
    criar_subtasks: bool
    criar_links: bool


# Cache de transições para evitar múltiplas chamadas
_TRANSITIONS_CACHE: dict[str, list[dict]] = {}

type TaskDict = dict[str, str | int | list[str] | None]
type ProjectDict = dict[str, str | list[TaskDict]]
type ProjectsDict = dict[str, ProjectDict]
type ConfigDict = dict[str, str | int | bool]


def log_debug(msg: str, debug: bool = False) -> None:
    if debug:
        print(f"  🔍 DEBUG: {msg}")


def log_info(msg: str) -> None:
    print(f"  ℹ️ {msg}")


def log_success(msg: str) -> None:
    print(f"  ✅ {msg}")


def log_warning(msg: str) -> None:
    print(f"  ⚠️ {msg}")


def log_error(msg: str) -> None:
    print(f"  ❌ {msg}")


def buscar_issue_por_resumo(summary: str, issue_type: str = "Task") -> str | None:
    """Busca se já existe uma issue com o mesmo resumo no projeto."""
    summary_escaped = summary.replace('"', '\\"')
    jql = f'project = "{PROJECT_KEY}" AND summary ~ "{summary_escaped}" AND issuetype = "{issue_type}"'
    
    url = f"https://{JIRA_DOMAIN}/rest/api/3/search/jql"
    payload = {"jql": jql, "maxResults": 5, "fields": ["key", "summary"]}
    
    try:
        response = requests.post(url, json=payload, auth=AUTH, headers=HEADERS)
        if response.status_code == 200:
            issues = response.json().get("issues", [])
            for issue in issues:
                if issue["fields"]["summary"].strip() == summary.strip():
                    return issue["key"]
    except Exception as e:
        log_error(f"Erro ao buscar duplicata: {e}")
        
    return None


def criar_issue(
    summary: str,
    issue_type: str = "Task",
    description: str = "",
    parent_epic_key: str | None = None,
    labels: list[str] | None = None,
    priority: str | None = None,
    due_date: str | None = None,
    original_estimate: int | None = None,
    story_points: float | None = None,
    start_date_field: str = "customfield_10015"
) -> str | None:
    """Cria uma issue no Jira com campos opcionais."""
    payload: dict = {
        "fields": {
            "project": {"key": PROJECT_KEY},
            "summary": summary,
            "description": description,
            "issuetype": {"name": issue_type}
        }
    }

    if labels:
        payload["fields"]["labels"] = labels
        
    if "[AGENT-AI]" in summary.upper() and AGENT_ASSIGNEE_ID:
        payload["fields"]["assignee"] = {"id": AGENT_ASSIGNEE_ID}
    elif DEFAULT_ASSIGNEE_ID:
        payload["fields"]["assignee"] = {"id": DEFAULT_ASSIGNEE_ID}

    if parent_epic_key and issue_type != "Epic":
        payload["fields"]["parent"] = {"key": parent_epic_key}

    if priority:
        payload["fields"]["priority"] = {"name": priority}

    if due_date:
        payload["fields"]["duedate"] = due_date

    if start_date_field:
        payload["fields"][start_date_field] = datetime.now().strftime("%Y-%m-%d")


    if original_estimate:
        hours = int(original_estimate / 3600)
        payload["fields"]["timetracking"] = {
            "originalEstimate": f"{hours}h",
            "remainingEstimate": f"{hours}h"
        }
        
    if story_points is not None:
        payload["fields"][STORY_POINTS_FIELD] = story_points
        if issue_type == "Epic":
            payload["fields"]["customfield_10033"] = story_points


    response = requests.post(URL_BASE, json=payload, auth=AUTH, headers=HEADERS)

    if response.status_code == 201:
        key = response.json().get("key")
        return key

    log_error(f"Falha ao criar '{summary}': {response.text[:200]}")
    return None


def criar_subtask(summary: str, parent_key: str, original_estimate: int | None = None) -> str | None:
    """Cria uma subtask vinculada à task pai, com verificação remota anti-duplicata e estimativa."""
    if subtask_exists_remotely(parent_key, summary):
        log_info(f"Subtask já existe em {parent_key}: '{summary[:40]}...'")
        return None
    
    payload = {
        "fields": {
            "project": {"key": PROJECT_KEY},
            "summary": summary,
            "issuetype": {"name": "Sub-task"},
            "parent": {"key": parent_key}
        }
    }

    if "[AGENT-AI]" in summary.upper() and AGENT_ASSIGNEE_ID:
        payload["fields"]["assignee"] = {"id": AGENT_ASSIGNEE_ID}
    elif DEFAULT_ASSIGNEE_ID:
        payload["fields"]["assignee"] = {"id": DEFAULT_ASSIGNEE_ID}


    if original_estimate:
        hours = int(original_estimate / 3600)
        payload["fields"]["timetracking"] = {
            "originalEstimate": f"{hours}h",
            "remainingEstimate": f"{hours}h"
        }


    response = requests.post(URL_BASE, json=payload, auth=AUTH, headers=HEADERS)

    if response.status_code == 201:
        return response.json().get("key")

    log_warning(f"Subtask não criada: {response.text[:100]}")
    return None


def subtask_exists_remotely(parent_key: str, summary: str) -> bool:
    """Verifica via JQL se subtask com mesmo summary já existe no parent."""
    summary_escaped = summary[:50].replace('"', '\\"')
    jql = f'project = "{PROJECT_KEY}" AND parent = {parent_key} AND summary ~ "{summary_escaped}"'
    url = f"https://{JIRA_DOMAIN}/rest/api/3/search/jql"
    
    try:
        r = requests.get(
            url,
            params={"jql": jql, "maxResults": 1, "fields": "key,summary"},
            auth=AUTH,
            headers=HEADERS
        )
        if r.status_code == 200:
            issues = r.json().get("issues", [])
            for issue in issues:
                if issue["fields"]["summary"].strip() == summary.strip():
                    return True
    except Exception as e:
        log_warning(f"Falha na verificação remota: {e}")
    
    return False


def criar_link(inward_key: str, outward_key: str, link_type: str = "Blocks") -> bool:
    """Cria um link entre duas issues."""
    url = f"https://{JIRA_DOMAIN}/rest/api/2/issueLink"
    payload = {
        "type": {"name": link_type},
        "inwardIssue": {"key": inward_key},
        "outwardIssue": {"key": outward_key}
    }

    response = requests.post(url, json=payload, auth=AUTH, headers=HEADERS)

    if response.status_code == 201:
        return True

    log_warning(f"Link falhou: {response.text[:100]}")
    return False


def calcular_due_date_respeitando_dependencias(
    task: TaskDict,
    todas_tasks: list[TaskDict],
    tarefas_criadas: dict[str, str],
    buffer_dias: int = 2
) -> str:
    """Calcula o Due Date respeitando a cadeia de dependências."""
    blocked_by = task.get("blocked_by")

    if not blocked_by:
        base_date = datetime.now()
        days = task.get("due_days", 3)
        return (base_date + timedelta(days=days)).strftime("%Y-%m-%d")

    jira_key_blocked = tarefas_criadas.get(blocked_by)

    if jira_key_blocked:
        url = f"{URL_BASE}/{jira_key_blocked}?fields=duedate"
        response = requests.get(url, auth=AUTH, headers=HEADERS)

        if response.status_code == 200:
            due_date_str = response.json().get("fields", {}).get("duedate")
            if due_date_str:
                blocked_due = datetime.strptime(due_date_str, "%Y-%m-%d")
                calculated_due = blocked_due + timedelta(days=buffer_dias)
                return calculated_due.strftime("%Y-%m-%d")

    base_date = datetime.now()
    days = task.get("due_days", 3)
    return (base_date + timedelta(days=days)).strftime("%Y-%m-%d")


def parse_estimate(estimate_str: str | int | None) -> int | None:
    """Converte string ou int de estimativa para segundos."""
    if not estimate_str:
        return None

    if isinstance(estimate_str, int):
        return estimate_str * 3600

    estimate_str = str(estimate_str).lower().strip()

    try:
        if estimate_str.endswith('h'):
            hours = int(estimate_str[:-1])
            return hours * 3600
        elif estimate_str.endswith('d'):
            days = int(estimate_str[:-1])
            return days * 8 * 3600
        elif estimate_str.endswith('m'):
            minutes = int(estimate_str[:-1])
            return minutes * 60
        elif estimate_str.isdigit():
            return int(estimate_str) * 3600
    except ValueError:
        pass

    return None


def determinar_labels(task_labels: list[str] | None) -> list[str]:
    return task_labels if task_labels else ["AGENT-AI"]


def sincronizar_projeto(
    projeto_id: str,
    projeto_config: ProjectDict,
    state: SyncState,
    args: Args
) -> str | None:
    """Sincroniza um único projeto."""
    nome_projeto = projeto_config.get("nome", projeto_id)
    tasks = projeto_config.get("tasks", [])

    print(f"\n📁 PROJETO: {nome_projeto} ({projeto_id})")

    # Calculate totals
    epic_total_estimate = 0
    epic_total_sp = 0
    
    # First pass: parse subtasks strings
    for task in tasks:
        task_total_estimate = 0
        parsed_subtasks = []
        for st in task.get("subtasks", []):
            st_str = st if isinstance(st, str) else st.get("summary", "")
            # Look for (Estimativa: Xh)
            match = re.search(r'\(Estimativa:\s*([^)]+)\)', st_str, re.IGNORECASE)
            st_estimate = None
            if match:
                st_estimate = parse_estimate(match.group(1))
                st_str = re.sub(r'\s*\(Estimativa:\s*[^)]+\)', '', st_str).strip()
            elif isinstance(st, dict) and st.get("estimate"):
                st_estimate = parse_estimate(st.get("estimate"))
                
            if st_estimate:
                task_total_estimate += st_estimate
            
            parsed_subtasks.append({"summary": st_str, "estimate": st_estimate})
            
        task["parsed_subtasks"] = parsed_subtasks
        task["total_estimate"] = task_total_estimate
        epic_total_estimate += task_total_estimate
        
    epic_total_sp = round(epic_total_estimate / 3600.0, 1)

    # 1. TENTAR RECUPERAR ÉPICO (STATE OU BUSCA JIRA)
    epico_key = state.get_epico_key(projeto_id)
    
    if not epico_key:
        epico_key = buscar_issue_por_resumo(f"Ecosistema: {nome_projeto}", "Epic")
        if epico_key:
            log_info(f"Épico recuperado via busca no Jira: {epico_key}")
            state.register_epico(projeto_id, epico_key)

    # 2. CRIAR ÉPICO SE NÃO EXISTIR
    if not epico_key and not args.force:
        epico_key = criar_issue(
            summary=f"Ecosistema: {nome_projeto}",
            issue_type="Epic",
            description=projeto_config.get("descricao", "Projeto do Portfólio RAG"),
            labels=["HUMAN", "AGENT-AI"],
            original_estimate=epic_total_estimate,
            story_points=epic_total_sp
        )

        if epico_key:
            state.register_epico(projeto_id, epico_key)
            log_success(f"Épico criado: {epico_key}")

    if not epico_key:
        log_error("Falha ao criar/localizar épico")
        return None
    else:
        log_info(f"Usando épico: {epico_key}")


    tarefas_criadas: dict[str, str] = {}

    for task in tasks:
        task_id = task.get("id", "")
        task_key = state.get_task_jira_key(task_id, PROJECT_KEY)

        # 3. TENTAR RECUPERAR TASK (STATE OU BUSCA JIRA)
        if not task_key:
            task_key = buscar_issue_por_resumo(str(task.get("summary")), "Task")
            if task_key:
                log_info(f"Task recuperada via busca no Jira: {task_key} ({task_id})")
                state.register_task(task_id, PROJECT_KEY, task_key, "", "")

        # 4. CRIAR TASK SE NÃO EXISTIR
        if not task_key:
            due_date = calcular_due_date_respeitando_dependencias(
                task, tasks, tarefas_criadas, buffer_dias=2
            )
            estimate_seconds = parse_estimate(task.get("estimate"))
            labels = determinar_labels(task.get("labels"))

            task_key = criar_issue(
                summary=str(task.get("summary")),
                issue_type="Task",
                description=str(task.get("description", "")),
                parent_epic_key=epico_key,
                labels=labels,
                priority=str(task.get("priority", "")),
                due_date=due_date,
                original_estimate=task.get("total_estimate") or estimate_seconds,
                story_points=round((task.get("total_estimate") or estimate_seconds or 0) / 3600.0, 1)
            )

            if task_key:
                state.register_task(
                    task_id,
                    PROJECT_KEY,
                    task_key,
                    due_date,
                    str(task.get("estimate", ""))
                )
        
        # 5. PROCESSAR SUBTASKS E LINKS
        if task_key:
            tarefas_criadas[task_id] = task_key
            
            labels = determinar_labels(task.get("labels"))
            print(f"  └─ {task_key} [{','.join(labels)}] {str(task.get('summary'))[:50]}...")

            if task.get("parsed_subtasks") and args.criar_subtasks:
                for st in task.get("parsed_subtasks"):
                    st_summary = st["summary"]
                    st_estimate = st["estimate"]
                        
                    st_key = criar_subtask(st_summary, task_key, original_estimate=st_estimate)
                    if st_key:
                        state.register_subtask(task_key, st_summary, st_key)
                        print(f"      └─ 📋 {st_key}: {st_summary[:50]}... (Estimativa: {st.get('estimate', 'N/A') if isinstance(st, dict) else 'N/A'})")

            blocked_by = task.get("blocked_by")
            if blocked_by and args.criar_links:
                blocking_jira_key = tarefas_criadas.get(str(blocked_by))
                if blocking_jira_key:
                    if not state.is_link_exists(task_key, blocking_jira_key, "Blocks"):
                        if criar_link(task_key, blocking_jira_key, "Blocks"):
                            state.register_link(task_key, blocking_jira_key, "Blocks")
                            print(f"      🔗 {task_key} is blocked by {blocking_jira_key}")

            import time
            time.sleep(0.5)
        else:
            log_error(f"Falha ao criar task: {str(task.get('summary'))[:50]}")

    return epico_key


def carregar_projetos(project_dir: Path) -> tuple[ProjectsDict, ConfigDict]:
    """Carrega projetos do arquivo YAML do diretório do projeto."""
    yaml_path = project_dir / "projeto.yaml"

    if not yaml_path.exists():
        log_error(f"Arquivo {yaml_path} não encontrado!")
        sys.exit(1)

    with open(yaml_path, 'r', encoding='utf-8') as f:
        data = yaml.safe_load(f)

    return data.get("projetos", {}), data.get("config", {})


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Sincronizador de Projetos com Jira Cloud"
    )

    parser.add_argument("--force", action="store_true", help="Força recriação de todas as issues")
    parser.add_argument("--dry-run", action="store_true", help="Simula execução sem criar issues no Jira")
    parser.add_argument("--debug", action="store_true", help="Mostra mensagens de debug")
    parser.add_argument("--clear", action="store_true", help="Limpa estado anterior antes de sincronizar")
    parser.add_argument("--no-subtasks", dest="criar_subtasks", action="store_false", help="Não criar subtasks")
    parser.add_argument("--no-links", dest="criar_links", action="store_false", help="Não criar links")
    parser.add_argument("--project-dir", default=os.getcwd(), help="Diretório raiz do projeto")

    parser.set_defaults(criar_subtasks=True, criar_links=True)

    parsed = parser.parse_args()

    args = Args(
        force=parsed.force,
        dry_run=parsed.dry_run,
        debug=parsed.debug,
        clear=parsed.clear,
        criar_subtasks=parsed.criar_subtasks,
        criar_links=parsed.criar_links
    )

    project_path = Path(parsed.project_dir).resolve()
    
    if not setup_env(project_path):
        log_error("Variáveis de ambiente faltando no .env local.")
        log_error("Necessários: JIRA_DOMAIN, JIRA_EMAIL, JIRA_TOKEN, JIRA_PROJECT_KEY")
        sys.exit(1)

    print("=" * 60)
    print("🚀 JIRA SYNC - Sincronizador de Projetos (Descentralizado)")
    print(f"📍 Projeto Base: {project_path}")
    print(f"🔑 Chave Jira: {PROJECT_KEY}")
    print("=" * 60)

    projetos, config = carregar_projetos(project_path)

    if not projetos:
        log_error(f"Nenhum projeto encontrado em {project_path}/projeto.yaml!")
        sys.exit(1)

    log_info(f"Carregados {len(projetos)} projetos do manifesto")

    state = criar_state_manager(state_dir=str(project_path))

    if args.clear:
        log_warning("Limpando estado anterior...")
        state.clear()

    if args.dry_run:
        log_warning("Modo DRY RUN - nenhuma issue será criada")

    total_criados = 0

    summary = state.get_summary()
    if summary["last_sync"]:
        log_info(f"Última sincronização: {summary['last_sync']}")
        log_info(f"Estado atual: {summary['tasks']} tasks, {summary['subtasks']} subtasks")

    for projeto_id, projeto_config in projetos.items():
        if args.dry_run:
            print(f"\n[DRY RUN] Projeto: {projeto_id}")
            print(f"  Tasks: {len(projeto_config.get('tasks', []))}")
        else:
            epico = sincronizar_projeto(projeto_id, projeto_config, state, args)
            if epico:
                total_criados += 1

    if not args.dry_run:
        state.save()
        log_info("Estado salvo")

    print("\n" + "=" * 60)
    print(f"🎉 Sincronização concluída!")
    print(f"   Projetos processados: {len(projetos)}")
    print(f"   Estado atualizado: {state.get_summary()}")
    print("=" * 60)


if __name__ == "__main__":
    main()
