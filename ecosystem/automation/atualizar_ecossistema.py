#!/usr/bin/env python3
"""
atualizar_ecossistema.py
========================
Protocolo de Atualização Contínua do Giulia AI Engineering Ecosystem.

Após qualquer ação relevante (feature entregue, decisão tomada, padrão definido),
este script pergunta interativamente se o usuário deseja:
  1. Registrar uma entrada no Diário de Bordo
  2. Atualizar o Manual com nova entrada no Changelog

Uso standalone:
    python3 ecosystem/automation/atualizar_ecossistema.py

Uso como hook (não-interativo parcial):
    python3 ecosystem/automation/atualizar_ecossistema.py --feature "Descrição da feature" --sessao 023

Uso silencioso (apenas diário, sem prompt do manual):
    python3 ecosystem/automation/atualizar_ecossistema.py --diario-only

Uso por projeto (grava no diário local do projeto, não no central):
    python3 ecosystem/automation/atualizar_ecossistema.py --projeto PRJ-XX_NomeDoProjeto

Referência: governance/standards/manual_do_ecossistema.md — Seção 13
"""

import argparse
import datetime
import os
import re
import sys
from pathlib import Path

# ──────────────────────────────────────────────────────────────
# CONFIGURAÇÃO DE CAMINHOS
# ──────────────────────────────────────────────────────────────

MONOREPO_ROOT = Path(__file__).resolve().parents[2]
PROJECTS_DIR  = MONOREPO_ROOT / "dev" / "Giulia"

DIARIO_CENTRAL_PATH = MONOREPO_ROOT / "governance" / "operational-memory" / "diario_de_bordo.md"
MANUAL_PATH = MONOREPO_ROOT / "governance" / "standards" / "manual_do_ecossistema.md"

PROJECT_DIARIO_TEMPLATE = """# 📓 Diário de Bordo — {nome}

> Registro de sessões de trabalho deste projeto. Decisões que afetam o
> ecossistema como um todo (padrões, arquitetura compartilhada) continuam
> registradas no diário central: `governance/operational-memory/diario_de_bordo.md`.

## 📝 Registro de Sessões

---

"""

# ──────────────────────────────────────────────────────────────
# CORES E FORMATAÇÃO
# ──────────────────────────────────────────────────────────────

RESET  = "\033[0m"
BOLD   = "\033[1m"
GREEN  = "\033[92m"
YELLOW = "\033[93m"
CYAN   = "\033[96m"
RED    = "\033[91m"
DIM    = "\033[2m"


def header(text: str) -> None:
    width = 60
    print(f"\n{BOLD}{CYAN}{'─' * width}{RESET}")
    print(f"{BOLD}{CYAN}  {text}{RESET}")
    print(f"{BOLD}{CYAN}{'─' * width}{RESET}\n")


def success(text: str) -> None:
    print(f"{GREEN}✅  {text}{RESET}")


def info(text: str) -> None:
    print(f"{CYAN}ℹ️   {text}{RESET}")


def warn(text: str) -> None:
    print(f"{YELLOW}⚠️   {text}{RESET}")


def ask(question: str) -> str:
    return input(f"{BOLD}{YELLOW}❓  {question}: {RESET}").strip()


def confirm(question: str) -> bool:
    ans = input(f"{BOLD}{YELLOW}❓  {question} (s/n): {RESET}").strip().lower()
    return ans in ("s", "sim", "y", "yes")


# ──────────────────────────────────────────────────────────────
# RESOLUÇÃO DO DIÁRIO (CENTRAL vs. POR PROJETO)
# ──────────────────────────────────────────────────────────────

def list_project_dirs() -> list[Path]:
    if not PROJECTS_DIR.exists():
        return []
    return sorted(p for p in PROJECTS_DIR.iterdir() if p.is_dir())


