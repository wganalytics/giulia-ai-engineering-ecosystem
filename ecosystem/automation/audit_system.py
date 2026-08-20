# ecosystem/automation/audit_system.py
import os
import json
import subprocess
from pathlib import Path

def auditar_ecossistema():
    base_dir = Path("dev")
    projetos_mapeados = {}

    print("🔍 Iniciando Auditoria Completa da Linha de Montagem...")

    if not base_dir.exists():
        print("❌ Erro: Diretório 'dev/' não encontrado na raiz.")
        return

    # Varre os silos (ex: rag, mcp)
    for silo in base_dir.iterdir():
        if silo.is_dir():
            for projeto in silo.iterdir():
                if projeto.is_dir():
                    path_str = str(projeto).replace("\\", "/")
                    
                    # Checa os componentes vitais do chassi de controle
                    has_yaml = (projeto / "projetos.yaml").exists()
                    has_env = (projeto / ".env").exists()
                    has_trace = (projeto / "handoff_trace.jsonl").exists()
                    has_specs = (projeto / "specs").is_dir()

                    # Verificação de TDD (pasta tests com pelo menos um arquivo .py)
                    pasta_tests = projeto / "tests"
                    has_tdd = False
                    if pasta_tests.is_dir():
                        has_tdd = any(f.suffix == ".py" for f in pasta_tests.iterdir() if f.is_file())

                    # Verificação de placeholders nas specs
                    has_placeholders = False
                    if has_specs:
                        for f in (projeto / "specs").iterdir():
                            if f.is_file() and f.suffix == ".md":
                                try:
                                    conteudo = f.read_text(encoding="utf-8").lower()
                                    if any(w in conteudo for w in ["todo", "placeholder", "mock", "lorem ipsum"]):
                                        has_placeholders = True
                                        break
                                except Exception:
                                    pass

                    # Verificação de alinhamento Git
                    git_status_res = subprocess.run(
                        ["git", "status", "--porcelain", str(projeto)],
                        capture_output=True,
                        text=True
                    )
                    git_alinhado = (git_status_res.returncode == 0 and not git_status_res.stdout.strip())

                    projetos_mapeados[path_str] = {
                        "nome": projeto.name,
                        "silo": silo.name,
                        "caminho_completo": path_str,
                        "status_arquivos": {
                            "projetos_yaml": has_yaml,
                            ".env": has_env,
                            "handoff_trace_jsonl": has_trace,
                            "pasta_specs": has_specs,
                            "cobertura_tdd": has_tdd,
                            "specs_sem_placeholder": not has_placeholders,
                            "git_alinhado": git_alinhado
                        },
                        "integro": has_yaml and has_trace and has_specs and has_tdd and not has_placeholders
                    }

    # Salva o relatório de auditoria para o script de reparo consumir
    output_path = Path("ecosystem/automation/audit_report.json")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(projetos_mapeados, f, indent=4, ensure_ascii=False)

    print(f"\n✅ Auditoria concluída. Relatório salvo em: {output_path}")
    print(f"Total de projetos mapeados: {len(projetos_mapeados)}")
    
    # Exibe resumo no terminal
    for p, dados in projetos_mapeados.items():
        status = "🟢 ÍNTEGRO" if dados["integro"] else "🔴 INCOMPLETO"
        print(f"- {p}: {status}")

if __name__ == "__main__":
    auditar_ecossistema()