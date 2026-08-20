#!/usr/bin/env python3
"""
Start Project - Script de Inicialização de Novos Projetos

用法:
    python start_project.py                          # Modo interativo
    python start_project.py --new PRJ-XX             # Criar PRJ-XX
    python start_project.py --list                   # Listar projetos
    python start_project.py --status PRJ-XX          # Ver status
    python start_project.py --init-jira PRJ-XX       # Inicializar no Jira

Funcionalidades:
- Criar estrutura de pastas para novo projeto
- Gerar documentos padrão (ideia.md, implementation_plan.md)
- Adicionar projeto ao registry
- Sincronizar com Jira (opcional)
"""

from __future__ import annotations

import os
import sys
import json
import argparse
from datetime import datetime
from pathlib import Path
from typing import Any

# Setup path para imports
SCRIPT_DIR = Path(__file__).parent
infra_DIR = SCRIPT_DIR.parent / "infra"
REGISTRY_DIR = SCRIPT_DIR.parent / "REGISTRY"
GOVERNANCE_DIR = SCRIPT_DIR.parent / "governance"
DEV_DIR = SCRIPT_DIR.parent / "DEV"

# Add lib to path
sys.path.insert(0, str(infra_DIR / "lib"))


# ============================================
# CONSTANTES E TIPOS
# ============================================

PROJECT_TEMPLATE = {
    "nome": "",
    "tecnica": "",
    "descricao": "",
    "status": "planejado",
    "jira_epico": None,
    "data_inicio": None,
    "caminho_dev": "",
    "caminho_docs": "",
    "tasks": {
        "total": 0,
        "concluidas": 0,
        "em_andamento": 0,
        "pendentes": 0
    }
}

TASK_TEMPLATE = {
    "id": "",
    "summary": "",
    "description": "",
    "subtasks": [],
    "priority": "Medium",
    "estimate": "4h",
    "due_days": 3,
    "blocked_by": None,
    "labels": ["AGENT-AI"]
}


# ============================================
# FUNÇÕES DE REGISTRY
# ============================================