def resolve_diario_path(projeto: str | None) -> Path:
    """Decide se grava no Diário central ou no Diário local de um projeto.

    Sem --projeto: mantém o comportamento histórico (diário central).
    Com --projeto: busca em dev/Giulia/ por nome exato ou, na falta dele,
    por correspondência parcial (case-insensitive) — evita obrigar o
    usuário a digitar o nome completo da pasta (ex: "PRJ-XX_NomeDoProjeto-dev").
    """
    if not projeto:
        return DIARIO_CENTRAL_PATH

    candidatos = list_project_dirs()
    alvo = projeto.strip().lower()

    exatos = [p for p in candidatos if p.name.lower() == alvo]
    if len(exatos) == 1:
        projeto_dir = exatos[0]
    else:
        parciais = [p for p in candidatos if alvo in p.name.lower()]
        if len(parciais) == 1:
            projeto_dir = parciais[0]
        elif len(parciais) == 0:
            disponiveis = "\n".join(f"  - {p.name}" for p in candidatos)
            warn(f"Nenhum projeto encontrado para \"{projeto}\" em {PROJECTS_DIR.relative_to(MONOREPO_ROOT)}/")
            print(f"Projetos disponíveis:\n{disponiveis}")
            sys.exit(1)
        else:
            nomes = "\n".join(f"  - {p.name}" for p in parciais)
            warn(f"\"{projeto}\" é ambíguo, corresponde a múltiplos projetos:")
            print(nomes)
            sys.exit(1)

    diario = projeto_dir / "diario_de_bordo.md"
    if not diario.exists():
        diario.write_text(
            PROJECT_DIARIO_TEMPLATE.format(nome=projeto_dir.name), encoding="utf-8"
        )
        info(f"Diário local criado para o projeto: {diario.relative_to(MONOREPO_ROOT)}")
    return diario


# ──────────────────────────────────────────────────────────────
# LÓGICA DO DIÁRIO DE BORDO
# ──────────────────────────────────────────────────────────────

def get_next_session_number(diario_path: Path) -> int:
    """Lê o Diário e retorna o próximo número de sessão disponível."""
    if not diario_path.exists():
        return 1

    content = diario_path.read_text(encoding="utf-8")
    matches = re.findall(r"###\s+Sessão\s+#(\d+)", content)
    if not matches:
        return 1

    numbers = [int(n) for n in matches]
    return max(numbers) + 1


def build_session_block(
    numero: int,
    data: str,
    agente: str,
    foco: str,
    features: list[str],
    decisoes: list[str],
    proximos: list[str],
) -> str:
    """Monta o bloco Markdown de uma sessão do Diário."""

    def fmt_list(items: list[str], prefix: str = "-") -> str:
        return "\n".join(f"{prefix} {item}" for item in items if item)

    block = f"""### Sessão #{numero:03d} — {data}
**Agente:** {agente}
**Foco:** {foco}

**Features entregues:**
{fmt_list(features)}
"""

    if decisoes:
        block += f"""
**Decisões arquiteturais:**
{fmt_list(decisoes)}
"""

    if proximos:
        block += f"""
**Próximos passos:**
{fmt_list(proximos)}
"""

    block += "\n---\n"
    return block


def insert_session_into_diary(block: str, diario_path: Path) -> None:
    """Insere nova sessão logo após o separador '## 📝 Registro de Sessões'."""
    content = diario_path.read_text(encoding="utf-8")

    # Âncora: insere após a linha "---" que segue "## 📝 Registro de Sessões"
    anchor = "## 📝 Registro de Sessões\n\n---\n\n"
    if anchor not in content:
        anchor = "## 📝 Registro de Sessões\n\n"

    if anchor in content:
        new_content = content.replace(anchor, anchor + block + "\n", 1)
    else:
        # Diários legados sem cabeçalho (ex: pré-existentes por projeto):
        # insere no topo do arquivo.
        new_content = block + "\n" + content

    diario_path.write_text(new_content, encoding="utf-8")


def update_portfolio_status_in_diary(projetos: dict) -> None:
    """Atualiza a tabela de status do portfólio no Diário (opcional)."""
    # Implementação futura — atualização automática da tabela de status
    pass


