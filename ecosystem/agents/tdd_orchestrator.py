import os
import sys
import subprocess
from pathlib import Path
from datetime import datetime

ECOSYSTEM_ROOT = Path(__file__).resolve().parent.parent.parent
GOVERNANCE_TDD_DIR = ECOSYSTEM_ROOT / "governance" / "tdd"

def find_testable_projects():
    """Retorna uma lista de diretórios raízes (PRJs e Infra) que contêm testes."""
    projects = []
    
    # Adicionar projetos RAG (PRJ-*)
    rag_dir = ECOSYSTEM_ROOT / "dev" / "rag"
    if rag_dir.exists():
        for prj in rag_dir.iterdir():
            if prj.is_dir() and "PRJ-" in prj.name:
                projects.append(prj)
                
    # Adicionar Shared Infra
    infra_dir = ECOSYSTEM_ROOT / "shared" / "infra"
    if infra_dir.exists():
        projects.append(infra_dir)
        
    return projects

def run_tests_isolated(project_dir: Path):
    """Roda pytest de forma isolada dentro da pasta do projeto e retorna a saída."""
    env = os.environ.copy()
    # Para garantir que o projeto ache o seu próprio src ou core
    env["PYTHONPATH"] = str(project_dir) + os.pathsep + str(ECOSYSTEM_ROOT)
    
    cmd = ["pytest", "--tb=short", "-v"]
    
    print(f"   [🚀] Rodando testes em: {project_dir.name}...")
    result = subprocess.run(cmd, cwd=str(project_dir), capture_output=True, text=True, env=env)
    return result.stdout

def parse_pytest_output(stdout: str):
    """Analisa o output do pytest para contar pass, fail, etc."""
    passed = 0
    failed = 0
    skipped = 0
    
    for line in stdout.splitlines():
        if "==" in line and ("passed" in line or "failed" in line):
            parts = line.strip("= ").split(",")
            for p in parts:
                p = p.strip()
                if "passed" in p:
                    passed += int(p.split()[0])
                elif "failed" in p:
                    failed += int(p.split()[0])
                elif "skipped" in p:
                    skipped += int(p.split()[0])
                    
    total = passed + failed + skipped
    return total, passed, failed, skipped

def generate_markdown_snapshot(total, passed, failed, skipped, all_logs, project_summaries):
    """Gera o arquivo Markdown na pasta governance/tdd/"""
    GOVERNANCE_TDD_DIR.mkdir(parents=True, exist_ok=True)
    
    date_str = datetime.now().strftime("%Y-%m-%d")
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    snapshot_path = GOVERNANCE_TDD_DIR / f"TDD_SNAPSHOT_{date_str}.md"
    
    health_score = 0
    if total > 0:
        health_score = int((passed / total) * 100)
    
    status_emoji = "🟢 EXCELENTE" if health_score == 100 else ("🟡 ALERTA" if health_score >= 80 else "🔴 CRÍTICO")
    if failed > 0:
        status_emoji = "🔴 CRÍTICO (TESTES FALHANDO)"
        
    summary_list = "\n".join([f"- **{prj}**: {stat}" for prj, stat in project_summaries.items()])
        
    md_content = f"""# 🧪 TDD Ecosystem Snapshot
    
> **Data da Auditoria:** {timestamp}
> **Status de Saúde:** {status_emoji} ({health_score}% Passing)

Este relatório foi gerado automaticamente pelo **TDD Orchestrator Agent**.
A execução dos testes agora é feita em contêineres lógicos (Loop DevOps isolado), garantindo a resolução correta de imports de todo o ecossistema.

---

## 📊 Resumo Executivo (Agregado)
- **Total de Testes:** {total}
- **Passaram (Green):** {passed}
- **Falharam (Red):** {failed}
- **Ignorados (Skipped):** {skipped}

---

## 🗂️ Cobertura por Módulo
{summary_list}

---

## 🔍 Logs Completos da Execução
```text
{all_logs.strip()}
```
"""
    
    snapshot_path.write_text(md_content, encoding="utf-8")
    return snapshot_path

def main():
    print("🛡️ Giulia AI TDD Orchestrator (Isolamento de Monorepo Ativado)")
    
    projects = find_testable_projects()
    print(f"🏃‍♂️ Encontrados {len(projects)} projetos no ecossistema.\n")
    
    global_total, global_passed, global_failed, global_skipped = 0, 0, 0, 0
    all_logs = ""
    project_summaries = {}
    
    for prj in projects:
        stdout = run_tests_isolated(prj)
        
        # Ignorar caso o projeto não tenha nenhum teste encontrado pelo pytest (exit code 5)
        if "no tests ran" in stdout.lower() or "collected 0 items" in stdout:
            project_summaries[prj.name] = "⚠️ Nenhum teste encontrado (Vibe Coding detectado)"
            all_logs += f"\n\n=== {prj.name} ===\n{stdout}"
            continue
            
        t, p, f, s = parse_pytest_output(stdout)
        global_total += t
        global_passed += p
        global_failed += f
        global_skipped += s
        
        score_txt = f"{p}/{t} passaram"
        if f > 0:
            score_txt += f" | {f} FALHAS"
            project_summaries[prj.name] = f"🔴 {score_txt}"
        else:
            project_summaries[prj.name] = f"🟢 {score_txt}"
            
        all_logs += f"\n\n=== {prj.name} ===\n{stdout}"
    
    snapshot_path = generate_markdown_snapshot(
        global_total, global_passed, global_failed, global_skipped, 
        all_logs, project_summaries
    )
    
    print(f"\n✅ Snapshot de TDD gerado com sucesso!")
    print(f"📊 Total de testes reais coletados: {global_total} ({global_passed} Passaram, {global_failed} Falharam)")
    print(f"💾 Salvo em: {snapshot_path}")
    
    if global_failed > 0:
        print("\n⚠️ ALERTA: Há testes falhando! Verifique o Snapshot.")
        sys.exit(1)
    else:
        print("\n🟢 Ecossistema saudável e testado.")
        sys.exit(0)

if __name__ == "__main__":
    main()
