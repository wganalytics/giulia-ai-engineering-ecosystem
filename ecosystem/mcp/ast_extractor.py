import ast
import os
from pathlib import Path

try:
    from neo4j import GraphDatabase
except ImportError:
    # Fallback to mock/dummy if neo4j is not installed in the current environment
    GraphDatabase = None

class ASTExtractor:
    """
    Extrator AST para analisar código Python e persistir dependências estruturais no Neo4j.
    """
    def __init__(self, root_path: str = ".", neo4j_uri: str = None, neo4j_auth: tuple = None):
        self.root_path = Path(root_path)
        self.uri = neo4j_uri or os.getenv("NEO4J_URI", "bolt://localhost:7687")
        username = os.getenv("NEO4J_USERNAME", "neo4j")
        password = os.getenv("NEO4J_PASSWORD")
        self.auth = neo4j_auth or (username, password)

        self.driver = None
        if GraphDatabase and self.auth[1]:
            try:
                self.driver = GraphDatabase.driver(self.uri, auth=self.auth)
            except Exception as e:
                print(f"Erro ao inicializar driver Neo4j: {e}")
        elif GraphDatabase and not self.auth[1]:
            print("⚠️ NEO4J_PASSWORD não definido — driver Neo4j não inicializado.")

    def extract_imports_from_code(self, code: str) -> list[str]:
        """Extrai todos os imports do código Python."""
        imports = []
        try:
            tree = ast.parse(code)
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        imports.append(alias.name)
                elif isinstance(node, ast.ImportFrom):
                    if node.module:
                        imports.append(node.module)
        except Exception as e:
            print(f"Erro ao parsear imports: {e}")
        return list(set(imports))

    def extract_inherits_from_code(self, code: str) -> dict[str, list[str]]:
        """Extrai relações de herança de classes do código Python."""
        inherits = {}
        try:
            tree = ast.parse(code)
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    bases = []
                    for base in node.bases:
                        if isinstance(base, ast.Name):
                            bases.append(base.id)
                        elif isinstance(base, ast.Attribute):
                            parts = []
                            curr = base
                            while isinstance(curr, ast.Attribute):
                                parts.append(curr.attr)
                                curr = curr.value
                            if isinstance(curr, ast.Name):
                                parts.append(curr.id)
                            parts.reverse()
                            bases.append(".".join(parts))
                    inherits[node.name] = bases
        except Exception as e:
            print(f"Erro ao parsear heranças: {e}")
        return inherits

    def extract_instantiates_from_code(self, code: str) -> list[str]:
        """Extrai instanciacoes de classes baseadas no uso de construtores Capitalizados."""
        instantiates = []
        try:
            tree = ast.parse(code)
            for node in ast.walk(tree):
                if isinstance(node, ast.Call):
                    func = node.func
                    if isinstance(func, ast.Name):
                        if func.id and func.id[0].isupper():
                            instantiates.append(func.id)
                    elif isinstance(func, ast.Attribute):
                        if func.attr and func.attr[0].isupper():
                            parts = [func.attr]
                            curr = func.value
                            while isinstance(curr, ast.Attribute):
                                parts.append(curr.attr)
                                curr = curr.value
                            if isinstance(curr, ast.Name):
                                parts.append(curr.id)
                            parts.reverse()
                            instantiates.append(".".join(parts))
        except Exception as e:
            print(f"Erro ao parsear instanciações: {e}")
        return list(set(instantiates))

    def resolve_import_to_path(self, imp: str) -> str | None:
        """Resolve um caminho de import em formato dot para um caminho de arquivo relativo se ele existir."""
        parts = imp.split(".")
        # Caminhos candidatos
        possible_paths = [
            "/".join(parts) + ".py",
            "/".join(parts) + "/__init__.py"
        ]
        for rel_path in possible_paths:
            full_path = self.root_path / rel_path
            if full_path.exists() and full_path.is_file():
                return rel_path
        return None

    def ingest_file_node(self, filepath: str, project: str):
        """Analisa o arquivo e persiste as informações no banco de grafos Neo4j."""
        full_path = self.root_path / filepath
        
        code = ""
        if full_path.exists():
            try:
                code = full_path.read_text(encoding="utf-8")
            except Exception as e:
                print(f"Erro ao ler arquivo {filepath}: {e}")
            
        imports = self.extract_imports_from_code(code)
        inherits = self.extract_inherits_from_code(code)
        instantiates = self.extract_instantiates_from_code(code)
        
        if not self.driver:
            return
            
        session = self.driver.session()
        try:
            # 1. Cria ou atualiza o nó do Arquivo
            session.run(
                "MERGE (f:File {path: $path, project: $project}) "
                "SET f.language = $language",
                path=filepath, project=project, language="python"
            )
            
            # 2. Cria ou atualiza as Classes e relações de herança
            for class_name, bases in inherits.items():
                session.run(
                    "MERGE (c:Class {name: $name, file_path: $file_path})",
                    name=class_name, file_path=filepath
                )
                session.run(
                    "MATCH (f:File {path: $file_path}), (c:Class {name: $name, file_path: $file_path}) "
                    "MERGE (c)-[:BELONGS_TO]->(f)",
                    file_path=filepath, name=class_name
                )
                for base in bases:
                    session.run(
                        "MERGE (b:Class {name: $name}) ON CREATE SET b.file_path = ''",
                        name=base
                    )
                    session.run(
                        "MATCH (c1:Class {name: $name, file_path: $file_path}), (c2:Class {name: $base}) "
                        "MERGE (c1)-[:INHERITS]->(c2)",
                        name=class_name, file_path=filepath, base=base
                    )
            
            # 3. Cria as relações de Imports
            for imp in imports:
                resolved_path = self.resolve_import_to_path(imp)
                if resolved_path:
                    session.run(
                        "MERGE (f2:File {path: $resolved_path})",
                        resolved_path=resolved_path
                    )
                    session.run(
                        "MATCH (f1:File {path: $path}), (f2:File {path: $resolved_path}) "
                        "MERGE (f1)-[:IMPORTS]->(f2)",
                        path=filepath, resolved_path=resolved_path
                    )
                else:
                    # Dependência externa
                    session.run(
                        "MERGE (f2:File {path: $imp}) "
                        "SET f2.project = 'external'",
                        imp=imp
                    )
                    session.run(
                        "MATCH (f1:File {path: $path}), (f2:File {path: $imp}) "
                        "MERGE (f1)-[:IMPORTS]->(f2)",
                        path=filepath, imp=imp
                    )
            
            # 4. Cria as relações de Instanciação
            for inst in instantiates:
                session.run(
                    "MERGE (c:Class {name: $name})",
                    name=inst
                )
                session.run(
                    "MATCH (f:File {path: $path}), (c:Class {name: $name}) "
                    "MERGE (f)-[:INSTANTIATES]->(c)",
                    path=filepath, name=inst
                )
        finally:
            session.close()
