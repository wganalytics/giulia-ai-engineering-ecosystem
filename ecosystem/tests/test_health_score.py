import json
import subprocess
from pathlib import Path

# Raiz do monorepo
MONOREPO_ROOT = Path(__file__).resolve().parents[2]
METRICS_DIR = MONOREPO_ROOT / "observability" / "metrics"
HS_FILE = METRICS_DIR / "health_score.json"

def test_validate_script_calculates_health_score():
    """Garante que a execução do script de validação gera o arquivo de telemetria health_score.json"""
    # Se o arquivo já existe, limpa para testar geração real
    if HS_FILE.exists():
        HS_FILE.unlink()
        
    # Executa o script de consistência
    script_path = MONOREPO_ROOT / "ecosystem" / "automation" / "validate_ecosystem.py"
    res = subprocess.run(["python3", str(script_path)], capture_output=True, text=True)
    
    assert HS_FILE.exists(), f"O arquivo {HS_FILE.name} não foi criado após a execução do validador!"

def test_health_score_json_schema():
    """Garante que o JSON de health_score gerado segue o schema técnico especificado no SDD"""
    assert HS_FILE.exists(), "health_score.json não encontrado!"
    
    with open(HS_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
        
    required_keys = {"timestamp", "health_score", "metrics", "projects"}
    for key in required_keys:
        assert key in data, f"Chave crítica '{key}' ausente no telemetry JSON do Health Score!"
        
    score = data["health_score"]
    assert isinstance(score, (int, float)), "health_score deve ser um valor numérico!"
    assert 0 <= score <= 100, f"health_score inválido: {score}! Deve estar entre 0 e 100."
