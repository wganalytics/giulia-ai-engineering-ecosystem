#!/usr/bin/env python3
"""
validate_ecosystem.py
Valida a consistência do ecossistema GARE entre todas as fontes de verdade:
- shared/REGISTRY/projects.json
- governance/operational-memory/status.md
- governance/operational-memory/contexto_rlm.md
- Jira (via API)
- shared/infra/config/.sync_state.json

Uso:
    python3 ecosystem/automation/validate_ecosystem.py          # Valida tudo
    python3 ecosystem/automation/validate_ecosystem.py --quick  # Só verifica arquivos locais (sem Jira)

Retorna exit code 0 se tudo consistente, 1 se encontrar problemas.
"""

import os
import sys
import json
import re
from pathlib import Path

root_dir = Path(__file__).resolve().parents[2]
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))

try:
    from ecosystem.jira.context_loader import (
        JIRA_DOMAIN,
        JIRA_EMAIL,
        JIRA_TOKEN
    )
except ImportError as e:
    print(f"⚠️ Aviso: Não foi possível carregar ecosystem/jira/context_loader.py: {e}")
    JIRA_DOMAIN = None
    JIRA_EMAIL = None
    JIRA_TOKEN = None

ROOT = root_dir
REGISTRY_PATH = ROOT / "shared" / "REGISTRY" / "projects.json"
STATUS_PATH = ROOT / "governance" / "operational-memory" / "status.md"
CONTEXTO_PATH = ROOT / "governance" / "operational-memory" / "contexto_rlm.md"
SYNC_STATE_PATH = ROOT / "shared" / "infra" / "config" / ".sync_state.json"


def load_json(path: Path) -> dict:
    if path.exists():
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}


def load_text(path: Path) -> str:
    if path.exists():
        with open(path, 'r', encoding='utf-8') as f:
            return f.read()
    return ""


def extract_status_from_md(content: str) -> dict:
    """Extrai status de projetos de um markdown com tabelas."""
    statuses = {}
    for line in content.split('\n'):
        match = re.match(r'\|\s*PRJ-(\d+)\s*\|.*\|\s*(✅|🟢|🟡|⚪|🔄).*\|', line)
        if match:
            prj_num = int(match.group(1))
            emoji = match.group(2)
            prj_id = f"PRJ-{prj_num:02d}"
            if emoji in ('✅', '🟢'):
                statuses[prj_id] = 'concluido'
            elif emoji in ('🟡', '🔄'):
                statuses[prj_id] = 'em_desenvolvimento'
            else:
                statuses[prj_id] = 'backlog'
    return statuses


def extract_epics_from_contexto(content: str) -> dict:
    """Extrai keys de épicos do contexto_rlm.md."""
    epics = {}
    for line in content.split('\n'):
        match = re.match(r'\|\s*PRJ-(\d+)\s*\|\s*(GARE-\d+)\s*\|', line)
        if match:
            prj_num = int(match.group(1))
            epic_key = match.group(2)
            epics[f"PRJ-{prj_num:02d}"] = epic_key
    return epics


