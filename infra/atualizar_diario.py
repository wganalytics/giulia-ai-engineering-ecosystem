#!/usr/bin/env python3
"""
Atualizador do Diário de Bordo

Script que автоматически atualiza o diario_de_bordo.md com base no estado atual.
Deve ser chamado ao final de cada sessão/scripts significativos.

用法:
    python atualizar_diario.py              # Atualiza com base no estado atual
    python atualizar_diario.py --force       # Força nova sessão
    python atualizar_diario.py --sessao "Descrição da sessão"
    python atualizar_diario.py --log "Feito algo"
"""

from __future__ import annotations

import os
import sys
import argparse
from datetime import datetime
from pathlib import Path
from typing import Any

# Add lib to path
sys.path.insert(0, str(Path(__file__).parent.parent / "lib"))

# Imports para logging
try:
    from file_logger import get_file_logger, log_project_start
    HAS_FILE_LOG = True
except ImportError:
    HAS_FILE_LOG = False


# ============================================
# CONFIGURAÇÃO
# ============================================

SCRIPT_DIR = Path(__file__).parent
ROOT_DIR = SCRIPT_DIR.parent

DIARIO_PATH = ROOT_DIR / "governance" / "operational-memory" / "diario_de_bordo.md"
REGISTRY_PATH = ROOT_DIR / "REGISTRY" / "projects.json"
SYNC_STATE_PATH = ROOT_DIR / "infra" / "config" / ".sync_state.json"

# Template para nova sessão
SESSAO_TEMPLATE = """---

### Sessão #{session_number} — {date}
**Agente:** {agent}  
**Foco:** {focus}

**O que foi feito:**
{what_done}

**Próximos passos:**
{next_steps}

**Status do projeto:**
{project_status}
"""


# ============================================
# FUNÇÕES
# ============================================

def load_json(file_path: Path) -> dict | None:
    """Carrega arquivo JSON."""
    if file_path.exists():
        with open(file_path, 'r', encoding='utf-8') as f:
            return __import__('json').load(f)
    return None


def get_project_status() -> dict[str, Any]:
    """Coleta status atual dos projetos."""
    status = {
        "projetos_em_andamento": [],
        "projetos_concluidos": [],
        "tarefas_jira": {},
        "ultima_sincronizacao": None
    }
    
    # Carrega registry
    registry = load_json(REGISTRY_PATH)
    if registry:
        for proj_id, proj in registry.get("projetos", {}).items():
            if proj.get("status") == "em_desenvolvimento":
                status["projetos_em_andamento"].append({
                    "id": proj_id,
                    "nome": proj.get("nome"),
                    "tasks": proj.get("tasks", {})
                })
            elif proj.get("status") == "concluido":
                status["projetos_concluidos"].append(proj_id)
    
    # Carrega sync state
    sync_state = load_json(SYNC_STATE_PATH)
    if sync_state:
        status["ultima_sincronizacao"] = sync_state.get("last_sync")
        status["tarefas_jira"] = {
            "total": sync_state.get("tasks", {}).__len__() if sync_state.get("tasks") else 0,
            "projetos": len(sync_state.get("projetos", {}))
        }
    
    return status


def format_project_status(status: dict) -> str:
    """Formata status dos projetos para o diário."""
    lines = []
    
    if status.get("projetos_em_andamento"):
        lines.append("**Projetos em Desenvolvimento:**")
        for proj in status["projetos_em_andamento"]:
            tasks = proj.get("tasks", {})
            total = tasks.get("total", 0)
            concluidas = tasks.get("concluidas", 0)
            lines.append(f"- {proj['id']}: {proj['nome']} ({concluidas}/{total} tasks)")
    
    if status.get("projetos_concluidos"):
        lines.append("\n**Projetos Concluídos:**")
        for proj_id in status["projetos_concluidos"]:
            lines.append(f"- {proj_id}")
    
    if status.get("ultima_sincronizacao"):
        lines.append(f"\n**Última sincronização:** {status['ultima_sincronizacao']}")
    
    return "\n".join(lines) if lines else "Sem projetos em desenvolvimento"


