import os
import json
from pathlib import Path
from dotenv import load_dotenv
import yaml

def find_client_env(start_dir: Path) -> Path | None:
    current_dir = start_dir.resolve()
    while True:
        env_path = current_dir / ".env"
        if env_path.exists():
            if (current_dir / "ecosystem").exists() and (current_dir / "dev").exists():
                return None
            return env_path
        if current_dir.parent == current_dir:
            break
        current_dir = current_dir.parent
        if current_dir.name == "dev":
            break
    return None

env_path = find_client_env(Path.cwd())
if env_path:
    load_dotenv(dotenv_path=env_path, override=True)
else:
    print(f"❌ ERRO CRÍTICO (ISOLAMENTO): Nenhum arquivo .env encontrado para o cliente em {Path.cwd()}")

JIRA_DOMAIN = os.getenv("JIRA_DOMAIN")
JIRA_EMAIL = os.getenv("JIRA_EMAIL")
JIRA_TOKEN = os.getenv("JIRA_TOKEN")

GITHUB_USER = os.getenv("GITHUB_USER")
GITHUB_REPO_URL = os.getenv("GITHUB_REPO_URL")
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")

def load_ecosystem_registry():
    """
    Carrega o arquivo ecosystem_registry.json localizado na raiz do ecossistema.
    """
    # Assume que o script está rodando a partir de alguma pasta dentro do ecossistema,
    # então procuramos o registry subindo as pastas até encontrar.
    current_dir = Path(os.getcwd()).resolve()
    
    # Procura até 5 níveis acima pelo ecosystem_registry.json
    registry_path = None
    search_dir = current_dir
    for _ in range(5):
        potential_path = search_dir / "ecosystem_registry.json"
        if potential_path.exists():
            registry_path = potential_path
            break
        search_dir = search_dir.parent
        
    if not registry_path:
        raise FileNotFoundError("Não foi possível encontrar o ecosystem_registry.json na árvore de diretórios.")
        
    with open(registry_path, "r", encoding="utf-8") as f:
        return json.load(f)

def get_current_jira_project_key():
    """
    Busca o projetos.yaml mais próximo subindo a árvore de diretórios
    e extrai o jira_project_key dele.
    """
    search_dir = Path(os.getcwd()).resolve()
    for _ in range(6):
        yaml_path = search_dir / "projetos.yaml"
        if yaml_path.exists():
            with open(yaml_path, "r", encoding="utf-8") as f:
                config = yaml.safe_load(f)
            # Tenta pegar do novo formato
            jira_config = config.get("jira", {})
            if "project_key" in jira_config:
                return jira_config["project_key"]
            
            # Tenta pegar do formato antigo para legados do RAG
            jira_issue_key = config.get("jira_issue_key", "")
            if jira_issue_key:
                return jira_issue_key.split('-')[0]
                
            break
        search_dir = search_dir.parent
            
    return None

if __name__ == "__main__":
    # Teste de execução local
    print("=== Teste de Contexto do Ecossistema ===")
    
    project_key = get_current_jira_project_key()
    
    if project_key:
        print(f"📍 Projeto Atual Detectado: {project_key}")
        print(f"🔗 Domínio do Jira: {JIRA_DOMAIN}")
        # Apenas para teste visual, evite imprimir o token real em produção
        token_preview = "***" if JIRA_TOKEN else "NÃO DEFINIDO"
        print(f"🔑 Token Encontrado: {token_preview}")
    else:
        print("⚠️ Você não está em um diretório de projeto mapeado.")
