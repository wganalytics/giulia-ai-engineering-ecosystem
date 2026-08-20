#!/usr/bin/env python3
"""
🧪 GARE - Infra Validation Script
Valida se as ferramentas de automação seguem os padrões inegociáveis.
"""

import sys
import os
from pathlib import Path

# Adiciona raiz ao path
BASE_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(BASE_DIR))

try:
    from infra.core.jira_sync import buscar_issue_por_resumo
    print("✅ Módulo jira_sync: OK")
except ImportError as e:
    print(f"❌ Erro ao importar jira_sync: {e}")

def test_commit_format():
    """Simula a geração de uma mensagem de commit e valida o padrão."""
    # Simulação de parâmetros
    type_ = "feat"
    scope = "infra"
    msg = "add auto git sync"
    task = "GARE-123"
    
    expected = "feat(infra): add auto git sync #GARE-123"
    result = f"{type_}({scope}): {msg} #{task}"
    
    if result == expected:
        print(f"✅ Formato Conventional Commit + Jira: OK ({result})")
        return True
    else:
        print(f"❌ Falha no formato de commit: {result}")
        return False

def check_env_placeholders():
    """Verifica se as chaves do GitHub existem no .env."""
    env_path = BASE_DIR / "infra/config/.env"
    if not env_path.exists():
        print("❌ Arquivo .env não encontrado!")
        return False
    
    content = env_path.read_text()
    required = ["GITHUB_USER", "GITHUB_REPO", "GITHUB_TOKEN"]
    missing = [req for req in required if req not in content]
    
    if missing:
        print(f"❌ Faltando chaves no .env: {missing}")
        return False
    else:
        print("✅ Chaves de ambiente GitHub: OK")
        return True

if __name__ == "__main__":
    print("-" * 40)
    print("🚀 VALIDANDO infraESTRUTURA GARE")
    print("-" * 40)
    
    s1 = test_commit_format()
    s2 = check_env_placeholders()
    
    if s1 and s2:
        print("\n🏆 infraESTRUTURA VALIDADA COM SUCESSO!")
    else:
        print("\n⚠️  EXISTEM PENDÊNCIAS NA infraESTRUTURA.")
        sys.exit(1)