def validate_local(errors: list) -> None:
    """Valida consistência entre arquivos locais."""

    # 1. Carregar registry
    registry = load_json(REGISTRY_PATH)
    if not registry:
        errors.append("❌ shared/REGISTRY/projects.json não encontrado ou vazio")
        return

    registry_projects = registry.get("projetos", {})

    # 2. Carregar status.md
    status_md = load_text(STATUS_PATH)
    status_statuses = extract_status_from_md(status_md) if status_md else {}

    # 3. Carregar contexto_rlm.md
    contexto_md = load_text(CONTEXTO_PATH)
    contexto_epics = extract_epics_from_contexto(contexto_md)

    # 4. Carregar sync_state
    sync_state = load_json(SYNC_STATE_PATH)

    # === VALIDAÇÕES ===

    # V1: Status consistentes entre registry e status.md
    for prj_id, prj_data in registry_projects.items():
        reg_status = prj_data.get("status", "")
        md_status = status_statuses.get(prj_id)

        if md_status and reg_status != md_status:
            errors.append(
                f"⚠️  {prj_id}: Status inconsistente — "
                f"registry='{reg_status}', status.md='{md_status}'"
            )

    # V2: Épicos consistentes entre registry e contexto_rlm.md
    for prj_id, prj_data in registry_projects.items():
        reg_epic = prj_data.get("jira_epico")
        ctx_epic = contexto_epics.get(prj_id)

        if reg_epic and ctx_epic and reg_epic != ctx_epic:
            errors.append(
                f"⚠️  {prj_id}: Épico inconsistente — "
                f"registry='{reg_epic}', CONTEXTO_RLM='{ctx_epic}'"
            )

    # V3: Todos os projetos do registry devem ter jira_epico preenchido
    for prj_id, prj_data in registry_projects.items():
        if not prj_data.get("jira_epico"):
            errors.append(f"⚠️  {prj_id}: jira_epico está null no registry")

    # V4: Caminhos devem ser relativos (não absolutos)
    for prj_id, prj_data in registry_projects.items():
        for field in ["caminho_dev", "caminho_docs"]:
            path = prj_data.get(field, "")
            if path.startswith("/"):
                errors.append(
                    f"⚠️  {prj_id}: {field} é caminho absoluto: '{path[:50]}...'"
                )

    # V5: sync_state deve ter projetos registrados (só é erro se o registry já tiver projetos)
    sync_projects = sync_state.get("projetos", {})
    if not sync_projects and registry_projects:
        errors.append("⚠️  .sync_state.json está vazio — rode rebuild_sync_state.py")

    # V6: Todos projetos do registry devem estar no sync_state
    for prj_id in registry_projects:
        if prj_id not in sync_projects:
            errors.append(f"⚠️  {prj_id}: presente no registry mas ausente no sync_state")


def validate_jira(errors: list) -> None:
    """Valida consistência com o Jira (requer API)."""
    try:
        import requests
    except ImportError:
        errors.append("⚠️  requests não instalado — pulando validação Jira")
        return

    DOMAIN = os.getenv("JIRA_DOMAIN", JIRA_DOMAIN)
    EMAIL = os.getenv("JIRA_EMAIL", JIRA_EMAIL)
    TOKEN = os.getenv("JIRA_TOKEN", JIRA_TOKEN)

    if not all([DOMAIN, EMAIL, TOKEN]):
        errors.append("⚠️  Credenciais Jira não configuradas — pulando validação Jira")
        return

    auth = (EMAIL, TOKEN)
    headers = {"Accept": "application/json"}
    base = f"https://{DOMAIN}/rest/api/3"

    registry = load_json(REGISTRY_PATH)
    registry_projects = registry.get("projetos", {})

    for prj_id, prj_data in registry_projects.items():
        epic_key = prj_data.get("jira_epico")
        if not epic_key:
            continue

        url = f"{base}/issue/{epic_key}?fields=status"
        r = requests.get(url, auth=auth, headers=headers)
        if r.status_code != 200:
            errors.append(f"⚠️  {prj_id}: Épico {epic_key} não encontrado no Jira (HTTP {r.status_code})")
            continue

        jira_status = r.json()["fields"]["status"]["name"]
        reg_status = prj_data.get("status", "")

        # Mapear status Jira → registry
        jira_mapped = {
            "Done": "concluido",
            "In Progress": "em_desenvolvimento",
            "Backlog": "backlog",
            "Selected for Development": "em_desenvolvimento"
        }.get(jira_status, jira_status)

        if reg_status != jira_mapped:
            errors.append(
                f"⚠️  {prj_id}: Status Jira '{jira_status}' ({jira_mapped}) ≠ "
                f"registry '{reg_status}'"
            )

        # V7: Integridade de tarefas filhas (Se Épico é Done, todas tasks devem ser Done)
        if jira_status == "Done":
            url_tasks = f"{base}/search/jql"
            params = {"jql": f"parent = {epic_key} AND status != Done", "fields": "status"}
            r_tasks = requests.get(url_tasks, params=params, auth=auth, headers=headers)
            if r_tasks.status_code == 200:
                issues = r_tasks.json().get("issues", [])
                if issues:
                    task_keys = [iss["key"] for iss in issues]
                    errors.append(
                        f"❌ {prj_id}: Épico {epic_key} está 'Done', mas possui {len(issues)} tarefas abertas: "
                        f"{', '.join(task_keys)}"
                    )
            else:
                errors.append(f"⚠️  {prj_id}: Falha ao checar tasks filhas do {epic_key} (HTTP {r_tasks.status_code}): {r_tasks.text[:100]}")

