#!/usr/bin/env python3
"""
dynamic_escalator.py
====================
Escalador Dinâmico de Modelo LLM para o ciclo autônomo do superpower_tdd.

Monitora o handoff_trace.jsonl de um projeto e, ao detectar exatamente 2
falhas TDD consecutivas para uma task, promove automaticamente o modelo LLM
para o próximo nível de capacidade na cadeia de escalação.

Separação de canais (crítico para uso em pipeline):
  • stdout  → contém APENAS o nome do modelo resultante (base ou escalado).
              Capture com: MODELO=$(python3 dynamic_escalator.py ...)
  • stderr  → diagnósticos, logs e mensagens de operação para o operador.

Uso:
    python3 ecosystem/automation/dynamic_escalator.py \\
        <projeto_id> <task_id> <modelo_base>

Argumentos:
    projeto_id    Pasta do projeto relativa a dev/ (ex: dominio/prj-xx_nome_do_projeto)
    task_id       Chave da task no Jira (ex: GARE-42)
    modelo_base   Modelo atual retornado pelo roteador (ex: llama3, gpt-4o-mini)

Exemplos de uso em pipeline shell:
    MODELO=$(python3 ecosystem/automation/dynamic_escalator.py \\
                dominio/prj-xx_nome_do_projeto GARE-42 llama3)
    echo "Usando modelo: $MODELO"

Cadeia de escalação:
    Tier 0 (local/ollama)  →  gpt-4o-mini
    Tier 1 (mini/fast)     →  claude-3-5-sonnet-20241022
    Tier 2 (full)          →  sem escalação (já no topo)

Referência: governance/standards/manual_do_ecossistema.md — Seção 14
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

# ──────────────────────────────────────────────────────────────
# BOOTSTRAP DE PATH — permite importar do mesmo monorepo
# ──────────────────────────────────────────────────────────────

MONOREPO_ROOT: Path = Path(__file__).resolve().parents[2]
if str(MONOREPO_ROOT) not in sys.path:
    sys.path.insert(0, str(MONOREPO_ROOT))

# ──────────────────────────────────────────────────────────────
# REUTILIZAÇÃO DE UTILITÁRIOS DO CIRCUIT BREAKER
# Importa funções de trace já validadas, sem duplicar código.
# ──────────────────────────────────────────────────────────────

from ecosystem.automation.circuit_breaker import (  # noqa: E402
    _append_trace_record,
    _count_consecutive_failures,
    _read_trace_lines,
    _resolve_trace_path,
)

# ──────────────────────────────────────────────────────────────
# CONSTANTES
# ──────────────────────────────────────────────────────────────

ESCALATION_THRESHOLD: int = 2
ESCALATED_ACTION: str = "MODEL_ESCALATED"

# ──────────────────────────────────────────────────────────────
# CADEIA DE ESCALAÇÃO DE MODELOS
#
# Estrutura: lista ordenada de (padrão_regex, modelo_escalado).
# A primeira regra que casar com `modelo_base` define o próximo nível.
# Modelos que não casam com nenhuma regra são considerados Tier 2 (topo)
# e retornam sem escalação.
# ──────────────────────────────────────────────────────────────

_EscalationRule = tuple[re.Pattern[str], str]

ESCALATION_CHAIN: list[_EscalationRule] = [
    # ── Tier 0 → Tier 1 ─────────────────────────────────────────
    # Modelos locais / Ollama: nomes típicos de LLMs open-source
    (
        re.compile(
            r"^(ollama[:/]|llama|mistral|phi|gemma|qwen|deepseek|"
            r"codellama|yi|vicuna|orca|neural|falcon|mamba|nous|"
            r"openchat|stablelm|internlm|baichuan|aquila|bloom)",
            re.IGNORECASE,
        ),
        "gpt-4o-mini",
    ),
    # ── Tier 1 → Tier 2 ─────────────────────────────────────────
    # Modelos "mini/fast/lite": qualquer provider com sufixo de baixo custo
    (
        re.compile(
            r"(mini|haiku|flash|instant|lite|nano|small|turbo|"
            r"gpt-3\.5|gpt4o-mini|4o-mini)",
            re.IGNORECASE,
        ),
        "claude-3-5-sonnet-20241022",
    ),
]


def resolve_escalation(modelo_base: str) -> str | None:
    """
    Retorna o próximo modelo na cadeia de escalação, ou None se já estiver
    no Tier 2 (topo da cadeia — sem progressão disponível).

    Args:
        modelo_base: Identificador do modelo atual (ex: 'llama3', 'gpt-4o-mini').

    Returns:
        Nome do modelo escalado, ou None se sem escalação.
    """
    for pattern, next_model in ESCALATION_CHAIN:
        if pattern.search(modelo_base):
            return next_model
    return None  # Tier 2: modelo já está no nível máximo


# ──────────────────────────────────────────────────────────────
# OUTPUT — separação explícita stdout / stderr
# ──────────────────────────────────────────────────────────────

def _log(text: str) -> None:
    """Diagnóstico para o operador — vai para stderr."""
    print(text, file=sys.stderr)


def _emit_model(model: str) -> None:
    """Resultado para o pipeline — vai para stdout, sem newline extra."""
    print(model, end="\n", flush=True)


# ──────────────────────────────────────────────────────────────
# LÓGICA PRINCIPAL
# ──────────────────────────────────────────────────────────────


def run_escalation(
    projeto_id: str,
    task_id: str,
    modelo_base: str,
    dry_run: bool = False,
) -> str:
    """
    Executa a lógica de escalação dinâmica de modelo.

    Lê o trace do projeto, conta falhas consecutivas para a task e decide
    se o modelo deve ser promovido. Em caso de escalação, registra o evento
    no JSONL e retorna o novo modelo; caso contrário, retorna o modelo_base.

    Args:
        projeto_id:   Identificador do projeto (relativo a dev/).
        task_id:      Chave da task no Jira (ex: GARE-42).
        modelo_base:  Modelo atual fornecido pelo roteador.
        dry_run:      Se True, não escreve no trace.

    Returns:
        Nome do modelo a ser utilizado (base ou escalado).
    """
    task_id = task_id.upper()

    _log(f"\n⚡ Dynamic Escalator — {task_id} @ {projeto_id}")
    _log(f"   Modelo base   : {modelo_base}")
    _log(f"   Threshold     : {ESCALATION_THRESHOLD} falhas consecutivas")
    if dry_run:
        _log("   ⚠️  DRY-RUN ativo — nada será escrito no trace.")

    # ── 1. Resolve trace ────────────────────────────────────────
    try:
        trace_path = _resolve_trace_path(projeto_id)
    except FileNotFoundError as exc:
        _log(f"❌ Erro ao localizar projeto: {exc}")
        sys.exit(2)

    _log(f"   Trace         : {trace_path.relative_to(MONOREPO_ROOT)}")

    # ── 2. Lê registros ─────────────────────────────────────────
    try:
        records = _read_trace_lines(trace_path)
    except OSError as exc:
        _log(f"❌ Erro ao ler trace: {exc}")
        sys.exit(2)

    # ── 3. Conta falhas consecutivas ────────────────────────────
    consecutive = _count_consecutive_failures(records, task_id)
    _log(f"   Falhas consec.: {consecutive}/{ESCALATION_THRESHOLD}")

    # ── 4. Decisão de escalação ─────────────────────────────────
    if consecutive < ESCALATION_THRESHOLD:
        _log(f"   ✅ Abaixo do threshold — mantendo modelo: {modelo_base}")
        return modelo_base

    # Exatamente >= ESCALATION_THRESHOLD falhas: verifica progressão
    next_model = resolve_escalation(modelo_base)

    if next_model is None:
        _log(
            f"   ℹ️  Modelo '{modelo_base}' já está no Tier 2 (topo). "
            "Nenhuma escalação disponível."
        )
        return modelo_base

    # ── 5. Registra escalonamento no JSONL ──────────────────────
    escalation_record: dict[str, Any] = {
        "timestamp": datetime.now(tz=timezone.utc).isoformat(),
        "action": ESCALATED_ACTION,
        "task_id": task_id,
        "projeto_id": projeto_id,
        "modelo_anterior": modelo_base,
        "modelo_escalado": next_model,
        "consecutive_failures": consecutive,
        "threshold": ESCALATION_THRESHOLD,
        "message": (
            f"Modelo escalado de '{modelo_base}' para '{next_model}' "
            f"após {consecutive} falhas TDD consecutivas."
        ),
    }

    if not dry_run:
        try:
            _append_trace_record(trace_path, escalation_record)
            _log(f"   ✅ Evento '{ESCALATED_ACTION}' registrado no trace.")
        except OSError as exc:
            _log(f"   ⚠️  Falha ao gravar no trace: {exc} — continuando com escalação.")
    else:
        _log(
            f"   [DRY-RUN] Registro que seria inserido: "
            f"{json.dumps(escalation_record, ensure_ascii=False)}"
        )

    _log(f"   🚀 Escalação: {modelo_base} → {next_model}")
    return next_model


# ──────────────────────────────────────────────────────────────
# CLI
# ──────────────────────────────────────────────────────────────


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="dynamic_escalator.py",
        description=(
            "Escalador Dinâmico de Modelo LLM.\n"
            "Promove o modelo LLM após 2 falhas TDD consecutivas.\n\n"
            "IMPORTANTE: stdout contém APENAS o nome do modelo resultante.\n"
            "Use stderr para diagnósticos."
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemplos:
  # Uso básico — captura o modelo para uso em pipeline
  MODELO=$(python3 ecosystem/automation/dynamic_escalator.py \\
              dominio/prj-xx_nome_do_projeto GARE-42 llama3)

  # Simulação sem escrita no trace
  python3 ecosystem/automation/dynamic_escalator.py \\
      dominio/prj-xx_nome_do_projeto GARE-42 gpt-4o-mini --dry-run

Cadeia de escalação:
  llama3 / mistral / gemma / phi  →  gpt-4o-mini
  gpt-4o-mini / claude-3-haiku    →  claude-3-5-sonnet-20241022
  claude-3-5-sonnet / gpt-4o      →  (sem escalação — Tier 2)

Códigos de saída:
  0  → Execução bem-sucedida (modelo emitido no stdout)
  2  → Erro de configuração (projeto não encontrado, trace ilegível)
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
        "modelo_base",
        type=str,
        help="Modelo atual retornado pelo roteador (ex: llama3, gpt-4o-mini)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Simula sem escrever no trace",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    modelo_final = run_escalation(
        projeto_id=args.projeto_id,
        task_id=args.task_id,
        modelo_base=args.modelo_base,
        dry_run=args.dry_run,
    )
    _emit_model(modelo_final)


if __name__ == "__main__":
    main()
