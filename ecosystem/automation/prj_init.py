#!/usr/bin/env python3
# dev/prj_init.py
import os
import json
import re
from datetime import datetime
import yaml
import requests
from requests.auth import HTTPBasicAuth
from dotenv import load_dotenv

def limpar_tela():
    os.system('cls' if os.name == 'nt' else 'clear')

def get_next_prj_number(caminho_silo):
    """Conta os projetos existentes na pasta e retorna o próximo número PRJ-XX"""
    if not os.path.exists(caminho_silo):
        return 1
        
    maior_num = 0
    padrao = re.compile(r"^PRJ-(\d+)_")
    
    for item in os.listdir(caminho_silo):
        if os.path.isdir(os.path.join(caminho_silo, item)):
            match = padrao.match(item)
            if match:
                num = int(match.group(1))
                if num > maior_num:
                    maior_num = num
                    
    return maior_num + 1

def inicializar_projeto():
    limpar_tela()
    print("🛸 GIULIA AI — INICIALIZADOR DE projetos (prj-init)")
    print("-" * 60)

    # FASE 0: Modo — projeto novo do zero ou retrofit de um projeto que já
    # tem código na pasta mas nunca passou pelo wizard (sem specs/, sem
    # projetos.yaml, sem CLAUDE.md local).
    modo = input("0. Modo: (N)ovo projeto ou (R)etrofit de projeto existente? [default: N]: ").strip().upper()
    retrofit = modo == 'R'

    # FASE 1: Gestão e Acesso
    tipo_gestao = input("1. Tipo de Gestão (Jira, Redmine, Github)? [default: Jira]: ").strip()
    if not tipo_gestao:
        tipo_gestao = "Jira"
        
    print(f"\n[Verificando acesso ao {tipo_gestao}...]")
    load_dotenv()
    if tipo_gestao.lower() == "jira":
        dominio = os.getenv("JIRA_DOMAIN")
        token = os.getenv("JIRA_TOKEN")
        if not dominio or not token:
            print("⚠️ AVISO: Credenciais do Jira (JIRA_DOMAIN ou JIRA_TOKEN) não encontradas no .env!")
            print("   Solicite ou configure o acesso antes de usar as automações de lifecycle.")
        else:
            print(f"✅ Credenciais detectadas para: {dominio}")
    else:
        print(f"ℹ️ Validação automática para {tipo_gestao} ainda não implementada. Certifique-se de ter acesso.")

    if retrofit:
        # FASE 2/3 (retrofit): a pasta já existe — apontamos direto pra ela
        # em vez de calcular o próximo número PRJ-XX.
        print("\n" + "-" * 60)
        caminho_projeto = input(
            "2. Caminho do projeto existente (relativo à raiz do ecossistema, "
            "ex: dev/giulia/PRJ-XX_NomeDoProjeto): "
        ).strip().rstrip("/")

        if not os.path.isdir(caminho_projeto):
            print(f"\n❌ ERRO: a pasta '{caminho_projeto}' não foi encontrada.")
            return

        nome_projeto = os.path.basename(caminho_projeto)
        nome_silo = os.path.basename(os.path.dirname(caminho_projeto))
        match = re.match(r"^PRJ-\d+_(.+)$", nome_projeto)
        nome_base = match.group(1) if match else nome_projeto

        tipo_origem = input("3. É um projeto de (C)liente ou (P)ortfólio? [default: C]: ").strip().upper()
        origem = "Portfólio" if tipo_origem == 'P' else "Cliente"

        print(f"📂 Retrofit de projeto existente: {caminho_projeto} (silo={nome_silo})")
    else:
        # FASE 2: Origem e Silo (Cliente)
        print("\n" + "-" * 60)
        tipo_origem = input("2. É um projeto de (C)liente ou (P)ortfólio? [default: C]: ").strip().upper()
        origem = "Portfólio" if tipo_origem == 'P' else "Cliente"

        nome_silo = input(f"3. Qual o nome do {origem} (ex: NomeDoCliente, rag)? ").strip()
        caminho_silo = os.path.join("dev", nome_silo)

        if not os.path.exists(caminho_silo):
            print(f"✨ Criando novo diretório para {origem}: {caminho_silo}")
            os.makedirs(caminho_silo, exist_ok=True)
        else:
            print(f"📂 Diretório existente encontrado: {caminho_silo}")

        # FASE 3: Nome do Projeto (Cálculo Automático)
        next_num = get_next_prj_number(caminho_silo)

        print("\n" + "-" * 60)
        print(f"O próximo projeto para este cliente será o PRJ-{next_num:02d}")
        nome_base = input("4. Digite o nome do projeto (ex: Dashboard_BI): ").strip()

        nome_projeto = f"PRJ-{next_num:02d}_{nome_base}"
        caminho_projeto = os.path.join(caminho_silo, nome_projeto)

        if os.path.exists(caminho_projeto):
            print(f"\n❌ ERRO: O projeto {nome_projeto} já existe!")
            return

        print(f"👉 O projeto será criado como: {nome_projeto}")

    # FASE 4: Chave do Quadro
    epic_key = input(f"\n5. Chave do Épico raiz no quadro do {tipo_gestao} (ex: ACME-1): ").strip().upper()
    project_key = epic_key.split('-')[0] if '-' in epic_key else epic_key

    # GUARDRAIL: nunca assumir que a chave digitada (ou lida de .env) aponta para o
    # board certo — validar contra o Jira real antes de prosseguir. Regra criada após
    # incidente real: um épico foi criado no board errado ao assumir que uma chave de
    # config genérica correspondia a um board específico — cada PRJ-XX tem seu próprio
    # board dedicado, sempre validar contra a API antes de agir.
    if tipo_gestao.lower() == "jira" and epic_key:
        jira_domain = os.getenv("JIRA_DOMAIN")
        jira_email = os.getenv("JIRA_EMAIL")
        jira_token = os.getenv("JIRA_TOKEN")
        if jira_domain and jira_email and jira_token:
            try:
                resp = requests.get(
                    f"https://{jira_domain}/rest/api/3/issue/{epic_key}",
                    auth=HTTPBasicAuth(jira_email, jira_token),
                    headers={"Accept": "application/json"},
                    params={"fields": "summary,project,issuetype"},
                    timeout=10
                )
                if resp.status_code == 200:
                    campos = resp.json().get("fields", {})
                    proj = campos.get("project", {})
                    tipo_issue = campos.get("issuetype", {}).get("name")
                    print(f"\n🔎 Validado no Jira: {epic_key} — \"{campos.get('summary')}\"")
                    print(f"   Projeto: {proj.get('key')} ({proj.get('name')}) | Tipo: {tipo_issue}")
                    if tipo_issue != "Epic":
                        print(f"   ⚠️ AVISO: {epic_key} não é do tipo Epic (é '{tipo_issue}').")
                    confirma = input("   Este é o board/épico correto para este projeto? (S/n): ").strip().upper()
                    if confirma == "N":
                        print("\n❌ Abortado pelo usuário. Rode o wizard novamente com a chave correta.")
                        return
                    project_key = proj.get("key", project_key)
                elif resp.status_code == 404:
                    print(f"\n⚠️ AVISO: {epic_key} não foi encontrado no Jira ({jira_domain}).")
                    confirma = input("   Continuar mesmo assim (ex: épico será criado depois)? (s/N): ").strip().upper()
                    if confirma != "S":
                        print("\n❌ Abortado. Crie o épico/board primeiro ou informe a chave correta.")
                        return
                else:
                    print(f"\n⚠️ Não foi possível validar {epic_key} no Jira (status {resp.status_code}). Prosseguindo sem confirmação — confira manualmente.")
            except Exception as e:
                print(f"\n⚠️ Falha ao validar Jira ({e}). Prosseguindo sem confirmação — confira manualmente.")
        else:
            print("\n⚠️ Credenciais Jira ausentes no .env — não foi possível validar o épico automaticamente. Confira manualmente.")

    # FASE 5: Composição do Time
    print("\n" + "-" * 60)
    print("6. Definição do Time (Governança e Responsabilidades)")
    tipo_time = input("O projeto será no modelo Pair-Programming (Você + Giulia AI) ou teremos mais pessoas? (P = Pair / M = Mais pessoas) [default: P]: ").strip().upper()
    time_projeto = ["Wemerson (Lead Architect / PO)", "Giulia (AI Agent / Dev)"]
    if tipo_time == 'M':
        outros = input("Informe o nome dos demais membros separados por vírgula: ")
        time_projeto.extend([nome.strip() for nome in outros.split(',') if nome.strip()])

    # FASE 6: Estruturação
    print("\n[+] Estruturando ambiente local...")

    # Retrofit: o código do projeto já existe e pode ter seu próprio layout
    # (ex: não usa src/tests/data genéricos) — só adicionamos as pastas de
    # governança (specs/ e .agents/skills), sem tocar no que já está lá.
    if retrofit:
        pastas = [
            os.path.join(caminho_projeto, "specs"),
            os.path.join(caminho_projeto, ".agents", "skills")
        ]
    else:
        pastas = [
            os.path.join(caminho_projeto, "specs"),
            os.path.join(caminho_projeto, "src"),
            os.path.join(caminho_projeto, "tests"),
            os.path.join(caminho_projeto, "data"),
            os.path.join(caminho_projeto, ".agents", "skills")
        ]
    # Guardrail: nenhum artefato de gestão do projeto (specs, projetos.yaml,
    # CLAUDE.md, diário local, handoff_trace.jsonl) pode falhar em silêncio.
    # Cada bloco abaixo tenta escrever e registra a falha aqui; ao final,
    # se algo faltou, o usuário é avisado explicitamente em vez de o wizard
    # reportar sucesso com artefatos faltando.
    falhas_artefatos = []

    for pasta in pastas:
        try:
            os.makedirs(pasta, exist_ok=True)
        except OSError as e:
            falhas_artefatos.append(f"pasta {pasta} ({e})")

    # Specs — em retrofit nunca sobrescreve um arquivo que já exista.
    specs = ["README.md", "PRD.md", "RULES.md", "ARCHITECTURE.md", "API_SPEC.md", "TESTS_SPEC.md", "AGENTS.md"]
    for spec in specs:
        destino = os.path.join(caminho_projeto, "specs", spec)
        if retrofit and os.path.exists(destino):
            print(f"   ↷ specs/{spec} já existe — mantido sem alteração.")
            continue

        conteudo = f"# {spec.replace('.md', '')} - {nome_projeto}\n\nDocumento gerado automaticamente via prj-init."
        if spec == "AGENTS.md":
            conteudo += f"\n\n## Composição do Time\n"
            for membro in time_projeto:
                conteudo += f"- {membro}\n"
            conteudo += "\n**Nota para os Agentes IA:** Respeite a divisão de papéis. Tarefas de infraestrutura e arquitetura cabem aos humanos. Código e automações cabem à IA."

        try:
            with open(destino, "w", encoding="utf-8") as f:
                f.write(conteudo)
        except OSError as e:
            falhas_artefatos.append(f"specs/{spec} ({e})")

    # yaml
    ignorar = {"specs", ".agents", "projetos.yaml", "CLAUDE.md", "handoff_trace.jsonl", ".DS_Store"}
    arquivos_legados = sorted(
        item for item in os.listdir(caminho_projeto) if item not in ignorar
    ) if retrofit else []

    metadados_path = os.path.join(caminho_projeto, "projetos.yaml")
    if retrofit and os.path.exists(metadados_path):
        print(f"   ↷ projetos.yaml já existe — mantido sem alteração.")
    else:
        metadados = {
            "projeto_id": nome_projeto,
            "origem": origem,
            "silo": nome_silo,
            "gerenciador_projetos": tipo_gestao.lower(),
            "team_composition": time_projeto,
            tipo_gestao.lower(): {
                "project_key": project_key,
                "epic_key": epic_key
            },
            "criado_em": datetime.now().isoformat(),
            "arquivos_legados": arquivos_legados,
            "status": "retrofit" if retrofit else "configurado"
        }

        try:
            with open(metadados_path, "w", encoding="utf-8") as f:
                yaml.safe_dump(metadados, f, default_flow_style=False, allow_unicode=True)
        except OSError as e:
            falhas_artefatos.append(f"projetos.yaml ({e})")

    # CLAUDE.md local — vínculo com os dados reais do ecossistema (não um template solto)
    nome_legivel = nome_base.replace('_', ' ')
    time_md = "\n".join(f"   - {membro}" for membro in time_projeto)
    intro_specs = (
        "Projeto retrofitado — já existe código em produção/desenvolvimento nesta pasta; "
        "as specs em `specs/` (README, PRD, RULES, ARCHITECTURE, API_SPEC, TESTS_SPEC, AGENTS) "
        "foram geradas como placeholder por este wizard e precisam ser preenchidas a partir do "
        "código e da documentação já existentes antes de novas mudanças de arquitetura."
        if retrofit else
        "Projeto novo — as specs em `specs/` (README, PRD, RULES, ARCHITECTURE, API_SPEC, TESTS_SPEC, AGENTS) "
        "foram geradas como placeholder por este wizard e precisam ser preenchidas antes de qualquer implementação."
    )
    claude_md = f"""# {nome_legivel} ({nome_projeto.split('_')[0]}) — Diretrizes de Desenvolvimento

Bem-vindo ao projeto {nome_legivel}. {intro_specs}

## 📍 Regras Arquiteturais e de Ecossistema

1. **Stack ainda não definida.** Não presuma framework, linguagem ou banco de dados — decida junto com o usuário e registre em `specs/ARCHITECTURE.md` antes de escrever código.

2. **Governança ({tipo_gestao}):**
   - Origem: {origem} | Silo: {nome_silo}
   - Board dedicado: **`{project_key}`**, épico raiz **`{epic_key}`**.
   - Consulte `projetos.yaml` para os metadados completos do projeto.
   - Sempre respeite as regras de negócio declaradas em `specs/RULES.md` assim que forem escritas.
   - **Nunca assuma qual board/projeto usar a partir de um `.env` compartilhado sem validar contra a API antes de criar ou modificar issues.**

3. **Time do projeto:**
{time_md}

4. **Diário de Bordo Global:**
   O ecossistema controla seu histórico através do repositório raiz em `../../governance/operational-memory/diario_de_bordo.md`. Ao concluir tarefas complexas, avise o usuário que o log global pode ser atualizado via `atualizar_ecossistema.py`.

5. **Aviso de contexto ocupado:**
   Sempre que a janela de contexto desta conversa atingir ~40% de ocupação, avise o usuário em uma linha antes de continuar a resposta. Repita o aviso apenas ao cruzar o próximo patamar relevante (ex: 60%, 80%), não a cada turno.
"""
    claude_md_path = os.path.join(caminho_projeto, "CLAUDE.md")
    if retrofit and os.path.exists(claude_md_path):
        print(f"   ↷ CLAUDE.md já existe — mantido sem alteração.")
    else:
        try:
            with open(claude_md_path, "w", encoding="utf-8") as f:
                f.write(claude_md)
        except OSError as e:
            falhas_artefatos.append(f"CLAUDE.md ({e})")

    # Diário de Bordo local — mesmo template usado por atualizar_ecossistema.py
    # (PROJECT_DIARIO_TEMPLATE), criado aqui no scaffold para que o projeto já
    # nasça com histórico local, sem depender de o usuário pedir depois.
    diario_local_path = os.path.join(caminho_projeto, "diario_de_bordo.md")
    if retrofit and os.path.exists(diario_local_path):
        print(f"   ↷ diario_de_bordo.md já existe — mantido sem alteração.")
    else:
        diario_local = f"""# 📓 Diário de Bordo — {nome_projeto}

> Registro de sessões de trabalho deste projeto. Decisões que afetam o
> ecossistema como um todo (padrões, arquitetura compartilhada) continuam
> registradas no diário central: `governance/operational-memory/diario_de_bordo.md`.

## 📝 Registro de Sessões

---

"""
        try:
            with open(diario_local_path, "w", encoding="utf-8") as f:
                f.write(diario_local)
        except OSError as e:
            falhas_artefatos.append(f"diario_de_bordo.md ({e})")

    # Trace
    trace = {
        "timestamp": datetime.now().isoformat() + "Z",
        "projeto_id": nome_projeto,
        f"{tipo_gestao.lower()}_issue_key": epic_key,
        "skill_utilizada": "prj-init" + ("-retrofit" if retrofit else ""),
        "solucao_decidida": "Retrofit: specs/, .agents/skills, CLAUDE.md e projetos.yaml adicionados a projeto já existente." if retrofit else "Estrutura do projeto inicializada com wizard avançado.",
        "justification": "Criação automatizada seguindo regras RLM.",
        "status": "retrofitted" if retrofit else "initialized",
        "consecutive_failures": 0
    }

    try:
        with open(os.path.join(caminho_projeto, "handoff_trace.jsonl"), "a", encoding="utf-8") as f:
            f.write(json.dumps(trace) + "\n")
    except OSError as e:
        falhas_artefatos.append(f"handoff_trace.jsonl ({e})")

    if falhas_artefatos:
        print(f"\n⚠️ ATENÇÃO: {len(falhas_artefatos)} artefato(s) de gestão NÃO foram criados — o projeto está incompleto:")
        for falha in falhas_artefatos:
            print(f"   ✗ {falha}")
        print("   Resolva o problema acima e rode o wizard novamente em modo retrofit para completar o que faltou.")
    else:
        print(f"\n🚀 Sucesso! Projeto estruturado em: {caminho_projeto}")
        print(f"   Incluindo CLAUDE.md e diario_de_bordo.md locais, vinculados a: silo={nome_silo}, board={project_key}, épico={epic_key}")

if __name__ == "__main__":
    inicializar_projeto()