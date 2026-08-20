# SDD — GARE-151: Validador do Ecossistema com Health Score (0-100)

**Versão:** 1.0  
**Issue Jira:** GARE-151  
**Autor:** Wemerson (RLM Session #009)  
**Data:** 2026-08-05  
**Status:** Draft  
**Fundamentação:** Métricas de Saúde de Repositório & Garantia Contínua de Governança

---

## 1. Contexto e Problema

### 1.1 O Cenário Atual

O script `validate_ecosystem.py` verifica se o ecossistema está consistente, ou seja, se os mapeamentos do `status.md` batem com as pastas do `dev/` e se os scripts funcionam. No entanto, ele possui duas limitações graves:
1. **Pass/Fail Binário:** O script é pass/fail. Ele não mede a *qualidade* ou o *grau de maturidade* de governança dos projetos individuais (ex: se um projeto tem testes implementados ou se tem uma especificação SDD escrita).
2. **Falta de Histórico:** Sem uma pontuação agregada histórica, o proprietário do ecossistema não consegue acompanhar em uma métrica clara se a dívida técnica do monorepo está aumentando ou diminuindo.

---

## 2. Objetivo

Evoluir o `validate_ecosystem.py` para calcular um **Ecosystem Health Score (0-100)** e persistir esses resultados em um arquivo JSON histórico (`observability/metrics/health_score.json`). O score deve punir desvios de governança (Vibe Coding) e incentivar a adoção de SDD, TDD e boas práticas.

---

## 3. Arquitetura do Score (Regra de Cálculo)

A pontuação de saúde do ecossistema partirá de uma pontuação base dinâmica calculada sobre a média dos projetos ativos mais verificações globais de governança.

### 3.1 Fórmula Geral

$$HealthScore = (ScoreGlobais * 0.4) + (ScoreMedioProjetos * 0.6)$$

### 3.2 Critérios de Avaliação Globais (Max 100pts)

| Critério | Pontuação | Validação Mecânica |
|---|---|---|
| **Ausência de arquivos órfãos na raiz** | 30 pts | Falha se existirem arquivos `.py`, `.json` ou `.png` não catalogados diretamente no root. |
| **Freshness do contexto_rlm.md** | 30 pts | Validado pelo `mtime` do arquivo. Pontuação cheia se atualizado nos últimos 7 dias. 0 pts se > 30 dias. |
| **Compliance do Diário de Bordo** | 20 pts | Verifica se a última sessão cadastrada no `diario_de_bordo.md` tem data de atualização correspondente ao último commit Git. |
| **Isolamento de Credenciais** | 20 pts | Garante que **nenhum** `.env` foi commitado (usando verificação git). |

### 3.3 Critérios de Avaliação por Projeto (Max 100pts por Projeto)

| Critério | Pontuação | Validação Mecânica |
|---|---|---|
| **Evolução baseada em SDD** | 30 pts | Presença de arquivo `*_SDD.md` na pasta `governance/sdd/` para o respectivo ID do projeto. |
| **Suíte de Testes Existente (TDD)** | 30 pts | Presença de pasta `/tests/` com pelo menos um arquivo de teste funcional dentro do workspace do projeto. |
| **Testes passando** | 20 pts | Executa o teste do projeto. Pontuação máxima se todos passarem. 0 pts se falhar. |
| **Diário de Bordo local** | 20 pts | Presença de `diario_de_bordo.md` local atualizado. |

---

## 4. Persistência de Telemetria

Toda execução de validação deve salvar um snapshot no arquivo `observability/metrics/health_score.json`:

```json
{
  "timestamp": "2026-08-05T17:50:00Z",
  "health_score": 85.5,
  "metrics": {
    "global_score": 90.0,
    "projects_average_score": 82.5,
    "orphan_files_count": 2,
    "rlm_freshness_days": 1
  },
  "projects": {
    "PRJ-XX": {"score": 100.0, "sdd": true, "tdd": true, "tests_pass": true},
    "PRJ-YY": {"score": 60.0, "sdd": true, "tdd": false, "tests_pass": false}
  }
}
```

---

## 5. Critérios de Aceite

- [ ] **CA-1:** O script `validate_ecosystem.py` calcula o score corretamente e exibe uma barra de progresso visual de saúde (ex: `[████████░░] 80%`).
- [ ] **CA-2:** A execução do validador cria ou atualiza `observability/metrics/health_score.json` com o schema correto.
- [ ] **CA-3:** Se o score global de saúde cair abaixo de **70%**, o script deve disparar um aviso visual destacado no terminal para o desenvolvedor.
- [ ] **CA-4:** O script não quebra caso algum projeto esteja incompleto ou falte sua venv (mecanismo de fallback silencioso).

---

## 6. Referências

- Issue Jira: [GARE-151](https://wganalytics.atlassian.net/browse/GARE-151)