def run_diary_flow(
    agente: str,
    diario_path: Path,
    pre_features: list[str] | None = None,
    pre_sessao: int | None = None,
) -> int | None:
    """Fluxo interativo de atualização do Diário de Bordo."""
    header("📓 Diário de Bordo — Nova Sessão")

    numero = pre_sessao or get_next_session_number(diario_path)
    data   = datetime.date.today().strftime("%Y-%m-%d")

    info(f"Próxima sessão: #{numero:03d} — {data}")
    info(f"Arquivo: {diario_path.relative_to(MONOREPO_ROOT)}")
    print()

    foco = ask("Qual foi o FOCO da sessão? (ex: Implementação do PRJ-10, Governança, ...)")
    if not foco:
        warn("Foco é obrigatório. Operação cancelada.")
        return None

    # Features
    print(f"\n{BOLD}Liste as FEATURES entregues (uma por linha, linha vazia para encerrar):{RESET}")
    features = list(pre_features) if pre_features else []
    while True:
        item = input(f"  {DIM}▸{RESET} ").strip()
        if not item:
            break
        features.append(item)

    if not features:
        warn("Nenhuma feature informada. Pulando registro do Diário.")
        return None

    # Decisões
    print(f"\n{BOLD}Houve DECISÕES ARQUITETURAIS? (opcional — linha vazia para pular):{RESET}")
    decisoes: list[str] = []
    while True:
        item = input(f"  {DIM}▸{RESET} ").strip()
        if not item:
            break
        decisoes.append(item)

    # Próximos passos
    print(f"\n{BOLD}Quais os PRÓXIMOS PASSOS? (opcional):{RESET}")
    proximos: list[str] = []
    while True:
        item = input(f"  {DIM}▸{RESET} ").strip()
        if not item:
            break
        proximos.append(item)

    # Confirma e grava
    print(f"\n{BOLD}Resumo da sessão #{numero:03d}:{RESET}")
    print(f"  {DIM}Data:{RESET}    {data}")
    print(f"  {DIM}Foco:{RESET}    {foco}")
    print(f"  {DIM}Features:{RESET} {len(features)} entregues")

    if not confirm("Confirmar e gravar no Diário de Bordo?"):
        warn("Operação cancelada pelo usuário.")
        return None

    block = build_session_block(numero, data, agente, foco, features, decisoes, proximos)
    insert_session_into_diary(block, diario_path)
    success(f"Sessão #{numero:03d} registrada em {diario_path.relative_to(MONOREPO_ROOT)}")

    return numero


# ──────────────────────────────────────────────────────────────
# LÓGICA DO MANUAL (CHANGELOG)
# ──────────────────────────────────────────────────────────────

def get_latest_manual_version() -> str:
    """Lê o Manual e retorna a última versão do Changelog."""
    if not MANUAL_PATH.exists():
        return "8.0"

    content = MANUAL_PATH.read_text(encoding="utf-8")
    matches = re.findall(r"###\s+v(\d+\.\d+)\s+—", content)
    if not matches:
        return "8.0"

    # Retorna a maior versão encontrada
    versions = [tuple(int(x) for x in v.split(".")) for v in matches]
    latest = max(versions)
    return f"{latest[0]}.{latest[1]}"


def suggest_next_version(current: str) -> str:
    """Sugere próxima versão minor ou major."""
    major, minor = map(int, current.split("."))
    return f"{major}.{minor + 1}"


def build_changelog_entry(version: str, data: str, titulo: str, decisoes: list[str]) -> str:
    """Monta o bloco Markdown de uma entrada do Changelog do Manual."""
    decisoes_md = "\n".join(f"- **Decisão:** {d}" for d in decisoes if d)
    return f"""
### v{version} — {data} — {titulo}

{decisoes_md}

---
"""


