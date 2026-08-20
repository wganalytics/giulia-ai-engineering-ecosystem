# ecosystem/automation/load_insights_rules.py
import re
from pathlib import Path
import json

INSIGHTS_DIR = Path("shared/source_documents/books/insights")
OUTPUT_MD = Path("ecosystem/automation/insights_system_prompt.md")
OUTPUT_JSON = Path("ecosystem/automation/insights_system_prompt.json")

def compile_insights():
    """
    Varre os arquivos de insights do ecossistema, extrai conceitos relevantes
    e compila uma lista ordenada de diretrizes de engenharia para injetar nos agentes.
    """
    if not INSIGHTS_DIR.exists():
        print(f"⚠️ Diretório de insights não encontrado em: {INSIGHTS_DIR}")
        return ""

    all_rules = []
    
    # Busca por arquivos markdown de insights
    for file_path in INSIGHTS_DIR.glob("INSIGHTS_*.md"):
        try:
            content = file_path.read_text(encoding="utf-8")
            
            # Tenta encontrar seções de conceitos relevantes
            # Captura tudo entre o título do conceito e a próxima seção markdown (### ou ##)
            sections = re.findall(
                r"(?:\*\*Conceitos relevantes para o ecossistema:\*\*|\*\*Conceitos relevantes:\*\*)(.*?)(?=##|###|$)",
                content,
                re.DOTALL
            )
            
            for section in sections:
                # Extrai itens de lista (- ou * ou números)
                items = re.findall(r"^[ \t]*[-*+\d\.]+[ \t]+(.*?)(?=\n^[ \t]*[-*+\d\.]+|\Z)", section, re.MULTILINE | re.DOTALL)
                for item in items:
                    cleaned = re.sub(r"\s+", " ", item.strip())
                    if cleaned and len(cleaned) > 20 and cleaned not in all_rules:
                        all_rules.append(cleaned)
        except Exception as e:
            print(f"⚠️ Erro ao ler insights de {file_path.name}: {e}")

    # Fallback se nenhum insight estruturado for encontrado nos arquivos existentes
    if not all_rules:
        all_rules = [
            "Evitar Vibe Coding: Todo código deve ser precedido por especificações de requisitos formais (specs).",
            "Test-Driven Development (TDD): Nenhum código de produção deve ser modificado sem teste correspondente.",
            "Reversibilidade ACID: Use controle de versão (Git) para criar savepoints reversíveis a cada iteração do agente.",
            "Arquitetura Modular: Componentes de software devem apresentar baixo acoplamento e alta coesão."
        ]

    # Salva em Markdown formatado
    prompt_lines = [
        "# 🛡️ DIRETRIZES DE ENGENHARIA DO ecossistema (INSIGHTS INGERIDOS)",
        "",
        "Você deve atuar estritamente sob as seguintes regras e diretrizes extraídas das bases de conhecimento de engenharia do ecossistema:",
        ""
    ]
    for rule in all_rules:
        prompt_lines.append(f"- **Regra:** {rule}")

    prompt_content = "\n".join(prompt_lines)
    
    # Salva os arquivos de saída
    OUTPUT_MD.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_MD.write_text(prompt_content, encoding="utf-8")
    
    with open(OUTPUT_JSON, "w", encoding="utf-8") as f:
        json.dump({"rules": all_rules, "system_prompt": prompt_content}, f, indent=4, ensure_ascii=False)

    print(f"✅ Compilação de insights concluída: {len(all_rules)} regras geradas.")
    return prompt_content

def load_system_prompt() -> str:
    """
    Retorna as regras de engenharia compiladas como string de prompt de sistema.
    """
    if not OUTPUT_JSON.exists():
        return compile_insights()
    try:
        with open(OUTPUT_JSON, "r", encoding="utf-8") as f:
            data = json.load(f)
            return data.get("system_prompt", "")
    except Exception:
        return compile_insights()

if __name__ == "__main__":
    compile_insights()
