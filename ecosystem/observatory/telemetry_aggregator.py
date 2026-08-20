import os
import json
import glob
from collections import defaultdict
from datetime import datetime

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
OBS_DIR = os.path.join(ROOT_DIR, "observability")

def build_metrics():
    metrics = {
        "total_executions": 0,
        "total_successes": 0,
        "total_failures": 0,
        "veto_protocol_count": 0,
        "top_skills": defaultdict(int),
        "projects_activity": defaultdict(int),
        "recent_traces": []
    }
    
    # Busca por arquivos handoff_trace.jsonl na pasta dev
    search_path = os.path.join(ROOT_DIR, "dev", "**", "handoff_trace.jsonl")
    trace_files = glob.glob(search_path, recursive=True)
    
    for filepath in trace_files:
        if ".git" in filepath or ".venv" in filepath or "node_modules" in filepath:
            continue
            
        with open(filepath, "r", encoding="utf-8") as f:
            for line in f:
                if not line.strip(): continue
                try:
                    data = json.loads(line)
                    
                    project = data.get("projeto_id", "Desconhecido")
                    
                    # Normalização de Nomenclaturas
                    if project == "EXEMPLO":
                        project = "PRJ-XX_ProjetoExemplo"
                        
                    # Remove o ruido de tarefas de background do dashboard para focar no trabalho real
                    if project == "auto-detect":
                        continue

                    metrics["total_executions"] += 1
                    
                    if data.get("event_type") == "veto_protocol" or data.get("status") == "veto_protocol":
                        metrics["veto_protocol_count"] += 1
                    
                    status = data.get("status", "")
                    success_statuses = ["success", "governance_synced", "initialized", "done", "completed", "auto_saved", "synced", "resolved", "In Progress", "Selected for Development", "Done"]
                    if status in success_statuses:
                        metrics["total_successes"] += 1
                    else:
                        metrics["total_failures"] += 1
                        
                    metrics["projects_activity"][project] += 1
                    
                    skills = data.get("skill_utilizada", "").split(",")
                    for skill in skills:
                        skill = skill.strip()
                        if skill:
                            metrics["top_skills"][skill] += 1
                            
                    # Guarda rastros recentes
                    metrics["recent_traces"].append(data)
                except json.JSONDecodeError:
                    continue
                    
    # Ordena top skills e filtra top 10
    metrics["top_skills"] = dict(sorted(metrics["top_skills"].items(), key=lambda item: item[1], reverse=True)[:10])
    
    # Ordena projetos mantendo todos
    metrics["projects_activity"] = dict(sorted(metrics["projects_activity"].items(), key=lambda item: item[1], reverse=True))
    
    # Ordena recent_traces pela data
    try:
        metrics["recent_traces"].sort(key=lambda x: x.get("timestamp", ""), reverse=True)
        metrics["recent_traces"] = metrics["recent_traces"][:20]
    except Exception:
        pass
        
    return metrics

