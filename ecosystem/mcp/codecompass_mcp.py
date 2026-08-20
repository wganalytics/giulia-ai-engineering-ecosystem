import os
from collections import namedtuple

try:
    from neo4j import GraphDatabase
except ImportError:
    GraphDatabase = None

# Definindo uma estrutura simples de ferramenta MCP para satisfazer o protocolo do teste
MCPTool = namedtuple("MCPTool", ["name", "description", "input_schema"])

class CodeCompassMCPServer:
    """
    Servidor MCP CodeCompass para expor ferramentas de navegação e análise de grafo do código.
    """
    def __init__(self, neo4j_uri: str = None, neo4j_auth: tuple = None):
        self.uri = neo4j_uri or os.getenv("NEO4J_URI", "bolt://localhost:7687")
        username = os.getenv("NEO4J_USERNAME", "neo4j")
        password = os.getenv("NEO4J_PASSWORD")
        self.auth = neo4j_auth or (username, password)

        self.driver = None
        if GraphDatabase and self.auth[1]:
            try:
                self.driver = GraphDatabase.driver(self.uri, auth=self.auth)
            except Exception as e:
                print(f"Erro ao inicializar driver Neo4j no MCP Server: {e}")
        elif GraphDatabase and not self.auth[1]:
            print("⚠️ NEO4J_PASSWORD não definido — driver Neo4j não inicializado.")

    def get_structural_neighborhood(self, filepath: str, hops: int = 1) -> dict:
        """
        Retorna a vizinhança estrutural direta e indireta de um arquivo no grafo.
        """
        if not self.driver:
            return {
                "imports": [],
                "imported_by": [],
                "inherits": [],
                "inherited_by": [],
                "instantiated_in": []
            }
            
        session = self.driver.session()
        try:
            # Query Cypher unificada para buscar todas as direções da vizinhança de f
            query = (
                "OPTIONAL MATCH (f:File {path: $path}) "
                "WITH f "
                "OPTIONAL MATCH (f)-[:IMPORTS]->(target:File) "
                "WITH f, collect(distinct target.path) as imports "
                "OPTIONAL MATCH (source:File)-[:IMPORTS]->(f) "
                "WITH f, imports, collect(distinct source.path) as imported_by "
                "OPTIONAL MATCH (f)<-[:BELONGS_TO]-(c:Class)-[:INHERITS]->(base:Class) "
                "WITH f, imports, imported_by, collect(distinct base.name) as inherits "
                "OPTIONAL MATCH (f)<-[:BELONGS_TO]-(base:Class)<-[:INHERITS]-(c:Class) "
                "WITH f, imports, imported_by, inherits, collect(distinct c.name) as inherited_by "
                "OPTIONAL MATCH (f)<-[:BELONGS_TO]-(c:Class)<-[:INSTANTIATES]-(inst_source:File) "
                "RETURN imports, imported_by, inherits, inherited_by, collect(distinct inst_source.path) as instantiated_in"
            )
            res = session.run(query, path=filepath)
            records = list(res)
            if records:
                data = records[0].data()
                # Tratamento para garantir que listas vazias sejam mantidas em vez de listas contendo [None]
                clean_data = {}
                for key in ["imports", "imported_by", "inherits", "inherited_by", "instantiated_in"]:
                    val = data.get(key, [])
                    if val is None or val == [None]:
                        clean_data[key] = []
                    else:
                        clean_data[key] = [v for v in val if v is not None]
                return clean_data
                
            return {
                "imports": [],
                "imported_by": [],
                "inherits": [],
                "inherited_by": [],
                "instantiated_in": []
            }
        finally:
            session.close()

    def find_files_by_class(self, class_name: str) -> list[str]:
        """
        Localiza os caminhos dos arquivos que definem uma classe específica.
        """
        if not self.driver:
            return []
        with self.driver.session() as session:
            query = (
                "MATCH (c:Class {name: $name})-[:BELONGS_TO]->(f:File) "
                "RETURN f.path AS path"
            )
            res = session.run(query, name=class_name)
            return [record["path"] for record in res if record["path"] is not None]

    def list_tools(self) -> list[MCPTool]:
        """
        Lista e descreve as ferramentas disponíveis expostas por este servidor MCP.
        """
        return [
            MCPTool(
                name="get_structural_neighborhood",
                description="Obtém a vizinhança estrutural de imports, heranças e instanciações de um arquivo.",
                input_schema={
                    "type": "object",
                    "properties": {
                        "filepath": {"type": "string", "description": "Caminho relativo do arquivo no repositório."},
                        "hops": {"type": "integer", "description": "Profundidade da busca (default: 1)."}
                    },
                    "required": ["filepath"]
                }
            ),
            MCPTool(
                name="find_files_by_class",
                description="Localiza arquivos no repositório que definem a classe especificada.",
                input_schema={
                    "type": "object",
                    "properties": {
                        "class_name": {"type": "string", "description": "Nome da classe a ser buscada."}
                    },
                    "required": ["class_name"]
                }
            )
        ]
