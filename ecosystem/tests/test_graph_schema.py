from pathlib import Path

# Raiz do monorepo
MONOREPO_ROOT = Path(__file__).resolve().parents[2]
SCHEMA_FILE = MONOREPO_ROOT / "shared" / "schemas" / "graph_schema.cypher"

def test_graph_schema_file_exists():
    """Garante que o arquivo de DDL do grafo unificado existe na pasta shared/schemas/"""
    assert SCHEMA_FILE.exists(), "Arquivo graph_schema.cypher não encontrado!"

def test_graph_schema_contains_constraints():
    """Garante que as constraints críticas de unicidade do Neo4j estão definidas no schema"""
    with open(SCHEMA_FILE, "r", encoding="utf-8") as f:
        content = f.read()
        
    assert "CONSTRAINT" in content, "Nenhuma restrição (CONSTRAINT) definida no schema!"
    assert "Project" in content, "Entidade 'Project' não referenciada nas constraints!"
    assert "File" in content, "Entidade 'File' não referenciada nas constraints!"
    assert "IS UNIQUE" in content, "Regras de unicidade ausentes no schema!"

def test_graph_schema_contains_indexes():
    """Garante que os índices de performance estão declarados no schema"""
    with open(SCHEMA_FILE, "r", encoding="utf-8") as f:
        content = f.read()
        
    assert "INDEX" in content, "Nenhum índice (INDEX) definido no schema para otimização de buscas!"
    assert "Class" in content, "Classe 'Class' não indexada no DDL!"
