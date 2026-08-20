#!/usr/bin/env python3
"""
validate_ecosystem.py
Valida a consistência do ecossistema GARE entre todas as fontes de verdade:
- REGISTRY/projects.json
- governance/operational-memory/status.md
- governance/architecture-decisions/contexto_rlm.md
- Jira (via API)
- .sync_state.json

Uso:
    python3 validate_ecosystem.py          # Valida tudo
    python3 validate_ecosystem.py --quick  # Só verifica arquivos locais (sem Jira)

Retorna exit code 0 se tudo consistente, 1 se encontrar problemas.
"""

import os
import sys
import json
import re
from pathlib import Path

try:
    from dotenv import load_dotenv
    config_dir = Path(__file__).parent.parent / "config"
    env_path = config_dir / ".env"
    if env_path.exists():
        load_dotenv(env_path)
except ImportError:
    pass

ROOT = Path(__file__).parent.parent.parent
REGISTRY_PATH = ROOT / "REGISTRY" / "projects.json"
STATUS_PATH = ROOT / "governance" / "operational-memory" / "status.md"
CONTEXTO_PATH = ROOT / "governance" / "architecture-decisions" / "contexto_rlm.md"
SYNC_STATE_PATH = ROOT / "infra" / "config" / ".sync_state.json"


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
        errors.append("❌ REGISTRY/projects.json não encontrado ou vazio")
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

    # V5: sync_state deve ter projetos registrados
    sync_projects = sync_state.get("projetos", {})
    if not sync_projects:
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

    DOMAIN = os.getenv("JIRA_DOMAIN")
    EMAIL = os.getenv("JIRA_EMAIL")
    TOKEN = os.getenv("JIRA_TOKEN")

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