def get_max_session_number(diario_content: str) -> int:
    """Extrai o maior número de sessão existente no diário."""
    import re
    # Captura números em '### Sessão #NNN' (com ou sem zeros à esquerda, com ou sem sufixo)
    matches = re.findall(r'### Sessão #(\d+)', diario_content)
    if not matches:
        return 0
    return max(int(n) for n in matches)


def get_next_session_number(diario_content: str, auto: bool = False) -> str:
    """Retorna próximo número de sessão sem colisão.
    
    Sessões automáticas recebem sufixo '-auto' para evitar
    colisão com sessões manuais.
    """
    max_num = get_max_session_number(diario_content)
    next_num = max_num + 1
    suffix = "-auto" if auto else ""
    return f"{next_num:03d}{suffix}"


def create_session_entry(
    session_number: str,
    agent: str = "Agente IA",
    focus: str = "Desenvolvimento",
    what_done: str = "- Tarefas automáticas",
    next_steps: str = "- Continuar desenvolvimento"
) -> str:
    """Cria uma nova entrada de sessão."""
    date = datetime.now().strftime("%Y-%m-%d")
    project_status = format_project_status(get_project_status())
    
    return SESSAO_TEMPLATE.format(
        session_number=session_number,
        date=date,
        agent=agent,
        focus=focus,
        what_done=what_done,
        next_steps=next_steps,
        project_status=project_status
    )


def update_diario(
    agent: str = "Agente IA",
    focus: str = "Desenvolvimento",
    what_done: str = "- Tarefas automáticas",
    next_steps: str = "- Continuar desenvolvimento",
    force: bool = False,
    auto: bool = True
) -> None:
    """Atualiza o diário de bordo."""
    
    # Carrega diário atual
    if DIARIO_PATH.exists():
        with open(DIARIO_PATH, 'r', encoding='utf-8') as f:
            content = f.read()
    else:
        print("❌ Diário de bordo não encontrado!")
        return
    
    # Verifica se precisa criar nova sessão
    if not force:
        today = datetime.now().strftime("%Y-%m-%d")
        if today not in content[-500:]:
            force = True
    
    # Calcular próximo número de sessão sem colisão
    session_number = get_next_session_number(content, auto=auto)
    
    # Criar nova sessão
    new_session = create_session_entry(
        session_number=session_number,
        agent=agent,
        focus=focus,
        what_done=what_done,
        next_steps=next_steps
    )
    
    # Inserir após a marca "## 📝 Registro de Sessões"
    if "## 📝 Registro de Sessões" in content:
        content = content.replace(
            "## 📝 Registro de Sessões\n\n---",
            f"## 📝 Registro de Sessões\n{new_session}\n"
        )
    
    # Salvar
    with open(DIARIO_PATH, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"✅ Diário atualizado! Sessão #{session_number} adicionada.")
    
    # Log se disponível
    if HAS_FILE_LOG:
        logger = get_file_logger()
        logger.log_execution(
            script="atualizar_diario",
            action="Atualizar diário",
            status="success",
            details={"sessao": session_number}
        )


def quick_log(message: str) -> None:
    """Adiciona um log rápido ao que foi feito."""
    update_diario(
        agent="Agente IA",
        focus="Sessão automática",
        what_done=f"- {message}",
        next_steps="- Continuar desenvolvimento"
    )


# ============================================
# MAIN
# ============================================

def main() -> None:
    """Função principal."""
    parser = argparse.ArgumentParser(
        description="Atualizador do Diário de Bordo",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemplos:
  python atualizar_diario.py --force
  python atualizar_diario.py --agent "Gemini" --focus "Setup inicial"
  python atualizar_diario.py --log "Configurado ambiente"
        """
    )
    
    parser.add_argument("--force", action="store_true", help="Força nova sessão")
    parser.add_argument("--agent", type=str, default="Agente IA", help="Nome do agente")
    parser.add_argument("--focus", type=str, default="Desenvolvimento", help="Foco da sessão")
    parser.add_argument("--log", type=str, help="Mensagem do que foi feito")
    parser.add_argument("--next", type=str, default="Continuar desenvolvimento", help="Próximos passos")
    
    args = parser.parse_args()
    
    if args.log:
        quick_log(args.log)
    else:
        update_diario(
            agent=args.agent,
            focus=args.focus,
            what_done=args.log or "- Sessão automática",
            next_steps=args.next,
            force=args.force
        )


if __name__ == "__main__":
    main()