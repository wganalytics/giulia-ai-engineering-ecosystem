#!/usr/bin/env bash
# =============================================================================
# run_tdd_pipeline.sh
# =============================================================================
# Orquestrador da esteira TDD autônoma do ecossistema GIULIA AI.
#
# Executa os três componentes de controle cognitivo na sequência exata:
#   A. cognition_router    → decide o modelo LLM baseado no SDD
#   B. dynamic_escalator   → promove o modelo se houver 2 falhas consecutivas
#   C. circuit_breaker     → aborta a esteira se houver 3 falhas consecutivas
# =============================================================================

set -euo pipefail

# ── Configuração ──────────────────────────────────────────────────────────────
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
MONOREPO_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
PYTHON="${GIULIA_PYTHON:-python3}"
DRY_RUN_FLAG=""
[[ "${GIULIA_DRY_RUN:-0}" == "1" ]] && DRY_RUN_FLAG="--dry-run"

# ── Cores (Compatibilidade máxima com macOS/Zsh/Bash) ─────────────────────────
RED='\x1b[31m'; GREEN='\x1b[32m'; YELLOW='\x1b[33m'
CYAN='\x1b[36m'; BOLD='\x1b[1m'; RESET='\x1b[0m'; DIM='\x1b[2m'

log()     { echo -e "${DIM}[pipeline]${RESET} $*" >&2; }
success() { echo -e "${GREEN}✅  $*${RESET}" >&2; }
warn()    { echo -e "${YELLOW}⚠️   $*${RESET}" >&2; }
error()   { echo -e "${RED}❌  $*${RESET}" >&2; }
header()  { echo -e "\n${BOLD}${CYAN}══════════════════════════════════════════════${RESET}" >&2
            echo -e "${BOLD}${CYAN}  $*${RESET}" >&2
            echo -e "${BOLD}${CYAN}══════════════════════════════════════════════${RESET}\n" >&2; }

# ── Validação de argumentos ───────────────────────────────────────────────────
if [[ $# -lt 3 ]]; then
    error "Uso: $0 <PROJETO_ID> <TASK_ID> <SDD_FILE>"
    error "Exemplo: $0 dominio/prj-xx_nome_do_projeto GARE-42 prj-xx-spec.md"
    exit 2
fi

PROJETO_ID="$1"
TASK_ID="${2^^}"       # Força maiúsculas
SDD_FILE="$3"

header "🛸 Giulia AI — Esteira TDD Autônoma"
log "Projeto : $PROJETO_ID"
log "Task    : $TASK_ID"
log "SDD     : $SDD_FILE"
[[ -n "$DRY_RUN_FLAG" ]] && warn "MODO DRY-RUN ativo — nenhum estado será persistido."
echo >&2

# ── PASSO A: Roteador de Cognição ─────────────────────────────────────────────
header "PASSO A — Roteador de Cognição"

# Desativamos temporariamente o set -e para capturar a falha sem derrubar o Bash
set +e
ROUTER_OUT=$(
    "$PYTHON" "$MONOREPO_ROOT/ecosystem/automation/cognition_router.py" \
        "$PROJETO_ID" "$SDD_FILE" \
        ${DRY_RUN_FLAG} 2>&1
)
ROUTER_EXIT=$?
set -e

if [[ $ROUTER_EXIT -ne 0 ]]; then
    error "cognition_router.py falhou com código $ROUTER_EXIT."
    echo -e "$ROUTER_OUT" >&2
    exit 2
fi

# Captura o modelo de forma flexível (suporta saída limpa ou formato de chave)
if echo "$ROUTER_OUT" | grep -q "LLM_TARGET="; then
    MODELO_BASE=$(echo "$ROUTER_OUT" | grep "LLM_TARGET=" | cut -d'=' -f2 | tr -d '\r\n[:space:]')
else
    MODELO_BASE=$(echo "$ROUTER_OUT" | tail -n1 | tr -d '\r\n[:space:]')
fi

# Envia logs normais de diagnóstico para o stderr do terminal
echo "$ROUTER_OUT" | grep -v "LLM_TARGET=" >&2 || true

if [[ -z "$MODELO_BASE" ]]; then
    error "cognition_router.py retornou um identificador de modelo vazio."
    exit 2
fi

success "Modelo base selecionado: $MODELO_BASE"

# ── PASSO B: Escalador Dinâmico ───────────────────────────────────────────────
header "PASSO B — Escalador Dinâmico"

set +e
ESCALATOR_OUT=$(
    "$PYTHON" "$MONOREPO_ROOT/ecosystem/automation/dynamic_escalator.py" \
        "$PROJETO_ID" "$TASK_ID" "$MODELO_BASE" \
        ${DRY_RUN_FLAG} 2>&1
)
ESCALATOR_EXIT=$?
set -e

if [[ $ESCALATOR_EXIT -ne 0 ]]; then
    error "dynamic_escalator.py falhou com código $ESCALATOR_EXIT. Abortando esteira."
    echo -e "$ESCALATOR_OUT" >&2
    exit 2
fi

# Captura o modelo final de forma flexível
if echo "$ESCALATOR_OUT" | grep -q "LLM_TARGET="; then
    MODELO_FINAL=$(echo "$ESCALATOR_OUT" | grep "LLM_TARGET=" | cut -d'=' -f2 | tr -d '\r\n[:space:]')
else
    MODELO_FINAL=$(echo "$ESCALATOR_OUT" | tail -n1 | tr -d '\r\n[:space:]')
fi

# Repassa os logs do escalador para a tela
echo "$ESCALATOR_OUT" | grep -v "LLM_TARGET=" >&2 || true

if [[ "$MODELO_FINAL" != "$MODELO_BASE" ]]; then
    warn "Modelo escalado: $MODELO_BASE → $MODELO_FINAL"
else
    success "Modelo mantido: $MODELO_FINAL (sem escalação necessária)"
fi

# ── PASSO C: Disjuntor de Segurança ──────────────────────────────────────────
header "PASSO C — Disjuntor de Segurança"

set +e
"$PYTHON" "$MONOREPO_ROOT/ecosystem/automation/circuit_breaker.py" \
    "$PROJETO_ID" "$TASK_ID" \
    ${DRY_RUN_FLAG}
BREAKER_EXIT=$?
set -e

if [[ $BREAKER_EXIT -eq 1 ]]; then
    echo >&2
    error "CIRCUIT BREAKER ACIONADO. Esteira interrompida. Task $TASK_ID aguarda revisão humana."
    exit 1
elif [[ $BREAKER_EXIT -ne 0 ]]; then
    error "circuit_breaker.py retornou código inesperado: $BREAKER_EXIT"
    exit 2
fi

# ── Resultado Final ───────────────────────────────────────────────────────────
echo >&2
success "Pipeline concluído. Sessão autorizada com modelo: $MODELO_FINAL"
echo >&2

# Retorna apenas o nome limpo do modelo no stdout
echo "$MODELO_FINAL"
exit 0