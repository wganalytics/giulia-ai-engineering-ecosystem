# ADR-002: Isolamento de Testes Unitários por Projeto (TDD)

* **Status:** Approved
* **Data:** 2026-08-05
* **Autor:** Wemerson
* **Jira:** GARE-152

---

## 1. Contexto
Com a escala de múltiplos subprojetos no monorepo, a execução global de testes pode se tornar lenta e gerar conflitos de ambiente/dependências entre bibliotecas distintas. Além disso, cada projeto deve ser uma unidade autônoma que possa ser testada e homologada de forma independente antes de ser empacotada ou enviada a produção.

## 2. Decisão
Fica estabelecido que cada projeto contido sob a árvore `dev/` (como `dev/<dominio>/PRJ-XX_<projeto>/`, etc.) deve possuir sua própria pasta `/tests/` interna, contendo testes unitários e funcionais que possam ser executados diretamente de dentro do subdiretório do projeto. A dependência de suítes de testes globais deve ser minimizada.

## 3. Consequências
* **Positivo:** Rapidez na validação local durante o ciclo de desenvolvimento (Red-Green-Refactor) e isolamento dos escopos de teste.
* **Negativo/Dívida:** Duplicação mínima de boilerplate de configuração de teste em cada projeto.
