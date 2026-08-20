import os

def tree(path, prefix='', depth=0):
    if depth > 5: return
    try:
        # Filtros de exclusão
        exclude = ['.git', 'venv', '__pycache__', '.DS_Store', 'node_modules', '.agents', '.gemini', '.pytest_cache', 'neo4j']
        files = [f for f in sorted(os.listdir(path)) if f not in exclude]
    except PermissionError:
        return
    
    for i, file in enumerate(files):
        is_last = (i == len(files) - 1)
        print(f"{prefix}{'└── ' if is_last else '├── '}{file}")
        full_path = os.path.join(path, file)
        if os.path.isdir(full_path):
            tree(full_path, prefix + ('    ' if is_last else '│   '), depth + 1)

if __name__ == "__main__":
    print("# 📂 Estrutura de Arquivos do Ecossistema RAG\n")
    print(f"Atualizado em: {os.popen('date').read().strip()}\n")
    print("```text\n.")
    tree('.')
    print("```")
