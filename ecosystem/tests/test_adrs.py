import os
from pathlib import Path

# Raiz do monorepo
MONOREPO_ROOT = Path(__file__).resolve().parents[2]
ADR_DIR = MONOREPO_ROOT / "governance" / "architecture-decisions"

def test_adr_directory_exists():
    """Garante que a pasta de decisões de arquitetura existe"""
    assert ADR_DIR.exists() and ADR_DIR.is_dir(), "Diretório de ADRs não encontrado!"

def test_adr_template_exists():
    """Garante que o template padrão de ADR existe"""
    template_path = ADR_DIR / "adr-xxx_template.md"
    assert template_path.exists(), "Template adr-xxx_template.md não encontrado!"
    
    with open(template_path, "r", encoding="utf-8") as f:
        content = f.read()
        
    assert "## 1. Contexto" in content, "Seção 'Contexto' ausente no template!"
    assert "## 2. Decisão" in content, "Seção 'Decisão' ausente no template!"
    assert "## 3. Consequências" in content, "Seção 'Consequências' ausente no template!"

def test_initial_adrs_exist():
    """Garante que as 3 primeiras decisões de arquitetura históricas foram escritas"""
    required_adrs = [
        "adr-001-sufixo-provedor-vectordb.md",
        "adr-002-isolamento-tdd-projetos.md",
        "adr-003-gate-revisao-code-review.md"
    ]
    
    for adr in required_adrs:
        path = ADR_DIR / adr
        assert path.exists(), f"Decisão crítica {adr} não foi documentada na pasta de ADRs!"

def test_adr_index_readme():
    """Garante que o arquivo README.md de índice existe na pasta de ADRs e lista os itens"""
    readme_path = ADR_DIR / "readme.md"
    assert readme_path.exists(), "Índice readme.md ausente na pasta de ADRs!"
    
    with open(readme_path, "r", encoding="utf-8") as f:
        content = f.read()
        
    assert "ADR-001" in content, "ADR-001 não listado no índice!"
    assert "ADR-002" in content, "ADR-002 não listado no índice!"
    assert "ADR-003" in content, "ADR-003 não listado no índice!"
