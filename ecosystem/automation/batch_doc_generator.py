import os
import json
import urllib.request
import urllib.error

# Configurações do Ollama Local
OLLAMA_URL = os.environ.get("GIULIA_OLLAMA_URL", "http://localhost:11434/api/generate")
OLLAMA_MODEL = os.environ.get("GIULIA_OLLAMA_MODEL", "llama3")

def generate_with_llm(prompt, system_prompt="Você é um assistente de documentação técnica especializado no ecossistema GARE."):
    """Função utilitária para chamar o Ollama rodando localmente."""
    data = {
        "model": OLLAMA_MODEL,
        "prompt": prompt,
        "system": system_prompt,
        "stream": False
    }
    
    try:
        req = urllib.request.Request(OLLAMA_URL, data=json.dumps(data).encode('utf-8'), headers={'Content-Type': 'application/json'})
        with urllib.request.urlopen(req) as response:
            result = json.loads(response.read().decode('utf-8'))
            return result.get('response', '')
    except urllib.error.URLError as e:
        print(f"  [!] Falha de conexão com o Ollama em {OLLAMA_URL}. Está rodando localmente?")
        # Retorna mock caso não consiga
        return f"<!-- Documentação gerada offline. Ollama não alcançado -->\n# Documento Gerado Automaticamente\nO servidor LLM não estava disponível no momento da geração."

def process_project(project_path, project_name):
    print(f"\n🚀 Processando: {project_name}")
    
    # Arquivos alvo
    readme_path = os.path.join(project_path, "README.md")
    manual_path = os.path.join(project_path, "MANUAL_DO_USUARIO.md")
    svg_path = os.path.join(project_path, "architecture.svg")

    # Lê um pouco do contexto do projeto para mandar pro prompt
    context = ""
    try:
        if os.path.exists(readme_path):
            with open(readme_path, 'r') as f:
                context = f.read()[:1000] # Pega primeiros 1000 caracteres
    except Exception:
        pass
    
    # 1. Gerar architecture.svg se não existir
    if not os.path.exists(svg_path):
        print("  -> Gerando architecture.svg...")
        svg_prompt = f"Gere APENAS o código SVG (sem crases de markdown) de um diagrama de arquitetura para este projeto. Contexto: {project_name}. {context}"
        svg_content = generate_with_llm(svg_prompt, system_prompt="Você é um software architect focado em diagramas vetoriais SVG.")
        # Simples limpeza
        if "```xml" in svg_content: svg_content = svg_content.split("```xml")[1].split("```")[0]
        elif "```svg" in svg_content: svg_content = svg_content.split("```svg")[1].split("```")[0]
        elif "```" in svg_content: svg_content = svg_content.split("```")[1].split("```")[0]
        
        with open(svg_path, 'w') as f:
            f.write(svg_content.strip())
    else:
        print("  -> architecture.svg já existe.")

    # 2. Gerar MANUAL_DO_USUARIO.md se não existir
    if not os.path.exists(manual_path):
        print("  -> Gerando MANUAL_DO_USUARIO.md...")
        manual_prompt = f"Escreva o Manual do Usuário em markdown para o projeto {project_name}. O manual deve focar no uso do sistema pelo usuário final. Use o seguinte contexto: {context}"
        manual_content = generate_with_llm(manual_prompt, system_prompt="Você é um Especialista de Treinamento focado no usuário final.")
        
        with open(manual_path, 'w') as f:
            f.write(manual_content.strip())
    else:
        print("  -> MANUAL_DO_USUARIO.md já existe.")

    # 3. Atualizar README com link para o SVG (se ainda não tiver)
    if os.path.exists(readme_path):
        with open(readme_path, 'r') as f:
            readme_content = f.read()
        
        if "architecture.svg" not in readme_content:
            print("  -> Atualizando README.md com o diagrama SVG...")
            new_content = readme_content.replace(f"# {project_name}", f"# {project_name}\n\n## 🏗️ Arquitetura do Sistema\n![Diagrama]({os.path.basename(svg_path)})\n")
            with open(readme_path, 'w') as f:
                f.write(new_content)
        else:
            print("  -> README.md já possui o diagrama.")

def main():
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    dev_dir = os.path.join(base_dir, "dev")
    
    # Apenas pastas rag e mcp
    domains = ["rag", "mcp"]
    
    for domain in domains:
        domain_path = os.path.join(dev_dir, domain)
        if not os.path.exists(domain_path):
            continue
            
        for project in os.listdir(domain_path):
            project_path = os.path.join(domain_path, project)
            
            if os.path.isdir(project_path) and project.upper().startswith("PRJ-"):
                # Adicione aqui os nomes de pastas de projetos já processados
                # manualmente, para pular na próxima execução em lote.
                ALREADY_PROCESSED = []
                if project in ALREADY_PROCESSED:
                    print(f"Skipping {project} (já processado anteriormente)")
                    continue

                process_project(project_path, project)

if __name__ == "__main__":
    main()
