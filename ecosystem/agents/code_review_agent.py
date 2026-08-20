import os
import sys
import argparse
import json
from pathlib import Path
from dotenv import load_dotenv

# Carregar variáveis de ambiente diretamente da raiz do ecossistema
env_path = Path(__file__).resolve().parents[2] / ".env"
load_dotenv(dotenv_path=env_path)

# Prompt de Sistema Extraído dos Conceitos do Livro 1
SYSTEM_PROMPT = """Você é um Engenheiro de Software Sênior Especialista em Arquitetura de Agentes Inteligentes.
Nossa metodologia abole o 'vibe coding'. Nós aplicamos 'IA + Processo de Engenharia de Software'.
Sua missão é realizar um Code Review cirúrgico no código fornecido.

Avalie rigorosamente os seguintes critérios:
1. Arquitetura e Clean Code: O código respeita SRP (Single Responsibility)? Há forte acoplamento?
2. Tratamento de Exceções: O código apenas confia na sorte ou trata timeouts, falhas de API e erros de LLM de forma explícita?
3. Tipagem e Docstrings: Há type hints claros (Python 3.10+) e documentação que explique O PORQUÊ da regra de negócio?
4. Observabilidade: O código emite logs estruturados ou 'prints' escondidos?

Forneça seu feedback em Markdown com três seções:
- 🟢 PONTOS FORTES
- 🔴 VULNERABILIDADES ARQUITETURAIS
- 🛠️ PROPOSTA DE REFATORAÇÃO (Mostre trechos de código corrigidos)
"""

def call_llm(prompt: str, content: str) -> str:
    """Faz a chamada para a LLM respeitando a cascata do .env."""
    import requests
    
    # 1. Tentar OpenAI
    if os.environ.get("OPENAI_API_KEY"):
        print("🤖 Usando: OpenAI (gpt-4o-mini)")
        headers = {"Authorization": f"Bearer {os.environ.get('OPENAI_API_KEY')}", "Content-Type": "application/json"}
        res = requests.post(
            "https://api.openai.com/v1/chat/completions",
            headers=headers,
            json={
                "model": "gpt-4o-mini",
                "messages": [
                    {"role": "system", "content": prompt},
                    {"role": "user", "content": f"Realize o Code Review deste código:\n\n```python\n{content}\n```"}
                ]
            },
            timeout=120
        )
        res.raise_for_status()
        return res.json()["choices"][0]["message"]["content"]
        
    # 2. Tentar Gemini
    elif os.environ.get("GEMINI_API_KEY"):
        print("🤖 Usando: Google Gemini (gemini-1.5-flash)")
        key = os.environ.get('GEMINI_API_KEY')
        res = requests.post(
            f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={key}",
            json={
                "systemInstruction": {"parts": [{"text": prompt}]},
                "contents": [{"parts": [{"text": f"Realize o Code Review deste código:\n\n```python\n{content}\n```"}]}]
            },
            timeout=120
        )
        res.raise_for_status()
        return res.json()["candidates"][0]["content"]["parts"][0]["text"]
        
    # 3. Tentar Groq (Excelente para isso)
    elif os.environ.get("GROQ_API_KEY"):
        print("🤖 Usando: Groq (llama3-70b-8192)")
        headers = {"Authorization": f"Bearer {os.environ.get('GROQ_API_KEY')}", "Content-Type": "application/json"}
        res = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers=headers,
            json={
                "model": "llama3-70b-8192",
                "messages": [
                    {"role": "system", "content": prompt},
                    {"role": "user", "content": f"Realize o Code Review deste código:\n\n```python\n{content}\n```"}
                ]
            },
            timeout=120
        )
        res.raise_for_status()
        return res.json()["choices"][0]["message"]["content"]
        
    # 4. Fallback Ollama
    else:
        print("🤖 Usando: Ollama Local (llama3)")
        res = requests.post(
            "http://localhost:11434/api/generate",
            json={
                "model": "llama3",
                "system": prompt,
                "prompt": f"Realize o Code Review deste código:\n\n```python\n{content}\n```",
                "stream": False
            },
            timeout=300
        )
        res.raise_for_status()
        return res.json()["response"]


def main():
    parser = argparse.ArgumentParser(description="🤖 Giulia AI: Agente de Code Review (Fim do Vibe Coding)")
    parser.add_argument("--target", required=True, help="Caminho para o arquivo ou diretório a ser revisado")
    args = parser.parse_args()

    target_path = Path(args.target)
    
    if not target_path.exists():
        print(f"❌ Erro: Caminho '{target_path}' não encontrado.", file=sys.stderr)
        sys.exit(1)

    files_to_review = []
    if target_path.is_file():
        if target_path.suffix == ".py":
            files_to_review.append(target_path)
        else:
            print(f"❌ Erro: O arquivo deve ser um script Python (.py)", file=sys.stderr)
            sys.exit(1)
    elif target_path.is_dir():
        files_to_review = list(target_path.glob("*.py"))
        if not files_to_review:
            print(f"❌ Erro: Nenhum arquivo .py encontrado no diretório.", file=sys.stderr)
            sys.exit(1)

    print(f"\n🔍 Giulia AI Code Review Agent ativado!")
    print(f"📋 Encontrado(s) {len(files_to_review)} arquivo(s) para revisão.\n")

    for py_file in files_to_review:
        print(f"[{'='*50}]")
        print(f"📄 Revisando: {py_file.name}")
        content = py_file.read_text(encoding="utf-8")
        
        if len(content.strip()) == 0:
            print("   ⚠️  Arquivo vazio, pulando...")
            continue
            
        try:
            feedback = call_llm(SYSTEM_PROMPT, content)
            
            # Salvar o review na mesma pasta do arquivo
            review_file = py_file.parent / f"REVIEW_{py_file.stem}.md"
            review_file.write_text(feedback, encoding="utf-8")
            
            print(f"✅ Code Review gerado com sucesso!")
            print(f"💾 Salvo em: {review_file}")
            
        except Exception as e:
            print(f"❌ Erro ao analisar {py_file.name}: {e}", file=sys.stderr)


if __name__ == "__main__":
    main()