def load_registry() -> dict[str, Any]:
    """Carrega o registry de projetos."""
    registry_path = REGISTRY_DIR / "projects.json"
    
    if registry_path.exists():
        with open(registry_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    return {"version": "1.0", "projetos": {}, "projetos_planejados": []}


def save_registry(registry: dict[str, Any]) -> None:
    """Salva o registry de projetos."""
    registry_path = REGISTRY_DIR / "projects.json"
    
    with open(registry_path, 'w', encoding='utf-8') as f:
        json.dump(registry, f, indent=2, ensure_ascii=False)


def list_projetos() -> None:
    """Lista todos os projetos."""
    registry = load_registry()
    
    print("\n" + "=" * 60)
    print("📋 projetos DO ecossistema RAG")
    print("=" * 60)
    
    # Projetos em desenvolvimento
    print("\n🟢 Projetos em Desenvolvimento:")
    for key, proj in registry.get("projetos", {}).items():
        if proj.get("status") == "em_desenvolvimento":
            print(f"  • {key}: {proj['nome']}")
            print(f"    Técnica: {proj['tecnica']}")
            print(f"    Tasks: {proj['tasks']['concluidas']}/{proj['tasks']['total']}")
    
    # Projetos planejados
    print("\n⚪ Projetos Planejados:")
    for proj in registry.get("projetos_planejados", []):
        print(f"  • {proj['id']}: {proj['nome']}")
        print(f"    Técnica: {proj['tecnica']}")
    
    print("\n" + "=" * 60)


def show_status(project_id: str) -> None:
    """Mostra status de um projeto."""
    registry = load_registry()
    projetos = registry.get("projetos", {})
    
    if project_id in projetos:
        proj = projetos[project_id]
        print(f"\n📊 Status: {project_id}")
        print(f"  Nome: {proj['nome']}")
        print(f"  Técnica: {proj['tecnica']}")
        print(f"  Status: {proj['status']}")
        print(f"  Épico Jira: {proj.get('jira_epico', 'N/A')}")
        
        tasks = proj.get("tasks", {})
        print(f"\n  Tasks:")
        print(f"    Total: {tasks.get('total', 0)}")
        print(f"    Concluídas: {tasks.get('concluidas', 0)}")
        print(f"    Em andamento: {tasks.get('em_andamento', 0)}")
        print(f"    Pendentes: {tasks.get('pendentes', 0)}")
    else:
        print(f"❌ Projeto {project_id} não encontrado")


# ============================================
# CRIAÇÃO DE PROJETO
# ============================================

def criar_estrutura_pastas(project_id: str, project_name: str) -> dict[str, str]:
    """Cria a estrutura de pastas para o novo projeto."""
    
    # Pastas do projeto
    dev_path = DEV_DIR / f"PRJ-{project_id.split('-')[1]}_{project_name.replace(' ', '_')}"
    
    # Guardrail: Documentação deve sempre ficar dentro de projetos
    docs_root = GOVERNANCE_DIR / "projects"
    docs_root.mkdir(exist_ok=True)
    docs_path = docs_root / f"PRJ-{project_id.split('-')[1]}_{project_name.replace(' ', '_')}"
    
    print(f"\n📁 Criando estrutura de pastas...")
    
    # Criar pastas
    dev_path.mkdir(parents=True, exist_ok=True)
    docs_path.mkdir(parents=True, exist_ok=True)
    
    # Criar subpastas do projeto DEV
    (dev_path / "src").mkdir(exist_ok=True)
    (dev_path / "src" / "api").mkdir(exist_ok=True)
    (dev_path / "src" / "core").mkdir(exist_ok=True)
    (dev_path / "frontend").mkdir(exist_ok=True)
    (dev_path / "scripts").mkdir(exist_ok=True)
    (dev_path / "data" / "uploads").mkdir(parents=True, exist_ok=True)
    (dev_path / "data" / "vector_db").mkdir(parents=True, exist_ok=True)
    
    # Arquivos iniciais
    (dev_path / "README.md").write_text(f"# {project_name}\n\nProjeto em desenvolvimento.\n", encoding='utf-8')
    (dev_path / ".env").write_text("# Variáveis de ambiente\n", encoding='utf-8')
    (dev_path / ".env.template").write_text("# Template de variáveis\n", encoding='utf-8')
    (dev_path / "requirements.txt").write_text("# Dependencies\n", encoding='utf-8')
    (dev_path / ".gitignore").write_text("__pycache__/\nvenv/\n.env\ndata/\n", encoding='utf-8')
    
    # Arquivo inicial do src
    (dev_path / "src" / "__init__.py").write_text("", encoding='utf-8')
    (dev_path / "src" / "api" / "__init__.py").write_text("", encoding='utf-8')
    (dev_path / "src" / "core" / "__init__.py").write_text("", encoding='utf-8')
    
    return {
        "dev": str(dev_path),
        "docs": str(docs_path)
    }


def criar_documentos(project_id: str, project_name: str, tecnica: str, descricao: str, pasta_docs: str) -> None:
    """Cria documentos padrão do projeto."""
    
    print(f"📝 Criando documentos...")
    
    # ideia.md
    ideia_content = f"""# 💡 Ideia Central do Projeto ({project_id})

## 🎯 Objetivo Principal
{descricao}

## 🧑‍💻 Público-Alvo / Casos de Uso
- **Público:** O próprio autor (para compor o portfólio), além de outros desenvolvedores e recrutadores.
- **Caso de uso primário:** Estudar, validar e demonstrar a técnica de {tecnica}.

## ✨ Principais Diferenciais
- **Técnica:** {tecnica}
- **Arquitetura:** A definir durante o planejamento
- **Tecnologias:** A definir durante o planejamento

## 🔮 Visão de Futuro (Ideias para os próximos passos)
- [ ] Definir arquitetura específica
- [ ] Escolher bibliotecas e frameworks
- [ ] Definir fontes de dados
- [ ] Planejar integração com outros projetos

## 🧠 Referências e Inspirações
- [Documentação Ollama](https://ollama.com/)
- [Documentação LangChain](https://python.langchain.com/)
- Artigos técnicos do portfólio
"""
    
    pasta_docs_path = Path(pasta_docs)
    (pasta_docs_path / "ideia.md").write_text(ideia_content, encoding='utf-8')
    
    # implementation_plan.md
    implementation_content = f"""# Plano de Implementação - {project_id}

> Este documento será preenchido durante a fase de planejamento.

## 1. Escopo do Projeto
- **Objetivo:** {descricao}
- **Técnica:** {tecnica}

## 2. Arquitetura Proposta
_A definir_

## 3. Estrutura de Pastas
```
PRJ-{project_id.split('-')[1]}/
├── src/
│   ├── main.py
│   ├── api/
│   └── core/
├── frontend/
├── scripts/
└── data/
```

## 4. Tasks do Jira
_A definir baseado no escopo_

## 5. Cronograma
_A definir_

## 6. Riscos e Mitigações
_A definir_

## 7. Critérios de Sucesso
_A definir_
"""
    
    (pasta_docs_path / f"PRJ-{project_id.split('-')[1]}_implementation_plan.md").write_text(
        implementation_content, encoding='utf-8'
    )
    
    print(f"  ✅ Documents created in {pasta_docs}")


def adicionar_ao_registry(
    project_id: str,
    nome: str,
    tecnica: str,
    descricao: str,
    pastas: dict[str, str]
) -> None:
    """Adiciona o projeto ao registry."""
    
    registry = load_registry()
    
    project_entry = {
        "nome": nome,
        "tecnica": tecnica,
        "descricao": descricao,
        "status": "em_desenvolvimento",
        "jira_epico": None,
        "data_inicio": datetime.now().strftime("%Y-%m-%d"),
        "caminho_dev": pastas["dev"],
        "caminho_docs": pastas["docs"],
        "tasks": {
            "total": 0,
            "concluidas": 0,
            "em_andamento": 0,
            "pendentes": 0
        }
    }
    
    registry["projetos"][project_id] = project_entry
    
    # Remove dos planejados se existir
    registry["projetos_planejados"] = [
        p for p in registry.get("projetos_planejados", [])
        if p["id"] != project_id
    ]
    
    save_registry(registry)
    print(f"\n✅ Projeto {project_id} adicionado ao registry")


def criar_tasks_jira(project_id: str, nome: str, tecnica: str) -> None:
    """Cria as tasks iniciais no Jira (se configurado)."""
    print(f"\n🎫 Para criar tasks no Jira, edite infra/config/projetos.yaml e execute:")
    print(f"   python infra/core/jira_sync.py")


# ============================================
# MODO INTERATIVO
# ============================================

def modo_interativo() -> None:
    """Modo interativo para criar novo projeto."""
    print("\n" + "=" * 60)
    print("🚀 INICIALIZAÇÃO DE NOVO PROJETO - ecossistema RAG")
    print("=" * 60)
    
    # Listar projetos planejados
    registry = load_registry()
    planejados = registry.get("projetos_planejados", [])
    
    if planejados:
        print("\n📋 Projetos planejados disponíveis:")
        for i, p in enumerate(planejados, 1):
            print(f"  {i}. {p['id']}: {p['nome']}")
    
    print("\n" + "-" * 60)
    
    # Escolha ou criar novo
    choice = input("Escolha um projeto planejado (número) ou digite 'novo': ").strip()
    
    if choice.lower() == "novo":
        project_id = input("ID do projeto (ex: PRJ-10): ").strip().upper()
        nome = input("Nome do projeto: ").strip()
        tecnica = input("Técnica (ex: Advanced RAG): ").strip()
        descricao = input("Descrição breve: ").strip()
    else:
        try:
            idx = int(choice) - 1
            p = planejados[idx]
            project_id = p["id"]
            nome = p["nome"]
            tecnica = p["tecnica"]
            descricao = p["descricao"]
        except (ValueError, IndexError):
            print("❌ Opção inválida")
            return
    
    print(f"\n📌 Criando projeto: {project_id} - {nome}")
    
    # Criar estrutura
    pastas = criar_estrutura_pastas(project_id, nome)
    
    # Criar documentos
    criar_documentos(project_id, nome, tecnica, descricao, pastas["docs"])
    
    # Adicionar ao registry
    adicionar_ao_registry(project_id, nome, tecnica, descricao, pastas)
    
    print("\n" + "=" * 60)
    print(f"✅ Projeto {project_id} criado com sucesso!")
    print("=" * 60)
    print(f"\n📂 Estrutura:")
    print(f"   DEV: {pastas['dev']}")
    print(f"   Docs: {pastas['docs']}")
    print(f"\n📝 Próximos passos:")
    print(f"   1. Edite os documentos em {pastas['docs']}")
    print(f"   2. Configure o ambiente em {pastas['dev']}")
    print(f"   3. Execute: python infra/core/jira_sync.py")


# ============================================
# MAIN
# ============================================

def main() -> None:
    """Função principal."""
    parser = argparse.ArgumentParser(
        description="Start Project - Inicializador de Projetos RAG",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemplos:
  python start_project.py                 # Modo interativo
  python start_project.py --list         # Listar projetos
  python start_project.py --status PRJ-XX  # Ver status
  python start_project.py --new PRJ-10 --nome "Novo Projeto" --tecnica "RAG"
        """
    )
    
    parser.add_argument("--list", action="store_true", help="Lista todos os projetos")
    parser.add_argument("--status", type=str, metavar="PROJECT_ID", help="Mostra status de um projeto")
    parser.add_argument("--new", type=str, metavar="PROJECT_ID", help="Cria novo projeto (use com --nome)")
    parser.add_argument("--snapshot", type=str, metavar="PROJECT_ID", help="Gera snapshot de governança para o projeto")
    parser.add_argument("--nome", type=str, help="Nome do novo projeto")
    parser.add_argument("--tecnica", type=str, help="Técnica do projeto")
    parser.add_argument("--descricao", type=str, help="Descrição do projeto")
    
    args = parser.parse_args()
    
    print("\n🔧 ecossistema RAG - START PROJECT")
    
    if args.list:
        list_projetos()
    elif args.status:
        show_status(args.status.upper())
    elif args.snapshot:
        os.system(f"python3 {SCRIPT_DIR}/core/governance_snapshot.py {args.snapshot.upper()}")
    elif args.new:
        if not args.nome:
            print("❌ Para criar novo projeto, use: --new PRJ-XX --nome 'Nome' --tecnica 'Técnica'")
            return
        
        project_id = args.new.upper()
        nome = args.nome
        tecnica = args.tecnica or "RAG"
        descricao = args.descricao or f"Projeto {project_id}"
        
        pastas = criar_estrutura_pastas(project_id, nome)
        criar_documentos(project_id, nome, tecnica, descricao, pastas["docs"])
        adicionar_ao_registry(project_id, nome, tecnica, descricao, pastas)
        
        print(f"\n✅ Projeto {project_id} criado!")
    else:
        modo_interativo()


if __name__ == "__main__":
    main()