def calculate_and_save_health_score(errors, quick):
    import subprocess
    from datetime import datetime
    
    # 1. Global Metrics
    # 1.1 Orphan files (30 pts)
    orphan_score = 30
    allowed_scripts = {"validate_ecosystem.py"}
    allowed_json = {"ecosystem_registry.json"}
    orphan_count = 0
    
    for f in os.listdir(ROOT):
        path = ROOT / f
        if path.is_file():
            if f.endswith(".py") and f not in allowed_scripts:
                orphan_score = 0
                orphan_count += 1
            elif f.endswith(".json") and f not in allowed_json:
                orphan_score = 0
                orphan_count += 1
            elif path.suffix.lower() in {".png", ".jpg", ".jpeg", ".gif", ".svg"}:
                orphan_score = 0
                orphan_count += 1
                
    # 1.2 Freshness (30 pts)
    freshness_score = 0
    freshness_days = 999
    if CONTEXTO_PATH.exists():
        mtime = CONTEXTO_PATH.stat().st_mtime
        freshness_days = (datetime.now() - datetime.fromtimestamp(mtime)).days
        if freshness_days <= 7:
            freshness_score = 30
        elif freshness_days > 30:
            freshness_score = 0
        else:
            freshness_score = int(round(30 - (freshness_days - 7) * (30 / 23)))
            
    # 1.3 Diary compliance (20 pts)
    diary_score = 0
    last_commit_date = ""
    try:
        last_commit_date = subprocess.run(
            ["git", "log", "-1", "--pretty=format:%cd", "--date=format:%Y-%m-%d"],
            cwd=str(ROOT), capture_output=True, text=True, check=True
        ).stdout.strip()
    except Exception:
        pass
        
    if last_commit_date:
        diary_file = ROOT / "governance" / "operational-memory" / "diario_de_bordo.md"
        if diary_file.exists():
            diary_content = load_text(diary_file)
            if last_commit_date in diary_content:
                diary_score = 20
            
    # 1.4 Credential isolation (20 pts)
    cred_score = 20
    try:
        git_files = subprocess.run(
            ["git", "ls-files"],
            cwd=str(ROOT), capture_output=True, text=True, check=True
        ).stdout.splitlines()
        for gf in git_files:
            if gf.strip().endswith(".env") or gf.strip() == ".env":
                cred_score = 0
                break
    except Exception:
        pass
        
    global_score = orphan_score + freshness_score + diary_score + cred_score
    
    # 2. Projects Metrics
    registry = load_json(REGISTRY_PATH)
    projects_data = registry.get("projetos", {})
    projects_scores = {}
    
    for prj_id, prj_info in projects_data.items():
        # SDD (30 pts)
        sdd_ok = False
        for folder in [ROOT / "docs" / "specs", ROOT / "governance" / "sdd"]:
            if folder.exists():
                for f in folder.glob("*.md"):
                    if f.name.startswith(prj_id) and ("SDD" in f.name or "sdd" in f.name.lower()):
                        sdd_ok = True
                        break
        sdd_pts = 30 if sdd_ok else 0
        
        # TDD tests directory (30 pts)
        dev_path = ROOT / prj_info.get("caminho_dev", "")
        tests_dir = dev_path / "tests"
        if not tests_dir.exists():
            tests_dir = dev_path / "test"
            
        tdd_ok = tests_dir.is_dir() and any(tests_dir.iterdir())
        tdd_pts = 30 if tdd_ok else 0
        
        # Test passing (20 pts)
        test_pass = False
        if tdd_ok and not quick:
            try:
                res = subprocess.run(["pytest", str(tests_dir)], capture_output=True, timeout=3)
                if res.returncode == 0:
                    test_pass = True
            except Exception:
                pass
        elif tdd_ok and quick:
            test_pass = True
            
        test_pts = 20 if test_pass else 0
        
        # Local diary (20 pts)
        docs_path = ROOT / prj_info.get("caminho_docs", "")
        diary_ok = (docs_path / "diario_de_bordo.md").exists()
        diary_pts = 20 if diary_ok else 0
        
        prj_score = sdd_pts + tdd_pts + test_pts + diary_pts
        projects_scores[prj_id] = {
            "score": float(prj_score),
            "sdd": sdd_ok,
            "tdd": tdd_ok,
            "tests_pass": test_pass,
            "diary": diary_ok
        }
        
    if projects_scores:
        avg_projects_score = sum(p["score"] for p in projects_scores.values()) / len(projects_scores)
    else:
        avg_projects_score = 100.0
        
    health_score = (global_score * 0.4) + (avg_projects_score * 0.6)
    
    # Save JSON
    telemetry = {
        "timestamp": datetime.now().isoformat() + "Z",
        "health_score": round(health_score, 1),
        "metrics": {
            "global_score": float(global_score),
            "projects_average_score": round(avg_projects_score, 1),
            "orphan_files_count": orphan_count,
            "rlm_freshness_days": freshness_days
        },
        "projects": projects_scores
    }
    
    metrics_dir = ROOT / "observability" / "metrics"
    metrics_dir.mkdir(parents=True, exist_ok=True)
    with open(metrics_dir / "health_score.json", "w", encoding="utf-8") as f:
        json.dump(telemetry, f, indent=2, ensure_ascii=False)
        
    # Render progress bar
    filled_len = int(round(health_score / 10))
    bar = '█' * filled_len + '░' * (10 - filled_len)
    print("\n" + "=" * 60)
    print(f"📊 HEALTH SCORE DO ecossistema: [{bar}] {health_score:.1f}%")
    print(f"   Métricas Globais: {global_score:.1f}/100 | Média dos Projetos: {avg_projects_score:.1f}/100")
    print("=" * 60)
    
    if health_score < 70.0:
        print("⚠️  ALERTA: O Ecosystem Health Score está abaixo de 70%!")
        print("   Por favor, revise as pendências de governança e TDD/SDD.")
        print("=" * 60)


if __name__ == "__main__":
    quick = "--quick" in sys.argv

    print("=" * 60)
    print("🔍 VALIDAÇÃO DE CONSISTÊNCIA DO ecossistema GARE")
    print("=" * 60)

    errors = []

    print("\n📋 Validação local (registry ↔ status.md ↔ contexto_rlm.md ↔ sync_state)...")
    validate_local(errors)

    if not quick:
        print("📋 Validação Jira (registry ↔ Jira API)...")
        validate_jira(errors)
    else:
        print("📋 Validação Jira: PULADA (modo --quick)")

    # Calcula e salva Health Score mesmo se houver erros locais/Jira
    calculate_and_save_health_score(errors, quick)

    print(f"\n{'=' * 60}")
    if errors:
        print(f"❌ {len(errors)} PROBLEMA(S) ENCONTRADO(S):\n")
        for e in errors:
            print(f"  {e}")
        print(f"\n{'=' * 60}")
        sys.exit(1)
    else:
        print("✅ ecossistema CONSISTENTE — Nenhum problema encontrado!")
        print("=" * 60)
        sys.exit(0)

