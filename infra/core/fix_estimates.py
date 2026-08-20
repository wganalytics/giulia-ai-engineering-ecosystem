#!/usr/bin/env python3
"""
fix_estimates.py
Sincroniza Original Estimate dos cards que estão com 0m/vazio,
buscando os valores do projetos.yaml como fonte de verdade.

Uso:
    python3 fix_estimates.py              # Dry-run (auditar)
    python3 fix_estimates.py --execute    # Aplicar correções
"""

import os
import sys
import json
import requests
from pathlib import Path

try:
    import yaml
except ImportError:
    print("❌ Instale PyYAML: pip install pyyaml")
    sys.exit(1)

try:
    from dotenv import load_dotenv
    config_dir = Path(__file__).parent.parent / "config"
    env_path = config_dir / ".env"
    if env_path.exists():
        load_dotenv(env_path)
    else:
        load_dotenv()
except ImportError:
    pass

DOMAIN = os.getenv("JIRA_DOMAIN")
EMAIL = os.getenv("JIRA_EMAIL")
TOKEN = os.getenv("JIRA_TOKEN")
PROJECT = os.getenv("JIRA_PROJECT_KEY", "GARE")

if not all([DOMAIN, EMAIL, TOKEN]):
    print("❌ ERRO: Variáveis JIRA_DOMAIN, JIRA_EMAIL, JIRA_TOKEN não encontradas.")
    sys.exit(1)

auth = (EMAIL, TOKEN)
headers = {"Accept": "application/json", "Content-Type": "application/json"}
base = f"https://{DOMAIN}/rest/api/3"


def parse_estimate_to_seconds(estimate_str: str) -> int:
    """Converte '4h' -> 14400, '30m' -> 1800, '1d' -> 28800"""
    estimate_str = str(estimate_str).strip().lower()
    if estimate_str.endswith('h'):
        return int(estimate_str[:-1]) * 3600
    elif estimate_str.endswith('m'):
        return int(estimate_str[:-1]) * 60
    elif estimate_str.endswith('d'):
        return int(estimate_str[:-1]) * 8 * 3600
    try:
        return int(estimate_str) * 3600
    except ValueError:
        return 0


def get_all_tasks() -> list[dict]:
    """Busca todas as tasks do projeto GARE."""
    jql = f'project = {PROJECT} AND issuetype = Task ORDER BY key ASC'
    all_issues = []
    start_at = 0

    while True:
        url = f"{base}/search/jql"
        params = {
            "jql": jql,
            "maxResults": 50,
            "startAt": start_at,
            "fields": "key,summary,timetracking"
        }
        r = requests.get(url, params=params, auth=auth, headers=headers)
        if r.status_code != 200:
            # Try older endpoint
            url = f"{base}/search"
            r = requests.get(url, params=params, auth=auth, headers=headers)
            if r.status_code != 200:
                print(f"  ⚠️  Erro na busca: HTTP {r.status_code}")
                break

        data = r.json()
        issues = data.get("issues", [])
        all_issues.extend(issues)

        if start_at + len(issues) >= data.get("total", 0):
            break
        start_at += len(issues)

    return all_issues


def set_issue_estimate(key: str, seconds: int) -> int:
    """Define o Original Estimate de uma issue."""
    url = f"{base}/issue/{key}"
    payload = {"fields": {"timetracking": {"originalEstimateSeconds": seconds}}}
    r = requests.put(url, json=payload, auth=auth, headers=headers)
    return r.status_code


def load_yaml_estimates() -> dict[str, int]:
    """Carrega estimativas do projetos.yaml indexadas por summary."""
    yaml_path = Path(__file__).parent.parent / "config" / "projetos.yaml"
    if not yaml_path.exists():
        print(f"  ⚠️  {yaml_path} não encontrado")
        return {}

    with open(yaml_path, 'r', encoding='utf-8') as f:
        projects = yaml.safe_load(f)

    estimates = {}
    for proj_id, proj_data in projects.get("projetos", {}).items():
        for task in proj_data.get("tasks", []):
            summary = task.get("summary", "")
            estimate = task.get("estimate")
            if summary and estimate:
                seconds = parse_estimate_to_seconds(estimate)
                if seconds > 0:
                    estimates[summary.strip()] = seconds

    return estimates


if __name__ == "__main__":
    dry_run = "--execute" not in sys.argv

    print("=" * 60)
    if dry_run:
        print("🔍 MODO DRY-RUN — Nenhuma alteração será feita.")
        print("   Use --execute para aplicar as correções.")
    else:
        print("🔧 MODO EXECUTE — Estimativas serão CORRIGIDAS.")
    print("=" * 60)

    # Carregar estimativas esperadas do YAML
    yaml_estimates = load_yaml_estimates()
    print(f"\n📄 Carregadas {len(yaml_estimates)} estimativas do projetos.yaml")

    # Buscar todas as tasks no Jira
    tasks = get_all_tasks()
    print(f"📋 Encontradas {len(tasks)} tasks no Jira")

    needs_fix = 0
    fixed = 0

    for task in tasks:
        key = task["key"]
        summary = task["fields"]["summary"].strip()
        tt = task["fields"].get("timetracking") or {}
        current_seconds = tt.get("originalEstimateSeconds", 0) or 0

        # Buscar estimate esperado pelo summary
        expected_seconds = yaml_estimates.get(summary, 0)

        if current_seconds == 0 and expected_seconds > 0:
            hours = expected_seconds / 3600
            print(f"\n  ⚠️  {key}: estimate=0m, deveria ser {hours:.0f}h ({expected_seconds}s)")
            print(f"     Summary: {summary[:60]}...")
            needs_fix += 1

            if not dry_run:
                status = set_issue_estimate(key, expected_seconds)
                if status in (200, 204):
                    print(f"     ✅ Corrigido (HTTP {status})")
                    fixed += 1
                else:
                    print(f"     ❌ Falha (HTTP {status})")

    print(f"\n{'=' * 60}")
    if dry_run:
        print(f"📊 Tasks com estimate zerado: {needs_fix}")
    else:
        print(f"📊 Correções aplicadas: {fixed}/{needs_fix}")
    print("=" * 60)
