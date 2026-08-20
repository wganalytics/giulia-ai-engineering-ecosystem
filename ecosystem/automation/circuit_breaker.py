#!/usr/bin/env python3
"""
circuit_breaker.py
==================
Disjuntor de Segurança para o ciclo autônomo do superpower_tdd.

Monitora o arquivo handoff_trace.jsonl de um projeto e conta falhas
consecutivas de ciclos TDD para uma task específica. Ao atingir o
limiar (padrão: 3 falhas), aciona a intervenção humana via Jira e
encerra a esteira autônoma com EXIT 1.

Uso:
    python3 ecosystem/automation/circuit_breaker.py <projeto_id> <task_id>

Argumentos:
    projeto_id   Pasta relativa dentro de dev/ (ex: dominio/prj-xx_nome_do_projeto)
    task_id      Chave da task no Jira (ex: GARE-42)

Códigos de saída:
    0  → Dentro do limite de falhas. Esteira pode continuar.
    1  → Limiar atingido. Esteira ABORTADA. Jira atualizado.
    2  → Erro de configuração ou arquivo não encontrado.

Referência: governance/standards/manual_do_ecossistema.md — Seção 14
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

# ──────────────────────────────────────────────────────────────
# CONFIGURAÇÃO DE CAMINHOS
# ──────────────────────────────────────────────────────────────

MONOREPO_ROOT: Path = Path(__file__).resolve().parents[2]
DEV_ROOT: Path = MONOREPO_ROOT / "dev"
ATUALIZAR_TAREFA_SCRIPT: Path = (
    MONOREPO_ROOT / "ecosystem" / "jira" / "atualizar_tarefa.py"
)

# ──────────────────────────────────────────────────────────────
# CONSTANTES
# ──────────────────────────────────────────────────────────────

TRACE_FILE_NAME: str = "handoff_trace.jsonl"
FAILURE_ACTION: str = "tdd_cycle_failed"
BREAKER_ACTION: str = "CIRCUIT_BREAKER_TRIGGERED"
DEFAULT_THRESHOLD: int = 3

# ──────────────────────────────────────────────────────────────
# CORES E FORMATAÇÃO (alinhado ao padrão do ecossistema)
# ──────────────────────────────────────────────────────────────

RESET = "\033[0m"
BOLD = "\033[1m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
CYAN = "\033[96m"
RED = "\033[91m"
DIM = "\033[2m"


def _header(text: str) -> None:
    width = 60
    print(f"\n{BOLD}{CYAN}{'─' * width}{RESET}")
    print(f"{BOLD}{CYAN}  {text}{RESET}")
    print(f"{BOLD}{CYAN}{'─' * width}{RESET}\n")


def _success(text: str) -> None:
    print(f"{GREEN}✅  {text}{RESET}")


def _warn(text: str) -> None:
    print(f"{YELLOW}⚠️   {text}{RESET}")


def _error(text: str) -> None:
    print(f"{RED}❌  {text}{RESET}")


def _info(text: str) -> None:
    print(f"{CYAN}ℹ️   {text}{RESET}")


def _dim(text: str) -> None:
    print(f"{DIM}    {text}{RESET}")


# ──────────────────────────────────────────────────────────────
# LEITURA E ESCRITA DO HANDOFF TRACE
# ──────────────────────────────────────────────────────────────


def _resolve_trace_path(projeto_id: str) -> Path:
    """
    Resolve o caminho absoluto do handoff_trace.jsonl.

    O projeto_id pode ser um caminho relativo a dev/ (ex: dominio/prj-xx_nome_do_projeto)
    ou o nome de uma pasta diretamente dentro de dev/. A busca é feita com
    poda ativa de diretórios pesados (venv, data, chroma_db, .git etc.) via
    os.walk com topdown=True, evitando varredura de milhões de arquivos de
    dependências e dados binários em ambientes de produção.

    Raises:
        FileNotFoundError: quando o diretório do projeto não existe.
    """
    import os

    # ── Fast-path: caminho direto dev/<projeto_id> ─────────────
    candidate = DEV_ROOT / projeto_id
    if candidate.is_dir():
        return candidate / TRACE_FILE_NAME

    # ── Pastas que NUNCA devem ser varridas ─────────────────────
    # Listadas em minúsculas para comparação case-insensitive.
    SKIP_DIRS: frozenset[str] = frozenset({
        "venv", ".venv", "env",            # ambientes virtuais Python
        "node_modules",                     # dependências JS
        ".git", ".github",                  # controle de versão
        "__pycache__", ".pytest_cache",     # cache Python
        "data", "chroma_db", "neo4j",       # bases de dados locais
        "dist", "build", ".tox",            # artefatos de build
        "logs", "backups",                  # dados operacionais volumosos
    })

    # ── Busca com poda ativa usando os.walk(topdown=True) ───────
    # Modificar `dirs` in-place com topdown=True impede o os.walk de
    # descer nos diretórios removidos — é a única forma de poda real no stdlib.
    for root_str, dirs, _ in os.walk(DEV_ROOT, topdown=True):
        # Poda: remove subpastas proibidas antes de descer nelas
        dirs[:] = [
            d for d in dirs
            if d.lower() not in SKIP_DIRS and not d.startswith(".")
        ]

        root = Path(root_str)
        if root.name == projeto_id and root != DEV_ROOT:
            return root / TRACE_FILE_NAME

    raise FileNotFoundError(
        f"Diretório do projeto '{projeto_id}' não encontrado dentro de {DEV_ROOT}. "
        f"Verifique se o projeto_id corresponde a uma pasta válida em dev/."
    )


def _read_trace_lines(trace_path: Path) -> list[dict[str, Any]]:
    """
    Lê o arquivo JSONL linha a linha, ignorando linhas vazias ou malformadas.

    Returns:
        Lista de dicionários com os registros válidos.

    Raises:
        OSError: quando o arquivo não pode ser aberto por motivo de permissão.
    """
    if not trace_path.exists():
        _warn(f"Arquivo de rastreamento não encontrado: {trace_path}")
        _info("Nenhuma falha anterior registrada. Esteira pode continuar.")
        return []

    records: list[dict[str, Any]] = []
    parse_errors: int = 0

    with trace_path.open(encoding="utf-8") as fh:
        for line_no, raw_line in enumerate(fh, start=1):
            stripped = raw_line.strip()
            if not stripped:
                continue
            try:
                records.append(json.loads(stripped))
            except json.JSONDecodeError as exc:
                parse_errors += 1
                _warn(f"Linha {line_no} inválida no JSONL (ignorada): {exc}")

    if parse_errors:
        _warn(f"{parse_errors} linha(s) malformada(s) ignorada(s) no trace.")

    return records


def _append_trace_record(trace_path: Path, record: dict[str, Any]) -> None:
    """
    Acrescenta um registro JSON ao final do arquivo JSONL (append-only).

    A operação é atômica a nível de linha: o registro é serializado e
    escrito com newline final antes de qualquer outro write ocorrer.

    Raises:
        OSError: quando não há permissão de escrita no arquivo.
    """
    trace_path.parent.mkdir(parents=True, exist_ok=True)
    with trace_path.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(record, ensure_ascii=False) + "\n")


# ──────────────────────────────────────────────────────────────
# LÓGICA DO CIRCUIT BREAKER
# ──────────────────────────────────────────────────────────────


def _count_consecutive_failures(
    records: list[dict[str, Any]], task_id: str
) -> int:
    """
    Conta falhas TDD consecutivas para uma task específica.

    Percorre os registros em ordem cronológica reversa (do mais recente
    para o mais antigo). A contagem é interrompida assim que um registro
    de outra ação for encontrado para a mesma task, ou quando a task_id
    mudar — garantindo que só falhas consecutivas sejam contadas.

    Args:
        records: Lista de registros lidos do JSONL, em ordem de inserção.
        task_id: Chave Jira da task a ser analisada (ex: GARE-42).

    Returns:
        Número inteiro de falhas consecutivas.
    """
    consecutive: int = 0

    # Percorre do registro mais recente para o mais antigo
    for record in reversed(records):
        rec_task = record.get("task_id", "")
        rec_action = record.get("action", "")

        # Ignora registros de outras tasks
        if rec_task != task_id:
            continue

        if rec_action == FAILURE_ACTION:
            consecutive += 1
        else:
            # Qualquer outra ação para esta task quebra a sequência consecutiva
            break

    return consecutive


def _trigger_jira_impedimento(task_id: str, consecutive_failures: int) -> bool:
    """
    Invoca o script atualizar_tarefa.py para mover o card para impedimento.

    Utiliza subprocess para chamar o script Jira como um processo filho,
    preservando a separação de responsabilidades e o contexto de autenticação
    já configurado no atualizar_tarefa.py.

    Args:
        task_id: Chave Jira da task (ex: GARE-42).
        consecutive_failures: Número de falhas que causaram o disparo.

    Returns:
        True se o Jira foi atualizado com sucesso, False caso contrário.
    """
    if not ATUALIZAR_TAREFA_SCRIPT.exists():
        _error(
            f"Script Jira não encontrado: {ATUALIZAR_TAREFA_SCRIPT}\n"
            "   Atualize o Jira manualmente e mova o card para impedimento."
        )
        return False

    nota_tecnica = (
        f"🔴 CIRCUIT BREAKER ACIONADO — Intervenção humana necessária.\n\n"
        f"Task ID: {task_id}\n"
        f"Falhas TDD consecutivas: {consecutive_failures}/{DEFAULT_THRESHOLD}\n"
        f"Data/Hora: {datetime.now(tz=timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}\n\n"
        f"O ciclo autônomo do superpower_tdd atingiu o limite de {DEFAULT_THRESHOLD} "
        f"falhas consecutivas sem sucesso. A esteira foi interrompida automaticamente "
        f"para evitar consumo desordenado de tokens e loop infinito de correção.\n\n"
        f"Ação requerida: Revisar os logs de falha em handoff_trace.jsonl e "
        f"intervir manualmente antes de reiniciar o ciclo autônomo."
    )

    cmd = [
        sys.executable,
        str(ATUALIZAR_TAREFA_SCRIPT),
        task_id.upper(),
        "selected",  # Retorna para 'Selected for Development' (revisão humana)
        "--nota", nota_tecnica,
    ]

    _info(f"Acionando atualizar_tarefa.py para {task_id}...")

    try:
        result = subprocess.run(
            cmd,
            cwd=str(MONOREPO_ROOT),
            capture_output=True,
            text=True,
            timeout=30,
        )

        if result.stdout:
            print(result.stdout)
        if result.stderr:
            _warn(f"Stderr do atualizar_tarefa: {result.stderr}")

        if result.returncode == 0:
            _success(f"Card {task_id} movido para revisão humana no Jira.")
            return True
        else:
            _error(
                f"atualizar_tarefa.py retornou código {result.returncode}. "
                f"Atualize o Jira manualmente."
            )
            return False

    except subprocess.TimeoutExpired:
        _error("Timeout ao chamar atualizar_tarefa.py (>30s). Atualize o Jira manualmente.")
        return False
    except OSError as exc:
        _error(f"Erro ao executar atualizar_tarefa.py: {exc}")
        return False


# ──────────────────────────────────────────────────────────────
# PONTO DE ENTRADA PRINCIPAL
# ──────────────────────────────────────────────────────────────


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="circuit_breaker.py",
        description=(
            "Disjuntor de Segurança para o ciclo autônomo do superpower_tdd.\n"
            "Monitora falhas consecutivas de TDD e aciona intervenção humana."
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemplos:
  # Verificar ciclo TDD de um projeto
  python3 ecosystem/automation/circuit_breaker.py dominio/prj-xx_nome_do_projeto GARE-42

  # Verificar com threshold customizado
  python3 ecosystem/automation/circuit_breaker.py dominio/prj-yy_outro_projeto GARE-10 --threshold 5

Códigos de saída:
  0  → Esteira pode continuar (falhas < threshold)
  1  → Esteira ABORTADA (limiar atingido, Jira atualizado)
  2  → Erro de configuração ou arquivo não encontrado
        """,
    )
    parser.add_argument(
        "projeto_id",
        type=str,
        help="Pasta do projeto relativa a dev/ (ex: dominio/prj-xx_nome_do_projeto)",
    )
    parser.add_argument(
        "task_id",
        type=str,
        help="Chave da task no Jira (ex: GARE-42)",
    )
    parser.add_argument(
        "--threshold",
        type=int,
        default=DEFAULT_THRESHOLD,
        metavar="N",
        help=f"Número máximo de falhas consecutivas permitidas (padrão: {DEFAULT_THRESHOLD})",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Simula a execução sem escrever no trace nem acionar o Jira",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    projeto_id: str = args.projeto_id
    task_id: str = args.task_id.upper()
    threshold: int = args.threshold
    dry_run: bool = args.dry_run

    _header("🔌 Giulia AI — Circuit Breaker (Disjuntor de Segurança)")
    _dim(f"Projeto : {projeto_id}")
    _dim(f"Task    : {task_id}")
    _dim(f"Limiar  : {threshold} falhas consecutivas")
    if dry_run:
        _warn("MODO DRY-RUN ativo — nenhuma escrita será realizada.")

    # ── 1. Resolve o caminho do trace ────────────────────────
    try:
        trace_path = _resolve_trace_path(projeto_id)
    except FileNotFoundError as exc:
        _error(str(exc))
        sys.exit(2)

    _dim(f"Trace   : {trace_path.relative_to(MONOREPO_ROOT)}")

    # ── 2. Lê registros do JSONL ─────────────────────────────
    try:
        records = _read_trace_lines(trace_path)
    except OSError as exc:
        _error(f"Erro ao ler o arquivo de trace: {exc}")
        sys.exit(2)

    # ── 3. Conta falhas consecutivas ─────────────────────────
    consecutive_failures = _count_consecutive_failures(records, task_id)

    print()
    _info(
        f"Falhas TDD consecutivas para {task_id}: "
        f"{consecutive_failures}/{threshold}"
    )

    # ── 4. Avalia o limiar ───────────────────────────────────
    if consecutive_failures < threshold:
        _success(
            f"Dentro do limite ({consecutive_failures} < {threshold}). "
            f"Esteira pode continuar. ✅"
        )
        sys.exit(0)

    # ── 5. LIMIAR ATINGIDO — aciona o disjuntor ──────────────
    print()
    _warn(
        f"LIMIAR ATINGIDO! {consecutive_failures} falhas consecutivas "
        f"para {task_id}. Acionando disjuntor..."
    )

    # 5a. Registra evento no trace
    breaker_record: dict[str, Any] = {
        "timestamp": datetime.now(tz=timezone.utc).isoformat(),
        "action": BREAKER_ACTION,
        "task_id": task_id,
        "projeto_id": projeto_id,
        "consecutive_failures": consecutive_failures,
        "threshold": threshold,
        "message": (
            f"Circuit breaker acionado após {consecutive_failures} falhas TDD "
            f"consecutivas. Esteira autônoma interrompida."
        ),
    }

    if not dry_run:
        try:
            _append_trace_record(trace_path, breaker_record)
            _success(
                f"Evento '{BREAKER_ACTION}' registrado em "
                f"{trace_path.relative_to(MONOREPO_ROOT)}"
            )
        except OSError as exc:
            _error(f"Não foi possível registrar o evento no trace: {exc}")
            # Não interrompe — ainda tenta acionar o Jira
    else:
        _dim(f"[DRY-RUN] Registro que seria inserido: {json.dumps(breaker_record)}")

    # 5b. Aciona o script Jira
    if not dry_run:
        jira_ok = _trigger_jira_impedimento(task_id, consecutive_failures)
        if not jira_ok:
            _warn(
                f"Falha ao atualizar o Jira automaticamente.\n"
                f"   Ação manual necessária: mover {task_id} para impedimento/revisão."
            )
    else:
        _dim(f"[DRY-RUN] Chamada Jira omitida. Task: {task_id}")
        jira_ok = True

    # 5c. Encerra com EXIT 1 — sinaliza para a esteira que deve parar
    print()
    _error(
        f"ESTEIRA AUTÔNOMA ABORTADA. Task {task_id} requer intervenção humana.\n"
        f"   Revise handoff_trace.jsonl e resolva os erros antes de reiniciar."
    )
    sys.exit(1)


if __name__ == "__main__":
    main()
