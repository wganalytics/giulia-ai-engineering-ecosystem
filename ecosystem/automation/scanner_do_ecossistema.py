#!/usr/bin/env python3
"""
scan_ecosystem.py
=================
Varrimento automático e auditoria de conformidade do ecossistema GIULIA AI.
Gera o relatório de conformidade DIAGNOSTICO_ARQUITETURA.md.
"""

import os
from pathlib import Path
from datetime import datetime

# Definição de caminhos absolutos baseados na estrutura do monorepo
ROOT = Path(__file__).resolve().parents[2]
DEV_DIR = ROOT / "dev"
AUTOMATION_DIR = ROOT / "ecosystem" / "automation"

def analisar_estrutura() -> None:
    """
    Executa uma varredura completa ao monorepo para identificar o estado dos componentes,
    detetar ficheiros órfãos ou obsoletos e validar o isolamento técnico.
    """
    report = []
    report.append("# 📊 DIAGNÓSTICO DE ARQUITETURA — GIULIA AI\n")
    report.append(f"Gerado em: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    # 1. Componentes de Automação da Esteira
    report.append("## 📂 1. Status dos Componentes de Automação (`ecosystem/automation/`) ")
    scripts = ["circuit_breaker.py", "cognition_router.py", "dynamic_escalator.py", "run_tdd_pipeline.sh"]
    
    for script in scripts:
        path = AUTOMATION_DIR / script
        if path.exists():
            executavel = os.access(path, os.X_OK)
            status = "✅ Íntegro" + (" (Executável)" if executavel else " (Sem permissão +x)")
        else:
            status = "❌ Ausente"
        report.append(f"- **{script}**: {status}")
    report.append("")

    # 2. Auditoria de Linha de Montagem de Projetos (dev/)
    report.append("## 🏭 2. Auditoria da Linha de Montagem (`dev/`) ")
    to_do_commands = []
    
    if not DEV_DIR.exists():
        report.append("❌ Diretório 'dev/' não encontrado.")
        to_do_commands.append("mkdir -p dev")
    else:
        # Analisa cada subpasta de categoria no diretório dev/
        categorias = [p for p in DEV_DIR.iterdir() if p.is_dir() and p.name not in ["venv", ".venv", "data"]]
        projetos = []
        
        for cat in categorias:
            # Projetos reais estão localizados um nível abaixo (ex: dev/dominio/prj-xx_nome_do_projeto)
            sub_pastas = [sp for sp in cat.iterdir() if sp.is_dir() and sp.name not in ["__pycache__", ".pytest_cache"]]
            if sub_pastas:
                projetos.extend(sub_pastas)
        
        if not projetos:
            report.append("ℹ️ Nenhum projeto ativo encontrado nas subpastas estruturais de 'dev/'.")
        
        for proj in projetos:
            rel_path = proj.relative_to(ROOT)
            report.append(f"### 📦 Projeto: {rel_path}")
            
            yaml_pct = proj / "projetos.yaml"
            env_pct = proj / ".env"
            trace_pct = proj / "handoff_trace.jsonl"
            
            report.append(f"- `projetos.yaml`: {'✅ Encontrado' if yaml_pct.exists() else '❌ Ausente'}")
            report.append(f"- `.env`: {'✅ Encontrado' if env_pct.exists() else '❌ Ausente'}")
            
            if trace_pct.exists():
                report.append("- `handoff_trace.jsonl`: ✅ Ativo")
            else:
                report.append("- `handoff_trace.jsonl`: ⚠️ Ausente (Será iniciado no primeiro ciclo)")
                to_do_commands.append(f"touch {rel_path}/handoff_trace.jsonl")

    # 3. Resíduos e Acoplamentos no Core
    report.append("\n## 🧼 3. Verificação de Resíduos no Core ")
    residuos = False
    
    # Restringe a varredura de resíduos apenas à pasta ecosystem/ e shared/infra/
    # Evita falsos positivos na pasta de artigos de marketing/documentação
    central_files = []
    for p in ROOT.glob("ecosystem/**/*"):
        if p.is_file():
            central_files.append(p)
    for p in ROOT.glob("shared/infra/**/*"):
        if p.is_file():
            central_files.append(p)
            
    for f in central_files:
        if any(palavra in f.name.lower() for palavra in ["rag", "chroma", "neo4j"]):
            if any(exempt in f.name for exempt in ["circuit_breaker", "cognition_router", "dynamic_escalator", "scan_ecosystem"]):
                continue
            report.append(f"- ⚠️ Ficheiro específico/antigo encontrado no core: `{f.relative_to(ROOT)}`")
            residuos = True
            
    if not residuos:
        report.append("✅ Núcleo limpo. Sem acoplamentos de ferramentas de clientes.")

    # 4. Lista de Ações Imediatas
    report.append("\n## 🛠️ 4. Lista de Ações Imediatas (To-Do) ")
    
    # Valida as permissões de execução para os scripts da esteira
    for script in scripts:
        path = AUTOMATION_DIR / script
        if path.exists() and not os.access(path, os.X_OK):
            to_do_commands.append(f"chmod +x ecosystem/automation/{script}")
            
    if to_do_commands:
        report.append("Execute os seguintes comandos no terminal para corrigir o ecossistema:\n")
        report.append("```bash")
        for cmd in to_do_commands:
            report.append(cmd)
        report.append("```")
    else:
        report.append("✅ Tudo pronto. Nenhuma ação de correção imediata necessária.")

    # Escrita do relatório final formatado
    with open(ROOT / "DIAGNOSTICO_ARQUITETURA.md", "w", encoding="utf-8") as f:
        f.write("\n".join(report))

if __name__ == "__main__":
    analisar_estrutura()
    print("✅ Varredura concluída. Relatório salvo em 'DIAGNOSTICO_ARQUITETURA.md'.")