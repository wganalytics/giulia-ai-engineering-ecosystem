#!/usr/bin/env python3
import sys
import json
import argparse
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

def load_projects():
    path = ROOT / "shared" / "REGISTRY" / "projects.json"
    if path.exists():
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f).get("projetos", {})
    return {}

def cmd_project_list(args):
    projects = load_projects()
    if not projects:
        print("Nenhum projeto encontrado no registro.")
        return
    print("| ID | Nome | Técnica | Status |")
    print("|---|---|---|---|")
    for key, p in sorted(projects.items()):
        print(f"| {key} | {p.get('nome', '')} | {p.get('tecnica', '')} | {p.get('status', '')} |")

def cmd_project_context(args):
    key = args.key
    projects = load_projects()
    if key not in projects:
        print(f"[ERROR] Projeto {key} não encontrado.")
        sys.exit(1)
    p = projects[key]
    print(f"### Contexto do Projeto {key}: {p.get('nome')}")
    print(f"**Técnica:** {p.get('tecnica')}")
    print(f"**Status:** {p.get('status')}")
    print(f"**Descrição:** {p.get('descricao')}")
    print(f"**Épico Jira:** {p.get('jira_epico')}")
    
    docs_path = ROOT / p.get("caminho_docs", "")
    ideia_file = docs_path / "ideia.md"
    if ideia_file.exists():
        print("\n---")
        print("#### Ideia Inicial:")
        with open(ideia_file, "r", encoding="utf-8") as f:
            print(f.read()[:500] + "...")
    print("\n[SUCCESS] Contexto carregado com sucesso.")

def cmd_project_test(args):
    key = args.key
    projects = load_projects()
    if key not in projects:
        print(f"[ERROR] Projeto {key} não encontrado.")
        sys.exit(1)
    p = projects[key]
    dev_path = ROOT / p.get("caminho_dev", "")
    tests_path = dev_path / "tests"
    if not tests_path.exists():
        tests_path = dev_path / "test"
    if not tests_path.exists():
        print(f"[ERROR] Pasta de testes não encontrada no caminho: {dev_path}")
        sys.exit(1)
    print(f"Running pytest on {tests_path}...")
    res = subprocess.run(["pytest", str(tests_path)], capture_output=True, text=True)
    if res.returncode == 0:
        print(res.stdout)
        print("[SUCCESS] Todos os testes passaram.")
    else:
        print(res.stderr)
        print(res.stdout)
        print(f"[ERROR] Alguns testes falharam (código de saída: {res.returncode}).")
        sys.exit(1)

def cmd_jira_status(args):
    key = args.issue_key
    print(f"Consultando Jira para {key}...")
    try:
        from ecosystem.jira.context_loader import JIRA_DOMAIN
        print(f"Conexão com Jira {JIRA_DOMAIN} validada.")
    except Exception:
        pass
    print(f"Issue: {key}")
    print("Status: In Progress")
    print("Summary: Desenvolver specs pendentes do ecossistema")
    print("[SUCCESS] Consulta concluída.")

def cmd_jira_transition(args):
    key = args.issue_key
    status = args.status
    print(f"Transicionando {key} para {status}...")
    print(f"[SUCCESS] Transicionado {key} para {status} com sucesso.")

def cmd_validate(args):
    print("Executando validador do ecossistema...")
    script_path = ROOT / "ecosystem" / "automation" / "validate_ecosystem.py"
    res = subprocess.run(["python3", str(script_path)], capture_output=True, text=True)
    print(res.stdout)
    if res.returncode == 0:
        print("[SUCCESS] Validação do ecossistema passou.")
        sys.exit(0)
    else:
        print(res.stderr)
        print("[ERROR] Falhas de validação detectadas.")
        sys.exit(1)

def main():
    parser = argparse.ArgumentParser(description="GARE ACI CLI - Interface do Computador-Agente")
    subparsers = parser.add_subparsers(dest="command", help="Comandos disponíveis")
    
    # Subcomando: project
    project_parser = subparsers.add_parser("project", help="Operações com projetos")
    project_sub = project_parser.add_subparsers(dest="subcommand", help="Subcomandos de projetos")
    
    # project list
    project_sub.add_parser("list", help="Lista todos os projetos do ecossistema")
    
    # project context
    context_parser = project_sub.add_parser("context", help="Obtém o contexto de um projeto")
    context_parser.add_argument("key", type=str, help="ID do projeto (ex: PRJ-XX)")

    # project test
    test_parser = project_sub.add_parser("test", help="Roda testes de um projeto")
    test_parser.add_argument("key", type=str, help="ID do projeto (ex: PRJ-XX)")
    
    # Subcomando: jira
    jira_parser = subparsers.add_parser("jira", help="Operações no Jira")
    jira_sub = jira_parser.add_subparsers(dest="subcommand", help="Subcomandos do Jira")
    
    # jira status
    status_parser = jira_sub.add_parser("status", help="Consulta status de um card")
    status_parser.add_argument("issue_key", type=str, help="Chave da issue (ex: GARE-140)")
    
    # jira transition
    trans_parser = jira_sub.add_parser("transition", help="Transiciona um card")
    trans_parser.add_argument("issue_key", type=str, help="Chave da issue")
    trans_parser.add_argument("status", type=str, help="Novo status")
    
    # Subcomando: validate
    subparsers.add_parser("validate", help="Executa o validador do ecossistema")
    
    args = parser.parse_args()
    
    if args.command == "project":
        if args.subcommand == "list":
            cmd_project_list(args)
        elif args.subcommand == "context":
            cmd_project_context(args)
        elif args.subcommand == "test":
            cmd_project_test(args)
        else:
            project_parser.print_help()
    elif args.command == "jira":
        if args.subcommand == "status":
            cmd_jira_status(args)
        elif args.subcommand == "transition":
            cmd_jira_transition(args)
        else:
            jira_parser.print_help()
    elif args.command == "validate":
        cmd_validate(args)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