def insert_changelog_into_manual(entry: str) -> None:
    """Insere nova entrada do Changelog antes da Seção 12 (Padrão RLM)."""
    content = MANUAL_PATH.read_text(encoding="utf-8")

    # Insere antes da Seção 12
    anchor = "\n## 12. Padrão RLM"
    if anchor not in content:
        anchor = "\n## 13. Protocolo"

    new_content = content.replace(anchor, entry + anchor, 1)
    MANUAL_PATH.write_text(new_content, encoding="utf-8")


def update_manual_header_version(version: str, data: str) -> None:
    """Atualiza versão e data no cabeçalho do Manual."""
    content = MANUAL_PATH.read_text(encoding="utf-8")

    content = re.sub(
        r"(?m)^> \*\*Versão:\*\*.*$",
        f"> **Versão:** {version} — Atualização Contínua",
        content,
    )
    content = re.sub(
        r"(?m)^> \*\*Última Atualização:\*\*.*$",
        f"> **Última Atualização:** {data}",
        content,
    )
    MANUAL_PATH.write_text(content, encoding="utf-8")


def run_manual_flow() -> str | None:
    """Fluxo interativo de atualização do Manual (Changelog)."""
    header("📘 Manual do Ecossistema — Nova Entrada no Changelog")

    latest  = get_latest_manual_version()
    suggest = suggest_next_version(latest)
    data    = datetime.date.today().strftime("%Y-%m-%d")

    info(f"Versão atual no Manual: v{latest}")
    info(f"Sugestão para próxima versão: v{suggest}")
    info(f"Arquivo: {MANUAL_PATH.relative_to(MONOREPO_ROOT)}")
    print()

    version_input = ask(f"Versão da nova entrada? [{suggest}]")
    version = version_input or suggest

    titulo = ask("Título da entrada? (ex: Centralização de Specs, Novo Padrão TDD, ...)")
    if not titulo:
        warn("Título é obrigatório. Operação cancelada.")
        return None

    print(f"\n{BOLD}Liste as DECISÕES tomadas (uma por linha, linha vazia para encerrar):{RESET}")
    decisoes: list[str] = []
    while True:
        item = input(f"  {DIM}▸{RESET} ").strip()
        if not item:
            break
        decisoes.append(item)

    if not decisoes:
        warn("Nenhuma decisão informada. Pulando atualização do Manual.")
        return None

    print(f"\n{BOLD}Resumo da entrada:{RESET}")
    print(f"  {DIM}Versão:{RESET}  v{version}")
    print(f"  {DIM}Título:{RESET}  {titulo}")
    print(f"  {DIM}Decisões:{RESET} {len(decisoes)} registradas")

    if not confirm("Confirmar e gravar no Manual do Ecossistema?"):
        warn("Operação cancelada pelo usuário.")
        return None

    entry = build_changelog_entry(version, data, titulo, decisoes)
    insert_changelog_into_manual(entry)
    update_manual_header_version(version, data)

    success(f"Changelog v{version} adicionado em {MANUAL_PATH.relative_to(MONOREPO_ROOT)}")
    return version


# ──────────────────────────────────────────────────────────────
# SUGESTÃO DE COMMIT
# ──────────────────────────────────────────────────────────────

def suggest_commit(
    diary_session: int | None,
    manual_version: str | None,
    diario_path: Path | None = None,
) -> None:
    """Exibe sugestão de commit semântico."""
    parts = []
    add_paths = []
    if diary_session:
        parts.append(f"sessao-{diary_session:03d}")
        if diario_path:
            add_paths.append(str(diario_path.relative_to(MONOREPO_ROOT)))
    if manual_version:
        parts.append(f"manual-v{manual_version}")
        add_paths.append(str(MANUAL_PATH.relative_to(MONOREPO_ROOT)))

    if not parts:
        return

    scope = "+".join(parts)
    add_cmd = " ".join(add_paths) if add_paths else "governance/"
    header("🚀 Commit Sugerido")
    print(f"  {CYAN}docs(governance): atualiza {scope} do ecossistema{RESET}\n")
    print(f"  {DIM}git add {add_cmd} && git commit -m \"docs(governance): atualiza {scope}\"{RESET}\n")


