# ADR-003: Gate de Revisão Mandatório por Agente de Code Review

* **Status:** Approved
* **Data:** 2026-08-05
* **Autor:** Wemerson
* **Jira:** GARE-152

---

## 1. Contexto
Com a utilização de assistentes e agentes autônomos de IA para codificação, há um risco considerável de degradação da base de código caso sejam permitidas alterações ad-hoc sem seguir os princípios SOLID, SRP (Single Responsibility Principle) e Clean Code. Modificações impulsivas ("Vibe Coding") levam a acúmulo acelerado de dívida técnica.

## 2. Decisão
É obrigatório que qualquer alteração de código ou funcionalidade passe por uma etapa de code review rigorosa. O Code Review Agent deve ser acionado para avaliar a qualidade e a conformidade da arquitetura de software antes que o desenvolvimento seja concluído e marcado como `Done`.

## 3. Consequências
* **Positivo:** Preservação da integridade estrutural, manutenibilidade e qualidade de código a longo prazo.
* **Negativo/Dívida:** Etapa extra de fricção no workflow que os agentes precisam seguir antes de finalizar as entregas.
