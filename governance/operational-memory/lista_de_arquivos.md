# 📂 Estrutura de Arquivos do Ecossistema

Atualizado em: Qua Ago 19 11:19:11 -0300 2026

```text
.
├── .pytest_cache
│   ├── v
│   │   └── cache
│   │       ├── lastfailed
│   │       └── nodeids
│   ├── .gitignore
│   ├── CACHEDIR.TAG
│   └── README.md
├── config
│   └── migration.env.template
├── deployment
│   ├── compose
│   ├── configs
│   └── docker
├── docs
│   ├── architecture
│   │   └── ecosystem_diagram.svg
│   ├── governance
│   │   └── QA_STANDARDS.md
│   └── roadmap
│       └── GIULIA_AI_ROADMAP_2026.md
├── ecosystem
│   ├── agents
│   │   ├── .gitkeep
│   │   ├── architecture_orchestrator.py
│   │   ├── code_review_agent.py
│   │   ├── gestora_master.md
│   │   ├── guardrails.py
│   │   ├── review_guardrails.md
│   │   └── tdd_orchestrator.py
│   ├── automation
│   │   ├── .gitkeep
│   │   ├── agent_harness.py
│   │   ├── atualizar_ecossistema.py
│   │   ├── audit_report.json
│   │   ├── audit_system.py
│   │   ├── auto_diary.py
│   │   ├── batch_doc_generator.py
│   │   ├── circuit_breaker.py
│   │   ├── cognition_router.py
│   │   ├── dynamic_escalator.py
│   │   ├── governance_snapshot.py
│   │   ├── insights_system_prompt.json
│   │   ├── insights_system_prompt.md
│   │   ├── load_insights_rules.py
│   │   ├── prj_init.py
│   │   ├── repair_system.py
│   │   ├── run_tdd_pipeline.sh
│   │   ├── scan_ecosystem.py
│   │   ├── scanner_do_ecossistema.py
│   │   ├── test_harness_integration.py
│   │   └── validate_ecosystem.py
│   ├── bench
│   │   ├── runner.py
│   │   └── tasks.json
│   ├── cli
│   │   ├── .gitkeep
│   │   └── gare_cli.py
│   ├── github
│   │   └── .gitkeep
│   ├── jira
│   │   ├── .gitkeep
│   │   ├── atualizar_tarefa.py
│   │   ├── cleanup_jira.py
│   │   ├── context_loader.py
│   │   ├── find_agent_jira.py
│   │   ├── find_story_points.py
│   │   ├── jira_project_sync.py
│   │   ├── jira_sync.py
│   │   └── lifecycle_manager.py
│   ├── mcp
│   │   ├── ast_extractor.py
│   │   └── codecompass_mcp.py
│   ├── observatory
│   │   ├── .gitkeep
│   │   └── telemetry_aggregator.py
│   ├── standards
│   │   └── .gitkeep
│   ├── templates
│   │   └── .gitkeep
│   └── tests
│       ├── test_adrs.py
│       ├── test_ast_extractor.py
│       ├── test_auto_diary.py
│       ├── test_codecompass_mcp.py
│       ├── test_gare_bench.py
│       ├── test_gare_cli.py
│       ├── test_graph_schema.py
│       └── test_health_score.py
├── governance
│   ├── architecture-decisions
│   │   ├── jira_docs
│   │   │   └── readme.md
│   │   ├── .gitkeep
│   │   ├── adr-001-sufixo-provedor-vectordb.md
│   │   ├── adr-002-isolamento-tdd-projetos.md
│   │   ├── adr-003-gate-revisao-code-review.md
│   │   ├── adr-xxx_template.md
│   │   ├── contexto_rlm.md
│   │   ├── estrutura_e_workflow.md
│   │   ├── governance_snapshot_standard.md
│   │   ├── rag_metrics_standard.md
│   │   └── readme.md
│   ├── onboarding
│   │   └── .gitkeep
│   ├── operational-memory
│   │   ├── .contexto_navegacao.md
│   │   ├── .gitkeep
│   │   ├── contexto_rlm.md
│   │   ├── diario_de_bordo.md
│   │   ├── index.md
│   │   ├── lista_de_arquivos.md
│   │   └── status.md
│   ├── projects
│   │   └── .gitkeep
│   ├── sdd
│   │   ├── .gitkeep
│   │   ├── deprecated.md
│   │   ├── gare-140_sdd.md
│   │   ├── gare-145_sdd.md
│   │   ├── gare-146_sdd.md
│   │   ├── gare-147_sdd.md
│   │   ├── gare-148_sdd.md
│   │   ├── gare-149_sdd.md
│   │   ├── gare-151_sdd.md
│   │   ├── gare-152_sdd.md
│   │   └── gare-153_sdd.md
│   ├── snapshots
│   │   └── .gitkeep
│   ├── standards
│   │   ├── .gitkeep
│   │   ├── diretrizes_desenvolvimento_ia.md
│   │   ├── ecosystem_master_readme.md
│   │   ├── manual_do_ecossistema.md
│   │   └── padrao_seguranca_aplicacoes.md
│   ├── tdd
│   │   └── .gitkeep
│   └── traceability
│       └── .gitkeep
├── infra
│   ├── .github
│   │   └── workflows
│   │       └── ci.yml
│   ├── config
│   │   └── pyproject.toml
│   ├── core
│   │   ├── atualizar_tarefa.py
│   │   ├── fix_duplicate_subtasks.py
│   │   ├── fix_estimates.py
│   │   ├── git_jira_link.py
│   │   ├── github_sync.py
│   │   ├── governance_snapshot.py
│   │   ├── jira_helper.py
│   │   ├── jira_manager.py
│   │   ├── jira_sync.py
│   │   ├── lifecycle_manager.py
│   │   ├── limpar_jira.py
│   │   ├── rebuild_sync_state.py
│   │   ├── sync_all_projects.py
│   │   └── validate_ecosystem.py
│   ├── docs
│   │   ├── exemplo_card_rag192.png
│   │   ├── norma_gestao_jira_v1.pdf
│   │   └── setup_github.md
│   ├── lib
│   │   └── sync_state.py
│   ├── tests
│   │   ├── __init__.py
│   │   ├── conftest.py
│   │   ├── test_jira_sync_utils.py
│   │   └── test_sync_state.py
│   ├── .gitignore
│   ├── atualizar_diario.py
│   └── start_project.py
├── observability
│   ├── dashboards
│   │   └── .gitkeep
│   ├── logs
│   ├── metrics
│   │   ├── .gitkeep
│   │   ├── aggregated_metrics.json
│   │   ├── bench_results.json
│   │   └── health_score.json
│   ├── profiling
│   │   └── .gitkeep
│   ├── reports
│   │   ├── .github
│   │   │   └── workflows
│   │   ├── config
│   │   ├── core
│   │   ├── docs
│   │   │   └── setup_github.md
│   │   ├── lib
│   │   ├── logs
│   │   │   └── rag_metrics.json
│   │   ├── tests
│   │   ├── .gitkeep
│   │   ├── index.html
│   │   └── telemetry_dashboard.md
│   ├── telemetry
│   │   └── .gitkeep
│   └── traces
│       └── .gitkeep
├── scripts
│   ├── governance
│   │   ├── .gitkeep
│   │   ├── architecture_orchestrator.py
│   │   ├── code_review_agent.py
│   │   └── tdd_orchestrator.py
│   ├── maintenance
│   │   ├── .gitkeep
│   │   ├── list_mcp_issues.py
│   │   └── mcp_issues.json
│   ├── migration
│   │   ├── .gitkeep
│   │   ├── 00_prepare_portfolio_assets.sh
│   │   ├── 01_backup_freeze.sh
│   │   ├── 02_validate_structure.sh
│   │   ├── 03_migrate_governance.sh
│   │   ├── 04_migrate_runtime.sh
│   │   ├── 05_migrate_shared.sh
│   │   ├── 06_migrate_observability.sh
│   │   ├── 07_generate_portfolio.sh
│   │   ├── 08_validate_migration.sh
│   │   ├── 09_generate_public_repo.sh
│   │   └── common.sh
│   ├── observability
│   │   └── .gitkeep
│   ├── publishing
│   │   └── .gitkeep
│   ├── cleanup_jira.py
│   ├── find_agent_jira.py
│   ├── find_story_points.py
│   ├── gerar_arvore.py
│   ├── stress_test_metrics.py
│   └── validate_infra.py
├── shared
│   ├── infra
│   │   └── config
│   │       └── .sync_state.json
│   ├── REGISTRY
│   │   └── projects.json
│   └── schemas
│       └── graph_schema.cypher
├── .env
├── .env.example
├── .gitignore
├── AI_BOOTSTRAP.md
├── CLAUDE.md
├── ecosystem_registry.json
├── LICENSE
├── README.md
└── requirements.txt

71 directories, 183 files
```