def save_json(metrics):
    metrics_dir = os.path.join(OBS_DIR, "metrics")
    os.makedirs(metrics_dir, exist_ok=True)
    
    out_path = os.path.join(metrics_dir, "aggregated_metrics.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2, ensure_ascii=False)
    print(f"✅ Métricas JSON exportadas para {out_path}")

def generate_html_dashboard(metrics):
    reports_dir = os.path.join(OBS_DIR, "reports")
    os.makedirs(reports_dir, exist_ok=True)
    out_path = os.path.join(reports_dir, "index.html")
    
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    success_rate = (metrics['total_successes'] / metrics['total_executions'] * 100) if metrics['total_executions'] > 0 else 0
    
    # Prepara dados para os gráficos
    proj_labels = list(metrics["projects_activity"].keys())
    proj_data = list(metrics["projects_activity"].values())
    
    skill_labels = list(metrics["top_skills"].keys())
    skill_data = list(metrics["top_skills"].values())
    
    html = f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>GIULIA - Telemetry & Observability</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;800&display=swap');
        
        :root {{
            --bg: #0f1117;
            --surface: rgba(22, 27, 34, 0.7);
            --border: rgba(255, 255, 255, 0.1);
            --text-main: #e8eaf0;
            --text-muted: #8b949e;
            --accent: #58a6ff;
            --success: #3fb950;
            --danger: #ff7b72;
        }}
        
        body {{
            margin: 0; padding: 0;
            font-family: 'Inter', sans-serif;
            background-color: var(--bg);
            color: var(--text-main);
            background-image: radial-gradient(circle at 50% 0%, #1c2331 0%, transparent 70%);
        }}
        
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            padding: 40px 20px;
        }}
        
        .header {{
            text-align: center;
            margin-bottom: 50px;
        }}
        .header h1 {{
            font-weight: 800;
            font-size: 2.5rem;
            letter-spacing: -1px;
            margin-bottom: 10px;
            background: -webkit-linear-gradient(#c9d1d9, #8b949e);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }}
        .header p {{ color: var(--text-muted); }}
        
        .grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin-bottom: 40px;
        }}
        
        .card {{
            background: var(--surface);
            border: 1px solid var(--border);
            border-radius: 16px;
            padding: 24px;
            backdrop-filter: blur(10px);
            box-shadow: 0 8px 32px rgba(0,0,0,0.3);
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            transition: transform 0.2s;
        }}
        .card:hover {{ transform: translateY(-5px); }}
        
        .card-value {{ font-size: 3rem; font-weight: 800; margin-bottom: 5px; }}
        .card-label {{ color: var(--text-muted); font-size: 0.9rem; text-transform: uppercase; letter-spacing: 1px; font-weight: 600;}}
        
        .val-success {{ color: var(--success); }}
        .val-danger {{ color: var(--danger); }}
        .val-accent {{ color: var(--accent); }}
        
        .charts-row {{
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 20px;
            margin-bottom: 40px;
        }}
        
        @media(max-width: 768px) {{ .charts-row {{ grid-template-columns: 1fr; }} }}
        
        .chart-container {{
            background: var(--surface);
            border: 1px solid var(--border);
            border-radius: 16px;
            padding: 20px;
            backdrop-filter: blur(10px);
        }}
        .chart-container h3 {{ margin-top: 0; color: var(--text-main); font-weight: 600; }}
        
        .table-container {{
            background: var(--surface);
            border: 1px solid var(--border);
            border-radius: 16px;
            padding: 20px;
            backdrop-filter: blur(10px);
            overflow-x: auto;
        }}
        table {{ width: 100%; border-collapse: collapse; }}
        th, td {{ padding: 12px 16px; text-align: left; border-bottom: 1px solid var(--border); }}
        th {{ color: var(--text-muted); font-weight: 600; text-transform: uppercase; font-size: 0.85rem; letter-spacing: 0.5px; }}
        tr:last-child td {{ border-bottom: none; }}
        
        .status-badge {{
            padding: 4px 10px;
            border-radius: 20px;
            font-size: 0.75rem;
            font-weight: 600;
            text-transform: uppercase;
        }}
        .status-success {{ background: rgba(63, 185, 80, 0.15); color: var(--success); border: 1px solid rgba(63, 185, 80, 0.3); }}
        .status-fail {{ background: rgba(255, 123, 114, 0.15); color: var(--danger); border: 1px solid rgba(255, 123, 114, 0.3); }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>GIULIA AI Telemetry</h1>
            <p>Observabilidade e Traceability do Ecossistema | Atualizado em: {now}</p>
        </div>
        
        <div class="grid">
            <div class="card">
                <div class="card-value">{metrics['total_executions']}</div>
                <div class="card-label">Rastros Totais</div>
            </div>
            <div class="card">
                <div class="card-value val-success">{metrics['total_successes']}</div>
                <div class="card-label">Execuções Sucedidas</div>
            </div>
            <div class="card">
                <div class="card-value val-danger">{metrics['total_failures']}</div>
                <div class="card-label">Falhas / Intervenções</div>
            </div>
            <div class="card">
                <div class="card-value val-accent">{success_rate:.1f}%</div>
                <div class="card-label">Win Rate Global</div>
            </div>
            <div class="card">
                <div class="card-value" style="color: #a371f7;">{metrics.get('veto_protocol_count', 0)}</div>
                <div class="card-label">Veto Activations</div>
            </div>
        </div>
        
        <div class="charts-row">
            <div class="chart-container">
                <h3>Distribuição por Projeto</h3>
                <div style="position: relative; height:450px; width:100%">
                    <canvas id="projChart"></canvas>
                </div>
            </div>
            <div class="chart-container">
                <h3>Top 10 Skills Executadas</h3>
                <div style="position: relative; height:450px; width:100%">
                    <canvas id="skillChart"></canvas>
                </div>
            </div>
        </div>
        
        <div class="table-container">
            <h3 style="margin-top:0">Rastros Cognitivos Recentes (Últimos 20)</h3>
            <table>
                <thead>
                    <tr>
                        <th>Data / Hora</th>
                        <th>Projeto</th>
                        <th>Skill Utilizada</th>
                        <th>Status</th>
                        <th>Justificativa do Agente</th>
                    </tr>
                </thead>
                <tbody>"""
    
    for trace in metrics["recent_traces"]:
        dt = trace.get("timestamp", "").replace("T", " ")[:19]
        proj = trace.get("projeto_id", "-")
        skill = trace.get("skill_utilizada", "-")
        status = trace.get("status", "-")
        just = trace.get("justification", "-")
        
        is_success = status in ["success", "governance_synced", "initialized", "done", "completed", "auto_saved", "synced", "resolved"]
        badge_class = "status-success" if is_success else "status-fail"
        
        html += f"""
                    <tr>
                        <td style="color:var(--text-muted);font-size:0.85rem;">{dt}</td>
                        <td style="font-weight:600;">{proj}</td>
                        <td style="color:var(--accent);font-family:monospace;">{skill}</td>
                        <td><span class="status-badge {badge_class}">{status}</span></td>
                        <td style="color:var(--text-muted);font-size:0.9rem;">{just}</td>
                    </tr>"""
                    
    clean_labels = proj_labels

    html += f"""
                </tbody>
            </table>
        </div>
    </div>
    
    <script>
        Chart.defaults.color = '#8b949e';
        Chart.defaults.font.family = 'Inter';
        
        new Chart(document.getElementById('projChart'), {{
            type: 'bar',
            data: {{
                labels: {json.dumps(clean_labels)},
                datasets: [{{
                    label: 'Traces',
                    data: {json.dumps(proj_data)},
                    backgroundColor: ['#58a6ff', '#3fb950', '#ff7b72', '#d29922', '#a371f7', '#1f6feb', '#2ea043', '#f85149', '#e3b341', '#bc8cff', '#0969da', '#238636', '#da3633'],
                    borderRadius: 4
                }}]
            }},
            options: {{
                indexAxis: 'y',
                responsive: true,
                maintainAspectRatio: false,
                plugins: {{
                    legend: {{ display: false }}
                }},
                scales: {{
                    x: {{ grid: {{ color: 'rgba(255,255,255,0.05)' }} }},
                    y: {{ 
                        grid: {{ display: false }}, 
                        ticks: {{ font: {{ size: 11 }}, autoSkip: false }} 
                    }}
                }}
            }}
        }});
        
        new Chart(document.getElementById('skillChart'), {{
            type: 'bar',
            data: {{
                labels: {json.dumps(skill_labels)},
                datasets: [{{
                    label: 'Invocações',
                    data: {json.dumps(skill_data)},
                    backgroundColor: '#58a6ff',
                    borderRadius: 4
                }}]
            }},
            options: {{
                responsive: true,
                maintainAspectRatio: false,
                plugins: {{ legend: {{ display: false }} }},
                scales: {{
                    y: {{ grid: {{ color: 'rgba(255,255,255,0.05)' }} }},
                    x: {{ 
                        grid: {{ display: false }},
                        ticks: {{ maxRotation: 45, minRotation: 45, font: {{ size: 10 }}, autoSkip: false }}
                    }}
                }},
                layout: {{ padding: {{ bottom: 20 }} }}
            }}
        }});
    </script>
</body>
</html>"""
    
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"✅ Dashboard HTML gerado em {out_path}")

if __name__ == "__main__":
    print("🔍 Iniciando rastreamento de telemetria...")
    metrics = build_metrics()
    
    if metrics["total_executions"] == 0:
        print("⚠️ Nenhum rastro encontrado (0 executions). Verifique se handoff_trace.jsonl existem nas pastas dev/.")
    else:
        save_json(metrics)
        generate_html_dashboard(metrics)
        print("🚀 Camada de observabilidade populada com sucesso!")