# ──────────────────────────────────────────────────────────────
# PONTO DE ENTRADA
# ──────────────────────────────────────────────────────────────

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Protocolo de Atualização Contínua do Giulia AI Ecosystem",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemplos:
  # Modo interativo completo
  python3 ecosystem/automation/atualizar_ecossistema.py

  # Feature pré-preenchida (ainda pergunta o restante)
  python3 ecosystem/automation/atualizar_ecossistema.py --feature "Implementado PRJ-10" --sessao 023

  # Apenas atualiza o Diário (não pergunta sobre o Manual)
  python3 ecosystem/automation/atualizar_ecossistema.py --diario-only

  # Apenas atualiza o Manual (não pergunta sobre o Diário)
  python3 ecosystem/automation/atualizar_ecossistema.py --manual-only

  # Grava no diário local do projeto (dev/Giulia/<projeto>/diario_de_bordo.md)
  # em vez do diário central do ecossistema
  python3 ecosystem/automation/atualizar_ecossistema.py --projeto PRJ-XX_NomeDoProjeto
        """,
    )
    parser.add_argument("--feature",      type=str,  help="Feature pré-preenchida para o Diário")
    parser.add_argument("--sessao",       type=int,  help="Número da sessão (padrão: auto-detectado)")
    parser.add_argument("--agente",       type=str,  default="Antigravity (IA)", help="Nome do agente")
    parser.add_argument("--diario-only",  action="store_true", help="Atualiza apenas o Diário de Bordo")
    parser.add_argument("--manual-only",  action="store_true", help="Atualiza apenas o Manual")
    parser.add_argument(
        "--projeto", type=str, default=None,
        help="Nome (completo ou parcial) da pasta em dev/Giulia/ — grava no diário "
             "local do projeto em vez do diário central. Cria o arquivo se não existir.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    diario_path = resolve_diario_path(args.projeto)

    # Validações
    if not args.projeto and not diario_path.exists():
        warn(f"Diário de Bordo não encontrado em: {diario_path}")
        sys.exit(1)
    if not MANUAL_PATH.exists():
        warn(f"Manual não encontrado em: {MANUAL_PATH}")
        sys.exit(1)

    print(f"\n{BOLD}🛸 Giulia AI — Protocolo de Atualização do Ecossistema{RESET}")
    print(f"{DIM}  Monorepo: {MONOREPO_ROOT}{RESET}")

    diary_session:   int | None = None
    manual_version:  str | None = None

    pre_features = [args.feature] if args.feature else None

    # ── Fluxo do Diário ──────────────────────────────────────
    if not args.manual_only:
        print()
        run_diary = True if args.diario_only else confirm(
            "\nDeseja registrar uma entrada no Diário de Bordo?"
        )
        if run_diary:
            diary_session = run_diary_flow(
                agente=args.agente,
                diario_path=diario_path,
                pre_features=pre_features,
                pre_sessao=args.sessao,
            )

    # ── Fluxo do Manual ──────────────────────────────────────
    if not args.diario_only:
        print()
        run_manual = True if args.manual_only else confirm(
            "Alguma mudança de padrão para registrar no Manual (Changelog)?"
        )
        if run_manual:
            manual_version = run_manual_flow()

    # ── Resumo Final ─────────────────────────────────────────
    print()
    header("📋 Resumo da Atualização")

    if diary_session:
        success(f"Diário de Bordo: Sessão #{diary_session:03d} registrada")
    else:
        info("Diário de Bordo: não atualizado nesta execução")

    if manual_version:
        success(f"Manual do Ecossistema: v{manual_version} adicionada ao Changelog")
    else:
        info("Manual do Ecossistema: não atualizado nesta execução")

    if diary_session or manual_version:
        suggest_commit(diary_session, manual_version, diario_path)
    else:
        print(f"\n{DIM}Nenhuma atualização realizada. Execute novamente quando necessário.{RESET}\n")


if __name__ == "__main__":
    main()
