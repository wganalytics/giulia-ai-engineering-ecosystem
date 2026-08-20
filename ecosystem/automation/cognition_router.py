#!/usr/bin/env python3
"""
cognition_router.py
===================
Roteador de Cognição para alocação dinâmica de LLMs baseada no SDD.

Lê os metadados YAML embutidos no topo do arquivo de especificação (SDD)
de um projeto ativo em dev/, valida o nível de complexidade técnica e
retorna o identificador do modelo de IA correto para a execução.
Também intercepta e registra overrides manuais do operador humano.

Uso:
    python3 ecosystem/automation/cognition_router.py <projeto_id> <sdd_filename>

Códigos de saída:
    0  → Roteamento concluído com sucesso. Retorna LLM_TARGET na saída padrão.
    2  → Erro de configuração, arquivo não encontrado ou YAML corrompido.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import yaml
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

# ──────────────────────────────────────────────────────────────
# CONFIGURAÇÃO DE CAMINHOS
# ──────────────────────────────────────────────────────────────

MONOREPO_ROOT: Path = Path(__file__).resolve().parents[2]
DEV_ROOT: Path = MONOREPO_ROOT / "dev"

# ──────────────────────────────────────────────────────────────
# CONSTANTES
# ──────────────────────────────────────────────────────────────

TRACE_FILE_NAME: str = "handoff_trace.jsonl"
OVERRIDE_ACTION: str = "COGNITION_ROUTER_OVERRIDE"

# ──────────────────────────────────────────────────────────────
# CORES E FORMATAÇÃO (Alinhado ao padrão Giulia AI)
# ──────────────────────────────────────────────────────────────

RESET = "\033[0m"
BOLD = "\033[1m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
CYAN = "\033[96m"
RED = "\033[91m"
DIM = "\033[2m"


# ── Saída de diagnóstico (stderr) — não polui a captura do pipeline ──
def _header(text: str) -> None:
    width = 60
    print(f"\n{BOLD}{CYAN}{'─' * width}{RESET}", file=sys.stderr)
    print(f"{BOLD}{CYAN}  {text}{RESET}", file=sys.stderr)
    print(f"{BOLD}{CYAN}{'─' * width}{RESET}\n", file=sys.stderr)


def _success(text: str) -> None:
    print(f"{GREEN}✅  {text}{RESET}", file=sys.stderr)


def _warn(text: str) -> None:
    print(f"{YELLOW}⚠️   {text}{RESET}", file=sys.stderr)


def _error(text: str) -> None:
    print(f"{RED}❌  {text}{RESET}", file=sys.stderr)


def _info(text: str) -> None:
    print(f"{CYAN}ℹ️   {text}{RESET}", file=sys.stderr)


def _dim(text: str) -> None:
    print(f"{DIM}    {text}{RESET}", file=sys.stderr)


def _emit_model(model: str) -> None:
    """Emite apenas o nome do modelo para stdout — capturável pelo pipeline."""
    print(model, end="\n", flush=True)


# ──────────────────────────────────────────────────────────────
# RESOLUÇÃO E DISCO
# ──────────────────────────────────────────────────────────────

def _resolve_project_path(projeto_id: str) -> Path:
    """Busca a pasta raiz do projeto de forma idêntica ao circuit breaker."""
    candidate = DEV_ROOT / projeto_id
    if candidate.is_dir():
        return candidate

    SKIP_DIRS = frozenset({
        "venv", ".venv", "env", "node_modules", ".git", ".github",
        "__pycache__", ".pytest_cache", "data", "chroma_db", "neo4j"
    })

    for root_str, dirs, _ in os.walk(DEV_ROOT, topdown=True):
        dirs[:] = [d for d in dirs if d.lower() not in SKIP_DIRS and not d.startswith(".")]
        root = Path(root_str)
        if root.name == projeto_id and root != DEV_ROOT:
            return root

    raise FileNotFoundError(f"Diretório do projeto '{projeto_id}' não encontrado em {DEV_ROOT}.")


def _extract_sdd_metadata(sdd_path: Path) -> dict[str, Any]:
    """Extrai de forma segura o bloco de código yaml no topo do markdown."""
    if not sdd_path.exists():
        raise FileNotFoundError(f"Arquivo SDD de especificação técnica não existe: {sdd_path}")

    yaml_lines: list[str] = []
    inside_block = False

    with sdd_path.open(encoding="utf-8") as f:
        for line in f:
            stripped = line.strip()
            if stripped == "```yaml":
                inside_block = True
                continue
            if stripped == "```" and inside_block:
                break
            if inside_block:
                yaml_lines.append(line)

    if not yaml_lines:
        return {}

    try:
        data = yaml.safe_load("".join(yaml_lines))
        return data.get("metadata", {}) if isinstance(data, dict) else {}
    except yaml.YAMLError as exc:
        _warn(f"Falha ao processar bloco YAML no SDD: {exc}")
        return {}


def _append_trace_record(trace_path: Path, record: dict[str, Any]) -> None:
    """Escrita atômica append-only no histórico do projeto."""
    trace_path.parent.mkdir(parents=True, exist_ok=True)
    with trace_path.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(record, ensure_ascii=False) + "\n")


# ──────────────────────────────────────────────────────────────
# EXECUÇÃO PRINCIPAL
# ──────────────────────────────────────────────────────────────

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="cognition_router.py",
        description="Roteador dinâmico de modelos baseado na complexidade do SDD."
    )
    parser.add_argument("projeto_id", type=str, help="ID ou nome da pasta do projeto em dev/")
    parser.add_argument("sdd_filename", type=str, help="Nome do arquivo markdown do SDD (ex: prj-xx-spec.md)")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Não grava registro de override no trace do projeto (simulação).",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    projeto_id: str = args.projeto_id
    sdd_filename: str = args.sdd_filename

    _header("🧠 Giulia AI — Cognition Router (Roteador de Modelos)")

    # 1. Resolve os caminhos físicos do workspace
    try:
        project_path = _resolve_project_path(projeto_id)
        trace_path = project_path / TRACE_FILE_NAME
        sdd_path = project_path / sdd_filename
    except FileNotFoundError as exc:
        _error(str(exc))
        sys.exit(2)

    _dim(f"Projeto : {projeto_id}")
    _dim(f"SDD     : {sdd_path.relative_to(MONOREPO_ROOT)}")

    # 2. Verifica se há Override Humano ativo via variável de ambiente
    env_override = os.environ.get("GIULIA_OVERRIDE_MODEL")
    if env_override:
        _warn(f"INTERVENÇÃO HUMANA ATIVA — Override para o modelo: {env_override}")
        
        override_record = {
            "timestamp": datetime.now(tz=timezone.utc).isoformat(),
            "action": OVERRIDE_ACTION,
            "projeto_id": projeto_id,
            "forced_model": env_override,
            "message": f"Roteamento padrão ignorado. Modelo {env_override} definido pelo desenvolvedor."
        }
        
        if args.dry_run:
            _dim("MODO DRY-RUN — override não gravado no trace.")
        else:
            try:
                _append_trace_record(trace_path, override_record)
            except OSError as exc:
                _error(f"Falha ao registrar override no trace: {exc}")

        _emit_model(env_override)
        sys.exit(0)

    # 3. Processamento normal via metadados do SDD
    try:
        metadata = _extract_sdd_metadata(sdd_path)
    except Exception as exc:
        _error(f"Erro ao ler metadados do arquivo de especificação: {exc}")
        sys.exit(2)

    complexidade = metadata.get("complexidade", "Nível 1")
    modelo_alvo = metadata.get("modelo_alvo", "llama3.2:7b")

    _success(f"Análise de escopo concluída: {complexidade} identificada.")
    _info(f"Modelo alocado: {modelo_alvo}")

    # stdout limpo — apenas o nome do modelo para captura pelo pipeline
    _emit_model(modelo_alvo)
    sys.exit(0)


if __name__ == "__main__":
    main()