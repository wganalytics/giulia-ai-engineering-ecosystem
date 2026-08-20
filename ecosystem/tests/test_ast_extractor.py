import ast
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch
import pytest

from ecosystem.mcp.ast_extractor import ASTExtractor

def test_ast_extractor_parses_imports():
    """Garante que o extrator detecta IMPORTS locais e de pacotes de forma correta"""
    code = """
import os
from pathlib import Path
from shared.utils import helper_func
"""
    extractor = ASTExtractor(root_path=".")
    imports = extractor.extract_imports_from_code(code)
    
    assert "os" in imports
    assert "pathlib" in imports
    assert "shared.utils" in imports

def test_ast_extractor_parses_inherits():
    """Garante que o extrator detecta heranças de classes (INHERITS)"""
    code = """
class MyClass(BaseClass):
    pass
class AnotherClass(module.ParentClass, Mixin):
    pass
"""
    extractor = ASTExtractor(root_path=".")
    inherits = extractor.extract_inherits_from_code(code)
    
    assert inherits["MyClass"] == ["BaseClass"]
    assert "module.ParentClass" in inherits["AnotherClass"]
    assert "Mixin" in inherits["AnotherClass"]

def test_ast_extractor_parses_instantiates():
    """Garante que o extrator detecta instanciações de classes (INSTANTIATES)"""
    code = """
obj = GraphRetriever()
another = module.HelperClass(arg=1)
"""
    extractor = ASTExtractor(root_path=".")
    instantiates = extractor.extract_instantiates_from_code(code)
    
    assert "GraphRetriever" in instantiates
    assert "module.HelperClass" in instantiates

@patch("ecosystem.mcp.ast_extractor.GraphDatabase")
def test_neo4j_ingestion_executes_queries(mock_db):
    """Garante que o extrator conecta e envia queries de MERGE corretos para o Neo4j"""
    mock_session = MagicMock()
    mock_driver = MagicMock()
    mock_driver.session.return_value = mock_session
    mock_db.driver.return_value = mock_driver
    
    extractor = ASTExtractor(root_path=".", neo4j_uri="bolt://localhost:7687", neo4j_auth=("user", "pass"))
    
    # Executa ingestão simulada
    extractor.ingest_file_node("dev/test_file.py", "PRJ-99")
    
    # Verifica se a query de MERGE foi chamada
    assert mock_session.run.called
    args, kwargs = mock_session.run.call_args
    query = args[0]
    assert "MERGE (f:File" in query
    assert "project: $project" in query
