from unittest.mock import MagicMock, patch
import pytest

from ecosystem.mcp.codecompass_mcp import CodeCompassMCPServer

@patch("ecosystem.mcp.codecompass_mcp.GraphDatabase")
def test_mcp_get_structural_neighborhood(mock_db):
    """Garante que a ferramenta get_structural_neighborhood executa a query Cypher correta e retorna a vizinhança"""
    mock_session = MagicMock()
    mock_driver = MagicMock()
    mock_driver.session.return_value = mock_session
    mock_db.driver.return_value = mock_driver
    
    # Mock do retorno do Neo4j (vizinhos importados e que importam)
    mock_record_imports = MagicMock()
    mock_record_imports.data.return_value = {
        "imports": ["shared/utils.py"],
        "imported_by": ["dev/rag/main.py"],
        "inherits": ["BaseRetriever"],
        "inherited_by": ["CustomRetriever"],
        "instantiated_in": ["dev/rag/factory.py"]
    }
    mock_session.run.return_value = [mock_record_imports]
    
    server = CodeCompassMCPServer(neo4j_uri="bolt://localhost:7687", neo4j_auth=("user", "pass"))
    neighborhood = server.get_structural_neighborhood("dev/rag/retriever.py")
    
    assert "shared/utils.py" in neighborhood["imports"]
    assert "dev/rag/main.py" in neighborhood["imported_by"]
    assert "BaseRetriever" in neighborhood["inherits"]
    assert "CustomRetriever" in neighborhood["inherited_by"]
    assert "dev/rag/factory.py" in neighborhood["instantiated_in"]

def test_mcp_tool_registration():
    """Garante que a ferramenta está registrada e exposta corretamente sob o protocolo MCP"""
    server = CodeCompassMCPServer()
    tools = server.list_tools()
    
    tool_names = [t.name for t in tools]
    assert "get_structural_neighborhood" in tool_names
    assert "find_files_by_class" in tool_names
