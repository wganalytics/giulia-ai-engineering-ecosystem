# ⚠️ PASTA DEPRECIADA — Não usar

> **Data:** 2026-05-24  
> **Motivo:** Consolidação seguindo padrão de mercado

## O que aconteceu

Esta pasta (`governance/sdd/`) foi reservada originalmente para specs SDD, mas nunca chegou a ser utilizada de forma consistente.

## Decisão Arquitetural

Seguindo o padrão de mercado (GitHub, Stripe, projetos open-source de referência), as **Specs SDD** foram migradas para:

```
docs/specs/PRJ-XX_Nome_SDD.md
```

## Por que `docs/specs/`?

- `docs/` é o local canônico reconhecido pela comunidade de engenharia
- Separa claramente **especificações** (`docs/specs/`) de **arquitetura visual** (`docs/architecture/`)
- Facilita descoberta por novos agentes e colaboradores sem contexto prévio

---

> **Regra:** Não criar specs nesta pasta. Usar sempre `docs/specs/`.
